#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
提示词管理API - 支持运行时动态更新提示词
提供RESTful API接口用于管理提示词，无需重启服务
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# 导入提示词管理器
from rag.prompt_manager import prompt_manager

app = FastAPI(
    title="提示词管理API",
    description="运行时动态管理RAG系统提示词",
    version="1.0.0"
)

# 数据模型
class PromptUpdateRequest(BaseModel):
    content: str
    description: str = ""

class PromptCreateRequest(BaseModel):
    name: str
    content: str
    description: str = ""

class BulkUpdateRequest(BaseModel):
    prompts: Dict[str, str]

# 全局变量用于跟踪更新历史
update_history: List[Dict[str, Any]] = []

def log_update(action: str, prompt_name: str, details: Dict[str, Any] = None):
    """记录更新历史"""
    update_history.append({
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "prompt_name": prompt_name,
        "details": details or {}
    })
    
    # 只保留最近100条记录
    if len(update_history) > 100:
        update_history.pop(0)

@app.get("/")
async def get_management_ui():
    """返回提示词管理界面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>提示词管理系统</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            h1, h2 {
                color: #333;
                margin-bottom: 20px;
            }
            .prompt-item {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                background-color: #fafafa;
            }
            .prompt-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .prompt-name {
                font-weight: bold;
                color: #007bff;
            }
            .prompt-info {
                font-size: 12px;
                color: #666;
            }
            .prompt-content {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 10px;
                font-family: monospace;
                font-size: 12px;
                max-height: 200px;
                overflow-y: auto;
                margin-bottom: 10px;
            }
            .button {
                padding: 8px 16px;
                margin: 5px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }
            .btn-primary { background-color: #007bff; color: white; }
            .btn-success { background-color: #28a745; color: white; }
            .btn-warning { background-color: #ffc107; color: black; }
            .btn-danger { background-color: #dc3545; color: white; }
            .btn-info { background-color: #17a2b8; color: white; }
            
            .button:hover { opacity: 0.8; }
            
            textarea {
                width: 100%;
                min-height: 200px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: monospace;
                font-size: 12px;
            }
            
            .status-message {
                padding: 10px;
                border-radius: 4px;
                margin: 10px 0;
            }
            .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .info { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
            
            .history-item {
                padding: 8px;
                border-left: 3px solid #007bff;
                margin-bottom: 8px;
                background-color: #f8f9fa;
            }
            
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.5);
            }
            
            .modal-content {
                background-color: white;
                margin: 5% auto;
                padding: 20px;
                border-radius: 8px;
                width: 80%;
                max-width: 600px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 提示词管理系统</h1>
            <p>运行时动态管理RAG系统提示词，无需重启服务</p>
            
            <div style="margin-bottom: 20px;">
                <button class="button btn-success" onclick="loadPrompts()">🔄 刷新提示词列表</button>
                <button class="button btn-info" onclick="reloadAllPrompts()">🔥 重载所有提示词</button>
                <button class="button btn-warning" onclick="showHistory()">📋 查看更新历史</button>
                <button class="button btn-primary" onclick="showCreateModal()">➕ 创建新提示词</button>
            </div>
            
            <div id="statusMessage"></div>
            <div id="promptsList"></div>
        </div>
        
        <div class="container">
            <h2>📊 系统状态</h2>
            <div id="systemStatus"></div>
        </div>
        
        <!-- 编辑模态框 -->
        <div id="editModal" class="modal">
            <div class="modal-content">
                <h3>编辑提示词: <span id="editPromptName"></span></h3>
                <textarea id="editPromptContent"></textarea>
                <div style="margin-top: 15px;">
                    <button class="button btn-success" onclick="savePrompt()">💾 保存</button>
                    <button class="button btn-danger" onclick="closeModal()">❌ 取消</button>
                </div>
            </div>
        </div>
        
        <!-- 创建模态框 -->
        <div id="createModal" class="modal">
            <div class="modal-content">
                <h3>创建新提示词</h3>
                <input type="text" id="newPromptName" placeholder="提示词名称" style="width: 100%; margin-bottom: 10px; padding: 8px;">
                <textarea id="newPromptContent" placeholder="提示词内容"></textarea>
                <div style="margin-top: 15px;">
                    <button class="button btn-success" onclick="createPrompt()">✨ 创建</button>
                    <button class="button btn-danger" onclick="closeCreateModal()">❌ 取消</button>
                </div>
            </div>
        </div>
        
        <!-- 历史记录模态框 -->
        <div id="historyModal" class="modal">
            <div class="modal-content">
                <h3>更新历史</h3>
                <div id="historyContent" style="max-height: 400px; overflow-y: auto;"></div>
                <div style="margin-top: 15px;">
                    <button class="button btn-danger" onclick="closeHistoryModal()">关闭</button>
                </div>
            </div>
        </div>

        <script>
            let currentEditingPrompt = null;
            
            async function loadPrompts() {
                try {
                    const response = await fetch('/api/prompts');
                    const data = await response.json();
                    
                    const promptsList = document.getElementById('promptsList');
                    promptsList.innerHTML = '';
                    
                    data.prompts.forEach(prompt => {
                        const promptDiv = document.createElement('div');
                        promptDiv.className = 'prompt-item';
                        promptDiv.innerHTML = `
                            <div class="prompt-header">
                                <span class="prompt-name">${prompt.name}</span>
                                <div class="prompt-info">
                                    大小: ${prompt.info.file_size} 字节 | 
                                    变量: ${prompt.info.template_variables.join(', ')} |
                                    缓存: ${prompt.info.is_cached ? '✅' : '❌'}
                                </div>
                            </div>
                            <div class="prompt-content">${prompt.info.content_preview}</div>
                            <div>
                                <button class="button btn-primary" onclick="editPrompt('${prompt.name}')">✏️ 编辑</button>
                                <button class="button btn-warning" onclick="reloadPrompt('${prompt.name}')">🔄 重载</button>
                                <button class="button btn-info" onclick="validatePrompt('${prompt.name}')">✅ 验证</button>
                                <button class="button btn-danger" onclick="deletePrompt('${prompt.name}')">🗑️ 删除</button>
                            </div>
                        `;
                        promptsList.appendChild(promptDiv);
                    });
                    
                    showMessage('提示词列表已刷新', 'success');
                } catch (error) {
                    showMessage('加载提示词失败: ' + error.message, 'error');
                }
            }
            
            async function editPrompt(promptName) {
                try {
                    const response = await fetch(`/api/prompts/${promptName}`);
                    const data = await response.json();
                    
                    currentEditingPrompt = promptName;
                    document.getElementById('editPromptName').textContent = promptName;
                    document.getElementById('editPromptContent').value = data.content;
                    document.getElementById('editModal').style.display = 'block';
                } catch (error) {
                    showMessage('加载提示词内容失败: ' + error.message, 'error');
                }
            }
            
            async function savePrompt() {
                if (!currentEditingPrompt) return;
                
                const content = document.getElementById('editPromptContent').value;
                
                try {
                    const response = await fetch(`/api/prompts/${currentEditingPrompt}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            content: content,
                            description: '通过Web界面更新'
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        showMessage(`提示词 "${currentEditingPrompt}" 已成功更新`, 'success');
                        closeModal();
                        loadPrompts();
                    } else {
                        showMessage('更新失败: ' + data.detail, 'error');
                    }
                } catch (error) {
                    showMessage('更新失败: ' + error.message, 'error');
                }
            }
            
            async function reloadPrompt(promptName) {
                try {
                    const response = await fetch(`/api/prompts/${promptName}/reload`, {
                        method: 'POST'
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        showMessage(`提示词 "${promptName}" 已重载`, 'success');
                        loadPrompts();
                    } else {
                        showMessage('重载失败: ' + data.detail, 'error');
                    }
                } catch (error) {
                    showMessage('重载失败: ' + error.message, 'error');
                }
            }
            
            async function reloadAllPrompts() {
                try {
                    const response = await fetch('/api/prompts/reload-all', {
                        method: 'POST'
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        showMessage(`已重载 ${Object.keys(data.reloaded_prompts).length} 个提示词`, 'success');
                        loadPrompts();
                    } else {
                        showMessage('批量重载失败: ' + data.detail, 'error');
                    }
                } catch (error) {
                    showMessage('批量重载失败: ' + error.message, 'error');
                }
            }
            
            async function validatePrompt(promptName) {
                try {
                    const response = await fetch(`/api/prompts/${promptName}/validate`);
                    const data = await response.json();
                    
                    if (data.valid) {
                        showMessage(`提示词 "${promptName}" 验证通过 ✅`, 'success');
                    } else {
                        let errorMsg = `提示词 "${promptName}" 验证失败:\\n`;
                        if (data.missing_variables.length > 0) {
                            errorMsg += `缺少变量: ${data.missing_variables.join(', ')}\\n`;
                        }
                        if (data.format_test && !data.format_test.success) {
                            errorMsg += `格式错误: ${data.format_test.error}`;
                        }
                        showMessage(errorMsg, 'error');
                    }
                } catch (error) {
                    showMessage('验证失败: ' + error.message, 'error');
                }
            }
            
            async function showHistory() {
                try {
                    const response = await fetch('/api/history');
                    const data = await response.json();
                    
                    const historyContent = document.getElementById('historyContent');
                    historyContent.innerHTML = '';
                    
                    data.history.forEach(item => {
                        const historyDiv = document.createElement('div');
                        historyDiv.className = 'history-item';
                        historyDiv.innerHTML = `
                            <strong>${item.action}</strong> - ${item.prompt_name}<br>
                            <small>${item.timestamp}</small>
                        `;
                        historyContent.appendChild(historyDiv);
                    });
                    
                    document.getElementById('historyModal').style.display = 'block';
                } catch (error) {
                    showMessage('加载历史记录失败: ' + error.message, 'error');
                }
            }
            
            function showCreateModal() {
                document.getElementById('newPromptName').value = '';
                document.getElementById('newPromptContent').value = '';
                document.getElementById('createModal').style.display = 'block';
            }
            
            async function createPrompt() {
                const name = document.getElementById('newPromptName').value.trim();
                const content = document.getElementById('newPromptContent').value;
                
                if (!name || !content) {
                    showMessage('请填写提示词名称和内容', 'error');
                    return;
                }
                
                try {
                    const response = await fetch('/api/prompts', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            name: name,
                            content: content,
                            description: '通过Web界面创建'
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        showMessage(`提示词 "${name}" 已成功创建`, 'success');
                        closeCreateModal();
                        loadPrompts();
                    } else {
                        showMessage('创建失败: ' + data.detail, 'error');
                    }
                } catch (error) {
                    showMessage('创建失败: ' + error.message, 'error');
                }
            }
            
            function closeModal() {
                document.getElementById('editModal').style.display = 'none';
                currentEditingPrompt = null;
            }
            
            function closeCreateModal() {
                document.getElementById('createModal').style.display = 'none';
            }
            
            function closeHistoryModal() {
                document.getElementById('historyModal').style.display = 'none';
            }
            
            function showMessage(message, type) {
                const statusDiv = document.getElementById('statusMessage');
                statusDiv.innerHTML = `<div class="status-message ${type}">${message}</div>`;
                
                // 3秒后自动清除消息
                setTimeout(() => {
                    statusDiv.innerHTML = '';
                }, 3000);
            }
            
            // 页面加载时自动加载提示词列表
            window.onload = function() {
                loadPrompts();
            };
            
            // 点击模态框外部关闭
            window.onclick = function(event) {
                const editModal = document.getElementById('editModal');
                const createModal = document.getElementById('createModal');
                const historyModal = document.getElementById('historyModal');
                
                if (event.target === editModal) {
                    closeModal();
                }
                if (event.target === createModal) {
                    closeCreateModal();
                }
                if (event.target === historyModal) {
                    closeHistoryModal();
                }
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/prompts")
async def list_prompts():
    """获取所有提示词列表"""
    try:
        available_prompts = prompt_manager.list_available_prompts()
        prompts_info = []
        
        for prompt_name in available_prompts:
            info = prompt_manager.get_prompt_info(prompt_name)
            prompts_info.append({
                "name": prompt_name,
                "info": info
            })
        
        return {
            "success": True,
            "count": len(prompts_info),
            "prompts": prompts_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prompts/{prompt_name}")
async def get_prompt(prompt_name: str):
    """获取指定提示词的内容"""
    try:
        content = prompt_manager.load_prompt(prompt_name)
        info = prompt_manager.get_prompt_info(prompt_name)
        
        return {
            "success": True,
            "name": prompt_name,
            "content": content,
            "info": info
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"提示词 '{prompt_name}' 不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/prompts/{prompt_name}")
async def update_prompt(prompt_name: str, request: PromptUpdateRequest):
    """更新指定提示词的内容"""
    try:
        # 保存新内容
        prompt_manager.save_prompt(prompt_name, request.content)
        
        # 记录更新历史
        log_update("UPDATE", prompt_name, {
            "content_length": len(request.content),
            "description": request.description
        })
        
        return {
            "success": True,
            "message": f"提示词 '{prompt_name}' 已成功更新",
            "content_length": len(request.content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prompts")
async def create_prompt(request: PromptCreateRequest):
    """创建新的提示词"""
    try:
        # 检查是否已存在
        existing_prompts = prompt_manager.list_available_prompts()
        if request.name in existing_prompts:
            raise HTTPException(status_code=400, detail=f"提示词 '{request.name}' 已存在")
        
        # 保存新提示词
        prompt_manager.save_prompt(request.name, request.content)
        
        # 记录创建历史
        log_update("CREATE", request.name, {
            "content_length": len(request.content),
            "description": request.description
        })
        
        return {
            "success": True,
            "message": f"提示词 '{request.name}' 已成功创建",
            "name": request.name
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prompts/{prompt_name}/reload")
async def reload_prompt(prompt_name: str):
    """重新加载指定提示词"""
    try:
        content = prompt_manager.reload_prompt(prompt_name)
        
        # 记录重载历史
        log_update("RELOAD", prompt_name, {
            "content_length": len(content)
        })
        
        return {
            "success": True,
            "message": f"提示词 '{prompt_name}' 已重新加载",
            "content_length": len(content)
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"提示词 '{prompt_name}' 不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prompts/reload-all")
async def reload_all_prompts():
    """重新加载所有提示词"""
    try:
        reloaded_prompts = prompt_manager.reload_all_prompts()
        
        # 记录批量重载历史
        log_update("RELOAD_ALL", "all", {
            "count": len(reloaded_prompts),
            "prompts": list(reloaded_prompts.keys())
        })
        
        return {
            "success": True,
            "message": f"已重新加载 {len(reloaded_prompts)} 个提示词",
            "reloaded_prompts": reloaded_prompts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prompts/{prompt_name}/validate")
async def validate_prompt(prompt_name: str):
    """验证指定提示词的有效性"""
    try:
        validation_result = prompt_manager.validate_prompt(prompt_name)
        return {
            "success": True,
            "prompt_name": prompt_name,
            **validation_result
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"提示词 '{prompt_name}' 不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_update_history():
    """获取更新历史"""
    return {
        "success": True,
        "count": len(update_history),
        "history": update_history
    }

@app.post("/api/cache/clear")
async def clear_cache():
    """清除所有缓存"""
    try:
        prompt_manager.clear_cache()
        
        log_update("CLEAR_CACHE", "all", {})
        
        return {
            "success": True,
            "message": "所有缓存已清除"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_system_status():
    """获取系统状态"""
    try:
        available_prompts = prompt_manager.list_available_prompts()
        
        # 统计缓存状态
        cached_prompts = []
        uncached_prompts = []
        
        for prompt_name in available_prompts:
            info = prompt_manager.get_prompt_info(prompt_name)
            if info.get("is_cached", False):
                cached_prompts.append(prompt_name)
            else:
                uncached_prompts.append(prompt_name)
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "total_prompts": len(available_prompts),
            "cached_prompts": len(cached_prompts),
            "uncached_prompts": len(uncached_prompts),
            "recent_updates": len([h for h in update_history if 
                                (datetime.now() - datetime.fromisoformat(h["timestamp"])).seconds < 3600]),
            "prompts_directory": str(prompt_manager.prompts_dir),
            "available_prompts": available_prompts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    print("🔧 启动提示词管理API...")
    print("📱 管理界面: http://localhost:8001")
    print("📚 API文档: http://localhost:8001/docs")
    print("💡 支持运行时动态更新提示词，无需重启服务")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )