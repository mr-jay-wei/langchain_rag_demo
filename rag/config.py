# rag/config.py

from typing import Dict, Any

# --- 模型配置 ---

# 改回Hugging Face上的标准模型名称
EMBEDDING_MODEL_NAME: str = r'../local_models/bge-small-zh-v1.5'
RERANKER_MODEL_NAME: str = r'../local_models/bge-reranker-base/snapshots/2cfc18c9415c912f9d8155881c133215df768a70'

# 模型运行参数: 强制在CPU上运行，并设置缓存目录
MODEL_DEVICE: str = "cpu"
CACHE_DIR: str = "model_cache" # HuggingFaceEmbeddings会使用这个目录

EMBEDDING_MODEL_KWARGS: Dict[str, Any] = {"device": MODEL_DEVICE}
RERANKER_MODEL_KWARGS: Dict[str, Any] = {"device": MODEL_DEVICE}


# --- 文档处理配置 ---

# 文本分割块大小: 将文档分割成的小块的最大字符数
CHUNK_SIZE: int = 500
# 文本分割块重叠: 相邻块之间的重叠字符数，以保证语义连续性
CHUNK_OVERLAP: int = 150


# --- 检索与重排序配置 ---

# 向量检索Top K: 从向量数据库中初步检索出的最相似文档数量
RETRIEVER_TOP_K: int = 10

# 重排序Top N: 经过重排序后，最终选送给大语言模型的文档数量
RERANKER_TOP_N: int = 3