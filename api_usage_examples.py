#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG API 使用示例

展示如何使用 RAG Web API 的各种功能
"""

import requests
import json
import time
from typing import Dict, Any, List


class RAGAPIDemo:
    """RAG API 演示类"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def demo_basic_query(self):
        """演示基本查询功能"""
        print("🔍 演示基本查询功能")
        print("-" * 40)
        
        query = "什么是机器学习？"
        print(f"查询问题: {query}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/ask",
                json={
                    "query": query,
                    "options": {
                        "enable_rewriting": True,
                        "enable_hybrid_search": True,
                        "max_results": 3
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"✅ 查询成功")
                    print(f"回答: {result['data']['answer']}")
                    print(f"查询时间: {result['data']['query_info']['search_time']}秒")
                else:
                    print(f"❌ 查询失败: {result.get('error')}")
            else:
                print(f"❌ HTTP 错误: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到服务器，请确保服务已启动")
        except Exception as e:
            print(f"❌ 发生错误: {e}")
    
    def demo_category_query(self):
        """演示分类查询功能"""
        print("\n📂 演示分类查询功能")
        print("-" * 40)
        
        query = "Python编程语言的特点"
        categories = ["technical", "general"]
        print(f"查询问题: {query}")
        print(f"指定类别: {categories}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/ask",
                json={
                    "query": query,
                    "categories": categories,
                    "options": {
                        "enable_rewriting": True,
                        "max_results": 5
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"✅ 分类查询成功")
                    print(f"回答: {result['data']['answer']}")
                    print(f"使用类别: {result['data']['query_info']['categories']}")
                else:
                    print(f"❌ 查询失败: {result.get('error')}")
            else:
                print(f"❌ HTTP 错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 发生错误: {e}")
    
    def demo_batch_query(self):
        """演示批量查询功能"""
        print("\n📋 演示批量查询功能")
        print("-" * 40)
        
        queries = [
            "什么是人工智能？",
            "RAG系统的优势",
            "如何配置向量数据库？"
        ]
        
        print(f"批量查询 {len(queries)} 个问题:")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/ask/batch",
                json={
                    "queries": [{"query": q} for q in queries],
                    "options": {"parallel": True}
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    data = result['data']
                    print(f"✅ 批量查询完成")
                    print(f"总查询数: {data['total_queries']}")
                    print(f"成功查询: {data['successful_queries']}")
                    print(f"总耗时: {data['total_time']}秒")
                    
                    print("\n查询结果:")
                    for i, res in enumerate(data['results'], 1):
                        status = "✅" if res['success'] else "❌"
                        print(f"  {i}. {status} {res['query']}")
                        if res['success']:
                            print(f"     回答: {res['answer'][:100]}...")
                        else:
                            print(f"     错误: {res['error']}")
                else:
                    print(f"❌ 批量查询失败: {result.get('error')}")
            else:
                print(f"❌ HTTP 错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 发生错误: {e}")
    
    def demo_knowledge_management(self):
        """演示知识库管理功能"""
        print("\n📚 演示知识库管理功能")
        print("-" * 40)
        
        try:
            # 获取知识库状态
            print("1. 获取知识库状态...")
            response = self.session.get(f"{self.base_url}/api/v1/knowledge/status")
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    data = result['data']
                    print(f"   ✅ 文档总数: {data['total_documents']}")
                    print(f"   📂 文档类别: {data['categories']}")
                    print(f"   💾 数据库大小: {data['vector_store_size']}")
                else:
                    print(f"   ❌ 获取状态失败: {result.get('error')}")
            
            # 触发同步
            print("\n2. 触发知识库同步...")
            response = self.session.post(f"{self.base_url}/api/v1/knowledge/sync")
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"   ✅ 同步任务已启动: {result['data']['message']}")
                else:
                    print(f"   ❌ 同步失败: {result.get('error')}")
            
        except Exception as e:
            print(f"❌ 发生错误: {e}")
    
    def demo_system_monitoring(self):
        """演示系统监控功能"""
        print("\n📊 演示系统监控功能")
        print("-" * 40)
        
        try:
            # 健康检查
            print("1. 健康检查...")
            response = self.session.get(f"{self.base_url}/api/v1/health")
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    data = result['data']
                    print(f"   ✅ 服务状态: {data['status']}")
                    print(f"   🔢 版本: {data['version']}")
                    print(f"   ⏱️  运行时间: {data['uptime']}秒")
                    print(f"   🔧 组件状态: {data['components']}")
                else:
                    print(f"   ❌ 健康检查失败: {result.get('error')}")
            
            # 服务指标
            print("\n2. 服务指标...")
            response = self.session.get(f"{self.base_url}/api/v1/metrics")
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    data = result['data']
                    print(f"   📈 总查询数: {data['queries_total']}")
                    print(f"   ✅ 成功查询: {data['queries_success']}")
                    print(f"   ❌ 失败查询: {data['queries_error']}")
                    print(f"   ⚡ 平均响应时间: {data['average_response_time']}秒")
                    print(f"   📊 错误率: {data['error_rate']:.2%}")
                else:
                    print(f"   ❌ 获取指标失败: {result.get('error')}")
            
        except Exception as e:
            print(f"❌ 发生错误: {e}")
    
    def demo_performance_test(self):
        """演示性能测试"""
        print("\n🏃‍♂️ 演示性能测试")
        print("-" * 40)
        
        test_queries = [
            "什么是深度学习？",
            "Python的优势有哪些？",
            "如何使用RAG系统？"
        ]
        
        response_times = []
        
        for i, query in enumerate(test_queries, 1):
            print(f"测试查询 {i}: {query}")
            
            try:
                start_time = time.time()
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/ask",
                    json={"query": query}
                )
                
                response_time = time.time() - start_time
                response_times.append(response_time)
                
                if response.status_code == 200:
                    result = response.json()
                    if result['success']:
                        print(f"   ✅ 响应时间: {response_time:.2f}秒")
                    else:
                        print(f"   ❌ 查询失败: {result.get('error')}")
                else:
                    print(f"   ❌ HTTP 错误: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ 发生错误: {e}")
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"\n📊 性能统计:")
            print(f"   平均响应时间: {avg_time:.2f}秒")
            print(f"   最快响应: {min(response_times):.2f}秒")
            print(f"   最慢响应: {max(response_times):.2f}秒")


def main():
    """主函数"""
    print("🌐 RAG API 使用示例演示")
    print("=" * 60)
    
    # 检查服务是否可用
    demo = RAGAPIDemo()
    
    try:
        response = demo.session.get(f"{demo.base_url}/")
        if response.status_code != 200:
            print("❌ 无法连接到 RAG API 服务")
            print("请先启动服务: python start_server.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 RAG API 服务")
        print("请先启动服务: python start_server.py")
        return
    
    print("✅ 服务连接正常，开始演示...")
    
    # 运行各种演示
    demo.demo_basic_query()
    demo.demo_category_query()
    demo.demo_batch_query()
    demo.demo_knowledge_management()
    demo.demo_system_monitoring()
    demo.demo_performance_test()
    
    print("\n" + "=" * 60)
    print("🎉 所有演示完成!")
    print("\n💡 更多功能:")
    print("   - 访问 http://localhost:8000/docs 查看完整 API 文档")
    print("   - 使用 test_api_client.py 进行交互式测试")
    print("   - 查看 README.md 了解详细使用说明")


if __name__ == "__main__":
    main()