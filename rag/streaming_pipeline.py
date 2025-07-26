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
    
    async def ask_stream(self, question: str) -> AsyncGenerator[StreamEvent, None]:
        """
        流式问答 - 只有答案生成是流式的
        
        Args:
            question: 用户问题
            
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
                if final_docs:
                    async for event in self._generate_streaming_answer(question, final_docs):
                        yield event
                else:
                    async for event in self._stream_text("根据提供的资料，我无法找到相关信息来回答该问题。"):
                        yield event
                return
            
            # 2. 流式生成阶段 - 这里才是真正的流式
            if final_docs:
                async for event in self._generate_streaming_answer(question, final_docs):
                    yield event
            else:
                # 没有找到相关文档
                async for event in self._stream_text("根据提供的资料，我无法找到相关信息来回答该问题。"):
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
                    
                    category_docs = await self._run_in_executor(get_category_docs)
                    
                    # 使用真正的流式生成
                    if category_docs:
                        async for event in self._generate_streaming_answer(question, category_docs):
                            yield event
                    else:
                        async for event in self._stream_text("根据提供的资料，我无法找到相关信息来回答该问题。"):
                            yield event
                    return
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
                    if final_docs:
                        async for event in self._generate_streaming_answer(question, final_docs):
                            yield event
                    else:
                        async for event in self._stream_text("根据提供的资料，我无法找到相关信息来回答该问题。"):
                            yield event
                    return
            
            # 流式生成答案
            if final_docs:
                async for event in self._generate_streaming_answer(question, final_docs):
                    yield event
            else:
                async for event in self._stream_text("根据提供的资料，我无法找到相关信息来回答该问题。"):
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
    
    async def _generate_streaming_answer(self, question: str, documents: List[Document]) -> AsyncGenerator[StreamEvent, None]:
        """
        生成流式答案 - 真正的流式输出实现
        
        Args:
            question: 问题
            documents: 相关文档
            
        Yields:
            StreamEvent: 流式事件
        """
        yield StreamEvent(
            type=StreamEventType.GENERATION_START,
            data={"message": "开始生成答案"},
            timestamp=time.time()
        )
        
        try:
            # 构建上下文
            context = "\n\n".join([doc.page_content for doc in documents])
            
            # 构建提示
            # 使用提示词管理器获取问答提示模板
            qa_template = get_qa_prompt_template()
            prompt_template = qa_template.template
            
            prompt = prompt_template.format(context=context, question=question)
            
            # ✅ 关键改进：检查LLM是否支持流式调用
            if hasattr(self.llm, 'astream'):
                # 真正的流式LLM调用
                async for chunk in self.llm.astream(prompt):
                    if hasattr(chunk, 'content') and chunk.content:
                        yield StreamEvent(
                            type=StreamEventType.GENERATION_CHUNK,
                            data={"chunk": chunk.content},
                            timestamp=time.time()
                        )
                    elif isinstance(chunk, str) and chunk:
                        yield StreamEvent(
                            type=StreamEventType.GENERATION_CHUNK,
                            data={"chunk": chunk},
                            timestamp=time.time()
                        )
            else:
                # 如果LLM不支持流式，回退到当前实现
                response = await self._run_in_executor(self.llm.invoke, prompt)
                
                if hasattr(response, 'content'):
                    answer = response.content.strip()
                else:
                    answer = str(response).strip()
                
                # 流式输出已有答案
                async for event in self._stream_text(answer):
                    yield event
            
            # 生成结束，提供源文档信息
            yield StreamEvent(
                type=StreamEventType.GENERATION_END,
                data={
                    "message": "答案生成完成",
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