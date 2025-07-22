# test_enterprise_features.py
"""
测试企业级多路径和分类管理功能的脚本
"""

import os
import sys
import shutil
sys.path.append('.')

from rag.pipeline import RagPipeline
from rag import config

def setup_enterprise_directories():
    """设置企业级测试目录结构"""
    print("=" * 70)
    print("          企业级多路径和分类管理功能测试")
    print("=" * 70)
    
    # 创建多个数据源目录
    directories = [
        "./data",
        "./data/technical", 
        "./data/product"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"创建目录: {directory}")
    
    return directories

def create_categorized_test_files():
    """创建分类测试文件"""
    print("\n--- 创建分类测试文件 ---")
    
    # 通用文档 (./data)
    general_docs = {
        "公司介绍.txt": """
        我们是一家专注于人工智能技术的创新公司。
        公司成立于2020年，致力于为企业提供智能化解决方案。
        我们的核心业务包括自然语言处理、计算机视觉和机器学习平台。
        """,
        
        "企业文化.txt": """
        我们的企业文化以创新、协作、诚信为核心价值观。
        鼓励员工持续学习，追求技术卓越。
        重视团队合作，营造开放包容的工作环境。
        """
    }
    
    # 技术文档 (./data/technical)
    technical_docs = {
        "API文档.txt": """
        REST API接口说明文档
        
        1. 用户认证接口
        POST /api/auth/login
        参数: username, password
        返回: access_token, refresh_token
        
        2. 数据查询接口
        GET /api/data/query
        参数: query, limit, offset
        返回: data[], total_count
        
        3. 文件上传接口
        POST /api/files/upload
        参数: file (multipart/form-data)
        返回: file_id, file_url
        """,
        
        "系统架构.txt": """
        系统采用微服务架构设计，主要包括以下组件：
        
        1. API网关层：负责请求路由和认证
        2. 业务服务层：包括用户服务、数据服务、文件服务
        3. 数据存储层：MySQL主数据库、Redis缓存、MongoDB文档存储
        4. 消息队列：使用RabbitMQ处理异步任务
        5. 监控系统：Prometheus + Grafana监控告警
        """,
        
        "部署指南.txt": """
        生产环境部署步骤：
        
        1. 环境准备
        - Docker 20.10+
        - Kubernetes 1.20+
        - Helm 3.0+
        
        2. 配置文件
        - 修改config/production.yaml
        - 设置数据库连接信息
        - 配置Redis集群地址
        
        3. 部署命令
        helm install myapp ./charts/myapp -f config/production.yaml
        
        4. 验证部署
        kubectl get pods -n production
        curl http://api.example.com/health
        """
    }
    
    # 产品文档 (./data/product)
    product_docs = {
        "产品规格.txt": """
        智能问答系统 v2.0 产品规格书
        
        核心功能：
        1. 多轮对话支持，上下文理解能力强
        2. 支持文档、图片、音频多模态输入
        3. 实时流式回答，响应速度快
        4. 支持多种知识库格式导入
        
        技术指标：
        - 响应时间：< 2秒
        - 并发用户：10000+
        - 准确率：> 95%
        - 可用性：99.9%
        """,
        
        "用户手册.txt": """
        智能问答系统用户使用手册
        
        1. 快速开始
        - 注册账号并登录系统
        - 创建知识库项目
        - 上传文档资料
        - 开始智能问答
        
        2. 高级功能
        - 自定义问答模板
        - 设置回答风格
        - 配置敏感词过滤
        - 查看使用统计
        
        3. 常见问题
        Q: 支持哪些文档格式？
        A: 支持PDF、Word、TXT、Markdown等格式
        
        Q: 如何提高回答准确性？
        A: 提供高质量的知识库文档，定期更新内容
        """,
        
        "价格方案.txt": """
        智能问答系统价格方案
        
        基础版（免费）：
        - 1个知识库项目
        - 100MB存储空间
        - 1000次/月查询
        - 基础技术支持
        
        专业版（￥299/月）：
        - 10个知识库项目
        - 10GB存储空间
        - 50000次/月查询
        - 优先技术支持
        - API接口访问
        
        企业版（￥999/月）：
        - 无限知识库项目
        - 100GB存储空间
        - 无限次查询
        - 专属客服支持
        - 私有化部署选项
        """
    }
    
    # 创建文件
    for filename, content in general_docs.items():
        filepath = os.path.join("./data", filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"创建通用文档: {filename}")
    
    for filename, content in technical_docs.items():
        filepath = os.path.join("./data/technical", filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"创建技术文档: {filename}")
    
    for filename, content in product_docs.items():
        filepath = os.path.join("./data/product", filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"创建产品文档: {filename}")

def test_enterprise_sync():
    """测试企业级同步功能"""
    print("\n" + "="*50)
    print("测试企业级同步功能")
    print("="*50)
    
    # 启用企业级模式
    config.ENABLE_ENTERPRISE_MODE = True
    
    # 初始化RAG系统
    print("\n1. 初始化企业级RAG系统...")
    rag_pipeline = RagPipeline()
    
    # 执行同步
    print("\n2. 执行企业级同步...")
    rag_pipeline.sync_data_directory()
    
    return rag_pipeline

def test_category_queries(rag_pipeline):
    """测试分类查询功能"""
    print("\n" + "="*50)
    print("测试分类查询功能")
    print("="*50)
    
    # 获取可用类别
    categories = rag_pipeline.get_available_categories()
    print(f"\n可用类别: {categories}")
    
    # 获取数据源信息
    source_info = rag_pipeline.get_data_source_info()
    print(f"\n数据源信息:")
    for category, info in source_info.items():
        print(f"  - {category}: {info['count']} 个文档块")
    
    # 测试不同类别的查询
    test_cases = [
        {
            "question": "公司的核心业务是什么？",
            "categories": ["general"],
            "description": "通用类别查询"
        },
        {
            "question": "API接口如何使用？",
            "categories": ["technical"],
            "description": "技术类别查询"
        },
        {
            "question": "产品有哪些价格方案？",
            "categories": ["product"],
            "description": "产品类别查询"
        },
        {
            "question": "系统架构是怎样的？",
            "categories": ["technical"],
            "description": "技术架构查询"
        },
        {
            "question": "如何部署系统？",
            "categories": ["technical"],
            "description": "部署相关查询"
        },
        {
            "question": "企业版有什么功能？",
            "categories": ["product"],
            "description": "产品功能查询"
        },
        {
            "question": "公司文化是什么？",
            "categories": ["general", "product"],
            "description": "多类别查询"
        },
        {
            "question": "整个系统的情况如何？",
            "categories": None,  # 查询所有类别
            "description": "全类别查询"
        }
    ]
    
    print(f"\n开始分类查询测试...")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: {test_case['description']}")
        print(f"问题: {test_case['question']}")
        print(f"限定类别: {test_case['categories']}")
        print(f"{'='*60}")
        
        try:
            # 使用分类查询
            result = rag_pipeline.ask_with_categories(
                test_case['question'], 
                test_case['categories']
            )
            
            answer = result.get('result', '未获取到答案')
            sources = result.get('source_documents', [])
            
            print(f"\n【回答】")
            print(f"{answer}")
            
            print(f"\n【参考来源】({len(sources)} 个文档)")
            for j, doc in enumerate(sources, 1):
                source_file = os.path.basename(doc.metadata.get('source', '未知'))
                category = doc.metadata.get('category', '未知')
                data_source = doc.metadata.get('data_source', '未知')
                print(f"  [{j}] {source_file} (类别: {category})")
                print(f"      内容预览: {doc.page_content[:100].replace(chr(10), ' ')}...")
            
        except Exception as e:
            print(f"查询失败: {e}")
            import traceback
            traceback.print_exc()

def test_multi_path_management():
    """测试多路径管理功能"""
    print("\n" + "="*50)
    print("测试多路径管理功能")
    print("="*50)
    
    # 显示当前数据源配置
    print("\n当前企业级数据源配置:")
    for source_name, source_config in config.ENTERPRISE_DATA_SOURCES.items():
        if source_config.get('enabled', True):
            print(f"  - {source_name}:")
            print(f"    路径: {source_config['path']}")
            print(f"    类别: {source_config['category']}")
            print(f"    描述: {source_config['description']}")
            print(f"    优先级: {source_config.get('priority', 999)}")
            print(f"    文件模式: {source_config.get('file_patterns', ['*.txt'])}")
    
    # 测试添加新的数据源路径
    print(f"\n测试动态添加数据源...")
    
    # 创建一个新的测试目录
    new_path = "./data/research"
    if not os.path.exists(new_path):
        os.makedirs(new_path)
        print(f"创建新数据源目录: {new_path}")
    
    # 添加测试文件
    research_doc = """
    人工智能研究报告
    
    1. 当前AI技术发展趋势
    - 大语言模型持续发展，参数规模不断增大
    - 多模态AI成为新的研究热点
    - AI安全和可解释性受到更多关注
    
    2. 技术挑战
    - 计算资源需求巨大
    - 数据质量和隐私保护
    - 模型偏见和公平性问题
    
    3. 应用前景
    - 教育领域的个性化学习
    - 医疗诊断辅助系统
    - 自动驾驶技术成熟
    """
    
    research_file = os.path.join(new_path, "AI研究报告.txt")
    with open(research_file, 'w', encoding='utf-8') as f:
        f.write(research_doc.strip())
    print(f"创建研究文档: AI研究报告.txt")
    
    # 动态添加数据源配置（仅用于演示）
    print(f"\n注意: 要使用新数据源，需要在config.py中添加配置:")
    print(f"""
    "research": {{
        "path": "{new_path}",
        "category": "research",
        "description": "研究文档库",
        "enabled": True,
        "file_patterns": ["*.txt", "*.md"],
        "priority": 6
    }}
    """)

def cleanup_test_files():
    """清理测试文件"""
    cleanup = input("\n是否清理测试文件和目录？(y/n): ").lower().strip()
    if cleanup == 'y':
        print("\n清理测试文件...")
        
        # 删除测试文件
        test_files = [
            "./data/公司介绍.txt",
            "./data/企业文化.txt",
            "./data/technical/API文档.txt",
            "./data/technical/系统架构.txt", 
            "./data/technical/部署指南.txt",
            "./data/product/产品规格.txt",
            "./data/product/用户手册.txt",
            "./data/product/价格方案.txt"
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"删除文件: {file_path}")
        
        # 删除测试目录
        test_dirs = ["./data/research"]
        for dir_path in test_dirs:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                print(f"删除目录: {dir_path}")
        
        print("测试文件清理完成。")

def main():
    """主测试函数"""
    try:
        # 1. 设置测试环境
        setup_enterprise_directories()
        
        # 2. 创建分类测试文件
        create_categorized_test_files()
        
        # 3. 测试企业级同步
        rag_pipeline = test_enterprise_sync()
        
        # 4. 测试分类查询
        test_category_queries(rag_pipeline)
        
        # 5. 测试多路径管理
        test_multi_path_management()
        
        print(f"\n{'='*70}")
        print("企业级多路径和分类管理功能测试完成！")
        print(f"{'='*70}")
        
        # 6. 清理测试文件
        cleanup_test_files()
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()