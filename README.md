# 🌊 流式 RAG 问答系统

一个基于 LangChain 的智能文档问答系统，支持流式响应、提示词解耦、多模式检索等企业级特性。

## ✨ 核心特性

### 🚀 流式响应系统

- **真正的流式输出**：只有答案生成阶段是流式的，避免不必要的延迟
- **智能流式检测**：自动检测 LLM 是否支持流式调用（`astream`）
- **优雅降级**：不支持流式时自动回退到模拟流式输出
- **实时状态更新**：处理过程中提供清晰的状态反馈

### 🔧 提示词管理系统

- **完全解耦**：提示词与代码 100%分离，存储在独立的`.txt`文件中
- **缓存机制**：内置缓存提高性能，避免重复文件读取
- **动态重载**：支持运行时更新提示词，无需重启服务
- **统一管理**：集中管理所有提示词，便于版本控制和团队协作

### 🎯 多模式 RAG 流程

- **同步模式**：`RagPipeline` - 传统同步处理
- **异步模式**：`AsyncRagPipeline` - 高并发异步处理
- **流式模式**：`StreamingRagPipeline` - 实时流式响应

### 🧠 智能回答来源识别

- **知识库回答**：`"根据知识库资料："` + 基于检索文档的精准回答
- **大模型知识回答**：`"知识库资料未检索到内容，使用大模型训练知识回复："` + 基于训练知识的通用回答
- **无法回答**：`"根据提供的资料，我无法回答该问题。"` - 对于预测类、隐私类等无法回答的问题
- **智能判断**：系统自动判断回答来源，为用户提供透明的信息来源标识

### 🔍 智能检索系统

- **混合检索**：向量检索 + BM25 关键字检索
- **智能重排序**：使用 CrossEncoder 模型提高检索精度
- **问题改写**：自动生成多个相关问题提高检索覆盖面
- **分类检索**：支持按文档类别进行精准检索

### 🧠 短期记忆系统

- **对话历史保存**：自动保存用户问题和 AI 回答
- **智能长度管理**：总字符长度不超过配置限制（默认 100k 字符）
- **自动清理策略**：超出限制时自动移除最旧的对话记录
- **上下文整合**：将对话历史与检索结果整合，AI 能理解代词引用
- **灵活配置**：支持启用/禁用、不同清理策略、最小保留轮数等

### 📊 企业级数据管理

- **智能同步**：自动检测文件变化，增量更新向量数据库
- **多数据源**：支持多个数据源的分类管理
- **文件监控**：基于文件哈希的变更检测
- **批量处理**：支持大规模文档的并发处理

## 🏗️ 系统架构

```
rag_example/
├── rag
│   ├── prompts
│   │   ├── qa_prompt.txt
│   │   ├── query_rewrite_prompt.txt
│   │   └── README.md
│   ├── __init__.py
│   ├── async_pipeline.py
│   ├── config.py
│   ├── hot_reload_manager.py
│   ├── memory_manager.py
│   ├── pipeline.py
│   ├── prompt_manager.py
│   └── streaming_pipeline.py
├── .env_example
├── .gitignore
├── .python-version
├── async_main.py
├── main.py
├── pyproject.toml
├── README.md
├── sse_api_server.py
├── streaming_main.py
└── streaming_web_demo.py
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 使用uv安装依赖（推荐）
uv sync

# 或者从requirements.txt安装
uv pip install -r requirements.txt

# 配置环境变量（创建 .env 文件）
CLOUD_INFINI_API_KEY=your_api_key_here
CLOUD_BASE_URL=https://cloud.infini-ai.com/maas/v1/
CLOUD_MODEL_NAME=deepseek-chat
```

### 2. 数据准备

```bash
# 将文档放入 data 目录
mkdir -p data
cp your_documents.txt data/

# 同步数据到向量数据库
uv run main.py
```

### 3. 启动 Web 演示

```bash
# 启动流式Web演示
uv run streaming_web_demo.py

# 访问 http://localhost:8000
```

## 💻 使用示例

### 基础问答

```python
from rag.pipeline import RagPipeline

# 初始化RAG系统
rag = RagPipeline()

# 同步数据
rag.sync_data_directory()

# 问答
result = rag.ask("什么是机器学习？")
print(result['result'])
```

### 异步问答

```python
import asyncio
from rag.async_pipeline import AsyncRagPipeline

async def main():
    # 初始化异步RAG系统
    rag = AsyncRagPipeline()

    # 异步同步数据
    await rag.sync_data_directory_async()

    # 异步问答
    result = await rag.ask_async("什么是深度学习？")
    print(result['result'])

asyncio.run(main())
```

### 流式问答

```python
import asyncio
from rag.streaming_pipeline import StreamingRagPipeline

async def main():
    # 初始化流式RAG系统
    rag = StreamingRagPipeline()

    # 流式问答
    async for event in rag.ask_stream("解释一下神经网络"):
        if event.type.value == "generation_chunk":
            print(event.data["chunk"], end="", flush=True)
        elif event.type.value == "processing":
            print(f"\n🔍 {event.data['message']}")

asyncio.run(main())
```

### 智能回答来源识别示例

```python
import asyncio
from rag.streaming_pipeline import StreamingRagPipeline

async def demo_answer_sources():
    rag = StreamingRagPipeline()

    # 测试不同类型的问题
    test_cases = [
        {
            "question": "什么是Python？",
            "expected": "根据知识库资料：",
            "description": "知识库中有相关文档"
        },
        {
            "question": "埃及有多少座金字塔？",
            "expected": "知识库资料未检索到内容，使用大模型训练知识回复：",
            "description": "知识库无关但大模型知道"
        },
        {
            "question": "请帮我预测明天的彩票号码",
            "expected": "根据提供的资料，我无法回答该问题。",
            "description": "大模型也无法回答"
        }
    ]

    for case in test_cases:
        print(f"\n问题: {case['question']}")
        print(f"说明: {case['description']}")
        print("回答: ", end="")

        async for event in rag.ask_stream(case['question']):
            if event.type.value == "generation_chunk":
                print(event.data["chunk"], end="", flush=True)
        print("\n" + "-" * 50)

asyncio.run(demo_answer_sources())
```

### 分类检索

```python
# 按类别检索
result = rag.ask_with_categories(
    question="机器学习的应用场景",
    categories=["技术文档", "教程"]
)
```

### 提示词管理

```python
from rag.prompt_manager import prompt_manager

# 列出所有提示词
prompts = prompt_manager.list_available_prompts()
print(f"可用提示词: {prompts}")

# 重新加载提示词
prompt_manager.reload_prompt("qa_prompt")

# 保存新提示词
prompt_manager.save_prompt("custom_prompt", "自定义提示词内容")
```

### 短期记忆功能

```python
import asyncio
from rag.streaming_pipeline import StreamingRagPipeline
from rag.memory_manager import memory_manager

async def main():
    rag = StreamingRagPipeline()

    # 启用记忆的对话
    await rag.ask_stream("什么是人工智能？", use_memory=True)
    await rag.ask_stream("它有哪些应用？", use_memory=True)  # "它"会被理解为"人工智能"

    # 查看记忆统计
    stats = memory_manager.get_memory_stats()
    print(f"记忆统计: {stats}")

    # 搜索对话历史
    results = memory_manager.search_conversations("人工智能")
    print(f"搜索结果: {len(results)} 条")

asyncio.run(main())
```

## 🧠 短期记忆功能演示

### 运行演示脚本

```bash
# 运行完整的短期记忆功能演示
uv run demo_short_term_memory.py
```

**演示功能包括：**

- ✅ 基础记忆功能：自动保存对话历史，AI 能理解代词引用
- ✅ 记忆管理：查看统计、搜索历史、获取上下文
- ✅ 智能清理：演示长度限制和自动清理机制
- ✅ 不同模式：对比启用/禁用记忆的效果差异
- ✅ 上下文整合：展示记忆如何与检索结果整合

### 短期记忆配置

```python
# 在 rag/config.py 中配置短期记忆
ENABLE_SHORT_TERM_MEMORY = True           # 启用短期记忆
SHORT_TERM_MEMORY_MAX_LENGTH = 100_000    # 最大字符长度（100k）
MIN_CONVERSATION_ROUNDS = 1               # 最小保留轮数
MEMORY_CLEANUP_STRATEGY = "auto"          # 清理策略：auto/manual/sliding_window
SLIDING_WINDOW_SIZE = 20                  # 滑动窗口大小
```

### 记忆管理 API

```python
from rag.memory_manager import memory_manager

# 查看记忆统计
stats = memory_manager.get_memory_stats()
print(f"总对话轮数: {stats['total_conversations']}")
print(f"内存使用率: {stats['memory_usage_percent']:.1f}%")

# 搜索对话历史
results = memory_manager.search_conversations("人工智能", limit=5)
for idx, (pos, conv) in enumerate(results):
    print(f"{idx+1}. {conv.question[:30]}...")

# 导出/导入记忆
memory_manager.export_conversations("backup.json")
memory_manager.import_conversations("backup.json")

# 手动清理记忆
memory_manager.remove_old_conversations(keep_count=10)
memory_manager.clear_memory()  # 清空所有记忆
```

## 🔧 配置说明

### 核心配置 (`rag/config.py`)

```python
# 模型配置
EMBEDDING_MODEL_NAME = "BAAI/bge-small-zh-v1.5"
RERANKER_MODEL_NAME = "BAAI/bge-reranker-base"

# 检索配置
RETRIEVER_TOP_K = 5
RERANKER_TOP_N = 3
ENABLE_HYBRID_SEARCH = True

# 流式配置
ENABLE_QUERY_REWRITING = True
QUERY_REWRITE_COUNT = 3

# 企业级配置
ENABLE_ENTERPRISE_MODE = False
ENTERPRISE_DATA_SOURCES = {
    "docs": {
        "path": "data/docs",
        "category": "documentation",
        "description": "技术文档",
        "file_patterns": ["*.txt", "*.md"]
    }
}
```

### 提示词配置

直接编辑 `rag/prompts/` 目录下的 `.txt` 文件：

```bash
# 修改问答提示词
vim rag/prompts/qa_prompt.txt

# 修改问题改写提示词
vim rag/prompts/query_rewrite_prompt.txt
```

## 🌐 Web 演示特性

### 实时流式界面

- **WebSocket 连接**：实时双向通信
- **流式显示**：答案逐字符实时显示
- **状态反馈**：处理过程可视化
- **自动重连**：连接断开自动恢复

### 用户体验优化

- **响应式设计**：适配不同屏幕尺寸
- **连接状态显示**：实时显示连接状态
- **错误处理**：友好的错误提示
- **键盘快捷键**：支持回车发送

## 🔧 提示词运行时管理

### 演示脚本使用

```bash
# 运行完整的运行时更新演示
uv run demo_runtime_prompt_update.py
```

**演示功能包括：**

- ✅ 显示当前提示词内容和使用效果
- ✅ 运行时更新提示词内容
- ✅ 验证更新后的效果（无需重启服务）
- ✅ 演示手动重载功能
- ✅ 自动恢复原始提示词


### 实际应用场景


#### 场景 1：A/B 测试不同提示词

```python
# 创建测试脚本 test_prompts.py
import requests

# 版本A：严谨风格
prompt_a = "请严格按照文档内容回答用户问题..."

# 版本B：友好风格
prompt_b = "请用友好亲切的语气回答用户问题..."

# 切换到版本A并测试
requests.put("http://localhost:8001/api/prompts/qa_prompt",
            json={"content": prompt_a, "description": "测试严谨风格"})

# 切换到版本B并测试
requests.put("http://localhost:8001/api/prompts/qa_prompt",
            json={"content": prompt_b, "description": "测试友好风格"})
```

```bash
# 运行A/B测试
uv run test_prompts.py
```

## 🧪 测试与验证

### 运行测试

```bash
# 测试提示词管理器
uv run test_prompt_manager.py

# 验证提示词解耦
uv run verify_prompt_decoupling.py

# 测试智能回答来源识别功能
uv run test/test_answer_sources.py
```

### 智能回答来源识别测试

```bash
# 运行完整的回答来源测试
uv run test/test_answer_sources.py
```

**测试覆盖场景：**

1. **知识库相关问题** ✅

   - 问题：`"什么是Python？"`
   - 期望前缀：`"根据知识库资料："`
   - 验证：系统能从知识库找到相关文档并基于文档回答

2. **知识库无关但常识问题** ✅

   - 问题：`"埃及有多少座金字塔？"`
   - 期望前缀：`"知识库资料未检索到内容，使用大模型训练知识回复："`
   - 验证：知识库无相关内容时，使用大模型训练知识回答

3. **完全无法回答的问题** ✅
   - 问题：`"请帮我预测明天的彩票号码"`
   - 期望回复：`"根据提供的资料，我无法回答该问题。"`
   - 验证：对于预测类、隐私类问题，系统明确表示无法回答

**测试输出示例：**

```
🧪 测试不同回答来源的功能
============================================================

1. 测试: 知识库相关问题
   问题: 什么是Python？
   期望前缀: 根据知识库资料：
   --------------------------------------------------
   🚀 基于知识库文档生成答案
   根据知识库资料：Python是一种高级编程语言，具有简洁的语法和强大的功能...
   ✅ 前缀正确: 包含 '根据知识库资料：'
   🎯 测试结果: ✅ 通过

2. 测试: 知识库无关但常识问题
   问题: 埃及有多少座金字塔？
   期望前缀: 知识库资料未检索到内容，使用大模型训练知识回复：
   --------------------------------------------------
   🚀 知识库未找到相关资料，使用大模型训练知识回答
   知识库资料未检索到内容，使用大模型训练知识回复：埃及现存已知的金字塔数量约为118至138座...
   ✅ 前缀正确: 包含 '知识库资料未检索到内容，使用大模型训练知识回复：'
   🎯 测试结果: ✅ 通过

3. 测试: 完全无关的问题
   问题: 请帮我预测明天的彩票号码
   期望前缀: 根据提供的资料，我无法回答该问题。
   --------------------------------------------------
   🚀 知识库未找到相关资料，使用大模型训练知识回答
   根据提供的资料，我无法回答该问题。
   ✅ 前缀正确: 包含 '根据提供的资料，我无法回答该问题。'
   🎯 测试结果: ✅ 通过

🎉 所有测试完成！
```

### 性能测试

```bash
# 运行性能基准测试
uv run -c "
import time
import asyncio
from rag.streaming_pipeline import StreamingRagPipeline

async def benchmark():
    rag = StreamingRagPipeline()

    questions = [
        '什么是机器学习？',
        '深度学习的原理是什么？',
        '神经网络如何工作？'
    ]

    start_time = time.time()

    # 批量流式处理
    async for event in rag.batch_ask_stream(questions):
        if event.type.value == 'complete':
            break

    end_time = time.time()
    print(f'处理 {len(questions)} 个问题耗时: {end_time - start_time:.2f}秒')

asyncio.run(benchmark())
"
```

## 🔍 核心技术

### 流式响应设计理念

```python
# ✅ 正确的流式设计
async def ask_stream(self, question: str):
    # 1. 非流式处理阶段
    yield StreamEvent(type="processing", data={"message": "检索文档..."})
    docs = await self.retrieve_documents(question)

    # 2. 流式生成阶段
    yield StreamEvent(type="generation_start")
    if hasattr(self.llm, 'astream'):
        # 真正的LLM流式调用
        async for chunk in self.llm.astream(prompt):
            yield StreamEvent(type="generation_chunk", data={"chunk": chunk.content})
    else:
        # 优雅降级到模拟流式
        response = await self.llm.ainvoke(prompt)
        for char in response.content:
            yield StreamEvent(type="generation_chunk", data={"chunk": char})

    yield StreamEvent(type="generation_end")
```

### 提示词解耦架构

```python
# 提示词管理器设计
class PromptManager:
    def __init__(self):
        self.prompts_dir = Path(__file__).parent / "prompts"
        self._prompt_cache = {}  # 缓存机制
        self._template_cache = {}

    def get_template(self, prompt_name: str) -> PromptTemplate:
        # 缓存检查 -> 文件加载 -> 模板创建 -> 缓存存储
        if prompt_name in self._template_cache:
            return self._template_cache[prompt_name]

        content = self.load_prompt(prompt_name)
        template = PromptTemplate.from_template(content)
        self._template_cache[prompt_name] = template
        return template
```

### 智能检索流程

```python
# 混合检索 + 重排序
def _build_hybrid_retriever(self):
    # 1. 向量检索器
    vector_retriever = self.vector_store.as_retriever(k=5)

    # 2. BM25关键字检索器
    bm25_retriever = BM25Retriever.from_documents(
        self.all_documents,
        preprocess_func=lambda text: list(jieba.cut(text))
    )

    # 3. 混合检索器
    ensemble_retriever = EnsembleRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        weights=[0.7, 0.3]
    )

    # 4. 重排序器
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=self.reranker,
        base_retriever=ensemble_retriever
    )

    return compression_retriever
```

## 📈 性能优化

### 缓存策略

- **提示词缓存**：避免重复文件读取
- **文档缓存**：智能文档变更检测
- **模型缓存**：复用已加载的模型

### 并发优化

- **异步处理**：全面支持异步操作
- **线程池**：CPU 密集型任务使用线程池
- **批量处理**：支持问题批量并发处理

### 内存优化

- **增量更新**：只处理变更的文档
- **分块处理**：大文档自动分块
- **垃圾回收**：及时清理不用的资源

## 🛠️ 扩展开发

### 添加新的提示词

```bash
# 1. 创建提示词文件
echo "新的提示词内容 {variable}" > rag/prompts/new_prompt.txt

# 2. 在 prompt_manager.py 中添加辅助函数
def get_new_prompt_template():
    return prompt_manager.get_template("new_prompt")

# 3. 在业务代码中使用
uv run -c "
from rag.prompt_manager import get_new_prompt_template
template = get_new_prompt_template()
print(template.format(variable='test'))
"
```

### 自定义检索器

```python
class CustomRetriever:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def get_relevant_documents(self, query: str):
        # 自定义检索逻辑
        return self.vector_store.similarity_search(query, k=10)

# 集成到RAG流程
rag.custom_retriever = CustomRetriever(rag.vector_store)
```

### 新增流式事件类型

```python
class StreamEventType(Enum):
    PROCESSING = "processing"
    GENERATION_START = "generation_start"
    GENERATION_CHUNK = "generation_chunk"
    GENERATION_END = "generation_end"
    ERROR = "error"
    COMPLETE = "complete"
    # 新增事件类型
    CUSTOM_EVENT = "custom_event"
```

## 🤝 贡献指南

1. **Fork** 项目
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 **Pull Request**

## 📄 许可证

本项目采用 Apache 2.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - 强大的 LLM 应用框架
- [ChromaDB](https://github.com/chroma-core/chroma) - 高性能向量数据库
- [FastAPI](https://github.com/tiangolo/fastapi) - 现代化的 Web 框架
- [HuggingFace](https://huggingface.co/) - 优秀的模型生态

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 Email: [xiaofeng.0209@gmail.com]
- 🐛 Issues: [GitHub Issues](https://github.com/mr-jay-wei/langchain_rag_demo)
- 💬 Discussions: [GitHub Discussions](https://github.com/mr-jay-wei/langchain_rag_demo)

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！
如果要打赏，请打赏：
![alt text]({054CB209-A3AE-4CA3-90D2-419E20414EA4}.png)
