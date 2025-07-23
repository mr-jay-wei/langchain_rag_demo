# demo_vectorization.py
"""
演示向量化和存储的详细过程
"""

import os
import numpy as np
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

def demo_vectorization_process():
    """演示向量化的详细过程"""
    
    print("=" * 80)
    print("向量化过程详细演示")
    print("=" * 80)
    
    # 1. 准备测试数据
    test_chunks = [
        Document(
            page_content="人工智能是计算机科学的重要分支。",
            metadata={"source": "ai_doc.txt", "chunk_id": "doc_001_0"}
        ),
        Document(
            page_content="机器学习是AI的核心技术之一。",
            metadata={"source": "ai_doc.txt", "chunk_id": "doc_001_1"}
        ),
        Document(
            page_content="深度学习使用神经网络处理复杂任务。",
            metadata={"source": "ai_doc.txt", "chunk_id": "doc_001_2"}
        )
    ]
    
    print("准备的文档块:")
    for i, chunk in enumerate(test_chunks):
        print(f"  块 {i}: '{chunk.page_content}'")
        print(f"       元数据: {chunk.metadata}")
    
    # 2. 初始化嵌入模型
    print(f"\n步骤1: 初始化嵌入模型")
    embeddings = HuggingFaceEmbeddings(
        model_name="../local_models/bge-small-zh-v1.5",
        model_kwargs={"device": "cpu"}
    )
    print(f"  嵌入模型: {embeddings}")
    
    # 3. 手动演示向量化过程
    print(f"\n步骤2: 手动演示向量化过程")
    print("这就是 add_documents() 内部做的事情:")
    
    # 提取所有文档内容
    texts = [chunk.page_content for chunk in test_chunks]
    print(f"  提取的文本列表: {texts}")
    
    # 调用嵌入模型生成向量
    print(f"  正在调用嵌入模型生成向量...")
    vectors = embeddings.embed_documents(texts)
    
    print(f"  生成的向量信息:")
    print(f"    向量数量: {len(vectors)}")
    print(f"    每个向量维度: {len(vectors[0])}")
    print(f"    向量类型: {type(vectors[0])}")
    
    # 显示部分向量内容
    for i, vector in enumerate(vectors):
        print(f"    向量 {i} 前5维: {vector[:5]}")
        print(f"    向量 {i} 后5维: {vector[-5:]}")
    
    # 4. 演示 add_documents 的等价操作
    print(f"\n步骤3: add_documents() 等价操作演示")
    
    # 创建向量存储
    vector_store = Chroma(
        embedding_function=embeddings,
        persist_directory="demo_vector_store"
    )
    
    print("add_documents(chunks) 内部实际执行:")
    print("  1. 提取文档内容 → texts = [chunk.page_content for chunk in chunks]")
    print("  2. 生成向量 → vectors = embeddings.embed_documents(texts)")
    print("  3. 存储文档+向量+元数据 → database.store(texts, vectors, metadatas)")
    
    # 实际调用 add_documents
    print(f"\n执行 vector_store.add_documents(chunks)...")
    vector_store.add_documents(test_chunks)
    print("  ✅ 文档、向量、元数据已全部存储到数据库")
    
    # 5. 验证存储结果
    print(f"\n步骤4: 验证存储结果")
    
    # 查询验证
    query = "什么是人工智能？"
    print(f"  测试查询: '{query}'")
    
    results = vector_store.similarity_search(query, k=2)
    print(f"  检索结果数量: {len(results)}")
    
    for i, result in enumerate(results):
        print(f"    结果 {i+1}:")
        print(f"      内容: '{result.page_content}'")
        print(f"      元数据: {result.metadata}")
    
    # 清理
    import shutil
    if os.path.exists("demo_vector_store"):
        shutil.rmtree("demo_vector_store")

def demo_step_by_step_comparison():
    """对比手动向量化和自动向量化"""
    
    print("\n" + "=" * 80)
    print("手动 vs 自动向量化对比")
    print("=" * 80)
    
    # 准备测试文档
    test_doc = Document(
        page_content="自然语言处理是人工智能的重要应用领域。",
        metadata={"source": "nlp_doc.txt", "chunk_id": "doc_002_0"}
    )
    
    # 初始化嵌入模型
    embeddings = HuggingFaceEmbeddings(
        model_name="../local_models/bge-small-zh-v1.5",
        model_kwargs={"device": "cpu"}
    )
    
    print("测试文档:")
    print(f"  内容: '{test_doc.page_content}'")
    print(f"  元数据: {test_doc.metadata}")
    
    # 方法1: 手动向量化（展示内部过程）
    print(f"\n方法1: 手动向量化过程")
    print("  步骤1: 提取文档内容")
    text = test_doc.page_content
    print(f"    文本: '{text}'")
    
    print("  步骤2: 调用嵌入模型")
    vector = embeddings.embed_query(text)  # 单个文档用 embed_query
    print(f"    向量维度: {len(vector)}")
    print(f"    向量前3维: {vector[:3]}")
    
    print("  步骤3: 手动存储到向量数据库")
    vector_store_manual = Chroma(embedding_function=embeddings)
    # 手动添加（模拟内部过程）
    vector_store_manual.add_texts(
        texts=[text],
        metadatas=[test_doc.metadata]
    )
    print("    ✅ 手动存储完成")
    
    # 方法2: 自动向量化（一行代码）
    print(f"\n方法2: 自动向量化过程")
    vector_store_auto = Chroma(embedding_function=embeddings)
    print("  执行: vector_store.add_documents([test_doc])")
    vector_store_auto.add_documents([test_doc])
    print("    ✅ 自动存储完成（内部自动完成了向量化）")
    
    # 验证两种方法的结果一致性
    print(f"\n结果验证:")
    query = "什么是自然语言处理？"
    
    result_manual = vector_store_manual.similarity_search(query, k=1)[0]
    result_auto = vector_store_auto.similarity_search(query, k=1)[0]
    
    print(f"  查询: '{query}'")
    print(f"  手动方法结果: '{result_manual.page_content}'")
    print(f"  自动方法结果: '{result_auto.page_content}'")
    print(f"  结果一致: {result_manual.page_content == result_auto.page_content}")

def demo_real_world_workflow():
    """演示真实世界的完整工作流程"""
    
    print("\n" + "=" * 80)
    print("真实RAG系统工作流程")
    print("=" * 80)
    
    # 创建测试文件
    test_file = "vectorization_demo.txt"
    test_content = """机器学习基础知识

监督学习是机器学习的一种重要方法。
无监督学习用于发现数据中的隐藏模式。
强化学习通过试错来学习最优策略。

深度学习应用

卷积神经网络适用于图像处理任务。
循环神经网络擅长处理序列数据。
Transformer架构在自然语言处理中表现优异。"""
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("模拟完整的RAG处理流程:")
    
    # 步骤1: 加载文档
    print("\n1. 文档加载")
    loader = TextLoader(test_file, encoding='utf-8')
    docs = loader.load()
    print(f"   加载文档数量: {len(docs)}")
    
    # 步骤2: 文档分割
    print("\n2. 文档分割")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20
    )
    chunks = text_splitter.split_documents(docs)
    print(f"   分割后块数量: {len(chunks)}")
    
    # 步骤3: 添加元数据
    print("\n3. 添加元数据")
    for i, chunk in enumerate(chunks):
        chunk.metadata['chunk_id'] = f"doc_demo_{i}"
    print(f"   已为 {len(chunks)} 个块添加唯一ID")
    
    # 步骤4: 向量化和存储（关键步骤）
    print("\n4. 向量化和存储")
    embeddings = HuggingFaceEmbeddings(
        model_name="../local_models/bge-small-zh-v1.5",
        model_kwargs={"device": "cpu"}
    )
    
    vector_store = Chroma(
        embedding_function=embeddings,
        persist_directory="real_world_demo"
    )
    
    print("   执行: vector_store.add_documents(chunks)")
    print("   内部过程:")
    print("     a) 提取文档内容: [chunk.page_content for chunk in chunks]")
    print("     b) 调用嵌入模型: embeddings.embed_documents(texts)")
    print("     c) 存储: 文档内容 + 向量 + 元数据")
    
    vector_store.add_documents(chunks)
    print("   ✅ 向量化和存储完成")
    
    # 步骤5: 验证检索功能
    print("\n5. 验证检索功能")
    test_queries = [
        "什么是监督学习？",
        "深度学习有哪些应用？",
        "Transformer的特点是什么？"
    ]
    
    for query in test_queries:
        results = vector_store.similarity_search(query, k=1)
        if results:
            print(f"   查询: '{query}'")
            print(f"   结果: '{results[0].page_content[:50]}...'")
            print(f"   来源: {results[0].metadata.get('chunk_id')}")
    
    # 清理
    os.remove(test_file)
    import shutil
    if os.path.exists("real_world_demo"):
        shutil.rmtree("real_world_demo")

def demo_what_gets_stored():
    """演示数据库中实际存储的内容"""
    
    print("\n" + "=" * 80)
    print("数据库存储内容详解")
    print("=" * 80)
    
    print("""
当执行 vector_store.add_documents(chunks) 时，数据库中实际存储了：

1. 文档内容 (Document Content):
   - 原始文本: "人工智能是计算机科学的重要分支。"
   - 存储位置: documents 表的 content 字段

2. 向量数据 (Vector Embeddings):
   - 向量维度: [0.1234, -0.5678, 0.9012, ...] (通常512或768维)
   - 存储位置: vectors 表的 embedding 字段
   - 用途: 相似性搜索和语义匹配

3. 元数据 (Metadata):
   - 文件来源: {"source": "ai_doc.txt"}
   - 块ID: {"chunk_id": "doc_001_0"}
   - 其他信息: {"category": "technical", "timestamp": "..."}
   - 存储位置: metadata 表或 JSON 字段

4. 索引信息 (Index):
   - 向量索引: 用于快速相似性搜索
   - 文档ID: 用于关联文档内容和向量

数据库表结构示例:
┌─────────────┬──────────────────────┬─────────────────────┬──────────────────┐
│ document_id │ content              │ embedding_vector    │ metadata         │
├─────────────┼──────────────────────┼─────────────────────┼──────────────────┤
│ doc_001_0   │ 人工智能是计算机...   │ [0.12, -0.56, ...] │ {"source": ...}  │
│ doc_001_1   │ 机器学习是AI的...     │ [0.34, -0.78, ...] │ {"source": ...}  │
│ doc_001_2   │ 深度学习使用神经...   │ [0.56, -0.90, ...] │ {"source": ...}  │
└─────────────┴──────────────────────┴─────────────────────┴──────────────────┘

检索过程:
1. 用户查询: "什么是人工智能？"
2. 查询向量化: [0.11, -0.55, 0.88, ...]
3. 向量相似性搜索: 计算余弦相似度
4. 返回最相似的文档内容和元数据
""")

if __name__ == "__main__":
    demo_vectorization_process()
    demo_step_by_step_comparison()
    demo_real_world_workflow()
    demo_what_gets_stored()