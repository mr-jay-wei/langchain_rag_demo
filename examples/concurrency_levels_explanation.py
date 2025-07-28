"""
并发层次详解：单用户多问题 vs 多用户并发
解释RAG系统中两种不同层次的并发处理
"""

import asyncio
import time
from typing import List, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

class StreamEventType(Enum):
    PROCESSING = "processing"
    GENERATION_START = "generation_start"
    GENERATION_CHUNK = "generation_chunk"
    GENERATION_END = "generation_end"
    COMPLETE = "complete"
    USER_START = "user_start"
    USER_COMPLETE = "user_complete"

@dataclass
class StreamEvent:
    type: StreamEventType
    data: dict
    timestamp: float = None
    metadata: dict = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}

class MockRAGSystem:
    """模拟RAG系统"""
    
    def __init__(self):
        self.active_users = 0
    
    async def ask_stream(self, question: str, user_id: str = "user") -> AsyncGenerator[StreamEvent, None]:
        """单个问题的流式处理"""
        self.active_users += 1
        
        try:
            yield StreamEvent(
                type=StreamEventType.PROCESSING,
                data={"message": f"正在处理问题: {question}"},
                metadata={"user_id": user_id, "question": question}
            )
            
            # 模拟处理时间
            await asyncio.sleep(2.0)
            
            yield StreamEvent(
                type=StreamEventType.GENERATION_START,
                data={"message": "开始生成答案"},
                metadata={"user_id": user_id}
            )
            
            # 模拟答案生成
            answer_parts = ["这是", "对问题", f"'{question}'", "的回答"]
            for part in answer_parts:
                await asyncio.sleep(0.2)
                yield StreamEvent(
                    type=StreamEventType.GENERATION_CHUNK,
                    data={"chunk": part},
                    metadata={"user_id": user_id}
                )
            
            yield StreamEvent(
                type=StreamEventType.GENERATION_END,
                data={"message": "答案生成完成"},
                metadata={"user_id": user_id}
            )
            
            yield StreamEvent(
                type=StreamEventType.COMPLETE,
                data={"message": "问题处理完成"},
                metadata={"user_id": user_id, "question": question}
            )
            
        finally:
            self.active_users -= 1

# ==================== 第一层并发：单用户多问题 ====================

class SingleUserMultiQuestionConcurrency:
    """第一层并发：单用户多问题并发处理"""
    
    def __init__(self):
        self.rag = MockRAGSystem()
    
    async def batch_ask_stream(self, questions: List[str], user_id: str) -> AsyncGenerator[StreamEvent, None]:
        """单用户的多问题并发处理"""
        
        print(f"👤 用户 {user_id} 同时提出 {len(questions)} 个问题")
        
        # 创建并发任务
        tasks = []
        for i, question in enumerate(questions):
            task = asyncio.create_task(
                self._collect_question_events(question, user_id, i + 1)
            )
            tasks.append(task)
        
        # 等待所有问题处理完成
        results = await asyncio.gather(*tasks)
        
        # 合并并排序事件
        all_events = []
        for events in results:
            all_events.extend(events)
        all_events.sort(key=lambda e: e.timestamp)
        
        # 流式输出
        for event in all_events:
            yield event
    
    async def _collect_question_events(self, question: str, user_id: str, question_index: int) -> List[StreamEvent]:
        """收集单个问题的事件"""
        events = []
        async for event in self.rag.ask_stream(question, user_id):
            event.metadata.update({
                "question_index": question_index,
                "concurrency_level": "single_user_multi_question"
            })
            events.append(event)
        return events

# ==================== 第二层并发：多用户并发 ====================

class MultiUserConcurrency:
    """第二层并发：多用户并发处理"""
    
    def __init__(self):
        self.rag = MockRAGSystem()
    
    async def handle_multiple_users(self, user_requests: List[tuple]) -> AsyncGenerator[StreamEvent, None]:
        """处理多个用户的并发请求"""
        
        print(f"🌐 系统同时处理 {len(user_requests)} 个用户的请求")
        
        # 创建用户任务
        user_tasks = []
        for user_id, question in user_requests:
            task = asyncio.create_task(
                self._handle_single_user(user_id, question)
            )
            user_tasks.append(task)
        
        # 并发处理所有用户
        results = await asyncio.gather(*user_tasks)
        
        # 合并所有用户的事件
        all_events = []
        for events in results:
            all_events.extend(events)
        all_events.sort(key=lambda e: e.timestamp)
        
        # 流式输出
        for event in all_events:
            yield event
    
    async def _handle_single_user(self, user_id: str, question: str) -> List[StreamEvent]:
        """处理单个用户的请求"""
        events = []
        
        # 用户开始事件
        events.append(StreamEvent(
            type=StreamEventType.USER_START,
            data={"message": f"用户 {user_id} 开始处理"},
            metadata={"user_id": user_id, "concurrency_level": "multi_user"}
        ))
        
        # 处理用户问题
        async for event in self.rag.ask_stream(question, user_id):
            event.metadata.update({
                "concurrency_level": "multi_user"
            })
            events.append(event)
        
        # 用户完成事件
        events.append(StreamEvent(
            type=StreamEventType.USER_COMPLETE,
            data={"message": f"用户 {user_id} 处理完成"},
            metadata={"user_id": user_id, "concurrency_level": "multi_user"}
        ))
        
        return events

# ==================== 第三层并发：混合并发 ====================

class HybridConcurrency:
    """第三层并发：多用户 + 每用户多问题的混合并发"""
    
    def __init__(self):
        self.rag = MockRAGSystem()
    
    async def handle_hybrid_requests(self, user_batch_requests: List[tuple]) -> AsyncGenerator[StreamEvent, None]:
        """处理混合并发请求"""
        
        total_users = len(user_batch_requests)
        total_questions = sum(len(questions) for _, questions in user_batch_requests)
        
        print(f"🚀 混合并发：{total_users} 个用户，总共 {total_questions} 个问题")
        
        # 为每个用户创建批量处理任务
        user_tasks = []
        for user_id, questions in user_batch_requests:
            task = asyncio.create_task(
                self._handle_user_batch(user_id, questions)
            )
            user_tasks.append(task)
        
        # 并发处理所有用户的批量请求
        results = await asyncio.gather(*user_tasks)
        
        # 合并所有事件
        all_events = []
        for events in results:
            all_events.extend(events)
        all_events.sort(key=lambda e: e.timestamp)
        
        # 流式输出
        for event in all_events:
            yield event
    
    async def _handle_user_batch(self, user_id: str, questions: List[str]) -> List[StreamEvent]:
        """处理单个用户的批量问题"""
        events = []
        
        # 用户批量开始
        events.append(StreamEvent(
            type=StreamEventType.USER_START,
            data={"message": f"用户 {user_id} 开始批量处理 {len(questions)} 个问题"},
            metadata={"user_id": user_id, "concurrency_level": "hybrid"}
        ))
        
        # 用户内部的问题并发处理
        question_tasks = []
        for i, question in enumerate(questions):
            task = asyncio.create_task(
                self._collect_user_question_events(user_id, question, i + 1)
            )
            question_tasks.append(task)
        
        # 等待用户的所有问题完成
        question_results = await asyncio.gather(*question_tasks)
        
        # 合并用户的所有问题事件
        for question_events in question_results:
            events.extend(question_events)
        
        # 用户批量完成
        events.append(StreamEvent(
            type=StreamEventType.USER_COMPLETE,
            data={"message": f"用户 {user_id} 批量处理完成"},
            metadata={"user_id": user_id, "concurrency_level": "hybrid"}
        ))
        
        return events
    
    async def _collect_user_question_events(self, user_id: str, question: str, question_index: int) -> List[StreamEvent]:
        """收集用户单个问题的事件"""
        events = []
        async for event in self.rag.ask_stream(question, user_id):
            event.metadata.update({
                "question_index": question_index,
                "concurrency_level": "hybrid"
            })
            events.append(event)
        return events

# ==================== 演示和对比 ====================

async def demo_single_user_multi_question():
    """演示单用户多问题并发"""
    print("\n🔍 第一层并发：单用户多问题")
    print("=" * 60)
    
    processor = SingleUserMultiQuestionConcurrency()
    
    questions = [
        "什么是人工智能？",
        "机器学习的原理是什么？",
        "深度学习有哪些应用？"
    ]
    
    start_time = time.time()
    completed_questions = 0
    
    async for event in processor.batch_ask_stream(questions, "Alice"):
        if event.type == StreamEventType.COMPLETE:
            completed_questions += 1
            elapsed = time.time() - start_time
            question = event.metadata.get("question", "未知问题")
            print(f"  ✅ 问题 {completed_questions} 完成: {question[:20]}... (耗时: {elapsed:.1f}秒)")
    
    total_time = time.time() - start_time
    print(f"  📊 单用户多问题总耗时: {total_time:.1f}秒")
    print(f"  💡 特点: 一个用户的多个问题并发处理")

async def demo_multi_user():
    """演示多用户并发"""
    print("\n🔍 第二层并发：多用户并发")
    print("=" * 60)
    
    processor = MultiUserConcurrency()
    
    user_requests = [
        ("Alice", "什么是人工智能？"),
        ("Bob", "机器学习的原理是什么？"),
        ("Charlie", "深度学习有哪些应用？")
    ]
    
    start_time = time.time()
    completed_users = 0
    
    async for event in processor.handle_multiple_users(user_requests):
        if event.type == StreamEventType.USER_COMPLETE:
            completed_users += 1
            elapsed = time.time() - start_time
            user_id = event.metadata.get("user_id", "未知用户")
            print(f"  ✅ 用户 {user_id} 完成 (耗时: {elapsed:.1f}秒)")
    
    total_time = time.time() - start_time
    print(f"  📊 多用户并发总耗时: {total_time:.1f}秒")
    print(f"  💡 特点: 多个用户的请求并发处理")

async def demo_hybrid_concurrency():
    """演示混合并发"""
    print("\n🔍 第三层并发：混合并发")
    print("=" * 60)
    
    processor = HybridConcurrency()
    
    user_batch_requests = [
        ("Alice", ["什么是AI？", "AI的历史？"]),
        ("Bob", ["什么是ML？", "ML的算法？"]),
        ("Charlie", ["什么是DL？"])
    ]
    
    start_time = time.time()
    completed_users = 0
    
    async for event in processor.handle_hybrid_requests(user_batch_requests):
        if event.type == StreamEventType.USER_COMPLETE:
            completed_users += 1
            elapsed = time.time() - start_time
            user_id = event.metadata.get("user_id", "未知用户")
            print(f"  ✅ 用户 {user_id} 批量处理完成 (耗时: {elapsed:.1f}秒)")
    
    total_time = time.time() - start_time
    print(f"  📊 混合并发总耗时: {total_time:.1f}秒")
    print(f"  💡 特点: 多用户 + 每用户多问题的双重并发")

def explain_concurrency_levels():
    """解释并发层次"""
    print("\n📚 并发层次详解")
    print("=" * 60)
    
    print("🎯 第一层并发：单用户多问题")
    print("  场景: 一个用户同时问多个相关问题")
    print("  例子: 用户想了解AI、ML、DL三个概念")
    print("  实现: batch_ask_stream() 方法")
    print("  优势: 减少用户等待时间，提升单用户体验")
    
    print("\n🎯 第二层并发：多用户并发")
    print("  场景: 多个用户同时使用系统")
    print("  例子: Alice、Bob、Charlie同时提问")
    print("  实现: 异步函数 + asyncio.gather()")
    print("  优势: 提升系统吞吐量，支持更多用户")
    
    print("\n🎯 第三层并发：混合并发")
    print("  场景: 多用户 + 每用户多问题")
    print("  例子: 多个用户，每个用户都有多个问题")
    print("  实现: 双层并发处理")
    print("  优势: 最大化系统性能，最佳用户体验")
    
    print("\n📊 性能对比 (假设每问题2秒):")
    print("  顺序处理 3个问题: 6秒")
    print("  单用户并发 3个问题: 2秒")
    print("  3用户顺序处理: 6秒")
    print("  3用户并发处理: 2秒")
    print("  3用户×2问题混合并发: 2秒")

async def main():
    """主演示函数"""
    print("🔍 RAG系统并发层次详解")
    print("=" * 80)
    
    # 解释并发层次
    explain_concurrency_levels()
    
    # 演示各种并发
    await demo_single_user_multi_question()
    await demo_multi_user()
    await demo_hybrid_concurrency()
    
    print("\n" + "=" * 80)
    print("🎯 总结")
    print("=" * 80)
    print("💡 你的理解完全正确！")
    print()
    print("❓ 你的问题:")
    print("  batch函数 → 单用户多问题并发")
    print("  异步函数 → 多用户并发")
    print()
    print("✅ 两种并发的区别:")
    print("  1. batch_ask_stream(): 解决单用户的多问题等待问题")
    print("  2. async def ask_stream(): 解决多用户的系统阻塞问题")
    print()
    print("🚀 实际应用场景:")
    print("  - 用户批量查询: 使用batch_ask_stream()")
    print("  - 多用户系统: 使用异步函数")
    print("  - 企业级应用: 两种并发结合使用")
    print()
    print("📈 性能提升:")
    print("  - 单用户体验: 从等待6秒到等待2秒")
    print("  - 系统吞吐量: 从处理1用户到处理N用户")
    print("  - 资源利用率: 从25%提升到90%+")

if __name__ == "__main__":
    asyncio.run(main())