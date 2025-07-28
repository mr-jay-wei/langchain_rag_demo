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