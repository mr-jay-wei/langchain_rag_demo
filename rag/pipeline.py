# rag/pipeline.py

import os
import hashlib
import time
import glob
from pathlib import Path
from typing import List, Dict, Any, Set, Optional

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
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
# LLM 与 RAG 链
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

# 重排序相关组件
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder # <-- 导入这个新类

# 混合检索相关组件
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

# 抑制 jieba 的 pkg_resources 弃用警告
import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated", category=UserWarning)
import jieba  # 中文分词库

# 导入项目配置
from . import config
# 导入提示词管理器
from .prompt_manager import get_qa_prompt_template, get_query_rewrite_prompt_template


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
        self.all_documents = []  # 存储所有文档，用于关键字检索
        self.bm25_retriever = None  # BM25检索器
        
        # === 【已修正】关键改动：只有在成功加载数据库后才构建问答链 ===
        if self.vector_store:
            print("已成功加载现有数据库，正在构建问答链...")
            self._load_all_documents()  # 加载所有文档用于关键字检索
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

    def _setup_llm(self):
        """加载大语言模型配置。"""
        # api_key = os.getenv("CLOUD_INFINI_API_KEY")
        # base_url = os.getenv("CLOUD_BASE_URL")
        # model_name = os.getenv("CLOUD_MODEL_NAME")
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

    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取文件的详细信息，包括修改时间和内容哈希。
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含文件信息的字典
        """
        try:
            stat = os.stat(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'path': file_path,
                'mtime': stat.st_mtime,
                'size': stat.st_size,
                'hash': hashlib.md5(content.encode('utf-8')).hexdigest()
            }
        except Exception as e:
            print(f"获取文件信息失败 {file_path}: {e}")
            return None

    def _get_file_metadata_from_db(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        从数据库中获取文件的元数据信息。
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件的元数据信息，如果不存在则返回None
        """
        if not self.vector_store:
            return None
        
        try:
            # 获取该文件的所有文档块
            all_entries = self.vector_store.get(
                where={"source": file_path},
                include=["metadatas"]
            )
            
            if all_entries['metadatas']:
                # 返回第一个文档块的元数据（所有块的文件信息应该相同）
                return all_entries['metadatas'][0]
            
            return None
        except Exception as e:
            print(f"从数据库获取文件元数据失败 {file_path}: {e}")
            return None

    def _is_file_modified(self, file_path: str) -> bool:
        """
        检查文件是否已被修改。
        
        Args:
            file_path: 文件路径
            
        Returns:
            如果文件已修改返回True，否则返回False
        """
        current_info = self._get_file_info(file_path)
        if not current_info:
            return False
        
        db_metadata = self._get_file_metadata_from_db(file_path)
        if not db_metadata:
            return True  # 数据库中没有该文件，视为新文件
        
        # 比较文件哈希值
        db_hash = db_metadata.get('file_hash')
        return current_info['hash'] != db_hash

    def delete_documents_by_source(self, source_path: str) -> bool:
        """
        根据源文件路径删除向量数据库中的相关文档。
        
        Args:
            source_path: 源文件路径
            
        Returns:
            删除成功返回True，否则返回False
        """
        if not self.vector_store:
            print("向量数据库未初始化，无法删除文档。")
            return False
        
        try:
            # 获取该文件的所有文档ID
            all_entries = self.vector_store.get(
                where={"source": source_path},
                include=["metadatas"]
            )
            
            if not all_entries['ids']:
                print(f"未找到来源为 '{source_path}' 的文档。")
                return False
            
            # 删除所有相关文档
            self.vector_store.delete(ids=all_entries['ids'])
            print(f"已删除 {len(all_entries['ids'])} 个来源为 '{source_path}' 的文档块。")
            return True
            
        except Exception as e:
            print(f"删除文档时出错: {e}")
            return False

    def update_document(self, file_path: str) -> bool:
        """
        更新单个文档：先删除旧版本，再添加新版本。
        
        Args:
            file_path: 文件路径
            
        Returns:
            更新成功返回True，否则返回False
        """
        try:
            print(f"正在更新文档: {file_path}")
            
            # 1. 删除旧版本
            if not self.delete_documents_by_source(file_path):
                print(f"删除旧版本失败: {file_path}")
                return False
            
            # 2. 加载新版本
            loader = TextLoader(file_path, encoding='utf-8')
            new_docs = loader.load()
            
            # 3. 添加文件信息到元数据
            file_info = self._get_file_info(file_path)
            if file_info:
                for doc in new_docs:
                    doc.metadata.update({
                        'file_hash': file_info['hash'],
                        'file_mtime': file_info['mtime'],
                        'file_size': file_info['size']
                    })
            
            # 4. 分割文档
            chunks = self.text_splitter.split_documents(new_docs)
            
            # 5. 生成唯一ID
            for i, chunk in enumerate(chunks):
                chunk_id = f"{config.DOCUMENT_ID_PREFIX}{hashlib.md5(file_path.encode()).hexdigest()}_{i}"
                chunk.metadata['chunk_id'] = chunk_id
            
            # 6. 添加到数据库
            self.vector_store.add_documents(chunks)
            print(f"  - 已更新文档，新增 {len(chunks)} 个文本块。")
            
            return True
            
        except Exception as e:
            print(f"更新文档时出错: {e}")
            return False

    def _get_enterprise_data_sources(self) -> Dict[str, Dict[str, Any]]:
        """
        获取企业级数据源配置。
        
        Returns:
            数据源配置字典
        """
        if config.ENABLE_ENTERPRISE_MODE:
            return {k: v for k, v in config.ENTERPRISE_DATA_SOURCES.items() if v.get('enabled', True)}
        else:
            # 向后兼容模式
            return {
                "legacy": {
                    "path": config.DATA_PATH,
                    "category": "general",
                    "description": "传统数据目录",
                    "enabled": True,
                    "file_patterns": ["*.txt"],
                    "priority": 1
                }
            }

    def _scan_enterprise_files(self) -> Dict[str, List[str]]:
        """
        扫描企业级数据源中的所有文件。
        
        Returns:
            按数据源分组的文件列表
        """
        data_sources = self._get_enterprise_data_sources()
        all_files_by_source = {}
        
        for source_name, source_config in data_sources.items():
            source_path = source_config['path']
            file_patterns = source_config.get('file_patterns', ['*.txt'])
            
            if not os.path.exists(source_path):
                print(f"警告: 数据源 '{source_name}' 的路径 '{source_path}' 不存在。")
                all_files_by_source[source_name] = []
                continue
            
            source_files = []
            for pattern in file_patterns:
                # 使用glob递归搜索文件
                pattern_path = os.path.join(source_path, "**", pattern)
                matched_files = glob.glob(pattern_path, recursive=True)
                source_files.extend(matched_files)
            
            # 去重并规范化路径
            source_files = list(set(os.path.normpath(f) for f in source_files))
            all_files_by_source[source_name] = source_files
            
            print(f"数据源 '{source_name}' ({source_config['description']}): 发现 {len(source_files)} 个文件")
        
        return all_files_by_source

    def _add_category_metadata(self, docs: List[Document], source_name: str, source_config: Dict[str, Any]) -> List[Document]:
        """
        为文档添加分类元数据。
        
        Args:
            docs: 文档列表
            source_name: 数据源名称
            source_config: 数据源配置
            
        Returns:
            添加了分类元数据的文档列表
        """
        for doc in docs:
            doc.metadata.update({
                'data_source': source_name,
                'category': source_config['category'],
                'description': source_config['description'],
                'priority': source_config.get('priority', 999)
            })
        return docs

    def sync_data_directory(self):
        """
        企业级智能同步数据目录。支持多路径、分类管理。
        """
        if config.ENABLE_ENTERPRISE_MODE:
            print("--- 开始企业级智能同步 ---")
            self._sync_enterprise_data_sources()
        else:
            print("--- 开始传统模式同步 ---")
            self._sync_legacy_data_directory()

    def _sync_legacy_data_directory(self):
        """
        传统单一数据目录同步（向后兼容）。
        """
        data_path = config.DATA_PATH
        if not os.path.exists(data_path):
            print(f"警告: 数据目录 '{data_path}' 不存在。")
            return

        print("--- 开始智能同步数据目录 ---")
        
        # 1. 获取已处理的文件列表
        processed_sources = self._get_processed_sources()
        print(f"数据库中已存在 {len(processed_sources)} 个来源的文件。")

        # 2. 扫描数据目录，找出所有 .txt 文件
        current_files = []
        for root, _, files in os.walk(data_path):
            for file in files:
                if file.endswith(".txt"):
                    current_files.append(os.path.join(root, file))
        
        print(f"当前目录中发现 {len(current_files)} 个 .txt 文件。")
        
        # 3. 分类处理文件
        new_files = []
        modified_files = []
        unchanged_files = []
        
        for file_path in current_files:
            if file_path not in processed_sources:
                new_files.append(file_path)
            elif config.ENABLE_FILE_MONITORING and self._is_file_modified(file_path):
                modified_files.append(file_path)
            else:
                unchanged_files.append(file_path)
        
        # 4. 处理已删除的文件
        deleted_files = []
        if config.AUTO_DELETE_MISSING_FILES:
            for processed_file in processed_sources:
                if processed_file not in current_files:
                    deleted_files.append(processed_file)
        
        # 5. 报告分析结果
        print(f"文件分析结果:")
        print(f"  - 新增文件: {len(new_files)} 个")
        print(f"  - 修改文件: {len(modified_files)} 个")
        print(f"  - 删除文件: {len(deleted_files)} 个")
        print(f"  - 未变化文件: {len(unchanged_files)} 个")
        
        # 6. 处理删除的文件
        if deleted_files:
            print("\n--- 处理已删除的文件 ---")
            for file_path in deleted_files:
                if self.delete_documents_by_source(file_path):
                    print(f"  ✓ 已删除: {file_path}")
                else:
                    print(f"  ✗ 删除失败: {file_path}")
        
        # 7. 处理修改的文件
        if modified_files:
            print("\n--- 处理已修改的文件 ---")
            for file_path in modified_files:
                if self.update_document(file_path):
                    print(f"  ✓ 已更新: {file_path}")
                else:
                    print(f"  ✗ 更新失败: {file_path}")
        
        # 8. 处理新增的文件
        if new_files:
            print(f"\n--- 处理新增的文件 ---")
            print(f"发现 {len(new_files)} 个新文档，正在处理...")
            
            # 加载新文档
            new_docs = []
            for file_path in new_files:
                try:
                    loader = TextLoader(file_path, encoding='utf-8')
                    docs = loader.load()
                    
                    # 添加文件信息到元数据
                    file_info = self._get_file_info(file_path)
                    if file_info:
                        for doc in docs:
                            doc.metadata.update({
                                'file_hash': file_info['hash'],
                                'file_mtime': file_info['mtime'],
                                'file_size': file_info['size']
                            })
                    
                    new_docs.extend(docs)
                    print(f"  ✓ 已加载: {file_path}")
                except Exception as e:
                    print(f"  ✗ 加载失败: {file_path} - {e}")
            
            if new_docs:
                chunks = self.text_splitter.split_documents(new_docs)
                '''chunks demo
                chunks = [
                    Document(
                        page_content="机器学习是人工智能的一个分支，它使计算机能够在没有明确编程的情况下学习。",
                        metadata={
                            # 原始文件信息
                            'source': 'data/机器学习介绍.txt',
                            
                            # 文件元数据（由 _get_file_info 添加）
                            'file_hash': 'a1b2c3d4e5f6...',
                            'file_mtime': 1704067200.123,
                            'file_size': 256,
                            
                            # 分块信息（由代码添加）
                            'chunk_id': 'doc_5d41402abc4b2a76b9719d911017c592_0',
                            
                            # 可能的其他元数据
                            'chunk_index': 0,
                            'total_chunks': 3
                        }
                    ),
                    
                    Document(
                        page_content="机器学习算法通过训练数据来构建数学模型，以便对新数据进行预测或决策。",
                        metadata={
                            'source': 'data/机器学习介绍.txt',
                            'file_hash': 'a1b2c3d4e5f6...',
                            'file_mtime': 1704067200.123,
                            'file_size': 256,
                            'chunk_id': 'doc_5d41402abc4b2a76b9719d911017c592_1',
                            'chunk_index': 1,
                            'total_chunks': 3
                        }
                    ),
                    
                    Document(
                        page_content="常见的机器学习类型包括监督学习、无监督学习和强化学习。",
                        metadata={
                            'source': 'data/机器学习介绍.txt',
                            'file_hash': 'a1b2c3d4e5f6...',
                            'file_mtime': 1704067200.123,
                            'file_size': 256,
                            'chunk_id': 'doc_5d41402abc4b2a76b9719d911017c592_2',
                            'chunk_index': 2,
                            'total_chunks': 3
                        }
                    )
                ]
                '''
                print(f"  - 新文档被分割成 {len(chunks)} 个文本块。")

                # 生成唯一ID
                for chunk in chunks:
                    source_path = chunk.metadata.get('source', '')
                    chunk_hash = hashlib.md5(f"{source_path}_{chunk.page_content}".encode()).hexdigest()
                    chunk.metadata['chunk_id'] = f"{config.DOCUMENT_ID_PREFIX}{chunk_hash}"

                # 添加到数据库
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

        # 9. 重新构建问答链（如果有任何变化）
        if new_files or modified_files or deleted_files:
            print("\n--- 更新问答链 ---")
            self._load_all_documents()  # 重新加载所有文档用于关键字检索
            self._build_qa_chain()
            print("问答链已更新，包含最新知识。")
        else:
            print("\n--- 无需更新 ---")
            print("所有文件都是最新的，无需更新问答链。")
        
        print("--- 智能同步完成 ---")

    def _sync_enterprise_data_sources(self):
        """
        企业级多数据源同步。
        """
        # 1. 扫描所有企业级数据源
        all_files_by_source = self._scan_enterprise_files()
        
        # 2. 获取已处理的文件列表
        processed_sources = self._get_processed_sources()
        print(f"数据库中已存在 {len(processed_sources)} 个来源的文件。")
        
        # 3. 合并所有数据源的文件
        all_current_files = []
        for source_name, files in all_files_by_source.items():
            all_current_files.extend(files)
        
        print(f"所有数据源共发现 {len(all_current_files)} 个文件。")
        
        # 4. 分类处理文件
        new_files = []
        modified_files = []
        unchanged_files = []
        
        for file_path in all_current_files:
            if file_path not in processed_sources:
                new_files.append(file_path)
            elif config.ENABLE_FILE_MONITORING and self._is_file_modified(file_path):
                modified_files.append(file_path)
            else:
                unchanged_files.append(file_path)
        
        # 5. 处理已删除的文件
        deleted_files = []
        if config.AUTO_DELETE_MISSING_FILES:
            for processed_file in processed_sources:
                if processed_file not in all_current_files:
                    deleted_files.append(processed_file)
        
        # 6. 报告分析结果
        print(f"企业级文件分析结果:")
        print(f"  - 新增文件: {len(new_files)} 个")
        print(f"  - 修改文件: {len(modified_files)} 个")
        print(f"  - 删除文件: {len(deleted_files)} 个")
        print(f"  - 未变化文件: {len(unchanged_files)} 个")
        
        # 7. 处理删除的文件
        if deleted_files:
            print("\n--- 处理已删除的文件 ---")
            for file_path in deleted_files:
                if self.delete_documents_by_source(file_path):
                    print(f"  ✓ 已删除: {file_path}")
                else:
                    print(f"  ✗ 删除失败: {file_path}")
        
        # 8. 处理修改的文件
        if modified_files:
            print("\n--- 处理已修改的文件 ---")
            for file_path in modified_files:
                if self._update_enterprise_document(file_path):
                    print(f"  ✓ 已更新: {file_path}")
                else:
                    print(f"  ✗ 更新失败: {file_path}")
        
        # 9. 处理新增的文件
        if new_files:
            print(f"\n--- 处理新增的文件 ---")
            self._process_new_enterprise_files(new_files, all_files_by_source)
        
        # 10. 重新构建问答链（如果有任何变化）
        if new_files or modified_files or deleted_files:
            print("\n--- 更新问答链 ---")
            self._load_all_documents()
            self._build_qa_chain()
            print("问答链已更新，包含最新知识。")
        else:
            print("\n--- 无需更新 ---")
            print("所有文件都是最新的，无需更新问答链。")
        
        print("--- 企业级智能同步完成 ---")

    def _get_source_config_for_file(self, file_path: str, all_files_by_source: Dict[str, List[str]]) -> Optional[Dict[str, Any]]:
        """
        根据文件路径获取对应的数据源配置。
        
        Args:
            file_path: 文件路径
            all_files_by_source: 按数据源分组的文件列表
            
        Returns:
            数据源配置，如果未找到则返回None
        """
        data_sources = self._get_enterprise_data_sources()
        
        for source_name, files in all_files_by_source.items():
            if file_path in files:
                return data_sources.get(source_name)
        
        return None

    def _update_enterprise_document(self, file_path: str) -> bool:
        """
        更新企业级文档，包含分类信息。
        
        Args:
            file_path: 文件路径
            
        Returns:
            更新成功返回True，否则返回False
        """
        try:
            print(f"正在更新企业级文档: {file_path}")
            
            # 1. 删除旧版本
            if not self.delete_documents_by_source(file_path):
                print(f"删除旧版本失败: {file_path}")
                return False
            
            # 2. 获取文件对应的数据源配置
            all_files_by_source = self._scan_enterprise_files()
            source_config = self._get_source_config_for_file(file_path, all_files_by_source)
            
            if not source_config:
                print(f"未找到文件 {file_path} 对应的数据源配置")
                return False
            
            # 3. 加载新版本
            loader = TextLoader(file_path, encoding='utf-8')
            new_docs = loader.load()
            
            # 4. 添加文件信息和分类信息到元数据
            file_info = self._get_file_info(file_path)
            if file_info:
                for doc in new_docs:
                    doc.metadata.update({
                        'file_hash': file_info['hash'],
                        'file_mtime': file_info['mtime'],
                        'file_size': file_info['size'],
                        'category': source_config['category'],
                        'data_source': source_config.get('description', ''),
                        'priority': source_config.get('priority', 999)
                    })
            
            # 5. 分割文档
            chunks = self.text_splitter.split_documents(new_docs)
            
            # 6. 生成唯一ID
            for i, chunk in enumerate(chunks):
                chunk_id = f"{config.DOCUMENT_ID_PREFIX}{hashlib.md5(file_path.encode()).hexdigest()}_{i}"
                chunk.metadata['chunk_id'] = chunk_id
            
            # 7. 添加到数据库
            self.vector_store.add_documents(chunks)
            print(f"  - 已更新文档，新增 {len(chunks)} 个文本块，类别: {source_config['category']}")
            
            return True
            
        except Exception as e:
            print(f"更新企业级文档时出错: {e}")
            return False

    def _process_new_enterprise_files(self, new_files: List[str], all_files_by_source: Dict[str, List[str]]):
        """
        处理新增的企业级文件。
        
        Args:
            new_files: 新增文件列表
            all_files_by_source: 按数据源分组的文件列表
        """
        print(f"发现 {len(new_files)} 个新文档，正在处理...")
        
        # 按数据源分组处理新文件
        data_sources = self._get_enterprise_data_sources()
        files_by_category = {}
        
        for file_path in new_files:
            source_config = self._get_source_config_for_file(file_path, all_files_by_source)
            if source_config:
                category = source_config['category']
                if category not in files_by_category:
                    files_by_category[category] = []
                files_by_category[category].append((file_path, source_config))
        
        # 按类别处理文件
        all_new_docs = []
        for category, file_configs in files_by_category.items():
            print(f"\n处理类别 '{category}' 的文件:")
            
            for file_path, source_config in file_configs:
                try:
                    loader = TextLoader(file_path, encoding='utf-8')
                    docs = loader.load()
                    
                    # 添加文件信息和分类信息到元数据
                    file_info = self._get_file_info(file_path)
                    if file_info:
                        for doc in docs:
                            doc.metadata.update({
                                'file_hash': file_info['hash'],
                                'file_mtime': file_info['mtime'],
                                'file_size': file_info['size'],
                                'category': source_config['category'],
                                'data_source': source_config.get('description', ''),
                                'priority': source_config.get('priority', 999)
                            })
                    
                    all_new_docs.extend(docs)
                    print(f"  ✓ 已加载: {file_path} (类别: {category})")
                except Exception as e:
                    print(f"  ✗ 加载失败: {file_path} - {e}")
        
        if all_new_docs:
            chunks = self.text_splitter.split_documents(all_new_docs)
            print(f"\n新文档被分割成 {len(chunks)} 个文本块。")

            # 生成唯一ID并添加分类信息
            for chunk in chunks:
                source_path = chunk.metadata.get('source', '')
                chunk_hash = hashlib.md5(f"{source_path}_{chunk.page_content}".encode()).hexdigest()
                chunk.metadata['chunk_id'] = f"{config.DOCUMENT_ID_PREFIX}{chunk_hash}"

            # 添加到数据库
            if self.vector_store is None:
                print("正在创建新的向量数据库...")
                self.vector_store = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    persist_directory=config.VECTOR_STORE_PATH
                )
                print(f"  - 新的向量数据库已创建于 '{config.VECTOR_STORE_PATH}'。")
            else:
                self.vector_store.add_documents(chunks)
                print("  - 新的文本块已成功添加到现有数据库。")
            
            # 按类别统计
            category_stats = {}
            for chunk in chunks:
                category = chunk.metadata.get('category', 'unknown')
                category_stats[category] = category_stats.get(category, 0) + 1
            
            print("按类别统计:")
            for category, count in category_stats.items():
                print(f"  - {category}: {count} 个文本块")

    def _load_all_documents(self):
        """
        从向量数据库中加载所有文档，用于构建关键字检索器。
        """
        if not self.vector_store:
            print("警告: 向量数据库未初始化，无法加载文档用于关键字检索。")
            return
        
        try:
            # 从ChromaDB获取所有文档内容和元数据
            all_entries = self.vector_store.get(include=["documents", "metadatas"])
            
            # 重构Document对象
            self.all_documents = []
            for i, (doc_content, metadata) in enumerate(zip(all_entries['documents'], all_entries['metadatas'])):
                doc = Document(
                    page_content=doc_content,
                    metadata=metadata or {}
                )
                self.all_documents.append(doc)
            
            print(f"  - 已加载 {len(self.all_documents)} 个文档块用于关键字检索")
            
            # 构建BM25检索器
            self._build_bm25_retriever()
            
        except Exception as e:
            print(f"加载文档用于关键字检索时出错: {e}")
            self.all_documents = []

    def _build_bm25_retriever(self):
        """
        构建BM25关键字检索器。
        """
        if not self.all_documents:
            print("警告: 没有文档可用于构建BM25检索器。")
            return
        
        try:
            # 使用jieba进行中文分词的预处理函数
            def preprocess_func(text: str) -> List[str]:
                # 对中文文本进行分词
                return list(jieba.cut(text))
            
            # 构建BM25检索器
            self.bm25_retriever = BM25Retriever.from_documents(
                self.all_documents,
                preprocess_func=preprocess_func
            )
            self.bm25_retriever.k = config.KEYWORD_RETRIEVER_TOP_K
            
            print(f"  - BM25关键字检索器构建完成，Top-K: {config.KEYWORD_RETRIEVER_TOP_K}")
            
        except Exception as e:
            print(f"构建BM25检索器时出错: {e}")
            self.bm25_retriever = None

    def _build_qa_chain(self):
        """
        构建包含检索器、重排序器和LLM的问答链。
        """
        # 构建混合检索器
        hybrid_retriever = self._build_hybrid_retriever()
        
        # 压缩检索器，集成了重排序逻辑
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=self.reranker,
            base_retriever=hybrid_retriever
        )
        
        # 使用提示词管理器获取问答提示模板
        QA_CHAIN_PROMPT = get_qa_prompt_template()

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff", # "stuff"模式会将所有检索到的文档内容“塞”进一个Prompt中
            retriever=compression_retriever,
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
            return_source_documents=True # 返回引用的源文档，便于溯源
        )

    def _build_hybrid_retriever(self):
        """
        构建混合检索器，结合向量检索和关键字检索。
        """
        # 向量检索器
        vector_retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": config.RETRIEVER_TOP_K}
        )
        
        # 根据配置决定是否启用混合检索
        if config.ENABLE_HYBRID_SEARCH and self.bm25_retriever is not None:
            print(f"  - 启用混合检索模式 (向量权重: {config.VECTOR_SEARCH_WEIGHT}, 关键字权重: {config.KEYWORD_SEARCH_WEIGHT})")
            
            # 创建混合检索器
            ensemble_retriever = EnsembleRetriever(
                retrievers=[vector_retriever, self.bm25_retriever],
                weights=[config.VECTOR_SEARCH_WEIGHT, config.KEYWORD_SEARCH_WEIGHT]
            )
            return ensemble_retriever
        else:
            print("  - 使用纯向量检索模式")
            return vector_retriever

    def ask_with_categories(self, question: str, categories: List[str] = None) -> Dict[str, Any]:
        """
        支持分类检索的问答功能。
        
        Args:
            question: 用户提出的问题字符串
            categories: 指定检索的类别列表，None表示检索所有类别
            
        Returns:
            一个字典，包含'result' (答案) 和 'source_documents' (参考的文档片段)
        """
        if not self.qa_chain:
            return {
                "result": "错误: 问答链尚未初始化。请先调用 `sync_data_directory` 方法加载文档。",
                "source_documents": []
            }
        
        # 如果没有指定类别，使用默认类别或所有类别
        if categories is None:
            categories = config.DEFAULT_SEARCH_CATEGORIES
        
        print(f"\n正在处理问题: '{question}'...")
        if categories:
            print(f"限定检索类别: {categories}")
        
        # 如果启用了问题改写功能
        if config.ENABLE_QUERY_REWRITING:
            print("--- 问题改写阶段 ---")
            
            # 1. 改写问题
            rewritten_queries = self._rewrite_query(question)
            
            # 2. 使用多个问题进行分类检索
            print("--- 多查询分类检索阶段 ---")
            retrieved_docs = self._retrieve_with_multiple_queries_and_categories(rewritten_queries, categories)
            
            # 3. 重排序
            print("--- 重排序阶段 ---")
            if retrieved_docs and self.reranker:
                try:
                    reranked_docs = self.reranker.compress_documents(retrieved_docs, question)
                    final_docs = reranked_docs[:config.RERANKER_TOP_N]
                    print(f"  - 重排序完成，最终选择 {len(final_docs)} 个最相关文档")
                except Exception as e:
                    print(f"  - 重排序失败: {e}，使用原始检索结果")
                    final_docs = retrieved_docs[:config.RERANKER_TOP_N]
            else:
                final_docs = retrieved_docs[:config.RERANKER_TOP_N]
            
            # 4. 生成答案
            print("--- 答案生成阶段 ---")
            if final_docs:
                # 构建上下文
                context = "\n\n".join([doc.page_content for doc in final_docs])
                
                # 使用提示词管理器获取问答提示模板
                qa_template = get_qa_prompt_template()
                prompt = qa_template.format(context=context, question=question)
                response = self.llm.invoke(prompt)
                
                if hasattr(response, 'content'):
                    answer = response.content.strip()
                else:
                    answer = str(response).strip()
                
                return {
                    "result": answer,
                    "source_documents": final_docs
                }
            else:
                return {
                    "result": "根据提供的资料，我无法找到相关信息来回答该问题。",
                    "source_documents": []
                }
        else:
            # 使用分类检索的问答链
            if categories:
                # 创建临时的分类检索器
                category_retriever = self._build_category_retriever(categories)
                compression_retriever = ContextualCompressionRetriever(
                    base_compressor=self.reranker,
                    base_retriever=category_retriever
                )
                
                # 临时创建问答链
                from langchain.chains import RetrievalQA
                from langchain_core.prompts import PromptTemplate
                
                QA_CHAIN_PROMPT = get_qa_prompt_template()
                
                temp_qa_chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=compression_retriever,
                    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
                    return_source_documents=True
                )
                
                result = temp_qa_chain.invoke({"query": question})
                return result
            else:
                # 使用原始的问答链
                result = self.qa_chain.invoke({"query": question})
                return result

    def _retrieve_with_multiple_queries_and_categories(self, queries: List[str], categories: List[str] = None) -> List[Document]:
        """
        使用多个查询问题进行分类检索，并合并结果。
        
        Args:
            queries: 查询问题列表
            categories: 指定检索的类别列表
            
        Returns:
            合并后的文档列表
        """
        all_documents = []
        seen_contents = set()
        
        for i, query in enumerate(queries):
            print(f"  - 执行查询 {i+1}: {query}")
            
            try:
                # 使用分类检索器进行检索
                if categories:
                    category_retriever = self._build_category_retriever(categories)
                else:
                    category_retriever = self._build_hybrid_retriever()
                
                # 为改写的查询使用较少的检索数量
                if i == 0:
                    k = config.RETRIEVER_TOP_K
                else:
                    k = config.REWRITE_QUERY_TOP_K
                
                # 临时调整检索器的k值
                if hasattr(category_retriever, 'retrievers'):
                    for retriever in category_retriever.retrievers:
                        if hasattr(retriever, 'search_kwargs'):
                            retriever.search_kwargs['k'] = k
                        elif hasattr(retriever, 'k'):
                            retriever.k = k
                
                docs = category_retriever.invoke(query)
                
                # 去重处理
                for doc in docs:
                    content_hash = hash(doc.page_content)
                    if config.ENABLE_DOCUMENT_DEDUPLICATION:
                        if content_hash not in seen_contents:
                            all_documents.append(doc)
                            seen_contents.add(content_hash)
                    else:
                        all_documents.append(doc)
                        
                print(f"    检索到 {len(docs)} 个文档")
                
            except Exception as e:
                print(f"    查询执行失败: {e}")
                continue
        
        print(f"  - 多查询分类检索完成，共获得 {len(all_documents)} 个文档")
        return all_documents

    def _build_category_retriever(self, categories: List[str]):
        """
        构建分类检索器，只检索指定类别的文档。
        
        Args:
            categories: 类别列表
            
        Returns:
            分类检索器
        """
        if not categories:
            return self._build_hybrid_retriever()
        
        # 过滤指定类别的文档
        category_documents = []
        for doc in self.all_documents:
            doc_category = doc.metadata.get('category', 'general')
            if doc_category in categories:
                category_documents.append(doc)
        
        print(f"  - 分类过滤: 从 {len(self.all_documents)} 个文档中筛选出 {len(category_documents)} 个指定类别的文档")
        
        if not category_documents:
            print("  - 警告: 指定类别中没有找到文档")
            return self._build_hybrid_retriever()
        
        # 创建临时向量存储（仅包含指定类别的文档）
        try:
            temp_vector_store = Chroma.from_documents(
                documents=category_documents,
                embedding=self.embeddings
            )
            
            vector_retriever = temp_vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": config.RETRIEVER_TOP_K}
            )
            
            # 如果启用混合检索，还需要创建分类BM25检索器
            if config.ENABLE_HYBRID_SEARCH:
                try:
                    def preprocess_func(text: str) -> List[str]:
                        return list(jieba.cut(text))
                    
                    category_bm25_retriever = BM25Retriever.from_documents(
                        category_documents,
                        preprocess_func=preprocess_func
                    )
                    category_bm25_retriever.k = config.KEYWORD_RETRIEVER_TOP_K
                    
                    # 创建混合检索器
                    ensemble_retriever = EnsembleRetriever(
                        retrievers=[vector_retriever, category_bm25_retriever],
                        weights=[config.VECTOR_SEARCH_WEIGHT, config.KEYWORD_SEARCH_WEIGHT]
                    )
                    
                    print(f"  - 分类混合检索器构建完成")
                    return ensemble_retriever
                    
                except Exception as e:
                    print(f"  - 分类BM25检索器构建失败: {e}，使用纯向量检索")
                    return vector_retriever
            else:
                return vector_retriever
                
        except Exception as e:
            print(f"  - 分类检索器构建失败: {e}，使用全局检索器")
            return self._build_hybrid_retriever()

    def get_available_categories(self) -> Dict[str, int]:
        """
        获取知识库中可用的类别及其文档数量。
        
        Returns:
            类别名称到文档数量的映射
        """
        if not self.all_documents:
            return {}
        
        category_counts = {}
        for doc in self.all_documents:
            category = doc.metadata.get('category', 'general')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return category_counts

    def get_data_source_info(self) -> Dict[str, Dict[str, Any]]:
        """
        获取数据源信息统计。
        
        Returns:
            数据源信息字典
        """
        if not self.all_documents:
            return {}
        
        source_info = {}
        for doc in self.all_documents:
            category = doc.metadata.get('category', 'general')
            data_source = doc.metadata.get('data_source', 'unknown')
            
            if category not in source_info:
                source_info[category] = {
                    'count': 0,
                    'sources': set(),
                    'description': doc.metadata.get('description', ''),
                    'priority': doc.metadata.get('priority', 999)
                }
            
            source_info[category]['count'] += 1
            if data_source != 'unknown':
                source_info[category]['sources'].add(data_source)
        
        # 转换set为list以便JSON序列化
        for category in source_info:
            source_info[category]['sources'] = list(source_info[category]['sources'])
        
        return source_info

    def _rewrite_query(self, original_query: str) -> List[str]:
        """
        将原始问题改写成多个相关问题，提高搜索覆盖面。
        
        Args:
            original_query: 用户的原始问题
            
        Returns:
            包含原始问题和改写问题的列表
        """
        if not config.ENABLE_QUERY_REWRITING:
            return [original_query]
        
        try:
            # 使用提示词管理器获取问题改写提示模板
            rewrite_prompt = get_query_rewrite_prompt_template()
            
            # 调用LLM进行问题改写
            prompt = rewrite_prompt.format(
                original_query=original_query,
                count=config.QUERY_REWRITE_COUNT
            )
            
            response = self.llm.invoke(prompt)
            
            # 解析改写结果
            rewritten_queries = []
            if hasattr(response, 'content'):
                content = response.content.strip()
            else:
                content = str(response).strip()
            
            # 分割并清理改写的问题
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            for line in lines:
                # 移除可能的编号格式
                cleaned_line = line
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # 移除编号和标点
                    cleaned_line = line.split('.', 1)[-1].strip()
                    cleaned_line = cleaned_line.lstrip('- •').strip()
                
                if cleaned_line and cleaned_line not in rewritten_queries:
                    rewritten_queries.append(cleaned_line)
            
            # 确保包含原始问题
            all_queries = [original_query]
            all_queries.extend(rewritten_queries[:config.QUERY_REWRITE_COUNT])
            
            print(f"  - 问题改写完成，生成了 {len(all_queries)} 个查询问题")
            for i, query in enumerate(all_queries):
                print(f"    [{i+1}] {query}")
            
            return all_queries
            
        except Exception as e:
            print(f"问题改写失败: {e}")
            return [original_query]

    def _retrieve_with_multiple_queries(self, queries: List[str]) -> List[Document]:
        """
        使用多个查询问题进行检索，并合并结果。
        
        Args:
            queries: 查询问题列表
            
        Returns:
            合并后的文档列表
        """
        all_documents = []
        seen_contents = set()  # 用于去重
        
        for i, query in enumerate(queries):
            print(f"  - 执行查询 {i+1}: {query}")
            
            try:
                # 使用混合检索器进行检索
                hybrid_retriever = self._build_hybrid_retriever()
                
                # 为改写的查询使用较少的检索数量
                if i == 0:  # 原始查询使用正常数量
                    k = config.RETRIEVER_TOP_K
                else:  # 改写查询使用较少数量
                    k = config.REWRITE_QUERY_TOP_K
                
                # 临时调整检索器的k值
                if hasattr(hybrid_retriever, 'retrievers'):
                    # EnsembleRetriever
                    for retriever in hybrid_retriever.retrievers:
                        if hasattr(retriever, 'search_kwargs'):
                            retriever.search_kwargs['k'] = k
                        elif hasattr(retriever, 'k'):
                            retriever.k = k
                
                docs = hybrid_retriever.invoke(query)
                
                # 去重处理
                for doc in docs:
                    content_hash = hash(doc.page_content)
                    if config.ENABLE_DOCUMENT_DEDUPLICATION:
                        if content_hash not in seen_contents:
                            all_documents.append(doc)
                            seen_contents.add(content_hash)
                    else:
                        all_documents.append(doc)
                        
                print(f"    检索到 {len(docs)} 个文档")
                
            except Exception as e:
                print(f"    查询执行失败: {e}")
                continue
        
        print(f"  - 多查询检索完成，共获得 {len(all_documents)} 个文档")
        return all_documents

    def ask(self, question: str) -> Dict[str, Any]:
        """
        对已加载的文档提出问题，并获取答案。
        支持问题改写功能，提高搜索覆盖面。

        Args:
            question: 用户提出的问题字符串。

        Returns:
            一个字典，包含'result' (答案) 和 'source_documents' (参考的文档片段)。
        """
        if not self.qa_chain:
            return {
                "result": "错误: 问答链尚未初始化。请先调用 `sync_data_directory` 方法加载文档。",
                "source_documents": []
            }
        
        print(f"\n正在处理问题: '{question}'...")
        
        # 如果启用了问题改写功能
        if config.ENABLE_QUERY_REWRITING:
            print("--- 问题改写阶段 ---")
            
            # 1. 改写问题
            rewritten_queries = self._rewrite_query(question)
            
            # 2. 使用多个问题进行检索
            print("--- 多查询检索阶段 ---")
            retrieved_docs = self._retrieve_with_multiple_queries(rewritten_queries)
            
            # 3. 重排序
            print("--- 重排序阶段 ---")
            if retrieved_docs and self.reranker:
                try:
                    # 使用重排序器对所有检索到的文档进行重排序
                    reranked_docs = self.reranker.compress_documents(retrieved_docs, question)
                    final_docs = reranked_docs[:config.RERANKER_TOP_N]
                    print(f"  - 重排序完成，最终选择 {len(final_docs)} 个最相关文档")
                except Exception as e:
                    print(f"  - 重排序失败: {e}，使用原始检索结果")
                    final_docs = retrieved_docs[:config.RERANKER_TOP_N]
            else:
                final_docs = retrieved_docs[:config.RERANKER_TOP_N]
            
            # 4. 生成答案
            print("--- 答案生成阶段 ---")
            if final_docs:
                # 构建上下文
                context = "\n\n".join([doc.page_content for doc in final_docs])
                
                # 使用提示词管理器获取问答提示模板
                qa_template = get_qa_prompt_template()
                prompt = qa_template.format(context=context, question=question)
                response = self.llm.invoke(prompt)
                
                if hasattr(response, 'content'):
                    answer = response.content.strip()
                else:
                    answer = str(response).strip()
                
                return {
                    "result": answer,
                    "source_documents": final_docs
                }
            else:
                return {
                    "result": "根据提供的资料，我无法找到相关信息来回答该问题。",
                    "source_documents": []
                }
        else:
            # 使用原始的问答链
            result = self.qa_chain.invoke({"query": question})
            return result