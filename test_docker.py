#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker 部署测试脚本

测试 Docker 和 Docker Compose 部署的功能
"""

import subprocess
import time
import requests
import sys
import os


def run_command(cmd, timeout=30):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timeout"
    except Exception as e:
        return False, "", str(e)


def check_docker():
    """检查 Docker 是否可用"""
    print("🐳 检查 Docker 环境...")
    
    # 检查 Docker
    success, stdout, stderr = run_command("docker --version")
    if not success:
        print("❌ Docker 未安装或不可用")
        return False
    
    print(f"✅ Docker 版本: {stdout.strip()}")
    
    # 检查 Docker Compose
    success, stdout, stderr = run_command("docker-compose --version")
    if not success:
        print("❌ Docker Compose 未安装或不可用")
        return False
    
    print(f"✅ Docker Compose 版本: {stdout.strip()}")
    
    # 检查 Docker 服务状态
    success, stdout, stderr = run_command("docker info")
    if not success:
        print("❌ Docker 服务未运行")
        print(f"错误: {stderr}")
        return False
    
    print("✅ Docker 服务运行正常")
    return True


def check_files():
    """检查必要文件是否存在"""
    print("\n📁 检查必要文件...")
    
    required_files = [
        "Dockerfile",
        "docker-compose.yml",
        "app.py",
        "rag/config.py",
        "rag/pipeline.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✅ {file}")
    
    if missing_files:
        print(f"❌ 缺少文件: {', '.join(missing_files)}")
        return False
    
    # 检查 .env 文件
    if not os.path.exists(".env"):
        print("⚠️  .env 文件不存在，将创建示例文件")
        create_sample_env()
    else:
        print("✅ .env")
    
    return True


def create_sample_env():
    """创建示例 .env 文件"""
    env_content = """# RAG 系统环境变量配置

# LLM API 配置
DeepSeek_api_key="sk-your-api-key-here"
DeepSeek_base_url="https://api.deepseek.com"
DeepSeek_model_name="deepseek-chat"

# 服务配置
LOG_LEVEL=INFO
WORKERS=4
"""
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print("✅ 已创建示例 .env 文件，请根据需要修改配置")


def test_docker_build():
    """测试 Docker 镜像构建"""
    print("\n🔨 测试 Docker 镜像构建...")
    
    print("正在构建 Docker 镜像...")
    success, stdout, stderr = run_command("docker-compose build rag-api", timeout=300)
    
    if not success:
        print("❌ Docker 镜像构建失败")
        print(f"错误输出: {stderr}")
        return False
    
    print("✅ Docker 镜像构建成功")
    return True


def test_docker_compose():
    """测试 Docker Compose 部署"""
    print("\n🚀 测试 Docker Compose 部署...")
    
    try:
        # 启动服务
        print("正在启动服务...")
        success, stdout, stderr = run_command("docker-compose up -d", timeout=60)
        
        if not success:
            print("❌ 服务启动失败")
            print(f"错误输出: {stderr}")
            return False
        
        print("✅ 服务启动成功")
        
        # 等待服务就绪
        print("⏳ 等待服务就绪...")
        max_wait = 120  # 最多等待2分钟
        wait_time = 0
        service_ready = False
        
        while wait_time < max_wait:
            try:
                response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
                if response.status_code == 200:
                    service_ready = True
                    break
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(5)
            wait_time += 5
            print(f"等待中... ({wait_time}s)")
        
        if not service_ready:
            print("❌ 服务启动超时")
            return False
        
        print("✅ 服务就绪")
        
        # 测试 API 接口
        print("🧪 测试 API 接口...")
        
        # 测试健康检查
        try:
            response = requests.get("http://localhost:8000/api/v1/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ 健康检查: {health_data.get('data', {}).get('status', 'unknown')}")
            else:
                print(f"⚠️  健康检查异常: {response.status_code}")
        except Exception as e:
            print(f"❌ 健康检查失败: {e}")
            return False
        
        # 测试问答接口
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/ask",
                json={"query": "测试问题"},
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ 问答接口正常")
                else:
                    print(f"⚠️  问答接口返回错误: {result.get('error')}")
            else:
                print(f"⚠️  问答接口状态异常: {response.status_code}")
        except Exception as e:
            print(f"❌ 问答接口测试失败: {e}")
        
        # 测试 API 文档
        try:
            response = requests.get("http://localhost:8000/docs")
            if response.status_code == 200:
                print("✅ API 文档可访问")
            else:
                print(f"⚠️  API 文档访问异常: {response.status_code}")
        except Exception as e:
            print(f"❌ API 文档测试失败: {e}")
        
        return True
        
    finally:
        # 清理：停止服务
        print("\n🧹 清理测试环境...")
        run_command("docker-compose down", timeout=30)
        print("✅ 测试环境已清理")


def test_with_profiles():
    """测试带 profile 的部署"""
    print("\n🔧 测试 Profile 部署...")
    
    try:
        # 测试 nginx profile
        print("测试 Nginx profile...")
        success, stdout, stderr = run_command(
            "docker-compose --profile with-nginx config", 
            timeout=30
        )
        
        if success:
            print("✅ Nginx profile 配置正确")
        else:
            print(f"⚠️  Nginx profile 配置问题: {stderr}")
        
        # 测试 redis profile
        print("测试 Redis profile...")
        success, stdout, stderr = run_command(
            "docker-compose --profile with-cache config", 
            timeout=30
        )
        
        if success:
            print("✅ Redis profile 配置正确")
        else:
            print(f"⚠️  Redis profile 配置问题: {stderr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Profile 测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🐳 Docker 部署测试")
    print("=" * 50)
    
    # 检查 Docker 环境
    if not check_docker():
        print("\n❌ Docker 环境检查失败")
        sys.exit(1)
    
    # 检查必要文件
    if not check_files():
        print("\n❌ 文件检查失败")
        sys.exit(1)
    
    # 测试镜像构建
    if not test_docker_build():
        print("\n❌ Docker 镜像构建测试失败")
        sys.exit(1)
    
    # 测试 Docker Compose 部署
    if not test_docker_compose():
        print("\n❌ Docker Compose 部署测试失败")
        sys.exit(1)
    
    # 测试 Profile 配置
    if not test_with_profiles():
        print("\n⚠️  Profile 测试有问题，但不影响基本功能")
    
    # 总结
    print("\n" + "=" * 50)
    print("🎉 Docker 部署测试完成!")
    print("\n💡 使用方法:")
    print("   # 启动基本服务")
    print("   docker-compose up -d")
    print("")
    print("   # 启动完整服务栈")
    print("   docker-compose --profile with-nginx --profile with-cache up -d")
    print("")
    print("   # 查看服务状态")
    print("   docker-compose ps")
    print("")
    print("   # 查看日志")
    print("   docker-compose logs -f rag-api")
    print("")
    print("   # 停止服务")
    print("   docker-compose down")
    print("")
    print("📖 详细文档: DOCKER_GUIDE.md")


if __name__ == "__main__":
    main()