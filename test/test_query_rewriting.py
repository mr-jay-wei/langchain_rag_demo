# test_query_rewriting.py
"""
测试问题改写功能的脚本
"""

import os
import sys
sys.path.append('.')

from rag.pipeline import RagPipeline
from rag.config import DATA_PATH

def create_test_documents():
    """创建一些测试文档来验证问题改写功能"""
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
    
    # 创建包含不同主题内容的测试文档
    test_docs = {
        "AI技术文档.txt": """
        人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。
        机器学习是AI的核心技术之一，通过算法让计算机从数据中学习模式和规律。
        深度学习使用多层神经网络来处理复杂的模式识别和预测任务。
        自然语言处理(NLP)专注于让计算机理解、解释和生成人类语言。
        计算机视觉技术使机器能够识别和理解图像和视频内容。
        """,
        
        "RAG系统介绍.txt": """
        检索增强生成(RAG)是一种结合信息检索和文本生成的AI技术。
        RAG系统首先从知识库中检索相关信息，然后基于检索到的内容生成答案。
        向量数据库是RAG系统的核心组件，用于存储和检索文档的向量表示。
        嵌入模型将文本转换为高维向量，使得语义相似的文本在向量空间中距离较近。
        混合检索结合了向量检索和关键字检索，提高了信息检索的准确性和覆盖面。
        """,
        
        "编程语言对比.txt": """
        Python是一种高级编程语言，以其简洁的语法和强大的库生态系统而闻名。
        Java是一种面向对象的编程语言，具有"一次编写，到处运行"的特性。
        JavaScript主要用于Web开发，既可以在浏览器端运行，也可以在服务器端运行。
        C++是一种系统级编程语言，提供了对硬件的底层控制能力。
        Go语言由Google开发，专注于并发编程和云原生应用开发。
        """,
        
        "数据库技术.txt": """
        关系型数据库使用表格结构存储数据，支持ACID事务特性。
        NoSQL数据库包括文档数据库、键值数据库、列族数据库和图数据库。
        向量数据库专门用于存储和检索高维向量数据，支持相似性搜索。
        ChromaDB是一个开源的向量数据库，特别适合AI应用的嵌入存储。
        数据库索引可以显著提高查询性能，但会增加存储开销。
        """
    }
    
    for filename, content in test_docs.items():
        filepath = os.path.join(DATA_PATH, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            print(f"创建测试文档: {filename}")

def test_query_rewriting():
    """测试问题改写功能"""
    print("=" * 70)
    print("          问题改写功能测试")
    print("=" * 70)
    
    # 创建测试文档
    create_test_documents()
    
    try:
        # 初始化RAG系统
        print("\n1. 初始化RAG系统...")
        rag_pipeline = RagPipeline()
        
        # 同步数据
        print("\n2. 同步数据...")
        rag_pipeline.sync_data_directory()
        
        # 测试不同类型的查询
        test_queries = [
            "什么是人工智能？",           # 概念性问题
            "Python有什么特点？",        # 特定技术问题
            "RAG系统如何工作？",         # 工作原理问题
            "向量数据库的优势是什么？",   # 优势分析问题
            "如何选择编程语言？"         # 选择建议问题
        ]
        
        print("\n3. 开始测试问题改写和检索...")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*50}")
            print(f"测试查询 {i}: {query}")
            print(f"{'='*50}")
            
            try:
                # 执行查询（会自动进行问题改写）
                result = rag_pipeline.ask(query)
                
                # 显示结果
                answer = result.get('result', '未获取到答案')
                sources = result.get('source_documents', [])
                
                print(f"\n【最终答案】")
                print(f"{answer}")
                
                print(f"\n【参考来源】({len(sources)} 个文档)")
                for j, doc in enumerate(sources):
                    source_file = os.path.basename(doc.metadata.get('source', '未知'))
                    content_preview = doc.page_content[:150].replace('\n', ' ')
                    print(f"  [{j+1}] {source_file}")
                    print(f"      {content_preview}...")
                
            except Exception as e:
                print(f"查询执行失败: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*70}")
        print("问题改写功能测试完成！")
        print(f"{'='*70}")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

def test_with_and_without_rewriting():
    """对比启用和禁用问题改写的效果"""
    print("=" * 70)
    print("          问题改写效果对比测试")
    print("=" * 70)
    
    # 创建测试文档
    create_test_documents()
    
    try:
        from rag import config
        
        test_query = "深度学习和机器学习有什么区别？"
        
        print(f"\n测试问题: {test_query}")
        print("-" * 50)
        
        # 测试1: 启用问题改写
        print("\n【测试1: 启用问题改写】")
        config.ENABLE_QUERY_REWRITING = True
        rag_pipeline1 = RagPipeline()
        rag_pipeline1.sync_data_directory()
        
        result1 = rag_pipeline1.ask(test_query)
        print(f"答案: {result1.get('result', '未获取到答案')}")
        print(f"参考文档数量: {len(result1.get('source_documents', []))}")
        
        # 测试2: 禁用问题改写
        print(f"\n{'='*50}")
        print("【测试2: 禁用问题改写】")
        config.ENABLE_QUERY_REWRITING = False
        rag_pipeline2 = RagPipeline()
        rag_pipeline2.sync_data_directory()
        
        result2 = rag_pipeline2.ask(test_query)
        print(f"答案: {result2.get('result', '未获取到答案')}")
        print(f"参考文档数量: {len(result2.get('source_documents', []))}")
        
        # 恢复默认设置
        config.ENABLE_QUERY_REWRITING = True
        
        print(f"\n{'='*70}")
        print("对比测试完成！")
        print("可以看到问题改写功能对检索效果的影响。")
        print(f"{'='*70}")
        
    except Exception as e:
        print(f"对比测试中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        test_with_and_without_rewriting()
    else:
        test_query_rewriting()