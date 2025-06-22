#!/usr/bin/env python3
"""
便捷启动脚本：大文件智能处理
直接从根目录运行 auto_process_large.py
"""

import sys
import subprocess
from pathlib import Path

def main():
    """运行大文件处理脚本"""
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent
    
    # 构建tools目录下的auto_process_large.py路径
    large_process_script = current_dir / "tools" / "auto_process_large.py"
    
    if not large_process_script.exists():
        print("❌ 错误: 找不到 auto_process_large.py 脚本")
        print(f"   预期路径: {large_process_script}")
        return 1
    
    # 运行脚本，传递所有命令行参数
    try:
        result = subprocess.run([
            sys.executable, 
            str(large_process_script)
        ] + sys.argv[1:])
        return result.returncode
    except KeyboardInterrupt:
        print("\n❌ 用户中断")
        return 1
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 