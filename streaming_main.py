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