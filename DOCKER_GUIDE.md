# 🐳 Docker Compose 部署指南

## 概述

`docker-compose.yml` 是一个容器编排配置文件，用于定义和运行多容器的 RAG 系统。它可以让你通过一个命令启动整个应用栈，包括 RAG API 服务、可选的 Nginx 反向代理和 Redis 缓存。

## 🏗️ 架构组件

### 核心服务

#### 1. rag-api (主服务)
- **作用**: RAG 系统的核心 API 服务
- **端口**: 8000
- **功能**: 提供问答、知识库管理、系统监控等 API 接口

#### 2. nginx (可选)
- **作用**: 反向代理和负载均衡
- **端口**: 80 (HTTP), 443 (HTTPS)
- **功能**: SSL 终止、静态文件服务、请求转发

#### 3. redis (可选)
- **作用**: 缓存服务
- **端口**: 6379
- **功能**: 查询结果缓存、会话存储

## 📋 配置详解

### 主服务配置 (rag-api)

```yaml
rag-api:
  build: .                    # 从当前目录的 Dockerfile 构建镜像
  container_name: rag-api     # 容器名称
  ports:
    - "8000:8000"            # 端口映射：主机端口:容器端口
  volumes:
    # 数据目录挂载
    - ./data:/app/data
    - ./local_models:/app/local_models
    - ./my_chromadb_vector_store:/app/my_chromadb_vector_store
    # 配置文件挂载（只读）
    - ./.env:/app/.env:ro
  environment:
    - LOG_LEVEL=INFO         # 日志级别
    - WORKERS=4              # 工作进程数
  restart: unless-stopped    # 重启策略
  healthcheck:               # 健康检查
    test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
    interval: 30s            # 检查间隔
    timeout: 10s             # 超时时间
    retries: 3               # 重试次数
    start_period: 60s        # 启动等待时间
```

### 可选服务配置

#### Nginx 反向代理
```yaml
nginx:
  image: nginx:alpine        # 使用轻量级 Alpine 镜像
  container_name: rag-nginx
  ports:
    - "80:80"               # HTTP 端口
    - "443:443"             # HTTPS 端口
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf:ro  # Nginx 配置
    - ./ssl:/etc/nginx/ssl:ro                # SSL 证书
  depends_on:
    - rag-api               # 依赖 rag-api 服务
  profiles:
    - with-nginx            # 使用 profile 控制启动
```

#### Redis 缓存
```yaml
redis:
  image: redis:alpine
  container_name: rag-redis
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data      # 持久化数据
  profiles:
    - with-cache            # 使用 profile 控制启动
```

## 🚀 使用方法

### 基本使用

#### 1. 准备环境

```bash
# 确保 Docker 和 Docker Compose 已安装
docker --version
docker-compose --version

# 进入项目目录
cd rag_example
```

#### 2. 启动基本服务

```bash
# 启动 RAG API 服务（仅核心服务）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f rag-api
```

#### 3. 访问服务

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/v1/health
- **问答接口**: http://localhost:8000/api/v1/ask

### 高级使用

#### 启动完整服务栈（包含 Nginx 和 Redis）

```bash
# 启动所有服务
docker-compose --profile with-nginx --profile with-cache up -d

# 或者分别启动
docker-compose --profile with-nginx up -d  # 启动 Nginx
docker-compose --profile with-cache up -d  # 启动 Redis
```

#### 开发模式

```bash
# 构建并启动（强制重新构建）
docker-compose up --build -d

# 查看实时日志
docker-compose logs -f

# 重启特定服务
docker-compose restart rag-api
```

#### 生产模式

```bash
# 后台启动所有服务
docker-compose --profile with-nginx --profile with-cache up -d

# 设置自动重启
docker-compose up -d --restart unless-stopped
```

## 🔧 配置文件

### 创建必要的配置文件

#### 1. Nginx 配置 (nginx.conf)

```bash
# 创建 Nginx 配置文件
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream rag_api {
        server rag-api:8000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://rag_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF
```

#### 2. 环境变量文件 (.env)

```bash
# 确保 .env 文件存在
cat > .env << 'EOF'
# LLM API 配置
DeepSeek_api_key="sk-your-api-key-here"
DeepSeek_base_url="https://api.deepseek.com"
DeepSeek_model_name="deepseek-chat"

# 服务配置
LOG_LEVEL=INFO
WORKERS=4
EOF
```

## 📊 监控和管理

### 服务状态监控

```bash
# 查看所有服务状态
docker-compose ps

# 查看服务资源使用情况
docker stats

# 查看特定服务日志
docker-compose logs rag-api
docker-compose logs nginx
docker-compose logs redis
```

### 健康检查

```bash
# 检查 RAG API 健康状态
curl http://localhost:8000/api/v1/health

# 通过 Nginx 检查（如果启用）
curl http://localhost/api/v1/health

# 检查 Docker 健康状态
docker-compose ps
```

### 服务管理

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 重启服务
docker-compose restart

# 更新服务
docker-compose pull
docker-compose up -d
```

## 🔍 故障排除

### 常见问题

#### 1. 服务启动失败

```bash
# 查看详细日志
docker-compose logs rag-api

# 检查容器状态
docker-compose ps

# 重新构建镜像
docker-compose build --no-cache rag-api
```

#### 2. 端口冲突

```bash
# 检查端口占用
netstat -tulpn | grep :8000

# 修改端口映射
# 在 docker-compose.yml 中修改：
ports:
  - "8001:8000"  # 使用不同的主机端口
```

#### 3. 数据持久化问题

```bash
# 检查数据卷
docker volume ls

# 查看数据卷详情
docker volume inspect rag_example_redis_data

# 备份数据
docker run --rm -v rag_example_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_backup.tar.gz -C /data .
```

#### 4. 网络连接问题

```bash
# 查看 Docker 网络
docker network ls

# 检查容器网络连接
docker-compose exec rag-api ping nginx
docker-compose exec rag-api ping redis
```

## 🚀 部署最佳实践

### 生产环境部署

#### 1. 安全配置

```yaml
# 在 docker-compose.yml 中添加安全配置
services:
  rag-api:
    # ... 其他配置
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    user: "1000:1000"  # 非 root 用户
```

#### 2. 资源限制

```yaml
services:
  rag-api:
    # ... 其他配置
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

#### 3. 日志管理

```yaml
services:
  rag-api:
    # ... 其他配置
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 扩展配置

#### 添加数据库服务

```yaml
services:
  postgres:
    image: postgres:13
    container_name: rag-postgres
    environment:
      POSTGRES_DB: rag_db
      POSTGRES_USER: rag_user
      POSTGRES_PASSWORD: rag_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

#### 添加监控服务

```yaml
services:
  prometheus:
    image: prom/prometheus
    container_name: rag-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    container_name: rag-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 📝 维护和更新

### 定期维护

```bash
# 清理未使用的镜像和容器
docker system prune -a

# 更新镜像
docker-compose pull
docker-compose up -d

# 备份数据
docker-compose exec rag-api tar czf /tmp/backup.tar.gz /app/my_chromadb_vector_store
docker cp rag-api:/tmp/backup.tar.gz ./backup_$(date +%Y%m%d).tar.gz
```

### 版本升级

```bash
# 1. 停止服务
docker-compose down

# 2. 备份数据
docker run --rm -v rag_example_my_chromadb_vector_store:/data -v $(pwd):/backup alpine tar czf /backup/data_backup.tar.gz -C /data .

# 3. 更新代码和配置
git pull  # 或其他更新方式

# 4. 重新构建和启动
docker-compose build --no-cache
docker-compose up -d

# 5. 验证服务
curl http://localhost:8000/api/v1/health
```

## 🎯 总结

Docker Compose 为 RAG 系统提供了：

1. **简化部署**: 一个命令启动整个应用栈
2. **环境一致性**: 开发、测试、生产环境保持一致
3. **服务编排**: 自动管理服务依赖和启动顺序
4. **扩展性**: 轻松添加新的服务组件
5. **可维护性**: 统一的配置管理和服务监控

通过 Docker Compose，你可以快速部署一个完整的、生产就绪的 RAG 系统！

---

## 🔗 相关文档

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 官方文档](https://docs.docker.com/compose/)
- [项目 README.md](./README.md)
- [使用指南 USAGE_GUIDE.md](./USAGE_GUIDE.md)