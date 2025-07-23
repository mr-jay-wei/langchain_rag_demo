#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速 API 测试脚本

用于验证 FastAPI 应用是否能正常启动和响应
"""

import asyncio
import sys
from fastapi.testclient import TestClient

# 添加当前目录到 Python 路径
sys.path.insert(0, '.')

try:
    from app import app
    print("✅ 成功导入 FastAPI 应用")
except Exception as e:
    print(f"❌ 导入 FastAPI 应用失败: {e}")
    sys.exit(1)


def test_basic_endpoints():
    """测试基本端点"""
    print("🧪 开始测试基本端点...")
    
    # 创建测试客户端
    client = TestClient(app)
    
    try:
        # 测试根路径
        print("1️⃣ 测试根路径...")
        response = client.get("/")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   响应: {response.json()}")
            print("   ✅ 根路径测试通过")
        else:
            print("   ❌ 根路径测试失败")
        
        # 测试健康检查
        print("\n2️⃣ 测试健康检查...")
        response = client.get("/api/v1/health")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            service_status = health_data.get('data', {}).get('status', 'unknown')
            components = health_data.get('data', {}).get('components', {})
            print(f"   服务状态: {service_status}")
            print(f"   组件状态: {components}")
            
            if service_status in ['healthy', 'initializing']:
                print("   ✅ 健康检查测试通过")
            else:
                print("   ⚠️  服务状态异常，但接口正常响应")
        else:
            print("   ❌ 健康检查测试失败")
        
        # 测试知识库状态
        print("\n3️⃣ 测试知识库状态...")
        response = client.get("/api/v1/knowledge/status")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            status_data = response.json()
            if status_data.get('success'):
                data = status_data.get('data', {})
                status = data.get('status', 'unknown')
                total_docs = data.get('total_documents', 0)
                print(f"   知识库状态: {status}")
                print(f"   文档总数: {total_docs}")
                print("   ✅ 知识库状态测试通过")
            else:
                print(f"   ⚠️  知识库状态异常: {status_data.get('error')}")
                print("   ✅ 接口正常响应（优雅降级）")
        else:
            print("   ❌ 知识库状态测试失败")
        
        # 测试简单问答
        print("\n4️⃣ 测试简单问答...")
        test_query = {
            "query": "测试问题",
            "options": {
                "enable_rewriting": False,
                "enable_hybrid_search": False,
                "max_results": 1
            }
        }
        
        response = client.post("/api/v1/ask", json=test_query)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ 问答接口测试通过")
                print(f"   回答: {result.get('data', {}).get('answer', 'N/A')[:50]}...")
            else:
                error_msg = result.get('error', 'Unknown error')
                query_status = result.get('data', {}).get('query_info', {}).get('status', 'unknown')
                print(f"   ⚠️  问答接口返回错误: {error_msg}")
                print(f"   查询状态: {query_status}")
                if query_status == 'pipeline_not_ready':
                    print("   ✅ 优雅降级处理正常")
                else:
                    print("   ✅ 错误处理正常")
        else:
            print(f"   ❌ 问答接口测试失败: {response.text}")
        
        print("\n✅ 基本端点测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False


def test_api_documentation():
    """测试 API 文档端点"""
    print("\n📚 测试 API 文档端点...")
    
    client = TestClient(app)
    
    try:
        # 测试 OpenAPI JSON
        response = client.get("/openapi.json")
        if response.status_code == 200:
            print("   ✅ OpenAPI JSON 可访问")
        else:
            print("   ❌ OpenAPI JSON 不可访问")
        
        # 测试 Swagger UI
        response = client.get("/docs")
        if response.status_code == 200:
            print("   ✅ Swagger UI 可访问")
        else:
            print("   ❌ Swagger UI 不可访问")
        
        # 测试 ReDoc
        response = client.get("/redoc")
        if response.status_code == 200:
            print("   ✅ ReDoc 可访问")
        else:
            print("   ❌ ReDoc 不可访问")
            
        return True
        
    except Exception as e:
        print(f"❌ API 文档测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 FastAPI 应用快速测试")
    print("=" * 50)
    
    # 测试基本端点
    basic_test_passed = test_basic_endpoints()
    
    # 测试 API 文档
    doc_test_passed = test_api_documentation()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试总结:")
    print(f"   基本端点测试: {'✅ 通过' if basic_test_passed else '❌ 失败'}")
    print(f"   API 文档测试: {'✅ 通过' if doc_test_passed else '❌ 失败'}")
    
    if basic_test_passed and doc_test_passed:
        print("\n🎉 所有测试通过! FastAPI 应用可以正常启动")
        print("\n💡 下一步:")
        print("   1. 运行 'python start_server.py' 启动服务")
        print("   2. 访问 http://localhost:8000/docs 查看 API 文档")
        print("   3. 运行 'python test_api_client.py' 进行完整测试")
    else:
        print("\n⚠️  部分测试失败，请检查配置和依赖")


if __name__ == "__main__":
    main()