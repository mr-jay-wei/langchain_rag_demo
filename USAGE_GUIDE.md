# 🚀 RAG Web 服务使用指南

## 快速开始

### 1. 启动服务

```bash
# 开发模式启动（推荐用于测试）
python start_server.py --mode dev

# 或者直接运行
python app.py

# 生产模式启动
python start_server.py --mode prod --workers 4
```

### 2. 访问 API 文档

启动服务后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 3. 测试服务

```bash
# 快速测试
python run_tests.py --test-type quick

# 完整测试（会自动启动和停止服务）
python run_tests.py --test-type full

# 运行所有测试
python run_tests.py --test-type all
```

## 主要 API 接口

### 🔍 问答查询

**基本查询**
```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是机器学习？",
    "options": {
      "enable_rewriting": true,
      "enable_hybrid_search": true,
      "max_results": 5
    }
  }'
```

**分类查询**
```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python编程语言的特点",
    "categories": ["technical", "general"],
    "options": {
      "enable_rewriting": true,
      "max_results": 3
    }
  }'
```

**批量查询**
```bash
curl -X POST "http://localhost:8000/api/v1/ask/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      {"query": "什么是人工智能？"},
      {"query": "RAG系统的优势"},
      {"query": "如何配置向量数据库？"}
    ],
    "options": {"parallel": true}
  }'
```

### 📚 知识库管理

**获取知识库状态**
```bash
curl -X GET "http://localhost:8000/api/v1/knowledge/status"
```

**触发知识库同步**
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/sync"
```

### 🏥 系统监控

**健康检查**
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

**服务指标**
```bash
curl -X GET "http://localhost:8000/api/v1/metrics"
```

## Python 客户端示例

### 基本使用

```python
import requests

# 创建会话
session = requests.Session()
base_url = "http://localhost:8000"

# 问答查询
response = session.post(f"{base_url}/api/v1/ask", json={
    "query": "什么是深度学习？",
    "options": {
        "enable_rewriting": True,
        "enable_hybrid_search": True,
        "max_results": 5
    }
})

if response.status_code == 200:
    result = response.json()
    if result['success']:
        print(f"回答: {result['data']['answer']}")
        print(f"查询时间: {result['data']['query_info']['search_time']}秒")
    else:
        print(f"查询失败: {result['error']}")
```

### 使用提供的客户端工具

```python
# 使用交互式客户端
python test_api_client.py

# 运行 API 使用示例
python api_usage_examples.py
```

## JavaScript 客户端示例

```javascript
// 基本查询
async function askQuestion(query) {
    const response = await fetch('http://localhost:8000/api/v1/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: query,
            options: {
                enable_rewriting: true,
                enable_hybrid_search: true,
                max_results: 5
            }
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        console.log('回答:', result.data.answer);
        console.log('查询时间:', result.data.query_info.search_time, '秒');
    } else {
        console.error('查询失败:', result.error);
    }
}

// 使用示例
askQuestion('什么是机器学习？');
```

## 容器化部署

### Docker 部署

```bash
# 构建镜像
docker build -t rag-api .

# 运行容器
docker run -d \
  --name rag-api \
  -p 8000:8000 \
  -v ./data:/app/data \
  -v ./local_models:/app/local_models \
  -v ./my_chromadb_vector_store:/app/my_chromadb_vector_store \
  rag-api
```

### Docker Compose 部署

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f rag-api

# 停止服务
docker-compose down
```

## 配置说明

### 环境变量配置

创建 `.env` 文件：

```env
# LLM API 配置
DeepSeek_api_key="sk-xxxxxxxxxxxxxxxxxxxx"
DeepSeek_base_url="https://api.deepseek.com"
DeepSeek_model_name="deepseek-chat"

# 服务配置
LOG_LEVEL=INFO
WORKERS=4
```

### 模型配置

在 `rag/config.py` 中配置模型路径：

```python
# 嵌入模型路径
EMBEDDING_MODEL_NAME = "local_models/bge-small-zh-v1.5"

# 重排序模型路径
RERANKER_MODEL_NAME = "local_models/bge-reranker-base"

# 向量数据库路径
VECTOR_STORE_PATH = "./my_chromadb_vector_store"

# 数据目录
DATA_DIRECTORY = "./data"
```

## 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   # 检查依赖
   uv sync
   
   # 检查端口占用
   netstat -an | findstr :8000
   
   # 查看详细错误
   python start_server.py --mode dev
   ```

2. **RAG Pipeline 初始化失败**
   ```bash
   # 检查模型文件
   ls -la local_models/
   
   # 检查配置文件
   cat rag/config.py
   
   # 检查环境变量
   cat .env
   ```

3. **查询返回错误**
   ```bash
   # 检查数据目录
   ls -la data/
   
   # 检查向量数据库
   ls -la my_chromadb_vector_store/
   
   # 手动同步知识库
   curl -X POST "http://localhost:8000/api/v1/knowledge/sync"
   ```

### 性能优化

1. **提高查询速度**
   - 减少 `RETRIEVER_TOP_K` 参数
   - 禁用问题改写：`enable_rewriting: false`
   - 使用纯向量检索：`enable_hybrid_search: false`

2. **提高准确性**
   - 增加 `RERANKER_TOP_N` 参数
   - 启用混合检索：`enable_hybrid_search: true`
   - 启用问题改写：`enable_rewriting: true`

3. **内存优化**
   - 减少工作进程数：`--workers 2`
   - 清理向量数据库缓存
   - 定期重启服务

## 监控和日志

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8000/api/v1/health

# 检查服务指标
curl http://localhost:8000/api/v1/metrics
```

### 日志查看

```bash
# 查看服务日志（如果使用 Docker）
docker logs rag-api

# 查看实时日志
docker logs -f rag-api
```

## 扩展开发

### 添加新的 API 端点

在 `app.py` 中添加新的路由：

```python
@app.post("/api/v1/custom", response_model=QueryResponse)
async def custom_endpoint(request: CustomRequest):
    """自定义端点"""
    # 实现自定义逻辑
    pass
```

### 集成到现有系统

```python
# 作为微服务集成
import requests

class RAGService:
    def __init__(self, base_url="http://rag-api:8000"):
        self.base_url = base_url
    
    def ask(self, question):
        response = requests.post(f"{self.base_url}/api/v1/ask", 
                               json={"query": question})
        return response.json()

# 使用示例
rag = RAGService()
result = rag.ask("什么是人工智能？")
```

## 支持和反馈

如果遇到问题或有改进建议，请：

1. 查看 `README.md` 中的详细文档
2. 运行测试脚本进行诊断：`python run_tests.py --test-type all`
3. 检查 API 文档：http://localhost:8000/docs
4. 查看示例代码：`python api_usage_examples.py`

---

🎉 **恭喜！** 您已经成功部署了企业级的 RAG Web 服务！