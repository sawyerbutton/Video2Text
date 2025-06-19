"""
Platform utilities for cross-platform support and device detection.
Handles Windows, macOS, and Linux compatibility, plus GPU/CPU detection.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import colorama
    colorama.init()  # Initialize colorama for Windows
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


class PlatformUtils:
    """Cross-platform utilities for system detection and path handling."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == 'windows'
        self.is_macos = self.system == 'darwin'
        self.is_linux = self.system == 'linux'
        
    def get_system_info(self) -> Dict[str, str]:
        """Get comprehensive system information."""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': sys.version,
            'architecture': platform.architecture()[0]
        }
    
    def detect_device(self) -> Tuple[str, Dict[str, any]]:
        """
        Detect the best device for Whisper processing.
        Returns: (device_name, device_info)
        """
        device_info = {
            'torch_available': TORCH_AVAILABLE,
            'cuda_available': False,
            'mps_available': False,
            'device_name': 'cpu',
            'gpu_count': 0,
            'gpu_memory': 0
        }
        
        if not TORCH_AVAILABLE:
            return 'cpu', device_info
            
        # Check CUDA (NVIDIA GPU)
        if torch.cuda.is_available():
            device_info.update({
                'cuda_available': True,
                'device_name': 'cuda',
                'gpu_count': torch.cuda.device_count(),
                'gpu_memory': torch.cuda.get_device_properties(0).total_memory if torch.cuda.device_count() > 0 else 0
            })
            return 'cuda', device_info
            
        # Check MPS (Apple Silicon GPU)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device_info.update({
                'mps_available': True,
                'device_name': 'mps'
            })
            return 'mps', device_info
            
        return 'cpu', device_info
    
    def check_ffmpeg(self) -> Tuple[bool, Optional[str]]:
        """Check if FFmpeg is available and get version."""
        try:
            if self.is_windows:
                # Windows might have ffmpeg.exe
                cmd = ['ffmpeg.exe', '-version']
            else:
                cmd = ['ffmpeg', '-version']
                
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                # Extract version from output
                first_line = result.stdout.split('\n')[0]
                return True, first_line
            else:
                return False, None
                
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False, None
    
    def get_temp_dir(self) -> Path:
        """Get platform-appropriate temporary directory."""
        if self.is_windows:
            temp_base = Path(os.environ.get('TEMP', 'C:/temp'))
        else:
            temp_base = Path(os.environ.get('TMPDIR', '/tmp'))
            
        # Create app-specific temp directory
        app_temp = temp_base / 'mp4_to_text'
        app_temp.mkdir(exist_ok=True, parents=True)
        return app_temp
    
    def normalize_path(self, path: str) -> Path:
        """Normalize path for current platform."""
        path_obj = Path(path)
        
        # Expand user directory (~)
        if str(path_obj).startswith('~'):
            path_obj = path_obj.expanduser()
            
        # Resolve relative paths
        path_obj = path_obj.resolve()
        
        return path_obj
    
    def get_executable_extension(self) -> str:
        """Get executable extension for current platform."""
        return '.exe' if self.is_windows else ''
    
    def supports_colors(self) -> bool:
        """Check if terminal supports colored output."""
        if COLORAMA_AVAILABLE:
            return True
            
        # Check environment variables
        if self.is_windows:
            return os.environ.get('ANSICON') is not None
        else:
            term = os.environ.get('TERM', '')
            return 'color' in term or term in ['xterm', 'xterm-256color', 'screen']
    
    def get_whisper_model_cache_dir(self) -> Path:
        """Get Whisper model cache directory for current platform."""
        if self.is_windows:
            cache_dir = Path.home() / 'AppData' / 'Local' / 'whisper'
        elif self.is_macos:
            cache_dir = Path.home() / 'Library' / 'Caches' / 'whisper'
        else:  # Linux
            cache_dir = Path.home() / '.cache' / 'whisper'
            
        cache_dir.mkdir(exist_ok=True, parents=True)
        return cache_dir
    
    def get_recommended_workers(self) -> int:
        """Get recommended number of workers based on system resources."""
        try:
            cpu_count = os.cpu_count() or 1
            
            # Get available memory (if psutil is available)
            try:
                import psutil
                memory_gb = psutil.virtual_memory().total / (1024**3)
                
                # Conservative approach: 1 worker per 4GB RAM, max CPU count
                memory_workers = max(1, int(memory_gb // 4))
                return min(cpu_count, memory_workers, 4)  # Cap at 4 workers
                
            except ImportError:
                # Fallback: use CPU count with conservative limit
                return min(cpu_count // 2, 2) if cpu_count > 2 else 1
                
        except Exception:
            return 1  # Safe fallback
    
    def estimate_model_memory_usage(self, model_name: str) -> float:
        """Estimate memory usage for Whisper model in GB."""
        model_sizes = {
            'tiny': 1.0,
            'base': 2.0,
            'small': 3.0,
            'medium': 5.0,
            'large': 8.0,
            'large-v2': 8.0,
            'large-v3': 10.0
        }
        return model_sizes.get(model_name, 5.0)  # Default to medium
    
    def check_available_memory(self) -> Optional[float]:
        """Check available system memory in GB."""
        try:
            import psutil
            return psutil.virtual_memory().available / (1024**3)
        except ImportError:
            return None
    
    def print_system_info(self):
        """Print comprehensive system information."""
        print("=== System Information ===")
        info = self.get_system_info()
        for key, value in info.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
            
        print("\n=== Device Information ===")
        device, device_info = self.detect_device()
        print(f"Recommended device: {device}")
        for key, value in device_info.items():
            if isinstance(value, bool):
                status = "✓" if value else "✗"
                print(f"{key.replace('_', ' ').title()}: {status}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
                
        print("\n=== FFmpeg Status ===")
        ffmpeg_available, ffmpeg_version = self.check_ffmpeg()
        if ffmpeg_available:
            print(f"FFmpeg: ✓ Available")
            print(f"Version: {ffmpeg_version}")
        else:
            print("FFmpeg: ✗ Not found")
            
        memory = self.check_available_memory()
        if memory:
            print(f"\nAvailable Memory: {memory:.1f} GB")


# Convenience function for quick device detection
def get_device():
    """Quick function to get the best available device."""
    utils = PlatformUtils()
    device, _ = utils.detect_device()
    return device


if __name__ == "__main__":
    # Test the platform utilities
    utils = PlatformUtils()
    utils.print_system_info() 