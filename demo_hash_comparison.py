# demo_hash_comparison.py
"""
演示文件修改检测的工作原理
"""

import os
import hashlib
import time
import json
from datetime import datetime

class FileChangeDetector:
    """文件变化检测器演示"""
    
    def __init__(self):
        # 模拟数据库，存储文件的历史信息
        self.database = {}
        self.db_file = "file_metadata_db.json"
        self._load_database()
    
    def _load_database(self):
        """加载数据库"""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                self.database = json.load(f)
        else:
            self.database = {}
    
    def _save_database(self):
        """保存数据库"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.database, f, indent=2, ensure_ascii=False)
    
    def _get_file_info(self, file_path: str):
        """获取文件当前信息（模拟原函数）"""
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
    
    def _get_file_metadata_from_db(self, file_path: str):
        """从数据库获取文件的历史元数据（模拟原函数）"""
        return self.database.get(file_path)
    
    def _is_file_modified(self, file_path: str) -> bool:
        """检查文件是否已被修改（原函数）"""
        print(f"\n🔍 检查文件是否修改: {file_path}")
        
        # 1. 获取当前文件信息
        current_info = self._get_file_info(file_path)
        if not current_info:
            print("  ❌ 无法获取当前文件信息")
            return False
        
        print(f"  📄 当前文件哈希: {current_info['hash']}")
        print(f"  📄 当前文件大小: {current_info['size']} 字节")
        print(f"  📄 当前修改时间: {datetime.fromtimestamp(current_info['mtime'])}")
        
        # 2. 获取数据库中的历史信息
        db_metadata = self._get_file_metadata_from_db(file_path)
        if not db_metadata:
            print("  🆕 数据库中没有该文件记录，视为新文件")
            return True  # 数据库中没有该文件，视为新文件
        
        print(f"  💾 数据库中哈希: {db_metadata.get('file_hash', 'N/A')}")
        print(f"  💾 数据库中大小: {db_metadata.get('file_size', 'N/A')} 字节")
        print(f"  💾 数据库记录时间: {datetime.fromtimestamp(db_metadata.get('file_mtime', 0))}")
        
        # 3. 比较哈希值
        db_hash = db_metadata.get('file_hash')
        is_modified = current_info['hash'] != db_hash
        
        if is_modified:
            print("  ✅ 文件已被修改！")
        else:
            print("  ⭕ 文件未被修改")
        
        return is_modified
    
    def store_file_info(self, file_path: str):
        """将文件信息存储到数据库"""
        info = self._get_file_info(file_path)
        if info:
            self.database[file_path] = {
                'file_hash': info['hash'],
                'file_size': info['size'],
                'file_mtime': info['mtime'],
                'stored_at': time.time()
            }
            self._save_database()
            print(f"✅ 已将文件信息存储到数据库: {file_path}")

def demo_file_modification_detection():
    """演示文件修改检测的完整过程"""
    
    print("=" * 80)
    print("文件修改检测演示")
    print("=" * 80)
    
    detector = FileChangeDetector()
    test_file = "modification_test.txt"
    
    # 阶段1：创建初始文件
    print("\n📝 阶段1：创建初始文件")
    print("-" * 40)
    
    initial_content = """这是初始文件内容。
包含一些基本信息。
创建时间：2024年"""
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(initial_content)
    
    print(f"创建文件: {test_file}")
    print(f"初始内容:\n{initial_content}")
    
    # 第一次检查（新文件）
    is_modified_1 = detector._is_file_modified(test_file)
    print(f"第一次检查结果: {'已修改' if is_modified_1 else '未修改'}")
    
    # 存储文件信息到数据库
    detector.store_file_info(test_file)
    
    # 阶段2：再次检查（应该显示未修改）
    print("\n🔄 阶段2：立即再次检查")
    print("-" * 40)
    
    is_modified_2 = detector._is_file_modified(test_file)
    print(f"第二次检查结果: {'已修改' if is_modified_2 else '未修改'}")
    
    # 阶段3：修改文件内容
    print("\n✏️ 阶段3：修改文件内容")
    print("-" * 40)
    
    time.sleep(1)  # 确保修改时间不同
    
    modified_content = """这是修改后的文件内容。
包含一些更新的信息。
创建时间：2024年
修改时间：2025年"""
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"修改后内容:\n{modified_content}")
    
    # 第三次检查（应该显示已修改）
    is_modified_3 = detector._is_file_modified(test_file)
    print(f"第三次检查结果: {'已修改' if is_modified_3 else '未修改'}")
    
    # 阶段4：更新数据库记录
    print("\n💾 阶段4：更新数据库记录")
    print("-" * 40)
    
    detector.store_file_info(test_file)
    
    # 第四次检查（应该显示未修改）
    is_modified_4 = detector._is_file_modified(test_file)
    print(f"第四次检查结果: {'已修改' if is_modified_4 else '未修改'}")
    
    # 阶段5：仅修改文件时间，内容不变
    print("\n⏰ 阶段5：仅修改文件访问时间（内容不变）")
    print("-" * 40)
    
    # 读取文件（会更新访问时间，但不会更新修改时间和内容）
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用touch命令更新访问时间（如果在Unix系统上）
    # 这里我们通过重新写入相同内容来模拟
    time.sleep(1)
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)  # 写入相同内容
    
    is_modified_5 = detector._is_file_modified(test_file)
    print(f"第五次检查结果: {'已修改' if is_modified_5 else '未修改'}")
    print("注意：即使文件时间戳改变，但内容相同，哈希值也相同，所以显示未修改")
    
    # 清理
    os.remove(test_file)
    if os.path.exists(detector.db_file):
        os.remove(detector.db_file)
    
    print(f"\n🧹 清理完成")

def demo_hash_sensitivity():
    """演示哈希值对内容变化的敏感性"""
    
    print("\n" + "=" * 80)
    print("哈希值敏感性演示")
    print("=" * 80)
    
    test_cases = [
        "这是原始内容",
        "这是原始内容。",  # 添加一个句号
        "这是原始内容 ",   # 添加一个空格
        "这是原始內容",    # 改变一个字符
        "这是原始内容\n",  # 添加换行符
    ]
    
    print("演示微小变化如何导致完全不同的哈希值：\n")
    
    for i, content in enumerate(test_cases):
        hash_value = hashlib.md5(content.encode('utf-8')).hexdigest()
        print(f"内容 {i+1}: '{repr(content)}'")
        print(f"哈希值: {hash_value}")
        print(f"长度: {len(content)} 字符")
        print("-" * 60)

def demo_practical_workflow():
    """演示实际工作流程"""
    
    print("\n" + "=" * 80)
    print("实际工作流程演示")
    print("=" * 80)
    
    print("""
实际RAG系统中的工作流程：

1. 系统启动时：
   - 扫描data目录中的所有文件
   - 对每个文件调用 _is_file_modified()
   - 如果是新文件或已修改文件，重新处理并更新数据库

2. 文件检查过程：
   - current_info['hash'] ← 读取当前文件内容计算哈希
   - db_hash ← 从数据库读取上次存储的哈希
   - 比较两个哈希值判断是否修改

3. 处理结果：
   - 如果哈希值不同 → 文件已修改 → 重新向量化
   - 如果哈希值相同 → 文件未修改 → 跳过处理

4. 更新数据库：
   - 处理完文件后，将新的哈希值存储到数据库
   - 下次检查时使用这个新哈希值作为基准

这样就实现了高效的增量更新！
""")

if __name__ == "__main__":
    demo_file_modification_detection()
    demo_hash_sensitivity()
    demo_practical_workflow()