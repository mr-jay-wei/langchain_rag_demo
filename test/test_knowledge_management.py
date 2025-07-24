# test_knowledge_management.py
"""
测试知识库管理功能的脚本
包括文件添加、修改、删除的智能同步功能
"""

import os
import sys
import time
import shutil
sys.path.append('.')

from rag.pipeline import RagPipeline
from rag.config import DATA_PATH

def setup_test_environment():
    """设置测试环境"""
    print("=" * 60)
    print("          知识库管理功能测试")
    print("=" * 60)
    
    # 确保数据目录存在
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"创建测试数据目录: {DATA_PATH}")
    
    return DATA_PATH

def create_test_file(filename: str, content: str):
    """创建测试文件"""
    filepath = os.path.join(DATA_PATH, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"创建测试文件: {filename}")
    return filepath

def modify_test_file(filename: str, new_content: str):
    """修改测试文件"""
    filepath = os.path.join(DATA_PATH, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"修改测试文件: {filename}")
    return filepath

def delete_test_file(filename: str):
    """删除测试文件"""
    filepath = os.path.join(DATA_PATH, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"删除测试文件: {filename}")
        return True
    return False

def test_knowledge_management():
    """测试知识库管理功能的完整流程"""
    
    # 1. 设置测试环境
    test_dir = setup_test_environment()
    
    # 2. 初始化RAG系统
    print("\n1. 初始化RAG系统...")
    rag_pipeline = RagPipeline()
    
    # 3. 第一阶段：添加初始文件
    print("\n" + "="*50)
    print("阶段1: 添加初始测试文件")
    print("="*50)
    
    # 创建初始测试文件
    initial_files = {
        "测试文档1.txt": """
        这是第一个测试文档。
        内容包括：Python编程语言的基础知识。
        Python是一种高级编程语言，具有简洁的语法。
        """,
        
        "测试文档2.txt": """
        这是第二个测试文档。
        内容包括：机器学习的基本概念。
        机器学习是人工智能的重要分支。
        """,
        
        "测试文档3.txt": """
        这是第三个测试文档。
        内容包括：数据库技术介绍。
        数据库用于存储和管理数据。
        """
    }
    
    for filename, content in initial_files.items():
        create_test_file(filename, content.strip())
    
    # 同步数据目录
    print("\n执行第一次同步...")
    rag_pipeline.sync_data_directory()
    
    # 测试查询
    print("\n测试初始查询...")
    result = rag_pipeline.ask("什么是Python？")
    print(f"查询结果: {result.get('result', '无结果')}")
    print(f"参考文档数量: {len(result.get('source_documents', []))}")
    
    # 4. 第二阶段：修改现有文件
    print("\n" + "="*50)
    print("阶段2: 修改现有文件")
    print("="*50)
    
    # 修改第一个文件
    modified_content = """
    这是第一个测试文档（已修改版本）。
    内容包括：Python编程语言的高级特性。
    Python是一种高级编程语言，具有简洁的语法和强大的库生态系统。
    Python特别适合用于数据科学、Web开发和人工智能领域。
    """
    
    modify_test_file("测试文档1.txt", modified_content.strip())
    
    # 等待一秒确保文件修改时间不同
    time.sleep(1)
    
    # 同步数据目录
    print("\n执行修改后的同步...")
    rag_pipeline.sync_data_directory()
    
    # 测试查询修改后的内容
    print("\n测试修改后的查询...")
    result = rag_pipeline.ask("Python适合用于哪些领域？")
    print(f"查询结果: {result.get('result', '无结果')}")
    print(f"参考文档数量: {len(result.get('source_documents', []))}")
    
    # 5. 第三阶段：添加新文件
    print("\n" + "="*50)
    print("阶段3: 添加新文件")
    print("="*50)
    
    # 添加新文件
    new_file_content = """
    这是新添加的测试文档。
    内容包括：深度学习技术介绍。
    深度学习是机器学习的一个子集，使用神经网络进行学习。
    深度学习在图像识别、自然语言处理等领域有广泛应用。
    """
    
    create_test_file("测试文档4.txt", new_file_content.strip())
    
    # 同步数据目录
    print("\n执行添加新文件后的同步...")
    rag_pipeline.sync_data_directory()
    
    # 测试查询新内容
    print("\n测试新文件内容查询...")
    result = rag_pipeline.ask("什么是深度学习？")
    print(f"查询结果: {result.get('result', '无结果')}")
    print(f"参考文档数量: {len(result.get('source_documents', []))}")
    
    # 6. 第四阶段：删除文件
    print("\n" + "="*50)
    print("阶段4: 删除文件")
    print("="*50)
    
    # 删除一个文件
    delete_test_file("测试文档2.txt")
    
    # 同步数据目录
    print("\n执行删除文件后的同步...")
    rag_pipeline.sync_data_directory()
    
    # 测试查询已删除文件的内容
    print("\n测试已删除文件内容查询...")
    result = rag_pipeline.ask("机器学习是什么？")
    print(f"查询结果: {result.get('result', '无结果')}")
    print(f"参考文档数量: {len(result.get('source_documents', []))}")
    
    # 7. 第五阶段：综合测试
    print("\n" + "="*50)
    print("阶段5: 综合功能测试")
    print("="*50)
    
    # 同时进行多种操作
    print("同时执行多种操作...")
    
    # 修改现有文件
    modify_test_file("测试文档3.txt", """
    这是第三个测试文档（大幅修改版本）。
    内容包括：现代数据库技术的全面介绍。
    数据库技术包括关系型数据库、NoSQL数据库和向量数据库。
    向量数据库特别适合AI应用，支持语义搜索和相似性检索。
    ChromaDB是一个优秀的开源向量数据库。
    """.strip())
    
    # 添加新文件
    create_test_file("测试文档5.txt", """
    这是最新的测试文档。
    内容包括：RAG系统架构设计。
    RAG（检索增强生成）结合了信息检索和文本生成。
    RAG系统通常包括文档加载、向量化、检索和生成四个主要步骤。
    """.strip())
    
    # 删除另一个文件
    delete_test_file("测试文档4.txt")
    
    time.sleep(1)
    
    # 执行综合同步
    print("\n执行综合同步...")
    rag_pipeline.sync_data_directory()
    
    # 综合测试查询
    test_queries = [
        "向量数据库有什么特点？",
        "RAG系统包括哪些步骤？",
        "Python的应用领域有哪些？"
    ]
    
    print("\n综合查询测试:")
    for i, query in enumerate(test_queries, 1):
        print(f"\n查询 {i}: {query}")
        result = rag_pipeline.ask(query)
        answer = result.get('result', '无结果')
        sources = result.get('source_documents', [])
        print(f"回答: {answer}")
        print(f"参考来源: {len(sources)} 个文档")
        if sources:
            for j, doc in enumerate(sources):
                source_file = os.path.basename(doc.metadata.get('source', '未知'))
                print(f"  [{j+1}] {source_file}")
    
    print("\n" + "="*60)
    print("知识库管理功能测试完成！")
    print("="*60)
    
    # 8. 清理测试环境（可选）
    cleanup = input("\n是否清理测试文件？(y/n): ").lower().strip()
    if cleanup == 'y':
        print("\n清理测试文件...")
        for filename in ["测试文档1.txt", "测试文档3.txt", "测试文档5.txt"]:
            delete_test_file(filename)
        print("测试文件清理完成。")

def test_manual_operations():
    """测试手动操作功能"""
    print("=" * 60)
    print("          手动知识库管理测试")
    print("=" * 60)
    
    # 初始化RAG系统
    rag_pipeline = RagPipeline()
    rag_pipeline.sync_data_directory()
    
    while True:
        print("\n请选择操作:")
        print("1. 查看当前文档列表")
        print("2. 删除指定文档")
        print("3. 更新指定文档")
        print("4. 同步数据目录")
        print("5. 测试查询")
        print("6. 退出")
        
        choice = input("请输入选择 (1-6): ").strip()
        
        if choice == '1':
            # 查看当前文档列表
            sources = rag_pipeline._get_processed_sources()
            print(f"\n当前数据库中有 {len(sources)} 个文档:")
            for i, source in enumerate(sources, 1):
                print(f"  {i}. {os.path.basename(source)}")
        
        elif choice == '2':
            # 删除指定文档
            sources = list(rag_pipeline._get_processed_sources())
            if not sources:
                print("数据库中没有文档。")
                continue
            
            print("\n当前文档列表:")
            for i, source in enumerate(sources, 1):
                print(f"  {i}. {os.path.basename(source)}")
            
            try:
                index = int(input("请输入要删除的文档编号: ")) - 1
                if 0 <= index < len(sources):
                    source_to_delete = sources[index]
                    if rag_pipeline.delete_documents_by_source(source_to_delete):
                        print(f"成功删除文档: {os.path.basename(source_to_delete)}")
                        # 重新构建问答链
                        rag_pipeline._load_all_documents()
                        rag_pipeline._build_qa_chain()
                    else:
                        print("删除失败。")
                else:
                    print("无效的编号。")
            except ValueError:
                print("请输入有效的数字。")
        
        elif choice == '3':
            # 更新指定文档
            sources = list(rag_pipeline._get_processed_sources())
            if not sources:
                print("数据库中没有文档。")
                continue
            
            print("\n当前文档列表:")
            for i, source in enumerate(sources, 1):
                print(f"  {i}. {os.path.basename(source)}")
            
            try:
                index = int(input("请输入要更新的文档编号: ")) - 1
                if 0 <= index < len(sources):
                    source_to_update = sources[index]
                    if os.path.exists(source_to_update):
                        if rag_pipeline.update_document(source_to_update):
                            print(f"成功更新文档: {os.path.basename(source_to_update)}")
                            # 重新构建问答链
                            rag_pipeline._load_all_documents()
                            rag_pipeline._build_qa_chain()
                        else:
                            print("更新失败。")
                    else:
                        print(f"文件不存在: {source_to_update}")
                else:
                    print("无效的编号。")
            except ValueError:
                print("请输入有效的数字。")
        
        elif choice == '4':
            # 同步数据目录
            print("\n正在同步数据目录...")
            rag_pipeline.sync_data_directory()
        
        elif choice == '5':
            # 测试查询
            question = input("\n请输入查询问题: ").strip()
            if question:
                result = rag_pipeline.ask(question)
                print(f"\n回答: {result.get('result', '无结果')}")
                sources = result.get('source_documents', [])
                if sources:
                    print(f"参考来源 ({len(sources)} 个):")
                    for i, doc in enumerate(sources, 1):
                        source_file = os.path.basename(doc.metadata.get('source', '未知'))
                        print(f"  [{i}] {source_file}")
        
        elif choice == '6':
            print("退出手动测试。")
            break
        
        else:
            print("无效的选择，请重新输入。")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        test_manual_operations()
    else:
        test_knowledge_management()