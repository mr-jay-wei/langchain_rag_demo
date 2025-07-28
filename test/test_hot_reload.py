#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试提示词热重载功能
"""

import sys
import time
import asyncio
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from rag.hot_reload_manager import (
    hot_reload_manager, 
    enable_hot_reload, 
    disable_hot_reload, 
    is_hot_reload_enabled,
    get_hot_reload_status,
    WATCHDOG_AVAILABLE
)
from rag.prompt_manager import prompt_manager

def test_hot_reload_setup():
    """测试热重载功能的基础设置"""
    
    print("=== 测试热重载功能设置 ===")
    
    # 1. 检查watchdog库是否可用
    print(f"1. watchdog库可用性: {'✅ 可用' if WATCHDOG_AVAILABLE else '❌ 不可用'}")
    
    if not WATCHDOG_AVAILABLE:
        print("   请安装watchdog库: uv add watchdog")
        return False
    
    # 2. 检查热重载管理器是否初始化
    print(f"2. 热重载管理器: {'✅ 已初始化' if hot_reload_manager else '❌ 未初始化'}")
    
    if not hot_reload_manager:
        return False
    
    # 3. 检查监控目录
    watch_dir = hot_reload_manager.watch_directory
    print(f"3. 监控目录: {watch_dir}")
    print(f"   目录存在: {'✅ 是' if watch_dir.exists() else '❌ 否'}")
    
    # 确保目录存在
    watch_dir.mkdir(exist_ok=True)
    
    # 4. 检查热重载状态
    status = get_hot_reload_status()
    print(f"4. 热重载状态:")
    for key, value in status.items():
        print(f"   - {key}: {value}")
    
    return True

def test_basic_hot_reload():
    """测试基础热重载功能"""
    
    print("\n=== 测试基础热重载功能 ===")
    
    # 1. 启用热重载
    print("1. 启用热重载...")
    success = enable_hot_reload()
    print(f"   启用结果: {'✅ 成功' if success else '❌ 失败'}")
    
    if not success:
        return False
    
    # 2. 检查运行状态
    print(f"2. 运行状态: {'✅ 运行中' if is_hot_reload_enabled() else '❌ 未运行'}")
    
    # 3. 创建测试提示词文件
    test_prompt_file = prompt_manager.prompts_dir / "test_hot_reload.txt"
    original_content = "这是一个测试提示词: {context}\n\n问题: {question}\n\n回答:"
    
    print(f"3. 创建测试提示词文件: {test_prompt_file.name}")
    with open(test_prompt_file, 'w', encoding='utf-8') as f:
        f.write(original_content)
    print("   ✅ 测试文件已创建")
    
    # 等待文件系统事件
    print("   ⏳ 等待文件系统事件处理...")
    time.sleep(3)
    
    # 4. 验证提示词是否被加载
    try:
        loaded_content = prompt_manager.load_prompt("test_hot_reload")
        print(f"4. 提示词加载验证:")
        print(f"   原始长度: {len(original_content)}")
        print(f"   加载长度: {len(loaded_content)}")
        print(f"   内容匹配: {'✅ 是' if original_content == loaded_content else '❌ 否'}")
    except Exception as e:
        print(f"   ❌ 提示词加载失败: {e}")
        return False
    
    # 5. 修改提示词文件测试热重载
    modified_content = "这是修改后的测试提示词: {context}\n\n用户问题: {question}\n\n智能回答:"
    
    print(f"5. 修改提示词文件测试热重载...")
    with open(test_prompt_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    print("   ✅ 文件已修改")
    
    # 等待热重载事件
    print("   ⏳ 等待热重载事件处理...")
    time.sleep(3)
    
    # 6. 验证热重载效果
    try:
        reloaded_content = prompt_manager.load_prompt("test_hot_reload")
        print(f"6. 热重载效果验证:")
        print(f"   修改后长度: {len(modified_content)}")
        print(f"   重载后长度: {len(reloaded_content)}")
        print(f"   内容匹配: {'✅ 是' if modified_content == reloaded_content else '❌ 否'}")
        
        if modified_content == reloaded_content:
            print("   🎉 热重载功能工作正常！")
            hot_reload_success = True
        else:
            print("   ❌ 热重载功能未生效")
            print(f"   期望内容: {modified_content[:50]}...")
            print(f"   实际内容: {reloaded_content[:50]}...")
            hot_reload_success = False
            
    except Exception as e:
        print(f"   ❌ 热重载验证失败: {e}")
        hot_reload_success = False
    
    # 7. 清理测试文件
    print("7. 清理测试文件...")
    if test_prompt_file.exists():
        test_prompt_file.unlink()
        print("   ✅ 测试文件已删除")
        
        # 等待删除事件
        time.sleep(2)
    
    # 8. 停止热重载
    print("8. 停止热重载...")
    disable_hot_reload()
    print(f"   停止后状态: {'✅ 已停止' if not is_hot_reload_enabled() else '❌ 仍在运行'}")
    
    return hot_reload_success

def main():
    """主测试函数"""
    
    print("🔥 开始测试提示词热重载功能")
    print("=" * 50)
    
    # 测试1: 基础设置
    setup_ok = test_hot_reload_setup()
    if not setup_ok:
        print("\n❌ 基础设置测试失败，无法继续")
        return
    
    # 测试2: 基础功能测试
    functionality_ok = test_basic_hot_reload()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"   基础设置: {'✅ 通过' if setup_ok else '❌ 失败'}")
    print(f"   功能测试: {'✅ 通过' if functionality_ok else '❌ 失败'}")
    
    all_passed = setup_ok and functionality_ok
    print(f"\n🎯 总体结果: {'✅ 所有测试通过' if all_passed else '❌ 部分测试失败'}")
    
    if all_passed:
        print("🎉 热重载功能工作正常！")
    else:
        print("🔧 热重载功能存在问题，需要进一步调试")

if __name__ == "__main__":
    main()