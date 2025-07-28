# examples/async_vs_threading_explanation.py - async/await vs 线程池详解

import asyncio
import threading
import time
# import aiohttp  # 注释掉，避免依赖问题
# import aiofiles
from concurrent.futures import ThreadPoolExecutor

def show_thread_info(label: str):
    """显示当前线程信息"""
    thread_id = threading.get_ident()
    thread_name = threading.current_thread().name
    print(f"  {label}: 线程ID={thread_id}, 线程名={thread_name}")

async def demonstrate_async_single_thread():
    """演示 async/await 是单线程的"""
    print("🧵 演示 async/await 的单线程特性")
    print("=" * 50)
    
    show_thread_info("主程序开始")
    
    async def async_task_1():
        show_thread_info("异步任务1开始")
        await asyncio.sleep(1)  # 模拟I/O等待
        show_thread_info("异步任务1结束")
        return "任务1完成"
    
    async def async_task_2():
        show_thread_info("异步任务2开始")
        await asyncio.sleep(0.5)  # 模拟I/O等待
        show_thread_info("异步任务2结束")
        return "任务2完成"
    
    async def async_task_3():
        show_thread_info("异步任务3开始")
        await asyncio.sleep(0.8)  # 模拟I/O等待
        show_thread_info("异步任务3结束")
        return "任务3完成"
    
    print("\n🔄 并发执行3个异步任务...")
    start_time = time.time()
    
    # 并发执行多个异步任务
    results = await asyncio.gather(
        async_task_1(),
        async_task_2(), 
        async_task_3()
    )
    
    end_time = time.time()
    show_thread_info("主程序结束")
    
    print(f"\n📊 结果: {results}")
    print(f"⏱️  总耗时: {end_time - start_time:.2f}秒")
    print("💡 观察: 所有任务都在同一个线程中执行！")

def demonstrate_thread_pool():
    """演示线程池的多线程特性"""
    print("\n" + "=" * 50)
    print("🧵 演示线程池的多线程特性")
    print("=" * 50)
    
    show_thread_info("主程序开始")
    
    def blocking_task(task_id: int, duration: float):
        show_thread_info(f"线程池任务{task_id}开始")
        time.sleep(duration)  # 阻塞操作
        show_thread_info(f"线程池任务{task_id}结束")
        return f"任务{task_id}完成"
    
    print("\n🔄 使用线程池执行3个阻塞任务...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        # 提交任务到线程池
        futures = [
            executor.submit(blocking_task, 1, 1.0),
            executor.submit(blocking_task, 2, 0.5),
            executor.submit(blocking_task, 3, 0.8)
        ]
        
        # 等待所有任务完成
        results = [future.result() for future in futures]
    
    end_time = time.time()
    show_thread_info("主程序结束")
    
    print(f"\n📊 结果: {results}")
    print(f"⏱️  总耗时: {end_time - start_time:.2f}秒")
    print("💡 观察: 每个任务都在不同的线程中执行！")

async def demonstrate_async_io_operations():
    """演示 async/await 处理真实的I/O操作"""
    print("\n" + "=" * 50)
    print("🌐 演示 async/await 处理真实I/O操作")
    print("=" * 50)
    
    show_thread_info("开始I/O操作")
    
    async def async_file_operation():
        show_thread_info("文件操作开始")
        # 模拟异步文件操作
        await asyncio.sleep(0.5)  # 在真实场景中这里会是 aiofiles.open()
        show_thread_info("文件操作结束")
        return "文件读取完成"
    
    async def async_network_operation():
        show_thread_info("网络操作开始")
        # 模拟异步网络请求
        await asyncio.sleep(0.8)  # 在真实场景中这里会是 aiohttp.get()
        show_thread_info("网络操作结束")
        return "网络请求完成"
    
    async def async_database_operation():
        show_thread_info("数据库操作开始")
        # 模拟异步数据库查询
        await asyncio.sleep(0.3)  # 在真实场景中这里会是 await conn.execute()
        show_thread_info("数据库操作结束")
        return "数据库查询完成"
    
    start_time = time.time()
    
    # 并发执行I/O操作
    results = await asyncio.gather(
        async_file_operation(),
        async_network_operation(),
        async_database_operation()
    )
    
    end_time = time.time()
    show_thread_info("I/O操作全部完成")
    
    print(f"\n📊 结果: {results}")
    print(f"⏱️  总耗时: {end_time - start_time:.2f}秒")
    print("💡 关键点: 所有I/O操作都在同一线程中并发执行！")

async def demonstrate_mixed_approach():
    """演示混合方法：async/await + 线程池"""
    print("\n" + "=" * 50)
    print("🔀 演示混合方法：async/await + 线程池")
    print("=" * 50)
    
    show_thread_info("混合方法开始")
    
    # CPU密集型任务（需要线程池）
    def cpu_intensive_task(task_id: int):
        show_thread_info(f"CPU任务{task_id}开始")
        # 模拟CPU密集型计算
        total = 0
        for i in range(1000000):
            total += i * i
        show_thread_info(f"CPU任务{task_id}结束")
        return f"CPU任务{task_id}完成，结果={total}"
    
    # I/O密集型任务（直接用async/await）
    async def io_intensive_task(task_id: int):
        show_thread_info(f"I/O任务{task_id}开始")
        await asyncio.sleep(0.5)  # 模拟I/O等待
        show_thread_info(f"I/O任务{task_id}结束")
        return f"I/O任务{task_id}完成"
    
    start_time = time.time()
    
    # 创建线程池
    executor = ThreadPoolExecutor(max_workers=2)
    loop = asyncio.get_event_loop()
    
    # 混合执行：I/O任务用async/await，CPU任务用线程池
    results = await asyncio.gather(
        # I/O任务 - 直接用async/await
        io_intensive_task(1),
        io_intensive_task(2),
        
        # CPU任务 - 使用线程池
        loop.run_in_executor(executor, cpu_intensive_task, 1),
        loop.run_in_executor(executor, cpu_intensive_task, 2)
    )
    
    end_time = time.time()
    executor.shutdown(wait=True)
    show_thread_info("混合方法结束")
    
    print(f"\n📊 结果:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result}")
    print(f"⏱️  总耗时: {end_time - start_time:.2f}秒")
    print("💡 关键点: I/O任务在主线程，CPU任务在线程池！")

async def demonstrate_event_loop_internals():
    """演示事件循环的内部工作机制"""
    print("\n" + "=" * 50)
    print("⚙️ 事件循环内部工作机制演示")
    print("=" * 50)
    
    async def show_event_loop_behavior():
        show_thread_info("事件循环开始")
        
        print("\n📋 事件循环处理步骤:")
        
        # 步骤1: 注册多个协程
        print("1. 注册协程到事件循环")
        
        async def coroutine_a():
            print("  协程A: 开始执行")
            show_thread_info("协程A")
            await asyncio.sleep(0.1)  # 让出控制权
            print("  协程A: 恢复执行")
            return "A完成"
        
        async def coroutine_b():
            print("  协程B: 开始执行")
            show_thread_info("协程B")
            await asyncio.sleep(0.05)  # 让出控制权
            print("  协程B: 恢复执行")
            return "B完成"
        
        # 步骤2: 事件循环调度
        print("2. 事件循环开始调度")
        
        # 创建任务但不立即等待
        task_a = asyncio.create_task(coroutine_a())
        task_b = asyncio.create_task(coroutine_b())
        
        print("3. 协程在事件循环中交替执行")
        
        # 等待所有任务完成
        results = await asyncio.gather(task_a, task_b)
        
        print("4. 所有协程执行完成")
        show_thread_info("事件循环结束")
        
        return results
    
    # 运行事件循环演示
    results = await show_event_loop_behavior()
    print(f"\n📊 最终结果: {results}")
    print("💡 关键观察: 整个过程只使用了一个线程！")

async def compare_performance():
    """性能对比：async/await vs 线程池 vs 混合方法"""
    print("\n" + "=" * 50)
    print("⚡ 性能对比测试")
    print("=" * 50)
    
    # 测试数据
    task_count = 5
    io_duration = 0.2
    
    # 方法1: 纯同步（串行）
    def sync_approach():
        print("🔄 同步方法（串行执行）")
        show_thread_info("同步方法")
        start = time.time()
        
        results = []
        for i in range(task_count):
            time.sleep(io_duration)  # 阻塞I/O
            results.append(f"同步任务{i+1}")
        
        return time.time() - start, results
    
    # 方法2: async/await（并发）
    async def async_approach():
        print("⚡ async/await方法（并发执行）")
        show_thread_info("async/await方法")
        start = time.time()
        
        async def async_task(task_id):
            await asyncio.sleep(io_duration)  # 非阻塞I/O
            return f"异步任务{task_id}"
        
        tasks = [async_task(i+1) for i in range(task_count)]
        results = await asyncio.gather(*tasks)
        
        return time.time() - start, results
    
    # 方法3: 线程池（并行）
    def thread_pool_approach():
        print("🧵 线程池方法（并行执行）")
        show_thread_info("线程池方法")
        start = time.time()
        
        def blocking_task(task_id):
            time.sleep(io_duration)  # 阻塞I/O
            return f"线程池任务{task_id}"
        
        with ThreadPoolExecutor(max_workers=task_count) as executor:
            futures = [executor.submit(blocking_task, i+1) for i in range(task_count)]
            results = [future.result() for future in futures]
        
        return time.time() - start, results
    
    # 执行测试
    print(f"📝 测试场景: {task_count}个I/O任务，每个耗时{io_duration}秒\n")
    
    # 同步测试
    sync_time, sync_results = sync_approach()
    print(f"  ⏱️  耗时: {sync_time:.2f}秒\n")
    
    # 异步测试
    async_time, async_results = await async_approach()
    print(f"  ⏱️  耗时: {async_time:.2f}秒\n")
    
    # 线程池测试
    thread_time, thread_results = thread_pool_approach()
    print(f"  ⏱️  耗时: {thread_time:.2f}秒\n")
    
    # 性能对比
    print("📊 性能对比总结:")
    print(f"  同步方法:     {sync_time:.2f}秒 (基准)")
    print(f"  async/await: {async_time:.2f}秒 (提升 {((sync_time - async_time) / sync_time * 100):.0f}%)")
    print(f"  线程池:       {thread_time:.2f}秒 (提升 {((sync_time - thread_time) / sync_time * 100):.0f}%)")
    
    print(f"\n💡 结论:")
    print(f"  - 对于I/O密集型任务，async/await和线程池都能显著提升性能")
    print(f"  - async/await使用单线程，资源开销更小")
    print(f"  - 线程池使用多线程，但有线程创建和切换开销")

async def main():
    """主函数"""
    await demonstrate_async_single_thread()
    demonstrate_thread_pool()
    await demonstrate_async_io_operations()
    await demonstrate_mixed_approach()
    await demonstrate_event_loop_internals()
    await compare_performance()
    
    print("\n" + "=" * 60)
    print("🎓 核心要点总结")
    print("=" * 60)
    print("1. async/await 是单线程的协程机制，不创建新线程")
    print("2. 事件循环在单线程中调度多个协程")
    print("3. 线程池才是真正的多线程并行执行")
    print("4. I/O密集型任务 → 用 async/await")
    print("5. CPU密集型任务 → 用线程池")
    print("6. 混合场景 → async/await + 线程池")
    print("7. async/await 的优势：资源开销小，无线程切换成本")
    print("8. 线程池的优势：真正并行，适合CPU密集型任务")

if __name__ == "__main__":
    asyncio.run(main())