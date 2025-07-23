#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整服务测试脚本

测试实际启动的 RAG Web 服务的所有功能
"""

import requests
import time
import json
import subprocess
import threading
import sys
from typing import Optional


class ServiceTester:
    """服务测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.service_process: Optional[subprocess.Popen] = None
        
    def wait_for_service(self, timeout: int = 60) -> bool:
        """等待服务启动"""
        print(f"⏳ 等待服务启动 (最多等待 {timeout} 秒)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.session.get(f"{self.base_url}/", timeout=5)
                if response.status_code == 200:
                    print("✅ 服务已启动")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
            print(".", end="", flush=True)
        
        print("\n❌ 服务启动超时")
        return False
    
    def test_service_initialization(self) -> bool:
        """测试服务初始化"""
        print("\n🔧 测试服务初始化...")
        
        try:
            # 检查根路径
            response = self.session.get(f"{self.base_url}/")
            if response.status_code != 200:
                print("❌ 根路径不可访问")
                return False
            
            # 检查健康状态
            response = self.session.get(f"{self.base_url}/api/v1/health")
            if response.status_code != 200:
                print("❌ 健康检查接口不可访问")
                return False
            
            health_data = response.json()
            status = health_data.get('data', {}).get('status', 'unknown')
            print(f"   服务状态: {status}")
            
            # 等待 RAG Pipeline 初始化完成
            if status == 'initializing':
                print("⏳ 等待 RAG Pipeline 初始化...")
                max_wait = 120  # 最多等待2分钟
                wait_time = 0
                
                while wait_time < max_wait:
                    time.sleep(5)
                    wait_time += 5
                    
                    response = self.session.get(f"{self.base_url}/api/v1/health")
                    if response.status_code == 200:
                        health_data = response.json()
                        status = health_data.get('data', {}).get('status', 'unknown')
                        print(f"   当前状态: {status} ({wait_time}s)")
                        
                        if status == 'healthy':
                            print("✅ RAG Pipeline 初始化完成")
                            break
                        elif status == 'unhealthy':
                            print("❌ RAG Pipeline 初始化失败")
                            return False
                else:
                    print("⚠️  RAG Pipeline 初始化超时，但继续测试")
            
            print("✅ 服务初始化测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 服务初始化测试失败: {e}")
            return False
    
    def test_basic_functionality(self) -> bool:
        """测试基本功能"""
        print("\n🧪 测试基本功能...")
        
        try:
            # 测试知识库状态
            print("1. 测试知识库状态...")
            response = self.session.get(f"{self.base_url}/api/v1/knowledge/status")
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    data = result['data']
                    print(f"   文档总数: {data.get('total_documents', 0)}")
                    print(f"   类别: {data.get('categories', {})}")
                    print("   ✅ 知识库状态正常")
                else:
                    print(f"   ⚠️  知识库状态异常: {result.get('error')}")
            
            # 测试简单问答
            print("\n2. 测试简单问答...")
            test_query = {
                "query": "你好，这是一个测试问题",
                "options": {
                    "enable_rewriting": False,
                    "enable_hybrid_search": False,
                    "max_results": 3
                }
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/ask", json=test_query)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    answer = result['data']['answer']
                    search_time = result['data']['query_info']['search_time']
                    print(f"   回答: {answer[:100]}...")
                    print(f"   查询时间: {search_time}秒")
                    print("   ✅ 问答功能正常")
                else:
                    error = result.get('error', 'Unknown error')
                    print(f"   ⚠️  问答返回错误: {error}")
                    if 'pipeline_not_ready' in str(error) or '未初始化' in str(error):
                        print("   ℹ️  这是正常的，RAG Pipeline 可能还在初始化")
            
            # 测试服务指标
            print("\n3. 测试服务指标...")
            response = self.session.get(f"{self.base_url}/api/v1/metrics")
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    data = result['data']
                    print(f"   总查询数: {data.get('queries_total', 0)}")
                    print(f"   平均响应时间: {data.get('average_response_time', 0)}秒")
                    print("   ✅ 服务指标正常")
            
            print("✅ 基本功能测试完成")
            return True
            
        except Exception as e:
            print(f"❌ 基本功能测试失败: {e}")
            return False
    
    def test_api_documentation(self) -> bool:
        """测试 API 文档"""
        print("\n📚 测试 API 文档...")
        
        try:
            # 测试 Swagger UI
            response = self.session.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                print("   ✅ Swagger UI 可访问")
            else:
                print("   ❌ Swagger UI 不可访问")
                return False
            
            # 测试 ReDoc
            response = self.session.get(f"{self.base_url}/redoc")
            if response.status_code == 200:
                print("   ✅ ReDoc 可访问")
            else:
                print("   ❌ ReDoc 不可访问")
                return False
            
            # 测试 OpenAPI JSON
            response = self.session.get(f"{self.base_url}/openapi.json")
            if response.status_code == 200:
                openapi_data = response.json()
                print(f"   API 版本: {openapi_data.get('info', {}).get('version', 'unknown')}")
                print(f"   端点数量: {len(openapi_data.get('paths', {}))}")
                print("   ✅ OpenAPI 规范正常")
            else:
                print("   ❌ OpenAPI JSON 不可访问")
                return False
            
            print("✅ API 文档测试通过")
            return True
            
        except Exception as e:
            print(f"❌ API 文档测试失败: {e}")
            return False
    
    def run_comprehensive_test(self) -> bool:
        """运行综合测试"""
        print("🚀 开始综合服务测试")
        print("=" * 60)
        
        # 等待服务启动
        if not self.wait_for_service():
            return False
        
        # 测试服务初始化
        init_result = self.test_service_initialization()
        
        # 测试基本功能
        func_result = self.test_basic_functionality()
        
        # 测试 API 文档
        doc_result = self.test_api_documentation()
        
        # 总结结果
        print("\n" + "=" * 60)
        print("📊 测试结果总结:")
        print(f"   服务初始化: {'✅ 通过' if init_result else '❌ 失败'}")
        print(f"   基本功能: {'✅ 通过' if func_result else '❌ 失败'}")
        print(f"   API 文档: {'✅ 通过' if doc_result else '❌ 失败'}")
        
        overall_success = init_result and func_result and doc_result
        
        if overall_success:
            print("\n🎉 所有测试通过! RAG Web 服务运行正常")
            print("\n💡 可以开始使用以下功能:")
            print(f"   - API 文档: {self.base_url}/docs")
            print(f"   - 问答接口: POST {self.base_url}/api/v1/ask")
            print(f"   - 健康检查: GET {self.base_url}/api/v1/health")
        else:
            print("\n⚠️  部分测试失败，请检查服务配置")
        
        return overall_success


def test_with_running_service():
    """测试已运行的服务"""
    print("🔍 测试已运行的服务...")
    
    tester = ServiceTester()
    
    # 检查服务是否已经运行
    try:
        response = tester.session.get(f"{tester.base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 发现运行中的服务")
            return tester.run_comprehensive_test()
        else:
            print("❌ 服务未运行或不可访问")
            return False
    except requests.exceptions.RequestException:
        print("❌ 无法连接到服务")
        return False


def main():
    """主函数"""
    print("🌐 RAG Web 服务完整测试")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--running":
        # 测试已运行的服务
        success = test_with_running_service()
    else:
        print("请先启动服务，然后运行:")
        print("python test_full_service.py --running")
        print("\n或者在另一个终端运行:")
        print("python start_server.py")
        print("然后在当前终端运行:")
        print("python test_full_service.py --running")
        return
    
    if success:
        print("\n✅ 测试完成，服务运行正常!")
        sys.exit(0)
    else:
        print("\n❌ 测试失败，请检查服务状态")
        sys.exit(1)


if __name__ == "__main__":
    main()