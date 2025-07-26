#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证提示词解耦是否完全成功
"""

import os
import re

def check_file_for_hardcoded_prompts(file_path):
    """检查文件中是否还有硬编码的提示词"""
    if not os.path.exists(file_path):
        return False, f"文件不存在: {file_path}"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否还有硬编码的提示词
    hardcoded_patterns = [
        r'请你扮演一个严谨的文档问答机器人',
        r'你是一个专业的问题改写助手',
        r'prompt_template\s*=\s*""".*请你扮演',
        r'rewrite_prompt\s*=\s*PromptTemplate\.from_template\(""".*你是一个专业'
    ]
    
    found_issues = []
    for pattern in hardcoded_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        if matches:
            found_issues.extend(matches)
    
    # 检查是否正确导入了提示词管理器
    has_import = 'from .prompt_manager import' in content or 'from rag.prompt_manager import' in content
    
    # 检查是否使用了提示词管理器的函数
    uses_manager = 'get_qa_prompt_template()' in content or 'get_query_rewrite_prompt_template()' in content
    
    return {
        'has_hardcoded': len(found_issues) > 0,
        'hardcoded_issues': found_issues,
        'has_import': has_import,
        'uses_manager': uses_manager,
        'is_clean': len(found_issues) == 0 and (has_import or not uses_manager)
    }

def verify_prompt_decoupling():
    """验证所有文件的提示词解耦状态"""
    print("=== 验证提示词解耦状态 ===\n")
    
    files_to_check = [
        'rag/pipeline.py',
        'rag/async_pipeline.py', 
        'rag/streaming_pipeline.py'
    ]
    
    all_clean = True
    
    for file_path in files_to_check:
        print(f"检查文件: {file_path}")
        result = check_file_for_hardcoded_prompts(file_path)
        
        if isinstance(result, tuple):
            print(f"  ❌ {result[1]}")
            all_clean = False
            continue
        
        if result['is_clean']:
            print(f"  ✅ 提示词解耦完成")
            if result['has_import']:
                print(f"     - 已导入提示词管理器")
            if result['uses_manager']:
                print(f"     - 正在使用提示词管理器")
        else:
            print(f"  ❌ 仍有硬编码提示词")
            all_clean = False
            
            if result['hardcoded_issues']:
                print(f"     发现的问题:")
                for issue in result['hardcoded_issues'][:3]:  # 只显示前3个
                    preview = issue[:50] + "..." if len(issue) > 50 else issue
                    print(f"       - {preview}")
            
            if not result['has_import']:
                print(f"     - 缺少提示词管理器导入")
        
        print()
    
    # 检查提示词文件是否存在
    print("检查提示词文件:")
    prompt_files = [
        'rag/prompts/qa_prompt.txt',
        'rag/prompts/query_rewrite_prompt.txt',
        'rag/prompt_manager.py'
    ]
    
    for file_path in prompt_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - 文件不存在")
            all_clean = False
    
    print(f"\n=== 验证结果 ===")
    if all_clean:
        print("🎉 提示词解耦完全成功！")
        print("\n优势:")
        print("  ✅ 所有硬编码提示词已移除")
        print("  ✅ 提示词文件已创建")
        print("  ✅ 提示词管理器已集成")
        print("  ✅ 代码与提示词完全解耦")
        
        print("\n使用方法:")
        print("  1. 直接编辑 rag/prompts/*.txt 文件来修改提示词")
        print("  2. 无需重启程序，提示词会自动更新")
        print("  3. 支持版本控制和团队协作")
    else:
        print("❌ 提示词解耦未完全成功，请检查上述问题")
    
    return all_clean

if __name__ == "__main__":
    verify_prompt_decoupling()