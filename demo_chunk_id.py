# demo_chunk_id.py
"""
演示文档块ID生成的详细过程
"""

import hashlib
import os
from typing import List

# 模拟配置
class Config:
    DOCUMENT_ID_PREFIX = "doc_"

config = Config()

def demo_chunk_id_generation():
    """演示文档块ID生成的完整过程"""
    
    print("=" * 80)
    print("文档块ID生成演示")
    print("=" * 80)
    
    # 示例文件路径
    file_paths = [
        "./data/技术文档.txt",
        "./data/product/产品介绍.txt", 
        "D:/documents/用户手册.txt",
        "/home/user/docs/API文档.md"
    ]
    
    for file_path in file_paths:
        print(f"\n文件路径: {file_path}")
        print("-" * 50)
        
        # 步骤1：文件路径编码
        print("步骤1：文件路径编码")
        file_path_bytes = file_path.encode()
        print(f"  原始路径: '{file_path}'")
        print(f"  编码后字节: {file_path_bytes}")
        print(f"  字节长度: {len(file_path_bytes)}")
        
        # 步骤2：计算MD5哈希
        print(f"\n步骤2：计算MD5哈希")
        md5_hash = hashlib.md5(file_path_bytes)
        hash_hex = md5_hash.hexdigest()
        print(f"  MD5哈希对象: {md5_hash}")
        print(f"  十六进制哈希: {hash_hex}")
        print(f"  哈希长度: {len(hash_hex)} 字符")
        
        # 步骤3：生成不同块的ID
        print(f"\n步骤3：生成文档块ID")
        print(f"  前缀: '{config.DOCUMENT_ID_PREFIX}'")
        
        # 模拟该文件被分割成5个块
        for i in range(5):
            chunk_id = f"{config.DOCUMENT_ID_PREFIX}{hash_hex}_{i}"
            print(f"  块 {i}: {chunk_id}")

def demo_real_world_example():
    """真实世界的例子"""
    
    print("\n" + "=" * 80)
    print("真实场景演示")
    print("=" * 80)
    
    # 创建测试文件
    test_files = {
        "公司介绍.txt": """我们是一家专注于人工智能技术的创新公司。
公司成立于2020年，致力于为企业提供智能化解决方案。
我们的核心业务包括自然语言处理、计算机视觉和机器学习平台。""",
        
        "API文档.txt": """REST API接口说明文档

1. 用户认证接口
POST /api/auth/login
参数: username, password
返回: access_token, refresh_token

2. 数据查询接口  
GET /api/data/query
参数: query, limit, offset
返回: data[], total_count"""
    }
    
    # 创建文件并演示ID生成
    for filename, content in test_files.items():
        # 创建文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n处理文件: {filename}")
        print(f"文件内容长度: {len(content)} 字符")
        print("-" * 40)
        
        # 模拟文档分割过程
        # 假设每100字符一个块
        chunk_size = 100
        chunks = []
        
        for i in range(0, len(content), chunk_size):
            chunk_content = content[i:i+chunk_size]
            chunks.append(chunk_content)
        
        print(f"分割成 {len(chunks)} 个块:")
        
        # 为每个块生成ID
        file_path = filename
        file_hash = hashlib.md5(file_path.encode()).hexdigest()
        
        print(f"文件路径哈希: {file_hash}")
        
        for i, chunk_content in enumerate(chunks):
            chunk_id = f"{config.DOCUMENT_ID_PREFIX}{file_hash}_{i}"
            print(f"\n块 {i}:")
            print(f"  ID: {chunk_id}")
            print(f"  长度: {len(chunk_content)} 字符")
            print(f"  内容: '{chunk_content[:50]}{'...' if len(chunk_content) > 50 else ''}'")
        
        # 清理文件
        os.remove(filename)

def demo_id_uniqueness():
    """演示ID的唯一性特征"""
    
    print("\n" + "=" * 80)
    print("ID唯一性演示")
    print("=" * 80)
    
    # 测试不同路径产生不同哈希
    test_paths = [
        "./data/document.txt",
        "./data/Document.txt",  # 大小写不同
        "./data/document.TXT",  # 扩展名大小写不同
        "./data/documents.txt", # 文件名稍有不同
        "./data/doc/document.txt", # 路径不同
    ]
    
    print("不同文件路径的哈希值:")
    hashes = {}
    
    for path in test_paths:
        hash_value = hashlib.md5(path.encode()).hexdigest()
        hashes[path] = hash_value
        print(f"路径: {path}")
        print(f"哈希: {hash_value}")
        print()
    
    # 检查是否有重复
    hash_values = list(hashes.values())
    unique_hashes = set(hash_values)
    
    print(f"总路径数: {len(test_paths)}")
    print(f"唯一哈希数: {len(unique_hashes)}")
    print(f"是否全部唯一: {'是' if len(hash_values) == len(unique_hashes) else '否'}")
    
    # 演示同一文件的不同块ID
    print(f"\n同一文件的不同块ID:")
    sample_path = "./data/document.txt"
    sample_hash = hashlib.md5(sample_path.encode()).hexdigest()
    
    for i in range(3):
        chunk_id = f"{config.DOCUMENT_ID_PREFIX}{sample_hash}_{i}"
        print(f"块 {i}: {chunk_id}")

def demo_practical_usage():
    """演示实际使用场景"""
    
    print("\n" + "=" * 80)
    print("实际使用场景演示")
    print("=" * 80)
    
    print("""
在RAG系统中，chunk_id的实际用途：

1. 数据库存储标识：
   - 每个文档块在向量数据库中都有唯一ID
   - 便于后续的查询、更新、删除操作

2. 文件关联追踪：
   - 通过ID可以知道某个块来自哪个文件
   - 文件路径哈希确保不同文件的块不会冲突

3. 块序号管理：
   - 序号 _i 表示块在原文件中的位置
   - 便于重建文档的原始顺序

4. 增量更新支持：
   - 文件修改时，可以精确删除该文件的所有块
   - 通过文件路径哈希快速定位相关块

5. 调试和维护：
   - 出现问题时可以快速定位到具体文件和块
   - 便于系统监控和日志分析
""")
    
    # 模拟数据库操作
    print("模拟数据库操作:")
    
    # 假设的文档块数据
    chunks_data = [
        {
            "id": "doc_a1b2c3d4e5f6789012345678901234567_0",
            "file": "./data/技术文档.txt",
            "content": "第一个块的内容..."
        },
        {
            "id": "doc_a1b2c3d4e5f6789012345678901234567_1", 
            "file": "./data/技术文档.txt",
            "content": "第二个块的内容..."
        },
        {
            "id": "doc_b2c3d4e5f6789012345678901234567a_0",
            "file": "./data/产品介绍.txt", 
            "content": "产品介绍的内容..."
        }
    ]
    
    print("\n数据库中的文档块:")
    for chunk in chunks_data:
        print(f"ID: {chunk['id']}")
        print(f"文件: {chunk['file']}")
        print(f"内容: {chunk['content']}")
        print()
    
    # 演示如何通过ID操作
    print("通过ID进行操作:")
    target_file = "./data/技术文档.txt"
    target_hash = "a1b2c3d4e5f6789012345678901234567"  # 假设的哈希值
    
    print(f"1. 查找文件 '{target_file}' 的所有块:")
    for chunk in chunks_data:
        if target_hash in chunk['id']:
            print(f"   找到块: {chunk['id']}")
    
    print(f"\n2. 删除文件 '{target_file}' 的所有块:")
    remaining_chunks = [chunk for chunk in chunks_data if target_hash not in chunk['id']]
    print(f"   删除前: {len(chunks_data)} 个块")
    print(f"   删除后: {len(remaining_chunks)} 个块")

def demo_edge_cases():
    """演示边界情况"""
    
    print("\n" + "=" * 80)
    print("边界情况演示")
    print("=" * 80)
    
    edge_cases = [
        "",  # 空路径
        "a",  # 单字符路径
        "非常长的文件路径" * 10,  # 很长的路径
        "./data/中文文件名.txt",  # 中文路径
        "./data/file with spaces.txt",  # 包含空格
        "./data/file-with-special@#$%.txt",  # 特殊字符
    ]
    
    print("各种边界情况的哈希值:")
    
    for i, path in enumerate(edge_cases):
        try:
            hash_value = hashlib.md5(path.encode()).hexdigest()
            chunk_id = f"{config.DOCUMENT_ID_PREFIX}{hash_value}_{0}"
            
            print(f"\n情况 {i+1}:")
            print(f"  路径: '{path}'")
            print(f"  路径长度: {len(path)}")
            print(f"  哈希: {hash_value}")
            print(f"  块ID: {chunk_id}")
            
        except Exception as e:
            print(f"\n情况 {i+1} 出错:")
            print(f"  路径: '{path}'")
            print(f"  错误: {e}")

if __name__ == "__main__":
    demo_chunk_id_generation()
    demo_real_world_example()
    demo_id_uniqueness()
    demo_practical_usage()
    demo_edge_cases()