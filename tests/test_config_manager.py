#!/usr/bin/env python3
"""
测试配置管理模块
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """配置管理器测试类"""
    
    def setUp(self):
        """测试前设置"""
        self.config_manager = ConfigManager()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_default_config_initialization(self):
        """测试默认配置初始化"""
        self.assertIsNotNone(self.config_manager.processing_config)
        self.assertIsNotNone(self.config_manager.audio_config)
        self.assertIsNotNone(self.config_manager.logging_config)
    
    def test_whisper_models_info(self):
        """测试Whisper模型信息"""
        models = self.config_manager.list_available_models()
        self.assertIsInstance(models, list)
        self.assertIn('medium', models)
        self.assertIn('tiny', models)
        
        # 测试模型信息获取
        model_info = self.config_manager.get_model_info('medium')
        self.assertIsInstance(model_info, dict)
        self.assertIn('size', model_info)
    
    def test_supported_languages(self):
        """测试支持的语言列表"""
        languages = self.config_manager.list_supported_languages()
        self.assertIsInstance(languages, list)
        self.assertIn('auto', languages)
        self.assertIn('zh', languages)
        self.assertIn('en', languages)
    
    def test_device_resolution(self):
        """测试设备解析"""
        effective_device = self.config_manager.get_effective_device()
        self.assertIsInstance(effective_device, str)
        self.assertIn(effective_device, ['cpu', 'cuda', 'mps'])
    
    def test_config_validation(self):
        """测试配置验证"""
        # 设置有效的配置
        self.config_manager.processing_config.input_dir = str(self.temp_dir)
        self.config_manager.processing_config.output_dir = str(self.temp_dir)
        
        errors = self.config_manager.validate_config()
        # 可能会有FFmpeg相关的错误，但不应该有目录相关的错误
        directory_errors = [e for e in errors if 'directory' in e.lower()]
        self.assertEqual(len(directory_errors), 0)
    
    def test_config_file_save_load(self):
        """测试配置文件保存和加载"""
        config_file = Path(self.temp_dir) / 'test_config.ini'
        
        # 修改一些配置
        self.config_manager.processing_config.model_name = 'large'
        self.config_manager.processing_config.language = 'zh'
        
        # 保存配置
        self.config_manager.save_config(str(config_file))
        self.assertTrue(config_file.exists())
        
        # 创建新的配置管理器并加载配置
        new_config_manager = ConfigManager(config_file=str(config_file))
        self.assertEqual(new_config_manager.processing_config.model_name, 'large')
        self.assertEqual(new_config_manager.processing_config.language, 'zh')
    
    def test_command_line_args_update(self):
        """测试命令行参数更新"""
        # 模拟命令行参数
        class MockArgs:
            def __init__(self):
                self.input = '/test/input'
                self.output = '/test/output'
                self.model = 'small'
                self.language = 'en'
                self.workers = 2
                self.verbose = True
        
        args = MockArgs()
        self.config_manager.update_from_args(args)
        
        self.assertEqual(self.config_manager.processing_config.model_name, 'small')
        self.assertEqual(self.config_manager.processing_config.language, 'en')
        self.assertEqual(self.config_manager.processing_config.max_workers, 2)
        self.assertEqual(self.config_manager.processing_config.verbose, True)
    
    def test_invalid_model_validation(self):
        """测试无效模型验证"""
        with self.assertRaises(ValueError):
            # 模拟无效模型的命令行参数
            class MockArgsInvalid:
                def __init__(self):
                    self.model = 'invalid_model'
            
            args = MockArgsInvalid()
            self.config_manager.update_from_args(args)
    
    def test_invalid_language_validation(self):
        """测试无效语言验证"""
        with self.assertRaises(ValueError):
            # 模拟无效语言的命令行参数
            class MockArgsInvalid:
                def __init__(self):
                    self.language = 'invalid_language'
            
            args = MockArgsInvalid()
            self.config_manager.update_from_args(args)


if __name__ == '__main__':
    unittest.main() 