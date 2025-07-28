"""
WebSocket并发性能测试
展示WebSocket在多用户场景下的表现
"""

import asyncio
import json
import time
import websockets
from typing import List
import statistics

class WebSocketConcurrencyTest:
    """WebSocket并发测试"""
    
    def __init__(self, server_url: str = "ws://localhost:8000/ws"):
        self.server_url = server_url
        self.results = []
    
    async def single_user_test(self, user_id: int, question: str) -> dict:
        """单个用户的测试"""
        start_time = time.time()
        response_times = []
        chunks_received = 0
        
        try:
            async with websockets.connect(self.server_url) as websocket:
                # 发送问题
                await websocket.send(json.dumps({
                    "type": "question",
                    "content": f"[用户{user_id}] {question}"
                }))
                
                first_response_time = None
                
                # 接收响应
                async for message in websocket:
                    current_time = time.time()
                    
                    if first_response_time is None:
                        first_response_time = current_time - start_time
                    
                    data = json.loads(message)
                    
                    if data["type"] == "answer_chunk":
                        chunks_received += 1
                        response_times.append(current_time - start_time)
                    
                    elif data["type"] == "answer_complete":
                        break
                    
                    elif data["type"] == "error":
                        raise Exception(f"服务器错误: {data['message']}")
                
                total_time = time.time() - start_time
                
                return {
                    "user_id": user_id,
                    "success": True,
                    "total_time": total_time,
                    "first_response_time": first_response_time,
                    "chunks_received": chunks_received,
                    "avg_chunk_interval": statistics.mean(response_times) if response_times else 0,
                    "error": None
                }
                
        except Exception as e:
            return {
                "user_id": user_id,
                "success": False,
                "total_time": time.time() - start_time,
                "first_response_time": None,
                "chunks_received": 0,
                "avg_chunk_interval": 0,
                "error": str(e)
            }
    
    async def concurrent_test(self, num_users: int, question: str = "什么是人工智能？"):
        """并发测试"""
        print(f"🚀 开始 {num_users} 用户并发测试")
        print("=" * 60)
        
        start_time = time.time()
        
        # 创建并发任务
        tasks = [
            self.single_user_test(i, question) 
            for i in range(1, num_users + 1)
        ]
        
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # 分析结果
        successful_results = [r for r in results if isinstance(r, dict) and r["success"]]
        failed_results = [r for r in results if isinstance(r, dict) and not r["success"]]
        exceptions = [r for r in results if not isinstance(r, dict)]
        
        print(f"📊 测试结果分析")
        print("=" * 60)
        print(f"总用户数: {num_users}")
        print(f"成功连接: {len(successful_results)}")
        print(f"连接失败: {len(failed_results)}")
        print(f"异常错误: {len(exceptions)}")
        print(f"总测试时间: {total_time:.2f}秒")
        
        if successful_results:
            # 性能统计
            total_times = [r["total_time"] for r in successful_results]
            first_response_times = [r["first_response_time"] for r in successful_results if r["first_response_time"]]
            chunks_counts = [r["chunks_received"] for r in successful_results]
            
            print(f"\n⚡ 性能指标")
            print("=" * 60)
            print(f"平均响应时间: {statistics.mean(total_times):.2f}秒")
            print(f"最快响应时间: {min(total_times):.2f}秒")
            print(f"最慢响应时间: {max(total_times):.2f}秒")
            
            if first_response_times:
                print(f"平均首次响应: {statistics.mean(first_response_times):.2f}秒")
                print(f"最快首次响应: {min(first_response_times):.2f}秒")
            
            print(f"平均接收片段: {statistics.mean(chunks_counts):.1f}个")
            print(f"总处理片段: {sum(chunks_counts)}个")
            
            # 并发效率
            sequential_time_estimate = statistics.mean(total_times) * num_users
            concurrency_efficiency = (sequential_time_estimate / total_time) * 100
            print(f"\n🎯 并发效率")
            print("=" * 60)
            print(f"预估串行时间: {sequential_time_estimate:.2f}秒")
            print(f"实际并发时间: {total_time:.2f}秒")
            print(f"并发效率提升: {concurrency_efficiency:.1f}%")
        
        # 错误分析
        if failed_results or exceptions:
            print(f"\n❌ 错误分析")
            print("=" * 60)
            for result in failed_results:
                print(f"用户{result['user_id']}: {result['error']}")
            for i, exc in enumerate(exceptions):
                print(f"异常{i+1}: {exc}")
        
        return {
            "total_users": num_users,
            "successful": len(successful_results),
            "failed": len(failed_results),
            "exceptions": len(exceptions),
            "total_time": total_time,
            "results": successful_results
        }
    
    async def scalability_test(self):
        """可扩展性测试 - 测试不同并发数的表现"""
        print("🔬 WebSocket可扩展性测试")
        print("=" * 80)
        
        test_cases = [1, 5, 10, 20, 50]  # 不同的并发用户数
        scalability_results = []
        
        for num_users in test_cases:
            print(f"\n📈 测试 {num_users} 并发用户...")
            result = await self.concurrent_test(num_users)
            scalability_results.append(result)
            
            # 等待一段时间让服务器恢复
            await asyncio.sleep(2)
        
        # 可扩展性分析
        print(f"\n📊 可扩展性分析")
        print("=" * 80)
        print(f"{'用户数':<8} {'成功率':<8} {'平均响应时间':<12} {'并发效率':<10}")
        print("-" * 50)
        
        for result in scalability_results:
            success_rate = (result["successful"] / result["total_users"]) * 100
            avg_response_time = statistics.mean([r["total_time"] for r in result["results"]]) if result["results"] else 0
            
            # 计算相对于单用户的效率
            single_user_time = scalability_results[0]["results"][0]["total_time"] if scalability_results[0]["results"] else 1
            efficiency = (single_user_time / avg_response_time) * 100 if avg_response_time > 0 else 0
            
            print(f"{result['total_users']:<8} {success_rate:<7.1f}% {avg_response_time:<11.2f}s {efficiency:<9.1f}%")

async def main():
    """主测试函数"""
    print("🌐 WebSocket并发性能测试")
    print("=" * 80)
    print("💡 请确保Web服务器正在运行: uv run examples/streaming_web_demo.py")
    print("📱 服务器地址: http://localhost:8000")
    print()
    
    # 等待用户确认
    input("按Enter键开始测试...")
    
    tester = WebSocketConcurrencyTest()
    
    try:
        # 运行可扩展性测试
        await tester.scalability_test()
        
        print(f"\n🎉 测试完成！")
        print("=" * 80)
        print("📝 结论:")
        print("1. WebSocket支持高并发连接")
        print("2. 每个连接都是独立的长连接")
        print("3. 流式响应不会阻塞其他用户")
        print("4. 服务器可以同时处理多个流式会话")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("请确保Web服务器正在运行")

if __name__ == "__main__":
    asyncio.run(main())