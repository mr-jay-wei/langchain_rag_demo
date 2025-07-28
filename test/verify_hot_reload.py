#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证热重载功能的简单脚本
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from rag.hot_reload_manager import enable_hot_reload, disable_hot_reload
from rag.prompt_manager import prompt_manager, get_qa_prompt_template

def main():
    """主验证函数"""
    
    print("🔥 热重载功能验证")
    print("=" * 40)
    
    # 启用热重载
    print("1. 启用热重载...")
    enable_hot_reload()
    
    qa_prompt_file = prompt_manager.prompts_dir / "qa_prompt.txt"
    
    print(f"\n2. 当前提示词文件: {qa_prompt_file}")
    
    def show_current_template():
        template = get_qa_prompt_template()
        content = template.template
        print(f"   当前模板长度: {len(content)} 字符")
        if "根据资料V1版本：" in content:
            print("   ✅ 包含V1标识符")
        elif "根据资料V2版本：" in content:
            print("   ✅ 包含V2标识符")
        elif "根据你的资料：" in content:
            print("   ✅ 包含'根据你的资料：'")
        else:
            print(f"   📄 内容预览: {content[:100]}...")
    
    print("\n3. 当前模板状态:")
    show_current_template()
    
    print(f"\n4. 🎯 请按以下步骤操作:")
    print(f"   1. 打开文件: {qa_prompt_file}")
    print(f"   2. 在提示词中添加或修改标识符")
    print(f"   3. 保存文件")
    print(f"   4. 观察控制台的热重载消息")
    print(f"   5. 按Enter键查看更新后的模板")
    
    print(f"\n按Enter键查看当前模板，输入'q'退出...")
    
    try:
        while True:
            user_input = input().strip().lower()
            if user_input == 'q':
                break
            
            print("\n📄 当前模板状态:")
            show_current_template()
            print("\n继续修改文件，按Enter查看更新，或输入'q'退出...")
    
    except KeyboardInterrupt:
        print("\n用户中断")
    
    # 停止热重载
    print("\n5. 停止热重载...")
    disable_hot_reload()
    print("✅ 验证完成")

if __name__ == "__main__":
    main()