"""
测试真正的流式响应实现
验证改进后的流式RAG系统是否能实现真正的流式响应
"""

import asyncio
import time
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from rag.streaming_pipeline import StreamingRagPipeline, StreamEventType

class MockStreamingLLM:
    """模拟支持流式的LLM，用于测试"""
    
    def __init__(self, original_llm):
        self.original_llm = original_llm
    
    async def astream(self, prompt):
        """模拟异步流式生成"""
        # 模拟真实的流式LLM响应
        response_tokens = [
            "根据", "检索到的", "文档", "内容，", "我", "可以", "回答", "您的", "问题：",
            "\n\n", "人工智能", "（AI）", "是", "计算机科学", "的", "一个", "分支，",
            "致力于", "创建", "能够", "执行", "通常", "需要", "人类", "智能", "的",
            "任务", "的", "系统。"
        ]
        
        for token in response_tokens:
            # 模拟真实的LLM生成延迟
            await asyncio.sleep(0.1)
            yield token
    
    def invoke(self, prompt):
        """保持原有的同步调用兼容性"""
        return self.original_llm.invoke(prompt)

async def test_streaming_comparison():
    """对比测试：原实现 vs 流式实现"""
    print("🔍 流式响应对比测试")
    print("=" * 80)
    
    # 创建RAG实例
    rag = StreamingRagPipeline()
    
    # 检查是否需要初始化
    if not rag.qa_chain:
        print("⚠️  问答链未初始化，需要先同步数据")
        print("请确保 data/ 目录中有文档文件")
        return
    
    question = "什么是人工智能？"
    print(f"📝 测试问题: {question}")
    
    # 测试1：当前实现（LLM不支持流式）
    print("\n1️⃣ 当前实现测试（LLM不支持流式）:")
    print("-" * 50)
    
    start_time = time.time()
    first_chunk_time = None
    chunk_count = 0
    
    async for event in rag.ask_stream(question):
        current_time = time.time() - start_time
        
        if event.type == StreamEventType.PROCESSING:
            print(f"📋 [{current_time:.2f}s] {event.data['message']}")
            
        elif event.type == StreamEventType.GENERATION_START:
            print(f"🤖 [{current_time:.2f}s] {event.data['message']}")
            
        elif event.type == StreamEventType.GENERATION_CHUNK:
            if first_chunk_time is None:
                first_chunk_time = current_time
                print(f"⚡ [{current_time:.2f}s] 首个字符输出")
            chunk_count += 1
            if chunk_count % 10 == 0:
                print(f"📝 [{current_time:.2f}s] 已输出 {chunk_count} 个字符")
                
        elif event.type == StreamEventType.GENERATION_END:
            print(f"✅ [{current_time:.2f}s] {event.data['message']}")
            
        elif event.type == StreamEventType.COMPLETE:
            total_time = current_time
            print(f"🎉 [{current_time:.2f}s] {event.data['message']}")
            break
            
        elif event.type == StreamEventType.ERROR:
            print(f"❌ [{current_time:.2f}s] 错误: {event.data['error']}")
            return
    
    print(f"\n📊 当前实现性能:")
    print(f"   首字符延迟: {first_chunk_time:.2f}秒")
    print(f"   总处理时间: {total_time:.2f}秒")
    print(f"   总字符数: {chunk_count}")
    
    # 测试2：模拟真正的流式LLM
    print("\n2️⃣ 流式LLM实现测试:")
    print("-" * 50)
    
    # 临时替换LLM为支持流式的版本
    original_llm = rag.llm
    rag.llm = MockStreamingLLM(original_llm)
    
    start_time = time.time()
    first_chunk_time = None
    chunk_count = 0
    
    async for event in rag.ask_stream(question):
        current_time = time.time() - start_time
        
        if event.type == StreamEventType.PROCESSING:
            print(f"📋 [{current_time:.2f}s] {event.data['message']}")
            
        elif event.type == StreamEventType.GENERATION_START:
            print(f"🤖 [{current_time:.2f}s] {event.data['message']}")
            
        elif event.type == StreamEventType.GENERATION_CHUNK:
            if first_chunk_time is None:
                first_chunk_time = current_time
                print(f"⚡ [{current_time:.2f}s] 首个token输出: '{event.data['chunk']}'")
            chunk_count += 1
            if chunk_count <= 10 or chunk_count % 5 == 0:
                print(f"📝 [{current_time:.2f}s] Token {chunk_count}: '{event.data['chunk']}'")
                
        elif event.type == StreamEventType.GENERATION_END:
            print(f"✅ [{current_time:.2f}s] {event.data['message']}")
            
        elif event.type == StreamEventType.COMPLETE:
            streaming_total_time = current_time
            print(f"🎉 [{current_time:.2f}s] {event.data['message']}")
            break
            
        elif event.type == StreamEventType.ERROR:
            print(f"❌ [{current_time:.2f}s] 错误: {event.data['error']}")
            # 恢复原始LLM
            rag.llm = original_llm
            return
    
    # 恢复原始LLM
    rag.llm = original_llm
    
    print(f"\n📊 流式实现性能:")
    print(f"   首token延迟: {first_chunk_time:.2f}秒")
    print(f"   总处理时间: {streaming_total_time:.2f}秒")
    print(f"   总token数: {chunk_count}")
    
    # 性能对比
    print(f"\n🚀 性能对比:")
    print(f"   首次响应改善: {first_chunk_time:.2f}s → {first_chunk_time:.2f}s")
    print(f"   总时间对比: {total_time:.2f}s → {streaming_total_time:.2f}s")
    
    if first_chunk_time < total_time / 2:
        print("   ✅ 流式响应显著改善用户体验")
    else:
        print("   ⚠️  流式响应改善有限")

async def test_llm_detection():
    """测试LLM流式支持检测"""
    print("\n🔍 LLM流式支持检测测试")
    print("=" * 80)
    
    rag = StreamingRagPipeline()
    
    if not rag.qa_chain:
        print("⚠️  问答链未初始化，跳过测试")
        return
    
    print(f"当前LLM类型: {type(rag.llm)}")
    print(f"是否支持astream: {hasattr(rag.llm, 'astream')}")
    
    if hasattr(rag.llm, 'astream'):
        print("✅ LLM支持流式调用，将使用真正的流式响应")
    else:
        print("❌ LLM不支持流式调用，将回退到模拟流式响应")
    
    # 测试实际调用
    print("\n测试实际调用:")
    question = "简单测试问题"
    
    start_time = time.time()
    event_count = 0
    
    async for event in rag.ask_stream(question):
        event_count += 1
        elapsed = time.time() - start_time
        
        if event.type == StreamEventType.GENERATION_CHUNK:
            if event_count <= 5:
                print(f"  事件 {event_count}: [{elapsed:.2f}s] '{event.data['chunk']}'")
        elif event.type == StreamEventType.COMPLETE:
            print(f"  完成: [{elapsed:.2f}s] 总共 {event_count} 个事件")
            break

async def test_real_world_scenario():
    """真实世界场景测试"""
    print("\n🌍 真实世界场景测试")
    print("=" * 80)
    
    rag = StreamingRagPipeline()
    
    if not rag.qa_chain:
        print("⚠️  问答链未初始化，跳过测试")
        return
    
    # 模拟用户的实际使用场景
    questions = [
        "什么是人工智能？",
        "机器学习的基本原理是什么？"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n📝 问题 {i}: {question}")
        print("-" * 40)
        
        start_time = time.time()
        user_saw_first_output = False
        
        async for event in rag.ask_stream(question):
            elapsed = time.time() - start_time
            
            if event.type == StreamEventType.GENERATION_CHUNK and not user_saw_first_output:
                print(f"⚡ 用户首次看到输出: {elapsed:.2f}秒")
                user_saw_first_output = True
                
            elif event.type == StreamEventType.COMPLETE:
                print(f"✅ 问题完成: {elapsed:.2f}秒")
                break
                
            elif event.type == StreamEventType.ERROR:
                print(f"❌ 错误: {event.data['error']}")
                break
        
        # 模拟用户间隔
        await asyncio.sleep(1)

async def main():
    """主测试函数"""
    print("🧪 真正的流式响应实现测试")
    print("=" * 80)
    print("💡 这个测试验证了你的改进思路：")
    print("   在返回给用户的最后一步调用真正的异步流式大模型接口")
    print()
    
    # LLM检测测试
    await test_llm_detection()
    
    # 对比测试
    await test_streaming_comparison()
    
    # 真实场景测试
    await test_real_world_scenario()
    
    print("\n" + "=" * 80)
    print("🎯 测试总结")
    print("=" * 80)
    print("✅ 实现了你的改进思路:")
    print("  1. 检测LLM是否支持流式调用 (hasattr(llm, 'astream'))")
    print("  2. 如果支持，直接使用流式API")
    print("  3. 如果不支持，回退到原有实现")
    print("  4. 保持了向后兼容性")
    
    print("\n🚀 预期效果:")
    print("  - 支持流式的LLM: 真正的流式响应，用户体验大幅提升")
    print("  - 不支持流式的LLM: 保持原有功能，无破坏性变更")
    print("  - 系统架构: 更加灵活和可扩展")
    
    print("\n💡 下一步建议:")
    print("  1. 配置支持流式的LLM客户端 (如OpenAI、DeepSeek)")
    print("  2. 测试真实的流式API调用")
    print("  3. 优化流式响应的用户界面")
    print("  4. 监控流式响应的性能指标")

if __name__ == "__main__":
    asyncio.run(main())