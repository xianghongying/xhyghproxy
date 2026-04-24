FROM docker.1ms.run/tiangolo/uwsgi-nginx:python3.12

LABEL maintainer="xianghy <xhy@itzgr.cn>"

# 安装Python依赖
RUN pip install --no-cache-dir flask requests uwsgi flask-cors flask-limiter

# 时区设置
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./app /app
WORKDIR /app

ENV PYTHONPATH=/app

# 配置环境变量默认值
ENV FLASK_DEBUG=false
ENV JSDELIVR_ENABLE=0
ENV LISTEN_HOST=0.0.0.0
ENV FLASK_PORT=80
ENV NGINX_LISTEN_PORT=80
ENV REQUEST_TIMEOUT=30
ENV RATE_LIMIT="200 per minute"
ENV RATE_LIMIT_ENABLE=true
ENV MAX_CONTENT_LENGTH=104857600

RUN mv /entrypoint.sh /uwsgi-nginx-entrypoint.sh
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 创建日志目录
RUN mkdir -p /var/log/gh-proxy && \
    chown -R www-data:www-data /var/log/gh-proxy

ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

CMD ["/start.sh"]
