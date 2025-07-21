# rag/pipeline.py

import os
from typing import List, Dict, Any

# 从 .env 文件加载环境变量，必须在访问 os.getenv 之前调用
from dotenv import load_dotenv
load_dotenv()

# LangChain 核心组件
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

# 文档加载器和分割器
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 向量存储与嵌入
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
# LLM 与 RAG 链
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

# 重排序相关组件
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder # <-- 导入这个新类

# 导入项目配置
from . import config


class RagPipeline:
    """
    一个封装了完整RAG（检索-增强-生成）流程的类。

    该流程包括：加载文档 -> 分割文本 -> 向量化 -> 存入向量数据库 ->
    用户提问 -> 检索相关文档 -> 重排序文档 -> 调用LLM生成答案。
    """
    def __init__(self):
        """
        初始化RAG流程所需的所有组件。
        此过程会自动下载并加载本地模型（如果缓存中不存在）。
        """
        print("正在初始化 RAG Pipeline...")
        self._setup_components()
        print("RAG Pipeline 初始化完成。")

    def _setup_components(self):
        """
        私有方法，用于设置所有核心组件。
        """
        # 1. 初始化嵌入模型 (Embedding Model)
        # 1. 初始化嵌入模型 (Embedding Model)
        print(f"  - 加载嵌入模型: {config.EMBEDDING_MODEL_NAME} (设备: {config.MODEL_DEVICE})"
        )
        # 使用 HuggingFaceEmbeddings，它原生支持从本地路径加载模型
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL_NAME,
            model_kwargs=config.EMBEDDING_MODEL_KWARGS
            # cache_folder=config.CACHE_DIR 
        # 注意这里参数名是 cache_folder
        )

        # 2. 初始化重排序模型 (Reranker Model)
        print(f"  - 加载重排序模型: {config.RERANKER_MODEL_NAME} (设备: {config.MODEL_DEVICE})")
        # 使用LangChain提供的包装类，它会自动处理模型下载和类型匹配
        reranker_model = HuggingFaceCrossEncoder(
            model_name=config.RERANKER_MODEL_NAME,
            model_kwargs=config.RERANKER_MODEL_KWARGS
        )
        self.reranker = CrossEncoderReranker(model=reranker_model, top_n=config.RERANKER_TOP_N)

        # 3. 初始化文本分割器 (Text Splitter)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )

        # 4. 初始化大语言模型 (LLM)
        self._setup_llm()
        
        # 5. 初始化其他变量
        self.vector_store = None
        self.qa_chain = None

    def _setup_llm(self):
        """加载大语言模型配置。"""
        api_key = os.getenv("DeepSeek_api_key")
        base_url = os.getenv("DeepSeek_base_url")
        model_name = os.getenv("DeepSeek_model_name")

        if not all([api_key, base_url, model_name]):
            raise ValueError(
                "API密钥或模型配置未找到。请检查您的 .env 文件是否包含 "
                "LLM_API_KEY, LLM_BASE_URL, 和 LLM_MODEL_NAME。"
            )
        
        print(f"  - 配置大语言模型: {model_name}")
        self.llm = ChatOpenAI(
        model=model_name,  # 模型名称
        openai_api_key=api_key,  # 在平台注册账号后获取
        openai_api_base=base_url,  # 平台 API 地址
        temperature=0,
        seed=42
        )

    def load_and_process_documents(self, documents: List[Document]):
        """
        加载文档、分割、嵌入并构建完整的问答链。

        Args:
            documents: LangChain Document对象的列表。
        """
        if not documents:
            print("警告: 传入的文档列表为空。")
            return

        # 1. 分割文档
        print("步骤 1/3: 正在分割文档...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"  - 文档被成功分割成 {len(chunks)} 个文本块。")

        # 2. 构建向量数据库
        print("步骤 2/3: 正在构建向量数据库...")
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection_name="rag_documents",
            # db_file=":memory:"  # ":memory:" 表示这是一个纯内存数据库
            persist_directory="./my_chromadb_vector_store"
        )
        print("  - 向量数据库构建完成。")

        # 3. 构建问答链 (QA Chain)
        print("步骤 3/3: 正在构建问答链...")
        self._build_qa_chain()
        print("  - 问答链构建完成。现在可以开始提问了。")

    def _build_qa_chain(self):
        """
        构建包含检索器、重排序器和LLM的问答链。
        """
        # 基础检索器，从向量数据库中获取文档
        base_retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": config.RETRIEVER_TOP_K}
        )
        
        # 压缩检索器，集成了重排序逻辑
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=self.reranker,
            base_retriever=base_retriever
        )
        
        # 定义一个提示模板，指导LLM如何利用上下文回答问题
        prompt_template = """
        请你扮演一个严谨的文档问答机器人。
        请严格根据下面提供的“上下文信息”来回答“问题”。
        如果上下文中没有足够的信息来回答问题，请直接说：“根据提供的资料，我无法回答该问题。”
        不允许编造或添加上下文之外的任何信息。

        ---
        上下文信息:
        {context}
        ---

        问题: {question}

        回答:
        """
        QA_CHAIN_PROMPT = PromptTemplate.from_template(prompt_template)

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff", # "stuff"模式会将所有检索到的文档内容“塞”进一个Prompt中
            retriever=compression_retriever,
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
            return_source_documents=True # 返回引用的源文档，便于溯源
        )

    def ask(self, question: str) -> Dict[str, Any]:
        """
        对已加载的文档提出问题，并获取答案。

        Args:
            question: 用户提出的问题字符串。

        Returns:
            一个字典，包含'result' (答案) 和 'source_documents' (参考的文档片段)。
        """
        if not self.qa_chain:
            return {
                "result": "错误: 问答链尚未初始化。请先调用 `load_and_process_documents` 方法加载文档。",
                "source_documents": []
            }
        
        print(f"\n正在处理问题: '{question}'...")
        result = self.qa_chain.invoke({"query": question})
        return result