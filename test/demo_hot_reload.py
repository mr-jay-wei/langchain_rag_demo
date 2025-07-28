#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
热重载功能演示
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from rag.hot_reload_manager import enable_hot_reload, disable_hot_reload
from rag.prompt_manager import prompt_manager, get_qa_prompt_template

def main():
    """主演示函数"""
    
    print("🔥 提示词热重载功能演示")
    print("=" * 50)
    
    # 1. 启用热重载
    print("1. 启用热重载功能...")
    success = enable_hot_reload()
    
    if not success:
        print("❌ 热重载启用失败")
        return
    
    print("✅ 热重载功能已启用")
    
    # 2. 显示当前提示词内容
    def show_current_prompt():
        try:
            template = get_qa_prompt_template()
            content = template.template
            print(f"\n📄 当前qa_prompt.txt内容 (长度: {len(content)} 字符):")
            print("-" * 60)
            print(content)
            print("-" * 60)
        except Exception as e:
            print(f"❌ 读取提示词失败: {e}")
    
    # 3. 显示初始内容
    print("\n2. 当前提示词内容:")
    show_current_prompt()
    
    # 4. 交互式演示
    qa_prompt_file = prompt_manager.prompts_dir / "qa_prompt.txt"
    
    print(f"\n3. 🎯 交互式热重载演示")
    print(f"📝 提示词文件位置: {qa_prompt_file}")
    print("\n现在你可以：")
    print("1. 打开文件编辑器")
    print("2. 编辑上述文件")
    print("3. 保存文件")
    print("4. 观察控制台的热重载消息")
    print("5. 按 Enter 键查看更新后的内容")
    
    print("\n按 Enter 键查看当前内容，输入 'q' 退出...")
    
    try:
        while True:
            user_input = input().strip().lower()
            
            if user_input == 'q':
                break
            
            # 显示当前提示词内容
            show_current_prompt()
            
            print("\n继续修改文件，按 Enter 查看更新，或输入 'q' 退出...")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断")
    
    # 5. 停止热重载
    print("\n4. 停止热重载...")
    disable_hot_reload()
    print("✅ 热重载已停止")
    
    print("\n🎉 演示完成！")
    print("\n💡 热重载功能说明:")
    print("   - 监控目录: rag/prompts/")
    print("   - 支持的文件: *.txt")
    print("   - 自动检测: 创建、修改、删除")
    print("   - 实时重载: 无需重启应用")
    print("   - 缓存管理: 自动清理和重建")
    
    print("\n🚀 在实际应用中:")
    print("   - Web应用会立即使用更新后的提示词")
    print("   - RAG管道会自动应用新的提示词模板")
    print("   - 可以实时调优AI的回答风格和质量")

if __name__ == "__main__":
    main()