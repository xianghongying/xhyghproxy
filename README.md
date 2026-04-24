# GitHub Proxy - GitHub资源加速服务

[![GitHub license](https://img.shields.io/github/license/hunshcn/gh-proxy.svg)](https://github.com/hunshcn/gh-proxy/blob/master/LICENSE)
[![Docker Pulls](https://img.shields.io/docker/pulls/x120952576/xhyghproxy.svg)](https://hub.docker.com/r/x120952576/xhyghproxy)

🔄 **GitHub 文件、Release、仓库 加速下载代理服务**

---

## ✨ 功能特性

| 特性 | 说明 |
|------|------|
| 🚀 **多CDN支持** | jsDelivr / ghproxy / GitMirror 多源智能切换 |
| ⚡ **性能优化** | 连接池复用、gzip压缩、大文件传输优化 |
| 🔒 **安全加固** | 速率限制、CORS支持、请求头过滤、Debug模式可控 |
| 📊 **健康检查** | 内置健康检查端点，支持容器自动恢复 |
| 🎨 **友好UI** | 一键复制链接、实时验证、快捷键支持、Toast通知 |
| ⚙️ **灵活配置** | 所有配置通过环境变量，无需修改代码 |
| 📋 **黑白名单** | 支持仓库级、用户级访问控制 |
| 🐳 **容器优化** | 健康检查、日志轮转、时区设置 |

---

## 🚀 快速开始

### Docker 镜像构建

```shell
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --cache-from=type=local,src=/root/.buildx-cache \
    --cache-to=type=local,dest=/root/.buildx-cache,mode=max \
    -t registry.cn-hangzhou.aliyuncs.com/xhyimages/xhyghproxy:v1.0.1 \
    --push .
```

### Docker 一键部署

```bash
docker run -d \
  --name xhyghproxy \
  -p 8001:80 \
  --restart always \
  -e TZ=Asia/Shanghai \
  -e JSDELIVR_ENABLE=1 \
  x120952576/xhyghproxy:latest
```

### Docker Compose 部署（推荐）

```bash
# 下载配置
wget https://raw.githubusercontent.com/your-repo/xhyghproxy/main/docker-compose.yml

# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f
```

访问：http://your-server-ip:8001

---

## ⚙️ 配置说明

所有配置通过环境变量进行，无需修改代码。复制 `.env.example` 为 `.env` 并自定义：

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `FLASK_DEBUG` | `false` | Debug模式，生产环境保持关闭 |
| `JSDELIVR_ENABLE` | `0` | CDN重定向开关 (0=关闭, 1=开启) |
| `PREFERRED_CDN` | `jsdelivr` | 首选CDN源 (jsdelivr/ghproxy/gitmirror) |
| `NGINX_LISTEN_PORT` | `80` | Nginx监听端口 |
| `FLASK_PORT` | `80` | Flask监听端口 |
| `REQUEST_TIMEOUT` | `30` | 请求超时时间(秒) |
| `SIZE_LIMIT` | `999GB` | 文件大小限制(字节) |
| `MAX_CONTENT_LENGTH` | `100MB` | 请求体最大限制(字节) |
| `RATE_LIMIT` | `200 per minute` | 速率限制 |
| `RATE_LIMIT_ENABLE` | `true` | 是否开启速率限制 |
| `TZ` | `Asia/Shanghai` | 时区设置 |

### 访问控制名单

```bash
# 格式示例（每行一个规则，# 开头为注释）
WHITE_LIST="user1
user1/repo1
*/repo1"

BLACK_LIST="baduser
baduser/badrepo"
```

---

## 📡 API 文档

### 健康检查
```http
GET /health
```

**响应示例：**
```json
{
  "status": "ok",
  "service": "gh-proxy",
  "version": "1.1.0",
  "cdn_enabled": true,
  "preferred_cdn": "jsdelivr"
}
```

### 获取配置
```http
GET /api/config
```

### 代理请求
```http
GET /https://github.com/owner/repo/releases/download/v1.0/file.tar.gz
```

支持的URL模式：
- `github.com/owner/repo/releases/...`
- `github.com/owner/repo/archive/...`
- `github.com/owner/repo/blob/...`
- `github.com/owner/repo/raw/...`
- `raw.githubusercontent.com/owner/repo/...`
- `gist.github.com/owner/...`

---

## 🎯 使用示例

### 合法输入格式

```
分支源码：https://github.com/hunshcn/project/archive/master.zip
Release源码：https://github.com/hunshcn/project/archive/v0.1.0.tar.gz
Release文件：https://github.com/hunshcn/project/releases/download/v0.1.0/example.zip
分支文件：https://github.com/hunshcn/project/blob/master/filename
原始文件：https://raw.githubusercontent.com/owner/repo/main/file.py
```

### 加速效果

```
原始地址：https://github.com/kubeedge/kubeedge/releases/download/v1.20.0/kubeedge-v1.20.0-linux-amd64.tar.gz
加速地址：http://gh.yourdomain.com/https://github.com/kubeedge/kubeedge/releases/download/v1.20.0/kubeedge-v1.20.0-linux-amd64.tar.gz
```

### 快捷键

- `Ctrl/Cmd + K` - 快速聚焦输入框

---

## 🏗️ 本地开发

```bash
# 克隆项目
git clone https://github.com/your-repo/xhyghproxy.git
cd xhyghproxy

# 安装依赖
pip install flask requests flask-cors flask-limiter uwsgi

# 运行开发服务器
cd app
python main.py
```

---

## 📦 构建镜像

```bash
# 构建镜像
docker build -t xhyghproxy:local .

# 测试运行
docker run --rm -p 8001:80 --name ghproxy-test xhyghproxy:local
```

---

## 📝 更新日志

详细的版本变更记录请查看 [CHANGELOG.md](./CHANGELOG.md)

### v1.1.0 (2025-04-25)
- ✨ 多CDN源支持
- ✨ 复制到剪贴板功能
- ✨ 健康检查端点
- ✨ 速率限制保护
- ⚡ 连接池性能优化
- 🔒 安全增强
- 🎨 UI全面升级

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

---

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](./LICENSE) 文件了解详情。

---

## 🙏 致谢

- 原始项目：[hunshcn/gh-proxy](https://github.com/hunshcn/gh-proxy)
- 基础镜像：[tiangolo/uwsgi-nginx-docker](https://github.com/tiangolo/uwsgi-nginx-docker)
- CDN服务：jsDelivr, ghproxy, GitMirror

---

## 📞 支持

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至 xhy@itzgr.cn

---

**⭐ 如果这个项目对你有帮助，欢迎点个 Star 支持一下！**
