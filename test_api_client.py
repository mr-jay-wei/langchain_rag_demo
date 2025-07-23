#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG API 客户端测试脚本

用于测试 FastAPI Web 服务的各种接口功能
"""

import requests
import json
import time
from typing import Dict, Any, List


class RAGAPIClient:
    """RAG API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def ask(self, query: str, categories: List[str] = None) -> Dict[str, Any]:
        """发送问答请求"""
        url = f"{self.base_url}/api/v1/ask"
        payload = {
            "query": query,
            "categories": categories,
            "options": {
                "enable_rewriting": True,
                "enable_hybrid_search": True,
                "max_results": 5
            }
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def ask_batch(self, queries: List[str]) -> Dict[str, Any]:
        """发送批量问答请求"""
        url = f"{self.base_url}/api/v1/ask/batch"
        payload = {
            "queries": [{"query": q} for q in queries],
            "options": {"parallel": True}
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_knowledge_status(self) -> Dict[str, Any]:
        """获取知识库状态"""
        url = f"{self.base_url}/api/v1/knowledge/status"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def sync_knowledge(self) -> Dict[str, Any]:
        """触发知识库同步"""
        url = f"{self.base_url}/api/v1/knowledge/sync"
        response = self.session.post(url)
        response.raise_for_status()
        return response.json()
    
    def get_health(self) -> Dict[str, Any]:
        """获取健康状态"""
        url = f"{self.base_url}/api/v1/health"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取服务指标"""
        url = f"{self.base_url}/api/v1/metrics"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()


def print_response(title: str, response: Dict[str, Any]):
    """格式化打印响应结果"""
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print(f"{'='*50}")
    print(json.dumps(response, ensure_ascii=False, indent=2))


def test_basic_functionality():
    """测试基本功能"""
    print("🚀 开始测试 RAG API 基本功能...")
    
    client = RAGAPIClient()
    
    try:
        # 1. 健康检查
        print("\n1️⃣ 测试健康检查...")
        health = client.get_health()
        print_response("健康检查结果", health)
        
        # 2. 知识库状态
        print("\n2️⃣ 测试知识库状态...")
        status = client.get_knowledge_status()
        print_response("知识库状态", status)
        
        # 3. 基本问答
        print("\n3️⃣ 测试基本问答...")
        result = client.ask("什么是机器学习？")
        print_response("问答结果", result)
        
        # 4. 分类查询
        print("\n4️⃣ 测试分类查询...")
        result = client.ask("Python有什么特点？", categories=["technical"])
        print_response("分类查询结果", result)
        
        # 5. 批量查询
        print("\n5️⃣ 测试批量查询...")
        queries = [
            "什么是人工智能？",
            "RAG系统的优势是什么？",
            "如何配置向量数据库？"
        ]
        result = client.ask_batch(queries)
        print_response("批量查询结果", result)
        
        # 6. 服务指标
        print("\n6️⃣ 测试服务指标...")
        metrics = client.get_metrics()
        print_response("服务指标", metrics)
        
        print("\n✅ 所有测试完成!")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 API 服务，请确保服务已启动 (python app.py)")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")


def test_performance():
    """性能测试"""
    print("\n🏃‍♂️ 开始性能测试...")
    
    client = RAGAPIClient()
    
    test_queries = [
        "什么是机器学习？",
        "Python编程语言的特点",
        "如何使用RAG系统？",
        "向量数据库的优势",
        "人工智能的应用领域"
    ]
    
    response_times = []
    
    for i, query in enumerate(test_queries, 1):
        try:
            print(f"📝 测试查询 {i}: {query}")
            start_time = time.time()
            
            result = client.ask(query)
            
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            print(f"   ⏱️  响应时间: {response_time:.2f}秒")
            print(f"   ✅ 查询成功: {result['success']}")
            
        except Exception as e:
            print(f"   ❌ 查询失败: {e}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"\n📊 性能统计:")
        print(f"   平均响应时间: {avg_time:.2f}秒")
        print(f"   最快响应时间: {min_time:.2f}秒")
        print(f"   最慢响应时间: {max_time:.2f}秒")
        print(f"   总查询次数: {len(response_times)}")


def interactive_test():
    """交互式测试"""
    print("\n💬 进入交互式测试模式...")
    print("输入 'quit' 或 'exit' 退出")
    
    client = RAGAPIClient()
    
    while True:
        try:
            query = input("\n🤔 请输入您的问题: ").strip()
            
            if query.lower() in ['quit', 'exit', '退出']:
                print("👋 再见!")
                break
            
            if not query:
                continue
            
            print("🔍 正在查询...")
            start_time = time.time()
            
            result = client.ask(query)
            response_time = time.time() - start_time
            
            if result['success']:
                answer = result['data']['answer']
                search_time = result['data']['query_info']['search_time']
                
                print(f"\n💡 回答:")
                print(f"{answer}")
                print(f"\n⏱️  查询时间: {search_time:.2f}秒")
            else:
                print(f"❌ 查询失败: {result.get('error', '未知错误')}")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")


def main():
    """主函数"""
    print("🌐 RAG API 客户端测试工具")
    print("=" * 50)
    
    while True:
        print("\n请选择测试模式:")
        print("1. 基本功能测试")
        print("2. 性能测试")
        print("3. 交互式测试")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == '1':
            test_basic_functionality()
        elif choice == '2':
            test_performance()
        elif choice == '3':
            interactive_test()
        elif choice == '4':
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择，请重新输入")


if __name__ == "__main__":
    main()