# test/test_async_vs_sync_comparison.py - 异步方案对比测试

import asyncio
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import hashlib

def cpu_intensive_task(data: str, duration: float = 0.1):
    """模拟CPU密集型任务"""
    # 模拟向量计算或文本处理
    start = time.time()
    while time.time() - start < duration:
        # 执行一些CPU密集型计算
        hash_result = hashlib.md5(data.encode()).hexdigest()
        for i in range(1000):
            hash_result = hashlib.md5(hash_result.encode()).hexdigest()
    return f"处理完成: {data[:20]}..."

async def io_intensive_task(data: str, duration: float = 0.1):
    """模拟I/O密集型任务"""
    # 模拟网络请求或文件读取
    await asyncio.sleep(duration)
    return f"I/O完成: {data[:20]}..."

# ❌ 方案1: 错误的异步方案 - 直接改成async def但内部仍是同步
async def wrong_async_approach(tasks_data):
    """错误的异步方案：直接在async函数中调用同步的CPU密集型任务"""
    print("🚫 错误方案：直接在async函数中调用CPU密集型任务")
    results = []
    
    for data in tasks_data:
        # 这里虽然是async函数，但cpu_intensive_task会阻塞事件循环
        result = cpu_intensive_task(data)  # 阻塞！
        results.append(result)
    
    return results

# ✅ 方案2: 正确的异步方案 - 使用线程池
async def correct_async_approach(tasks_data):
    """正确的异步方案：使用线程池处理CPU密集型任务"""
    print("✅ 正确方案：使用线程池处理CPU密集型任务")
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        loop = asyncio.get_event_loop()
        
        # 并发执行CPU密集型任务
        tasks = [
            loop.run_in_executor(executor, cpu_intensive_task, data)
            for data in tasks_data
        ]
        
        results = await asyncio.gather(*tasks)
    
    return results

# 📊 方案3: 纯I/O异步方案 - 可以直接使用async/await
async def pure_io_async_approach(tasks_data):
    """纯I/O异步方案：可以直接使用async/await"""
    print("💡 I/O方案：直接使用async/await")
    
    # 并发执行I/O密集型任务
    tasks = [io_intensive_task(data) for data in tasks_data]
    results = await asyncio.gather(*tasks)
    
    return results

# 🔄 同步方案对比
def sync_approach(tasks_data):
    """同步方案"""
    print("🔄 同步方案：顺序执行")
    results = []
    
    for data in tasks_data:
        result = cpu_intensive_task(data)
        results.append(result)
    
    return results

async def performance_comparison():
    """性能对比测试"""
    print("=" * 60)
    print("🧪 异步方案性能对比测试")
    print("=" * 60)
    
    # 测试数据
    test_data = [f"任务数据_{i}" for i in range(5)]
    
    print(f"📝 测试数据: {len(test_data)} 个CPU密集型任务")
    print()
    
    # 1. 同步方案测试
    print("1️⃣ 同步方案测试")
    start_time = time.time()
    sync_results = sync_approach(test_data)
    sync_time = time.time() - start_time
    print(f"   ⏱️ 耗时: {sync_time:.2f}秒")
    print()
    
    # 2. 错误的异步方案测试
    print("2️⃣ 错误的异步方案测试")
    start_time = time.time()
    wrong_results = await wrong_async_approach(test_data)
    wrong_time = time.time() - start_time
    print(f"   ⏱️ 耗时: {wrong_time:.2f}秒")
    print("   ⚠️ 注意：这种方案实际上是串行执行，没有真正的并发！")
    print()
    
    # 3. 正确的异步方案测试
    print("3️⃣ 正确的异步方案测试（使用线程池）")
    start_time = time.time()
    correct_results = await correct_async_approach(test_data)
    correct_time = time.time() - start_time
    print(f"   ⏱️ 耗时: {correct_time:.2f}秒")
    print()
    
    # 4. 纯I/O异步方案测试
    print("4️⃣ 纯I/O异步方案测试")
    start_time = time.time()
    io_results = await pure_io_async_approach(test_data)
    io_time = time.time() - start_time
    print(f"   ⏱️ 耗时: {io_time:.2f}秒")
    print()
    
    # 性能对比总结
    print("📊 性能对比总结:")
    print(f"   同步方案:           {sync_time:.2f}秒")
    print(f"   错误异步方案:       {wrong_time:.2f}秒 (无改善)")
    print(f"   正确异步方案(线程池): {correct_time:.2f}秒 (提升 {((sync_time - correct_time) / sync_time * 100):.1f}%)")
    print(f"   纯I/O异步方案:      {io_time:.2f}秒 (提升 {((sync_time - io_time) / sync_time * 100):.1f}%)")
    print()
    
    # 结论
    print("💡 结论:")
    print("   1. 直接将同步函数改成async def不会带来性能提升")
    print("   2. CPU密集型任务需要使用线程池才能实现真正的并发")
    print("   3. I/O密集型任务可以直接使用async/await获得很好的并发效果")
    print("   4. 混合场景（CPU + I/O）需要根据具体情况选择合适的方案")

async def demonstrate_event_loop_blocking():
    """演示事件循环阻塞问题"""
    print("\n" + "=" * 60)
    print("🚫 事件循环阻塞演示")
    print("=" * 60)
    
    async def monitor_task():
        """监控任务，每秒打印一次"""
        for i in range(10):
            print(f"   监控器: {i+1}秒 - 事件循环正常运行")
            await asyncio.sleep(1)
    
    async def blocking_task():
        """阻塞任务"""
        print("🚫 开始执行阻塞任务（3秒CPU密集型计算）...")
        # 这会阻塞事件循环3秒
        cpu_intensive_task("阻塞测试", 3.0)
        print("🚫 阻塞任务完成")
    
    async def non_blocking_task():
        """非阻塞任务"""
        print("✅ 开始执行非阻塞任务（3秒线程池计算）...")
        with ThreadPoolExecutor(max_workers=1) as executor:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(executor, cpu_intensive_task, "非阻塞测试", 3.0)
        print("✅ 非阻塞任务完成")
    
    print("1️⃣ 阻塞方案测试：")
    print("   启动监控器和阻塞任务...")
    
    # 创建监控任务
    monitor = asyncio.create_task(monitor_task())
    
    # 执行阻塞任务
    await blocking_task()
    
    # 取消监控任务
    monitor.cancel()
    
    print("\n   结果：监控器被阻塞，无法正常输出")
    print()
    
    print("2️⃣ 非阻塞方案测试：")
    print("   启动监控器和非阻塞任务...")
    
    # 重新创建监控任务
    monitor = asyncio.create_task(monitor_task())
    
    # 执行非阻塞任务
    await non_blocking_task()
    
    # 等待一下让监控器继续运行
    await asyncio.sleep(2)
    
    # 取消监控任务
    monitor.cancel()
    
    print("\n   结果：监控器正常运行，事件循环未被阻塞")

async def main():
    """主测试函数"""
    await performance_comparison()
    await demonstrate_event_loop_blocking()
    
    print("\n" + "=" * 60)
    print("🎓 学习要点总结")
    print("=" * 60)
    print("1. async/await 只对 I/O 密集型任务有效")
    print("2. CPU 密集型任务需要使用线程池或进程池")
    print("3. 不要在 async 函数中直接调用阻塞的同步函数")
    print("4. 使用 loop.run_in_executor() 将 CPU 任务移到线程池")
    print("5. 正确的异步设计可以显著提升并发性能")

if __name__ == "__main__":
    asyncio.run(main())