"""
MP4ToText - Video to Text Transcription Tool
Core processing modules for cross-platform video transcription.
"""

__version__ = "1.0.0"
__author__ = "Video2Text Team"

from .config_manager import ConfigManager
from .file_manager import FileManager
from .audio_processor import AudioProcessor
from .transcriber import WhisperTranscriber
from .platform_utils import PlatformUtils

__all__ = [
    'ConfigManager',
    'FileManager', 
    'AudioProcessor',
    'WhisperTranscriber',
    'PlatformUtils'
] 