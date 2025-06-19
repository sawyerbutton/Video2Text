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
        """Get video info using subprocess."""
        try:
            cmd = [
                self.ffmpeg_path, '-i', str(video_path),
                '-f', 'null', '-'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse stderr output for info
            stderr = result.stderr
            info = {'duration': 0, 'has_audio': False, 'has_video': False}
            
            # Extract duration
            duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})', stderr)
            if duration_match:
                hours, minutes, seconds, centiseconds = map(int, duration_match.groups())
                info['duration'] = hours * 3600 + minutes * 60 + seconds + centiseconds / 100
            
            # Check for audio/video streams
            info['has_audio'] = 'Audio:' in stderr
            info['has_video'] = 'Video:' in stderr
            
            # Extract audio info
            audio_match = re.search(r'Audio: (\w+).*?(\d+) Hz.*?(\d+) channels?', stderr)
            if audio_match:
                info['audio_codec'] = audio_match.group(1)
                info['audio_sample_rate'] = int(audio_match.group(2))
                info['audio_channels'] = int(audio_match.group(3))
            
            # Get file size
            try:
                info['size_bytes'] = video_path.stat().st_size
            except Exception:
                info['size_bytes'] = 0
            
            return info
            
        except Exception as e:
            print(f"Warning: Failed to get video info: {e}")
            return {'duration': 0, 'has_audio': False, 'has_video': False, 'size_bytes': 0}
    
    def extract_audio(self, video_path: Path, output_path: Optional[Path] = None, 
                     progress_callback: Optional[Callable[[float], None]] = None) -> Path:
        """
        Extract audio from video file with progress monitoring.
        
        Args:
            video_path: Path to input video file
            output_path: Path for output audio file (optional)
            progress_callback: Callback function for progress updates (0.0 to 1.0)
            
        Returns:
            Path to extracted audio file
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Generate output path if not provided
        if output_path is None:
            audio_filename = f"{video_path.stem}.{self.config['output_format']}"
            output_path = self.temp_dir / audio_filename
        
        # Get video info for progress calculation
        video_info = self.get_video_info(video_path)
        total_duration = video_info.get('duration', 0)
        
        if not video_info.get('has_audio', False):
            raise ValueError(f"No audio stream found in video: {video_path}")
        
        # Use appropriate extraction method
        if FFMPEG_PYTHON_AVAILABLE:
            return self._extract_audio_ffmpeg_python(
                video_path, output_path, total_duration, progress_callback
            )
        else:
            return self._extract_audio_subprocess(
                video_path, output_path, total_duration, progress_callback
            )
    
    def _extract_audio_ffmpeg_python(self, video_path: Path, output_path: Path,
                                   total_duration: float, 
                                   progress_callback: Optional[Callable[[float], None]]) -> Path:
        """Extract audio using ffmpeg-python library."""
        try:
            # Build ffmpeg stream
            stream = ffmpeg.input(str(video_path))
            
            # Audio processing options
            audio_options = {
                'acodec': 'pcm_s16le',  # Uncompressed PCM for best quality
                'ar': self.config['sample_rate'],
                'ac': self.config['channels']
            }
            
            # Apply audio filters if configured
            if self.config.get('normalize_audio', False):
                stream = ffmpeg.filter(stream, 'loudnorm')
            
            if self.config.get('remove_silence', False):
                stream = ffmpeg.filter(stream, 'silenceremove', 
                                     start_periods=1, start_duration=0.1, start_threshold=-50)
            
            # Output stream
            stream = ffmpeg.output(stream, str(output_path), **audio_options)
            
            # Run with progress monitoring
            if progress_callback and total_duration > 0:
                self._run_ffmpeg_with_progress(stream, total_duration, progress_callback)
            else:
                ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise RuntimeError("Audio extraction failed: output file is empty or missing")
            
            return output_path
            
        except Exception as e:
            # Cleanup failed output
            if output_path.exists():
                try:
                    output_path.unlink()
                except Exception:
                    pass
            raise RuntimeError(f"Audio extraction failed: {e}")
    
    def _extract_audio_subprocess(self, video_path: Path, output_path: Path,
                                total_duration: float,
                                progress_callback: Optional[Callable[[float], None]]) -> Path:
        """Extract audio using subprocess."""
        try:
            # Build FFmpeg command
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
            
            # Add progress monitoring if callback provided
            if progress_callback and total_duration > 0:
                cmd.insert(-1, '-progress')
                cmd.insert(-1, 'pipe:1')
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                self._monitor_ffmpeg_progress(process, total_duration, progress_callback)
            else:
                # Run without progress monitoring
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=3600  # 1 hour timeout
                )
                
                if result.returncode != 0:
                    raise RuntimeError(f"FFmpeg error: {result.stderr}")
            
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise RuntimeError("Audio extraction failed: output file is empty or missing")
            
            return output_path
            
        except Exception as e:
            # Cleanup failed output
            if output_path.exists():
                try:
                    output_path.unlink()
                except Exception:
                    pass
            raise RuntimeError(f"Audio extraction failed: {e}")
    
    def _run_ffmpeg_with_progress(self, stream, total_duration: float, 
                                progress_callback: Callable[[float], None]):
        """Run ffmpeg-python stream with progress monitoring."""
        try:
            process = ffmpeg.run_async(stream, pipe_stdout=True, pipe_stderr=True, overwrite_output=True)
            self._monitor_ffmpeg_progress(process, total_duration, progress_callback)
        except Exception as e:
            raise RuntimeError(f"FFmpeg execution failed: {e}")
    
    def _monitor_ffmpeg_progress(self, process, total_duration: float,
                               progress_callback: Callable[[float], None]):
        """Monitor FFmpeg process and call progress callback."""
        try:
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                
                line = line.strip()
                
                # Look for time progress
                if line.startswith('out_time_ms='):
                    try:
                        time_ms = int(line.split('=')[1])
                        current_seconds = time_ms / 1000000  # Convert microseconds to seconds
                        
                        if total_duration > 0:
                            progress = min(current_seconds / total_duration, 1.0)
                            progress_callback(progress)
                    except (ValueError, IndexError):
                        continue
                
                # Check for completion
                elif line.startswith('progress=end'):
                    progress_callback(1.0)
                    break
            
            # Wait for process to complete
            return_code = process.wait()
            
            if return_code != 0:
                stderr = process.stderr.read() if process.stderr else ""
                raise RuntimeError(f"FFmpeg failed with return code {return_code}: {stderr}")
                
        except Exception as e:
            # Terminate process if still running
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            
            raise RuntimeError(f"FFmpeg progress monitoring failed: {e}")
    
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