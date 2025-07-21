from rag.pipeline import RagPipeline
from langchain_core.documents import Document

def run_demo():
    """
    运行一个完整的RAG演示。

    该函数会依次执行以下步骤：
    1. 初始化RAG Pipeline，加载本地模型和LLM配置。
    2. 定义一个简单的文本知识库。
    3. 加载并处理知识库文档（分割、向量化、构建问答链）。
    4. 启动一个循环，接收用户输入并进行问答。
    5. 打印由LLM生成的结果以及答案的来源参考。
    """
    # 打印欢迎信息，增强用户体验
    print("=" * 50)
    print("          欢迎使用本地RAG问答系统")
    print("=" * 50)

    try:
        # 步骤 1: 初始化RAG Pipeline
        # 首次运行时会从网络下载所需模型到'model_cache'目录，请耐心等待。
        # 如果.env文件配置不正确，这里会抛出ValueError。
        rag_pipeline = RagPipeline()
    except ValueError as e:
        print(f"\n[错误] 初始化失败: {e}")
        print("请确保您已经在项目根目录创建了 .env 文件并正确配置了API信息。")
        return # 初始化失败，直接退出程序

    # 步骤 2: 定义知识库内容
    # 您可以替换成任何您想查询的文本内容，或者从文件中读取
    knowledge_base_text = """
    Python是一种由吉多·范罗苏姆（Guido van Rossum）在1989年底发明的解释型、面向对象、动态数据类型的高级程序设计语言。
    Python的设计哲学是“优雅”、“明确”、“简单”，强调代码的可读性和简洁的语法。
    与C++或Java等编译型语言相比，Python的运行速度较慢，但开发效率极高，能让开发者用更少的代码表达想法。
    它被广泛应用于Web开发（如Django、Flask框架）、数据科学（如Pandas、NumPy库）、人工智能（如TensorFlow、PyTorch库）和自动化脚本等领域。
    """
    
    # 步骤 3: 将文本包装成LangChain的Document对象并加载到Pipeline中
    print("\n--- 正在加载知识库 ---")
    # LangChain的许多加载器都以Document对象列表的形式返回数据
    documents = [Document(page_content=knowledge_base_text, metadata={"source": "内置文本"})]
    rag_pipeline.load_and_process_documents(documents)
    
    # 步骤 4: 开始交互式问答循环
    print("\n--- 问答环节 ---")
    print("您可以开始提问了。输入 '退出' 或 'exit' 来结束程序。")
    
    while True:
        # 获取用户输入
        question = input("\n[您]：")
        
        # 检查是否退出
        if question.lower() in ['退出', 'exit', 'quit']:
            print("感谢使用，再见！")
            break
            
        # 检查输入是否为空
        if not question.strip():
            print("[系统]：问题不能为空，请重新输入。")
            continue
            
        # 步骤 5: 调用ask方法获取答案
        # 这是调用RAG核心功能的关键一步
        answer_dict = rag_pipeline.ask(question)
        
        # 步骤 6: 格式化并打印结果
        print("\n" + "-"*20 + " 回答 " + "-"*20)
        # 使用.get()方法安全地获取'result'，避免因键不存在而报错
        print(f"[机器人]：{answer_dict.get('result', '未能获取到答案。').strip()}")
        
        # 打印参考的源文档，这是RAG的核心优势之一：答案可溯源
        source_documents = answer_dict.get('source_documents', [])
        if source_documents:
            print("\n--- 参考资料来源 ---")
            for i, doc in enumerate(source_documents):
                # 打印被引用的文本片段，将换行符替换为空格使输出更整洁
                print(f"[{i+1}] {doc.page_content.replace('\n', ' ')}\n")
        print("-" * 46)

# Python的标准入口点，确保只有当该文件被直接执行时，run_demo()才会被调用
if __name__ == "__main__":
    run_demo()