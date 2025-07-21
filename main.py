# main.py

import os
from rag.pipeline import RagPipeline
from rag.config import DATA_PATH # 导入数据路径

def setup_data_directory():
    """检查并创建.data目录和示例文件（如果不存在）。"""
    if not os.path.exists(DATA_PATH):
        print(f"正在创建数据目录: {DATA_PATH}")
        os.makedirs(DATA_PATH)
    
    sample_file_path = os.path.join(DATA_PATH, "initial_doc.txt")
    if not os.path.exists(sample_file_path):
        print(f"正在创建示例文件: {sample_file_path}")
        with open(sample_file_path, "w", encoding="utf-8") as f:
            f.write("这是系统初始化的示例文档。你可以向.data目录添加更多.txt文件。")

def run_demo():
    """运行一个完整的RAG演示，具备智能数据同步功能。"""
    print("=" * 50)
    print("          欢迎使用本地RAG问答系统 (V3.0)")
    print("=" * 50)

    # 0. 准备工作：确保.data目录存在
    setup_data_directory()

    # 1. 初始化RAG Pipeline
    # 它会自动尝试加载现有数据库
    rag_pipeline = RagPipeline()

    # 2. 核心步骤：同步数据文件夹
    print("\n--- 正在检查并同步知识库 ---")
    rag_pipeline.sync_data_directory()
    
    # 3. 开始交互式问答
    print("\n--- 问答环节 ---")
    print("知识库已就绪。您可以开始提问了。输入 '退出' 或 'exit' 或 'quit' 来结束程序。")
    
    while True:
        question = input("\n[您]：")
        if question.lower() in ['退出', 'exit', 'quit']:
            print("感谢使用，再见！")
            break
            
        if not question.strip():
            print("[系统]：问题不能为空，请重新输入。")
            continue
            
        answer_dict = rag_pipeline.ask(question)
        
        print("\n" + "-"*20 + " 回答 " + "-"*20)
        print(f"[机器人]：{answer_dict.get('result', '未能获取到答案。').strip()}")
        
        source_documents = answer_dict.get('source_documents', [])
        if source_documents:
            print("\n--- 参考资料来源 ---")
            for i, doc in enumerate(source_documents):
                source = doc.metadata.get('source', '未知来源')
                print(f"[{i+1}] 来源: {os.path.basename(source)}")
                print(f"    内容: {doc.page_content.replace('\n', ' ')}\n")
        print("-" * 46)

if __name__ == "__main__":
    run_demo()