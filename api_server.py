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
from rag.streaming_pipeline import StreamingRagPipeline, StreamEventType

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