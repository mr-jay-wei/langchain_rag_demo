#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Web 服务启动脚本

提供多种启动模式和配置选项
"""

import os
import sys
import argparse
import uvicorn
from pathlib import Path


def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查必要的目录
    required_dirs = [
        "data",
        "rag",
        "local_models"
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ 缺少必要目录: {', '.join(missing_dirs)}")
        print("请确保项目结构完整")
        return False
    
    # 检查配置文件
    if not os.path.exists(".env"):
        print("⚠️  未找到 .env 配置文件")
        print("请创建 .env 文件并配置 API 密钥")
    
    # 检查模型文件
    model_dirs = [
        "local_models/bge-small-zh-v1.5",
        "local_models/bge-reranker-base"
    ]
    
    missing_models = []
    for model_dir in model_dirs:
        if not os.path.exists(model_dir):
            missing_models.append(model_dir)
    
    if missing_models:
        print(f"⚠️  未找到本地模型: {', '.join(missing_models)}")
        print("请下载并配置本地模型，或修改 rag/config.py 中的模型路径")
    
    print("✅ 环境检查完成")
    return True


def start_development_server(host: str = "0.0.0.0", port: int = 8000):
    """启动开发服务器"""
    print("🚀 启动开发模式服务器...")
    print(f"📖 API 文档: http://{host}:{port}/docs")
    print(f"🔍 ReDoc: http://{host}:{port}/redoc")
    print("⚡ 使用 Ctrl+C 停止服务")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
        access_log=True
    )


def start_production_server(host: str = "0.0.0.0", port: int = 8000, workers: int = 4):
    """启动生产服务器"""
    print("🏭 启动生产模式服务器...")
    print(f"👥 工作进程数: {workers}")
    print(f"📖 API 文档: http://{host}:{port}/docs")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        workers=workers,
        log_level="warning",
        access_log=False
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="RAG Web 服务启动脚本")
    
    parser.add_argument(
        "--mode", 
        choices=["dev", "prod"], 
        default="dev",
        help="启动模式: dev(开发) 或 prod(生产)"
    )
    
    parser.add_argument(
        "--host", 
        default="0.0.0.0",
        help="服务器主机地址 (默认: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="服务器端口 (默认: 8000)"
    )
    
    parser.add_argument(
        "--workers", 
        type=int, 
        default=4,
        help="生产模式下的工作进程数 (默认: 4)"
    )
    
    parser.add_argument(
        "--skip-check", 
        action="store_true",
        help="跳过环境检查"
    )
    
    args = parser.parse_args()
    
    print("🌐 RAG Web 服务启动器")
    print("=" * 50)
    
    # 环境检查
    if not args.skip_check:
        if not check_environment():
            print("❌ 环境检查失败，使用 --skip-check 跳过检查")
            sys.exit(1)
    
    # 启动服务器
    try:
        if args.mode == "dev":
            start_development_server(args.host, args.port)
        else:
            start_production_server(args.host, args.port, args.workers)
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()