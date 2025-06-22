"""
Audio processor for MP4ToText tool.
Handles cross-platform audio extraction using FFmpeg with progress monitoring.
"""

import os
import subprocess
import time
import re
from pathlib import Path
from typing import Optional, Callable, Dict, Any, Tuple
from dataclasses import dataclass

try:
    import ffmpeg
    FFMPEG_PYTHON_AVAILABLE = True
except ImportError:
    FFMPEG_PYTHON_AVAILABLE = False

from .platform_utils import PlatformUtils


@dataclass
class AudioInfo:
    """Audio file information."""
    duration: float = 0.0
    sample_rate: int = 0
    channels: int = 0
    format: str = ""
    bitrate: int = 0
    size_bytes: int = 0


class AudioProcessor:
    """Cross-platform audio processor using FFmpeg."""
    
    def __init__(self, temp_dir: str, audio_config: Optional[Dict] = None):
        self.platform_utils = PlatformUtils()
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Audio processing configuration
        self.config = {
            'output_format': 'wav',
            'sample_rate': 16000,  # Whisper optimal sample rate
            'channels': 1,         # Mono for Whisper
            'quality': 'high',
            'normalize_audio': False,
            'remove_silence': False
        }
        
        if audio_config:
            self.config.update(audio_config)
            
        # Find FFmpeg executable
        self.ffmpeg_path = self._find_ffmpeg()
        if not self.ffmpeg_path:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg to process video files.")
    
    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFmpeg executable on current platform."""
        possible_names = ['ffmpeg', 'ffmpeg.exe'] if self.platform_utils.is_windows else ['ffmpeg']
        
        # Check if ffmpeg is in PATH
        for name in possible_names:
            try:
                result = subprocess.run(
                    [name, '-version'], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                if result.returncode == 0:
                    return name
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        # Check common installation paths
        if self.platform_utils.is_windows:
            common_paths = [
                r'C:\ffmpeg\bin\ffmpeg.exe',
                r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
                r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe'
            ]
        elif self.platform_utils.is_macos:
            common_paths = [
                '/usr/local/bin/ffmpeg',
                '/opt/homebrew/bin/ffmpeg',
                '/usr/bin/ffmpeg'
            ]
        else:  # Linux
            common_paths = [
                '/usr/bin/ffmpeg',
                '/usr/local/bin/ffmpeg',
                '/snap/bin/ffmpeg'
            ]
        
        for path in common_paths:
            if Path(path).exists():
                return path
                
        return None
    
    def get_video_info(self, video_path: Path) -> Dict[str, Any]:
        """
        Get comprehensive information about a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary containing video information
        """
        if FFMPEG_PYTHON_AVAILABLE:
            return self._get_video_info_ffmpeg_python(video_path)
        else:
            return self._get_video_info_subprocess(video_path)
    
    def _get_video_info_ffmpeg_python(self, video_path: Path) -> Dict[str, Any]:
        """Get video info using ffmpeg-python library."""
        try:
            probe = ffmpeg.probe(str(video_path))
            
            # Find video and audio streams
            video_stream = None
            audio_stream = None
            
            for stream in probe['streams']:
                if stream['codec_type'] == 'video' and not video_stream:
                    video_stream = stream
                elif stream['codec_type'] == 'audio' and not audio_stream:
                    audio_stream = stream
            
            # Extract information
            info = {
                'duration': float(probe['format'].get('duration', 0)),
                'size_bytes': int(probe['format'].get('size', 0)),
                'format_name': probe['format'].get('format_name', ''),
                'has_video': video_stream is not None,
                'has_audio': audio_stream is not None
            }
            
            if video_stream:
                info.update({
                    'video_codec': video_stream.get('codec_name', ''),
                    'width': int(video_stream.get('width', 0)),
                    'height': int(video_stream.get('height', 0)),
                    'fps': eval(video_stream.get('r_frame_rate', '0/1'))
                })
            
            if audio_stream:
                info.update({
                    'audio_codec': audio_stream.get('codec_name', ''),
                    'audio_sample_rate': int(audio_stream.get('sample_rate', 0)),
                    'audio_channels': int(audio_stream.get('channels', 0)),
                    'audio_bitrate': int(audio_stream.get('bit_rate', 0))
                })
            
            return info
            
        except Exception as e:
            print(f"Warning: Failed to get video info using ffmpeg-python: {e}")
            return self._get_video_info_subprocess(video_path)
    
    def _get_video_info_subprocess(self, video_path: Path) -> Dict[str, Any]:
        """Get video info using subprocess and ffprobe."""
        try:
            # Determine ffprobe path
            if self.ffmpeg_path:
                ffprobe_path = self.ffmpeg_path.replace('ffmpeg', 'ffprobe')
            else:
                ffprobe_path = 'ffprobe'  # Hope it's in PATH
                
            cmd = [
                ffprobe_path,
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(video_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=30
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"ffprobe error: {result.stderr}")
            
            import json
            probe_data = json.loads(result.stdout)
            
            # Extract relevant information
            info = {
                'duration': 0.0,
                'has_video': False,
                'has_audio': False,
                'video_codec': '',
                'audio_codec': '',
                'width': 0,
                'height': 0,
                'fps': 0.0,
                'bitrate': 0
            }
            
            # Parse format info
            if 'format' in probe_data:
                format_info = probe_data['format']
                info['duration'] = float(format_info.get('duration', 0))
                info['bitrate'] = int(format_info.get('bit_rate', 0))
            
            # Parse streams
            if 'streams' in probe_data:
                for stream in probe_data['streams']:
                    codec_type = stream.get('codec_type', '')
                    
                    if codec_type == 'video':
                        info['has_video'] = True
                        info['video_codec'] = stream.get('codec_name', '')
                        info['width'] = int(stream.get('width', 0))
                        info['height'] = int(stream.get('height', 0))
                        
                        # Calculate FPS
                        r_frame_rate = stream.get('r_frame_rate', '0/1')
                        if '/' in r_frame_rate:
                            num, den = r_frame_rate.split('/')
                            if int(den) > 0:
                                info['fps'] = float(num) / float(den)
                    
                    elif codec_type == 'audio':
                        info['has_audio'] = True
                        info['audio_codec'] = stream.get('codec_name', '')
            
            return info
            
        except Exception as e:
            # Return basic info on error
            print(f"Warning: Failed to get video info: {e}")
            return {
                'duration': 0.0,
                'has_video': False,
                'has_audio': False,
                'video_codec': '',
                'audio_codec': '',
                'width': 0,
                'height': 0,
                'fps': 0.0,
                'bitrate': 0
            }
    
    def extract_audio(self, video_path: Path, output_path: Optional[Path] = None, 
                     progress_callback: Optional[Callable[[float], None]] = None) -> Path:
        """
        Extract audio from video file with optional progress monitoring.
        
        Args:
            video_path: Path to input video file
            output_path: Path for output audio file (optional)
            progress_callback: Callback function for progress updates (optional)
            
        Returns:
            Path to extracted audio file
        """
        if output_path is None:
            # Generate output filename based on input
            output_path = self.temp_dir / f"{video_path.stem}.wav"
        
        # 使用最简单直接的方法
        cmd = [
            self.ffmpeg_path,
            '-i', str(video_path),
            '-vn',  # No video
            '-acodec', 'pcm_s16le',
            '-ar', str(self.config['sample_rate']),
            '-ac', str(self.config['channels']),
            '-y',   # Overwrite output
            str(output_path)
        ]
        
        print(f"🎵 提取音频: {video_path.name}")
        start_time = time.time()
        
        try:
            # 简单直接运行，不搞复杂的进度监控
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg error: {result.stderr}")
            
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise RuntimeError("Audio extraction failed: output file is empty or missing")
            
            print(f"✅ 音频提取完成 (用时: {duration:.1f}秒)")
            
            # 如果有进度回调，直接调用100%
            if progress_callback:
                progress_callback(1.0)
            
            return output_path
            
        except Exception as e:
            # Cleanup failed output
            if output_path.exists():
                try:
                    output_path.unlink()
                except Exception:
                    pass
            raise RuntimeError(f"Audio extraction failed: {e}")
    
    def get_audio_info(self, audio_path: Path) -> AudioInfo:
        """Get information about an audio file."""
        try:
            if FFMPEG_PYTHON_AVAILABLE:
                probe = ffmpeg.probe(str(audio_path))
                
                audio_stream = None
                for stream in probe['streams']:
                    if stream['codec_type'] == 'audio':
                        audio_stream = stream
                        break
                
                if audio_stream:
                    return AudioInfo(
                        duration=float(probe['format'].get('duration', 0)),
                        sample_rate=int(audio_stream.get('sample_rate', 0)),
                        channels=int(audio_stream.get('channels', 0)),
                        format=audio_stream.get('codec_name', ''),
                        bitrate=int(audio_stream.get('bit_rate', 0)),
                        size_bytes=int(probe['format'].get('size', 0))
                    )
            
            # Fallback to basic file info
            return AudioInfo(
                size_bytes=audio_path.stat().st_size if audio_path.exists() else 0
            )
            
        except Exception:
            return AudioInfo()
    
    def cleanup_temp_audio(self, audio_path: Path):
        """Clean up temporary audio file."""
        try:
            if audio_path.exists() and audio_path.parent == self.temp_dir:
                audio_path.unlink()
        except Exception as e:
            print(f"Warning: Failed to cleanup temp audio file {audio_path}: {e}")
    
    def validate_video_file(self, video_path: Path) -> Tuple[bool, str]:
        """
        Validate if a video file can be processed.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not video_path.exists():
            return False, f"File does not exist: {video_path}"
        
        if not video_path.is_file():
            return False, f"Path is not a file: {video_path}"
        
        if video_path.stat().st_size == 0:
            return False, f"File is empty: {video_path}"
        
        # Check video info
        try:
            video_info = self.get_video_info(video_path)
            
            if not video_info.get('has_audio', False):
                return False, "No audio stream found in video file"
            
            if video_info.get('duration', 0) <= 0:
                return False, "Video duration is zero or unknown"
            
            return True, ""
            
        except Exception as e:
            return False, f"Failed to analyze video file: {e}"


if __name__ == "__main__":
    # Test audio processor
    import sys
    
    if len(sys.argv) >= 2:
        video_file = Path(sys.argv[1])
        temp_dir = Path.cwd() / 'temp' / 'audio'
        
        processor = AudioProcessor(str(temp_dir))
        
        print(f"Testing audio processor with: {video_file}")
        
        # Validate video
        is_valid, error = processor.validate_video_file(video_file)
        if not is_valid:
            print(f"Validation failed: {error}")
            sys.exit(1)
        
        # Get video info
        info = processor.get_video_info(video_file)
        print(f"Video info: {info}")
        
        # Extract audio with progress
        def progress_callback(progress):
            print(f"\rExtracting audio: {progress*100:.1f}%", end='', flush=True)
        
        try:
            audio_path = processor.extract_audio(video_file, progress_callback=progress_callback)
            print(f"\nAudio extracted to: {audio_path}")
            
            # Get audio info
            audio_info = processor.get_audio_info(audio_path)
            print(f"Audio info: {audio_info}")
            
        except Exception as e:
            print(f"\nError: {e}")
    else:
        print("Usage: python audio_processor.py <video_file>") 