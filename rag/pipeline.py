# rag/pipeline.py

import os
from typing import List, Dict, Any, Set

# 从 .env 文件加载环境变量，必须在访问 os.getenv 之前调用
from dotenv import load_dotenv
load_dotenv()

# LangChain 核心组件
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

# 文档加载器和分割器
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader

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
    一个封装了完整RAG流程的类 (版本 3.1 - 修正版)。
    特性:
    - 从本地加载嵌入和重排序模型。
    - 使用ChromaDB进行持久化向量存储。
    - 智能同步数据目录，自动加载新文件。
    """
    def __init__(self):
        """初始化RAG流程所需的所有组件。"""
        print("正在初始化 RAG Pipeline...")
        self._setup_models()
        self.vector_store = self._load_vector_store()
        
        # === 【已修正】关键改动：只有在成功加载数据库后才构建问答链 ===
        if self.vector_store:
            print("已成功加载现有数据库，正在构建问答链...")
            self._build_qa_chain()
        else:
            print("未发现现有数据库。问答链将在数据同步后构建。")
            
        print("RAG Pipeline 初始化完成。")

    def _setup_models(self):
        """私有方法，用于设置所有模型和分割器。"""
        print(f"  - 加载嵌入模型: {config.EMBEDDING_MODEL_NAME}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL_NAME,
            model_kwargs=config.EMBEDDING_MODEL_KWARGS
        )
        print(f"  - 加载重排序模型: {config.RERANKER_MODEL_NAME}")
        reranker_model = HuggingFaceCrossEncoder(
            model_name=config.RERANKER_MODEL_NAME,
            model_kwargs=config.RERANKER_MODEL_KWARGS
        )
        self.reranker = CrossEncoderReranker(model=reranker_model, top_n=config.RERANKER_TOP_N)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        self._setup_llm()
        self.qa_chain = None

    def _load_vector_store(self) -> Chroma:
        """加载向量数据库。如果不存在，则返回None。"""
        persist_directory = config.VECTOR_STORE_PATH
        if os.path.exists(persist_directory) and os.listdir(persist_directory):
            print(f"发现已存在的向量数据库，正在从 '{persist_directory}' 加载...")
            return Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings
            )
        return None

    # === 【已修正】补充了 _get_processed_sources 方法的完整实现 ===
    def _get_processed_sources(self) -> Set[str]:
        """
        从向量数据库中获取所有已处理过的文档源路径。

        这是实现增量更新的关键，通过它我们可以知道哪些文件已经是“旧”文件。
        
        Returns:
            一个包含所有唯一源文件路径的集合(Set)。
        """
        if not self.vector_store:
            return set()
        
        try:
            # ChromaDB的 .get() 方法可以获取数据库中的条目。
            # 我们只需要元数据(metadatas)部分。
            all_entries = self.vector_store.get(include=["metadatas"])
            
            # 使用集合推导式高效地提取所有'source'元数据
            # 'source'是在加载文档时由DirectoryLoader自动添加的元数据，值为文件路径。
            sources = {
                metadata['source'] 
                for metadata in all_entries['metadatas'] 
                if metadata and 'source' in metadata
            }
            return sources
        except Exception as e:
            # 增加错误处理，提高代码健壮性
            print(f"从数据库获取源文件列表时出错: {e}")
            return set()

    def sync_data_directory(self):
        """
        智能同步数据目录。自动发现新文件并将其添加到向量数据库中。
        """
        data_path = config.DATA_PATH
        if not os.path.exists(data_path):
            print(f"警告: 数据目录 '{data_path}' 不存在。")
            return

        # 1. 获取已处理的文件列表
        processed_sources = self._get_processed_sources()
        print(f"数据库中已存在 {len(processed_sources)} 个来源的文件。")

        # 2. 扫描数据目录，找出所有 .txt 文件
        all_files_in_dir = []
        for root, _, files in os.walk(data_path):
            for file in files:
                if file.endswith(".txt"):
                    all_files_in_dir.append(os.path.join(root, file))
        
        # 3. 计算出需要新增的文件列表
        new_files_to_process = [f for f in all_files_in_dir if f not in processed_sources]

        if not new_files_to_process:
            print("没有发现需要处理的新文件。")
            return

        print(f"发现 {len(new_files_to_process)} 个新文档，正在处理...")
        
        # 4. 加载新文档
        new_docs = []
        for file_path in new_files_to_process:
            loader = TextLoader(file_path, encoding='utf-8')
            new_docs.extend(loader.load())
            
        chunks = self.text_splitter.split_documents(new_docs)
        print(f"  - 新文档被分割成 {len(chunks)} 个文本块。")

        # 5. 将新文档块添加到数据库
        if self.vector_store is None:
            # 如果数据库是空的，直接基于新文档创建
            print("正在创建新的向量数据库...")
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=config.VECTOR_STORE_PATH
            )
            print(f"  - 新的向量数据库已创建于 '{config.VECTOR_STORE_PATH}'。")
        else:
            # 否则，增量添加
            self.vector_store.add_documents(chunks)
            print("  - 新的文本块已成功添加到现有数据库。")

        # 6. 重新构建问答链以包含新知识
        print("数据同步完成，正在更新问答链...")
        self._build_qa_chain()
        print("问答链已更新，包含最新知识。")

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