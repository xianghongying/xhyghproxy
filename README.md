
### 使用方式

+ Docker部署  

```shell
docker run -d --name="gh-proxy-py" \
  -p 0.0.0.0:80:80 \
  --restart=always \
  x120952576/xhyghproxy:v1
```

+ Docker Compose部署

```shell
cat > docker-compose.yaml <<EOF
services:
  gh-proxy:
    restart: always
    image: x120952576/xhyghproxy:v1
    ports:
      - "8001:80"
EOF

docker compose up -d
```

<font color=red>提示：Docker Compose 安装可参考 <a href="https://www.cnblogs.com/itzgr/p/10171046.html" target="_blank">009.Docker Compose部署及基础使用</a>
</font> 

<font color=red>提示：国内用户可将镜像替换为： uhub.service.ucloud.cn/imxhy/xhyghproxy:v1
</font> 
