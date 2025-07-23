# demo_textloader.py
"""
演示 TextLoader 的实际行为
"""

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def demo_textloader_behavior():
    """演示 TextLoader 的实际加载行为"""
    
    print("=" * 80)
    print("TextLoader 行为演示")
    print("=" * 80)
    
    # 创建一个包含多行内容的测试文件
    test_file = "textloader_test.txt"
    test_content = """第一行：这是文档的标题
第二行：这是第一段内容，包含一些重要信息。

第四行：这是第二段内容。
第五行：继续第二段的内容。

第七行：这是第三段内容。
第八行：包含更多详细信息。
第九行：结束语。"""
    
    # 写入测试文件
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("创建的测试文件内容:")
    print("-" * 40)
    print(test_content)
    print("-" * 40)
    print(f"文件总行数: {len(test_content.split(chr(10)))}")
    print(f"文件总字符数: {len(test_content)}")
    
    # 使用 TextLoader 加载文件
    print(f"\n使用 TextLoader 加载文件...")
    loader = TextLoader(test_file, encoding='utf-8')
    new_docs = loader.load()
    
    # 分析加载结果
    print(f"\nTextLoader 加载结果分析:")
    print(f"返回的文档数量: {len(new_docs)}")
    print(f"返回对象类型: {type(new_docs)}")
    
    if new_docs:
        print(new_docs)
        doc = new_docs[0]
        print(f"\n第一个（也是唯一的）文档:")
        print(f"  文档类型: {type(doc)}")
        print(f"  文档内容长度: {len(doc.page_content)} 字符")
        print(f"  文档元数据: {doc.metadata}")
        
        print(f"\n文档完整内容:")
        print(f"'{repr(doc.page_content)}'")
        
        print(f"\n文档显示内容:")
        print(doc.page_content)
    
    # 清理测试文件
    os.remove(test_file)

def demo_textloader_vs_splitter():
    """对比 TextLoader 和 TextSplitter 的区别"""
    
    print("\n" + "=" * 80)
    print("TextLoader vs TextSplitter 对比")
    print("=" * 80)
    
    # 创建测试文件
    test_file = "comparison_test.txt"
    test_content = """# 第一章：人工智能概述

人工智能是什么？它是计算机科学的重要分支。

## 1.1 定义
人工智能（AI）是指由人制造出来的机器所表现出来的智能。

## 1.2 发展历程
1956年，达特茅斯会议标志着AI的诞生。
1980年代，专家系统兴起。
2010年代，深度学习革命。

# 第二章：机器学习基础

机器学习是AI的核心技术。它包括监督学习、无监督学习和强化学习。"""
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("测试文件内容:")
    print("-" * 40)
    print(test_content)
    print("-" * 40)
    
    # 1. 使用 TextLoader 加载
    print(f"\n1. TextLoader 加载结果:")
    print("-" * 30)
    
    loader = TextLoader(test_file, encoding='utf-8')
    loaded_docs = loader.load()
    
    print(f"文档数量: {len(loaded_docs)}")
    for i, doc in enumerate(loaded_docs):
        print(f"文档 {i+1}:")
        print(f"  长度: {len(doc.page_content)} 字符")
        print(f"  内容预览: {repr(doc.page_content[:100])}...")
    
    # 2. 使用 TextSplitter 分割
    print(f"\n2. TextSplitter 分割结果:")
    print("-" * 30)
    
    text_splitter = RecursiveCharacterTextSplitter(
        separators=[r'\n# ', r'\n## ', r'\n\n', r'\n', r' '],
        is_separator_regex=True,
        keep_separator=True,
        chunk_size=200,
        chunk_overlap=50
    )
    
    # 注意：TextSplitter 作用于已加载的文档
    split_docs = text_splitter.split_documents(loaded_docs)
    
    print(f"分割后文档数量: {len(split_docs)}")
    for i, doc in enumerate(split_docs):
        print(f"块 {i+1}:")
        print(f"  长度: {len(doc.page_content)} 字符")
        print(f"  内容: {repr(doc.page_content)}")
        print()
    
    # 清理
    os.remove(test_file)

def demo_multiple_files():
    """演示加载多个文件的情况"""
    
    print("\n" + "=" * 80)
    print("多文件加载演示")
    print("=" * 80)
    
    # 创建多个测试文件
    files_content = {
        "file1.txt": "这是第一个文件的内容。\n包含两行文本。",
        "file2.txt": "这是第二个文件。\n内容稍有不同。\n有三行文本。",
        "file3.txt": "第三个文件\n只是为了演示\n多文件加载的效果"
    }
    
    # 创建文件
    for filename, content in files_content.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("创建的文件:")
    for filename, content in files_content.items():
        print(f"{filename}: {repr(content)}")
    
    # 逐个加载文件
    all_docs = []
    for filename in files_content.keys():
        loader = TextLoader(filename, encoding='utf-8')
        docs = loader.load()
        all_docs.extend(docs)
        
        print(f"\n{filename} 加载结果:")
        print(f"  文档数量: {len(docs)}")
        print(f"  内容: {repr(docs[0].page_content)}")
        print(f"  元数据: {docs[0].metadata}")
    
    print(f"\n总计加载的文档数量: {len(all_docs)}")
    print("每个文件产生一个 Document 对象，不会按行分割")
    
    # 清理文件
    for filename in files_content.keys():
        os.remove(filename)

def demo_common_misconception():
    """演示常见的误解"""
    
    print("\n" + "=" * 80)
    print("常见误解澄清")
    print("=" * 80)
    
    test_file = "misconception_test.txt"
    content_with_many_lines = """行1：第一行内容
行2：第二行内容
行3：第三行内容
行4：第四行内容
行5：第五行内容
行6：第六行内容
行7：第七行内容
行8：第八行内容
行9：第九行内容
行10：第十行内容"""
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(content_with_many_lines)
    
    print("文件包含10行内容:")
    print(content_with_many_lines)
    
    # 加载文件
    loader = TextLoader(test_file, encoding='utf-8')
    docs = loader.load()
    
    print(f"\n❌ 错误理解: TextLoader 会产生10个文档（每行一个）")
    print(f"✅ 实际结果: TextLoader 产生 {len(docs)} 个文档（整个文件作为一个文档）")
    
    print(f"\n实际加载的文档内容:")
    print(f"'{docs[0].page_content}'")
    
    print(f"\n如果要按行分割，需要使用 TextSplitter:")
    line_splitter = RecursiveCharacterTextSplitter(
        separators=[r'\n'],
        is_separator_regex=True,
        keep_separator=False,
        chunk_size=50,
        chunk_overlap=0
    )
    
    split_docs = line_splitter.split_documents(docs)
    print(f"使用 TextSplitter 按行分割后: {len(split_docs)} 个文档块")
    
    for i, doc in enumerate(split_docs[:3]):  # 只显示前3个
        print(f"  块 {i+1}: '{doc.page_content}'")
    
    # 清理
    os.remove(test_file)

def demo_workflow_in_rag():
    """演示在RAG系统中的实际工作流程"""
    
    print("\n" + "=" * 80)
    print("RAG系统中的实际工作流程")
    print("=" * 80)
    
    print("""
RAG系统中文档处理的完整流程：

1. TextLoader 阶段：
   loader = TextLoader(file_path, encoding='utf-8')
   new_docs = loader.load()
   # 结果：[Document(page_content="整个文件内容", metadata={...})]

2. TextSplitter 阶段：
   chunks = text_splitter.split_documents(new_docs)
   # 结果：[Document(chunk1), Document(chunk2), Document(chunk3), ...]

3. 向量化阶段：
   embeddings = embedding_model.embed_documents([chunk.page_content for chunk in chunks])

4. 存储阶段：
   vector_store.add_documents(chunks)

关键理解：
- TextLoader: 文件 → 单个Document对象
- TextSplitter: 单个Document → 多个Document块
- 分割是为了适应向量模型的输入长度限制
- 分割是为了提高检索的精确性
""")

if __name__ == "__main__":
    demo_textloader_behavior()
    demo_textloader_vs_splitter()
    demo_multiple_files()
    demo_common_misconception()
    demo_workflow_in_rag()