# Changelog

## [1.1.0] - 2025-04-25

### ✨ 新增功能
- 多CDN源支持 (jsDelivr, ghproxy, GitMirror)
- 复制到剪贴板功能
- 健康检查端点 `/health`
- 配置API `/api/config`
- 速率限制保护
- CORS跨域支持
- 环境变量配置支持
- Docker健康检查
- 键盘快捷键支持 (Ctrl/Cmd + K 聚焦输入框)
- 实时URL验证反馈

### ⚡ 性能优化
- 使用连接池提升请求性能
- 增加chunk大小到64KB优化大文件传输
- 添加HTTP缓存头
- gzip压缩支持
- 移除敏感请求头/响应头

### 🔒 安全增强
- 请求体大小限制 (默认100MB)
- 生产环境默认关闭debug模式
- 敏感请求头过滤
- 优雅的错误处理

### 🐛 修复
- 修复uwsgi.ini重复配置问题
- 修复请求超时无响应问题
- 改进错误提示信息

### 📦 运维优化
- docker-compose.yml配置
- 日志文件轮转配置
- 时区设置 (Asia/Shanghai)
- 详细的环境变量示例
- .gitignore配置

### 🎨 UI改进
- 新增复制按钮
- 新增第四张功能卡片
- Toast通知
- 输入验证实时反馈
- 移动端响应式优化
- 平滑动画效果

---

## [1.0.0] - 原始版本
- 基础GitHub代理功能
- Flask + uWSGI + Nginx架构
- 黑白名单支持
- jsDelivr CDN支持
