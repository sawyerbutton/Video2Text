#!/usr/bin/env python3
"""
测试运行器 - 运行所有测试
"""

import unittest
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """运行所有测试"""
    print("=" * 60)
    print("           MP4ToText 项目测试")
    print("=" * 60)
    
    # 设置测试目录
    test_dir = Path(__file__).parent
    
    # 发现并运行测试
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir), pattern='test_*.py')
    
    # 设置测试运行器
    runner = unittest.TextTestRunner(
        verbosity=2,
        buffer=True,
        failfast=False
    )
    
    # 运行测试
    print(f"发现测试模块: {suite.countTestCases()} 个测试")
    print("-" * 60)
    
    result = runner.run(suite)
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("                测试结果摘要")
    print("=" * 60)
    
    print(f"运行测试数量: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    print("\n" + "=" * 60)
    
    # 根据测试结果返回适当的退出码
    if result.wasSuccessful():
        print("✅ 所有测试通过！")
        return 0
    else:
        print("❌ 存在测试失败或错误")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 