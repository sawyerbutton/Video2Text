#!/usr/bin/env python3
"""
Auto Process - 自动化视频转文本处理脚本

自动监控 videos_todo 目录中的视频文件，
将其转换为文本保存到 results 目录，
并将处理完的视频文件移动到 videos_done 目录。

使用方法:
python auto_process.py

Author: Video2Text Team
License: MIT
"""

import sys
import argparse
import logging
import time
from pathlib import Path
from typing import List

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

try:
    import colorama
    colorama.init()
    COLORAMA_AVAILABLE = True
    
    # ANSI color codes
    class Colors:
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        BLUE = '\033[94m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        BOLD = '\033[1m'
        END = '\033[0m'
except ImportError:
    COLORAMA_AVAILABLE = False
    
    class Colors:
        GREEN = YELLOW = RED = BLUE = CYAN = WHITE = BOLD = END = ''

# Add parent directory to path for imports
script_dir = Path(__file__).parent.absolute()
parent_dir = script_dir.parent
sys.path.insert(0, str(parent_dir))

# Import core modules
try:
    from core import (
        ConfigManager,
        FileManager,
        # AudioProcessor removed - faster-whisper handles video directly via PyAV
        WhisperTranscriber,
        PlatformUtils
    )
    from mp4_to_text import MP4ToTextProcessor
except ImportError as e:
    print(f"Error: Failed to import core modules: {e}")
    print("Please ensure all dependencies are installed and core modules are available.")
    print(f"Script directory: {script_dir}")
    print(f"Parent directory: {parent_dir}")
    sys.exit(1)


def print_header():
    """Print application header."""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 60)
    print("           Auto Process - 自动化视频转文本工具")
    print("=" * 60)
    print(f"{Colors.END}")


def validate_directories():
    """验证必要的目录结构"""
    # 使用项目根目录（tools的父目录）
    project_root = Path(__file__).parent.parent.absolute()
    
    # 定义目录路径
    videos_todo_dir = project_root / "videos_todo"
    results_dir = project_root / "results" 
    videos_done_dir = project_root / "videos_done"
    
    # 创建目录（如果不存在）
    videos_todo_dir.mkdir(exist_ok=True)
    results_dir.mkdir(exist_ok=True)
    videos_done_dir.mkdir(exist_ok=True)
    
    print(f"📁 目录配置:")
    print(f"  待处理视频: {videos_todo_dir}")
    print(f"  文本输出: {results_dir}")
    print(f"  已处理视频: {videos_done_dir}")
    print()
    
    return videos_todo_dir, results_dir, videos_done_dir


def check_videos_todo(videos_todo_dir: Path) -> List[Path]:
    """检查待处理视频目录中的文件"""
    supported_formats = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.webm', '.m4v', '.wmv', '.3gp', '.ogv'}
    
    video_files = []
    for file_path in videos_todo_dir.glob("*"):
        if file_path.is_file() and file_path.suffix.lower() in supported_formats:
            video_files.append(file_path)
    
    return sorted(video_files)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Auto Process - 自动化视频转文本处理脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用说明:
  1. 将需要处理的视频文件放在 videos_todo 目录中
  2. 运行此脚本: python auto_process.py
  3. 转换后的文本文件将保存在 results 目录中
  4. 处理完的视频文件将移动到 videos_done 目录中

支持的视频格式: .mp4, .avi, .mov, .mkv, .flv, .webm, .m4v
支持的模型: tiny, base, small, medium, large, large-v2, large-v3
支持的语言: auto, zh, en, ja, ko, fr, de, es, ru, pt, it, ar, hi
        """)
    
    # Model and processing options
    parser.add_argument('-m', '--model', type=str, default='medium',
                        choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'],
                        help='Whisper模型 (默认: medium)')
    parser.add_argument('-l', '--language', type=str, default='auto',
                        help='音频语言 (auto/zh/en/ja/ko/fr/de/es/ru/pt/it/ar/hi, 默认: auto)')
    parser.add_argument('-d', '--device', type=str, default='auto',
                        choices=['auto', 'cpu', 'cuda', 'mps'],
                        help='处理设备 (默认: auto)')
    
    # Parallel processing
    parser.add_argument('-w', '--workers', type=int, default=1,
                        help='并行处理数量 (默认: 1)')
    
    # Behavior options
    parser.add_argument('-s', '--skip-existing', action='store_true',
                        help='跳过已经处理过的文件')
    parser.add_argument('--no-cleanup', action='store_true',
                        help='不清理临时文件')
    parser.add_argument('--no-move', action='store_true',
                        help='不移动处理完的文件到videos_done目录')
    
    # Configuration
    parser.add_argument('-c', '--config', type=str,
                        help='配置文件路径')
    
    # Output options
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='详细输出')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='静默模式')
    
    # Information options
    parser.add_argument('--system-info', action='store_true',
                        help='显示系统信息并退出')
    parser.add_argument('--list-models', action='store_true',
                        help='列出可用模型并退出')
    
    return parser


def main():
    """Main entry point."""
    try:
        # Parse command line arguments
        parser = create_argument_parser()
        args = parser.parse_args()
        
        print_header()
        
        # Handle information requests
        if args.system_info:
            utils = PlatformUtils()
            utils.print_system_info()
            return 0
        
        if args.list_models:
            from core.transcriber import get_available_models, get_recommended_model
            print("可用的Whisper模型:")
            for model in get_available_models():
                print(f"  - {model}")
            print(f"\n推荐模型: {get_recommended_model()}")
            return 0
        
        # 验证目录结构
        videos_todo_dir, results_dir, videos_done_dir = validate_directories()
        
        # 检查待处理的视频文件
        video_files = check_videos_todo(videos_todo_dir)
        
        if not video_files:
            print(f"{Colors.YELLOW}📝 在 videos_todo 目录中没有找到待处理的视频文件{Colors.END}")
            print(f"   请将需要处理的视频文件放入: {videos_todo_dir}")
            print(f"   支持的格式: .mp4, .avi, .mov, .mkv, .flv, .webm, .m4v, .wmv, .3gp, .ogv")
            return 0
        
        print(f"{Colors.GREEN}🎬 找到 {len(video_files)} 个待处理的视频文件:{Colors.END}")
        for video_file in video_files:
            file_size = video_file.stat().st_size / (1024 * 1024)  # MB
            print(f"  - {video_file.name} ({file_size:.1f} MB)")
        print()
        
        # 创建配置管理器
        config_manager = ConfigManager(config_file=args.config)
        
        # 设置固定的输入输出目录
        config_manager.processing_config.input_dir = str(videos_todo_dir)
        config_manager.processing_config.output_dir = str(results_dir)
        
        # 从命令行参数更新配置
        if args.model:
            config_manager.processing_config.model_name = args.model
        if args.language:
            config_manager.processing_config.language = args.language
        if args.device:
            config_manager.processing_config.device = args.device
        if args.workers:
            config_manager.processing_config.max_workers = args.workers
        if args.skip_existing:
            config_manager.processing_config.skip_existing = True
        if args.no_cleanup:
            config_manager.processing_config.cleanup_temp = False
        if args.verbose:
            config_manager.processing_config.verbose = True
        if args.quiet:
            config_manager.processing_config.quiet = True
        
        # 设置日志
        if not args.quiet:
            logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)
        
        # 创建并运行处理器
        move_to_done = not args.no_move
        processor = MP4ToTextProcessor(
            config_manager, 
            move_to_done=move_to_done, 
            done_dir=str(videos_done_dir)
        )
        
        if not args.quiet:
            print(f"{Colors.BLUE}⚙️  处理配置:{Colors.END}")
            print(f"  模型: {config_manager.processing_config.model_name}")
            print(f"  语言: {config_manager.processing_config.language}")
            print(f"  设备: {config_manager.get_effective_device()}")
            print(f"  并行数: {config_manager.processing_config.max_workers}")
            print(f"  跳过已处理: {config_manager.processing_config.skip_existing}")
            print(f"  移动完成文件: {move_to_done}")
            print()
        
        # 开始处理
        print(f"{Colors.CYAN}🚀 开始处理视频文件...{Colors.END}")
        start_time = time.time()
        
        success = processor.process_batch()
        
        total_time = time.time() - start_time
        
        if success:
            print(f"{Colors.GREEN}✅ 处理完成！总耗时: {total_time:.1f}秒{Colors.END}")
            
            # 检查结果
            result_files = list(results_dir.glob("*.txt"))
            if result_files:
                print(f"{Colors.GREEN}📄 生成的文本文件:{Colors.END}")
                for result_file in result_files:
                    if result_file.name != '.processing_history.json':
                        file_size = result_file.stat().st_size / 1024  # KB
                        print(f"  - {result_file.name} ({file_size:.1f} KB)")
            
            if move_to_done:
                done_files = check_videos_todo(videos_done_dir)
                if done_files:
                    print(f"{Colors.GREEN}📁 已移动到完成目录的文件:{Colors.END}")
                    for done_file in done_files:
                        print(f"  - {done_file.name}")
        else:
            print(f"{Colors.RED}❌ 处理过程中遇到错误{Colors.END}")
            
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  用户中断处理{Colors.END}")
        return 130
    except Exception as e:
        print(f"{Colors.RED}❌ 错误: {e}{Colors.END}")
        if __debug__:
            import traceback
            traceback.print_exc()
        return 1
    finally:
        # 清理工作
        try:
            if 'processor' in locals():
                processor.transcriber.unload_model()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main()) 