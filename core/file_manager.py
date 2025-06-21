"""
File manager for MP4ToText tool.
Handles cross-platform file operations, path management, and video file processing.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Iterator, Set
from datetime import datetime

try:
    from pathvalidate import validate_filename, sanitize_filename
    PATHVALIDATE_AVAILABLE = True
except ImportError:
    PATHVALIDATE_AVAILABLE = False

from .platform_utils import PlatformUtils


class FileManager:
    """Cross-platform file manager for video processing."""
    
    def __init__(self, input_dir: str, output_dir: str, temp_dir: Optional[str] = None):
        self.platform_utils = PlatformUtils()
        
        # Normalize paths
        self.input_dir = self.platform_utils.normalize_path(input_dir)
        self.output_dir = self.platform_utils.normalize_path(output_dir)
        
        # Set temp directory
        if temp_dir:
            self.temp_dir = self.platform_utils.normalize_path(temp_dir)
        else:
            self.temp_dir = self.platform_utils.get_temp_dir() / 'mp4_to_text'
            
        # Create necessary directories
        self._ensure_directories()
        
        # Supported video formats
        self.supported_formats = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.webm', '.m4v', '.wmv', '.3gp', '.ogv'}
        
        # Processing history file
        self.history_file = self.output_dir / '.processing_history.json'
        self.processing_history = self._load_processing_history()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create audio temp directory
            audio_temp_dir = self.temp_dir / 'audio'
            audio_temp_dir.mkdir(parents=True, exist_ok=True)
            
        except Exception as e:
            raise RuntimeError(f"Failed to create directories: {e}")
    
    def _load_processing_history(self) -> Dict:
        """Load processing history from JSON file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load processing history: {e}")
                
        return {
            'processed_files': {},
            'statistics': {
                'total_processed': 0,
                'successful': 0,
                'failed': 0,
                'total_duration': 0,
                'total_processing_time': 0
            }
        }
    
    def _save_processing_history(self):
        """Save processing history to JSON file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.processing_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save processing history: {e}")
    
    def scan_videos(self, recursive: bool = True) -> List[Path]:
        """
        Scan input directory for video files.
        
        Args:
            recursive: Whether to scan subdirectories recursively
            
        Returns:
            List of video file paths
        """
        video_files = []
        
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory does not exist: {self.input_dir}")
            
        if not self.input_dir.is_dir():
            raise NotADirectoryError(f"Input path is not a directory: {self.input_dir}")
        
        # Choose scanning method
        pattern = "**/*" if recursive else "*"
        
        try:
            for file_path in self.input_dir.glob(pattern):
                if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                    video_files.append(file_path)
                    
        except Exception as e:
            print(f"Warning: Error scanning directory {self.input_dir}: {e}")
            
        return sorted(video_files)
    
    def get_output_path(self, video_path: Path, extension: str = '.txt') -> Path:
        """
        Generate output file path for a video file.
        
        Args:
            video_path: Path to the video file
            extension: Output file extension (default: .txt)
            
        Returns:
            Path to the output file
        """
        # Get relative path from input directory
        try:
            relative_path = video_path.relative_to(self.input_dir)
        except ValueError:
            # If not relative to input dir, use just the filename
            relative_path = video_path.name
            
        # Change extension
        output_name = relative_path.with_suffix(extension)
        
        # Sanitize filename if pathvalidate is available
        if PATHVALIDATE_AVAILABLE:
            output_name = Path(sanitize_filename(str(output_name)))
            
        return self.output_dir / output_name
    
    def get_temp_audio_path(self, video_path: Path) -> Path:
        """
        Generate temporary audio file path for a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Path to the temporary audio file
        """
        # Create unique filename based on video file hash
        file_hash = self._get_file_hash(video_path)
        audio_filename = f"{video_path.stem}_{file_hash[:8]}.wav"
        
        return self.temp_dir / 'audio' / audio_filename
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of file for unique identification."""
        hash_md5 = hashlib.md5()
        
        # Use file path and modification time for hash
        hash_input = f"{file_path.absolute()}_{file_path.stat().st_mtime}".encode('utf-8')
        hash_md5.update(hash_input)
        
        return hash_md5.hexdigest()
    
    def is_processed(self, video_path: Path, skip_existing: bool = True) -> bool:
        """
        Check if a video file has already been processed.
        
        Args:
            video_path: Path to the video file
            skip_existing: Whether to skip existing output files
            
        Returns:
            True if file should be skipped, False otherwise
        """
        if not skip_existing:
            return False
            
        # Check if output file exists
        output_path = self.get_output_path(video_path)
        if not output_path.exists():
            return False
            
        # Check processing history
        video_key = str(video_path.absolute())
        if video_key in self.processing_history['processed_files']:
            file_info = self.processing_history['processed_files'][video_key]
            
            # Check if file was successfully processed
            if file_info.get('success', False):
                # Check if output file still exists and is not empty
                if output_path.exists() and output_path.stat().st_size > 0:
                    return True
                    
        return False
    
    def mark_processed(self, video_path: Path, success: bool, 
                      duration: float = 0, processing_time: float = 0, 
                      model_used: str = "", error: str = ""):
        """
        Mark a video file as processed in the history.
        
        Args:
            video_path: Path to the video file
            success: Whether processing was successful
            duration: Video duration in seconds
            processing_time: Processing time in seconds
            model_used: Whisper model used
            error: Error message if processing failed
        """
        video_key = str(video_path.absolute())
        output_path = self.get_output_path(video_path)
        
        # Record file processing
        self.processing_history['processed_files'][video_key] = {
            'processed_at': datetime.now().isoformat(),
            'output_file': str(output_path),
            'duration': duration,
            'processing_time': processing_time,
            'model_used': model_used,
            'success': success,
            'error': error if not success else ""
        }
        
        # Update statistics
        stats = self.processing_history['statistics']
        stats['total_processed'] += 1
        
        if success:
            stats['successful'] += 1
        else:
            stats['failed'] += 1
            
        stats['total_duration'] += duration
        stats['total_processing_time'] += processing_time
        
        # Save history
        self._save_processing_history()
    
    def get_processing_stats(self) -> Dict:
        """Get processing statistics."""
        return self.processing_history['statistics'].copy()
    
    def cleanup_temp_files(self, keep_recent: int = 5):
        """
        Clean up temporary files, optionally keeping recent ones.
        
        Args:
            keep_recent: Number of recent temp files to keep (0 to delete all)
        """
        try:
            audio_temp_dir = self.temp_dir / 'audio'
            if not audio_temp_dir.exists():
                return
                
            # Get all temp audio files
            temp_files = list(audio_temp_dir.glob('*.wav'))
            
            if keep_recent > 0:
                # Sort by modification time (newest first)
                temp_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                
                # Keep recent files, delete the rest
                files_to_delete = temp_files[keep_recent:]
            else:
                files_to_delete = temp_files
            
            # Delete files
            deleted_count = 0
            for temp_file in files_to_delete:
                try:
                    temp_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"Warning: Failed to delete temp file {temp_file}: {e}")
                    
            if deleted_count > 0:
                print(f"Cleaned up {deleted_count} temporary files")
                
        except Exception as e:
            print(f"Warning: Error during temp file cleanup: {e}")
    
    def validate_input_directory(self) -> List[str]:
        """Validate input directory and return list of issues."""
        issues = []
        
        if not self.input_dir.exists():
            issues.append(f"Input directory does not exist: {self.input_dir}")
            return issues
            
        if not self.input_dir.is_dir():
            issues.append(f"Input path is not a directory: {self.input_dir}")
            return issues
            
        # Check for video files
        video_files = self.scan_videos()
        if not video_files:
            issues.append(f"No video files found in input directory: {self.input_dir}")
            issues.append(f"Supported formats: {', '.join(sorted(self.supported_formats))}")
            
        # Check read permissions
        if not os.access(self.input_dir, os.R_OK):
            issues.append(f"No read permission for input directory: {self.input_dir}")
            
        return issues
    
    def validate_output_directory(self) -> List[str]:
        """Validate output directory and return list of issues."""
        issues = []
        
        # Try to create output directory
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create output directory: {e}")
            return issues
            
        # Check write permissions
        if not os.access(self.output_dir, os.W_OK):
            issues.append(f"No write permission for output directory: {self.output_dir}")
            
        return issues
    
    def get_video_files_summary(self) -> Dict:
        """Get summary of video files in input directory."""
        video_files = self.scan_videos()
        
        # Group by extension
        by_extension = {}
        total_size = 0
        
        for video_path in video_files:
            ext = video_path.suffix.lower()
            if ext not in by_extension:
                by_extension[ext] = {'count': 0, 'size': 0}
                
            try:
                file_size = video_path.stat().st_size
                by_extension[ext]['count'] += 1
                by_extension[ext]['size'] += file_size
                total_size += file_size
            except Exception:
                by_extension[ext]['count'] += 1
        
        return {
            'total_files': len(video_files),
            'total_size': total_size,
            'by_extension': by_extension,
            'formats_found': list(by_extension.keys())
        }
    
    def move_processed_file(self, video_path: Path, destination_dir: str) -> bool:
        """
        Move a processed video file to destination directory.
        
        Args:
            video_path: Path to the video file to move
            destination_dir: Destination directory path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Normalize destination directory path
            dest_dir = self.platform_utils.normalize_path(destination_dir)
            
            # Create destination directory if it doesn't exist
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate destination file path
            dest_path = dest_dir / video_path.name
            
            # Handle file name conflicts
            counter = 1
            original_dest_path = dest_path
            while dest_path.exists():
                stem = original_dest_path.stem
                suffix = original_dest_path.suffix
                dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Move the file
            import shutil
            shutil.move(str(video_path), str(dest_path))
            
            print(f"  Moved to: {dest_path}")
            return True
            
        except Exception as e:
            print(f"  Warning: Failed to move file {video_path.name}: {e}")
            return False
    
    def print_summary(self):
        """Print summary of file manager status."""
        print("=== File Manager Summary ===")
        print(f"Input Directory: {self.input_dir}")
        print(f"Output Directory: {self.output_dir}")
        print(f"Temp Directory: {self.temp_dir}")
        
        # Video files summary
        summary = self.get_video_files_summary()
        print(f"\nVideo Files Found: {summary['total_files']}")
        
        if summary['total_size'] > 0:
            size_gb = summary['total_size'] / (1024**3)
            print(f"Total Size: {size_gb:.2f} GB")
            
        if summary['by_extension']:
            print("By Format:")
            for ext, info in summary['by_extension'].items():
                size_mb = info['size'] / (1024**2) if info['size'] > 0 else 0
                print(f"  {ext}: {info['count']} files ({size_mb:.1f} MB)")
                
        # Processing statistics
        stats = self.get_processing_stats()
        if stats['total_processed'] > 0:
            print(f"\nProcessing History:")
            print(f"  Total Processed: {stats['total_processed']}")
            print(f"  Successful: {stats['successful']}")
            print(f"  Failed: {stats['failed']}")
            
            success_rate = (stats['successful'] / stats['total_processed']) * 100
            print(f"  Success Rate: {success_rate:.1f}%")


if __name__ == "__main__":
    # Test file manager
    import sys
    
    if len(sys.argv) >= 3:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
        
        file_manager = FileManager(input_dir, output_dir)
        file_manager.print_summary()
        
        # Validate directories
        input_issues = file_manager.validate_input_directory()
        output_issues = file_manager.validate_output_directory()
        
        if input_issues:
            print("\nInput Directory Issues:")
            for issue in input_issues:
                print(f"  - {issue}")
                
        if output_issues:
            print("\nOutput Directory Issues:")
            for issue in output_issues:
                print(f"  - {issue}")
    else:
        print("Usage: python file_manager.py <input_dir> <output_dir>") 