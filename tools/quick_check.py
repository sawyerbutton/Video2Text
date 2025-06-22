#!/usr/bin/env python3
"""
快速检查脚本 - 验证项目环境和依赖
"""

import sys
import os
import subprocess
from pathlib import Path

# 颜色定义
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, status, details=""):
    """打印状态信息"""
    if status == "OK":
        status_color = Colors.GREEN + "✓" + Colors.ENDC
    elif status == "WARNING":
        status_color = Colors.YELLOW + "⚠" + Colors.ENDC
    else:  # ERROR
        status_color = Colors.RED + "✗" + Colors.ENDC
    
    print(f"{status_color} {message}")
    if details:
        print(f"    {details}")

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version >= (3, 9):
        print_status(f"Python版本: {version_str}", "OK")
        return True
    else:
        print_status(f"Python版本: {version_str}", "ERROR", "需要Python 3.9或更高版本")
        return False

def check_package_import(package_name, import_name=None):
    """检查Python包是否可以导入"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print_status(f"Python包 {package_name}", "OK")
        return True
    except ImportError:
        print_status(f"Python包 {package_name}", "ERROR", f"无法导入 {import_name}")
        return False

def check_ffmpeg():
    """检查FFmpeg是否可用"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print_status("FFmpeg", "OK", version_line)
            return True
        else:
            print_status("FFmpeg", "ERROR", "FFmpeg命令失败")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print_status("FFmpeg", "ERROR", "FFmpeg未找到或无法执行")
        return False

def check_project_structure():
    """检查项目结构"""
    required_files = [
        'mp4_to_text.py',
        'requirements.txt',
        'README.md',
        'core/__init__.py',
        'core/platform_utils.py',
        'core/config_manager.py',
        'core/file_manager.py',
        'core/audio_processor.py',
        'core/transcriber.py',
        'config/config.ini',
        'config/models.json',
        'examples/usage_examples.py',
        'examples/sample_config.ini'
    ]
    
    required_dirs = [
        'core',
        'config',
        'temp',
        'logs',
        'tests',
        'examples',
        'scripts'
    ]
    
    all_ok = True
    
    # 检查目录
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print_status(f"目录 {dir_name}/", "OK")
        else:
            print_status(f"目录 {dir_name}/", "ERROR", "目录不存在")
            all_ok = False
    
    # 检查文件
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists() and file_path.is_file():
            print_status(f"文件 {file_name}", "OK")
        else:
            print_status(f"文件 {file_name}", "ERROR", "文件不存在")
            all_ok = False
    
    return all_ok

def check_core_modules():
    """检查核心模块是否可以导入"""
    modules = [
        'core.platform_utils',
        'core.config_manager',
        'core.file_manager',
        'core.audio_processor',
        'core.transcriber'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print_status(f"模块 {module}", "OK")
        except ImportError as e:
            print_status(f"模块 {module}", "ERROR", str(e))
            all_ok = False
    
    return all_ok

def check_whisper_models():
    """检查Whisper模型信息"""
    try:
        import whisper
        models = whisper.available_models()
        print_status(f"Whisper模型", "OK", f"可用模型: {', '.join(models)}")
        return True
    except Exception as e:
        print_status("Whisper模型", "ERROR", str(e))
        return False

def check_device_availability():
    """检查设备可用性"""
    try:
        # 添加项目根目录到路径
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from core.platform_utils import PlatformUtils
        platform_utils = PlatformUtils()
        
        device, device_info = platform_utils.detect_device()
        print_status(f"计算设备", "OK", f"检测到设备: {device}")
        
        if device_info.get('cuda_available'):
            print_status("  CUDA支持", "OK", f"CUDA版本: {device_info.get('cuda_version', 'Unknown')}")
        elif device_info.get('mps_available'):
            print_status("  MPS支持", "OK", "Apple Silicon GPU可用")
        else:
            print_status("  GPU支持", "WARNING", "仅CPU可用，处理速度较慢")
        
        return True
    except Exception as e:
        print_status("设备检测", "ERROR", str(e))
        return False

def main():
    """主函数"""
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}           MP4ToText 项目环境检查{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print()
    
    checks = []
    
    print(f"{Colors.BLUE}1. 基础环境检查{Colors.ENDC}")
    print("-" * 40)
    checks.append(check_python_version())
    checks.append(check_ffmpeg())
    print()
    
    print(f"{Colors.BLUE}2. Python依赖检查{Colors.ENDC}")
    print("-" * 40)
    packages = [
        ('torch', 'torch'),
        ('openai-whisper', 'whisper'),
        ('ffmpeg-python', 'ffmpeg'),
        ('tqdm', 'tqdm'),
        ('psutil', 'psutil'),
        ('configparser', 'configparser')
    ]
    
    for package_name, import_name in packages:
        checks.append(check_package_import(package_name, import_name))
    print()
    
    print(f"{Colors.BLUE}3. 项目结构检查{Colors.ENDC}")
    print("-" * 40)
    checks.append(check_project_structure())
    print()
    
    print(f"{Colors.BLUE}4. 核心模块检查{Colors.ENDC}")
    print("-" * 40)
    checks.append(check_core_modules())
    print()
    
    print(f"{Colors.BLUE}5. Whisper模型检查{Colors.ENDC}")
    print("-" * 40)
    checks.append(check_whisper_models())
    print()
    
    print(f"{Colors.BLUE}6. 设备兼容性检查{Colors.ENDC}")
    print("-" * 40)
    checks.append(check_device_availability())
    print()
    
    # 总结
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}                检查结果总结{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    total_checks = len(checks)
    passed_checks = sum(checks)
    
    if passed_checks == total_checks:
        print(f"{Colors.GREEN}✅ 所有检查通过！ ({passed_checks}/{total_checks}){Colors.ENDC}")
        print(f"{Colors.GREEN}项目环境配置正确，可以开始使用。{Colors.ENDC}")
        return 0
    else:
        failed_checks = total_checks - passed_checks
        print(f"{Colors.RED}❌ {failed_checks} 个检查失败 ({passed_checks}/{total_checks}){Colors.ENDC}")
        print(f"{Colors.YELLOW}请根据上述错误信息修复环境问题。{Colors.ENDC}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 