# test/test_async_features.py - 异步功能测试

import asyncio
import time
import os
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.async_pipeline import AsyncRagPipeline
from rag import config


class AsyncFeatureTester:
    """异步功能测试类"""
    
    def __init__(self):
        self.test_data_dir = None
        self.original_data_path = None
        self.rag = None
    
    async def setup_test_environment(self):
        """设置测试环境"""
        print("🔧 设置异步测试环境...")
        
        # 创建临时测试目录
        self.test_data_dir = tempfile.mkdtemp(prefix="async_rag_test_")
        print(f"📁 创建测试目录: {self.test_data_dir}")
        
        # 备份原始配置
        self.original_data_path = config.DATA_PATH
        config.DATA_PATH = self.test_data_dir
        
        # 创建测试文档
        await self._create_test_documents()
        
        # 初始化异步RAG系统
        self.rag = AsyncRagPipeline()
        print("✅ 异步测试环境设置完成")
    
    async def _create_test_documents(self):
        """创建测试文档"""
        test_docs = {
            "机器学习基础.txt": """
机器学习是人工智能的一个重要分支。
它使计算机能够在没有明确编程的情况下学习和改进。
机器学习算法通过训练数据来构建数学模型。
常见的机器学习类型包括监督学习、无监督学习和强化学习。
            """.strip(),
            
            "Python编程.txt": """
Python是一种高级编程语言，具有简洁的语法。
Python广泛应用于数据科学、Web开发和人工智能领域。
Python拥有丰富的第三方库生态系统。
Python的优势包括易学易用、跨平台兼容性强。
            """.strip(),
            
            "RAG系统介绍.txt": """
RAG（检索增强生成）是一种结合检索和生成的AI技术。
RAG系统能够从知识库中检索相关信息来增强回答质量。
混合检索结合了向量检索和关键字检索的优势。
企业级RAG系统支持多数据源和分类管理功能。
            """.strip(),
            
            "异步编程.txt": """
异步编程是一种并发编程模式。
异步编程可以提高程序的性能和响应速度。
Python的asyncio库提供了异步编程支持。
异步函数使用async/await关键字定义和调用。
            """.strip(),
            
            "系统优化.txt": """
系统优化是提高软件性能的重要手段。
并发处理可以显著提升系统吞吐量。
缓存机制能够减少重复计算和I/O操作。
负载均衡有助于分散系统压力。
            """.strip()
        }
        
        print("📝 创建测试文档...")
        for filename, content in test_docs.items():
            file_path = os.path.join(self.test_data_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✓ 创建: {filename}")
    
    async def test_async_sync(self):
        """测试异步同步功能"""
        print("\n" + "=" * 50)
        print("🔄 测试异步同步功能")
        print("=" * 50)
        
        start_time = time.time()
        await self.rag.sync_data_directory_async()
        sync_time = time.time() - start_time
        
        print(f"✅ 异步同步完成，耗时: {sync_time:.2f}秒")
        
        # 验证文档是否正确加载
        categories = self.rag.get_available_categories()
        print(f"📊 加载的文档类别: {categories}")
        
        return sync_time
    
    async def test_async_qa(self):
        """测试异步问答功能"""
        print("\n" + "=" * 50)
        print("🤖 测试异步问答功能")
        print("=" * 50)
        
        test_questions = [
            "什么是机器学习？",
            "Python有什么优势？",
            "异步编程的好处是什么？",
            "如何优化系统性能？"
        ]
        
        # 串行测试
        print("📝 串行问答测试...")
        serial_start = time.time()
        serial_results = []
        for i, question in enumerate(test_questions):
            print(f"   问题 {i+1}: {question}")
            result = await self.rag.ask_async(question)
            serial_results.append(result)
            print(f"   回答: {result['result'][:100]}...")
        serial_time = time.time() - serial_start
        
        # 并行测试
        print("\n⚡ 并行问答测试...")
        parallel_start = time.time()
        parallel_tasks = [self.rag.ask_async(question) for question in test_questions]
        parallel_results = await asyncio.gather(*parallel_tasks)
        parallel_time = time.time() - parallel_start
        
        print(f"\n📊 问答性能对比:")
        print(f"   串行执行: {serial_time:.2f}秒")
        print(f"   并行执行: {parallel_time:.2f}秒")
        if serial_time > parallel_time:
            improvement = ((serial_time - parallel_time) / serial_time) * 100
            print(f"   🚀 并行提升: {improvement:.1f}%")
        
        return parallel_time, serial_time
    
    async def test_async_file_operations(self):
        """测试异步文件操作"""
        print("\n" + "=" * 50)
        print("📁 测试异步文件操作")
        print("=" * 50)
        
        # 测试文件修改检测
        test_file = os.path.join(self.test_data_dir, "测试修改.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("这是一个测试文件。")
        
        print("📝 测试文件修改检测...")
        is_new = await self.rag._is_file_modified_async(test_file)
        print(f"   新文件检测: {is_new}")
        
        # 添加到数据库
        await self.rag.update_document_async(test_file)
        
        # 修改文件内容
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("这是修改后的测试文件内容。")
        
        is_modified = await self.rag._is_file_modified_async(test_file)
        print(f"   文件修改检测: {is_modified}")
        
        # 测试文件删除
        print("🗑️  测试文件删除...")
        delete_success = await self.rag.delete_documents_by_source_async(test_file)
        print(f"   删除结果: {delete_success}")
    
    async def test_concurrent_operations(self):
        """测试并发操作"""
        print("\n" + "=" * 50)
        print("⚡ 测试并发操作")
        print("=" * 50)
        
        # 创建多个测试文件
        concurrent_files = []
        for i in range(5):
            file_path = os.path.join(self.test_data_dir, f"并发测试_{i}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"这是并发测试文件 {i}。\n内容包括测试数据和示例信息。")
            concurrent_files.append(file_path)
        
        # 并发文件信息获取
        print("📊 并发获取文件信息...")
        start_time = time.time()
        info_tasks = [self.rag._get_file_info_async(file_path) for file_path in concurrent_files]
        file_infos = await asyncio.gather(*info_tasks)
        info_time = time.time() - start_time
        
        print(f"   ✅ 并发获取 {len(file_infos)} 个文件信息，耗时: {info_time:.2f}秒")
        
        # 并发文档更新
        print("🔄 并发文档更新...")
        start_time = time.time()
        update_tasks = [self.rag.update_document_async(file_path) for file_path in concurrent_files]
        update_results = await asyncio.gather(*update_tasks)
        update_time = time.time() - start_time
        
        success_count = sum(update_results)
        print(f"   ✅ 并发更新 {success_count}/{len(concurrent_files)} 个文档，耗时: {update_time:.2f}秒")
        
        # 并发问答测试
        print("🤖 并发问答测试...")
        concurrent_questions = [
            "什么是机器学习？",
            "Python的特点",
            "异步编程优势",
            "系统优化方法",
            "RAG系统功能"
        ]
        
        start_time = time.time()
        qa_tasks = [self.rag.ask_async(question) for question in concurrent_questions]
        qa_results = await asyncio.gather(*qa_tasks)
        qa_time = time.time() - start_time
        
        print(f"   ✅ 并发回答 {len(qa_results)} 个问题，耗时: {qa_time:.2f}秒")
        print(f"   📊 平均每个问题: {qa_time / len(qa_results):.2f}秒")
    
    async def test_error_handling(self):
        """测试错误处理"""
        print("\n" + "=" * 50)
        print("⚠️  测试错误处理")
        print("=" * 50)
        
        # 测试不存在文件的处理
        print("📁 测试不存在文件处理...")
        non_existent_file = os.path.join(self.test_data_dir, "不存在的文件.txt")
        file_info = await self.rag._get_file_info_async(non_existent_file)
        print(f"   不存在文件信息: {file_info}")
        
        # 测试删除不存在文档
        print("🗑️  测试删除不存在文档...")
        delete_result = await self.rag.delete_documents_by_source_async(non_existent_file)
        print(f"   删除不存在文档结果: {delete_result}")
        
        # 测试空问题处理
        print("❓ 测试空问题处理...")
        try:
            empty_result = await self.rag.ask_async("")
            print(f"   空问题回答: {empty_result['result'][:50]}...")
        except Exception as e:
            print(f"   空问题异常: {e}")
    
    async def test_memory_usage(self):
        """测试内存使用情况"""
        print("\n" + "=" * 50)
        print("💾 测试内存使用情况")
        print("=" * 50)
        
        import psutil
        import gc
        
        # 获取初始内存使用
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"📊 初始内存使用: {initial_memory:.2f} MB")
        
        # 执行大量操作
        print("🔄 执行大量异步操作...")
        tasks = []
        for i in range(20):
            tasks.append(self.rag.ask_async(f"测试问题 {i}"))
        
        results = await asyncio.gather(*tasks)
        
        # 检查内存使用
        after_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"📊 操作后内存使用: {after_memory:.2f} MB")
        print(f"📈 内存增长: {after_memory - initial_memory:.2f} MB")
        
        # 强制垃圾回收
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"📊 垃圾回收后内存: {final_memory:.2f} MB")
    
    async def cleanup_test_environment(self):
        """清理测试环境"""
        print("\n🧹 清理测试环境...")
        
        # 恢复原始配置
        if self.original_data_path:
            config.DATA_PATH = self.original_data_path
        
        # 删除临时目录
        if self.test_data_dir and os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)
            print(f"🗑️  删除测试目录: {self.test_data_dir}")
        
        # 清理RAG实例
        if self.rag and hasattr(self.rag, 'executor'):
            self.rag.executor.shutdown(wait=True)
        
        print("✅ 测试环境清理完成")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始异步功能全面测试")
        print("=" * 60)
        
        try:
            # 设置测试环境
            await self.setup_test_environment()
            
            # 运行各项测试
            sync_time = await self.test_async_sync()
            parallel_time, serial_time = await self.test_async_qa()
            await self.test_async_file_operations()
            await self.test_concurrent_operations()
            await self.test_error_handling()
            
            # 可选：内存测试（需要psutil）
            try:
                await self.test_memory_usage()
            except ImportError:
                print("⚠️  跳过内存测试（需要安装psutil）")
            
            # 测试总结
            print("\n" + "=" * 60)
            print("📊 异步功能测试总结")
            print("=" * 60)
            print(f"✅ 异步同步耗时: {sync_time:.2f}秒")
            print(f"✅ 串行问答耗时: {serial_time:.2f}秒")
            print(f"✅ 并行问答耗时: {parallel_time:.2f}秒")
            if serial_time > parallel_time:
                improvement = ((serial_time - parallel_time) / serial_time) * 100
                print(f"🚀 并行性能提升: {improvement:.1f}%")
            print("✅ 所有异步功能测试通过！")
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # 清理测试环境
            await self.cleanup_test_environment()


async def main():
    """主测试函数"""
    tester = AsyncFeatureTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    # 运行异步测试
    asyncio.run(main())