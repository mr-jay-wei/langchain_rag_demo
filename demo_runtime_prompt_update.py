#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
演示运行时更新提示词功能
展示如何在不重启服务的情况下动态更新提示词
"""

import asyncio
import time
from pathlib import Path

from rag.prompt_manager import prompt_manager, get_qa_prompt_template
from rag.streaming_pipeline import StreamingRagPipeline


async def demo_runtime_prompt_update():
    """演示运行时提示词更新"""
    print("🌊 运行时提示词更新演示")
    print("=" * 50)
    
    # 1. 初始化RAG系统
    print("\n1. 初始化RAG系统...")
    try:
        rag = StreamingRagPipeline()
        print("✅ RAG系统初始化完成")
    except Exception as e:
        print(f"❌ RAG系统初始化失败: {e}")
        print("💡 请确保已配置好环境变量和数据")
        return
    
    # 2. 显示当前提示词
    print("\n2. 当前提示词内容:")
    current_prompt = prompt_manager.load_prompt("qa_prompt")
    print(f"📝 当前提示词长度: {len(current_prompt)} 字符")
    print(f"📝 提示词预览: {current_prompt[:100]}...")
    
    # 3. 使用当前提示词进行问答
    print("\n3. 使用当前提示词进行问答:")
    test_question = "什么是人工智能？"
    
    print(f"❓ 问题: {test_question}")
    print("🤖 回答: ", end="", flush=True)
    
    try:
        async for event in rag.ask_stream(test_question):
            if event.type.value == "generation_chunk":
                print(event.data["chunk"], end="", flush=True)
            elif event.type.value == "generation_end":
                print("\n✅ 回答完成")
                break
            elif event.type.value == "error":
                print(f"\n❌ 错误: {event.data['error']}")
                break
    except Exception as e:
        print(f"\n❌ 问答过程出错: {e}")
    
    # 4. 备份原始提示词
    print("\n4. 备份原始提示词...")
    original_prompt = current_prompt
    backup_file = Path("rag/prompts/qa_prompt_backup.txt")
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original_prompt)
    print(f"✅ 原始提示词已备份到: {backup_file}")
    
    # 5. 运行时更新提示词
    print("\n5. 运行时更新提示词...")
    new_prompt = """你是一个友好的AI助手。
请根据下面提供的"上下文信息"来回答"问题"。
请用简洁明了的语言回答，并在回答前加上"根据资料显示："。
如果上下文中没有足够的信息，请说："抱歉，我在提供的资料中没有找到相关信息。"

---
上下文信息:
{context}
---

问题: {question}

回答:"""
    
    # 保存新提示词（这会自动清除缓存）
    prompt_manager.save_prompt("qa_prompt", new_prompt)
    print("✅ 新提示词已保存")
    
    # 验证提示词已更新
    updated_prompt = prompt_manager.load_prompt("qa_prompt")
    print(f"📝 更新后提示词长度: {len(updated_prompt)} 字符")
    print(f"📝 更新后提示词预览: {updated_prompt[:100]}...")
    
    # 6. 使用新提示词进行问答（无需重启服务）
    print("\n6. 使用新提示词进行问答（无需重启服务）:")
    print(f"❓ 问题: {test_question}")
    print("🤖 回答: ", end="", flush=True)
    
    try:
        async for event in rag.ask_stream(test_question):
            if event.type.value == "generation_chunk":
                print(event.data["chunk"], end="", flush=True)
            elif event.type.value == "generation_end":
                print("\n✅ 回答完成")
                break
            elif event.type.value == "error":
                print(f"\n❌ 错误: {event.data['error']}")
                break
    except Exception as e:
        print(f"\n❌ 问答过程出错: {e}")
    
    # 7. 演示手动重载功能
    print("\n7. 演示手动重载功能...")
    
    # 直接修改文件（模拟外部编辑）
    manual_prompt = """你是一个专业的技术顾问。
请基于提供的"上下文信息"给出专业的技术解答。
回答要包含技术细节，并在最后加上"以上信息仅供参考"。

---
上下文信息:
{context}
---

问题: {question}

专业解答:"""
    
    # 直接写入文件
    prompt_file = Path("rag/prompts/qa_prompt.txt")
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(manual_prompt)
    print("✅ 直接修改了提示词文件")
    
    # 手动重载（清除缓存）
    prompt_manager.reload_prompt("qa_prompt")
    print("✅ 手动重载提示词完成")
    
    # 验证重载效果
    reloaded_prompt = prompt_manager.load_prompt("qa_prompt")
    print(f"📝 重载后提示词长度: {len(reloaded_prompt)} 字符")
    print(f"📝 重载后提示词预览: {reloaded_prompt[:100]}...")
    
    # 8. 使用重载后的提示词进行问答
    print("\n8. 使用重载后的提示词进行问答:")
    print(f"❓ 问题: {test_question}")
    print("🤖 回答: ", end="", flush=True)
    
    try:
        async for event in rag.ask_stream(test_question):
            if event.type.value == "generation_chunk":
                print(event.data["chunk"], end="", flush=True)
            elif event.type.value == "generation_end":
                print("\n✅ 回答完成")
                break
            elif event.type.value == "error":
                print(f"\n❌ 错误: {event.data['error']}")
                break
    except Exception as e:
        print(f"\n❌ 问答过程出错: {e}")
    
    # 9. 恢复原始提示词
    print("\n9. 恢复原始提示词...")
    prompt_manager.save_prompt("qa_prompt", original_prompt)
    print("✅ 原始提示词已恢复")
    
    # 清理备份文件
    if backup_file.exists():
        backup_file.unlink()
        print("✅ 备份文件已清理")
    
    print("\n" + "=" * 50)
    print("🎉 运行时提示词更新演示完成！")
    print("\n💡 关键要点:")
    print("  ✅ 提示词更新无需重启服务")
    print("  ✅ 缓存机制确保更新立即生效")
    print("  ✅ 支持程序化更新和手动文件编辑")
    print("  ✅ 提供重载功能确保缓存同步")


async def demo_hot_reload_monitoring():
    """演示热重载监控功能"""
    print("\n🔥 热重载监控演示")
    print("=" * 30)
    
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class PromptFileHandler(FileSystemEventHandler):
            def __init__(self, rag_system):
                self.rag_system = rag_system
                
            def on_modified(self, event):
                if event.is_directory:
                    return
                    
                if event.src_path.endswith('.txt') and 'prompts' in event.src_path:
                    prompt_name = Path(event.src_path).stem
                    print(f"🔄 检测到提示词文件变化: {prompt_name}")
                    
                    # 自动重载
                    try:
                        prompt_manager.reload_prompt(prompt_name)
                        print(f"✅ 自动重载完成: {prompt_name}")
                    except Exception as e:
                        print(f"❌ 自动重载失败: {e}")
        
        # 设置文件监控
        rag = StreamingRagPipeline()
        event_handler = PromptFileHandler(rag)
        observer = Observer()
        observer.schedule(event_handler, "rag/prompts", recursive=False)
        observer.start()
        
        print("🔍 文件监控已启动，正在监控 rag/prompts 目录...")
        print("💡 请尝试修改 rag/prompts/qa_prompt.txt 文件")
        print("⏰ 监控将运行30秒...")
        
        # 运行30秒
        await asyncio.sleep(30)
        
        observer.stop()
        observer.join()
        print("🛑 文件监控已停止")
        
    except ImportError:
        print("❌ 需要安装 watchdog 库来支持文件监控:")
        print("   pip install watchdog")


if __name__ == "__main__":
    print("🚀 启动运行时提示词更新演示...")
    
    # 运行主演示
    asyncio.run(demo_runtime_prompt_update())
    
    # 询问是否运行热重载演示
    try:
        choice = input("\n🔥 是否演示热重载监控功能？(y/n): ").lower().strip()
        if choice == 'y':
            asyncio.run(demo_hot_reload_monitoring())
    except KeyboardInterrupt:
        print("\n👋 演示结束")