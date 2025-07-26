"""
并发批量流式处理演示
对比顺序处理 vs 并发处理的性能差异
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
    BATCH_START = "batch_start"
    BATCH_COMPLETE = "batch_complete"

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

class MockRAGPipeline:
    """模拟RAG管道"""
    
    async def ask_stream(self, question: str) -> AsyncGenerator[StreamEvent, None]:
        """模拟单个问题的流式处理"""
        
        # 模拟处理时间
        processing_time = 2.0  # 每个问题2秒
        
        yield StreamEvent(
            type=StreamEventType.PROCESSING,
            data={"message": f"正在处理: {question}"}
        )
        
        yield StreamEvent(
            type=StreamEventType.GENERATION_START,
            data={"message": "开始生成答案"}
        )
        
        # 模拟流式生成
        answer_parts = ["这是", "对问题", f"'{question}'", "的回答"]
        for part in answer_parts:
            await asyncio.sleep(processing_time / len(answer_parts))
            yield StreamEvent(
                type=StreamEventType.GENERATION_CHUNK,
                data={"chunk": part}
            )
        
        yield StreamEvent(
            type=StreamEventType.GENERATION_END,
            data={"message": "答案生成完成"}
        )
        
        yield StreamEvent(
            type=StreamEventType.COMPLETE,
            data={"message": "问题处理完成"}
        )

# ==================== 顺序处理版本 ====================

class SequentialBatchProcessor:
    """顺序批量处理器"""
    
    def __init__(self):
        self.rag = MockRAGPipeline()
    
    async def batch_ask_stream(self, questions: List[str]) -> AsyncGenerator[StreamEvent, None]:
        """❌ 顺序处理版本（当前实现）"""
        
        yield StreamEvent(
            type=StreamEventType.BATCH_START,
            data={"message": f"开始顺序处理 {len(questions)} 个问题"}
        )
        
        for i, question in enumerate(questions):
            yield StreamEvent(
                type=StreamEventType.PROCESSING,
                data={
                    "message": f"处理第 {i+1}/{len(questions)} 个问题: {question}",
                    "question_index": i + 1,
                    "total_questions": len(questions)
                }
            )
            
            # ❌ 顺序处理：等待当前问题完全完成
            async for event in self.rag.ask_stream(question):
                event.metadata.update({
                    "batch_index": i + 1,
                    "batch_total": len(questions),
                    "batch_question": question,
                    "processing_mode": "sequential"
                })
                yield event
        
        yield StreamEvent(
            type=StreamEventType.BATCH_COMPLETE,
            data={
                "message": f"顺序处理完成，共处理 {len(questions)} 个问题",
                "total_processed": len(questions)
            }
        )

# ==================== 并发处理版本 ====================

class ConcurrentBatchProcessor:
    """并发批量处理器"""
    
    def __init__(self):
        self.rag = MockRAGPipeline()
    
    async def batch_ask_stream(self, questions: List[str]) -> AsyncGenerator[StreamEvent, None]:
        """✅ 并发处理版本（优化实现）"""
        
        yield StreamEvent(
            type=StreamEventType.BATCH_START,
            data={"message": f"开始并发处理 {len(questions)} 个问题"}
        )
        
        # 创建并发任务
        tasks = []
        for i, question in enumerate(questions):
            task = asyncio.create_task(
                self._process_single_question(question, i + 1, len(questions))
            )
            tasks.append(task)
        
        # 使用队列来收集所有任务的事件
        event_queue = asyncio.Queue()
        
        # 启动事件收集器
        async def collect_events(task, question_index):
            async for event in await task:
                await event_queue.put((question_index, event))
        
        # 为每个任务启动事件收集器
        collectors = []
        for i, task in enumerate(tasks):
            collector = asyncio.create_task(collect_events(task, i + 1))
            collectors.append(collector)
        
        # 等待所有收集器完成的任务
        completion_task = asyncio.create_task(self._wait_for_completion(collectors, event_queue))
        
        # 流式输出事件
        completed_questions = 0
        while completed_questions < len(questions):
            try:
                question_index, event = await asyncio.wait_for(event_queue.get(), timeout=0.1)
                
                # 添加批量处理元数据
                event.metadata.update({
                    "batch_index": question_index,
                    "batch_total": len(questions),
                    "processing_mode": "concurrent"
                })
                
                yield event
                
                # 检查是否是完成事件
                if event.type == StreamEventType.COMPLETE:
                    completed_questions += 1
                    
            except asyncio.TimeoutError:
                # 检查是否所有任务都完成了
                if all(task.done() for task in tasks):
                    break
                continue
        
        # 等待清理
        await completion_task
        
        yield StreamEvent(
            type=StreamEventType.BATCH_COMPLETE,
            data={
                "message": f"并发处理完成，共处理 {len(questions)} 个问题",
                "total_processed": len(questions)
            }
        )
    
    async def _process_single_question(self, question: str, index: int, total: int) -> AsyncGenerator[StreamEvent, None]:
        """处理单个问题"""
        async for event in self.rag.ask_stream(question):
            event.metadata.update({
                "question_index": index,
                "question": question
            })
            yield event
    
    async def _wait_for_completion(self, collectors, event_queue):
        """等待所有收集器完成"""
        await asyncio.gather(*collectors)
        await event_queue.put((0, None))  # 结束信号

# ==================== 简化的并发版本 ====================

class SimpleConcurrentBatchProcessor:
    """简化的并发批量处理器"""
    
    def __init__(self):
        self.rag = MockRAGPipeline()
    
    async def batch_ask_stream(self, questions: List[str]) -> AsyncGenerator[StreamEvent, None]:
        """✅ 简化的并发处理版本"""
        
        yield StreamEvent(
            type=StreamEventType.BATCH_START,
            data={"message": f"开始并发处理 {len(questions)} 个问题"}
        )
        
        # 创建所有任务
        tasks = [
            asyncio.create_task(self._collect_question_events(question, i + 1, len(questions)))
            for i, question in enumerate(questions)
        ]
        
        # 并发执行并收集结果
        async for event in self._merge_concurrent_streams(tasks):
            yield event
        
        yield StreamEvent(
            type=StreamEventType.BATCH_COMPLETE,
            data={
                "message": f"并发处理完成，共处理 {len(questions)} 个问题",
                "total_processed": len(questions)
            }
        )
    
    async def _collect_question_events(self, question: str, index: int, total: int) -> List[StreamEvent]:
        """收集单个问题的所有事件"""
        events = []
        async for event in self.rag.ask_stream(question):
            event.metadata.update({
                "batch_index": index,
                "batch_total": total,
                "batch_question": question,
                "processing_mode": "concurrent"
            })
            events.append(event)
        return events
    
    async def _merge_concurrent_streams(self, tasks) -> AsyncGenerator[StreamEvent, None]:
        """合并并发流的事件"""
        # 等待所有任务完成
        results = await asyncio.gather(*tasks)
        
        # 按时间戳排序所有事件
        all_events = []
        for events in results:
            all_events.extend(events)
        
        # 按时间戳排序
        all_events.sort(key=lambda e: e.timestamp)
        
        # 流式输出
        for event in all_events:
            yield event

# ==================== 性能测试 ====================

async def performance_comparison():
    """性能对比测试"""
    print("🔍 批量处理性能对比")
    print("=" * 80)
    
    questions = [
        "什么是人工智能？",
        "机器学习的原理是什么？",
        "深度学习有哪些应用？"
    ]
    
    print(f"测试问题数量: {len(questions)}")
    print(f"每个问题预计处理时间: 2秒")
    print()
    
    # 测试顺序处理
    print("1. 顺序处理测试:")
    print("-" * 40)
    
    sequential_processor = SequentialBatchProcessor()
    start_time = time.time()
    
    question_count = 0
    async for event in sequential_processor.batch_ask_stream(questions):
        if event.type == StreamEventType.COMPLETE:
            question_count += 1
            elapsed = time.time() - start_time
            print(f"   问题 {question_count} 完成，耗时: {elapsed:.1f}秒")
        elif event.type == StreamEventType.BATCH_COMPLETE:
            total_time = time.time() - start_time
            print(f"   顺序处理总耗时: {total_time:.1f}秒")
    
    print()
    
    # 测试并发处理
    print("2. 并发处理测试:")
    print("-" * 40)
    
    concurrent_processor = SimpleConcurrentBatchProcessor()
    start_time = time.time()
    
    question_count = 0
    async for event in concurrent_processor.batch_ask_stream(questions):
        if event.type == StreamEventType.COMPLETE:
            question_count += 1
            elapsed = time.time() - start_time
            print(f"   问题 {question_count} 完成，耗时: {elapsed:.1f}秒")
        elif event.type == StreamEventType.BATCH_COMPLETE:
            concurrent_time = time.time() - start_time
            print(f"   并发处理总耗时: {concurrent_time:.1f}秒")
    
    # 性能对比
    print("\n📊 性能对比:")
    print("-" * 40)
    print(f"顺序处理: {total_time:.1f}秒")
    print(f"并发处理: {concurrent_time:.1f}秒")
    print(f"性能提升: {total_time/concurrent_time:.1f}倍")
    print(f"时间节省: {total_time - concurrent_time:.1f}秒")

async def main():
    """主演示函数"""
    
    await performance_comparison()
    
    print("\n" + "=" * 80)
    print("🎯 总结")
    print("=" * 80)
    print("❌ 当前的 batch_ask_stream 实现问题:")
    print("  1. 顺序处理，性能低下")
    print("  2. 无法充分利用异步优势")
    print("  3. 用户等待时间过长")
    
    print("\n✅ 并发处理的优势:")
    print("  1. 多个问题同时处理")
    print("  2. 充分利用系统资源")
    print("  3. 显著减少总处理时间")
    print("  4. 更好的用户体验")
    
    print("\n🚀 建议的改进:")
    print("  1. 实现真正的并发批量处理")
    print("  2. 使用 asyncio.gather 或 asyncio.create_task")
    print("  3. 合理处理并发事件流")
    print("  4. 添加并发数量限制（避免资源耗尽）")

if __name__ == "__main__":
    asyncio.run(main())