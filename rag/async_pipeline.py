# rag/async_pipeline.py

import os
import hashlib
import asyncio
from typing import List, Dict, Any, Set, Optional
from concurrent.futures import ThreadPoolExecutor

# 导入同步版本的RagPipeline
from .pipeline import RagPipeline
from . import config
# 导入提示词管理器
from .prompt_manager import get_qa_prompt_template, get_query_rewrite_prompt_template
# 导入短期记忆管理器
from .memory_manager import memory_manager

# 导入需要的组件
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document


class AsyncRagPipeline(RagPipeline):
    """
    异步版本的RAG流程类 (版本 4.0 - 异步增强版)。
    继承自RagPipeline，添加异步操作支持。
    特性:
    - 支持异步操作，提高并发性能
    - 继承所有同步功能
    - 异步问答和检索功能
    - 异步文档管理功能
    """
    def __init__(self):
        """初始化异步RAG流程，继承父类功能并添加线程池。"""
        print("正在初始化异步 RAG Pipeline...")
        # 初始化线程池用于CPU密集型任务
        self.executor = ThreadPoolExecutor(max_workers=4)
        # 调用父类初始化
        super().__init__()
        print("异步 RAG Pipeline 初始化完成。")

    async def _run_in_executor(self, func, *args):
        """在线程池中运行CPU密集型任务。"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)

    async def get_processed_sources_async(self) -> Set[str]:
        """
        异步获取向量数据库中所有已处理过的文档源路径。
        
        Returns:
            一个包含所有唯一源文件路径的集合(Set)。
        """
        if not self.vector_store:
            return set()
        
        try:
            # 在线程池中执行数据库查询
            all_entries = await self._run_in_executor(
                lambda: self.vector_store.get(include=["metadatas"])
            )
            
            sources = {
                metadata['source'] 
                for metadata in all_entries['metadatas'] 
                if metadata and 'source' in metadata
            }
            return sources
        except Exception as e:
            print(f"从数据库获取源文件列表时出错: {e}")
            return set()

    async def _get_file_info_async(self, file_path: str) -> Dict[str, Any]:
        """
        异步获取文件的详细信息，包括修改时间和内容哈希。
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含文件信息的字典
        """
        def _get_file_info_sync():
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
        
        return await self._run_in_executor(_get_file_info_sync)

    async def _get_file_metadata_from_db_async(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        异步从数据库中获取文件的元数据信息。
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件的元数据信息，如果不存在则返回None
        """
        if not self.vector_store:
            return None
        
        try:
            all_entries = await self._run_in_executor(
                lambda: self.vector_store.get(
                    where={"source": file_path},
                    include=["metadatas"]
                )
            )
            
            if all_entries['metadatas']:
                return all_entries['metadatas'][0]
            
            return None
        except Exception as e:
            print(f"从数据库获取文件元数据失败 {file_path}: {e}")
            return None

    async def _is_file_modified_async(self, file_path: str) -> bool:
        """
        异步检查文件是否已被修改。
        
        Args:
            file_path: 文件路径
            
        Returns:
            如果文件已修改返回True，否则返回False
        """
        current_info = await self._get_file_info_async(file_path)
        if not current_info:
            return False
        
        db_metadata = await self._get_file_metadata_from_db_async(file_path)
        if not db_metadata:
            return True  # 数据库中没有该文件，视为新文件
        
        # 比较文件哈希值
        db_hash = db_metadata.get('file_hash')
        return current_info['hash'] != db_hash

    async def delete_documents_by_source_async(self, source_path: str) -> bool:
        """
        异步根据源文件路径删除向量数据库中的相关文档。
        
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
            all_entries = await self._run_in_executor(
                lambda: self.vector_store.get(
                    where={"source": source_path},
                    include=["metadatas"]
                )
            )
            
            if not all_entries['ids']:
                print(f"未找到来源为 '{source_path}' 的文档。")
                return False
            
            # 删除所有相关文档
            await self._run_in_executor(
                lambda: self.vector_store.delete(ids=all_entries['ids'])
            )
            print(f"已删除 {len(all_entries['ids'])} 个来源为 '{source_path}' 的文档块。")
            return True
            
        except Exception as e:
            print(f"删除文档时出错: {e}")
            return False

    async def update_document_async(self, file_path: str) -> bool:
        """
        异步更新单个文档：先删除旧版本，再添加新版本。
        
        Args:
            file_path: 文件路径
            
        Returns:
            更新成功返回True，否则返回False
        """
        try:
            print(f"正在更新文档: {file_path}")
            
            # 1. 删除旧版本
            if not await self.delete_documents_by_source_async(file_path):
                print(f"删除旧版本失败: {file_path}")
                return False
            
            # 2. 异步加载新版本
            def load_document():
                loader = TextLoader(file_path, encoding='utf-8')
                return loader.load()
            
            new_docs = await self._run_in_executor(load_document)
            
            # 3. 添加文件信息到元数据
            file_info = await self._get_file_info_async(file_path)
            if file_info:
                for doc in new_docs:
                    doc.metadata.update({
                        'file_hash': file_info['hash'],
                        'file_mtime': file_info['mtime'],
                        'file_size': file_info['size']
                    })
            
            # 4. 分割文档
            chunks = await self._run_in_executor(
                self.text_splitter.split_documents, new_docs
            )
            
            # 5. 生成唯一ID
            for i, chunk in enumerate(chunks):
                chunk_id = f"{config.DOCUMENT_ID_PREFIX}{hashlib.md5(file_path.encode()).hexdigest()}_{i}"
                chunk.metadata['chunk_id'] = chunk_id
            
            # 6. 添加到数据库
            await self._run_in_executor(
                self.vector_store.add_documents, chunks
            )
            print(f"  - 已更新文档，新增 {len(chunks)} 个文本块。")
            
            return True
            
        except Exception as e:
            print(f"更新文档时出错: {e}")
            return False

    async def sync_data_directory_async(self):
        """
        异步版本的智能同步数据目录。支持多路径、分类管理。
        """
        if config.ENABLE_ENTERPRISE_MODE:
            print("--- 开始异步企业级智能同步 ---")
            await self._sync_enterprise_data_sources_async()
        else:
            print("--- 开始异步传统模式同步 ---")
            await self._sync_legacy_data_directory_async()

    async def _sync_legacy_data_directory_async(self):
        """
        异步版本的传统单一数据目录同步（向后兼容）。
        """
        data_path = config.DATA_PATH
        if not os.path.exists(data_path):
            print(f"警告: 数据目录 '{data_path}' 不存在。")
            return

        print("--- 开始异步智能同步数据目录 ---")
        
        # 1. 异步获取已处理的文件列表
        processed_sources = await self.get_processed_sources_async()
        print(f"数据库中已存在 {len(processed_sources)} 个来源的文件。")

        # 2. 异步扫描数据目录，找出所有 .txt 文件
        def scan_files():
            current_files = []
            for root, _, files in os.walk(data_path):
                for file in files:
                    if file.endswith(".txt"):
                        current_files.append(os.path.join(root, file))
            return current_files
        
        current_files = await self._run_in_executor(scan_files)
        print(f"当前目录中发现 {len(current_files)} 个 .txt 文件。")
        
        # 3. 并发分类处理文件
        new_files = []
        modified_files = []
        unchanged_files = []
        
        # 并发检查文件修改状态
        file_check_tasks = []
        for file_path in current_files:
            if file_path not in processed_sources:
                new_files.append(file_path)
            elif config.ENABLE_FILE_MONITORING:
                file_check_tasks.append(self._is_file_modified_async(file_path))
            else:
                unchanged_files.append(file_path)
        
        # 等待所有文件检查完成
        if file_check_tasks:
            modification_results = await asyncio.gather(*file_check_tasks)
            for i, (file_path, is_modified) in enumerate(zip(
                [f for f in current_files if f in processed_sources and config.ENABLE_FILE_MONITORING],
                modification_results
            )):
                if is_modified:
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
        
        # 6. 并发处理删除的文件
        if deleted_files:
            print("\n--- 处理已删除的文件 ---")
            delete_tasks = [self.delete_documents_by_source_async(file_path) for file_path in deleted_files]
            delete_results = await asyncio.gather(*delete_tasks)
            
            for file_path, success in zip(deleted_files, delete_results):
                if success:
                    print(f"  ✓ 已删除: {file_path}")
                else:
                    print(f"  ✗ 删除失败: {file_path}")
        
        # 7. 并发处理修改的文件
        if modified_files:
            print("\n--- 处理已修改的文件 ---")
            update_tasks = [self.update_document_async(file_path) for file_path in modified_files]
            update_results = await asyncio.gather(*update_tasks)
            
            for file_path, success in zip(modified_files, update_results):
                if success:
                    print(f"  ✓ 已更新: {file_path}")
                else:
                    print(f"  ✗ 更新失败: {file_path}")
        
        # 8. 处理新增的文件
        if new_files:
            print(f"\n--- 处理新增的文件 ---")
            await self._process_new_files_async(new_files)
        
        # 9. 重新构建问答链（如果有任何变化）
        if new_files or modified_files or deleted_files:
            print("\n--- 更新问答链 ---")
            await self._rebuild_qa_chain_async()
            print("问答链已更新，包含最新知识。")
        else:
            print("\n--- 无需更新 ---")
            print("所有文件都是最新的，无需更新问答链。")
        
        print("--- 异步智能同步完成 ---")

    async def _process_new_files_async(self, new_files: List[str]):
        """
        异步处理新增的文件。
        
        Args:
            new_files: 新增文件列表
        """
        print(f"发现 {len(new_files)} 个新文档，正在处理...")
        
        # 并发加载新文档
        async def load_single_file(file_path: str):
            try:
                def load_doc():
                    loader = TextLoader(file_path, encoding='utf-8')
                    return loader.load()
                
                docs = await self._run_in_executor(load_doc)
                
                # 添加文件信息到元数据
                file_info = await self._get_file_info_async(file_path)
                if file_info:
                    for doc in docs:
                        doc.metadata.update({
                            'file_hash': file_info['hash'],
                            'file_mtime': file_info['mtime'],
                            'file_size': file_info['size']
                        })
                
                print(f"  ✓ 已加载: {file_path}")
                return docs
            except Exception as e:
                print(f"  ✗ 加载失败: {file_path} - {e}")
                return []
        
        # 并发加载所有新文件
        load_tasks = [load_single_file(file_path) for file_path in new_files]
        all_docs_lists = await asyncio.gather(*load_tasks)
        
        # 合并所有文档
        new_docs = []
        for docs_list in all_docs_lists:
            new_docs.extend(docs_list)
        
        if new_docs:
            # 分割文档
            chunks = await self._run_in_executor(
                self.text_splitter.split_documents, new_docs
            )
            print(f"  - 新文档被分割成 {len(chunks)} 个文本块。")

            # 生成唯一ID
            for chunk in chunks:
                source_path = chunk.metadata.get('source', '')
                chunk_hash = hashlib.md5(f"{source_path}_{chunk.page_content}".encode()).hexdigest()
                chunk.metadata['chunk_id'] = f"{config.DOCUMENT_ID_PREFIX}{chunk_hash}"

            # 添加到数据库
            if self.vector_store is None:
                print("正在创建新的向量数据库...")
                
                def create_vector_store():
                    from langchain_chroma import Chroma
                    return Chroma.from_documents(
                        documents=chunks,
                        embedding=self.embeddings,
                        persist_directory=config.VECTOR_STORE_PATH
                    )
                
                self.vector_store = await self._run_in_executor(create_vector_store)
                print(f"  - 新的向量数据库已创建于 '{config.VECTOR_STORE_PATH}'。")
            else:
                await self._run_in_executor(self.vector_store.add_documents, chunks)
                print("  - 新的文本块已成功添加到现有数据库。")

    async def _rebuild_qa_chain_async(self):
        """
        异步重新构建问答链。
        """
        def rebuild_sync():
            self._load_all_documents()  # 重新加载所有文档用于关键字检索
            self._build_qa_chain()
        
        await self._run_in_executor(rebuild_sync)

    async def ask_async(self, question: str, use_memory: bool = True) -> Dict[str, Any]:
        """
        异步版本的问答功能。
        支持问题改写功能，提高搜索覆盖面。

        Args:
            question: 用户提出的问题字符串。

        Returns:
            一个字典，包含'result' (答案) 和 'source_documents' (参考的文档片段)。
        """
        if not self.qa_chain:
            return {
                "result": "错误: 问答链尚未初始化。请先调用 `sync_data_directory_async` 方法加载文档。",
                "source_documents": []
            }
        
        print(f"\n正在异步处理问题: '{question}'...")
        
        # 如果启用了问题改写功能
        if config.ENABLE_QUERY_REWRITING:
            print("--- 异步问题改写阶段 ---")
            
            # 1. 异步改写问题
            rewritten_queries = await self._rewrite_query_async(question)
            
            # 2. 使用多个问题进行异步检索
            print("--- 异步多查询检索阶段 ---")
            retrieved_docs = await self._retrieve_with_multiple_queries_async(rewritten_queries)
            
            # 3. 异步重排序
            print("--- 异步重排序阶段 ---")
            if retrieved_docs and self.reranker:
                try:
                    reranked_docs = await self._run_in_executor(
                        self.reranker.compress_documents, retrieved_docs, question
                    )
                    final_docs = reranked_docs[:config.RERANKER_TOP_N]
                    print(f"  - 重排序完成，最终选择 {len(final_docs)} 个最相关文档")
                except Exception as e:
                    print(f"  - 重排序失败: {e}，使用原始检索结果")
                    final_docs = retrieved_docs[:config.RERANKER_TOP_N]
            else:
                final_docs = retrieved_docs[:config.RERANKER_TOP_N]
            
            # 4. 异步生成答案
            print("--- 异步答案生成阶段 ---")
            if final_docs:
                # 构建上下文
                context = "\n\n".join([doc.page_content for doc in final_docs])
                
                # 使用自定义提示模板生成答案
                # 使用提示词管理器获取问答提示模板
                qa_template = get_qa_prompt_template()
                prompt_template = qa_template.template
                
                prompt = prompt_template.format(context=context, question=question)
                response = await self._run_in_executor(self.llm.invoke, prompt)
                
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
            result = await self._run_in_executor(
                self.qa_chain.invoke, {"query": question}
            )
            return result

    async def ask_with_categories_async(self, question: str, categories: List[str] = None) -> Dict[str, Any]:
        """
        异步版本的支持分类检索的问答功能。
        
        Args:
            question: 用户提出的问题字符串
            categories: 指定检索的类别列表，None表示检索所有类别
            
        Returns:
            一个字典，包含'result' (答案) 和 'source_documents' (参考的文档片段)
        """
        if not self.qa_chain:
            return {
                "result": "错误: 问答链尚未初始化。请先调用 `sync_data_directory_async` 方法加载文档。",
                "source_documents": []
            }
        
        # 如果没有指定类别，使用默认类别或所有类别
        if categories is None:
            categories = config.DEFAULT_SEARCH_CATEGORIES
        
        print(f"\n正在异步处理问题: '{question}'...")
        if categories:
            print(f"限定检索类别: {categories}")
        
        # 如果启用了问题改写功能
        if config.ENABLE_QUERY_REWRITING:
            print("--- 异步问题改写阶段 ---")
            
            # 1. 异步改写问题
            rewritten_queries = await self._rewrite_query_async(question)
            
            # 2. 使用多个问题进行异步分类检索
            print("--- 异步多查询分类检索阶段 ---")
            retrieved_docs = await self._retrieve_with_multiple_queries_and_categories_async(rewritten_queries, categories)
            
            # 3. 异步重排序
            print("--- 异步重排序阶段 ---")
            if retrieved_docs and self.reranker:
                try:
                    reranked_docs = await self._run_in_executor(
                        self.reranker.compress_documents, retrieved_docs, question
                    )
                    final_docs = reranked_docs[:config.RERANKER_TOP_N]
                    print(f"  - 重排序完成，最终选择 {len(final_docs)} 个最相关文档")
                except Exception as e:
                    print(f"  - 重排序失败: {e}，使用原始检索结果")
                    final_docs = retrieved_docs[:config.RERANKER_TOP_N]
            else:
                final_docs = retrieved_docs[:config.RERANKER_TOP_N]
            
            # 4. 异步生成答案
            print("--- 异步答案生成阶段 ---")
            if final_docs:
                # 构建上下文
                context = "\n\n".join([doc.page_content for doc in final_docs])
                
                # 使用自定义提示模板生成答案
                # 使用提示词管理器获取问答提示模板
                qa_template = get_qa_prompt_template()
                prompt_template = qa_template.template
                
                prompt = prompt_template.format(context=context, question=question)
                response = await self._run_in_executor(self.llm.invoke, prompt)
                
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
                # 创建临时的分类检索器并异步执行
                def create_category_qa():
                    category_retriever = self._build_category_retriever(categories)
                    compression_retriever = ContextualCompressionRetriever(
                        base_compressor=self.reranker,
                        base_retriever=category_retriever
                    )
                    
                    from langchain.chains import RetrievalQA
                    from langchain_core.prompts import PromptTemplate
                    
                    # 使用提示词管理器获取问答提示模板
                    qa_template = get_qa_prompt_template()
                    prompt_template = qa_template.template
                    QA_CHAIN_PROMPT = PromptTemplate.from_template(prompt_template)
                    
                    temp_qa_chain = RetrievalQA.from_chain_type(
                        llm=self.llm,
                        chain_type="stuff",
                        retriever=compression_retriever,
                        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
                        return_source_documents=True
                    )
                    
                    return temp_qa_chain.invoke({"query": question})
                
                result = await self._run_in_executor(create_category_qa)
                return result
            else:
                # 使用原始的问答链
                result = await self._run_in_executor(
                    self.qa_chain.invoke, {"query": question}
                )
                return result

    async def _rewrite_query_async(self, original_query: str) -> List[str]:
        """
        异步版本的问题改写功能。
        将原始问题改写成多个相关问题，提高搜索覆盖面。
        
        Args:
            original_query: 用户的原始问题
            
        Returns:
            包含原始问题和改写问题的列表
        """
        if not config.ENABLE_QUERY_REWRITING:
            return [original_query]
        
        try:
            # 构建问题改写的提示模板
            from langchain_core.prompts import PromptTemplate
            
            # 使用提示词管理器获取问题改写提示模板
            rewrite_prompt = get_query_rewrite_prompt_template()
            
            # 异步调用LLM进行问题改写
            prompt = rewrite_prompt.format(
                original_query=original_query,
                count=config.QUERY_REWRITE_COUNT
            )
            
            response = await self._run_in_executor(self.llm.invoke, prompt)
            
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

    async def _retrieve_with_multiple_queries_async(self, queries: List[str]) -> List[Document]:
        """
        异步版本的多查询检索功能。
        使用多个查询问题进行检索，并合并结果。
        
        Args:
            queries: 查询问题列表
            
        Returns:
            合并后的文档列表
        """
        all_documents = []
        seen_contents = set()  # 用于去重
        
        # 并发执行所有查询
        async def single_query_retrieve(query: str, index: int):
            print(f"  - 执行查询 {index+1}: {query}")
            
            try:
                # 使用混合检索器进行检索
                def retrieve_sync():
                    hybrid_retriever = self._build_hybrid_retriever()
                    
                    # 为改写的查询使用较少的检索数量
                    if index == 0:  # 原始查询使用正常数量
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
                    
                    return hybrid_retriever.invoke(query)
                
                docs = await self._run_in_executor(retrieve_sync)
                print(f"    检索到 {len(docs)} 个文档")
                return docs
                
            except Exception as e:
                print(f"    查询执行失败: {e}")
                return []
        
        # 并发执行所有查询
        query_tasks = [single_query_retrieve(query, i) for i, query in enumerate(queries)]
        all_docs_lists = await asyncio.gather(*query_tasks)
        
        # 合并结果并去重
        for docs_list in all_docs_lists:
            for doc in docs_list:
                content_hash = hash(doc.page_content)
                if config.ENABLE_DOCUMENT_DEDUPLICATION:
                    if content_hash not in seen_contents:
                        all_documents.append(doc)
                        seen_contents.add(content_hash)
                else:
                    all_documents.append(doc)
        
        print(f"  - 异步多查询检索完成，共获得 {len(all_documents)} 个文档")
        return all_documents

    async def _retrieve_with_multiple_queries_and_categories_async(self, queries: List[str], categories: List[str] = None) -> List[Document]:
        """
        异步版本的多查询分类检索功能。
        使用多个查询问题进行分类检索，并合并结果。
        
        Args:
            queries: 查询问题列表
            categories: 指定检索的类别列表
            
        Returns:
            合并后的文档列表
        """
        all_documents = []
        seen_contents = set()
        
        # 并发执行所有查询
        async def single_category_query_retrieve(query: str, index: int):
            print(f"  - 执行查询 {index+1}: {query}")
            
            try:
                # 使用分类检索器进行检索
                def retrieve_sync():
                    if categories:
                        category_retriever = self._build_category_retriever(categories)
                    else:
                        category_retriever = self._build_hybrid_retriever()
                    
                    # 为改写的查询使用较少的检索数量
                    if index == 0:
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
                    
                    return category_retriever.invoke(query)
                
                docs = await self._run_in_executor(retrieve_sync)
                print(f"    检索到 {len(docs)} 个文档")
                return docs
                
            except Exception as e:
                print(f"    查询执行失败: {e}")
                return []
        
        # 并发执行所有查询
        query_tasks = [single_category_query_retrieve(query, i) for i, query in enumerate(queries)]
        all_docs_lists = await asyncio.gather(*query_tasks)
        
        # 合并结果并去重
        for docs_list in all_docs_lists:
            for doc in docs_list:
                content_hash = hash(doc.page_content)
                if config.ENABLE_DOCUMENT_DEDUPLICATION:
                    if content_hash not in seen_contents:
                        all_documents.append(doc)
                        seen_contents.add(content_hash)
                else:
                    all_documents.append(doc)
        
        print(f"  - 异步多查询分类检索完成，共获得 {len(all_documents)} 个文档")
        return all_documents

    async def _sync_enterprise_data_sources_async(self):
        """
        异步版本的企业级多数据源同步。
        """
        # 1. 异步扫描所有企业级数据源
        def scan_enterprise_files():
            return self._scan_enterprise_files()
        
        all_files_by_source = await self._run_in_executor(scan_enterprise_files)
        
        # 2. 异步获取已处理的文件列表
        processed_sources = await self.get_processed_sources_async()
        print(f"数据库中已存在 {len(processed_sources)} 个来源的文件。")
        
        # 3. 合并所有数据源的文件
        all_current_files = []
        for source_name, files in all_files_by_source.items():
            all_current_files.extend(files)
        
        print(f"所有数据源共发现 {len(all_current_files)} 个文件。")
        
        # 4. 并发分类处理文件
        new_files = []
        modified_files = []
        unchanged_files = []
        
        # 并发检查文件修改状态
        file_check_tasks = []
        for file_path in all_current_files:
            if file_path not in processed_sources:
                new_files.append(file_path)
            elif config.ENABLE_FILE_MONITORING:
                file_check_tasks.append(self._is_file_modified_async(file_path))
            else:
                unchanged_files.append(file_path)
        
        # 等待所有文件检查完成
        if file_check_tasks:
            modification_results = await asyncio.gather(*file_check_tasks)
            for i, (file_path, is_modified) in enumerate(zip(
                [f for f in all_current_files if f in processed_sources and config.ENABLE_FILE_MONITORING],
                modification_results
            )):
                if is_modified:
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
        
        # 7. 并发处理删除的文件
        if deleted_files:
            print("\n--- 处理已删除的文件 ---")
            delete_tasks = [self.delete_documents_by_source_async(file_path) for file_path in deleted_files]
            delete_results = await asyncio.gather(*delete_tasks)
            
            for file_path, success in zip(deleted_files, delete_results):
                if success:
                    print(f"  ✓ 已删除: {file_path}")
                else:
                    print(f"  ✗ 删除失败: {file_path}")
        
        # 8. 并发处理修改的文件
        if modified_files:
            print("\n--- 处理已修改的文件 ---")
            update_tasks = [self._update_enterprise_document_async(file_path, all_files_by_source) for file_path in modified_files]
            update_results = await asyncio.gather(*update_tasks)
            
            for file_path, success in zip(modified_files, update_results):
                if success:
                    print(f"  ✓ 已更新: {file_path}")
                else:
                    print(f"  ✗ 更新失败: {file_path}")
        
        # 9. 处理新增的文件
        if new_files:
            print(f"\n--- 处理新增的文件 ---")
            await self._process_new_enterprise_files_async(new_files, all_files_by_source)
        
        # 10. 重新构建问答链（如果有任何变化）
        if new_files or modified_files or deleted_files:
            print("\n--- 更新问答链 ---")
            await self._rebuild_qa_chain_async()
            print("问答链已更新，包含最新知识。")
        else:
            print("\n--- 无需更新 ---")
            print("所有文件都是最新的，无需更新问答链。")
        
        print("--- 异步企业级智能同步完成 ---")

    async def _update_enterprise_document_async(self, file_path: str, all_files_by_source: Dict[str, List[str]]) -> bool:
        """
        异步更新企业级文档，包含分类信息。
        
        Args:
            file_path: 文件路径
            all_files_by_source: 按数据源分组的文件列表
            
        Returns:
            更新成功返回True，否则返回False
        """
        try:
            print(f"正在更新企业级文档: {file_path}")
            
            # 1. 删除旧版本
            if not await self.delete_documents_by_source_async(file_path):
                print(f"删除旧版本失败: {file_path}")
                return False
            
            # 2. 获取文件对应的数据源配置
            source_config = self._get_source_config_for_file(file_path, all_files_by_source)
            
            if not source_config:
                print(f"未找到文件 {file_path} 对应的数据源配置")
                return False
            
            # 3. 异步加载新版本
            def load_document():
                loader = TextLoader(file_path, encoding='utf-8')
                return loader.load()
            
            new_docs = await self._run_in_executor(load_document)
            
            # 4. 添加文件信息和分类信息到元数据
            file_info = await self._get_file_info_async(file_path)
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
            chunks = await self._run_in_executor(
                self.text_splitter.split_documents, new_docs
            )
            
            # 6. 生成唯一ID
            for i, chunk in enumerate(chunks):
                chunk_id = f"{config.DOCUMENT_ID_PREFIX}{hashlib.md5(file_path.encode()).hexdigest()}_{i}"
                chunk.metadata['chunk_id'] = chunk_id
            
            # 7. 添加到数据库
            await self._run_in_executor(
                self.vector_store.add_documents, chunks
            )
            print(f"  - 已更新文档，新增 {len(chunks)} 个文本块，类别: {source_config['category']}")
            
            return True
            
        except Exception as e:
            print(f"更新企业级文档时出错: {e}")
            return False

    async def _process_new_enterprise_files_async(self, new_files: List[str], all_files_by_source: Dict[str, List[str]]):
        """
        异步处理新增的企业级文件。
        
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
        
        # 并发按类别处理文件
        async def process_category_files(category: str, file_configs: List[tuple]):
            print(f"\n处理类别 '{category}' 的文件:")
            
            async def load_single_enterprise_file(file_path: str, source_config: Dict[str, Any]):
                try:
                    def load_doc():
                        loader = TextLoader(file_path, encoding='utf-8')
                        return loader.load()
                    
                    docs = await self._run_in_executor(load_doc)
                    
                    # 添加文件信息和分类信息到元数据
                    file_info = await self._get_file_info_async(file_path)
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
                    
                    print(f"  ✓ 已加载: {file_path} (类别: {category})")
                    return docs
                except Exception as e:
                    print(f"  ✗ 加载失败: {file_path} - {e}")
                    return []
            
            # 并发加载该类别的所有文件
            load_tasks = [load_single_enterprise_file(file_path, source_config) for file_path, source_config in file_configs]
            all_docs_lists = await asyncio.gather(*load_tasks)
            
            # 合并该类别的所有文档
            category_docs = []
            for docs_list in all_docs_lists:
                category_docs.extend(docs_list)
            
            return category_docs
        
        # 并发处理所有类别
        category_tasks = [process_category_files(category, file_configs) for category, file_configs in files_by_category.items()]
        all_category_docs = await asyncio.gather(*category_tasks)
        
        # 合并所有类别的文档
        all_new_docs = []
        for category_docs in all_category_docs:
            all_new_docs.extend(category_docs)
        
        if all_new_docs:
            chunks = await self._run_in_executor(
                self.text_splitter.split_documents, all_new_docs
            )
            print(f"\n新文档被分割成 {len(chunks)} 个文本块。")

            # 生成唯一ID并添加分类信息
            for chunk in chunks:
                source_path = chunk.metadata.get('source', '')
                chunk_hash = hashlib.md5(f"{source_path}_{chunk.page_content}".encode()).hexdigest()
                chunk.metadata['chunk_id'] = f"{config.DOCUMENT_ID_PREFIX}{chunk_hash}"

            # 添加到数据库
            if self.vector_store is None:
                print("正在创建新的向量数据库...")
                
                def create_vector_store():
                    from langchain_chroma import Chroma
                    return Chroma.from_documents(
                        documents=chunks,
                        embedding=self.embeddings,
                        persist_directory=config.VECTOR_STORE_PATH
                    )
                
                self.vector_store = await self._run_in_executor(create_vector_store)
                print(f"  - 新的向量数据库已创建于 '{config.VECTOR_STORE_PATH}'。")
            else:
                await self._run_in_executor(self.vector_store.add_documents, chunks)
                print("  - 新的文本块已成功添加到现有数据库。")
            
            # 按类别统计
            category_stats = {}
            for chunk in chunks:
                category = chunk.metadata.get('category', 'unknown')
                category_stats[category] = category_stats.get(category, 0) + 1
            
            print("按类别统计:")
            for category, count in category_stats.items():
                print(f"  - {category}: {count} 个文本块")

    def __del__(self):
        """析构函数，清理线程池资源。"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)