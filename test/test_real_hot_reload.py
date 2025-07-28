#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试实际运行中的热重载功能
模拟真实的使用场景
"""

import sys
import time
import asyncio
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from rag.hot_reload_manager import enable_hot_reload, disable_hot_reload
from rag.prompt_manager import prompt_manager, get_qa_prompt_template
from rag.streaming_pipeline import StreamingRagPipeline

async def test_real_world_hot_reload():
    """测试真实世界中的热重载功能"""
    
    print("🔥 测试实际运行中的热重载功能")
    print("=" * 60)
    
    # 1. 启用热重载
    print("1. 启用热重载功能...")
    success = enable_hot_reload()
    if not success:
        print("❌ 热重载启用失败")
        return False
    print("✅ 热重载功能已启用")
    
    # 2. 初始化StreamingRagPipeline
    print("\n2. 初始化StreamingRagPipeline...")
    try:
        pipeline = StreamingRagPipeline()
        print("✅ StreamingRagPipeline初始化成功")
    except Exception as e:
        print(f"❌ StreamingRagPipeline初始化失败: {e}")
        return False
    
    # 3. 备份原始qa_prompt.txt文件
    qa_prompt_file = prompt_manager.prompts_dir / "qa_prompt.txt"
    backup_file = prompt_manager.prompts_dir / "qa_prompt_backup.txt"
    
    print(f"\n3. 备份原始提示词文件...")
    try:
        with open(qa_prompt_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print("✅ 原始文件已备份")
    except Exception as e:
        print(f"❌ 备份文件失败: {e}")
        return False
    
    # 4. 设置测试提示词（包含明显的标识符）
    test_prompt_v1 = """请你扮演一个严谨的文档问答机器人。
请严格根据下面提供的"上下文信息"来回答"问题"。
在答案前加上"根据资料V1版本："
如果上下文中没有足够的信息来回答问题，请直接说："根据提供的资料，我无法回答该问题。"
不允许编造或添加上下文之外的任何信息。

---
上下文信息:
{context}
---

问题: {question}

回答:"""
    
    print(f"\n4. 设置测试提示词V1（包含'根据资料V1版本：'）...")
    try:
        with open(qa_prompt_file, 'w', encoding='utf-8') as f:
            f.write(test_prompt_v1)
        print("✅ 测试提示词V1已设置")
    except Exception as e:
        print(f"❌ 设置测试提示词失败: {e}")
        return False
    
    # 等待热重载
    print("   ⏳ 等待热重载...")
    time.sleep(3)
    
    # 5. 验证V1提示词是否生效
    print(f"\n5. 验证V1提示词是否生效...")
    try:
        template_v1 = get_qa_prompt_template()
        if "根据资料V1版本：" in template_v1.template:
            print("✅ V1提示词已加载到模板中")
        else:
            print("❌ V1提示词未加载到模板中")
            print(f"   实际模板内容: {template_v1.template[:200]}...")
    except Exception as e:
        print(f"❌ 验证V1提示词失败: {e}")
    
    # 6. 进行第一次问答测试
    print(f"\n6. 进行第一次问答测试（应该包含'根据资料V1版本：'）...")
    test_question = "什么是Python？"
    
    try:
        print(f"   问题: {test_question}")
        print("   开始流式生成...")
        
        answer_chunks = []
        async for event in pipeline.ask_stream(test_question, use_memory=False):
            if event.type.value == "generation_chunk":
                chunk = event.data.get("chunk", "")
                answer_chunks.append(chunk)
                print(f"   收到chunk: {chunk}", end="", flush=True)
            elif event.type.value == "error":
                print(f"\n   ❌ 生成错误: {event.data.get('error')}")
                break
            elif event.type.value == "complete":
                break
        
        full_answer_v1 = "".join(answer_chunks)
        print(f"\n   完整回答: {full_answer_v1}")
        
        if "根据资料V1版本：" in full_answer_v1:
            print("✅ V1回答包含预期标识符")
            v1_test_success = True
        else:
            print("❌ V1回答不包含预期标识符")
            v1_test_success = False
            
    except Exception as e:
        print(f"❌ 第一次问答测试失败: {e}")
        v1_test_success = False
    
    # 7. 修改提示词为V2版本
    test_prompt_v2 = """请你扮演一个严谨的文档问答机器人。
请严格根据下面提供的"上下文信息"来回答"问题"。
在答案前加上"根据资料V2版本："
如果上下文中没有足够的信息来回答问题，请直接说："根据提供的资料，我无法回答该问题。"
不允许编造或添加上下文之外的任何信息。

---
上下文信息:
{context}
---

问题: {question}

回答:"""
    
    print(f"\n7. 修改提示词为V2版本（包含'根据资料V2版本：'）...")
    try:
        with open(qa_prompt_file, 'w', encoding='utf-8') as f:
            f.write(test_prompt_v2)
        print("✅ 测试提示词V2已设置")
    except Exception as e:
        print(f"❌ 设置V2提示词失败: {e}")
        return False
    
    # 等待热重载
    print("   ⏳ 等待热重载...")
    time.sleep(3)
    
    # 8. 验证V2提示词是否生效
    print(f"\n8. 验证V2提示词是否生效...")
    try:
        template_v2 = get_qa_prompt_template()
        if "根据资料V2版本：" in template_v2.template:
            print("✅ V2提示词已加载到模板中")
            template_updated = True
        else:
            print("❌ V2提示词未加载到模板中")
            print(f"   实际模板内容: {template_v2.template[:200]}...")
            template_updated = False
    except Exception as e:
        print(f"❌ 验证V2提示词失败: {e}")
        template_updated = False
    
    # 9. 进行第二次问答测试
    print(f"\n9. 进行第二次问答测试（应该包含'根据资料V2版本：'）...")
    
    try:
        print(f"   问题: {test_question}")
        print("   开始流式生成...")
        
        answer_chunks = []
        async for event in pipeline.ask_stream(test_question, use_memory=False):
            if event.type.value == "generation_chunk":
                chunk = event.data.get("chunk", "")
                answer_chunks.append(chunk)
                print(f"   收到chunk: {chunk}", end="", flush=True)
            elif event.type.value == "error":
                print(f"\n   ❌ 生成错误: {event.data.get('error')}")
                break
            elif event.type.value == "complete":
                break
        
        full_answer_v2 = "".join(answer_chunks)
        print(f"\n   完整回答: {full_answer_v2}")
        
        if "根据资料V2版本：" in full_answer_v2:
            print("✅ V2回答包含预期标识符 - 热重载成功！")
            v2_test_success = True
        elif "根据资料V1版本：" in full_answer_v2:
            print("❌ V2回答仍包含V1标识符 - 热重载失败！")
            v2_test_success = False
        else:
            print("❌ V2回答不包含任何版本标识符")
            v2_test_success = False
            
    except Exception as e:
        print(f"❌ 第二次问答测试失败: {e}")
        v2_test_success = False
    
    # 10. 对比两次回答
    print(f"\n10. 对比两次回答...")
    if v1_test_success and v2_test_success:
        print("✅ 两次回答都包含了对应版本的标识符")
        print("✅ 热重载功能在实际运行中正常工作！")
        hot_reload_working = True
    elif v1_test_success and not v2_test_success:
        print("❌ 第一次正常，第二次失败 - 热重载功能有问题")
        hot_reload_working = False
    elif not v1_test_success and v2_test_success:
        print("❌ 第一次失败，第二次正常 - 可能是初始化问题")
        hot_reload_working = False
    else:
        print("❌ 两次都失败 - 可能是其他问题")
        hot_reload_working = False
    
    # 11. 恢复原始提示词文件
    print(f"\n11. 恢复原始提示词文件...")
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(qa_prompt_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print("✅ 原始文件已恢复")
        
        # 等待恢复事件
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ 恢复文件失败: {e}")
    
    # 12. 清理备份文件
    print(f"\n12. 清理备份文件...")
    try:
        if backup_file.exists():
            backup_file.unlink()
            print("✅ 备份文件已删除")
    except Exception as e:
        print(f"❌ 清理备份文件失败: {e}")
    
    # 13. 停止热重载
    print(f"\n13. 停止热重载...")
    disable_hot_reload()
    print("✅ 热重载已停止")
    
    # 14. 总结结果
    print(f"\n" + "=" * 60)
    print("📊 实际运行测试结果:")
    print(f"   V1测试: {'✅ 成功' if v1_test_success else '❌ 失败'}")
    print(f"   模板更新: {'✅ 成功' if template_updated else '❌ 失败'}")
    print(f"   V2测试: {'✅ 成功' if v2_test_success else '❌ 失败'}")
    print(f"   热重载功能: {'✅ 正常工作' if hot_reload_working else '❌ 存在问题'}")
    
    if not hot_reload_working:
        print(f"\n🔧 可能的问题:")
        print(f"   1. StreamingRagPipeline可能有自己的缓存")
        print(f"   2. 热重载的时机可能有问题")
        print(f"   3. 提示词模板可能在其他地方被缓存")
        print(f"   4. LLM调用可能有延迟或缓存")
    
    return hot_reload_working

def main():
    """主函数"""
    asyncio.run(test_real_world_hot_reload())

if __name__ == "__main__":
    main()