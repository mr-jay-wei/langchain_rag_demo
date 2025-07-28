# 项目概览: rag_example

本文档由`generate_project_overview.py`自动生成，包含了项目的结构树和所有可读文件的内容。

## 项目结构

```
rag_example/
├── rag
│   ├── prompts
│   │   ├── prompt_README.md
│   │   ├── qa_prompt.txt
│   │   └── query_rewrite_prompt.txt
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

---

# 文件内容

## `.env_example`

```
CLOUD_INFINI_API_KEY = ""
CLOUD_BASE_URL = ""
CLOUD_MODEL_NAME = ""
DeepSeek_api_key = ""
DeepSeek_base_url = ""
DeepSeek_model_name = ""
```

## `.gitignore`

```
# Python-generated files
__pycache__/
*.py[oc]
build/
dist/
wheels/
*.egg-info

# Virtual environments
.venv

```

## `.python-version`

```
3.12

```

## `async_main.py`

```python
# async_main.py - 异步RAG系统使用示例

import asyncio
import time
from rag.async_pipeline import AsyncRagPipeline


async def main():
    """异步RAG系统的主要演示函数。"""
    print("=" * 60)
    print("🚀 异步RAG系统演示")
    print("=" * 60)
    
    # 初始化异步RAG流程
    rag = AsyncRagPipeline()
    
    # 异步同步数据目录
    print("\n📁 开始异步同步数据目录...")
    start_time = time.time()
    await rag.sync_data_directory_async()
    sync_time = time.time() - start_time
    print(f"✅ 异步同步完成，耗时: {sync_time:.2f}秒")
    
    # 测试问题列表
    # test_questions = [
    #     "什么是机器学习？",
    # ]
    test_questions = [
        "什么是机器学习？",
        "Python有什么优势？",
        "如何使用RAG系统？",
        "什么是混合检索？",
        "企业级功能有哪些？"
    ]


    print("\n🤖 开始异步问答测试...")
    print("-" * 50)
    
    # 并发执行多个问答
    async def ask_question(question: str, index: int):
        print(f"\n[问题 {index + 1}] {question}")
        start_time = time.time()
        
        result = await rag.ask_async(question)
        
        end_time = time.time()
        print(f"⏱️  响应时间: {end_time - start_time:.2f}秒")
        print(f"📝 回答: {result['result']}")
        
        if result['source_documents']:
            print(f"📚 参考文档数量: {len(result['source_documents'])}")
            for i, doc in enumerate(result['source_documents'][:2]):  # 只显示前2个
                source = doc.metadata.get('source', '未知来源')
                print(f"   [{i+1}] {source}")
        
        return result
    
    # 并发执行所有问答
    start_time = time.time()
    tasks = [ask_question(question, i) for i, question in enumerate(test_questions)]
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    print(f"\n✅ 所有问答完成，总耗时: {total_time:.2f}秒")
    print(f"📊 平均每个问题耗时: {total_time / len(test_questions):.2f}秒")
    
    # 测试分类检索功能
    print("\n🏷️  测试异步分类检索功能...")
    print("-" * 50)
    
    # 获取可用类别
    categories = rag.get_available_categories()
    print(f"📋 可用类别: {list(categories.keys())}")
    
    if categories:
        # 测试分类检索
        category_list = list(categories.keys())[:2]  # 取前两个类别
        question = "这个系统有什么特点？"
        
        print(f"\n[分类检索测试] 问题: {question}")
        print(f"🎯 限定类别: {category_list}")
        
        start_time = time.time()
        result = await rag.ask_with_categories_async(question, category_list)
        end_time = time.time()
        
        print(f"⏱️  响应时间: {end_time - start_time:.2f}秒")
        print(f"📝 回答: {result['result']}")
        
        if result['source_documents']:
            print(f"📚 参考文档数量: {len(result['source_documents'])}")
            for i, doc in enumerate(result['source_documents']):
                source = doc.metadata.get('source', '未知来源')
                category = doc.metadata.get('category', '未知类别')
                print(f"   [{i+1}] {source} (类别: {category})")
    
    print("\n" + "=" * 60)
    print("🎉 异步RAG系统演示完成！")
    print("=" * 60)


async def performance_comparison():
    """性能对比测试：同步 vs 异步"""
    print("\n" + "=" * 60)
    print("⚡ 性能对比测试：同步 vs 异步")
    print("=" * 60)
    
    # 导入同步版本
    from rag.pipeline import RagPipeline
    
    # 测试问题
    test_questions = [
        "什么是人工智能？",
        "Python编程语言的特点",
        "如何优化系统性能？"
    ]
    
    # 同步版本测试
    print("\n🔄 同步版本测试...")
    sync_rag = RagPipeline()
    sync_rag.sync_data_directory()
    
    sync_start = time.time()
    sync_results = []
    for question in test_questions:
        result = sync_rag.ask(question)
        sync_results.append(result)
    sync_time = time.time() - sync_start
    
    print(f"✅ 同步版本完成，耗时: {sync_time:.2f}秒")
    
    # 异步版本测试
    print("\n⚡ 异步版本测试...")
    async_rag = AsyncRagPipeline()
    await async_rag.sync_data_directory_async()
    
    async_start = time.time()
    async_tasks = [async_rag.ask_async(question) for question in test_questions]
    async_results = await asyncio.gather(*async_tasks)
    async_time = time.time() - async_start
    
    print(f"✅ 异步版本完成，耗时: {async_time:.2f}秒")
    
    # 性能对比
    print(f"\n📊 性能对比结果:")
    print(f"   同步版本: {sync_time:.2f}秒")
    print(f"   异步版本: {async_time:.2f}秒")
    if sync_time > async_time:
        improvement = ((sync_time - async_time) / sync_time) * 100
        print(f"   🚀 异步版本提升: {improvement:.1f}%")
    else:
        print(f"   ⚠️  在此测试中同步版本更快（可能由于问题简单或并发开销）")


async def batch_processing_demo():
    """批量处理演示"""
    print("\n" + "=" * 60)
    print("📦 批量处理演示")
    print("=" * 60)
    
    rag = AsyncRagPipeline()
    await rag.sync_data_directory_async()
    
    # 大量问题批量处理
    batch_questions = [
        "什么是机器学习？",
        "深度学习的应用领域",
        "Python的优势是什么？",
        "如何优化算法性能？",
        "数据科学的工作流程",
        "人工智能的发展趋势",
        "编程语言的选择标准",
        "系统架构设计原则",
        "数据库优化技巧",
        "云计算的优势"
    ]
    
    print(f"📝 准备处理 {len(batch_questions)} 个问题...")
    
    # 分批处理（每批5个）
    batch_size = 5
    all_results = []
    all_response_times = []
    
    for i in range(0, len(batch_questions), batch_size):
        batch = batch_questions[i:i + batch_size]
        print(f"\n🔄 处理第 {i//batch_size + 1} 批 ({len(batch)} 个问题)...")
        
        # 为每个问题单独计时
        async def ask_with_timing(question):
            start_time = time.time()
            result = await rag.ask_async(question)
            end_time = time.time()
            response_time = end_time - start_time
            return result, response_time
        
        batch_start = time.time()
        batch_tasks = [ask_with_timing(question) for question in batch]
        batch_results_with_timing = await asyncio.gather(*batch_tasks)
        batch_time = time.time() - batch_start
        
        # 分离结果和响应时间
        batch_results = [result for result, _ in batch_results_with_timing]
        batch_response_times = [response_time for _, response_time in batch_results_with_timing]
        
        all_results.extend(batch_results)
        all_response_times.extend(batch_response_times)
        
        avg_batch_response_time = sum(batch_response_times) / len(batch_response_times)
        print(f"✅ 第 {i//batch_size + 1} 批完成，总耗时: {batch_time:.2f}秒，平均单问题: {avg_batch_response_time:.2f}秒")
    
    print(f"\n🎉 批量处理完成！")
    print(f"📊 总共处理: {len(all_results)} 个问题")
    print(f"⏱️  平均响应时间: {sum(all_response_times) / len(all_response_times):.2f}秒")
    print(f"⚡ 最快响应: {min(all_response_times):.2f}秒")
    print(f"🐌 最慢响应: {max(all_response_times):.2f}秒")


if __name__ == "__main__":
    # 运行主演示
    # asyncio.run(main())
    
    # 可选：运行性能对比测试
    # asyncio.run(performance_comparison())
    
    # 可选：运行批量处理演示
    asyncio.run(batch_processing_demo())
```

## `main.py`

```python
# main.py

import os
from rag.pipeline import RagPipeline
from rag.config import DATA_PATH # 导入数据路径

def setup_data_directory():
    """检查并创建.data目录和示例文件（如果不存在）。"""
    if not os.path.exists(DATA_PATH):
        print(f"正在创建数据目录: {DATA_PATH}")
        os.makedirs(DATA_PATH)
    
    sample_file_path = os.path.join(DATA_PATH, "initial_doc.txt")
    if not os.path.exists(sample_file_path):
        print(f"正在创建示例文件: {sample_file_path}")
        with open(sample_file_path, "w", encoding="utf-8") as f:
            f.write("这是系统初始化的示例文档。你可以向.data目录添加更多.txt文件。")

def run_demo():
    """运行一个完整的RAG演示，具备智能数据同步功能。"""
    print("=" * 50)
    print("          欢迎使用本地RAG问答系统 (V3.0)")
    print("=" * 50)

    # 0. 准备工作：确保.data目录存在
    setup_data_directory()

    # 1. 初始化RAG Pipeline
    # 它会自动尝试加载现有数据库
    rag_pipeline = RagPipeline()

    # 2. 核心步骤：同步数据文件夹
    print("\n--- 正在检查并同步知识库 ---")
    rag_pipeline.sync_data_directory()
    
    # 3. 开始交互式问答
    print("\n--- 问答环节 ---")
    print("知识库已就绪。您可以开始提问了。输入 '退出' 或 'exit' 或 'quit' 来结束程序。")
    
    while True:
        question = input("\n[您]：")
        if question.lower() in ['退出', 'exit', 'quit']:
            print("感谢使用，再见！")
            break
            
        if not question.strip():
            print("[系统]：问题不能为空，请重新输入。")
            continue
            
        answer_dict = rag_pipeline.ask(question)
        
        print("\n" + "-"*20 + " 回答 " + "-"*20)
        print(f"[机器人]：{answer_dict.get('result', '未能获取到答案。').strip()}")
        
        source_documents = answer_dict.get('source_documents', [])
        if source_documents:
            print("\n--- 参考资料来源 ---")
            for i, doc in enumerate(source_documents):
                source = doc.metadata.get('source', '未知来源')
                print(f"[{i+1}] 来源: {os.path.basename(source)}")
                print(f"    内容: {doc.page_content.replace('\n', ' ')}\n")
        print("-" * 46)

if __name__ == "__main__":
    run_demo()
```

## `pyproject.toml`

```
[project]
name = "rag-example"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "chromadb>=1.0.15",
    "dotenv>=0.9.9",
    "fastapi>=0.116.1",
    "jieba>=0.42.1",
    "langchain>=0.3.26",
    "langchain-chroma>=0.2.5",
    "langchain-community>=0.3.27",
    "langchain-huggingface>=0.3.1",
    "langchain-openai>=0.3.28",
    "openai>=1.97.0",
    "python-multipart>=0.0.20",
    "rank-bm25>=0.2.2",
    "sentence-transformers>=5.0.0",
    "sse-starlette>=3.0.2",
    "uvicorn>=0.35.0",
    "watchdog>=6.0.0",
    "websockets>=14.0",
]

```

## `rag/__init__.py`

```python
[文件为空]
```

## `rag/async_pipeline.py`

```python
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
        
        # 获取短期记忆上下文（所有分支都需要）
        memory_context = ""
        if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
            memory_context = memory_manager.get_conversation_context(include_count=None)  # 使用所有对话轮次
            if memory_context:
                print("--- 短期记忆上下文 ---")
                print(f"包含 {len(memory_manager.get_recent_conversations())} 轮对话作为上下文")
        
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
                
                # 构建完整的上下文（包含记忆上下文和检索上下文）
                full_context = context
                if memory_context:
                    full_context = f"对话历史:\n{memory_context}\n\n当前检索到的相关信息:\n{context}"
                
                # 使用自定义提示模板生成答案
                # 使用提示词管理器获取问答提示模板
                qa_template = get_qa_prompt_template()
                prompt_template = qa_template.template
                
                prompt = prompt_template.format(context=full_context, question=question)
                response = await self._run_in_executor(self.llm.invoke, prompt)
                
                if hasattr(response, 'content'):
                    answer = response.content.strip()
                else:
                    answer = str(response).strip()
                
                # 保存对话到短期记忆
                if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
                    memory_manager.add_conversation(
                        question=question,
                        answer=answer,
                        metadata={
                            "source_documents_count": len(final_docs),
                            "memory_context_included": bool(memory_context),
                            "async_mode": True
                        }
                    )
                
                return {
                    "result": answer,
                    "source_documents": final_docs
                }
            else:
                no_result_answer = "根据提供的资料，我无法回答该问题。"
                
                # 保存对话到短期记忆
                if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
                    memory_manager.add_conversation(
                        question=question,
                        answer=no_result_answer,
                        metadata={
                            "source_documents_count": 0,
                            "memory_context_included": False,
                            "async_mode": True,
                            "no_result": True
                        }
                    )
                
                return {
                    "result": no_result_answer,
                    "source_documents": []
                }
        else:
            # 使用原始的问答链，但需要手动处理记忆上下文
            print("--- 异步原始问答链模式 ---")
            
            # 先获取相关文档
            retriever = self.qa_chain.retriever
            retrieved_docs = await self._run_in_executor(
                retriever.get_relevant_documents, question
            )
            
            if retrieved_docs:
                # 构建上下文
                context = "\n\n".join([doc.page_content for doc in retrieved_docs])
                
                # 构建完整的上下文（包含记忆上下文和检索上下文）
                full_context = context
                if memory_context:
                    full_context = f"对话历史:\n{memory_context}\n\n当前检索到的相关信息:\n{context}"
                
                # 使用提示词管理器获取问答提示模板
                qa_template = get_qa_prompt_template()
                prompt = qa_template.format(context=full_context, question=question)
                response = await self._run_in_executor(self.llm.invoke, prompt)
                
                if hasattr(response, 'content'):
                    answer = response.content.strip()
                else:
                    answer = str(response).strip()
                
                result = {
                    "result": answer,
                    "source_documents": retrieved_docs
                }
            else:
                no_result_answer = "根据提供的资料，我无法回答该问题。"
                result = {
                    "result": no_result_answer,
                    "source_documents": []
                }
            
            # 保存对话到短期记忆（原始问答链模式）
            if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
                memory_manager.add_conversation(
                    question=question,
                    answer=result.get("result", ""),
                    metadata={
                        "source_documents_count": len(result.get("source_documents", [])),
                        "memory_context_included": bool(memory_context),
                        "async_mode": True,
                        "original_chain": True
                    }
                )
            
            return result

    async def ask_with_categories_async(self, question: str, categories: List[str] = None, use_memory: bool = True) -> Dict[str, Any]:
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
        
        # 获取短期记忆上下文（所有分支都需要）
        memory_context = ""
        if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
            memory_context = memory_manager.get_conversation_context(include_count=None)  # 使用所有对话轮次
            if memory_context:
                print("--- 短期记忆上下文 ---")
                print(f"包含 {len(memory_manager.get_recent_conversations())} 轮对话作为上下文")
        
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
                
                # 构建完整的上下文（包含记忆上下文和检索上下文）
                full_context = context
                if memory_context:
                    full_context = f"对话历史:\n{memory_context}\n\n当前检索到的相关信息:\n{context}"
                
                # 使用自定义提示模板生成答案
                # 使用提示词管理器获取问答提示模板
                qa_template = get_qa_prompt_template()
                prompt_template = qa_template.template
                
                prompt = prompt_template.format(context=full_context, question=question)
                response = await self._run_in_executor(self.llm.invoke, prompt)
                
                if hasattr(response, 'content'):
                    answer = response.content.strip()
                else:
                    answer = str(response).strip()
                
                # 保存对话到短期记忆
                if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
                    memory_manager.add_conversation(
                        question=question,
                        answer=answer,
                        metadata={
                            "used_query_rewriting": True,
                            "used_categories": categories,
                            "memory_context_included": bool(memory_context),
                            "source_documents_count": len(final_docs),
                            "async_mode": True
                        }
                    )
                
                return {
                    "result": answer,
                    "source_documents": final_docs
                }
            else:
                no_result_answer = "根据提供的资料，我无法回答该问题。"
                
                # 保存对话到短期记忆
                if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
                    memory_manager.add_conversation(
                        question=question,
                        answer=no_result_answer,
                        metadata={
                            "used_query_rewriting": True,
                            "used_categories": categories,
                            "memory_context_included": bool(memory_context),
                            "source_documents_count": 0,
                            "async_mode": True,
                            "no_result": True
                        }
                    )
                
                return {
                    "result": no_result_answer,
                    "source_documents": []
                }
        else:
            # 使用分类检索的问答链，但需要手动处理记忆上下文
            if categories:
                print("--- 异步分类检索模式 ---")
                
                # 创建临时的分类检索器并异步执行
                def get_category_docs():
                    category_retriever = self._build_category_retriever(categories)
                    compression_retriever = ContextualCompressionRetriever(
                        base_compressor=self.reranker,
                        base_retriever=category_retriever
                    )
                    return compression_retriever.get_relevant_documents(question)
                
                retrieved_docs = await self._run_in_executor(get_category_docs)
                
                if retrieved_docs:
                    # 构建上下文
                    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
                    
                    # 构建完整的上下文（包含记忆上下文和检索上下文）
                    full_context = context
                    if memory_context:
                        full_context = f"对话历史:\n{memory_context}\n\n当前检索到的相关信息:\n{context}"
                    
                    # 使用提示词管理器获取问答提示模板
                    qa_template = get_qa_prompt_template()
                    prompt = qa_template.format(context=full_context, question=question)
                    response = await self._run_in_executor(self.llm.invoke, prompt)
                    
                    if hasattr(response, 'content'):
                        answer = response.content.strip()
                    else:
                        answer = str(response).strip()
                    
                    result = {
                        "result": answer,
                        "source_documents": retrieved_docs
                    }
                else:
                    no_result_answer = "根据提供的资料，我无法回答该问题。"
                    result = {
                        "result": no_result_answer,
                        "source_documents": []
                    }
                
                # 保存对话到短期记忆
                if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
                    memory_manager.add_conversation(
                        question=question,
                        answer=result.get("result", ""),
                        metadata={
                            "used_query_rewriting": False,
                            "used_categories": categories,
                            "memory_context_included": bool(memory_context),
                            "source_documents_count": len(result.get("source_documents", [])),
                            "async_mode": True
                        }
                    )
                
                return result
            else:
                # 使用原始的问答链，但需要手动处理记忆上下文
                print("--- 异步原始问答链模式 (ask_with_categories) ---")
                
                # 先获取相关文档
                retriever = self.qa_chain.retriever
                retrieved_docs = await self._run_in_executor(
                    retriever.get_relevant_documents, question
                )
                
                if retrieved_docs:
                    # 构建上下文
                    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
                    
                    # 构建完整的上下文（包含记忆上下文和检索上下文）
                    full_context = context
                    if memory_context:
                        full_context = f"对话历史:\n{memory_context}\n\n当前检索到的相关信息:\n{context}"
                    
                    # 使用提示词管理器获取问答提示模板
                    qa_template = get_qa_prompt_template()
                    prompt = qa_template.format(context=full_context, question=question)
                    response = await self._run_in_executor(self.llm.invoke, prompt)
                    
                    if hasattr(response, 'content'):
                        answer = response.content.strip()
                    else:
                        answer = str(response).strip()
                    
                    result = {
                        "result": answer,
                        "source_documents": retrieved_docs
                    }
                else:
                    no_result_answer = "根据提供的资料，我无法回答该问题。"
                    result = {
                        "result": no_result_answer,
                        "source_documents": []
                    }
                
                # 保存对话到短期记忆
                if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
                    memory_manager.add_conversation(
                        question=question,
                        answer=result.get("result", ""),
                        metadata={
                            "used_query_rewriting": False,
                            "used_categories": None,
                            "memory_context_included": bool(memory_context),
                            "source_documents_count": len(result.get("source_documents", [])),
                            "async_mode": True
                        }
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

```

## `rag/config.py`

```python
# rag/config.py

from typing import Dict, Any

# --- 模型配置 ---

# 改回Hugging Face上的标准模型名称
EMBEDDING_MODEL_NAME: str = r'../local_models/bge-small-zh-v1.5'
RERANKER_MODEL_NAME: str = r'../local_models/bge-reranker-base/snapshots/2cfc18c9415c912f9d8155881c133215df768a70'

# 模型运行参数: 强制在CPU上运行，并设置缓存目录
VECTOR_STORE_PATH: str = "my_chromadb_vector_store" 
MODEL_DEVICE: str = "cpu"
EMBEDDING_MODEL_KWARGS: Dict[str, Any] = {"device": MODEL_DEVICE}
RERANKER_MODEL_KWARGS: Dict[str, Any] = {"device": MODEL_DEVICE}

# --- 企业级多路径数据源配置 ---

# 传统单一数据路径（向后兼容）
DATA_PATH: str = "./data"

# 企业级多路径数据源配置
# 支持多个硬盘/目录，每个路径可以指定类别
ENTERPRISE_DATA_SOURCES: Dict[str, Dict[str, Any]] = {
    # 主数据目录
    "main": {
        "path": "./data",
        "category": "general",
        "description": "通用知识库",
        "enabled": True,
        "file_patterns": ["*.txt", "*.md", "*.pdf"],
        "priority": 1 # 预留字段，用于未来的优先级功能
    },
    
    # 技术文档目录
    "technical": {
        "path": "./data/technical",
        "category": "technical",
        "description": "技术文档库",
        "enabled": True,
        "file_patterns": ["*.txt", "*.md"],
        "priority": 2 # 预留字段，用于未来的优先级功能
    },
    
    # 产品文档目录
    "product": {
        "path": "./data/product",
        "category": "product",
        "description": "产品文档库",
        "enabled": True,
        "file_patterns": ["*.txt", "*.md"],
        "priority": 3 # 预留字段，用于未来的优先级功能
    },
    
    # 可以添加更多数据源，比如不同硬盘的路径
    # "disk_d": {
    #     "path": "D:/enterprise_docs",
    #     "category": "enterprise",
    #     "description": "企业文档库(D盘)",
    #     "enabled": True,
    #     "file_patterns": ["*.txt", "*.md", "*.pdf"],
    #     "priority": 4 # 预留字段，用于未来的优先级功能
    # },
    
    # "disk_e": {
    #     "path": "E:/research_docs",
    #     "category": "research",
    #     "description": "研究文档库(E盘)",
    #     "enabled": True,
    #     "file_patterns": ["*.txt", "*.md"],
    #     "priority": 5 # 预留字段，用于未来的优先级功能
    # }
}

# 是否启用企业级多路径模式
ENABLE_ENTERPRISE_MODE: bool = True

# 默认检索的类别（空列表表示检索所有类别）
DEFAULT_SEARCH_CATEGORIES: list = []  # 例如: ["technical", "product"]

# 类别优先级（数字越小优先级越高）
CATEGORY_PRIORITIES: Dict[str, int] = {
    "general": 1,
    "technical": 2,
    "product": 3,
    "enterprise": 4,
    "research": 5
}


# --- 文档处理配置 ---

# 文本分割块大小: 将文档分割成的小块的最大字符数
CHUNK_SIZE: int = 500
# 文本分割块重叠: 相邻块之间的重叠字符数，以保证语义连续性
CHUNK_OVERLAP: int = 150


# --- 短期记忆配置 ---

# 是否启用短期记忆功能
ENABLE_SHORT_TERM_MEMORY: bool = True

# 短期记忆最大字符长度（100k字符）
SHORT_TERM_MEMORY_MAX_LENGTH: int = 100_000

# 单条对话记录的最大字符长度（防止单条记录过长）
# 设置为总记忆的1/5，确保至少能容纳5轮对话
SINGLE_CONVERSATION_MAX_LENGTH: int = 20_000

# 记忆保留的最小对话轮数（即使超过长度限制也保留最近的N轮对话）
MIN_CONVERSATION_ROUNDS: int = 1

# 记忆清理策略
# "auto" - 自动清理最旧的记录
# "manual" - 手动清理
# "sliding_window" - 滑动窗口，保持固定数量的对话
MEMORY_CLEANUP_STRATEGY: str = "auto"

# 滑动窗口大小（当策略为sliding_window时使用）
SLIDING_WINDOW_SIZE: int = 20

# --- 热重载配置 ---

# 是否启用提示词热重载功能
ENABLE_HOT_RELOAD: bool = True

# 热重载防抖时间（秒）
HOT_RELOAD_DEBOUNCE_TIME: float = 0.5

# --- 检索与重排序配置 ---

# 向量检索Top K: 从向量数据库中初步检索出的最相似文档数量
RETRIEVER_TOP_K: int = 10

# 关键字检索Top K: 从关键字检索中获取的文档数量
KEYWORD_RETRIEVER_TOP_K: int = 5

# 混合检索权重配置
VECTOR_SEARCH_WEIGHT: float = 0.7  # 向量检索权重
KEYWORD_SEARCH_WEIGHT: float = 0.3  # 关键字检索权重

# 重排序Top N: 经过重排序后，最终选送给大语言模型的文档数量
RERANKER_TOP_N: int = 3

# 是否启用混合检索 (True: 混合检索, False: 仅向量检索)
ENABLE_HYBRID_SEARCH: bool = True

# --- 问题改写配置 ---

# 是否启用问题改写功能
ENABLE_QUERY_REWRITING: bool = True

# 问题改写数量: 将原问题改写成多少个相关问题
QUERY_REWRITE_COUNT: int = 3

# 问题改写时每个改写问题的检索数量
REWRITE_QUERY_TOP_K: int = 5

# 是否在最终结果中去重相似文档
ENABLE_DOCUMENT_DEDUPLICATION: bool = True

# --- 知识库管理配置 ---

# 是否启用智能文件监控和更新
ENABLE_FILE_MONITORING: bool = True

# 是否在同步时自动删除不存在的文件对应的文档
AUTO_DELETE_MISSING_FILES: bool = True

# 文档ID前缀，用于标识文档块的来源文件
DOCUMENT_ID_PREFIX: str = "doc_"
```

## `rag/hot_reload_manager.py`

```python
# rag/hot_reload_manager.py

import os
import time
import threading
from pathlib import Path
from typing import Dict, Set, Optional, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent

from .prompt_manager import prompt_manager
from . import config


class PromptFileHandler(FileSystemEventHandler):
    """提示词文件变化处理器"""
    
    def __init__(self, callback: Optional[Callable[[str, str], None]] = None):
        """
        初始化文件处理器
        
        Args:
            callback: 文件变化时的回调函数，参数为(event_type, prompt_name)
        """
        super().__init__()
        self.callback = callback
        self.last_modified: Dict[str, float] = {}
        self.debounce_time = config.HOT_RELOAD_DEBOUNCE_TIME  # 防抖时间（秒）
        
    def _should_process_event(self, file_path: str) -> bool:
        """
        判断是否应该处理该事件（防抖处理）
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否应该处理
        """
        current_time = time.time()
        last_time = self.last_modified.get(file_path, 0)
        
        if current_time - last_time < self.debounce_time:
            return False
        
        self.last_modified[file_path] = current_time
        return True
    
    def _get_prompt_name(self, file_path: str) -> Optional[str]:
        """
        从文件路径获取提示词名称
        
        Args:
            file_path: 文件路径
            
        Returns:
            提示词名称，如果不是提示词文件则返回None
        """
        path = Path(file_path)
        
        # 检查是否是提示词文件
        if (path.suffix == '.txt' and 
            'prompts' in str(path) and 
            path.parent.name == 'prompts'):
            return path.stem
        
        return None
    
    def on_modified(self, event):
        """文件修改事件处理"""
        if event.is_directory:
            return
        
        prompt_name = self._get_prompt_name(event.src_path)
        if not prompt_name:
            return
        
        if not self._should_process_event(event.src_path):
            return
        
        try:
            print(f"🔄 检测到提示词文件修改: {prompt_name}")
            
            # 清除所有相关缓存
            prompt_manager._prompt_cache.pop(prompt_name, None)
            prompt_manager._template_cache.pop(prompt_name, None)
            
            # 重新加载提示词（这会重新填充缓存）
            prompt_manager.load_prompt(prompt_name)
            print(f"✅ 自动重载完成: {prompt_name}")
            
            # 调用回调函数
            if self.callback:
                self.callback("modified", prompt_name)
                
        except Exception as e:
            print(f"❌ 自动重载失败 {prompt_name}: {e}")
    
    def on_created(self, event):
        """文件创建事件处理"""
        if event.is_directory:
            return
        
        prompt_name = self._get_prompt_name(event.src_path)
        if not prompt_name:
            return
        
        try:
            print(f"➕ 检测到新提示词文件: {prompt_name}")
            
            # 加载新提示词
            prompt_manager.load_prompt(prompt_name)
            print(f"✅ 自动加载完成: {prompt_name}")
            
            # 调用回调函数
            if self.callback:
                self.callback("created", prompt_name)
                
        except Exception as e:
            print(f"❌ 自动加载失败 {prompt_name}: {e}")
    
    def on_deleted(self, event):
        """文件删除事件处理"""
        if event.is_directory:
            return
        
        prompt_name = self._get_prompt_name(event.src_path)
        if not prompt_name:
            return
        
        try:
            print(f"🗑️ 检测到提示词文件删除: {prompt_name}")
            
            # 从缓存中移除
            prompt_manager._prompt_cache.pop(prompt_name, None)
            prompt_manager._template_cache.pop(prompt_name, None)
            print(f"✅ 缓存清理完成: {prompt_name}")
            
            # 调用回调函数
            if self.callback:
                self.callback("deleted", prompt_name)
                
        except Exception as e:
            print(f"❌ 缓存清理失败 {prompt_name}: {e}")


class HotReloadManager:
    """热重载管理器"""
    
    def __init__(self, enable_hot_reload: bool = True):
        """
        初始化热重载管理器
        
        Args:
            enable_hot_reload: 是否启用热重载功能
        """
        self.enable_hot_reload = enable_hot_reload
        self.observer: Optional[Observer] = None
        self.event_handler: Optional[PromptFileHandler] = None
        self.is_running = False
        self.callbacks: Set[Callable[[str, str], None]] = set()
        
        # 监控的目录
        self.watch_directory = prompt_manager.prompts_dir
        
        if self.enable_hot_reload:
            self._setup_file_watcher()
    
    def _setup_file_watcher(self):
        """设置文件监控器"""
        try:
            # 确保监控目录存在
            self.watch_directory.mkdir(exist_ok=True)
            
            # 创建事件处理器
            self.event_handler = PromptFileHandler(callback=self._on_file_change)
            
            # 创建观察者
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                str(self.watch_directory),
                recursive=False
            )
            
            print(f"🔍 热重载监控已设置，监控目录: {self.watch_directory}")
            
        except Exception as e:
            print(f"❌ 设置文件监控器失败: {e}")
            self.enable_hot_reload = False
    
    def _on_file_change(self, event_type: str, prompt_name: str):
        """文件变化回调处理"""
        # 通知所有注册的回调函数
        for callback in self.callbacks:
            try:
                callback(event_type, prompt_name)
            except Exception as e:
                print(f"❌ 回调函数执行失败: {e}")
    
    def start(self):
        """启动热重载监控"""
        if not self.enable_hot_reload:
            print("⚠️ 热重载功能未启用")
            return False
        
        if self.is_running:
            print("⚠️ 热重载监控已在运行中")
            return True
        
        # 如果observer已经停止，需要重新创建
        if self.observer and not self.observer.is_alive():
            self._setup_file_watcher()
        
        if not self.observer:
            print("❌ 文件监控器初始化失败")
            return False
        
        try:
            self.observer.start()
            self.is_running = True
            print(f"🔥 热重载监控已启动，正在监控: {self.watch_directory}")
            return True
            
        except Exception as e:
            print(f"❌ 启动热重载监控失败: {e}")
            # 尝试重新创建observer
            self._setup_file_watcher()
            if self.observer:
                try:
                    self.observer.start()
                    self.is_running = True
                    print(f"🔥 热重载监控已重新启动，正在监控: {self.watch_directory}")
                    return True
                except Exception as e2:
                    print(f"❌ 重新启动也失败: {e2}")
            return False
    
    def stop(self):
        """停止热重载监控"""
        if not self.observer or not self.is_running:
            return
        
        try:
            self.observer.stop()
            self.observer.join(timeout=5)  # 等待最多5秒
            self.is_running = False
            print("🛑 热重载监控已停止")
            
        except Exception as e:
            print(f"❌ 停止热重载监控失败: {e}")
    
    def add_callback(self, callback: Callable[[str, str], None]):
        """
        添加文件变化回调函数
        
        Args:
            callback: 回调函数，参数为(event_type, prompt_name)
        """
        self.callbacks.add(callback)
        print(f"📝 已添加热重载回调函数")
    
    def remove_callback(self, callback: Callable[[str, str], None]):
        """
        移除文件变化回调函数
        
        Args:
            callback: 要移除的回调函数
        """
        self.callbacks.discard(callback)
        print(f"🗑️ 已移除热重载回调函数")
    
    def get_status(self) -> Dict[str, any]:
        """
        获取热重载状态信息
        
        Returns:
            状态信息字典
        """
        return {
            "enabled": self.enable_hot_reload,
            "running": self.is_running,
            "watch_directory": str(self.watch_directory),
            "callbacks_count": len(self.callbacks),
            "observer_alive": self.observer.is_alive() if self.observer else False
        }
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()


# 检查是否安装了watchdog库
try:
    import watchdog
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("⚠️ 未安装watchdog库，热重载功能不可用")
    print("   安装命令: uv add watchdog")


# 创建全局热重载管理器实例
hot_reload_manager = HotReloadManager(
    enable_hot_reload=WATCHDOG_AVAILABLE and getattr(config, 'ENABLE_HOT_RELOAD', True)
) if WATCHDOG_AVAILABLE else None


def enable_hot_reload():
    """启用热重载功能"""
    if not WATCHDOG_AVAILABLE:
        print("❌ watchdog库未安装，无法启用热重载功能")
        print("   安装命令: uv add watchdog")
        return False
    
    if hot_reload_manager:
        return hot_reload_manager.start()
    return False


def disable_hot_reload():
    """禁用热重载功能"""
    if hot_reload_manager:
        hot_reload_manager.stop()


def is_hot_reload_enabled() -> bool:
    """检查热重载是否启用"""
    return (hot_reload_manager is not None and 
            hot_reload_manager.is_running if hot_reload_manager else False)


def get_hot_reload_status() -> Dict[str, any]:
    """获取热重载状态"""
    if hot_reload_manager:
        return hot_reload_manager.get_status()
    else:
        return {
            "enabled": False,
            "running": False,
            "error": "watchdog库未安装" if not WATCHDOG_AVAILABLE else "热重载管理器未初始化"
        }
```

## `rag/memory_manager.py`

```python
# rag/memory_manager.py

import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import json

from . import config


@dataclass
class ConversationTurn:
    """单轮对话记录"""
    question: str
    answer: str
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.metadata is None:
            self.metadata = {}
        
        # 计算字符长度
        self.char_length = len(self.question) + len(self.answer)
        
        # 截断过长的内容
        if self.char_length > config.SINGLE_CONVERSATION_MAX_LENGTH:
            max_q_len = config.SINGLE_CONVERSATION_MAX_LENGTH // 2
            max_a_len = config.SINGLE_CONVERSATION_MAX_LENGTH - max_q_len
            
            if len(self.question) > max_q_len:
                self.question = self.question[:max_q_len-3] + "..."
            
            if len(self.answer) > max_a_len:
                self.answer = self.answer[:max_a_len-3] + "..."
            
            # 重新计算长度
            self.char_length = len(self.question) + len(self.answer)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationTurn':
        """从字典创建对象"""
        return cls(**data)
    
    def get_formatted_time(self) -> str:
        """获取格式化的时间字符串"""
        return datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S")


class ShortTermMemoryManager:
    """短期记忆管理器"""
    
    def __init__(self):
        """初始化记忆管理器"""
        self.conversations: List[ConversationTurn] = []
        self.total_char_length = 0
        self.max_length = config.SHORT_TERM_MEMORY_MAX_LENGTH
        self.min_rounds = config.MIN_CONVERSATION_ROUNDS
        self.cleanup_strategy = config.MEMORY_CLEANUP_STRATEGY
        self.sliding_window_size = config.SLIDING_WINDOW_SIZE
        
        print(f"短期记忆管理器已初始化 (最大长度: {self.max_length:,} 字符)")
    
    def add_conversation(self, question: str, answer: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        添加一轮对话到记忆中
        
        Args:
            question: 用户问题
            answer: AI回答
            metadata: 额外的元数据
        """
        if not config.ENABLE_SHORT_TERM_MEMORY:
            return
        
        # 创建对话记录
        conversation = ConversationTurn(
            question=question,
            answer=answer,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        
        # 添加到列表
        self.conversations.append(conversation)
        self.total_char_length += conversation.char_length
        
        print(f"📝 添加对话记录 (长度: {conversation.char_length} 字符, 总长度: {self.total_char_length:,} 字符)")
        
        # 检查是否需要清理
        self._cleanup_if_needed()
    
    def _cleanup_if_needed(self) -> None:
        """根据策略清理记忆"""
        if self.total_char_length <= self.max_length:
            return
        
        if self.cleanup_strategy == "auto":
            self._auto_cleanup()
        elif self.cleanup_strategy == "sliding_window":
            self._sliding_window_cleanup()
        # manual策略不自动清理
    
    def _auto_cleanup(self) -> None:
        """
        自动清理策略：严格控制总长度不超过max_length
        优先级：长度限制 > 轮数保留
        如果单轮对话超长，会截取该轮对话的内容
        """
        removed_count = 0
        truncated_count = 0
        
        # 第一阶段：移除整轮对话直到满足长度要求或只剩一轮
        while (self.total_char_length > self.max_length and len(self.conversations) > 1):
            removed_conversation = self.conversations.pop(0)
            self.total_char_length -= removed_conversation.char_length
            removed_count += 1
        
        # 第二阶段：如果还是超长且只剩一轮对话，截取该轮对话
        if self.total_char_length > self.max_length and len(self.conversations) == 1:
            last_conversation = self.conversations[0]
            
            # 计算需要截取多少字符
            excess_chars = self.total_char_length - self.max_length
            target_length = last_conversation.char_length - excess_chars
            
            if target_length > 0:
                # 按比例截取问题和答案
                total_original_length = len(last_conversation.question) + len(last_conversation.answer)
                question_ratio = len(last_conversation.question) / total_original_length
                answer_ratio = len(last_conversation.answer) / total_original_length
                
                target_question_length = int(target_length * question_ratio)
                target_answer_length = target_length - target_question_length
                
                # 截取问题和答案
                if target_question_length > 3:  # 保留至少3个字符用于"..."
                    truncated_question = last_conversation.question[:target_question_length-3] + "..."
                else:
                    truncated_question = "..."
                
                if target_answer_length > 3:  # 保留至少3个字符用于"..."
                    truncated_answer = last_conversation.answer[:target_answer_length-3] + "..."
                else:
                    truncated_answer = "..."
                
                # 更新对话内容
                old_length = last_conversation.char_length
                last_conversation.question = truncated_question
                last_conversation.answer = truncated_answer
                last_conversation.char_length = len(truncated_question) + len(truncated_answer)
                
                # 更新总长度
                self.total_char_length = self.total_char_length - old_length + last_conversation.char_length
                truncated_count = 1
                
                print(f"⚠️  最后一轮对话过长，已截取 {old_length - last_conversation.char_length} 字符")
            else:
                # 如果目标长度太小，直接清空该轮对话
                self.conversations.clear()
                self.total_char_length = 0
                removed_count += 1
                print(f"⚠️  单轮对话超出限制太多，已清空所有记忆")
        
        # 第三阶段：如果还有多轮对话但仍超长，继续移除（理论上不应该发生）
        while self.total_char_length > self.max_length and len(self.conversations) > 0:
            removed_conversation = self.conversations.pop(0)
            self.total_char_length -= removed_conversation.char_length
            removed_count += 1
        
        # 输出清理结果
        if removed_count > 0 or truncated_count > 0:
            messages = []
            if removed_count > 0:
                messages.append(f"移除了 {removed_count} 轮旧对话")
            if truncated_count > 0:
                messages.append(f"截取了 {truncated_count} 轮对话内容")
            
            print(f"🧹 自动清理完成：{', '.join(messages)} (当前总长度: {self.total_char_length:,} 字符)")
        
        # 最终验证：确保绝对不超过限制
        if self.total_char_length > self.max_length:
            print(f"❌ 警告：清理后仍超出限制 ({self.total_char_length:,} > {self.max_length:,})")
            # 紧急处理：直接清空
            self.conversations.clear()
            self.total_char_length = 0
            print(f"🚨 紧急清空所有记忆以避免超出限制")
    
    def _sliding_window_cleanup(self) -> None:
        """滑动窗口清理策略：保持固定数量的对话"""
        if len(self.conversations) <= self.sliding_window_size:
            return
        
        # 计算需要移除的对话数量
        excess_count = len(self.conversations) - self.sliding_window_size
        
        # 移除最旧的对话
        for _ in range(excess_count):
            removed_conversation = self.conversations.pop(0)
            self.total_char_length -= removed_conversation.char_length
        
        print(f"🪟 滑动窗口清理了 {excess_count} 轮旧对话 (保留最近 {self.sliding_window_size} 轮)")
    
    def get_recent_conversations(self, count: Optional[int] = None) -> List[ConversationTurn]:
        """
        获取最近的对话记录
        
        Args:
            count: 获取的对话轮数，None表示获取所有
            
        Returns:
            对话记录列表
        """
        if count is None:
            return self.conversations.copy()
        
        return self.conversations[-count:] if count > 0 else []
    
    def get_conversation_context(self, include_count: Optional[int] = None) -> str:
        """
        获取对话上下文字符串，用于提供给LLM
        
        Args:
            include_count: 包含的对话轮数，None表示包含所有
            
        Returns:
            格式化的对话上下文
        """
        conversations = self.get_recent_conversations(include_count)
        
        if not conversations:
            return ""
        
        context_parts = []
        for i, conv in enumerate(conversations, 1):
            context_parts.append(f"第{i}轮对话:")
            context_parts.append(f"用户: {conv.question}")
            context_parts.append(f"助手: {conv.answer}")
            context_parts.append("")  # 空行分隔
        
        return "\n".join(context_parts).strip()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        获取记忆统计信息
        
        Returns:
            统计信息字典
        """
        if not self.conversations:
            return {
                "total_conversations": 0,
                "total_char_length": 0,
                "memory_usage_percent": 0.0,
                "oldest_conversation": None,
                "newest_conversation": None,
                "average_conversation_length": 0
            }
        
        return {
            "total_conversations": len(self.conversations),
            "total_char_length": self.total_char_length,
            "memory_usage_percent": (self.total_char_length / self.max_length) * 100,
            "oldest_conversation": self.conversations[0].get_formatted_time(),
            "newest_conversation": self.conversations[-1].get_formatted_time(),
            "average_conversation_length": self.total_char_length // len(self.conversations)
        }
    
    def clear_memory(self) -> int:
        """
        清空所有记忆
        
        Returns:
            清除的对话轮数
        """
        cleared_count = len(self.conversations)
        self.conversations.clear()
        self.total_char_length = 0
        
        print(f"🗑️ 已清空所有记忆 (清除了 {cleared_count} 轮对话)")
        return cleared_count
    
    def remove_old_conversations(self, keep_count: int) -> int:
        """
        手动移除旧对话，保留指定数量的最新对话
        
        Args:
            keep_count: 保留的对话轮数
            
        Returns:
            移除的对话轮数
        """
        if keep_count >= len(self.conversations):
            return 0
        
        # 计算需要移除的数量
        remove_count = len(self.conversations) - keep_count
        
        # 移除最旧的对话
        removed_conversations = self.conversations[:remove_count]
        self.conversations = self.conversations[remove_count:]
        
        # 更新总长度
        removed_length = sum(conv.char_length for conv in removed_conversations)
        self.total_char_length -= removed_length
        
        print(f"🧹 手动移除了 {remove_count} 轮旧对话 (当前总长度: {self.total_char_length:,} 字符)")
        return remove_count
    
    def search_conversations(self, keyword: str, limit: int = 10) -> List[Tuple[int, ConversationTurn]]:
        """
        在对话历史中搜索关键词
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制
            
        Returns:
            匹配的对话记录列表，包含索引和对话对象
        """
        results = []
        keyword_lower = keyword.lower()
        
        for i, conv in enumerate(self.conversations):
            if (keyword_lower in conv.question.lower() or 
                keyword_lower in conv.answer.lower()):
                results.append((i, conv))
                
                if len(results) >= limit:
                    break
        
        return results
    
    def export_conversations(self, file_path: str) -> bool:
        """
        导出对话记录到JSON文件
        
        Args:
            file_path: 导出文件路径
            
        Returns:
            导出是否成功
        """
        try:
            export_data = {
                "export_time": datetime.now().isoformat(),
                "total_conversations": len(self.conversations),
                "total_char_length": self.total_char_length,
                "conversations": [conv.to_dict() for conv in self.conversations]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"📤 对话记录已导出到: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 导出对话记录失败: {e}")
            return False
    
    def import_conversations(self, file_path: str, append: bool = False) -> bool:
        """
        从JSON文件导入对话记录
        
        Args:
            file_path: 导入文件路径
            append: 是否追加到现有记录（False表示替换）
            
        Returns:
            导入是否成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_conversations = [
                ConversationTurn.from_dict(conv_data) 
                for conv_data in import_data['conversations']
            ]
            
            if not append:
                self.clear_memory()
            
            # 添加导入的对话
            for conv in imported_conversations:
                self.conversations.append(conv)
                self.total_char_length += conv.char_length
            
            # 清理如果需要
            self._cleanup_if_needed()
            
            print(f"📥 已导入 {len(imported_conversations)} 轮对话记录")
            return True
            
        except Exception as e:
            print(f"❌ 导入对话记录失败: {e}")
            return False


# 创建全局记忆管理器实例
memory_manager = ShortTermMemoryManager()
```

## `rag/pipeline.py`

```python
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
# 导入短期记忆管理器
from .memory_manager import memory_manager


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
        api_key = os.getenv("CLOUD_INFINI_API_KEY")
        base_url = os.getenv("CLOUD_BASE_URL")
        model_name = os.getenv("CLOUD_MODEL_NAME")
        # api_key = os.getenv("DeepSeek_api_key")
        # base_url = os.getenv("DeepSeek_base_url")
        # model_name = os.getenv("DeepSeek_model_name")
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

    def ask_with_categories(self, question: str, categories: List[str] = None, use_memory: bool = True) -> Dict[str, Any]:
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
        
        # 获取短期记忆上下文
        memory_context = ""
        if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
            memory_context = memory_manager.get_conversation_context(include_count=None)  # 使用所有对话轮次
            if memory_context:
                print("--- 短期记忆上下文 ---")
                print(f"包含 {len(memory_manager.get_recent_conversations())} 轮对话作为上下文")
        
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
                
                # 构建完整的上下文（包含记忆上下文和检索上下文）
                full_context = context
                if memory_context:
                    full_context = f"对话历史:\n{memory_context}\n\n当前检索到的相关信息:\n{context}"
                
                # 使用提示词管理器获取问答提示模板
                qa_template = get_qa_prompt_template()
                prompt = qa_template.format(context=full_context, question=question)
                response = self.llm.invoke(prompt)
                
                if hasattr(response, 'content'):
                    answer = response.content.strip()
                else:
                    answer = str(response).strip()
                
                # 保存对话到短期记忆
                if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
                    memory_manager.add_conversation(
                        question=question,
                        answer=answer,
                        metadata={
                            "used_query_rewriting": True,
                            "used_categories": categories,
                            "memory_context_included": bool(memory_context),
                            "source_documents_count": len(final_docs)
                        }
                    )
                
                return {
                    "result": answer,
                    "source_documents": final_docs
                }
            else:
                no_result_answer = "根据提供的资料，我无法回答该问题。"
                
                # 保存对话到短期记忆
                if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
                    memory_manager.add_conversation(
                        question=question,
                        answer=no_result_answer,
                        metadata={
                            "used_query_rewriting": True,
                            "used_categories": categories,
                            "memory_context_included": bool(memory_context),
                            "source_documents_count": 0,
                            "no_result": True
                        }
                    )
                
                return {
                    "result": no_result_answer,
                    "source_documents": []
                }
        else:
            # 使用分类检索的问答链，但需要手动处理记忆上下文
            if categories:
                print("--- 分类检索模式 ---")
                
                # 创建临时的分类检索器
                category_retriever = self._build_category_retriever(categories)
                compression_retriever = ContextualCompressionRetriever(
                    base_compressor=self.reranker,
                    base_retriever=category_retriever
                )
                
                # 获取相关文档
                retrieved_docs = compression_retriever.get_relevant_documents(question)
                
                if retrieved_docs:
                    # 构建上下文
                    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
                    
                    # 构建完整的上下文（包含记忆上下文和检索上下文）
                    full_context = context
                    if memory_context:
                        full_context = f"对话历史:\n{memory_context}\n\n当前检索到的相关信息:\n{context}"
                    
                    # 使用提示词管理器获取问答提示模板
                    qa_template = get_qa_prompt_template()
                    prompt = qa_template.format(context=full_context, question=question)
                    response = self.llm.invoke(prompt)
                    
                    if hasattr(response, 'content'):
                        answer = response.content.strip()
                    else:
                        answer = str(response).strip()
                    
                    result = {
                        "result": answer,
                        "source_documents": retrieved_docs
                    }
                else:
                    no_result_answer = "根据提供的资料，我无法回答该问题。"
                    result = {
                        "result": no_result_answer,
                        "source_documents": []
                    }
                
                # 保存对话到短期记忆
                if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
                    memory_manager.add_conversation(
                        question=question,
                        answer=result.get("result", ""),
                        metadata={
                            "used_query_rewriting": False,
                            "used_categories": categories,
                            "memory_context_included": bool(memory_context),
                            "source_documents_count": len(result.get("source_documents", []))
                        }
                    )
                
                return result
            else:
                # 使用原始的问答链，但需要手动处理记忆上下文
                print("--- 原始问答链模式 (ask_with_categories) ---")
                
                # 先获取相关文档
                retriever = self.qa_chain.retriever
                retrieved_docs = retriever.get_relevant_documents(question)
                
                if retrieved_docs:
                    # 构建上下文
                    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
                    
                    # 构建完整的上下文（包含记忆上下文和检索上下文）
                    full_context = context
                    if memory_context:
                        full_context = f"对话历史:\n{memory_context}\n\n当前检索到的相关信息:\n{context}"
                    
                    # 使用提示词管理器获取问答提示模板
                    qa_template = get_qa_prompt_template()
                    prompt = qa_template.format(context=full_context, question=question)
                    response = self.llm.invoke(prompt)
                    
                    if hasattr(response, 'content'):
                        answer = response.content.strip()
                    else:
                        answer = str(response).strip()
                    
                    result = {
                        "result": answer,
                        "source_documents": retrieved_docs
                    }
                else:
                    no_result_answer = "根据提供的资料，我无法回答该问题。"
                    result = {
                        "result": no_result_answer,
                        "source_documents": []
                    }
                
                # 保存对话到短期记忆
                if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
                    memory_manager.add_conversation(
                        question=question,
                        answer=result.get("result", ""),
                        metadata={
                            "used_query_rewriting": False,
                            "used_categories": None,
                            "memory_context_included": bool(memory_context),
                            "source_documents_count": len(result.get("source_documents", []))
                        }
                    )
                
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

    def ask(self, question: str, use_memory: bool = True) -> Dict[str, Any]:
        """
        对已加载的文档提出问题，并获取答案。
        支持问题改写功能和短期记忆功能，提高搜索覆盖面。

        Args:
            question: 用户提出的问题字符串。
            use_memory: 是否使用短期记忆功能

        Returns:
            一个字典，包含'result' (答案) 和 'source_documents' (参考的文档片段)。
        """
        if not self.qa_chain:
            error_msg = "错误: 问答链尚未初始化。请先调用 `sync_data_directory` 方法加载文档。"
            return {
                "result": error_msg,
                "source_documents": []
            }
        
        print(f"\n正在处理问题: '{question}'...")
        
        # 获取短期记忆上下文
        memory_context = ""
        if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
            memory_context = memory_manager.get_conversation_context(include_count=None)  # 使用所有对话轮次
            if memory_context:
                print("--- 短期记忆上下文 ---")
                print(f"包含最近 {len(memory_manager.get_recent_conversations(5))} 轮对话作为上下文")
        
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
                
                # 构建完整的上下文（包含记忆上下文和检索上下文）
                full_context = context
                if memory_context:
                    full_context = f"对话历史:\n{memory_context}\n\n当前检索到的相关信息:\n{context}"
                
                # 使用提示词管理器获取问答提示模板
                qa_template = get_qa_prompt_template()
                prompt = qa_template.format(context=full_context, question=question)
                response = self.llm.invoke(prompt)
                
                if hasattr(response, 'content'):
                    answer = response.content.strip()
                else:
                    answer = str(response).strip()
                
                # 保存对话到短期记忆
                if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
                    memory_manager.add_conversation(
                        question=question,
                        answer=answer,
                        metadata={
                            "used_query_rewriting": True,
                            "memory_context_included": bool(memory_context),
                            "source_documents_count": len(final_docs)
                        }
                    )
                
                return {
                    "result": answer,
                    "source_documents": final_docs
                }
            else:
                no_result_answer = "根据提供的资料，我无法回答该问题。"
                
                # 保存对话到短期记忆
                if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
                    memory_manager.add_conversation(
                        question=question,
                        answer=no_result_answer,
                        metadata={
                            "used_query_rewriting": True,
                            "memory_context_included": bool(memory_context),
                            "source_documents_count": 0,
                            "no_result": True
                        }
                    )
                
                return {
                    "result": no_result_answer,
                    "source_documents": []
                }
        else:
            # 使用原始的问答链，但需要手动处理记忆上下文
            print("--- 原始问答链模式 ---")
            
            # 先获取相关文档
            retriever = self.qa_chain.retriever
            retrieved_docs = retriever.get_relevant_documents(question)
            
            if retrieved_docs:
                # 构建上下文
                context = "\n\n".join([doc.page_content for doc in retrieved_docs])
                
                # 构建完整的上下文（包含记忆上下文和检索上下文）
                full_context = context
                if memory_context:
                    full_context = f"对话历史:\n{memory_context}\n\n当前检索到的相关信息:\n{context}"
                
                # 使用提示词管理器获取问答提示模板
                qa_template = get_qa_prompt_template()
                prompt = qa_template.format(context=full_context, question=question)
                response = self.llm.invoke(prompt)
                
                if hasattr(response, 'content'):
                    answer = response.content.strip()
                else:
                    answer = str(response).strip()
                
                result = {
                    "result": answer,
                    "source_documents": retrieved_docs
                }
            else:
                no_result_answer = "根据提供的资料，我无法回答该问题。"
                result = {
                    "result": no_result_answer,
                    "source_documents": []
                }
            
            # 保存对话到短期记忆
            if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
                memory_manager.add_conversation(
                    question=question,
                    answer=result.get("result", ""),
                    metadata={
                        "used_query_rewriting": False,
                        "memory_context_included": bool(memory_context),
                        "source_documents_count": len(result.get("source_documents", []))
                    }
                )
            
            return result

```

## `rag/prompt_manager.py`

```python
# rag/prompt_manager.py

import os
from pathlib import Path
from typing import Dict, Optional, Any
from langchain_core.prompts import PromptTemplate


class PromptManager:
    """
    提示词管理器，负责加载和管理所有提示词模板。
    实现提示词与代码的解耦。
    """
    
    def __init__(self):
        """初始化提示词管理器。"""
        self.prompts_dir = Path(__file__).parent / "prompts"
        self._prompt_cache: Dict[str, str] = {}
        self._template_cache: Dict[str, PromptTemplate] = {}
        
        # 确保提示词目录存在
        self.prompts_dir.mkdir(exist_ok=True)
    
    def load_prompt(self, prompt_name: str) -> str:
        """
        加载指定的提示词内容。
        
        Args:
            prompt_name: 提示词文件名（不含扩展名）
            
        Returns:
            提示词内容字符串
            
        Raises:
            FileNotFoundError: 如果提示词文件不存在
        """
        # 检查缓存
        if prompt_name in self._prompt_cache:
            return self._prompt_cache[prompt_name]
        
        # 构建文件路径
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"提示词文件不存在: {prompt_file}")
        
        # 读取文件内容
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 缓存内容
            self._prompt_cache[prompt_name] = content
            return content
            
        except Exception as e:
            raise RuntimeError(f"读取提示词文件失败 {prompt_file}: {e}")
    
    def get_template(self, prompt_name: str) -> PromptTemplate:
        """
        获取指定的提示词模板对象。
        
        Args:
            prompt_name: 提示词文件名（不含扩展名）
            
        Returns:
            LangChain PromptTemplate 对象
        """
        # 检查缓存
        if prompt_name in self._template_cache:
            return self._template_cache[prompt_name]
        
        # 加载提示词内容
        prompt_content = self.load_prompt(prompt_name)
        
        # 创建模板对象
        template = PromptTemplate.from_template(prompt_content)
        
        # 缓存模板
        self._template_cache[prompt_name] = template
        return template
    
    def reload_prompt(self, prompt_name: str) -> str:
        """
        重新加载指定的提示词（清除缓存后重新读取）。
        
        Args:
            prompt_name: 提示词文件名（不含扩展名）
            
        Returns:
            提示词内容字符串
        """
        # 清除缓存
        self._prompt_cache.pop(prompt_name, None)
        self._template_cache.pop(prompt_name, None)
        
        # 重新加载
        return self.load_prompt(prompt_name)
    
    def list_available_prompts(self) -> list:
        """
        列出所有可用的提示词文件。
        
        Returns:
            提示词文件名列表（不含扩展名）
        """
        prompt_files = []
        # 使用 pathlib.Path.glob() 方法 (推荐)
        for file_path in self.prompts_dir.glob("*.txt"):
            prompt_files.append(file_path.stem)  # .stem 获取不含扩展名的文件名
        return sorted(prompt_files)
        
        # 如果使用标准库 glob 的等价写法：
        # import glob
        # pattern = str(self.prompts_dir / "*.txt")
        # for file_path in glob.glob(pattern):
        #     filename = os.path.splitext(os.path.basename(file_path))[0]
        #     prompt_files.append(filename)
    
    def save_prompt(self, prompt_name: str, content: str) -> None:
        """
        保存提示词到文件。
        
        Args:
            prompt_name: 提示词文件名（不含扩展名）
            content: 提示词内容
        """
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        
        try:
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            
            # 清除缓存，确保下次加载时使用新内容
            self._prompt_cache.pop(prompt_name, None)
            self._template_cache.pop(prompt_name, None)
            
            print(f"提示词已保存到: {prompt_file}")
            
        except Exception as e:
            raise RuntimeError(f"保存提示词文件失败 {prompt_file}: {e}")
    
    def clear_cache(self) -> None:
        """清除所有缓存。"""
        self._prompt_cache.clear()
        self._template_cache.clear()
        print("提示词缓存已清除")
    
    def reload_all_prompts(self) -> Dict[str, str]:
        """
        重新加载所有提示词。
        
        Returns:
            重新加载的提示词字典
        """
        # 清除所有缓存
        self.clear_cache()
        
        # 重新加载所有提示词
        reloaded_prompts = {}
        for prompt_name in self.list_available_prompts():
            try:
                content = self.load_prompt(prompt_name)
                reloaded_prompts[prompt_name] = content
                print(f"✅ 重新加载: {prompt_name}")
            except Exception as e:
                print(f"❌ 重新加载失败 {prompt_name}: {e}")
        
        return reloaded_prompts
    
    def get_prompt_info(self, prompt_name: str) -> Dict[str, Any]:
        """
        获取提示词的详细信息。
        
        Args:
            prompt_name: 提示词文件名（不含扩展名）
            
        Returns:
            提示词信息字典
        """
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        
        if not prompt_file.exists():
            return {"exists": False, "error": f"提示词文件不存在: {prompt_file}"}
        
        try:
            stat = prompt_file.stat()
            content = self.load_prompt(prompt_name)
            template = self.get_template(prompt_name)
            
            return {
                "exists": True,
                "file_path": str(prompt_file),
                "file_size": stat.st_size,
                "modified_time": stat.st_mtime,
                "content_length": len(content),
                "content_preview": content[:100] + "..." if len(content) > 100 else content,
                "template_variables": template.input_variables,
                "is_cached": prompt_name in self._prompt_cache
            }
        except Exception as e:
            return {"exists": True, "error": f"获取提示词信息失败: {e}"}
    
    def validate_prompt(self, prompt_name: str) -> Dict[str, Any]:
        """
        验证提示词模板的有效性。
        
        Args:
            prompt_name: 提示词文件名（不含扩展名）
            
        Returns:
            验证结果字典
        """
        try:
            template = self.get_template(prompt_name)
            
            # 检查必需的变量
            required_vars = {"context", "question"}  # 问答提示词的必需变量
            missing_vars = required_vars - set(template.input_variables)
            extra_vars = set(template.input_variables) - required_vars
            
            # 尝试格式化测试
            test_values = {var: f"test_{var}" for var in template.input_variables}
            try:
                formatted = template.format(**test_values)
                format_test = {"success": True, "formatted_length": len(formatted)}
            except Exception as e:
                format_test = {"success": False, "error": str(e)}
            
            return {
                "valid": len(missing_vars) == 0 and format_test["success"],
                "template_variables": template.input_variables,
                "missing_variables": list(missing_vars),
                "extra_variables": list(extra_vars),
                "format_test": format_test
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"验证提示词失败: {e}"
            }


# 创建全局提示词管理器实例
prompt_manager = PromptManager()


def get_qa_prompt_template() -> PromptTemplate:
    """获取问答提示词模板。"""
    return prompt_manager.get_template("qa_prompt")


def get_query_rewrite_prompt_template() -> PromptTemplate:
    """获取问题改写提示词模板。"""
    return prompt_manager.get_template("query_rewrite_prompt")


def load_qa_prompt() -> str:
    """加载问答提示词内容。"""
    return prompt_manager.load_prompt("qa_prompt")


def load_query_rewrite_prompt() -> str:
    """加载问题改写提示词内容。"""
    return prompt_manager.load_prompt("query_rewrite_prompt")
```

## `rag/prompts/prompt_README.md`

```markdown
# 提示词管理系统

本目录包含了RAG系统中使用的所有提示词模板，实现了提示词与代码的解耦。

## 文件结构

```
prompts/
├── README.md                 # 本说明文件
├── qa_prompt.txt            # 问答提示词模板
└── query_rewrite_prompt.txt # 问题改写提示词模板
```

## 提示词文件说明

### qa_prompt.txt
用于指导LLM如何基于检索到的上下文回答用户问题。

**变量:**
- `{context}`: 检索到的相关文档内容
- `{question}`: 用户提出的问题

### query_rewrite_prompt.txt
用于指导LLM如何将用户的原始问题改写成多个相关问题，以提高检索覆盖面。

**变量:**
- `{original_query}`: 用户的原始问题
- `{count}`: 需要生成的改写问题数量

## 使用方法

### 在代码中使用提示词管理器

```python
from rag.prompt_manager import (
    get_qa_prompt_template,
    get_query_rewrite_prompt_template,
    load_qa_prompt,
    load_query_rewrite_prompt
)

# 获取提示词模板对象
qa_template = get_qa_prompt_template()
rewrite_template = get_query_rewrite_prompt_template()

# 格式化提示词
formatted_prompt = qa_template.format(
    context="相关文档内容",
    question="用户问题"
)

# 直接加载提示词内容
qa_prompt_content = load_qa_prompt()
```

### 修改提示词

1. 直接编辑对应的 `.txt` 文件
2. 保存文件后，系统会自动使用新的提示词内容
3. 如果需要立即生效，可以调用 `prompt_manager.reload_prompt(prompt_name)`

### 添加新的提示词

1. 在 `prompts/` 目录下创建新的 `.txt` 文件
2. 在 `prompt_manager.py` 中添加对应的辅助函数
3. 在需要使用的地方导入并使用

## 优势

1. **解耦性**: 提示词与代码分离，便于维护和修改
2. **可维护性**: 集中管理所有提示词，便于版本控制和协作
3. **性能优化**: 内置缓存机制，避免重复读取文件
4. **灵活性**: 支持动态重新加载，便于调试和优化
5. **一致性**: 统一的接口和使用方式

## 最佳实践

1. **命名规范**: 使用描述性的文件名，如 `qa_prompt.txt`、`summary_prompt.txt`
2. **变量标记**: 使用 `{variable_name}` 格式标记模板变量
3. **文档注释**: 在提示词文件开头添加注释说明用途和变量
4. **版本控制**: 将提示词文件纳入版本控制，跟踪变更历史
5. **测试验证**: 修改提示词后进行充分测试，确保效果符合预期

## 示例

### 创建新的提示词文件

```bash
# 创建摘要提示词文件
echo "请对以下内容进行简洁的摘要：

{content}

摘要：" > prompts/summary_prompt.txt
```

### 在代码中使用新提示词

```python
# 在 prompt_manager.py 中添加
def get_summary_prompt_template():
    return prompt_manager.get_template("summary_prompt")

# 在业务代码中使用
from rag.prompt_manager import get_summary_prompt_template

summary_template = get_summary_prompt_template()
formatted_prompt = summary_template.format(content="要摘要的内容")
```
```

## `rag/prompts/qa_prompt.txt`

```
请你扮演一个严谨的文档问答机器人。
请严格根据下面提供的"上下文信息"来回答"问题"。在答案前加上"根据知识库资料："
如果上下文中没有足够的信息来回答问题，请直接说："根据提供的资料，我无法回答该问题。"
不允许编造或添加上下文之外的任何信息。

---
上下文信息:
{context}
---

问题: {question}

回答:
```

## `rag/prompts/query_rewrite_prompt.txt`

```
你是一个专业的问题改写助手。请将用户的问题改写成{count}个不同角度但相关的问题，以提高信息检索的覆盖面。

要求：
1. 保持问题的核心意图不变
2. 从不同角度或层面来表达同一个需求
3. 使用不同的关键词和表达方式
4. 每个问题都应该是完整、清晰的
5. 问题之间要有一定的差异性

原始问题：{original_query}

请生成{count}个改写问题，每行一个问题，不要添加编号或其他格式：
```

## `rag/streaming_pipeline.py`

```python
# rag/streaming_pipeline_v2.py - 正确的流式响应实现

import asyncio
import time
from typing import AsyncGenerator, Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# 继承异步RAG流程
from .async_pipeline import AsyncRagPipeline
from . import config
# 导入提示词管理器
from .prompt_manager import get_qa_prompt_template, get_query_rewrite_prompt_template
# 导入短期记忆管理器
from .memory_manager import memory_manager

# 导入需要的组件
from langchain_core.documents import Document


class StreamEventType(Enum):
    """流式事件类型（简化版）"""
    PROCESSING = "processing"           # 处理状态更新
    GENERATION_START = "generation_start"  # 开始生成答案
    GENERATION_CHUNK = "generation_chunk"  # 答案片段
    GENERATION_END = "generation_end"      # 生成完成
    ERROR = "error"                        # 错误
    COMPLETE = "complete"                  # 完成


@dataclass
class StreamEvent:
    """流式事件数据结构"""
    type: StreamEventType
    data: Any
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp,
            "metadata": self.metadata or {}
        }


class StreamingRagPipeline(AsyncRagPipeline):
    """
    正确的流式响应RAG系统
    - 中间处理过程不流式，只做状态通知
    - 只有最终答案生成是真正的流式输出
    """
    
    def __init__(self):
        print("正在初始化流式RAG系统...")
        super().__init__()
        print("流式RAG系统初始化完成。")
    
    async def ask_stream(self, question: str, use_memory: bool = True) -> AsyncGenerator[StreamEvent, None]:
        """
        流式问答 - 只有答案生成是流式的，支持短期记忆功能
        
        Args:
            question: 用户问题
            use_memory: 是否使用短期记忆功能
            
        Yields:
            StreamEvent: 流式事件
        """
        if not self.qa_chain:
            yield StreamEvent(
                type=StreamEventType.ERROR,
                data={"error": "问答链尚未初始化"},
                timestamp=time.time()
            )
            return
        
        try:
            # 1. 处理阶段 - 内部处理，只发送状态更新
            yield StreamEvent(
                type=StreamEventType.PROCESSING,
                data={"message": "正在处理您的问题..."},
                timestamp=time.time()
            )
            
            # 内部处理：问题改写、检索、重排序（非流式）
            if config.ENABLE_QUERY_REWRITING:
                # 问题改写
                rewritten_queries = await self._rewrite_query_async(question)
                
                # 检索
                retrieved_docs = await self._retrieve_with_multiple_queries_async(rewritten_queries)
                
                # 重排序
                if retrieved_docs and self.reranker:
                    try:
                        reranked_docs = await self._run_in_executor(
                            self.reranker.compress_documents, retrieved_docs, question
                        )
                        final_docs = reranked_docs[:config.RERANKER_TOP_N]
                    except Exception:
                        final_docs = retrieved_docs[:config.RERANKER_TOP_N]
                else:
                    final_docs = retrieved_docs[:config.RERANKER_TOP_N]
            else:
                # ✅ 使用异步检索功能，避免调用LLM
                retriever = self.qa_chain.retriever
                
                # 使用异步检索方法
                if hasattr(retriever, 'ainvoke'):
                    final_docs = await retriever.ainvoke(question)
                elif hasattr(retriever, 'aget_relevant_documents'):
                    final_docs = await retriever.aget_relevant_documents(question)
                else:
                    # 如果没有异步方法，回退到线程池
                    final_docs = await self._run_in_executor(
                        retriever.get_relevant_documents, question
                    )
                
                # 使用真正的流式生成（LLM只被调用一次，且是流式的）
                # if final_docs:
                #     async for event in self._generate_streaming_answer(question, final_docs):
                #         yield event
                # else:
                #     async for event in self._stream_existing_answer("根据提供的资料，我无法找到相关信息来回答该问题。"):
                #         yield event

                # yield StreamEvent(
                #         type=StreamEventType.COMPLETE,
                #         data={"message": "回答完成"},
                #         timestamp=time.time()
                #     )
                # return
            
            # 2. 流式生成阶段 - 这里才是真正的流式
            if final_docs:
                # 先尝试基于文档生成答案
                knowledge_base_answer = ""
                answer_events = []
                
                async for event in self._generate_streaming_answer(question, final_docs, use_memory):
                    answer_events.append(event)
                    if event.type.value == "generation_chunk":
                        knowledge_base_answer += event.data.get("chunk", "")
                
                # 检查是否是"无法回答"的回复
                if "根据提供的资料，我无法回答该问题" in knowledge_base_answer:
                    # 知识库文档不相关，使用大模型自身知识
                    async for event in self._stream_no_result_answer(question, use_memory):
                        yield event
                else:
                    # 知识库文档相关，输出之前收集的事件
                    for event in answer_events:
                        yield event
            else:
                # 没有找到相关文档
                async for event in self._stream_no_result_answer(question, use_memory):
                    yield event
            
            # 3. 完成
            yield StreamEvent(
                type=StreamEventType.COMPLETE,
                data={"message": "回答完成"},
                timestamp=time.time()
            )
            
        except Exception as e:
            yield StreamEvent(
                type=StreamEventType.ERROR,
                data={"error": str(e)},
                timestamp=time.time()
            )
    
    async def ask_with_categories_stream(self, question: str, categories: List[str] = None) -> AsyncGenerator[StreamEvent, None]:
        """
        分类流式问答
        
        Args:
            question: 用户问题
            categories: 指定类别
            
        Yields:
            StreamEvent: 流式事件
        """
        if not self.qa_chain:
            yield StreamEvent(
                type=StreamEventType.ERROR,
                data={"error": "问答链尚未初始化"},
                timestamp=time.time()
            )
            return
        
        if categories is None:
            categories = config.DEFAULT_SEARCH_CATEGORIES
        
        try:
            # 处理阶段 - 内部处理
            yield StreamEvent(
                type=StreamEventType.PROCESSING,
                data={"message": f"正在处理您的问题（类别: {categories or '所有'})..."},
                timestamp=time.time()
            )
            
            # 内部处理：分类检索等
            if config.ENABLE_QUERY_REWRITING:
                rewritten_queries = await self._rewrite_query_async(question)
                retrieved_docs = await self._retrieve_with_multiple_queries_and_categories_async(rewritten_queries, categories)
                
                if retrieved_docs and self.reranker:
                    try:
                        reranked_docs = await self._run_in_executor(
                            self.reranker.compress_documents, retrieved_docs, question
                        )
                        final_docs = reranked_docs[:config.RERANKER_TOP_N]
                    except Exception:
                        final_docs = retrieved_docs[:config.RERANKER_TOP_N]
                else:
                    final_docs = retrieved_docs[:config.RERANKER_TOP_N]
            else:
                # ✅ 改进：使用分类检索但仍然使用真正的流式生成
                if categories:
                    # 获取分类相关的文档
                    def get_category_docs():
                        category_retriever = self._build_category_retriever(categories)
                        if self.reranker:
                            from langchain.retrievers import ContextualCompressionRetriever
                            compression_retriever = ContextualCompressionRetriever(
                                base_compressor=self.reranker,
                                base_retriever=category_retriever
                            )
                            return compression_retriever.get_relevant_documents(question)
                        else:
                            return category_retriever.get_relevant_documents(question)
                    
                    final_docs = await self._run_in_executor(get_category_docs)
                    
                    # 使用真正的流式生成
                    # if category_docs:
                    #     async for event in self._generate_streaming_answer(question, category_docs):
                    #         yield event
                    # else:
                    #     async for event in self._stream_existing_answer("根据提供的资料，我无法找到相关信息来回答该问题。"):
                    #         yield event

                    # yield StreamEvent(
                    #         type=StreamEventType.COMPLETE,
                    #         data={"message": "回答完成"},
                    #         timestamp=time.time()
                    #     )
                    # return
                else:
                    # ✅ 使用异步检索功能，避免调用LLM
                    retriever = self.qa_chain.retriever
                    
                    # 使用异步检索方法
                    if hasattr(retriever, 'ainvoke'):
                        final_docs = await retriever.ainvoke(question)
                    elif hasattr(retriever, 'aget_relevant_documents'):
                        final_docs = await retriever.aget_relevant_documents(question)
                    else:
                        # 如果没有异步方法，回退到线程池
                        final_docs = await self._run_in_executor(
                            retriever.get_relevant_documents, question
                        )
                    
                    # 使用真正的流式生成（LLM只被调用一次，且是流式的）
                    # if final_docs:
                    #     async for event in self._generate_streaming_answer(question, final_docs):
                    #         yield event
                    # else:
                    #     async for event in self._stream_existing_answer("根据提供的资料，我无法找到相关信息来回答该问题。"):
                    #         yield event
                    
                    # yield StreamEvent(
                    #         type=StreamEventType.COMPLETE,
                    #         data={"message": "回答完成"},
                    #         timestamp=time.time()
                    #     )
                    # return
            
            # 流式生成答案
            if final_docs:
                async for event in self._generate_streaming_answer(question, final_docs):
                    yield event
            else:
                async for event in self._stream_no_result_answer(question, True):
                    yield event
            
            yield StreamEvent(
                type=StreamEventType.COMPLETE,
                data={"message": "回答完成"},
                timestamp=time.time()
            )
            
        except Exception as e:
            yield StreamEvent(
                type=StreamEventType.ERROR,
                data={"error": str(e)},
                timestamp=time.time()
            )
    
    async def _generate_streaming_answer(self, question: str, documents: List[Document], use_memory: bool = True) -> AsyncGenerator[StreamEvent, None]:
        """
        生成流式答案 - 基于知识库文档的回答，支持短期记忆功能
        
        Args:
            question: 问题
            documents: 相关文档
            use_memory: 是否使用短期记忆功能
            
        Yields:
            StreamEvent: 流式事件
        """
        yield StreamEvent(
            type=StreamEventType.GENERATION_START,
            data={"message": "基于知识库文档生成答案"},
            timestamp=time.time()
        )
        
        try:
            # 构建上下文
            context = "\n\n".join([doc.page_content for doc in documents])
            
            # 获取短期记忆上下文
            memory_context = ""
            if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
                memory_context = memory_manager.get_conversation_context(include_count=None)  # 使用所有对话轮次
            
            # 构建完整的上下文（包含记忆上下文和检索上下文）
            full_context = context
            if memory_context:
                full_context = f"对话历史:\n{memory_context}\n\n当前检索到的相关信息:\n{context}"
            
            # 构建提示 - 使用提示词模板
            try:
                qa_template = get_qa_prompt_template()
                knowledge_base_prompt = qa_template.format(
                    context=full_context,
                    question=question
                )
            except Exception:
                # 如果提示词模板加载失败，使用备用提示词
                knowledge_base_prompt = f"""请严格根据下面提供的"上下文信息"来回答"问题"。
                    请在回答前加上"根据知识库资料："
                    如果上下文中没有足够的信息来回答问题，请直接说："根据提供的资料，我无法回答该问题。"
                    不允许编造或添加上下文之外的任何信息。

                    ---
                    上下文信息:
                    {full_context}
                    ---

                    问题: {question}

                    回答:"""
            
            # 收集完整答案用于保存到记忆
            complete_answer = ""
            
            # ✅ 关键改进：检查LLM是否支持流式调用
            if hasattr(self.llm, 'astream'):
                # 真正的流式LLM调用
                async for chunk in self.llm.astream(knowledge_base_prompt):
                    if hasattr(chunk, 'content') and chunk.content:
                        complete_answer += chunk.content
                        yield StreamEvent(
                            type=StreamEventType.GENERATION_CHUNK,
                            data={"chunk": chunk.content},
                            timestamp=time.time()
                        )
                    elif isinstance(chunk, str) and chunk:
                        complete_answer += chunk
                        yield StreamEvent(
                            type=StreamEventType.GENERATION_CHUNK,
                            data={"chunk": chunk},
                            timestamp=time.time()
                        )
            else:
                # 如果LLM不支持流式，回退到当前实现
                response = await self._run_in_executor(self.llm.invoke, knowledge_base_prompt)
                
                if hasattr(response, 'content'):
                    answer = response.content.strip()
                else:
                    answer = str(response).strip()
                
                complete_answer = answer
                
                # 流式输出已有答案
                async for event in self._stream_text(answer):
                    yield event
            
            # 保存对话到短期记忆
            if use_memory and config.ENABLE_SHORT_TERM_MEMORY and complete_answer:
                memory_manager.add_conversation(
                    question=question,
                    answer=complete_answer.strip(),
                    metadata={
                        "source_documents_count": len(documents),
                        "memory_context_included": bool(memory_context),
                        "streaming_mode": True,
                        "answer_source": "knowledge_base"
                    }
                )
            
            # 生成结束，提供源文档信息
            yield StreamEvent(
                type=StreamEventType.GENERATION_END,
                data={
                    "message": "基于知识库的答案生成完成",
                    "source_documents": [
                        {
                            "source": doc.metadata.get('source', '未知来源'),
                            "category": doc.metadata.get('category', '未知类别')
                        }
                        for doc in documents
                    ]
                },
                timestamp=time.time()
            )
            
        except Exception as e:
            yield StreamEvent(
                type=StreamEventType.ERROR,
                data={"error": f"生成答案时出错: {e}"},
                timestamp=time.time()
            )
    
    async def _stream_existing_answer(self, answer: str) -> AsyncGenerator[StreamEvent, None]:
        """
        流式输出已有的答案
        
        Args:
            answer: 已生成的答案
            
        Yields:
            StreamEvent: 流式事件
        """
        yield StreamEvent(
            type=StreamEventType.GENERATION_START,
            data={"message": "开始生成答案"},
            timestamp=time.time()
        )
        
        async for event in self._stream_text(answer):
            yield event
        
        yield StreamEvent(
            type=StreamEventType.GENERATION_END,
            data={"message": "答案生成完成"},
            timestamp=time.time()
        )
    
    async def _stream_text(self, text: str) -> AsyncGenerator[StreamEvent, None]:
        """
        核心的文本流式输出方法 - 生产环境版本
        
        Args:
            text: 要流式输出的文本
            
        Yields:
            StreamEvent: 流式事件
        """
        if not text:
            return
        
        # 生产环境：按字符流式输出，无人为延迟
        for i, char in enumerate(text):
            # ✅ 移除人为延迟，直接流式输出
            # 真实的延迟应该来自LLM生成，而不是人为添加
            
            yield StreamEvent(
                type=StreamEventType.GENERATION_CHUNK,
                data={"chunk": char},
                timestamp=time.time(),
                metadata={
                    "progress": (i + 1) / len(text),
                    "char_index": i + 1,
                    "total_chars": len(text)
                }
            )
        
        # 方案2: 按词语流式输出（可选）
        # words = text.split()
        # for i, word in enumerate(words):
        #     await asyncio.sleep(0.05)  # 50ms延迟
        #     
        #     yield StreamEvent(
        #         type=StreamEventType.GENERATION_CHUNK,
        #         data={"chunk": word + (" " if i < len(words) - 1 else "")},
        #         timestamp=time.time(),
        #         metadata={
        #             "progress": (i + 1) / len(words),
        #             "word_index": i + 1,
        #             "total_words": len(words)
        #         }
        #     )
    
    async def batch_ask_stream(self, questions: List[str]) -> AsyncGenerator[StreamEvent, None]:
        """
        批量流式问答 - 并发处理版本
        
        Args:
            questions: 问题列表
            
        Yields:
            StreamEvent: 流式事件
        """
        if not questions:
            return
        
        yield StreamEvent(
            type=StreamEventType.PROCESSING,
            data={
                "message": f"开始并发处理 {len(questions)} 个问题",
                "total_questions": len(questions),
                "processing_mode": "concurrent"
            },
            timestamp=time.time()
        )
        
        # 创建并发任务
        tasks = []
        for i, question in enumerate(questions):
            task = asyncio.create_task(
                self._collect_question_events(question, i + 1, len(questions))
            )
            tasks.append(task)
        
        # 等待所有任务完成并收集结果
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 合并所有事件并按时间戳排序
            all_events = []
            successful_count = 0
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # 处理异常情况
                    yield StreamEvent(
                        type=StreamEventType.ERROR,
                        data={
                            "error": f"处理问题 {i+1} 时出错: {str(result)}",
                            "question": questions[i],
                            "question_index": i + 1
                        },
                        timestamp=time.time()
                    )
                else:
                    all_events.extend(result)
                    successful_count += 1
            
            # 按时间戳排序所有事件
            all_events.sort(key=lambda e: e.timestamp)
            
            # 流式输出所有事件
            for event in all_events:
                yield event
            
            # 发送完成事件
            yield StreamEvent(
                type=StreamEventType.COMPLETE,
                data={
                    "message": f"批量处理完成，成功处理 {successful_count}/{len(questions)} 个问题",
                    "total_processed": successful_count,
                    "total_questions": len(questions),
                    "processing_mode": "concurrent"
                },
                timestamp=time.time()
            )
            
        except Exception as e:
            yield StreamEvent(
                type=StreamEventType.ERROR,
                data={
                    "error": f"批量处理过程中出错: {str(e)}",
                    "total_questions": len(questions)
                },
                timestamp=time.time()
            )
    
    async def _collect_question_events(self, question: str, index: int, total: int) -> List[StreamEvent]:
        """
        收集单个问题的所有事件
        
        Args:
            question: 问题内容
            index: 问题索引
            total: 总问题数
            
        Returns:
            List[StreamEvent]: 事件列表
        """
        events = []
        
        try:
            async for event in self.ask_stream(question):
                # 为批量处理添加元数据
                if event.metadata is None:
                    event.metadata = {}
                event.metadata.update({
                    "batch_index": index,
                    "batch_total": total,
                    "batch_question": question,
                    "processing_mode": "concurrent"
                })
                events.append(event)
                
        except Exception as e:
            # 单个问题处理失败
            error_event = StreamEvent(
                type=StreamEventType.ERROR,
                data={
                    "error": f"处理问题失败: {str(e)}",
                    "question": question
                },
                timestamp=time.time(),
                metadata={
                    "batch_index": index,
                    "batch_total": total,
                    "batch_question": question,
                    "processing_mode": "concurrent"
                }
            )
            events.append(error_event)
        
        return events
    
    async def _stream_no_result_answer(self, question: str = "", use_memory: bool = True) -> AsyncGenerator[StreamEvent, None]:
        """
        当知识库没有相关文档时，使用大模型自身知识回答
        
        Args:
            question: 用户问题
            use_memory: 是否使用短期记忆功能
        
        Yields:
            StreamEvent: 流式事件
        """
        yield StreamEvent(
            type=StreamEventType.GENERATION_START,
            data={"message": "知识库未找到相关资料，使用大模型训练知识回答"},
            timestamp=time.time()
        )
        
        try:
            # 获取短期记忆上下文
            memory_context = ""
            if use_memory and config.ENABLE_SHORT_TERM_MEMORY:
                memory_context = memory_manager.get_conversation_context(include_count=None)
            
            # 构建使用大模型自身知识的提示
            llm_knowledge_prompt = f"""知识库中没有找到相关资料来回答这个问题。
                现在请使用你的训练知识来尝试回答用户的问题。

                回答规则：
                1. 如果这是一个你可以基于训练知识回答的常识性问题（比如科学知识、历史事实、一般性概念等），请在回答前加上"知识库资料未检索到内容，使用大模型训练知识回复："，然后提供准确的回答。

                2. 只有在以下情况下才回复"根据提供的资料，我无法回答该问题。"：
                - 需要预测未来的具体事件（如彩票号码、股价走势等）
                - 涉及个人隐私信息
                - 违法或有害内容
                - 需要实时信息但你确实无法获取的情况
                - 你完全不知道答案的专业技术问题

                3. 对于"今天是星期几"这类问题，虽然你无法获取实时信息，但你可以解释如何查询，这属于可以回答的范畴。

                {f"对话历史:{memory_context}" if memory_context else ""}

                用户问题: {question}

                回答:"""
            
            # 收集完整答案用于保存到记忆
            complete_answer = ""
            
            # 使用大模型自身知识生成答案
            if hasattr(self.llm, 'astream'):
                # 流式调用
                async for chunk in self.llm.astream(llm_knowledge_prompt):
                    if hasattr(chunk, 'content') and chunk.content:
                        complete_answer += chunk.content
                        yield StreamEvent(
                            type=StreamEventType.GENERATION_CHUNK,
                            data={"chunk": chunk.content},
                            timestamp=time.time()
                        )
                    elif isinstance(chunk, str) and chunk:
                        complete_answer += chunk
                        yield StreamEvent(
                            type=StreamEventType.GENERATION_CHUNK,
                            data={"chunk": chunk},
                            timestamp=time.time()
                        )
            else:
                # 非流式调用
                response = await self._run_in_executor(self.llm.invoke, llm_knowledge_prompt)
                
                if hasattr(response, 'content'):
                    answer = response.content.strip()
                else:
                    answer = str(response).strip()
                
                complete_answer = answer
                
                # 流式输出答案
                async for event in self._stream_text(answer):
                    yield event
            
            # 保存对话到短期记忆
            if use_memory and config.ENABLE_SHORT_TERM_MEMORY and question and complete_answer:
                memory_manager.add_conversation(
                    question=question,
                    answer=complete_answer.strip(),
                    metadata={
                        "source_documents_count": 0,
                        "memory_context_included": bool(memory_context),
                        "streaming_mode": True,
                        "answer_source": "llm_knowledge"
                    }
                )
            
            # 生成结束
            yield StreamEvent(
                type=StreamEventType.GENERATION_END,
                data={"message": "基于大模型训练知识的答案生成完成"},
                timestamp=time.time()
            )
            
        except Exception as e:
            # 如果大模型调用也失败了，返回标准的无法回答消息
            fallback_message = "根据提供的资料，我无法回答该问题。"
            
            yield StreamEvent(
                type=StreamEventType.GENERATION_CHUNK,
                data={"chunk": fallback_message},
                timestamp=time.time()
            )
            
            # 保存失败情况到记忆
            if use_memory and config.ENABLE_SHORT_TERM_MEMORY and question:
                memory_manager.add_conversation(
                    question=question,
                    answer=fallback_message,
                    metadata={
                        "source_documents_count": 0,
                        "memory_context_included": bool(memory_context),
                        "streaming_mode": True,
                        "answer_source": "fallback",
                        "error": str(e)
                    }
                )
            
            yield StreamEvent(
                type=StreamEventType.GENERATION_END,
                data={"message": "回答生成完成"},
                timestamp=time.time()
            )
```

## `README.md`

```markdown
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

```

## `sse_api_server.py`

```python
# api_server.py

import asyncio
import logging
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import json # <--- 导入json库
# 导入我们的核心 RAG 引擎
from rag.streaming_pipeline import StreamingRagPipeline, StreamEventType, StreamEvent

# --- 日志配置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- FastAPI 应用实例 ---
app = FastAPI(
    title="企业级高性能流式RAG API",
    description="一个基于FastAPI的、支持流式响应、批量处理和智能同步的RAG系统API。",
    version="5.0.0",
)

# --- 数据模型 (用于请求和响应体) ---
class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户提出的问题")
    categories: Optional[List[str]] = Field(None, description="限定检索的类别列表，为空则检索所有类别")

class BatchAskRequest(BaseModel):
    questions: List[str] = Field(..., min_items=1, description="需要批量处理的问题列表")

# --- 全局单例：RAG Pipeline ---
# 在应用启动时创建pipeline实例，确保全局只有一个，避免重复加载模型
pipeline: Optional[StreamingRagPipeline] = None

@app.on_event("startup")
async def startup_event():
    """FastAPI应用启动时执行的事件"""
    global pipeline
    logger.info("应用启动，正在初始化RAG Pipeline...")
    try:
        pipeline = StreamingRagPipeline()
        # 首次启动时，建议执行一次同步
        logger.info("首次启动，执行一次知识库同步...")
        await pipeline.sync_data_directory_async()
        logger.info("RAG Pipeline 初始化和首次同步完成。")
    except Exception as e:
        logger.error(f"Pipeline初始化失败: {e}", exc_info=True)
        # 在这种情况下，后续的API调用会失败，这是预期的
        pipeline = None

@app.on_event("shutdown")
async def shutdown_event():
    """FastAPI应用关闭时执行的事件"""
    if pipeline and hasattr(pipeline, 'executor'):
        logger.info("应用关闭，正在关闭线程池...")
        pipeline.executor.shutdown(wait=True)
        logger.info("线程池已关闭。")

# --- API Endpoints ---

@app.get("/", summary="健康检查", description="检查API服务是否正在运行。")
async def health_check():
    """根路径，用于简单的健康检查。"""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="服务不可用：RAG Pipeline初始化失败。")
    return {"status": "ok", "message": "RAG API Service is running."}

@app.post("/sync", summary="同步知识库", description="异步触发一次知识库的完全同步。")
async def sync_knowledge_base():
    """
    触发对所有数据源的智能同步。这是一个耗时操作，API会立即返回，同步在后台进行。
    """
    if pipeline is None:
        raise HTTPException(status_code=503, detail="服务不可用。")
    
    # 在后台异步执行同步任务，不阻塞API响应
    asyncio.create_task(pipeline.sync_data_directory_async())
    
    return JSONResponse(
        status_code=202, # 202 Accepted: 请求已被接受，但处理尚未完成
        content={"message": "知识库同步任务已在后台启动。"}
    )

@app.get("/stats", summary="获取知识库统计信息", description="获取当前知识库的详细构成信息。")
async def get_stats():
    """
    返回知识库的详细统计数据，包括各个类别的文档数量和来源。
    """
    if pipeline is None:
        raise HTTPException(status_code=503, detail="服务不可用。")
    
    # 这是一个快速的同步方法，可以直接调用
    stats = pipeline.get_data_source_info()
    return JSONResponse(content=stats)

@app.get("/categories", summary="获取可用类别", description="获取知识库中所有可用的文档类别。")
async def get_categories():
    """
    返回一个包含所有可用类别及其文档块数量的字典。
    """
    if pipeline is None:
        raise HTTPException(status_code=503, detail="服务不可用。")
        
    categories = pipeline.get_available_categories()
    return JSONResponse(content=categories)

@app.post("/ask/stream", summary="流式问答", description="核心的流式问答接口，使用Server-Sent Events (SSE)进行流式响应。")
async def ask_streaming(request: AskRequest):
    """
    接收一个问题和可选的类别，通过SSE返回一个事件流。
    事件类型包括：processing, generation_start, generation_chunk, generation_end, error, complete。
    """
    if pipeline is None:
        raise HTTPException(status_code=503, detail="服务不可用。")

    async def event_generator():
        try:
            if request.categories is not None:
                stream = pipeline.ask_with_categories_stream(request.question, request.categories)
            else:
                stream = pipeline.ask_stream(request.question)
            
            async for event in stream:
                # === 【关键修正】 ===
                # 将我们自己的StreamEvent对象转换为字典，然后再序列化成JSON字符串
                # 作为sse-starlette的"data"字段发送出去。
                # 我们还可以指定一个事件名称，方便前端根据名称来监听。
                yield {
                    "event": event.type.value, # 使用我们自己的事件类型作为SSE的事件名
                    "data": json.dumps(event.to_dict()) # 将整个事件对象作为JSON数据发送
                }
        except Exception as e:
            logger.error(f"流式问答处理失败: {e}", exc_info=True)
            # 对于错误，也遵循同样的格式
            error_event_data = StreamEvent(
                type=StreamEventType.ERROR,
                data={"error": f"服务器内部错误: {e}"},
                timestamp=time.time()
            ).to_dict()
            yield {
                "event": "error",
                "data": json.dumps(error_event_data)
            }

    return EventSourceResponse(event_generator())

@app.post("/ask/batch-stream", summary="并发批量流式问答", description="并发处理多个问题，并通过SSE流式返回所有事件。")
async def batch_ask_streaming(request: BatchAskRequest):
    """
    接收一个问题列表，并发地处理它们，并通过单个SSE连接流式返回所有问题的事件。
    事件会包含`batch_index`等元数据，以便客户端区分。
    """
    if pipeline is None:
        raise HTTPException(status_code=503, detail="服务不可用。")

    async def batch_event_generator():
        try:
            async for event in pipeline.batch_ask_stream(request.questions):
                # === 【关键修正】 ===
                # 对批量接口也应用同样的格式转换
                yield {
                    "event": event.type.value,
                    "data": json.dumps(event.to_dict())
                }
        except Exception as e:
            logger.error(f"批量流式问答处理失败: {e}", exc_info=True)
            error_event_data = StreamEvent(
                type=StreamEventType.ERROR,
                data={"error": f"服务器内部错误: {e}"},
                timestamp=time.time()
            ).to_dict()
            yield {
                "event": "error",
                "data": json.dumps(error_event_data)
            }

    return EventSourceResponse(batch_event_generator())
# --- 如何运行 ---
# 在终端中，进入项目根目录，然后运行以下命令:
# uvicorn api_server:app --reload
#
# --reload: 代码更改时自动重启服务器，方便开发
#
# API文档将自动生成在: http://127.0.0.1:8000/docs
# 另一个UI界面在: http://127.0.0.1:8000/redoc

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting server programmatically...")
    
    # 以编程方式启动Uvicorn
    # 这种方式对环境的依赖最小
    uvicorn.run(
        # 第一个参数 "api_server:app" 告诉uvicorn应用实例在哪里
        # 如果此文件就叫api_server.py，可以直接写 "app"
        # 但为了明确，写全 "api_server:app" 是最好的实践
        "api_server:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,  # 开启内置的热重载功能
        log_level="info"
    )
```

## `streaming_main.py`

```python
# streaming_main.py - 正确的流式响应演示

import asyncio
import time
from rag.streaming_pipeline import StreamingRagPipeline, StreamEvent, StreamEventType


class StreamingDemo:
    """流式响应演示"""
    
    def __init__(self):
        self.rag = None
    
    async def initialize(self):
        """初始化RAG系统"""
        print("🚀 初始化流式RAG系统...")
        self.rag = StreamingRagPipeline()
        
        print("📁 同步数据目录...")
        await self.rag.sync_data_directory_async()
        print("✅ 初始化完成！\n")
    
    def display_event(self, event: StreamEvent):
        """显示事件"""
        timestamp = time.strftime("%H:%M:%S", time.localtime(event.timestamp))
        
        if event.type == StreamEventType.PROCESSING:
            print(f"🔄 [{timestamp}] {event.data.get('message', '')}")
        
        elif event.type == StreamEventType.GENERATION_START:
            print(f"💭 [{timestamp}] {event.data.get('message', '')}")
            print("📝 答案: ", end='', flush=True)  # 开始答案输出行
        
        elif event.type == StreamEventType.GENERATION_CHUNK:
            # ✅ 这里展示真正的流式输出效果
            chunk = event.data.get('chunk', '')
            print(chunk, end='', flush=True)
            
            # 如果是真正的流式LLM，chunk可能是token而不是字符
            # 这里可以根据chunk的长度来判断是字符流式还是token流式
            if len(chunk) > 1:
                # 可能是token流式，添加小延迟以便观察效果
                import time as time_module
                time_module.sleep(0.01)
        
        elif event.type == StreamEventType.GENERATION_END:
            print()  # 换行
            sources = event.data.get('source_documents', [])
            if sources:
                print(f"\n📚 [{timestamp}] 参考文档:")
                for doc in sources:
                    print(f"    📄 {doc['source']} (类别: {doc['category']})")
            else:
                print(f"\n✅ [{timestamp}] {event.data.get('message', '')}")
        
        elif event.type == StreamEventType.ERROR:
            print(f"\n❌ [{timestamp}] 错误: {event.data.get('error', '')}")
        
        elif event.type == StreamEventType.COMPLETE:
            print(f"\n🎉 [{timestamp}] {event.data.get('message', '')}")
    
    async def demo_correct_streaming(self):
        """演示正确的流式响应"""
        print("=" * 60)
        print("✅ 正确的流式响应演示")
        print("=" * 60)
        print("💡 特点: 只有最终答案是流式的，中间处理不流式")
        
        question = "什么是机器学习？"
        print(f"\n❓ 问题: {question}\n")
        
        async for event in self.rag.ask_stream(question):
            self.display_event(event)
    
    async def demo_performance_comparison(self):
        """演示性能对比：正确流式 vs 非流式"""
        print("\n" + "=" * 60)
        print("⚡ 性能对比：正确流式 vs 非流式")
        print("=" * 60)
        
        question = "Python有什么优势？"
        print(f"❓ 测试问题: {question}\n")
        
        # 1. 非流式版本
        print("🔄 非流式版本:")
        start_time = time.time()
        result = await self.rag.ask_async(question)
        non_streaming_time = time.time() - start_time
        
        print(f"  ⏱️ 总耗时: {non_streaming_time:.2f}秒")
        print(f"  📝 答案: {result['result'][:100]}...")
        
        # 2. 正确的流式版本
        print(f"\n⚡ 正确的流式版本:")
        start_time = time.time()
        first_chunk_time = None
        processing_done_time = None
        generation_start_time = None
        
        async for event in self.rag.ask_stream(question):
            current_time = time.time()
            
            if event.type == StreamEventType.PROCESSING:
                print(f"  🔄 [{current_time - start_time:.2f}s] {event.data['message']}")
            
            elif event.type == StreamEventType.GENERATION_START:
                generation_start_time = current_time
                processing_done_time = current_time - start_time
                print(f"  💭 [{processing_done_time:.2f}s] 开始流式生成答案...")
            
            elif event.type == StreamEventType.GENERATION_CHUNK:
                if first_chunk_time is None:
                    first_chunk_time = current_time
                    first_chunk_latency = first_chunk_time - start_time
                    print(f"  ⚡ [{first_chunk_latency:.2f}s] 首个字符输出！")
                    print(f"  📝 答案: ", end='', flush=True)
                
                print(event.data.get('chunk', ''), end='', flush=True)
            
            elif event.type == StreamEventType.COMPLETE:
                total_time = current_time - start_time
                print(f"\n  ✅ [{total_time:.2f}s] 完成")
        
        # 3. 性能分析
        if first_chunk_time and processing_done_time:
            print(f"\n📊 性能分析:")
            print(f"  处理阶段耗时: {processing_done_time:.2f}秒")
            print(f"  首字符延迟: {first_chunk_time - start_time:.2f}秒")
            print(f"  用户感知延迟: {first_chunk_time - generation_start_time:.2f}秒 (生成开始到首字符)")
            
            print(f"\n💡 关键洞察:")
            print(f"  - 中间处理不需要流式，用户不关心具体步骤")
            print(f"  - 流式的价值在于答案生成阶段")
            print(f"  - 用户看到答案开始生成的延迟很短")
    
    async def demo_interactive_experience(self):
        """演示交互体验"""
        print("\n" + "=" * 60)
        print("💬 交互体验演示")
        print("=" * 60)
        print("输入问题体验正确的流式响应（输入 'quit' 退出）:")
        
        while True:
            try:
                question = input("\n❓ 请输入问题: ").strip()
                
                if question.lower() in ['quit', 'exit', '退出']:
                    print("👋 再见！")
                    break
                
                if not question:
                    continue
                
                print()  # 空行
                
                async for event in self.rag.ask_stream(question):
                    self.display_event(event)
                
            except KeyboardInterrupt:
                print("\n\n👋 用户中断，退出程序")
                break
            except Exception as e:
                print(f"\n❌ 处理错误: {e}")
    
    async def demo_batch_processing(self):
        """演示批量处理"""
        print("\n" + "=" * 60)
        print("📦 批量处理演示")
        print("=" * 60)
        
        questions = [
            "什么是深度学习？",
            "Python的主要特点是什么？",
            "如何优化程序性能？"
        ]
        
        print(f"📝 批量处理 {len(questions)} 个问题:")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")
        print()
        
        async for event in self.rag.batch_ask_stream(questions):
            self.display_event(event)


async def main():
    """主演示函数"""
    demo = StreamingDemo()
    
    try:
        # 初始化系统
        await demo.initialize()
        
        # 运行演示
        await demo.demo_correct_streaming()
        await demo.demo_performance_comparison()
        await demo.demo_batch_processing()
        
        # 可选：交互演示
        # await demo.demo_interactive_experience()
        
        print("\n" + "=" * 60)
        print("🎉 正确的流式响应演示完成！")
        print("=" * 60)
        print("💡 正确流式响应的特点:")
        print("  1. 中间处理过程不流式，只做状态通知")
        print("  2. 只有最终答案生成是真正的流式输出")
        print("  3. 用户体验聚焦在看到答案逐步生成")
        print("  4. 减少不必要的事件，提高效率")
        print("  5. 更符合用户的实际需求和期望")
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行正确的流式响应演示
    asyncio.run(main())
```

## `streaming_web_demo.py`

```python
"""
流式RAG Web演示 - FastAPI + WebSocket实现
展示正确的流式响应理念：只有答案生成是流式的
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# 导入我们的流式RAG管道
import sys
sys.path.append(str(Path(__file__).parent))

from rag.streaming_pipeline import StreamingRagPipeline

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="流式RAG演示", description="基于FastAPI + WebSocket的流式问答系统")

# 全局RAG管道实例
rag_pipeline = None

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化RAG管道和热重载功能"""
    global rag_pipeline
    try:
        logger.info("正在初始化RAG管道...")
        rag_pipeline = StreamingRagPipeline()
        logger.info("RAG管道初始化完成")
        
        # 启用热重载功能
        from rag.hot_reload_manager import enable_hot_reload
        if enable_hot_reload():
            logger.info("🔥 热重载功能已启用")
        else:
            logger.warning("⚠️ 热重载功能启用失败")
            
    except Exception as e:
        logger.error(f"初始化失败: {e}")
        raise

# === 添加 shutdown 事件 ===
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    global rag_pipeline
    
    # 停止热重载监控
    from rag.hot_reload_manager import disable_hot_reload
    disable_hot_reload()
    logger.info("🛑 热重载监控已停止")
    
    # 清理线程池
    if rag_pipeline and hasattr(rag_pipeline, 'executor'):
        logger.info("应用正在关闭，清理线程池...")
        rag_pipeline.executor.shutdown(wait=True)
        logger.info("线程池已成功关闭。")

@app.get("/")
async def get_homepage():
    """返回Web界面HTML"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>流式RAG问答系统</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .chat-container {
                height: 400px;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                overflow-y: auto;
                background-color: #fafafa;
                margin-bottom: 20px;
            }
            .message {
                margin-bottom: 15px;
                padding: 10px;
                border-radius: 8px;
            }
            .user-message {
                background-color: #007bff;
                color: white;
                margin-left: 20%;
                text-align: right;
            }
            .bot-message {
                background-color: #e9ecef;
                color: #333;
                margin-right: 20%;
            }
            .status-message {
                background-color: #fff3cd;
                color: #856404;
                font-style: italic;
                text-align: center;
                border: 1px solid #ffeaa7;
            }
            .input-container {
                display: flex;
                gap: 10px;
            }
            #questionInput {
                flex: 1;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 16px;
            }
            #sendButton {
                padding: 12px 24px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
            }
            #sendButton:hover {
                background-color: #0056b3;
            }
            #sendButton:disabled {
                background-color: #6c757d;
                cursor: not-allowed;
            }
            .connection-status {
                text-align: center;
                padding: 10px;
                margin-bottom: 20px;
                border-radius: 6px;
            }
            .connected {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .disconnected {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌊 流式RAG问答系统</h1>
            
            <div id="connectionStatus" class="connection-status disconnected">
                正在连接...
            </div>
            
            <div id="chatContainer" class="chat-container">
                <div class="message status-message">
                    欢迎使用流式RAG问答系统！请输入您的问题。
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="questionInput" placeholder="请输入您的问题..." />
                <button id="sendButton" disabled>发送</button>
            </div>
        </div>

        <script>
            let ws = null;
            let isConnected = false;
            
            const chatContainer = document.getElementById('chatContainer');
            const questionInput = document.getElementById('questionInput');
            const sendButton = document.getElementById('sendButton');
            const connectionStatus = document.getElementById('connectionStatus');
            
            function connectWebSocket() {
                const wsUrl = `ws://${window.location.host}/ws`;
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    console.log('WebSocket连接已建立');
                    isConnected = true;
                    updateConnectionStatus(true);
                    sendButton.disabled = false;
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleMessage(data);
                };
                
                ws.onclose = function(event) {
                    console.log('WebSocket连接已关闭');
                    isConnected = false;
                    updateConnectionStatus(false);
                    sendButton.disabled = true;
                    
                    // 尝试重连
                    setTimeout(connectWebSocket, 3000);
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket错误:', error);
                };
            }
            
            function updateConnectionStatus(connected) {
                if (connected) {
                    connectionStatus.textContent = '✅ 已连接';
                    connectionStatus.className = 'connection-status connected';
                } else {
                    connectionStatus.textContent = '❌ 连接断开';
                    connectionStatus.className = 'connection-status disconnected';
                }
            }
            
            function addMessage(content, type) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}-message`;
                messageDiv.textContent = content;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
                return messageDiv;
            }
            
            let currentBotMessage = null;
            
            function handleMessage(data) {
                switch (data.type) {
                    case 'status':
                        addMessage(data.message, 'status');
                        break;
                        
                    case 'answer_start':
                        // 开始接收答案，创建新的消息容器
                        currentBotMessage = addMessage('', 'bot');
                        break;
                        
                    case 'answer_chunk':
                        // 流式更新答案内容
                        if (currentBotMessage) {
                            currentBotMessage.textContent += data.content;
                            chatContainer.scrollTop = chatContainer.scrollHeight;
                        }
                        break;
                        
                    case 'answer_complete':
                        // 答案生成完成
                        currentBotMessage = null;
                        sendButton.disabled = false;
                        sendButton.textContent = '发送';
                        break;
                        
                    case 'error':
                        addMessage(`错误: ${data.message}`, 'status');
                        sendButton.disabled = false;
                        sendButton.textContent = '发送';
                        break;
                }
            }
            
            function sendQuestion() {
                const question = questionInput.value.trim();
                if (!question || !isConnected) return;
                
                // 显示用户问题
                addMessage(question, 'user');
                
                // 发送到服务器
                ws.send(JSON.stringify({
                    type: 'question',
                    content: question
                }));
                
                // 清空输入框并禁用发送按钮
                questionInput.value = '';
                sendButton.disabled = true;
                sendButton.textContent = '处理中...';
            }
            
            // 事件监听
            sendButton.addEventListener('click', sendQuestion);
            
            questionInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendQuestion();
                }
            });
            
            // 初始化连接
            connectWebSocket();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点处理流式问答"""
    await websocket.accept()
    logger.info("WebSocket连接已建立")
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "question":
                question = message["content"]
                logger.info(f"收到问题: {question}")
                
                # 处理问题并流式返回答案
                await handle_question(websocket, question)
                
    except WebSocketDisconnect:
        logger.info("WebSocket连接已断开")
    except Exception as e:
        logger.error(f"WebSocket处理错误: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))

async def handle_question(websocket: WebSocket, question: str):
    """处理问题并流式返回答案"""
    try:
        answer_started = False
        
        # 使用流式RAG管道生成答案
        async for event in rag_pipeline.ask_stream(question):
            if event.type.value == "processing":
                # 处理状态更新
                await websocket.send_text(json.dumps({
                    "type": "status",
                    "message": f"🔍 {event.data.get('message', '正在处理...')}"
                }))
                
            elif event.type.value == "generation_start":
                # 开始生成答案
                if not answer_started:
                    await websocket.send_text(json.dumps({
                        "type": "answer_start"
                    }))
                    answer_started = True
                    
            elif event.type.value == "generation_chunk":
                # 流式答案片段
                chunk = event.data.get("chunk", "")
                if chunk.strip():  # 只发送非空内容
                    await websocket.send_text(json.dumps({
                        "type": "answer_chunk",
                        "content": chunk
                    }))
                    
            elif event.type.value == "generation_end":
                # 答案生成完成
                await websocket.send_text(json.dumps({
                    "type": "answer_complete"
                }))
                
            elif event.type.value == "error":
                # 错误处理
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": event.data.get("error", "未知错误")
                }))
                return
                
            elif event.type.value == "complete":
                # 整个流程完成
                if not answer_started:
                    # 如果没有流式答案，可能是直接返回了结果
                    await websocket.send_text(json.dumps({
                        "type": "answer_complete"
                    }))
        
    except Exception as e:
        logger.error(f"处理问题时出错: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"处理问题时出错: {str(e)}"
        }))

if __name__ == "__main__":
    import uvicorn
    
    print("🌊 启动流式RAG Web演示...")
    print("📱 访问地址: http://localhost:8000")
    print("💡 这个演示展示了正确的流式响应理念：只有答案生成是流式的")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
```

