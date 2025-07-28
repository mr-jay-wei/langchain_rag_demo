"""
流式RAG Web演示 - FastAPI + WebSocket实现
展示正确的流式响应理念：只有答案生成是流式的
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# 导入我们的流式RAG管道
import sys
sys.path.append(str(Path(__file__).parent.parent))

from rag.streaming_pipeline import StreamingRagPipeline

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="流式RAG演示", description="基于FastAPI + WebSocket的流式问答系统")

# 全局RAG管道实例
rag_pipeline = None

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化RAG管道"""
    global rag_pipeline
    try:
        logger.info("正在初始化RAG管道...")
        rag_pipeline = StreamingRagPipeline()
        logger.info("RAG管道初始化完成")
    except Exception as e:
        logger.error(f"RAG管道初始化失败: {e}")
        raise

@app.get("/")
async def get_homepage():
    """返回Web界面HTML"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>流式RAG问答系统</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .chat-container {
                height: 400px;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                overflow-y: auto;
                background-color: #fafafa;
                margin-bottom: 20px;
            }
            .message {
                margin-bottom: 15px;
                padding: 10px;
                border-radius: 8px;
            }
            .user-message {
                background-color: #007bff;
                color: white;
                margin-left: 20%;
                text-align: right;
            }
            .bot-message {
                background-color: #e9ecef;
                color: #333;
                margin-right: 20%;
            }
            .status-message {
                background-color: #fff3cd;
                color: #856404;
                font-style: italic;
                text-align: center;
                border: 1px solid #ffeaa7;
            }
            .input-container {
                display: flex;
                gap: 10px;
            }
            #questionInput {
                flex: 1;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 16px;
            }
            #sendButton {
                padding: 12px 24px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
            }
            #sendButton:hover {
                background-color: #0056b3;
            }
            #sendButton:disabled {
                background-color: #6c757d;
                cursor: not-allowed;
            }
            .connection-status {
                text-align: center;
                padding: 10px;
                margin-bottom: 20px;
                border-radius: 6px;
            }
            .connected {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .disconnected {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌊 流式RAG问答系统</h1>
            
            <div id="connectionStatus" class="connection-status disconnected">
                正在连接...
            </div>
            
            <div id="chatContainer" class="chat-container">
                <div class="message status-message">
                    欢迎使用流式RAG问答系统！请输入您的问题。
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="questionInput" placeholder="请输入您的问题..." />
                <button id="sendButton" disabled>发送</button>
            </div>
        </div>

        <script>
            let ws = null;
            let isConnected = false;
            
            const chatContainer = document.getElementById('chatContainer');
            const questionInput = document.getElementById('questionInput');
            const sendButton = document.getElementById('sendButton');
            const connectionStatus = document.getElementById('connectionStatus');
            
            function connectWebSocket() {
                const wsUrl = `ws://${window.location.host}/ws`;
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    console.log('WebSocket连接已建立');
                    isConnected = true;
                    updateConnectionStatus(true);
                    sendButton.disabled = false;
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleMessage(data);
                };
                
                ws.onclose = function(event) {
                    console.log('WebSocket连接已关闭');
                    isConnected = false;
                    updateConnectionStatus(false);
                    sendButton.disabled = true;
                    
                    // 尝试重连
                    setTimeout(connectWebSocket, 3000);
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket错误:', error);
                };
            }
            
            function updateConnectionStatus(connected) {
                if (connected) {
                    connectionStatus.textContent = '✅ 已连接';
                    connectionStatus.className = 'connection-status connected';
                } else {
                    connectionStatus.textContent = '❌ 连接断开';
                    connectionStatus.className = 'connection-status disconnected';
                }
            }
            
            function addMessage(content, type) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}-message`;
                messageDiv.textContent = content;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
                return messageDiv;
            }
            
            let currentBotMessage = null;
            
            function handleMessage(data) {
                switch (data.type) {
                    case 'status':
                        addMessage(data.message, 'status');
                        break;
                        
                    case 'answer_start':
                        // 开始接收答案，创建新的消息容器
                        currentBotMessage = addMessage('', 'bot');
                        break;
                        
                    case 'answer_chunk':
                        // 流式更新答案内容
                        if (currentBotMessage) {
                            currentBotMessage.textContent += data.content;
                            chatContainer.scrollTop = chatContainer.scrollHeight;
                        }
                        break;
                        
                    case 'answer_complete':
                        // 答案生成完成
                        currentBotMessage = null;
                        sendButton.disabled = false;
                        sendButton.textContent = '发送';
                        break;
                        
                    case 'error':
                        addMessage(`错误: ${data.message}`, 'status');
                        sendButton.disabled = false;
                        sendButton.textContent = '发送';
                        break;
                }
            }
            
            function sendQuestion() {
                const question = questionInput.value.trim();
                if (!question || !isConnected) return;
                
                // 显示用户问题
                addMessage(question, 'user');
                
                // 发送到服务器
                ws.send(JSON.stringify({
                    type: 'question',
                    content: question
                }));
                
                // 清空输入框并禁用发送按钮
                questionInput.value = '';
                sendButton.disabled = true;
                sendButton.textContent = '处理中...';
            }
            
            // 事件监听
            sendButton.addEventListener('click', sendQuestion);
            
            questionInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendQuestion();
                }
            });
            
            // 初始化连接
            connectWebSocket();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点处理流式问答"""
    await websocket.accept()
    logger.info("WebSocket连接已建立")
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "question":
                question = message["content"]
                logger.info(f"收到问题: {question}")
                
                # 处理问题并流式返回答案
                await handle_question(websocket, question)
                
    except WebSocketDisconnect:
        logger.info("WebSocket连接已断开")
    except Exception as e:
        logger.error(f"WebSocket处理错误: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))

async def handle_question(websocket: WebSocket, question: str):
    """处理问题并流式返回答案"""
    try:
        answer_started = False
        
        # 使用流式RAG管道生成答案
        async for event in rag_pipeline.ask_stream(question):
            if event.type.value == "processing":
                # 处理状态更新
                await websocket.send_text(json.dumps({
                    "type": "status",
                    "message": f"🔍 {event.data.get('message', '正在处理...')}"
                }))
                
            elif event.type.value == "generation_start":
                # 开始生成答案
                if not answer_started:
                    await websocket.send_text(json.dumps({
                        "type": "answer_start"
                    }))
                    answer_started = True
                    
            elif event.type.value == "generation_chunk":
                # 流式答案片段
                chunk = event.data.get("chunk", "")
                if chunk.strip():  # 只发送非空内容
                    await websocket.send_text(json.dumps({
                        "type": "answer_chunk",
                        "content": chunk
                    }))
                    
            elif event.type.value == "generation_end":
                # 答案生成完成
                await websocket.send_text(json.dumps({
                    "type": "answer_complete"
                }))
                
            elif event.type.value == "error":
                # 错误处理
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": event.data.get("error", "未知错误")
                }))
                return
                
            elif event.type.value == "complete":
                # 整个流程完成
                if not answer_started:
                    # 如果没有流式答案，可能是直接返回了结果
                    await websocket.send_text(json.dumps({
                        "type": "answer_complete"
                    }))
        
    except Exception as e:
        logger.error(f"处理问题时出错: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"处理问题时出错: {str(e)}"
        }))

if __name__ == "__main__":
    import uvicorn
    
    print("🌊 启动流式RAG Web演示...")
    print("📱 访问地址: http://localhost:8000")
    print("💡 这个演示展示了正确的流式响应理念：只有答案生成是流式的")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )