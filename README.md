# Python RAG (Retrieval-Augmented Generation) 项目

**版本: 3.2 (稳定版)**

本项目从零开始，成功构建了一个功能完整、高度模块化且可用于实际生产的检索增强生成（RAG）系统。该系统实现了核心模型的本地化部署、知识库的持久化存储和智能化的增量更新，为处理本地知识文档提供了高效、安全的解决方案。

## 项目亮点

-   [x] **全流程本地化**: 关键的嵌入（Embedding）和重排序（Reranking）模型完全从本地文件加载，确保数据处理过程的隐私与安全，并支持离线运行。
-   [x] **持久化向量知识库**: 利用 `ChromaDB` 将文档向量持久化存储在本地磁盘，实现了知识的长期积累。程序重启后可直接加载现有知识，无需重复处理。
-   [x] **智能化增量同步**: 系统能够自动扫描指定的数据目录 (`data`)，智能识别并处理新增的文档，实现知识库的轻松、高效维护。
-   [x] **混合检索技术**: 创新性地结合向量检索和关键字检索（BM25），通过 `EnsembleRetriever` 实现混合检索，显著提升召回率和检索准确性。
-   [x] **高度模块化与可扩展**: 项目遵循高内聚、低耦合的设计原则。更换LLM（如从Kimi切换到DeepSeek）、向量数据库或模型都无需改动核心逻辑。
-   [x] **健壮的工程实践**: 代码结构清晰，配置、核心逻辑、执行入口分离。包含了完善的错误处理和时序安全逻辑，确保在各种场景下都能稳定运行。
-   [x] **现代化的工具链**: 全程使用 `uv` 进行包和虚拟环境管理，体验极致的开发效率。

## 技术栈

| 组件 | 技术/库 | 说明 |
| :--- | :--- | :--- |
| **包管理** | `uv` | 极速的Python包安装器与虚拟环境管理器。 |
| **核心框架** | `LangChain` | 简化RAG流程编排的强大LLM应用开发框架。 |
| **向量嵌入模型**| 本地 `bge-small-zh-v1.5` | 从本地路径加载的高效中英双语嵌入模型。 |
| **重排序模型** | 本地 `bge-reranker-base` | 从本地路径加载，用于优化检索结果排序。 |
| **向量数据库** | `ChromaDB` | 跨平台、持久化的开源向量数据库。 |
| **大语言模型(LLM)** | `ChatOpenAI` 兼容的API | 可轻松对接DeepSeek, Kimi, 智谱AI等多种LLM服务。 |
| **混合检索** | `EnsembleRetriever` + `BM25Retriever` | 结合向量检索和关键字检索，提升召回率。 |
| **中文分词** | `jieba` | 为关键字检索提供高质量的中文分词支持。 |
| **文件加载** | `TextLoader` | 用于加载和处理`.txt`格式的文档。 |
| **环境变量** | `python-dotenv` | 安全、便捷地管理API密钥等敏感信息。 |

## 项目结构

```
/rag_example
|-- .venv/                      # 虚拟环境目录
|-- data/                       # 存放知识文档 (txt文件)
|-- my_chromadb_vector_store/   # 持久化的向量数据库目录
|-- rag/
|   |-- __init__.py
|   |-- config.py               # 全局配置文件
|   |-- pipeline.py             # RAG核心逻辑实现
|-- .env                        # 环境变量文件 (存储API密钥)
|-- main.py                     # 程序主入口和交互界面
|-- requirements.txt            # Python依赖包列表
`-- README.md                   # 本文档
```

## 如何使用

### 1. 环境设置

```bash
# 在您的开发环境中安装uv (如果尚未安装)
pip install uv

# 进入项目根目录 (rag_example)
cd path/to/rag_example

# 使用uv同步环境和依赖
uv sync
```

### 2. 模型与配置

-   **下载模型**: 请预先将`bge-small-zh-v1.5`和`bge-reranker-base`等模型下载到您的本地机器。
-   **修改配置**: 打开`rag/config.py`，确保`EMBEDDING_MODEL_NAME`和`RERANKER_MODEL_NAME`变量指向您本地模型的正确路径。
-   **混合检索配置**: 在`rag/config.py`中可以调整以下混合检索参数：
    ```python
    # 启用/禁用混合检索
    ENABLE_HYBRID_SEARCH = True  # True: 混合检索, False: 纯向量检索
    
    # 检索权重配置 (两个权重之和应为1.0)
    VECTOR_SEARCH_WEIGHT = 0.7   # 向量检索权重
    KEYWORD_SEARCH_WEIGHT = 0.3  # 关键字检索权重
    
    # 检索数量配置
    RETRIEVER_TOP_K = 10         # 向量检索返回的文档数
    KEYWORD_RETRIEVER_TOP_K = 5  # 关键字检索返回的文档数
    ```
-   **API密钥**: 在项目根目录 (`rag_example`) 创建一个名为`.env`的文件，并按以下格式填入您的LLM API密钥信息：

    ```env
    # .env file
    DeepSeek_api_key="sk-xxxxxxxxxxxxxxxxxxxx"
    DeepSeek_base_url="https://api.deepseek.com"
    DeepSeek_model_name="deepseek-chat"
    ```

### 3. 添加知识文档

-   将您的`.txt`格式的知识文档放入项目根目录下的`data`文件夹中。程序启动时会自动同步该目录下的新文件。

### 4. 运行程序

在项目根目录下，确保虚拟环境已激活，然后运行：
```bash
python main.py
```
-   **首次运行**: 程序会自动处理`data`文件夹下的所有文档，并创建持久化的向量数据库 `my_chromadb_vector_store`。
-   **后续运行**: 程序会直接加载现有数据库，并**自动同步**`data`文件夹中新增的文档，然后进入问答环节。

### 5. 测试混合检索功能

我们提供了一个专门的测试脚本来验证混合检索功能：
```bash
python test_hybrid_search.py
```
该脚本会：
- 自动创建测试文档
- 测试不同类型的查询（语义查询、关键字查询、混合查询）
- 展示混合检索相比纯向量检索的优势

---

## 未来发展方向 (Next Steps)

我们的基础已经非常坚实，未来可以在此之上构建更强大的功能：

1.  **支持更多文件类型**:
    *   **挑战**: 当前只支持`.txt`。如何让系统能处理`.pdf`, `.docx`, `.md`等常见文档？
    *   **方案**: 在`sync_data_directory`方法中扩展逻辑，根据文件后缀名选择不同的LangChain文档加载器（如`PyPDFLoader`, `UnstructuredMarkdownLoader`）。

2.  **知识库管理功能**:
    *   **挑战**: 如何删除或更新知识库中某个文件的内容？
    *   **方案**: 为ChromaDB中的文档块添加唯一的ID。实现一个`delete_documents_by_source`方法，在检测到文件被删除或修改时，先删除旧的文档块，再添加新的。

3.  **封装为Web API**:
    *   **挑战**: 如何让其他程序或前端界面调用我们的RAG能力？
    *   **方案**: 使用`FastAPI`或`Flask`框架，将`RagPipeline`封装成一个Web服务。提供一个`/ask`的API端点，接收问题并返回JSON格式的答案。

4.  **提升交互体验**:
    *   **挑战**: 命令行交互不够直观。
    *   **方案**: 使用`Streamlit`或`Gradio`库，在几十分钟内为我们的项目创建一个漂亮的Web UI界面，提供对话式的问答体验。