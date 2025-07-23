#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本

提供多种测试选项和便捷的测试执行
"""

import os
import sys
import subprocess
import time
import argparse


def run_quick_test():
    """运行快速测试"""
    print("🚀 运行快速 API 测试...")
    try:
        result = subprocess.run([sys.executable, "quick_api_test.py"], 
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 快速测试失败: {e}")
        return False


def run_unit_tests():
    """运行单元测试"""
    print("🧪 运行单元测试...")
    
    test_files = [
        "test_hybrid_search.py",
        "test_query_rewriting.py", 
        "test_knowledge_management.py",
        "test_enterprise_features.py"
    ]
    
    passed = 0
    total = len(test_files)
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n📝 运行 {test_file}...")
            try:
                result = subprocess.run([sys.executable, test_file], 
                                      capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    print(f"   ✅ {test_file} 通过")
                    passed += 1
                else:
                    print(f"   ❌ {test_file} 失败")
                    if result.stderr:
                        print(f"   错误: {result.stderr[:200]}...")
            except subprocess.TimeoutExpired:
                print(f"   ⏰ {test_file} 超时")
            except Exception as e:
                print(f"   ❌ {test_file} 执行失败: {e}")
        else:
            print(f"   ⚠️  {test_file} 不存在，跳过")
    
    print(f"\n📊 单元测试结果: {passed}/{total} 通过")
    return passed == total


def start_service_and_test():
    """启动服务并运行测试"""
    print("🌐 启动服务并运行完整测试...")
    
    # 启动服务
    print("1. 启动 RAG Web 服务...")
    try:
        service_process = subprocess.Popen(
            [sys.executable, "start_server.py", "--mode", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务启动
        print("⏳ 等待服务启动...")
        time.sleep(10)  # 给服务一些启动时间
        
        # 检查服务是否还在运行
        if service_process.poll() is not None:
            stdout, stderr = service_process.communicate()
            print(f"❌ 服务启动失败:")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return False
        
        print("✅ 服务启动成功")
        
        # 运行完整测试
        print("\n2. 运行完整服务测试...")
        try:
            result = subprocess.run(
                [sys.executable, "test_full_service.py", "--running"],
                capture_output=False, text=True, timeout=300
            )
            test_success = result.returncode == 0
        except subprocess.TimeoutExpired:
            print("⏰ 测试超时")
            test_success = False
        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
            test_success = False
        
        # 停止服务
        print("\n3. 停止服务...")
        service_process.terminate()
        try:
            service_process.wait(timeout=10)
            print("✅ 服务已停止")
        except subprocess.TimeoutExpired:
            service_process.kill()
            print("🔪 强制停止服务")
        
        return test_success
        
    except Exception as e:
        print(f"❌ 启动服务失败: {e}")
        return False


def run_api_examples():
    """运行 API 使用示例"""
    print("📖 运行 API 使用示例...")
    
    print("请确保服务已启动 (python start_server.py)")
    input("按 Enter 继续...")
    
    try:
        result = subprocess.run([sys.executable, "api_usage_examples.py"],
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ API 示例运行失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="RAG 系统测试运行器")
    
    parser.add_argument(
        "--test-type",
        choices=["quick", "unit", "full", "examples", "all"],
        default="quick",
        help="测试类型"
    )
    
    args = parser.parse_args()
    
    print("🧪 RAG 系统测试运行器")
    print("=" * 50)
    
    success = True
    
    if args.test_type == "quick":
        success = run_quick_test()
    
    elif args.test_type == "unit":
        success = run_unit_tests()
    
    elif args.test_type == "full":
        success = start_service_and_test()
    
    elif args.test_type == "examples":
        success = run_api_examples()
    
    elif args.test_type == "all":
        print("🔄 运行所有测试...")
        
        # 1. 快速测试
        print("\n" + "="*30 + " 快速测试 " + "="*30)
        quick_success = run_quick_test()
        
        # 2. 单元测试
        print("\n" + "="*30 + " 单元测试 " + "="*30)
        unit_success = run_unit_tests()
        
        # 3. 完整服务测试
        print("\n" + "="*30 + " 完整服务测试 " + "="*30)
        full_success = start_service_and_test()
        
        success = quick_success and unit_success and full_success
        
        # 总结
        print("\n" + "="*60)
        print("📊 所有测试结果总结:")
        print(f"   快速测试: {'✅ 通过' if quick_success else '❌ 失败'}")
        print(f"   单元测试: {'✅ 通过' if unit_success else '❌ 失败'}")
        print(f"   完整测试: {'✅ 通过' if full_success else '❌ 失败'}")
    
    # 最终结果
    print("\n" + "="*50)
    if success:
        print("🎉 所有测试通过!")
        print("\n💡 下一步:")
        print("   - 运行 'python start_server.py' 启动服务")
        print("   - 访问 http://localhost:8000/docs 查看 API 文档")
        print("   - 使用 'python test_api_client.py' 进行交互式测试")
    else:
        print("❌ 部分测试失败")
        print("\n🔧 故障排除:")
        print("   - 检查依赖是否正确安装: uv sync")
        print("   - 检查配置文件: .env")
        print("   - 检查模型文件路径: rag/config.py")
        print("   - 查看详细错误信息")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()