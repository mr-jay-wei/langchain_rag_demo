# demo_file_info.py
"""
演示文件信息获取的详细过程
"""

import os
import hashlib
import time
from datetime import datetime

def demo_file_info():
    """演示获取文件信息的过程"""
    
    # 创建一个测试文件
    test_file = "test_file_info.txt"
    test_content = """这是一个测试文件。
用于演示文件信息获取功能。
包含中文内容和英文内容。
Created for demonstration purposes."""
    
    # 写入测试文件
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("=" * 60)
    print("文件信息获取演示")
    print("=" * 60)
    
    # 步骤1：获取文件系统统计信息
    print("步骤1：获取文件系统统计信息")
    print("-" * 30)
    
    stat = os.stat(test_file)
    print(f"os.stat() 返回的对象类型: {type(stat)}")
    print(f"stat 对象的所有属性:")
    
    # 显示 stat 对象的所有属性
    for attr in dir(stat):
        if attr.startswith('st_'):
            value = getattr(stat, attr)
            print(f"  {attr}: {value}")
    
    print(f"\n重要属性解释:")
    print(f"  st_mtime (修改时间戳): {stat.st_mtime}")
    print(f"  st_mtime (可读格式): {datetime.fromtimestamp(stat.st_mtime)}")
    print(f"  st_size (文件大小): {stat.st_size} 字节")
    print(f"  st_ctime (创建时间戳): {stat.st_ctime}")
    print(f"  st_atime (访问时间戳): {stat.st_atime}")
    
    # 步骤2：读取文件内容
    print(f"\n步骤2：读取文件内容")
    print("-" * 30)
    
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"文件内容:")
    print(f"'{content}'")
    print(f"\n内容长度: {len(content)} 字符")
    print(f"内容类型: {type(content)}")
    
    # 步骤3：计算内容哈希值
    print(f"\n步骤3：计算内容哈希值")
    print("-" * 30)
    
    # 3.1 将字符串编码为字节
    content_bytes = content.encode('utf-8')
    print(f"编码后的字节: {content_bytes}")
    print(f"字节长度: {len(content_bytes)} 字节")
    print(f"字节类型: {type(content_bytes)}")
    
    # 3.2 计算MD5哈希
    md5_hash = hashlib.md5(content_bytes)
    print(f"\nMD5哈希对象: {md5_hash}")
    print(f"MD5哈希对象类型: {type(md5_hash)}")
    
    # 3.3 获取十六进制字符串
    hash_hex = md5_hash.hexdigest()
    print(f"MD5哈希值(十六进制): {hash_hex}")
    print(f"哈希值长度: {len(hash_hex)} 字符")
    print(f"哈希值类型: {type(hash_hex)}")
    
    # 步骤4：组装最终结果
    print(f"\n步骤4：组装最终结果")
    print("-" * 30)
    
    file_info = {
        'path': test_file,
        'mtime': stat.st_mtime,
        'size': stat.st_size,
        'hash': hash_hex
    }
    
    print(f"最终文件信息字典:")
    for key, value in file_info.items():
        print(f"  {key}: {value}")
    
    # 清理测试文件
    os.remove(test_file)
    print(f"\n测试文件已删除")

def demo_hash_comparison():
    """演示哈希值的作用 - 检测文件变化"""
    
    print("\n" + "=" * 60)
    print("哈希值变化检测演示")
    print("=" * 60)
    
    test_file = "hash_test.txt"
    
    # 创建原始文件
    original_content = "这是原始内容"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    # 获取原始哈希
    with open(test_file, 'r', encoding='utf-8') as f:
        content1 = f.read()
    hash1 = hashlib.md5(content1.encode('utf-8')).hexdigest()
    
    print(f"原始内容: '{original_content}'")
    print(f"原始哈希: {hash1}")
    
    # 等待1秒，修改文件
    time.sleep(1)
    modified_content = "这是修改后的内容"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    # 获取修改后的信息
    stat_after = os.stat(test_file)
    with open(test_file, 'r', encoding='utf-8') as f:
        content2 = f.read()
    hash2 = hashlib.md5(content2.encode('utf-8')).hexdigest()
    
    print(f"\n修改后内容: '{modified_content}'")
    print(f"修改后哈希: {hash2}")
    
    print(f"\n比较结果:")
    print(f"内容是否相同: {content1 == content2}")
    print(f"哈希是否相同: {hash1 == hash2}")
    print(f"修改时间变化: {stat_after.st_mtime}")
    
    # 演示相同内容的哈希
    print(f"\n相同内容哈希验证:")
    same_content = "这是原始内容"
    hash3 = hashlib.md5(same_content.encode('utf-8')).hexdigest()
    print(f"相同内容: '{same_content}'")
    print(f"相同内容哈希: {hash3}")
    print(f"与原始哈希相同: {hash1 == hash3}")
    
    # 清理
    os.remove(test_file)

def demo_encoding_importance():
    """演示编码的重要性"""
    
    print("\n" + "=" * 60)
    print("编码重要性演示")
    print("=" * 60)
    
    # 包含中文的字符串
    text = "你好世界Hello World"
    print(f"原始字符串: '{text}'")
    print(f"字符串长度: {len(text)} 字符")
    
    # 不同编码方式
    encodings = ['utf-8', 'gbk', 'ascii']
    
    for encoding in encodings:
        try:
            # 编码为字节
            encoded_bytes = text.encode(encoding)
            print(f"\n{encoding} 编码:")
            print(f"  字节表示: {encoded_bytes}")
            print(f"  字节长度: {len(encoded_bytes)} 字节")
            
            # 计算哈希
            hash_value = hashlib.md5(encoded_bytes).hexdigest()
            print(f"  MD5哈希: {hash_value}")
            
        except UnicodeEncodeError as e:
            print(f"\n{encoding} 编码失败: {e}")
    
    print(f"\n结论: 不同编码产生不同的字节序列，从而产生不同的哈希值")

def demo_practical_usage():
    """演示实际使用场景"""
    
    print("\n" + "=" * 60)
    print("实际使用场景演示")
    print("=" * 60)
    
    def get_file_info(file_path):
        """实际的文件信息获取函数"""
        try:
            stat = os.stat(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'path': file_path,
                'mtime': stat.st_mtime,
                'size': stat.st_size,
                'hash': hashlib.md5(content.encode('utf-8')).hexdigest()
            }
        except Exception as e:
            print(f"获取文件信息失败 {file_path}: {e}")
            return None
    
    # 创建测试文件
    test_files = {
        "doc1.txt": "这是第一个文档的内容。",
        "doc2.txt": "这是第二个文档的内容。",
        "doc3.txt": "这是第一个文档的内容。"  # 与doc1内容相同
    }
    
    print("创建测试文件并获取信息:")
    file_infos = {}
    
    for filename, content in test_files.items():
        # 创建文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 获取文件信息
        info = get_file_info(filename)
        file_infos[filename] = info
        
        print(f"\n{filename}:")
        print(f"  内容: '{content}'")
        print(f"  大小: {info['size']} 字节")
        print(f"  哈希: {info['hash']}")
        print(f"  修改时间: {datetime.fromtimestamp(info['mtime'])}")
    
    # 比较哈希值
    print(f"\n哈希值比较:")
    print(f"doc1.txt 和 doc3.txt 内容相同:")
    print(f"  哈希值相同: {file_infos['doc1.txt']['hash'] == file_infos['doc3.txt']['hash']}")
    print(f"doc1.txt 和 doc2.txt 内容不同:")
    print(f"  哈希值相同: {file_infos['doc1.txt']['hash'] == file_infos['doc2.txt']['hash']}")
    
    # 清理文件
    for filename in test_files.keys():
        os.remove(filename)
    
    print(f"\n实际应用:")
    print(f"1. 文件变更检测: 比较哈希值判断文件是否被修改")
    print(f"2. 重复文件检测: 相同哈希值表示内容相同")
    print(f"3. 数据完整性验证: 确保文件传输或存储过程中未损坏")
    print(f"4. 缓存失效判断: 哈希值变化时更新缓存")

if __name__ == "__main__":
    demo_file_info()
    demo_hash_comparison()
    demo_encoding_importance()
    demo_practical_usage()