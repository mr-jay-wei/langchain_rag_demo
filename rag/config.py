# rag/config.py

from typing import Dict, Any

# --- 模型配置 ---

# 改回Hugging Face上的标准模型名称
EMBEDDING_MODEL_NAME: str = r'../local_models/bge-small-zh-v1.5'
RERANKER_MODEL_NAME: str = r'../local_models/bge-reranker-base/snapshots/2cfc18c9415c912f9d8155881c133215df768a70'

# 模型运行参数: 强制在CPU上运行，并设置缓存目录
VECTOR_STORE_PATH: str = "my_chromadb_vector_store" 
MODEL_DEVICE: str = "cpu"
EMBEDDING_MODEL_KWARGS: Dict[str, Any] = {"device": MODEL_DEVICE}
RERANKER_MODEL_KWARGS: Dict[str, Any] = {"device": MODEL_DEVICE}

# --- 企业级多路径数据源配置 ---

# 传统单一数据路径（向后兼容）
DATA_PATH: str = "./data"

# 企业级多路径数据源配置
# 支持多个硬盘/目录，每个路径可以指定类别
ENTERPRISE_DATA_SOURCES: Dict[str, Dict[str, Any]] = {
    # 主数据目录
    "main": {
        "path": "./data",
        "category": "general",
        "description": "通用知识库",
        "enabled": True,
        "file_patterns": ["*.txt", "*.md", "*.pdf"],
        "priority": 1
    },
    
    # 技术文档目录
    "technical": {
        "path": "./data/technical",
        "category": "technical",
        "description": "技术文档库",
        "enabled": True,
        "file_patterns": ["*.txt", "*.md"],
        "priority": 2
    },
    
    # 产品文档目录
    "product": {
        "path": "./data/product",
        "category": "product",
        "description": "产品文档库",
        "enabled": True,
        "file_patterns": ["*.txt", "*.md"],
        "priority": 3
    },
    
    # 可以添加更多数据源，比如不同硬盘的路径
    # "disk_d": {
    #     "path": "D:/enterprise_docs",
    #     "category": "enterprise",
    #     "description": "企业文档库(D盘)",
    #     "enabled": True,
    #     "file_patterns": ["*.txt", "*.md", "*.pdf"],
    #     "priority": 4
    # },
    
    # "disk_e": {
    #     "path": "E:/research_docs",
    #     "category": "research",
    #     "description": "研究文档库(E盘)",
    #     "enabled": True,
    #     "file_patterns": ["*.txt", "*.md"],
    #     "priority": 5
    # }
}

# 是否启用企业级多路径模式
ENABLE_ENTERPRISE_MODE: bool = True

# 默认检索的类别（空列表表示检索所有类别）
DEFAULT_SEARCH_CATEGORIES: list = []  # 例如: ["technical", "product"]

# 类别优先级（数字越小优先级越高）
CATEGORY_PRIORITIES: Dict[str, int] = {
    "general": 1,
    "technical": 2,
    "product": 3,
    "enterprise": 4,
    "research": 5
}


# --- 文档处理配置 ---

# 文本分割块大小: 将文档分割成的小块的最大字符数
CHUNK_SIZE: int = 500
# 文本分割块重叠: 相邻块之间的重叠字符数，以保证语义连续性
CHUNK_OVERLAP: int = 150


# --- 检索与重排序配置 ---

# 向量检索Top K: 从向量数据库中初步检索出的最相似文档数量
RETRIEVER_TOP_K: int = 10

# 关键字检索Top K: 从关键字检索中获取的文档数量
KEYWORD_RETRIEVER_TOP_K: int = 5

# 混合检索权重配置
VECTOR_SEARCH_WEIGHT: float = 0.7  # 向量检索权重
KEYWORD_SEARCH_WEIGHT: float = 0.3  # 关键字检索权重

# 重排序Top N: 经过重排序后，最终选送给大语言模型的文档数量
RERANKER_TOP_N: int = 3

# 是否启用混合检索 (True: 混合检索, False: 仅向量检索)
ENABLE_HYBRID_SEARCH: bool = True

# --- 问题改写配置 ---

# 是否启用问题改写功能
ENABLE_QUERY_REWRITING: bool = True

# 问题改写数量: 将原问题改写成多少个相关问题
QUERY_REWRITE_COUNT: int = 3

# 问题改写时每个改写问题的检索数量
REWRITE_QUERY_TOP_K: int = 5

# 是否在最终结果中去重相似文档
ENABLE_DOCUMENT_DEDUPLICATION: bool = True

# --- 知识库管理配置 ---

# 是否启用智能文件监控和更新
ENABLE_FILE_MONITORING: bool = True

# 文件修改时间检查间隔(秒)，用于检测文件是否被修改
FILE_CHECK_INTERVAL: int = 1

# 是否在同步时自动删除不存在的文件对应的文档
AUTO_DELETE_MISSING_FILES: bool = True

# 文档ID前缀，用于标识文档块的来源文件
DOCUMENT_ID_PREFIX: str = "doc_"