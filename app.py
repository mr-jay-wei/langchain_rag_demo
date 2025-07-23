#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI Web 服务 - RAG 系统 API 接口

提供 RESTful API 接口，将 RAG Pipeline 封装为 Web 服务
支持问答查询、知识库管理、系统监控等功能
"""

import os
import time
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

from rag.pipeline import RagPipeline
from rag import config


# ================================
# 数据模型定义
# ================================

class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str = Field(..., description="用户查询问题", max_length=1000)
    categories: Optional[List[str]] = Field(default=None, description="指定搜索的文档类别")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="查询选项")

class QueryOptions(BaseModel):
    """查询选项模型"""
    enable_rewriting: bool = Field(default=True, description="是否启用问题改写")
    enable_hybrid_search: bool = Field(default=True, description="是否启用混合检索")
    max_results: int = Field(default=5, description="最大返回结果数", ge=1, le=20)
    timeout: int = Field(default=30, description="查询超时时间(秒)", ge=5, le=120)

class BatchQueryRequest(BaseModel):
    """批量查询请求模型"""
    queries: List[QueryRequest] = Field(..., description="查询列表", max_items=10)
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="批量查询选项")

class DocumentSource(BaseModel):
    """文档来源模型"""
    content: str = Field(..., description="文档内容片段")
    source: str = Field(..., description="来源文件名")
    category: Optional[str] = Field(default=None, description="文档类别")
    score: float = Field(..., description="相关性评分", ge=0.0, le=1.0)

class QueryResponse(BaseModel):
    """查询响应模型"""
    success: bool = Field(..., description="请求是否成功")
    data: Optional[Dict[str, Any]] = Field(default=None, description="响应数据")
    error: Optional[str] = Field(default=None, description="错误信息")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="响应时间戳")

class KnowledgeStatus(BaseModel):
    """知识库状态模型"""
    total_documents: int = Field(..., description="文档总数")
    categories: Dict[str, int] = Field(..., description="各类别文档数量")
    last_sync: Optional[str] = Field(default=None, description="最后同步时间")
    vector_store_size: str = Field(..., description="向量数据库大小")

class HealthStatus(BaseModel):
    """健康状态模型"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="版本号")
    uptime: int = Field(..., description="运行时间(秒)")
    components: Dict[str, str] = Field(..., description="组件状态")


# ================================
# 全局变量和初始化
# ================================

# 服务启动时间
SERVICE_START_TIME = time.time()

# RAG Pipeline 实例
rag_pipeline: Optional[RagPipeline] = None

# 服务统计信息
service_stats = {
    "queries_total": 0,
    "queries_success": 0,
    "queries_error": 0,
    "total_response_time": 0.0,
    "last_query_time": None
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global rag_pipeline
    
    print("🚀 正在启动 RAG Web 服务...")
    
    # 初始化 RAG Pipeline
    try:
        rag_pipeline = RagPipeline()
        print("✅ RAG Pipeline 初始化成功")
    except Exception as e:
        print(f"❌ RAG Pipeline 初始化失败: {e}")
        raise
    
    print("🌐 RAG Web 服务启动完成!")
    print(f"📖 API 文档: http://localhost:8000/docs")
    print(f"🔍 ReDoc: http://localhost:8000/redoc")
    
    yield
    
    print("🛑 正在关闭 RAG Web 服务...")


# ================================
# FastAPI 应用初始化
# ================================

app = FastAPI(
    title="RAG 系统 API",
    description="企业级检索增强生成(RAG)系统的 Web API 接口",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================================
# 辅助函数
# ================================

def update_stats(success: bool, response_time: float):
    """更新服务统计信息"""
    global service_stats
    service_stats["queries_total"] += 1
    service_stats["total_response_time"] += response_time
    service_stats["last_query_time"] = datetime.now().isoformat()
    
    if success:
        service_stats["queries_success"] += 1
    else:
        service_stats["queries_error"] += 1

def get_file_size_str(path: str) -> str:
    """获取文件大小的字符串表示"""
    if not os.path.exists(path):
        return "0B"
    
    size = sum(
        os.path.getsize(os.path.join(dirpath, filename))
        for dirpath, dirnames, filenames in os.walk(path)
        for filename in filenames
    )
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}TB"


# ================================
# API 路由定义
# ================================

@app.get("/", summary="根路径", description="服务基本信息")
async def root():
    """根路径 - 返回服务基本信息"""
    return {
        "service": "RAG 系统 API",
        "version": "4.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.post("/api/v1/ask", response_model=QueryResponse, summary="问答查询", description="核心问答接口")
async def ask_question(request: QueryRequest):
    """
    核心问答接口
    
    支持以下功能:
    - 智能问答查询
    - 分类检索
    - 混合检索
    - 问题改写
    """
    start_time = time.time()
    
    try:
        if not rag_pipeline:
            # 返回友好的错误信息而不是抛出异常
            response_time = time.time() - start_time
            update_stats(False, response_time)
            
            return QueryResponse(
                success=False,
                error="RAG Pipeline 未初始化，请稍后重试或联系管理员",
                data={
                    "answer": "抱歉，系统正在初始化中，请稍后重试。",
                    "query_info": {
                        "original_query": request.query,
                        "categories": request.categories,
                        "search_time": round(time.time() - start_time, 2),
                        "status": "pipeline_not_ready"
                    }
                }
            )
        
        # 解析查询选项
        options = request.options or {}
        
        # 执行查询
        if request.categories:
            # 分类查询
            result = rag_pipeline.ask_with_categories(
                query=request.query,
                categories=request.categories
            )
        else:
            # 普通查询
            result = rag_pipeline.ask(request.query)
        
        # 构建响应数据
        response_data = {
            "answer": result,
            "query_info": {
                "original_query": request.query,
                "categories": request.categories,
                "search_time": round(time.time() - start_time, 2),
                "options": options,
                "status": "success"
            }
        }
        
        # 更新统计信息
        response_time = time.time() - start_time
        update_stats(True, response_time)
        
        return QueryResponse(
            success=True,
            data=response_data
        )
        
    except Exception as e:
        # 更新统计信息
        response_time = time.time() - start_time
        update_stats(False, response_time)
        
        # 返回更友好的错误响应
        return QueryResponse(
            success=False,
            error=f"查询处理失败: {str(e)}",
            data={
                "answer": "抱歉，处理您的查询时出现了问题，请稍后重试。",
                "query_info": {
                    "original_query": request.query,
                    "categories": request.categories,
                    "search_time": round(time.time() - start_time, 2),
                    "status": "error"
                }
            }
        )


@app.post("/api/v1/ask/batch", response_model=QueryResponse, summary="批量查询", description="批量问答接口")
async def ask_batch(request: BatchQueryRequest):
    """
    批量问答接口
    
    支持同时处理多个查询请求
    """
    start_time = time.time()
    
    try:
        if not rag_pipeline:
            raise HTTPException(status_code=503, detail="RAG Pipeline 未初始化")
        
        results = []
        
        for query_req in request.queries:
            try:
                if query_req.categories:
                    result = rag_pipeline.ask_with_categories(
                        query=query_req.query,
                        categories=query_req.categories
                    )
                else:
                    result = rag_pipeline.ask(query_req.query)
                
                results.append({
                    "query": query_req.query,
                    "answer": result,
                    "success": True,
                    "error": None
                })
                
            except Exception as e:
                results.append({
                    "query": query_req.query,
                    "answer": None,
                    "success": False,
                    "error": str(e)
                })
        
        response_data = {
            "results": results,
            "total_queries": len(request.queries),
            "successful_queries": sum(1 for r in results if r["success"]),
            "total_time": round(time.time() - start_time, 2)
        }
        
        # 更新统计信息
        response_time = time.time() - start_time
        update_stats(True, response_time)
        
        return QueryResponse(
            success=True,
            data=response_data
        )
        
    except Exception as e:
        response_time = time.time() - start_time
        update_stats(False, response_time)
        
        raise HTTPException(status_code=500, detail=f"批量查询处理失败: {str(e)}")


@app.get("/api/v1/knowledge/status", response_model=QueryResponse, summary="知识库状态", description="获取知识库状态信息")
async def get_knowledge_status():
    """获取知识库状态信息"""
    try:
        # 如果 RAG Pipeline 未初始化，返回基本信息
        if not rag_pipeline:
            return QueryResponse(
                success=True,
                data={
                    "total_documents": 0,
                    "categories": {},
                    "last_sync": None,
                    "vector_store_size": "0B",
                    "status": "pipeline_not_initialized"
                }
            )
        
        # 获取知识库统计信息
        categories = {}
        total_docs = 0
        
        try:
            if hasattr(rag_pipeline, 'get_available_categories'):
                categories = rag_pipeline.get_available_categories()
                total_docs = sum(categories.values()) if categories else 0
        except Exception as e:
            print(f"获取类别信息失败: {e}")
            categories = {}
            total_docs = 0
        
        # 获取向量数据库大小
        try:
            vector_store_path = getattr(config, 'VECTOR_STORE_PATH', './my_chromadb_vector_store')
            vector_store_size = get_file_size_str(vector_store_path)
        except Exception as e:
            print(f"获取向量数据库大小失败: {e}")
            vector_store_size = "unknown"
        
        status_data = {
            "total_documents": total_docs,
            "categories": categories,
            "last_sync": None,  # 可以从配置或日志中获取
            "vector_store_size": vector_store_size,
            "status": "ready"
        }
        
        return QueryResponse(
            success=True,
            data=status_data
        )
        
    except Exception as e:
        # 返回错误信息但不抛出异常
        return QueryResponse(
            success=False,
            error=f"获取知识库状态失败: {str(e)}",
            data={
                "total_documents": 0,
                "categories": {},
                "last_sync": None,
                "vector_store_size": "unknown",
                "status": "error"
            }
        )


@app.post("/api/v1/knowledge/sync", response_model=QueryResponse, summary="同步知识库", description="手动触发知识库同步")
async def sync_knowledge_base(background_tasks: BackgroundTasks):
    """手动触发知识库同步"""
    try:
        if not rag_pipeline:
            raise HTTPException(status_code=503, detail="RAG Pipeline 未初始化")
        
        # 在后台执行同步任务
        def sync_task():
            try:
                rag_pipeline.sync_data_directory()
                print("✅ 知识库同步完成")
            except Exception as e:
                print(f"❌ 知识库同步失败: {e}")
        
        background_tasks.add_task(sync_task)
        
        return QueryResponse(
            success=True,
            data={
                "message": "知识库同步任务已启动",
                "status": "running"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动知识库同步失败: {str(e)}")


@app.get("/api/v1/health", response_model=QueryResponse, summary="健康检查", description="服务健康状态检查")
async def health_check():
    """服务健康状态检查"""
    try:
        uptime = int(time.time() - SERVICE_START_TIME)
        
        # 检查各组件状态（更宽松的检查）
        components = {}
        
        # 检查 RAG Pipeline
        if rag_pipeline:
            components["rag_pipeline"] = "healthy"
        else:
            components["rag_pipeline"] = "initializing"
        
        # 检查向量存储路径
        try:
            vector_store_path = getattr(config, 'VECTOR_STORE_PATH', './my_chromadb_vector_store')
            components["vector_store"] = "healthy" if os.path.exists(vector_store_path) else "not_found"
        except:
            components["vector_store"] = "unknown"
        
        # 检查数据目录
        try:
            data_directory = getattr(config, 'DATA_DIRECTORY', './data')
            components["data_directory"] = "healthy" if os.path.exists(data_directory) else "not_found"
        except:
            components["data_directory"] = "unknown"
        
        # 判断整体状态（更宽松的判断）
        critical_components = ["rag_pipeline"]
        overall_status = "healthy"
        
        for component in critical_components:
            if components.get(component) == "unhealthy":
                overall_status = "unhealthy"
                break
        
        if components.get("rag_pipeline") == "initializing":
            overall_status = "initializing"
        
        health_data = {
            "status": overall_status,
            "version": "4.0.0",
            "uptime": uptime,
            "components": components
        }
        
        return QueryResponse(
            success=True,
            data=health_data
        )
        
    except Exception as e:
        # 即使出错也返回基本信息，而不是抛出异常
        return QueryResponse(
            success=False,
            error=f"健康检查部分失败: {str(e)}",
            data={
                "status": "error",
                "version": "4.0.0",
                "uptime": int(time.time() - SERVICE_START_TIME),
                "components": {"error": str(e)}
            }
        )


@app.get("/api/v1/metrics", response_model=QueryResponse, summary="服务指标", description="获取服务运行指标")
async def get_metrics():
    """获取服务运行指标"""
    try:
        # 计算平均响应时间
        avg_response_time = 0.0
        if service_stats["queries_total"] > 0:
            avg_response_time = service_stats["total_response_time"] / service_stats["queries_total"]
        
        # 计算错误率
        error_rate = 0.0
        if service_stats["queries_total"] > 0:
            error_rate = service_stats["queries_error"] / service_stats["queries_total"]
        
        metrics_data = {
            "queries_total": service_stats["queries_total"],
            "queries_success": service_stats["queries_success"],
            "queries_error": service_stats["queries_error"],
            "average_response_time": round(avg_response_time, 2),
            "error_rate": round(error_rate, 4),
            "last_query_time": service_stats["last_query_time"],
            "uptime": int(time.time() - SERVICE_START_TIME)
        }
        
        return QueryResponse(
            success=True,
            data=metrics_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取服务指标失败: {str(e)}")


# ================================
# 主程序入口
# ================================

if __name__ == "__main__":
    print("🚀 启动 RAG Web 服务...")
    print("📖 API 文档将在 http://localhost:8000/docs 提供")
    print("🔍 ReDoc 文档将在 http://localhost:8000/redoc 提供")
    print("⚡ 使用 Ctrl+C 停止服务")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式，生产环境应设为 False
        log_level="info"
    )