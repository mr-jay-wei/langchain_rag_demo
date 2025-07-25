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