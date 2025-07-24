# test_hybrid_search.py
"""
测试混合检索功能的简单脚本
"""

import os
import sys
sys.path.append('.')

from rag.pipeline import RagPipeline
from rag.config import DATA_PATH

def create_test_documents():
    """创建一些测试文档来验证混合检索功能"""
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
    
    # 创建包含不同类型内容的测试文档
    test_docs = {
        "技术文档.txt": """
        Python是一种高级编程语言，具有简洁的语法和强大的功能。
        机器学习是人工智能的一个重要分支，使用算法让计算机从数据中学习。
        深度学习使用神经网络来处理复杂的模式识别任务。
        自然语言处理(NLP)是让计算机理解和生成人类语言的技术。
        """,
        
        "产品介绍.txt": """
        我们的RAG系统支持向量检索和关键字检索两种模式。
        向量检索基于语义相似性，能够找到意思相近的内容。
        关键字检索基于精确匹配，适合查找特定的术语和概念。
        混合检索结合了两种方法的优势，提高了召回率和准确性。
        """,
        
        "使用指南.txt": """
        如何配置混合检索：
        1. 在config.py中设置ENABLE_HYBRID_SEARCH为True
        2. 调整VECTOR_SEARCH_WEIGHT和KEYWORD_SEARCH_WEIGHT权重
        3. 设置KEYWORD_RETRIEVER_TOP_K参数
        系统会自动使用jieba进行中文分词处理。
        """
    }
    
    for filename, content in test_docs.items():
        filepath = os.path.join(DATA_PATH, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            print(f"创建测试文档: {filename}")

def test_hybrid_search():
    """测试混合检索功能"""
    print("=" * 60)
    print("          混合检索功能测试")
    print("=" * 60)
    
    # 创建测试文档
    create_test_documents()
    
    # 初始化RAG系统
    print("\n1. 初始化RAG系统...")
    rag_pipeline = RagPipeline()
    
    # 同步数据
    print("\n2. 同步数据...")
    rag_pipeline.sync_data_directory()
    
    # 测试不同类型的查询
    test_queries = [
        "什么是机器学习？",  # 语义查询，应该能通过向量检索找到
        "RAG系统",  # 关键字查询，应该能通过关键字检索找到
        "jieba分词",  # 精确关键字查询
        "如何配置权重",  # 混合查询，需要语义理解和关键字匹配
        "Python编程语言"  # 混合查询
    ]
    
    print("\n3. 开始测试查询...")
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- 测试查询 {i}: {query} ---")
        
        try:
            result = rag_pipeline.ask(query)
            answer = result.get('result', '未获取到答案')
            sources = result.get('source_documents', [])
            
            print(f"回答: {answer}")
            print(f"参考来源数量: {len(sources)}")
            
            if sources:
                print("来源文件:")
                for j, doc in enumerate(sources):
                    source_file = os.path.basename(doc.metadata.get('source', '未知'))
                    print(f"  [{j+1}] {source_file}")
                    
        except Exception as e:
            print(f"查询出错: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成！")

if __name__ == "__main__":
    test_hybrid_search()