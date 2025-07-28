#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试热重载功能与RAG管道的集成
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from rag.hot_reload_manager import enable_hot_reload, disable_hot_reload
from rag.prompt_manager import prompt_manager, get_qa_prompt_template
from rag.pipeline import RagPipeline

def test_hot_reload_with_qa_prompt():
    """测试qa_prompt.txt的热重载功能"""
    
    print("🔥 测试qa_prompt.txt热重载功能")
    print("=" * 50)
    
    # 1. 启用热重载
    print("1. 启用热重载功能...")
    success = enable_hot_reload()
    if not success:
        print("❌ 热重载启用失败")
        return False
    print("✅ 热重载功能已启用")
    
    # 2. 获取原始提示词模板
    print("\n2. 获取原始提示词模板...")
    try:
        original_template = get_qa_prompt_template()
        original_content = original_template.template
        print(f"   原始模板长度: {len(original_content)} 字符")
        print(f"   原始模板预览: {original_content[:100]}...")
    except Exception as e:
        print(f"❌ 获取原始模板失败: {e}")
        return False
    
    # 3. 备份原始qa_prompt.txt文件
    qa_prompt_file = prompt_manager.prompts_dir / "qa_prompt.txt"
    backup_file = prompt_manager.prompts_dir / "qa_prompt_backup.txt"
    
    print(f"\n3. 备份原始提示词文件...")
    try:
        with open(qa_prompt_file, 'r', encoding='utf-8') as f:
            original_file_content = f.read()
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_file_content)
        print("✅ 原始文件已备份")
    except Exception as e:
        print(f"❌ 备份文件失败: {e}")
        return False
    
    # 4. 修改提示词文件
    modified_content = """🤖 我是一个友好的AI助手，会在回答前加上"根据资料分析："

请基于以下上下文信息回答问题：

上下文信息:
{context}

用户问题: {question}

我的回答:"""
    
    print(f"\n4. 修改提示词文件...")
    try:
        with open(qa_prompt_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print("✅ 提示词文件已修改")
    except Exception as e:
        print(f"❌ 修改文件失败: {e}")
        return False
    
    # 等待热重载事件
    print("   ⏳ 等待热重载事件...")
    time.sleep(3)
    
    # 5. 验证热重载效果
    print("\n5. 验证热重载效果...")
    try:
        # 方法1: 直接从prompt_manager加载
        reloaded_content = prompt_manager.load_prompt("qa_prompt")
        print(f"   直接加载长度: {len(reloaded_content)} 字符")
        print(f"   直接加载预览: {reloaded_content[:50]}...")
        
        # 方法2: 通过get_qa_prompt_template获取
        updated_template = get_qa_prompt_template()
        template_content = updated_template.template
        print(f"   模板获取长度: {len(template_content)} 字符")
        print(f"   模板获取预览: {template_content[:50]}...")
        
        # 检查是否包含修改后的内容
        if "🤖 我是一个友好的AI助手" in reloaded_content:
            print("✅ 直接加载：热重载成功！")
            direct_success = True
        else:
            print("❌ 直接加载：热重载失败！")
            direct_success = False
        
        if "🤖 我是一个友好的AI助手" in template_content:
            print("✅ 模板获取：热重载成功！")
            template_success = True
        else:
            print("❌ 模板获取：热重载失败！")
            template_success = False
            
        hot_reload_success = direct_success and template_success
        
    except Exception as e:
        print(f"❌ 验证热重载效果失败: {e}")
        hot_reload_success = False
    
    # 6. 测试缓存清理
    print("\n6. 测试缓存清理...")
    try:
        # 检查缓存状态
        print(f"   prompt_cache中的qa_prompt: {'存在' if 'qa_prompt' in prompt_manager._prompt_cache else '不存在'}")
        print(f"   template_cache中的qa_prompt: {'存在' if 'qa_prompt' in prompt_manager._template_cache else '不存在'}")
        
        # 手动清理缓存测试
        prompt_manager._prompt_cache.pop('qa_prompt', None)
        prompt_manager._template_cache.pop('qa_prompt', None)
        print("   ✅ 手动清理缓存完成")
        
        # 重新获取模板
        fresh_template = get_qa_prompt_template()
        fresh_content = fresh_template.template
        
        if "🤖 我是一个友好的AI助手" in fresh_content:
            print("✅ 缓存清理后重新加载成功")
            cache_success = True
        else:
            print("❌ 缓存清理后重新加载失败")
            cache_success = False
            
    except Exception as e:
        print(f"❌ 测试缓存清理失败: {e}")
        cache_success = False
    
    # 7. 恢复原始提示词文件
    print(f"\n7. 恢复原始提示词文件...")
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
    
    # 8. 清理备份文件
    print(f"\n8. 清理备份文件...")
    try:
        if backup_file.exists():
            backup_file.unlink()
            print("✅ 备份文件已删除")
    except Exception as e:
        print(f"❌ 清理备份文件失败: {e}")
    
    # 9. 停止热重载
    print(f"\n9. 停止热重载...")
    disable_hot_reload()
    print("✅ 热重载已停止")
    
    # 10. 总结结果
    print(f"\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"   热重载功能: {'✅ 正常' if hot_reload_success else '❌ 异常'}")
    print(f"   缓存管理: {'✅ 正常' if cache_success else '❌ 异常'}")
    
    overall_success = hot_reload_success and cache_success
    print(f"\n🎯 总体结果: {'✅ 所有测试通过' if overall_success else '❌ 部分测试失败'}")
    
    return overall_success

def test_manual_hot_reload():
    """手动测试热重载功能"""
    
    print("\n🎯 手动热重载测试")
    print("=" * 30)
    
    # 启用热重载
    enable_hot_reload()
    
    qa_prompt_file = prompt_manager.prompts_dir / "qa_prompt.txt"
    
    print(f"📝 请手动编辑文件: {qa_prompt_file}")
    print("1. 打开文件编辑器")
    print("2. 修改文件内容")
    print("3. 保存文件")
    print("4. 观察控制台输出")
    print("\n按 Enter 键检查当前内容，输入 'q' 退出...")
    
    try:
        while True:
            user_input = input().strip().lower()
            
            if user_input == 'q':
                break
            
            # 显示当前提示词内容
            try:
                current_template = get_qa_prompt_template()
                current_content = current_template.template
                print(f"\n📄 当前提示词内容 (长度: {len(current_content)} 字符):")
                print("-" * 50)
                print(current_content[:200] + ("..." if len(current_content) > 200 else ""))
                print("-" * 50)
            except Exception as e:
                print(f"❌ 读取提示词失败: {e}")
            
            print("\n继续修改文件或输入 'q' 退出...")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断")
    
    # 停止热重载
    disable_hot_reload()
    print("✅ 热重载已停止")

def main():
    """主函数"""
    
    print("🔥 热重载功能集成测试")
    print("=" * 50)
    
    # 自动测试
    auto_success = test_hot_reload_with_qa_prompt()
    
    if not auto_success:
        print("\n❌ 自动测试失败，启动手动测试...")
        test_manual_hot_reload()
    else:
        print("\n✅ 自动测试通过！")
        
        # 询问是否进行手动测试
        print("\n是否进行手动测试？(y/n): ", end="")
        try:
            choice = input().strip().lower()
            if choice == 'y':
                test_manual_hot_reload()
        except KeyboardInterrupt:
            print("\n跳过手动测试")

if __name__ == "__main__":
    main()