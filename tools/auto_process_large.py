#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大文件视频转文本自动处理工具
采用分层策略和保守设置处理videos_large目录中的大文件
"""

import os
import sys
import time
import threading
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from mp4_to_text import MP4ToTextProcessor
from core.config_manager import ConfigManager
from core.file_manager import FileManager

class LargeFileProcessor:
    def __init__(self):
        # 使用项目根目录（tools的父目录）
        self.base_dir = Path(__file__).parent.parent.absolute()
        self.videos_dir = self.base_dir / "videos_large"
        self.results_dir = self.base_dir / "results"
        self.done_dir = self.base_dir / "videos_done"
        
        # 分层策略配置
        self.size_tiers = {
            "small": {"max_size": 200 * 1024 * 1024, "model": "base", "timeout": 1800},      # 30分钟
            "medium": {"max_size": 300 * 1024 * 1024, "model": "base", "timeout": 2700},     # 45分钟
            "large": {"max_size": 500 * 1024 * 1024, "model": "tiny", "timeout": 3600},      # 60分钟
            "huge": {"max_size": float('inf'), "model": "tiny", "timeout": 7200}             # 120分钟
        }
        
        self.current_tier = None
        self.timeout_thread = None
        self.process_killed = False
        
    def analyze_files(self):
        """分析文件并按大小分组"""
        if not self.videos_dir.exists():
            print(f"❌ 目录不存在: {self.videos_dir}")
            return {}
            
        files = list(self.videos_dir.glob("*.mp4"))
        if not files:
            print("📭 没有找到待处理的视频文件")
            return {}
            
        # 按大小分组
        groups = {"small": [], "medium": [], "large": [], "huge": []}
        
        for file_path in files:
            size = file_path.stat().st_size
            size_mb = size / (1024 * 1024)
            
            if size <= self.size_tiers["small"]["max_size"]:
                groups["small"].append((file_path, size, size_mb))
            elif size <= self.size_tiers["medium"]["max_size"]:
                groups["medium"].append((file_path, size, size_mb))
            elif size <= self.size_tiers["large"]["max_size"]:
                groups["large"].append((file_path, size, size_mb))
            else:
                groups["huge"].append((file_path, size, size_mb))
        
        return groups
    
    def print_analysis(self, groups):
        """打印文件分析结果"""
        print("\n" + "="*60)
        print("           大文件处理策略分析")
        print("="*60)
        
        total_files = sum(len(group) for group in groups.values())
        print(f"📁 总文件数: {total_files}")
        
        for tier_name, files in groups.items():
            if files:
                tier_config = self.size_tiers[tier_name]
                print(f"\n🎯 {tier_name.upper()} 层级 ({len(files)}个文件):")
                print(f"   模型: {tier_config['model']}")
                print(f"   超时: {tier_config['timeout']//60}分钟")
                
                for file_path, size, size_mb in files:
                    print(f"   📹 {file_path.name} ({size_mb:.1f}MB)")
    
    def setup_timeout_monitor(self, timeout_seconds, process_name):
        """设置超时监控"""
        self.process_killed = False
        
        def timeout_handler():
            time.sleep(timeout_seconds)
            if not self.process_killed:
                print(f"\n⚠️  超时警告: {process_name} 处理超过 {timeout_seconds//60} 分钟")
                print("   建议检查进程状态或考虑中断处理")
                # 这里不强制杀死进程，而是给出警告让用户决定
        
        self.timeout_thread = threading.Thread(target=timeout_handler, daemon=True)
        self.timeout_thread.start()
    
    def process_tier(self, tier_name, files):
        """处理指定层级的文件"""
        if not files:
            return True
            
        tier_config = self.size_tiers[tier_name]
        model = tier_config["model"]
        timeout = tier_config["timeout"]
        
        print(f"\n🚀 开始处理 {tier_name.upper()} 层级文件...")
        print(f"   使用模型: {model}")
        print(f"   超时设置: {timeout//60}分钟")
        
        # 创建配置管理器
        try:
            from core.config_manager import ConfigManager
            config_manager = ConfigManager()
            
            # 设置模型和设备
            config_manager.processing_config.model_name = model
            config_manager.processing_config.language = "auto"
            config_manager.processing_config.device = "cuda" if self.check_cuda() else "cpu"
            config_manager.processing_config.max_workers = 1
            config_manager.processing_config.input_dir = str(self.videos_dir)
            config_manager.processing_config.output_dir = str(self.results_dir)
            config_manager.processing_config.quiet = False
            
            processor = MP4ToTextProcessor(
                config_manager=config_manager,
                move_to_done=True,
                done_dir=str(self.done_dir)
            )
            
            success_count = 0
            total_count = len(files)
            
            for i, (file_path, size, size_mb) in enumerate(files, 1):
                print(f"\n📹 处理文件 {i}/{total_count}: {file_path.name} ({size_mb:.1f}MB)")
                
                # 设置超时监控
                self.setup_timeout_monitor(timeout, file_path.name)
                
                try:
                    start_time = time.time()
                    result = self.process_single_file_with_progress(file_path, size_mb, processor, tier_name, model)
                    end_time = time.time()
                    
                    self.process_killed = True  # 停止超时监控
                    
                    if result:
                        success_count += 1
                        duration = end_time - start_time
                        print(f"✅ 成功处理，用时 {duration:.1f}秒")
                    else:
                        print(f"❌ 处理失败")
                        
                except Exception as e:
                    self.process_killed = True
                    print(f"❌ 处理异常: {str(e)}")
                    print(f"   建议跳过此文件或使用更小的模型重试")
            
            print(f"\n📊 {tier_name.upper()} 层级处理完成:")
            print(f"   成功: {success_count}/{total_count}")
            print(f"   成功率: {success_count/total_count*100:.1f}%")
            
            return success_count == total_count
            
        except Exception as e:
            print(f"❌ 初始化处理器失败: {str(e)}")
            return False
    
    def check_cuda(self):
        """检查CUDA可用性"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def process_single_file_with_progress(self, file_path, size_mb, processor, tier_name, model_name):
        """
        处理单个视频文件，显示详细进度信息
        """
        start_time = time.time()
        
        # 获取视频信息
        video_info = processor.audio_processor.get_video_info(file_path)
        duration = video_info.get('duration', 0.0)
        
        print(f"\n{'='*60}")
        print(f"🎬 开始处理: {file_path.name}")
        print(f"📊 文件信息:")
        print(f"  📁 大小: {size_mb:.1f} MB")
        print(f"  ⏱️ 时长: {duration:.1f}秒 ({duration//60:.0f}分{duration%60:.0f}秒)")
        print(f"  🏷️ 层级: {tier_name}")
        print(f"  🤖 模型: {model_name}")
        print(f"  ⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        # 进度跟踪
        stage_progress = {'extract': 0.0, 'transcribe': 0.0}
        
        def audio_progress_callback(progress):
            """音频提取进度回调"""
            stage_progress['extract'] = progress
            elapsed = time.time() - start_time
            
            # 显示音频提取进度
            bar_length = 20
            filled_length = int(bar_length * progress)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            print(f"\r🎵 音频提取: [{bar}] {progress*100:.1f}% (用时: {elapsed:.0f}秒)", end='', flush=True)
        
        def transcribe_progress_callback(progress):
            """转录进度回调"""
            stage_progress['transcribe'] = progress
            elapsed = time.time() - start_time
            
            # 显示转录进度
            bar_length = 20
            filled_length = int(bar_length * progress)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # 计算总进度 (音频提取30%, 转录70%)
            overall = stage_progress['extract'] * 0.3 + stage_progress['transcribe'] * 0.7
            
            print(f"\r🎤 转录进度: [{bar}] {progress*100:.1f}% | 总进度: {overall*100:.1f}% (用时: {elapsed:.0f}秒)", end='', flush=True)
        
        try:
            # 验证视频文件
            is_valid, error_msg = processor.audio_processor.validate_video_file(file_path)
            if not is_valid:
                print(f"❌ 文件验证失败: {error_msg}")
                return False
            
            print("🎵 开始音频提取...")
            
            # 提取音频（带真实进度监控）
            audio_path = processor.audio_processor.extract_audio(
                file_path, 
                progress_callback=audio_progress_callback
            )
            
            print(f"\n✅ 音频提取完成")
            print("🎤 开始转录...")
            
            # 转录音频（带进度监控）
            result = processor.transcriber.transcribe(
                audio_path,
                language=processor.config.processing_config.language,
                progress_callback=transcribe_progress_callback
            )
            
            print(f"\n✅ 转录完成")
            
            if not result.text.strip():
                print("⚠️  警告: 未提取到文本内容")
                return False
            
            # 保存结果
            output_path = processor.file_manager.get_output_path(file_path)
            processor.transcriber.save_result(result, output_path)
            
            # 记录处理历史
            processing_time = time.time() - start_time
            processor.file_manager.mark_processed(
                file_path, success=True,
                duration=duration, processing_time=processing_time,
                model_used=model_name
            )
            
            # 移动文件到完成目录
            if processor.move_to_done and processor.done_dir:
                print("📁 移动文件到完成目录...")
                processor.file_manager.move_processed_file(file_path, processor.done_dir)
            
            # 清理临时文件
            if processor.config.processing_config.cleanup_temp:
                processor.audio_processor.cleanup_temp_audio(audio_path)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"\n✅ 处理完成!")
            print(f"📈 性能统计:")
            print(f"  ⏱️ 总用时: {total_time:.1f}秒 ({total_time//60:.0f}分{total_time%60:.0f}秒)")
            print(f"  🚀 RTF: {total_time/duration:.3f}" if duration > 0 else "")
            print(f"  📝 文本长度: {len(result.text)}字符")
            print(f"  💾 输出文件: {output_path}")
            
            return True
            
        except Exception as e:
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"\n❌ 处理失败!")
            print(f"  ⏱️ 用时: {total_time:.1f}秒")
            print(f"  🚨 错误: {str(e)}")
            
            # 记录失败
            processor.file_manager.mark_processed(
                file_path, success=False, error=str(e),
                duration=duration, processing_time=total_time,
                model_used=model_name
            )
            
            return False
    
    def interactive_mode(self, groups):
        """交互式处理模式"""
        print(f"\n🎮 交互式处理模式")
        print("请选择要处理的层级:")
        print("1. SMALL (150-200MB, base模型, 30分钟超时)")
        print("2. MEDIUM (200-300MB, base模型, 45分钟超时)")  
        print("3. LARGE (300-500MB, tiny模型, 60分钟超时)")
        print("4. HUGE (>500MB, tiny模型, 120分钟超时)")
        print("5. 全部处理 (按顺序逐层)")
        print("0. 退出")
        
        try:
            choice = input("\n请输入选择 (0-5): ").strip()
            
            if choice == "0":
                return
            elif choice == "1":
                self.process_tier("small", groups["small"])
            elif choice == "2":
                self.process_tier("medium", groups["medium"])
            elif choice == "3":
                self.process_tier("large", groups["large"])
            elif choice == "4":
                self.process_tier("huge", groups["huge"])
            elif choice == "5":
                for tier in ["small", "medium", "large", "huge"]:
                    if groups[tier]:
                        print(f"\n{'='*50}")
                        success = self.process_tier(tier, groups[tier])
                        if not success:
                            print(f"⚠️  {tier.upper()}层级处理未完全成功，是否继续？")
                            continue_choice = input("继续下一层级？(y/N): ").strip().lower()
                            if continue_choice not in ['y', 'yes']:
                                break
            else:
                print("❌ 无效选择")
                
        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断处理")
        except Exception as e:
            print(f"❌ 处理过程出错: {str(e)}")
    
    def run(self):
        """主运行函数"""
        print("🎬 大文件视频转文本处理工具启动...")
        
        # 分析文件
        groups = self.analyze_files()
        if not any(groups.values()):
            return
        
        # 打印分析结果
        self.print_analysis(groups)
        
        # 交互式处理
        self.interactive_mode(groups)
        
        print("\n✅ 处理完成！")

def main():
    processor = LargeFileProcessor()
    processor.run()

if __name__ == "__main__":
    main() 