#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试不同回答来源的功能
1. 有相关文档 -> "根据知识库资料："
2. 无相关文档 -> "知识库资料未检索到内容，使用大模型训练知识回复："
3. 大模型也不知道 -> "根据提供的资料，我无法回答该问题。"
"""

import sys
import asyncio
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from rag.streaming_pipeline import StreamingRagPipeline

async def test_answer_sources():
    """测试不同回答来源的功能"""
    
    print("🧪 测试不同回答来源的功能")
    print("=" * 60)
    
    # 初始化管道
    print("1. 初始化StreamingRagPipeline...")
    try:
        pipeline = StreamingRagPipeline()
        print("✅ 初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 测试用例
    test_cases = [
        {
            "name": "知识库相关问题",
            "question": "什么是Python？",
            "expected_prefix": "根据知识库资料：",
            "description": "应该从知识库找到相关文档"
        },
        {
            "name": "知识库无关但常识问题", 
            "question": "埃及有多少座金字塔？",
            "expected_prefix": "知识库资料未检索到内容，使用大模型训练知识回复：",
            "description": "知识库没有相关内容，但大模型知道"
        },
        {
            "name": "完全无关的问题",
            "question": "请帮我预测明天的彩票号码",
            "expected_prefix": "根据提供的资料，我无法回答该问题。",
            "description": "大模型也无法回答的问题"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试: {test_case['name']}")
        print(f"   问题: {test_case['question']}")
        print(f"   期望前缀: {test_case['expected_prefix']}")
        print(f"   说明: {test_case['description']}")
        print("   " + "-" * 50)
        
        try:
            # 收集流式回答
            answer_chunks = []
            processing_messages = []
            
            async for event in pipeline.ask_stream(test_case['question'], use_memory=False):
                if event.type.value == "processing":
                    processing_messages.append(event.data.get("message", ""))
                elif event.type.value == "generation_start":
                    print(f"   🚀 {event.data.get('message', '开始生成')}")
                elif event.type.value == "generation_chunk":
                    chunk = event.data.get("chunk", "")
                    answer_chunks.append(chunk)
                    print(chunk, end="", flush=True)
                elif event.type.value == "generation_end":
                    print(f"\n   ✅ {event.data.get('message', '生成完成')}")
                elif event.type.value == "error":
                    print(f"\n   ❌ 错误: {event.data.get('error')}")
                    break
                elif event.type.value == "complete":
                    break
            
            # 分析回答
            full_answer = "".join(answer_chunks)
            print(f"\n   📄 完整回答: {full_answer}")
            
            # 检查前缀
            if test_case['expected_prefix'] in full_answer:
                print(f"   ✅ 前缀正确: 包含 '{test_case['expected_prefix']}'")
                test_success = True
            else:
                print(f"   ❌ 前缀错误: 未包含 '{test_case['expected_prefix']}'")
                test_success = False
            
            # 显示处理过程
            if processing_messages:
                print(f"   📋 处理过程: {' -> '.join(processing_messages)}")
            
            print(f"   🎯 测试结果: {'✅ 通过' if test_success else '❌ 失败'}")
            
        except Exception as e:
            print(f"   ❌ 测试执行失败: {e}")
        
        print()  # 空行分隔
    
    print("🎉 所有测试完成！")

def main():
    """主函数"""
    asyncio.run(test_answer_sources())

if __name__ == "__main__":
    main()