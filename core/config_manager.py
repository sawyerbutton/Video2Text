"""
Configuration manager for MP4ToText tool.
Handles cross-platform configuration loading and device-specific settings.
"""

import os
import json
from configparser import ConfigParser
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from .platform_utils import PlatformUtils


@dataclass
class ProcessingConfig:
    """Processing configuration data class."""
    input_dir: str = ""
    output_dir: str = ""
    model_name: str = "medium"
    language: str = "auto"
    device: str = "auto"
    max_workers: int = 1
    skip_existing: bool = False
    cleanup_temp: bool = True
    verbose: bool = False
    quiet: bool = False


@dataclass
class AudioConfig:
    """Audio processing configuration."""
    format: str = "wav"
    sample_rate: int = 16000
    channels: int = 1
    quality: str = "high"


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    file: Optional[str] = None
    max_size: int = 10485760  # 10MB
    backup_count: int = 5
    console_output: bool = True


class ConfigManager:
    """Manages configuration for MP4ToText with cross-platform support."""
    
    WHISPER_MODELS = {
        'tiny': {
            'size': '39MB',
            'memory_required': '1GB',
            'speed': 'very_fast',
            'accuracy': 'low',
            'recommended_for': '快速测试'
        },
        'base': {
            'size': '142MB', 
            'memory_required': '2GB',
            'speed': 'fast',
            'accuracy': 'medium',
            'recommended_for': '日常使用'
        },
        'small': {
            'size': '244MB',
            'memory_required': '3GB',
            'speed': 'medium',
            'accuracy': 'good',
            'recommended_for': '平衡选择'
        },
        'medium': {
            'size': '769MB',
            'memory_required': '5GB',
            'speed': 'medium', 
            'accuracy': 'high',
            'recommended_for': '推荐使用',
            'default': True
        },
        'large': {
            'size': '1550MB',
            'memory_required': '8GB',
            'speed': 'slow',
            'accuracy': 'very_high',
            'recommended_for': '高质量转录'
        },
        'large-v2': {
            'size': '1550MB',
            'memory_required': '8GB',
            'speed': 'slow',
            'accuracy': 'very_high',
            'recommended_for': '改进版大模型'
        },
        'large-v3': {
            'size': '1550MB',
            'memory_required': '10GB',
            'speed': 'slow',
            'accuracy': 'very_high',
            'recommended_for': '最新版本'
        }
    }
    
    SUPPORTED_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.webm', '.m4v']
    
    SUPPORTED_LANGUAGES = {
        'auto': '自动检测',
        'zh': '中文',
        'en': '英文',
        'ja': '日文',
        'ko': '韩文',
        'fr': '法文',
        'de': '德文',
        'es': '西班牙文',
        'ru': '俄文',
        'pt': '葡萄牙文',
        'it': '意大利文',
        'ar': '阿拉伯文',
        'hi': '印地文'
    }
    
    def __init__(self, config_file: Optional[str] = None):
        self.platform_utils = PlatformUtils()
        self.config_file = self._resolve_config_file(config_file)
        self.config = ConfigParser()
        
        # Initialize default configurations
        self.processing_config = ProcessingConfig()
        self.audio_config = AudioConfig()
        self.logging_config = LoggingConfig()
        
        # Load configuration
        self._load_default_config()
        if self.config_file and self.config_file.exists():
            self._load_config_file()
    
    def _resolve_config_file(self, config_file: Optional[str]) -> Optional[Path]:
        """Resolve configuration file path."""
        if config_file:
            return self.platform_utils.normalize_path(config_file)
        
        # Look for default config files
        possible_configs = [
            Path.cwd() / 'config' / 'config.ini',
            Path.cwd() / 'config.ini',
            Path.home() / '.mp4_to_text' / 'config.ini'
        ]
        
        for config_path in possible_configs:
            if config_path.exists():
                return config_path
                
        return None
    
    def _load_default_config(self):
        """Load default configuration values."""
        # Detect best device automatically
        device, device_info = self.platform_utils.detect_device()
        
        # Adjust default model based on available memory
        default_model = self._get_recommended_model(device_info)
        
        # Set device-specific defaults
        self.processing_config.device = device
        self.processing_config.model_name = default_model
        self.processing_config.max_workers = self.platform_utils.get_recommended_workers()
        
        # Set logging file path
        log_dir = Path.cwd() / 'logs'
        log_dir.mkdir(exist_ok=True)
        self.logging_config.file = str(log_dir / 'mp4_to_text.log')
    
    def _get_recommended_model(self, device_info: Dict[str, Any]) -> str:
        """Get recommended Whisper model based on available resources."""
        available_memory = self.platform_utils.check_available_memory()
        
        if available_memory is None:
            return 'medium'  # Safe default
            
        # Recommend model based on memory
        if available_memory >= 12:
            return 'large-v3'
        elif available_memory >= 8:
            return 'large'
        elif available_memory >= 5:
            return 'medium'
        elif available_memory >= 3:
            return 'small'
        elif available_memory >= 2:
            return 'base'
        else:
            return 'tiny'
    
    def _load_config_file(self):
        """Load configuration from file."""
        try:
            self.config.read(self.config_file)
            
            # Load processing config
            if self.config.has_section('PROCESSING'):
                section = self.config['PROCESSING']
                self.processing_config.model_name = section.get('model_name', self.processing_config.model_name)
                self.processing_config.language = section.get('language', self.processing_config.language)
                self.processing_config.max_workers = section.getint('max_workers', self.processing_config.max_workers)
                self.processing_config.skip_existing = section.getboolean('skip_existing', self.processing_config.skip_existing)
                self.processing_config.cleanup_temp = section.getboolean('cleanup_temp', self.processing_config.cleanup_temp)
                
                # Override device if specified in config
                config_device = section.get('device', 'auto')
                if config_device != 'auto':
                    self.processing_config.device = config_device
            
            # Load audio config
            if self.config.has_section('AUDIO'):
                section = self.config['AUDIO']
                self.audio_config.format = section.get('format', self.audio_config.format)
                self.audio_config.sample_rate = section.getint('sample_rate', self.audio_config.sample_rate)
                self.audio_config.channels = section.getint('channels', self.audio_config.channels)
                self.audio_config.quality = section.get('quality', self.audio_config.quality)
            
            # Load logging config
            if self.config.has_section('LOGGING'):
                section = self.config['LOGGING']
                self.logging_config.level = section.get('level', self.logging_config.level)
                self.logging_config.max_size = section.getint('max_size', self.logging_config.max_size)
                self.logging_config.backup_count = section.getint('backup_count', self.logging_config.backup_count)
                self.logging_config.console_output = section.getboolean('console_output', self.logging_config.console_output)
                
                # Override log file if specified
                config_log_file = section.get('file')
                if config_log_file:
                    self.logging_config.file = str(self.platform_utils.normalize_path(config_log_file))
                    
        except Exception as e:
            print(f"Warning: Failed to load config file {self.config_file}: {e}")
            print("Using default configuration.")
    
    def update_from_args(self, args):
        """Update configuration from command line arguments."""
        if hasattr(args, 'input') and args.input:
            self.processing_config.input_dir = str(self.platform_utils.normalize_path(args.input))
            
        if hasattr(args, 'output') and args.output:
            self.processing_config.output_dir = str(self.platform_utils.normalize_path(args.output))
            
        if hasattr(args, 'model') and args.model:
            if args.model in self.WHISPER_MODELS:
                self.processing_config.model_name = args.model
            else:
                raise ValueError(f"Unsupported model: {args.model}. Supported models: {list(self.WHISPER_MODELS.keys())}")
                
        if hasattr(args, 'language') and args.language:
            if args.language in self.SUPPORTED_LANGUAGES:
                self.processing_config.language = args.language
            else:
                raise ValueError(f"Unsupported language: {args.language}. Supported languages: {list(self.SUPPORTED_LANGUAGES.keys())}")
                
        if hasattr(args, 'device') and args.device:
            self.processing_config.device = args.device
            
        if hasattr(args, 'workers') and args.workers:
            self.processing_config.max_workers = args.workers
            
        if hasattr(args, 'skip_existing') and args.skip_existing:
            self.processing_config.skip_existing = args.skip_existing
            
        if hasattr(args, 'verbose') and args.verbose:
            self.processing_config.verbose = args.verbose
            self.logging_config.level = 'DEBUG'
            
        if hasattr(args, 'quiet') and args.quiet:
            self.processing_config.quiet = args.quiet
            self.logging_config.console_output = False
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Validate input directory
        if not self.processing_config.input_dir:
            errors.append("Input directory not specified")
        elif not Path(self.processing_config.input_dir).exists():
            errors.append(f"Input directory does not exist: {self.processing_config.input_dir}")
        elif not Path(self.processing_config.input_dir).is_dir():
            errors.append(f"Input path is not a directory: {self.processing_config.input_dir}")
            
        # Validate output directory
        if not self.processing_config.output_dir:
            errors.append("Output directory not specified")
        else:
            output_path = Path(self.processing_config.output_dir)
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create output directory: {e}")
        
        # Validate model
        if self.processing_config.model_name not in self.WHISPER_MODELS:
            errors.append(f"Invalid model: {self.processing_config.model_name}")
            
        # Validate device
        available_device, _ = self.platform_utils.detect_device()
        if self.processing_config.device not in ['auto', 'cpu', 'cuda', 'mps', available_device]:
            errors.append(f"Device '{self.processing_config.device}' not available. Available: {available_device}")
            
        # Check memory requirements
        available_memory = self.platform_utils.check_available_memory()
        if available_memory:
            required_memory = self.platform_utils.estimate_model_memory_usage(self.processing_config.model_name)
            if available_memory < required_memory:
                errors.append(f"Insufficient memory for model '{self.processing_config.model_name}'. "
                            f"Required: {required_memory}GB, Available: {available_memory:.1f}GB")
        
        # Validate FFmpeg
        ffmpeg_available, _ = self.platform_utils.check_ffmpeg()
        if not ffmpeg_available:
            errors.append("FFmpeg not found. Please install FFmpeg to process video files.")
            
        return errors
    
    def save_config(self, config_file: Optional[str] = None):
        """Save current configuration to file."""
        save_path = Path(config_file) if config_file else self.config_file
        if not save_path:
            save_path = Path.cwd() / 'config' / 'config.ini'
            
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create config object
        config = ConfigParser()
        
        # Add processing section
        config.add_section('PROCESSING')
        config.set('PROCESSING', 'model_name', self.processing_config.model_name)
        config.set('PROCESSING', 'language', self.processing_config.language)
        config.set('PROCESSING', 'device', self.processing_config.device)
        config.set('PROCESSING', 'max_workers', str(self.processing_config.max_workers))
        config.set('PROCESSING', 'skip_existing', str(self.processing_config.skip_existing))
        config.set('PROCESSING', 'cleanup_temp', str(self.processing_config.cleanup_temp))
        
        # Add audio section
        config.add_section('AUDIO')
        config.set('AUDIO', 'format', self.audio_config.format)
        config.set('AUDIO', 'sample_rate', str(self.audio_config.sample_rate))
        config.set('AUDIO', 'channels', str(self.audio_config.channels))
        config.set('AUDIO', 'quality', self.audio_config.quality)
        
        # Add logging section
        config.add_section('LOGGING')
        config.set('LOGGING', 'level', self.logging_config.level)
        config.set('LOGGING', 'max_size', str(self.logging_config.max_size))
        config.set('LOGGING', 'backup_count', str(self.logging_config.backup_count))
        config.set('LOGGING', 'console_output', str(self.logging_config.console_output))
        if self.logging_config.file:
            config.set('LOGGING', 'file', self.logging_config.file)
        
        # Write to file
        with open(save_path, 'w', encoding='utf-8') as f:
            config.write(f)
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a Whisper model."""
        return self.WHISPER_MODELS.get(model_name, {})
    
    def list_available_models(self) -> List[str]:
        """Get list of available Whisper models."""
        return list(self.WHISPER_MODELS.keys())
    
    def list_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self.SUPPORTED_LANGUAGES.keys())
    
    def get_effective_device(self) -> str:
        """Get the effective device to use (resolving 'auto')."""
        if self.processing_config.device == 'auto':
            device, _ = self.platform_utils.detect_device()
            return device
        return self.processing_config.device
    
    def print_config_summary(self):
        """Print a summary of current configuration."""
        print("=== Configuration Summary ===")
        print(f"Model: {self.processing_config.model_name}")
        print(f"Device: {self.get_effective_device()}")
        print(f"Language: {self.processing_config.language}")
        print(f"Max Workers: {self.processing_config.max_workers}")
        print(f"Input Directory: {self.processing_config.input_dir}")
        print(f"Output Directory: {self.processing_config.output_dir}")
        print(f"Skip Existing: {self.processing_config.skip_existing}")
        print(f"Audio Format: {self.audio_config.format}")
        print(f"Sample Rate: {self.audio_config.sample_rate}")
        print(f"Log Level: {self.logging_config.level}")
        
        # Show model info
        model_info = self.get_model_info(self.processing_config.model_name)
        if model_info:
            print(f"\nModel Details:")
            print(f"  Size: {model_info.get('size', 'Unknown')}")
            print(f"  Memory Required: {model_info.get('memory_required', 'Unknown')}")
            print(f"  Speed: {model_info.get('speed', 'Unknown')}")
            print(f"  Accuracy: {model_info.get('accuracy', 'Unknown')}")


if __name__ == "__main__":
    # Test configuration manager
    config_manager = ConfigManager()
    config_manager.print_config_summary()
    
    errors = config_manager.validate_config()
    if errors:
        print("\nValidation Errors:")
        for error in errors:
            print(f"  - {error}") 