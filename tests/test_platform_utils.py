#!/usr/bin/env python3
"""
测试平台工具模块
"""

import unittest
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.platform_utils import PlatformUtils


class TestPlatformUtils(unittest.TestCase):
    """平台工具测试类"""
    
    def setUp(self):
        """测试前设置"""
        self.platform_utils = PlatformUtils()
    
    def test_system_detection(self):
        """测试系统检测"""
        self.assertIsInstance(self.platform_utils.system, str)
        self.assertIn(self.platform_utils.system, ['windows', 'darwin', 'linux'])
    
    def test_device_detection(self):
        """测试设备检测"""
        device, device_info = self.platform_utils.detect_device()
        self.assertIsInstance(device, str)
        self.assertIn(device, ['cpu', 'cuda', 'mps'])
        self.assertIsInstance(device_info, dict)
        self.assertIn('torch_available', device_info)
    
    def test_ffmpeg_check(self):
        """测试FFmpeg检查"""
        available, version = self.platform_utils.check_ffmpeg()
        self.assertIsInstance(available, bool)
        if available:
            self.assertIsInstance(version, str)
            self.assertIn('ffmpeg', version.lower())
    
    def test_temp_dir_creation(self):
        """测试临时目录创建"""
        temp_dir = self.platform_utils.get_temp_dir()
        self.assertIsInstance(temp_dir, Path)
        self.assertTrue(temp_dir.exists())
        self.assertTrue(temp_dir.is_dir())
    
    def test_path_normalization(self):
        """测试路径标准化"""
        test_path = "~/test_path"
        normalized = self.platform_utils.normalize_path(test_path)
        self.assertIsInstance(normalized, Path)
        self.assertFalse(str(normalized).startswith('~'))
    
    def test_memory_check(self):
        """测试内存检查"""
        memory = self.platform_utils.check_available_memory()
        if memory is not None:
            self.assertIsInstance(memory, float)
            self.assertGreater(memory, 0)
    
    def test_workers_recommendation(self):
        """测试工作线程推荐"""
        workers = self.platform_utils.get_recommended_workers()
        self.assertIsInstance(workers, int)
        self.assertGreaterEqual(workers, 1)
        self.assertLessEqual(workers, 4)
    
    def test_model_memory_estimation(self):
        """测试模型内存估算"""
        for model in ['tiny', 'base', 'medium', 'large']:
            memory = self.platform_utils.estimate_model_memory_usage(model)
            self.assertIsInstance(memory, float)
            self.assertGreater(memory, 0)
    
    def test_whisper_cache_dir(self):
        """测试Whisper缓存目录"""
        cache_dir = self.platform_utils.get_whisper_model_cache_dir()
        self.assertIsInstance(cache_dir, Path)
        self.assertTrue(cache_dir.exists())
        self.assertTrue(cache_dir.is_dir())


if __name__ == '__main__':
    unittest.main() 