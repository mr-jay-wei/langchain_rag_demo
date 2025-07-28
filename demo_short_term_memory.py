#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
短期记忆功能演示脚本
展示RAG系统如何使用短期记忆来维持对话上下文
"""

import asyncio
import time
from typing import List

from rag.streaming_pipeline import StreamingRagPipeline
from rag.memory_manager import memory_manager
from rag import config


async def demo_basic_memory():
    """演示基础的短期记忆功能"""
    print("🧠 短期记忆功能演示")
    print("=" * 50)
    
    # 1. 初始化RAG系统
    print("\n1. 初始化流式RAG系统...")
    try:
        rag = StreamingRagPipeline()
        print("✅ RAG系统初始化完成")
    except Exception as e:
        print(f"❌ RAG系统初始化失败: {e}")
        print("💡 请确保已配置好环境变量和数据")
        return
    
    # 2. 显示记忆配置
    print(f"\n2. 短期记忆配置:")
    print(f"   - 启用状态: {config.ENABLE_SHORT_TERM_MEMORY}")
    print(f"   - 最大长度: {config.SHORT_TERM_MEMORY_MAX_LENGTH:,} 字符")
    print(f"   - 最小保留轮数: {config.MIN_CONVERSATION_ROUNDS}")
    print(f"   - 清理策略: {config.MEMORY_CLEANUP_STRATEGY}")
    
    # 3. 进行一系列对话来演示记忆功能
    print(f"\n3. 开始对话演示...")
    
    test_questions = [
        "什么是人工智能？",
        "它有哪些应用领域？",  # 这里的"它"应该能通过记忆理解为"人工智能"
        "机器学习和深度学习有什么区别？",
        "刚才提到的应用领域中，哪个最重要？",  # 引用之前的对话内容
        "请总结一下我们刚才讨论的内容"  # 需要基于整个对话历史
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n--- 第{i}轮对话 ---")
        print(f"👤 用户: {question}")
        print("🤖 助手: ", end="", flush=True)
        
        try:
            # 使用流式问答，启用记忆功能
            async for event in rag.ask_stream(question, use_memory=True):
                if event.type.value == "generation_chunk":
                    print(event.data["chunk"], end="", flush=True)
                elif event.type.value == "generation_end":
                    print()  # 换行
                    break
                elif event.type.value == "error":
                    print(f"\n❌ 错误: {event.data['error']}")
                    break
        except Exception as e:
            print(f"\n❌ 对话过程出错: {e}")
        
        # 显示当前记忆状态
        stats = memory_manager.get_memory_stats()
        print(f"📊 记忆状态: {stats['total_conversations']}轮对话, "
              f"{stats['total_char_length']:,}字符 "
              f"({stats['memory_usage_percent']:.1f}%)")
        
        # 短暂暂停
        await asyncio.sleep(1)


async def demo_memory_management():
    """演示记忆管理功能"""
    print(f"\n🔧 记忆管理功能演示")
    print("=" * 30)
    
    # 1. 查看详细记忆统计
    stats = memory_manager.get_memory_stats()
    print(f"\n1. 详细记忆统计:")
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    # 2. 查看最近的对话记录
    print(f"\n2. 最近3轮对话记录:")
    recent_conversations = memory_manager.get_recent_conversations(3)
    for i, conv in enumerate(recent_conversations, 1):
        print(f"   第{i}轮 ({conv.get_formatted_time()}):")
        print(f"     问: {conv.question[:50]}...")
        print(f"     答: {conv.answer[:50]}...")
    
    # 3. 搜索对话历史
    print(f"\n3. 搜索功能演示:")
    search_results = memory_manager.search_conversations("人工智能", limit=3)
    print(f"   搜索'人工智能'找到 {len(search_results)} 条记录:")
    for idx, (pos, conv) in enumerate(search_results, 1):
        print(f"     {idx}. 位置{pos}: {conv.question[:30]}...")
    
    # 4. 获取对话上下文
    print(f"\n4. 对话上下文格式:")
    context = memory_manager.get_conversation_context(include_count=2)
    if context:
        print("   " + context.replace("\n", "\n   ")[:200] + "...")
    else:
        print("   (无对话上下文)")


async def demo_memory_limits():
    """演示记忆限制和清理功能"""
    print(f"\n🗑️ 记忆限制和清理演示")
    print("=" * 30)
    
    # 1. 显示当前记忆使用情况
    stats = memory_manager.get_memory_stats()
    print(f"\n1. 当前记忆使用情况:")
    print(f"   - 总字符数: {stats['total_char_length']:,}")
    print(f"   - 使用率: {stats['memory_usage_percent']:.1f}%")
    print(f"   - 对话轮数: {stats['total_conversations']}")
    
    # 2. 手动清理演示
    if stats['total_conversations'] > 3:
        print(f"\n2. 手动清理演示 (保留最近2轮对话):")
        removed_count = memory_manager.remove_old_conversations(keep_count=2)
        print(f"   ✅ 已移除 {removed_count} 轮旧对话")
        
        # 显示清理后的状态
        new_stats = memory_manager.get_memory_stats()
        print(f"   - 清理后字符数: {new_stats['total_char_length']:,}")
        print(f"   - 清理后对话轮数: {new_stats['total_conversations']}")
    
    # 3. 导出记忆功能演示
    print(f"\n3. 导出记忆功能演示:")
    export_file = "memory_export.json"
    if memory_manager.export_conversations(export_file):
        print(f"   ✅ 记忆已导出到: {export_file}")
        
        # 清空记忆
        cleared_count = memory_manager.clear_memory()
        print(f"   🗑️ 已清空 {cleared_count} 轮对话")
        
        # 重新导入
        if memory_manager.import_conversations(export_file):
            print(f"   📥 记忆已重新导入")
            
            # 清理导出文件
            import os
            if os.path.exists(export_file):
                os.remove(export_file)
                print(f"   🧹 已清理导出文件")


async def demo_memory_with_different_modes():
    """演示不同模式下的记忆功能"""
    print(f"\n🔄 不同模式下的记忆功能演示")
    print("=" * 35)
    
    try:
        rag = StreamingRagPipeline()
        
        # 1. 启用记忆模式
        print(f"\n1. 启用记忆模式对话:")
        question1 = "什么是深度学习？"
        print(f"👤 用户: {question1}")
        print("🤖 助手: ", end="", flush=True)
        
        async for event in rag.ask_stream(question1, use_memory=True):
            if event.type.value == "generation_chunk":
                print(event.data["chunk"], end="", flush=True)
            elif event.type.value == "generation_end":
                print()
                break
        
        # 2. 禁用记忆模式
        print(f"\n2. 禁用记忆模式对话:")
        question2 = "它和传统机器学习有什么区别？"  # 这里的"它"在禁用记忆时无法理解
        print(f"👤 用户: {question2}")
        print("🤖 助手: ", end="", flush=True)
        
        async for event in rag.ask_stream(question2, use_memory=False):
            if event.type.value == "generation_chunk":
                print(event.data["chunk"], end="", flush=True)
            elif event.type.value == "generation_end":
                print()
                break
        
        # 3. 重新启用记忆模式
        print(f"\n3. 重新启用记忆模式对话:")
        question3 = "它和传统机器学习有什么区别？"  # 现在应该能理解"它"指的是深度学习
        print(f"👤 用户: {question3}")
        print("🤖 助手: ", end="", flush=True)
        
        async for event in rag.ask_stream(question3, use_memory=True):
            if event.type.value == "generation_chunk":
                print(event.data["chunk"], end="", flush=True)
            elif event.type.value == "generation_end":
                print()
                break
                
    except Exception as e:
        print(f"❌ 演示过程出错: {e}")


async def demo_memory_context_integration():
    """演示记忆上下文如何与检索结果整合"""
    print(f"\n🔗 记忆上下文整合演示")
    print("=" * 25)
    
    # 显示记忆上下文的构建过程
    print(f"\n当前对话历史上下文:")
    context = memory_manager.get_conversation_context(include_count=3)
    if context:
        print("=" * 40)
        print(context)
        print("=" * 40)
    else:
        print("(暂无对话历史)")
    
    print(f"\n💡 记忆上下文整合说明:")
    print("1. 系统会自动获取最近5轮对话作为上下文")
    print("2. 将对话历史与检索到的文档内容合并")
    print("3. 形成完整的上下文提供给LLM")
    print("4. 这样AI就能理解代词引用和上下文关联")


async def main():
    """主演示函数"""
    print("🚀 启动短期记忆功能演示...")
    
    try:
        # 基础记忆功能演示
        await demo_basic_memory()
        
        # 记忆管理功能演示
        await demo_memory_management()
        
        # 记忆限制和清理演示
        await demo_memory_limits()
        
        # 不同模式下的记忆功能演示
        await demo_memory_with_different_modes()
        
        # 记忆上下文整合演示
        await demo_memory_context_integration()
        
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n\n❌ 演示过程中出现错误: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 短期记忆功能演示完成！")
    print("\n💡 关键特性总结:")
    print("  ✅ 自动保存用户问题和AI回答")
    print("  ✅ 智能长度管理，超出限制自动清理旧记录")
    print("  ✅ 上下文整合，AI能理解代词和关联引用")
    print("  ✅ 灵活的记忆管理：搜索、导出、清理")
    print("  ✅ 可配置的清理策略和保留策略")
    print("  ✅ 支持启用/禁用记忆功能")
    
    # 最终记忆统计
    final_stats = memory_manager.get_memory_stats()
    print(f"\n📊 最终记忆统计:")
    print(f"  - 总对话轮数: {final_stats['total_conversations']}")
    print(f"  - 总字符数: {final_stats['total_char_length']:,}")
    print(f"  - 内存使用率: {final_stats['memory_usage_percent']:.1f}%")


if __name__ == "__main__":
    print("🧠 短期记忆功能演示脚本")
    print("展示RAG系统如何维持对话上下文和记忆管理")
    print()
    
    # 运行演示
    asyncio.run(main())