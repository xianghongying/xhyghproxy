# -*- coding: utf-8 -*-
import os
import re
import logging
from logging.handlers import RotatingFileHandler

import requests
from flask import Flask, Response, redirect, request, render_template, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from requests.exceptions import (
    ChunkedEncodingError,
    ContentDecodingError, ConnectionError, StreamConsumedError)
from requests.utils import (
    stream_decode_response_unicode, iter_slices, CaseInsensitiveDict)
from urllib3.exceptions import (
    DecodeError, ReadTimeoutError, ProtocolError)
from urllib.parse import quote

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gh-proxy')

# config - 支持环境变量
# 分支文件使用jsDelivr镜像的开关，0为关闭，默认关闭
jsdelivr = int(os.environ.get('JSDELIVR_ENABLE', '0'))
size_limit = int(os.environ.get('SIZE_LIMIT', str(1024 * 1024 * 1024 * 999)))  # 允许的文件大小
request_timeout = int(os.environ.get('REQUEST_TIMEOUT', '30'))  # 请求超时时间(秒)

"""
  先生效白名单再匹配黑名单，pass_list匹配到的会直接302到jsdelivr而忽略设置
  生效顺序 白->黑->pass，可以前往https://github.com/hunshcn/gh-proxy/issues/41 查看示例
  每个规则一行，可以封禁某个用户的所有仓库，也可以封禁某个用户的特定仓库，下方用黑名单示例，白名单同理
  user1 # 封禁user1的所有仓库
  user1/repo1 # 封禁user1的repo1
  */repo1 # 封禁所有叫做repo1的仓库
"""
# 支持从环境变量加载名单配置
white_list_str = os.environ.get('WHITE_LIST', '''
''')
black_list_str = os.environ.get('BLACK_LIST', '''
''')
pass_list_str = os.environ.get('PASS_LIST', '''
''')

HOST = os.environ.get('LISTEN_HOST', '0.0.0.0')  # 监听地址
PORT = int(os.environ.get('LISTEN_PORT', '80'))  # 监听端口
DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'  # Debug模式

# CDN源配置 - 支持多个CDN
CDN_SOURCES = {
    'jsdelivr': {'url': 'cdn.jsdelivr.net/gh', 'name': 'jsDelivr'},
    'ghproxy': {'url': 'ghproxy.net/https://', 'name': 'ghproxy'},
    'gitmirror': {'url': 'gitmirror.top/raw/', 'name': 'GitMirror'},
}
PREFERRED_CDN = os.environ.get('PREFERRED_CDN', 'jsdelivr')

white_list = [tuple([x.replace(' ', '') for x in i.split('/')]) for i in white_list_str.split('\n') if i and not i.strip().startswith('#')]
black_list = [tuple([x.replace(' ', '') for x in i.split('/')]) for i in black_list_str.split('\n') if i and not i.strip().startswith('#')]
pass_list = [tuple([x.replace(' ', '') for x in i.split('/')]) for i in pass_list_str.split('\n') if i and not i.strip().startswith('#')]

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', str(100 * 1024 * 1024)))  # 100MB

# 启用CORS
CORS(app, supports_credentials=True)

# 速率限制
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[os.environ.get('RATE_LIMIT', '200 per minute')],
    storage_uri='memory://',
    enabled=os.environ.get('RATE_LIMIT_ENABLE', 'true').lower() == 'true'
)

CHUNK_SIZE = 1024 * 64  # 64KB chunks，优化大文件传输性能

# 创建Session连接池，提升性能
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=50,
    pool_maxsize=100,
    pool_block=False,
    max_retries=2
)
session.mount('http://', adapter)
session.mount('https://', adapter)

# 预加载favicon
try:
    icon_r = session.get('https://hunshcn.github.io/gh-proxy/favicon.ico', timeout=10).content
except Exception:
    icon_r = b''
exp1 = re.compile(r'^(?:https?://)?github\.com/(?P<author>.+?)/(?P<repo>.+?)/(?:releases|archive)/.*$')
exp2 = re.compile(r'^(?:https?://)?github\.com/(?P<author>.+?)/(?P<repo>.+?)/(?:blob|raw)/.*$')
exp3 = re.compile(r'^(?:https?://)?github\.com/(?P<author>.+?)/(?P<repo>.+?)/(?:info|git-).*$')
exp4 = re.compile(r'^(?:https?://)?raw\.(?:githubusercontent|github)\.com/(?P<author>.+?)/(?P<repo>.+?)/.+?/.+$')
exp5 = re.compile(r'^(?:https?://)?gist\.(?:githubusercontent|github)\.com/(?P<author>.+?)/.+?/.+$')

requests.sessions.default_headers = lambda: CaseInsensitiveDict()


@app.route('/')
def index():
    if 'q' in request.args:
        return redirect('/' + request.args.get('q'))
    return render_template('index.html')


@app.route('/favicon.ico')
def icon():
    return Response(icon_r, content_type='image/vnd.microsoft.icon')


@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'ok',
        'service': 'gh-proxy',
        'version': '1.1.0',
        'cdn_enabled': jsdelivr == 1,
        'preferred_cdn': PREFERRED_CDN
    })


@app.route('/api/config')
def api_config():
    """获取配置信息API"""
    return jsonify({
        'cdn_sources': CDN_SOURCES,
        'preferred_cdn': PREFERRED_CDN,
        'cdn_enabled': jsdelivr == 1,
        'size_limit_mb': size_limit // (1024 * 1024)
    })


def iter_content(self, chunk_size=1, decode_unicode=False):
    """rewrite requests function, set decode_content with False"""

    def generate():
        # Special case for urllib3.
        if hasattr(self.raw, 'stream'):
            try:
                for chunk in self.raw.stream(chunk_size, decode_content=False):
                    yield chunk
            except ProtocolError as e:
                raise ChunkedEncodingError(e)
            except DecodeError as e:
                raise ContentDecodingError(e)
            except ReadTimeoutError as e:
                raise ConnectionError(e)
        else:
            # Standard file-like object.
            while True:
                chunk = self.raw.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        self._content_consumed = True

    if self._content_consumed and isinstance(self._content, bool):
        raise StreamConsumedError()
    elif chunk_size is not None and not isinstance(chunk_size, int):
        raise TypeError("chunk_size must be an int, it is instead a %s." % type(chunk_size))
    # simulate reading small chunks of the content
    reused_chunks = iter_slices(self._content, chunk_size)

    stream_chunks = generate()

    chunks = reused_chunks if self._content_consumed else stream_chunks

    if decode_unicode:
        chunks = stream_decode_response_unicode(chunks, self)

    return chunks


def check_url(u):
    for exp in (exp1, exp2, exp3, exp4, exp5):
        m = exp.match(u)
        if m:
            return m
    return False


@app.route('/<path:u>', methods=['GET', 'POST'])
def handler(u):
    u = u if u.startswith('http') else 'https://' + u
    if u.rfind('://', 3, 9) == -1:
        u = u.replace('s:/', 's://', 1)  # uwsgi会将//传递为/
    pass_by = False
    m = check_url(u)
    if m:
        m = tuple(m.groups())
        if white_list:
            for i in white_list:
                if m[:len(i)] == i or i[0] == '*' and len(m) == 2 and m[1] == i[1]:
                    break
            else:
                return Response('Forbidden by white list.', status=403)
        for i in black_list:
            if m[:len(i)] == i or i[0] == '*' and len(m) == 2 and m[1] == i[1]:
                return Response('Forbidden by black list.', status=403)
        for i in pass_list:
            if m[:len(i)] == i or i[0] == '*' and len(m) == 2 and m[1] == i[1]:
                pass_by = True
                break
    else:
        return Response('Invalid input.', status=403)

    if (jsdelivr or pass_by) and exp2.match(u):
        u = u.replace('/blob/', '@', 1).replace('github.com', 'cdn.jsdelivr.net/gh', 1)
        return redirect(u)
    elif (jsdelivr or pass_by) and exp4.match(u):
        u = re.sub(r'(\.com/.*?/.+?)/(.+?/)', r'\1@\2', u, 1)
        _u = u.replace('raw.githubusercontent.com', 'cdn.jsdelivr.net/gh', 1)
        u = u.replace('raw.github.com', 'cdn.jsdelivr.net/gh', 1) if _u == u else _u
        return redirect(u)
    else:
        if exp2.match(u):
            u = u.replace('/blob/', '/raw/', 1)
        if pass_by:
            url = u + request.url.replace(request.base_url, '', 1)
            if url.startswith('https:/') and not url.startswith('https://'):
                url = 'https://' + url[7:]
            return redirect(url)
        u = quote(u, safe='/:')
        return proxy(u)


def proxy(u, allow_redirects=False):
    headers = {}
    r_headers = dict(request.headers)
    
    # 清理不需要的请求头
    sensitive_headers = ['Host', 'X-Forwarded-For', 'X-Real-IP']
    for h in sensitive_headers:
        if h in r_headers:
            r_headers.pop(h)
    
    try:
        url = u + request.url.replace(request.base_url, '', 1)
        if url.startswith('https:/') and not url.startswith('https://'):
            url = 'https://' + url[7:]
        
        logger.info(f"Proxying request: {request.method} {url}")
        
        r = session.request(
            method=request.method,
            url=url,
            data=request.data,
            headers=r_headers,
            stream=True,
            allow_redirects=allow_redirects,
            timeout=request_timeout
        )
        headers = dict(r.headers)
        
        # 移除敏感响应头
        hop_by_hop_headers = [
            'connection', 'keep-alive', 'proxy-authenticate', 
            'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 'upgrade'
        ]
        for h in hop_by_hop_headers:
            headers.pop(h, None)
            headers.pop(h.title(), None)
        
        # 添加缓存头
        if r.status_code == 200:
            headers['Cache-Control'] = 'public, max-age=86400'  # 缓存1天
        
        if 'Content-length' in r.headers and int(r.headers['Content-length']) > size_limit:
            logger.info(f"File exceeds size limit, redirecting: {url}")
            return redirect(u + request.url.replace(request.base_url, '', 1))

        def generate():
            try:
                for chunk in iter_content(r, chunk_size=CHUNK_SIZE):
                    yield chunk
            except Exception as e:
                logger.warning(f"Stream interrupted: {str(e)}")
                raise

        if 'Location' in r.headers:
            _location = r.headers.get('Location')
            if check_url(_location):
                headers['Location'] = '/' + _location
            else:
                return proxy(_location, True)

        return Response(generate(), headers=headers, status=r.status_code)
    except requests.exceptions.Timeout:
        logger.error(f"Request timeout: {u}")
        return Response('Request timeout - please try again later', status=504)
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error: {u}")
        return Response('Connection failed - please check your network', status=503)
    except Exception as e:
        logger.error(f"Server error for {u}: {str(e)}", exc_info=True)
        return Response('Server error - please try again later', status=500)


app.debug = DEBUG

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, threaded=True)
