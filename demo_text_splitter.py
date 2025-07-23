# demo_text_splitter.py
"""
演示 RecursiveCharacterTextSplitter 的工作原理
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter

def demo_text_splitting():
    """演示文本分割的详细过程"""
    
    # 原始文档
    original_text = """# 第一章：人工智能概述

人工智能是什么？它是计算机科学的重要分支。

## 1.1 定义
人工智能（Artificial Intelligence，简称AI）是指由人制造出来的机器所表现出来的智能。

## 1.2 发展历程
1956年，达特茅斯会议标志着AI的诞生；1980年代，专家系统兴起；2010年代，深度学习革命。

# 第二章：机器学习基础

机器学习是AI的核心技术。它包括监督学习、无监督学习和强化学习三大类。"""

    print("=" * 80)
    print("原始文档内容:")
    print("=" * 80)
    print(repr(original_text))  # 使用repr显示所有字符，包括换行符
    print()
    
    # 配置分隔符
    separators = [
        r'\n# ',           # 一级标题
        r'\n## ',          # 二级标题  
        r'\n\n',           # 段落分隔
        r'[。！？]',        # 句子结束
        r'[；;]',          # 分句
        r' '               # 空格
    ]
    
    # 创建分割器
    content_splitter = RecursiveCharacterTextSplitter(
        separators=separators,
        is_separator_regex=True,
        keep_separator=True,
        chunk_size=200,  # 较小的块，便于演示
        chunk_overlap=0
    )
    
    # 执行分割
    chunks = content_splitter.split_text(original_text)
    
    print("=" * 80)
    print("分割结果详解:")
    print("=" * 80)
    
    for i, chunk in enumerate(chunks, 1):
        print(f"块 {i}:")
        print(f"长度: {len(chunk)} 字符")
        print(f"内容: {repr(chunk)}")
        print(f"显示: {chunk}")
        print("-" * 40)

def demo_step_by_step():
    """逐步演示分割过程"""
    
    original_text = """# 第一章：人工智能概述

人工智能是什么？它是计算机科学的重要分支。

## 1.1 定义
人工智能（Artificial Intelligence，简称AI）是指由人制造出来的机器所表现出来的智能。

## 1.2 发展历程
1956年，达特茅斯会议标志着AI的诞生；1980年代，专家系统兴起；2010年代，深度学习革命。

# 第二章：机器学习基础

机器学习是AI的核心技术。它包括监督学习、无监督学习和强化学习三大类。"""

    print("=" * 80)
    print("逐步分割过程演示:")
    print("=" * 80)
    
    # 步骤1：找到所有一级标题分割点
    print("步骤1：按一级标题 '\\n# ' 分割")
    import re
    
    # 找到一级标题的位置
    pattern1 = r'\n# '
    matches1 = list(re.finditer(pattern1, original_text))
    print(f"找到 {len(matches1)} 个一级标题分割点:")
    for match in matches1:
        start = max(0, match.start() - 10)
        end = min(len(original_text), match.end() + 20)
        context = original_text[start:end].replace('\n', '\\n')
        print(f"  位置 {match.start()}-{match.end()}: ...{context}...")
    
    # 步骤2：按一级标题分割后的片段
    parts1 = re.split(pattern1, original_text)
    print(f"\n按一级标题分割后得到 {len(parts1)} 个片段:")
    for i, part in enumerate(parts1):
        if part.strip():  # 只显示非空片段
            print(f"  片段 {i}: {repr(part[:50])}...")
    
    # 步骤3：检查每个片段的长度，决定是否需要进一步分割
    print(f"\n步骤2：检查片段长度（限制：200字符）")
    for i, part in enumerate(parts1):
        if part.strip():
            print(f"  片段 {i}: 长度 {len(part)} 字符")
            if len(part) > 200:
                print(f"    → 需要进一步分割")
            else:
                print(f"    → 长度合适，无需分割")

def demo_with_different_chunk_sizes():
    """演示不同chunk_size的效果"""
    
    original_text = """# 第一章：人工智能概述

人工智能是什么？它是计算机科学的重要分支。

## 1.1 定义
人工智能（Artificial Intelligence，简称AI）是指由人制造出来的机器所表现出来的智能。

## 1.2 发展历程
1956年，达特茅斯会议标志着AI的诞生；1980年代，专家系统兴起；2010年代，深度学习革命。

# 第二章：机器学习基础

机器学习是AI的核心技术。它包括监督学习、无监督学习和强化学习三大类。"""

    separators = [r'\n# ', r'\n## ', r'\n\n', r'[。！？]', r'[；;]', r' ']
    
    chunk_sizes = [100, 200, 400]
    
    for chunk_size in chunk_sizes:
        print("=" * 80)
        print(f"chunk_size = {chunk_size} 的分割结果:")
        print("=" * 80)
        
        splitter = RecursiveCharacterTextSplitter(
            separators=separators,
            is_separator_regex=True,
            keep_separator=True,
            chunk_size=chunk_size,
            chunk_overlap=0
        )
        
        chunks = splitter.split_text(original_text)
        
        for i, chunk in enumerate(chunks, 1):
            print(f"块 {i} (长度: {len(chunk)}):")
            print(f"{chunk}")
            print("-" * 40)

def explain_why_this_result():
    """解释为什么会得到这样的分割结果"""
    
    print("=" * 80)
    print("分割结果解释:")
    print("=" * 80)
    
    chunks = [
        "# 第一章：人工智能概述\n\n人工智能是什么？它是计算机科学的重要分支。",
        "## 1.1 定义\n人工智能（Artificial Intelligence，简称AI）是指由人制造出来的机器所表现出来的智能。",
        "## 1.2 发展历程\n1956年，达特茅斯会议标志着AI的诞生；",
        "1980年代，专家系统兴起；",
        "2010年代，深度学习革命。",
        "# 第二章：机器学习基础\n\n机器学习是AI的核心技术。",
        "它包括监督学习、无监督学习和强化学习三大类。"
    ]
    
    explanations = [
        "块1: 一级标题 + 段落，长度刚好在200字符以内，无需进一步分割",
        "块2: 二级标题 + 内容，长度超过200字符，但按句号分割后仍然太长，所以保持完整",
        "块3: 二级标题的一部分，按分号分割",
        "块4: 按分号分割的片段",
        "块5: 按分号分割的片段",
        "块6: 一级标题 + 段落的一部分，按句号分割",
        "块7: 剩余的句子"
    ]
    
    for i, (chunk, explanation) in enumerate(zip(chunks, explanations), 1):
        print(f"块 {i} ({len(chunk)} 字符):")
        print(f"内容: {repr(chunk)}")
        print(f"解释: {explanation}")
        print("-" * 60)

if __name__ == "__main__":
    # 运行所有演示
    demo_text_splitting()
    print("\n" + "="*80 + "\n")
    
    demo_step_by_step()
    print("\n" + "="*80 + "\n")
    
    demo_with_different_chunk_sizes()
    print("\n" + "="*80 + "\n")
    
    explain_why_this_result()