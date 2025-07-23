# demo_chunk_metadata.py
"""
演示 chunk 对象和 metadata 的详细结构
"""

import hashlib
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os

# 模拟配置
class Config:
    DOCUMENT_ID_PREFIX = "doc_"

config = Config()

def demo_chunk_structure():
    """演示 chunk 对象的详细结构"""
    
    print("=" * 80)
    print("Chunk 对象结构演示")
    print("=" * 80)
    
    # 创建测试文件
    test_file = "chunk_demo.txt"
    test_content = """第一段：这是文档的第一段内容，包含一些重要信息。

第二段：这是文档的第二段内容，继续描述相关主题。

第三段：这是文档的第三段内容，提供更多详细信息。

第四段：这是文档的最后一段，总结全文内容。"""
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("原始文档内容:")
    print("-" * 40)
    print(test_content)
    print("-" * 40)
    
    # 1. 使用 TextLoader 加载文档
    print("\n1. TextLoader 加载结果:")
    loader = TextLoader(test_file, encoding='utf-8')
    docs = loader.load()
    
    print(f"加载的文档数量: {len(docs)}")
    original_doc = docs[0]
    print(f"原始文档类型: {type(original_doc)}")
    print(f"原始文档内容长度: {len(original_doc.page_content)} 字符")
    print(f"原始文档元数据: {original_doc.metadata}")
    
    # 2. 使用 TextSplitter 分割文档
    print(f"\n2. TextSplitter 分割过程:")
    text_splitter = RecursiveCharacterTextSplitter(
        separators=[r'\n\n', r'\n', r' '],
        is_separator_regex=True,
        keep_separator=True,
        chunk_size=100,
        chunk_overlap=20
    )
    
    chunks = text_splitter.split_documents(docs)
    print(f"分割后的块数量: {len(chunks)}")
    
    # 3. 详细分析每个 chunk
    print(f"\n3. 每个 chunk 的详细结构:")
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i} ---")
        print(f"类型: {type(chunk)}")
        print(f"内容长度: {len(chunk.page_content)} 字符")
        print(f"内容: '{chunk.page_content}'")
        print(f"元数据: {chunk.metadata}")
        print(f"元数据类型: {type(chunk.metadata)}")
    
    # 清理
    os.remove(test_file)

def demo_metadata_assignment():
    """演示 metadata 赋值过程"""
    
    print("\n" + "=" * 80)
    print("Metadata 赋值过程演示")
    print("=" * 80)
    
    # 创建测试文件
    test_file = "metadata_demo.txt"
    test_content = """人工智能概述：人工智能是计算机科学的重要分支。

机器学习基础：机器学习是AI的核心技术之一。

深度学习应用：深度学习在各个领域都有广泛应用。"""
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # 加载和分割
    loader = TextLoader(test_file, encoding='utf-8')
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=80,
        chunk_overlap=10
    )
    chunks = text_splitter.split_documents(docs)
    
    print(f"分割前的原始文档元数据:")
    print(f"  {docs[0].metadata}")
    
    print(f"\n分割后各块的初始元数据:")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i}: {chunk.metadata}")
    
    # 模拟原代码中的 metadata 赋值过程
    print(f"\n执行 metadata 赋值过程:")
    print("for i, chunk in enumerate(chunks):")
    
    file_path = test_file
    for i, chunk in enumerate(chunks):
        # 生成 chunk_id
        chunk_id = f"{config.DOCUMENT_ID_PREFIX}{hashlib.md5(file_path.encode()).hexdigest()}_{i}"
        
        print(f"\n  处理 Chunk {i}:")
        print(f"    生成的 chunk_id: {chunk_id}")
        print(f"    赋值前的 metadata: {chunk.metadata}")
        
        # 关键操作：将 chunk_id 添加到 metadata 中
        chunk.metadata['chunk_id'] = chunk_id
        
        print(f"    赋值后的 metadata: {chunk.metadata}")
    
    # 验证最终结果
    print(f"\n最终各块的完整 metadata:")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i}:")
        print(f"    内容: '{chunk.page_content[:30]}...'")
        print(f"    metadata: {chunk.metadata}")
    
    # 清理
    os.remove(test_file)

def demo_document_object_details():
    """详细演示 Document 对象的结构"""
    
    print("\n" + "=" * 80)
    print("Document 对象详细结构")
    print("=" * 80)
    
    # 手动创建一个 Document 对象来演示
    sample_doc = Document(
        page_content="这是一个示例文档块的内容。",
        metadata={
            "source": "./data/example.txt",
            "created_at": "2024-01-01"
        }
    )
    
    print("Document 对象的组成部分:")
    print(f"1. page_content (文档内容):")
    print(f"   类型: {type(sample_doc.page_content)}")
    print(f"   值: '{sample_doc.page_content}'")
    
    print(f"\n2. metadata (元数据字典):")
    print(f"   类型: {type(sample_doc.metadata)}")
    print(f"   值: {sample_doc.metadata}")
    
    # 演示 metadata 的字典操作
    print(f"\n3. metadata 字典操作演示:")
    print(f"   原始 metadata: {sample_doc.metadata}")
    
    # 添加新的元数据
    sample_doc.metadata['chunk_id'] = "doc_abc123_0"
    print(f"   添加 chunk_id 后: {sample_doc.metadata}")
    
    # 添加更多元数据
    sample_doc.metadata['chunk_index'] = 0
    sample_doc.metadata['total_chunks'] = 5
    print(f"   添加更多信息后: {sample_doc.metadata}")
    
    # 访问元数据
    print(f"\n4. 访问元数据:")
    print(f"   chunk_id: {sample_doc.metadata.get('chunk_id')}")
    print(f"   source: {sample_doc.metadata.get('source')}")
    print(f"   不存在的键: {sample_doc.metadata.get('nonexistent', 'default_value')}")

def demo_real_world_workflow():
    """演示真实世界的完整工作流程"""
    
    print("\n" + "=" * 80)
    print("真实工作流程演示")
    print("=" * 80)
    
    # 创建测试文件
    test_file = "workflow_demo.txt"
    test_content = """# 产品介绍

我们的产品是一个智能问答系统。

## 核心功能
1. 自然语言理解
2. 智能检索
3. 准确回答

## 技术特点
- 支持中文处理
- 实时响应
- 高准确率

## 应用场景
适用于客服、教育、企业知识管理等多个领域。"""
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("模拟 RAG 系统的完整处理流程:")
    
    # 步骤1: 加载文档
    print("\n步骤1: 使用 TextLoader 加载文档")
    loader = TextLoader(test_file, encoding='utf-8')
    new_docs = loader.load()
    print(f"  加载结果: {len(new_docs)} 个文档")
    print(f"  原始元数据: {new_docs[0].metadata}")
    
    # 步骤2: 分割文档
    print("\n步骤2: 使用 TextSplitter 分割文档")
    text_splitter = RecursiveCharacterTextSplitter(
        separators=[r'\n## ', r'\n# ', r'\n\n', r'\n'],
        is_separator_regex=True,
        keep_separator=True,
        chunk_size=150,
        chunk_overlap=30
    )
    chunks = text_splitter.split_documents(new_docs)
    print(f"  分割结果: {len(chunks)} 个块")
    
    # 步骤3: 添加文件信息到元数据（模拟企业级功能）
    print("\n步骤3: 添加文件信息到元数据")
    file_info = {
        'file_hash': hashlib.md5(test_content.encode()).hexdigest(),
        'file_mtime': 1640995200.0,  # 示例时间戳
        'file_size': len(test_content),
        'category': 'product',
        'data_source': '产品文档库'
    }
    
    for doc in chunks:
        doc.metadata.update(file_info)
    
    print(f"  添加文件信息后的元数据示例: {chunks[0].metadata}")
    
    # 步骤4: 生成唯一ID（原问题中的代码）
    print("\n步骤4: 为每个块生成唯一ID")
    file_path = test_file
    
    for i, chunk in enumerate(chunks):
        chunk_id = f"{config.DOCUMENT_ID_PREFIX}{hashlib.md5(file_path.encode()).hexdigest()}_{i}"
        chunk.metadata['chunk_id'] = chunk_id
        
        print(f"  Chunk {i}:")
        print(f"    ID: {chunk_id}")
        print(f"    内容长度: {len(chunk.page_content)} 字符")
        print(f"    内容预览: '{chunk.page_content[:50]}...'")
    
    # 步骤5: 最终结果展示
    print(f"\n步骤5: 最终处理结果")
    print(f"总共处理了 {len(chunks)} 个文档块，每个块都包含:")
    print(f"  - page_content: 分割后的文档内容")
    print(f"  - metadata: 包含源文件、文件信息、分类信息、唯一ID等")
    
    # 展示最终的完整结构
    print(f"\n最终的 chunk 对象完整结构示例:")
    sample_chunk = chunks[0]
    print(f"类型: {type(sample_chunk)}")
    print(f"内容: '{sample_chunk.page_content}'")
    print(f"完整元数据: {sample_chunk.metadata}")
    
    # 清理
    os.remove(test_file)

def demo_metadata_usage():
    """演示 metadata 的实际用途"""
    
    print("\n" + "=" * 80)
    print("Metadata 实际用途演示")
    print("=" * 80)
    
    print("""
chunk.metadata['chunk_id'] 的实际用途：

1. 数据库存储标识：
   - 向量数据库需要为每个文档块分配唯一ID
   - chunk_id 作为主键存储在数据库中
   
2. 检索结果追踪：
   - 用户查询时，返回的结果包含 chunk_id
   - 可以通过 chunk_id 定位到具体的文档块
   
3. 文档管理操作：
   - 更新文档时，通过 chunk_id 找到需要删除的旧块
   - 删除文档时，批量删除所有相关的块
   
4. 调试和监控：
   - 出现问题时，可以通过 chunk_id 快速定位
   - 日志记录和性能分析
   
5. 缓存和优化：
   - 基于 chunk_id 的缓存策略
   - 避免重复处理相同的文档块
""")
    
    # 模拟实际使用场景
    print("实际使用场景模拟:")
    
    # 创建示例块
    chunks = [
        Document(
            page_content="人工智能是计算机科学的重要分支。",
            metadata={
                'source': './data/ai_intro.txt',
                'chunk_id': 'doc_abc123_0',
                'category': 'technical'
            }
        ),
        Document(
            page_content="机器学习是AI的核心技术。",
            metadata={
                'source': './data/ai_intro.txt', 
                'chunk_id': 'doc_abc123_1',
                'category': 'technical'
            }
        )
    ]
    
    print(f"\n1. 向量数据库存储:")
    for chunk in chunks:
        chunk_id = chunk.metadata['chunk_id']
        content = chunk.page_content
        print(f"   INSERT INTO vectors (id, content, metadata) VALUES ('{chunk_id}', '{content}', ...)")
    
    print(f"\n2. 检索结果处理:")
    print(f"   用户查询: '什么是人工智能？'")
    print(f"   检索结果: chunk_id='doc_abc123_0', 相似度=0.95")
    print(f"   通过 chunk_id 获取完整信息和来源")
    
    print(f"\n3. 文档更新操作:")
    file_hash = "abc123"
    print(f"   DELETE FROM vectors WHERE id LIKE 'doc_{file_hash}_%'")
    print(f"   然后重新插入更新后的文档块")

if __name__ == "__main__":
    demo_chunk_structure()
    demo_metadata_assignment()
    demo_document_object_details()
    demo_real_world_workflow()
    demo_metadata_usage()