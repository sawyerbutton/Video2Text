#!/usr/bin/env python3
"""
测试文件管理模块
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.file_manager import FileManager


class TestFileManager(unittest.TestCase):
    """文件管理器测试类"""
    
    def setUp(self):
        """测试前设置"""
        self.temp_input_dir = tempfile.mkdtemp()
        self.temp_output_dir = tempfile.mkdtemp()
        self.file_manager = FileManager(
            input_dir=self.temp_input_dir,
            output_dir=self.temp_output_dir
        )
        
        # 创建测试视频文件（空文件）
        self.test_video_files = [
            'video1.mp4',
            'video2.avi',
            'video3.mov',
            'document.txt',  # 不是视频文件
            'audio.mp3'      # 不是支持的格式
        ]
        
        for filename in self.test_video_files:
            (Path(self.temp_input_dir) / filename).touch()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_input_dir):
            shutil.rmtree(self.temp_input_dir)
        if os.path.exists(self.temp_output_dir):
            shutil.rmtree(self.temp_output_dir)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertTrue(self.file_manager.input_dir.exists())
        self.assertTrue(self.file_manager.output_dir.exists())
        self.assertTrue(self.file_manager.temp_dir.exists())
    
    def test_scan_videos(self):
        """测试视频文件扫描"""
        video_files = self.file_manager.scan_videos()
        
        # 应该找到3个视频文件
        self.assertEqual(len(video_files), 3)
        
        # 检查文件名
        video_names = [f.name for f in video_files]
        self.assertIn('video1.mp4', video_names)
        self.assertIn('video2.avi', video_names)
        self.assertIn('video3.mov', video_names)
        self.assertNotIn('document.txt', video_names)
        self.assertNotIn('audio.mp3', video_names)
    
    def test_get_output_path(self):
        """测试输出路径生成"""
        video_path = Path(self.temp_input_dir) / 'video1.mp4'
        output_path = self.file_manager.get_output_path(video_path)
        
        self.assertEqual(output_path.suffix, '.txt')
        self.assertEqual(output_path.stem, 'video1')
        self.assertTrue(str(output_path).startswith(str(self.file_manager.output_dir)))
    
    def test_temp_audio_path(self):
        """测试临时音频文件路径生成"""
        video_path = Path(self.temp_input_dir) / 'video1.mp4'
        temp_path = self.file_manager.get_temp_audio_path(video_path)
        
        self.assertEqual(temp_path.suffix, '.wav')
        self.assertTrue(str(temp_path).startswith(str(self.file_manager.temp_dir)))
        self.assertIn('audio', str(temp_path))
    
    def test_is_processed(self):
        """测试处理状态检查"""
        video_path = Path(self.temp_input_dir) / 'video1.mp4'
        
        # 初始状态应该是未处理
        self.assertFalse(self.file_manager.is_processed(video_path, skip_existing=True))
        
        # 创建输出文件后应该被识别为已处理
        output_path = self.file_manager.get_output_path(video_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("test transcription")
        
        self.assertTrue(self.file_manager.is_processed(video_path, skip_existing=True))
        
        # 如果不跳过已存在的文件，应该返回False
        self.assertFalse(self.file_manager.is_processed(video_path, skip_existing=False))
    
    def test_mark_processed(self):
        """测试标记文件为已处理"""
        video_path = Path(self.temp_input_dir) / 'video1.mp4'
        
        # 标记为成功处理
        self.file_manager.mark_processed(
            video_path=video_path,
            success=True,
            duration=120.5,
            processing_time=30.2,
            model_used='medium'
        )
        
        # 检查处理历史
        stats = self.file_manager.get_processing_stats()
        self.assertEqual(stats['total_processed'], 1)
        self.assertEqual(stats['successful'], 1)
        self.assertEqual(stats['failed'], 0)
    
    def test_processing_stats(self):
        """测试处理统计"""
        video_path1 = Path(self.temp_input_dir) / 'video1.mp4'
        video_path2 = Path(self.temp_input_dir) / 'video2.avi'
        
        # 标记一个成功，一个失败
        self.file_manager.mark_processed(video_path1, True, 100, 25, 'medium')
        self.file_manager.mark_processed(video_path2, False, 0, 5, 'medium', error='Test error')
        
        stats = self.file_manager.get_processing_stats()
        self.assertEqual(stats['total_processed'], 2)
        self.assertEqual(stats['successful'], 1)
        self.assertEqual(stats['failed'], 1)
        self.assertEqual(stats['total_duration'], 100)
        self.assertEqual(stats['total_processing_time'], 30)
    
    def test_validate_input_directory(self):
        """测试输入目录验证"""
        issues = self.file_manager.validate_input_directory()
        
        # 应该没有目录相关的问题（目录存在且可读）
        directory_issues = [i for i in issues if 'directory' in i.lower() and 'does not exist' in i]
        self.assertEqual(len(directory_issues), 0)
    
    def test_validate_output_directory(self):
        """测试输出目录验证"""
        issues = self.file_manager.validate_output_directory()
        
        # 应该没有输出目录问题
        self.assertEqual(len(issues), 0)
    
    def test_video_files_summary(self):
        """测试视频文件摘要"""
        summary = self.file_manager.get_video_files_summary()
        
        self.assertEqual(summary['total_files'], 3)
        self.assertIn('.mp4', summary['formats_found'])
        self.assertIn('.avi', summary['formats_found'])
        self.assertIn('.mov', summary['formats_found'])
        
        # 检查按扩展名分组
        self.assertEqual(summary['by_extension']['.mp4']['count'], 1)
        self.assertEqual(summary['by_extension']['.avi']['count'], 1)
        self.assertEqual(summary['by_extension']['.mov']['count'], 1)
    
    def test_cleanup_temp_files(self):
        """测试临时文件清理"""
        # 创建一些临时音频文件
        audio_temp_dir = self.file_manager.temp_dir / 'audio'
        audio_temp_dir.mkdir(exist_ok=True)
        
        temp_files = []
        for i in range(5):
            temp_file = audio_temp_dir / f'temp_audio_{i}.wav'
            temp_file.write_text(f"temp audio {i}")
            temp_files.append(temp_file)
        
        # 清理，保留2个最新的文件
        self.file_manager.cleanup_temp_files(keep_recent=2)
        
        # 检查剩余文件数量
        remaining_files = list(audio_temp_dir.glob('*.wav'))
        self.assertLessEqual(len(remaining_files), 2)


if __name__ == '__main__':
    unittest.main() 