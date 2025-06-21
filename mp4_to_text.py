#!/usr/bin/env python3
"""
MP4ToText - Video to Text Transcription Tool

A cross-platform tool for batch processing MP4 videos and extracting text using OpenAI Whisper.
Supports GPU/CPU auto-detection and multi-platform compatibility.

Author: Video2Text Team
License: MIT
"""

import sys
import argparse
import logging
import time
from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import signal

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

try:
    import colorama
    colorama.init()
    COLORAMA_AVAILABLE = True
    
    # ANSI color codes
    class Colors:
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        BLUE = '\033[94m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        BOLD = '\033[1m'
        END = '\033[0m'
except ImportError:
    COLORAMA_AVAILABLE = False
    
    class Colors:
        GREEN = YELLOW = RED = BLUE = CYAN = WHITE = BOLD = END = ''

# Import core modules
try:
    from core import (
        ConfigManager, 
        FileManager, 
        AudioProcessor, 
        WhisperTranscriber, 
        PlatformUtils
    )
except ImportError as e:
    print(f"Error: Failed to import core modules: {e}")
    print("Please ensure all dependencies are installed and core modules are available.")
    sys.exit(1)


class MP4ToTextProcessor:
    """Main processor for MP4 to text conversion."""
    
    def __init__(self, config_manager: ConfigManager, move_to_done: bool = False, done_dir: str = None):
        self.config = config_manager
        self.platform_utils = PlatformUtils()
        self.move_to_done = move_to_done
        self.done_dir = done_dir
        
        # Initialize components
        self.file_manager = FileManager(
            input_dir=self.config.processing_config.input_dir,
            output_dir=self.config.processing_config.output_dir
        )
        
        self.audio_processor = AudioProcessor(
            temp_dir=str(self.platform_utils.get_temp_dir() / 'mp4_to_text'),
            audio_config=self.config.audio_config.__dict__
        )
        
        self.transcriber = WhisperTranscriber(
            model_name=self.config.processing_config.model_name,
            device=self.config.get_effective_device()
        )
        
        # Processing statistics
        self.stats = {
            'total_files': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total_duration': 0.0,
            'total_processing_time': 0.0,
            'start_time': 0.0
        }
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        self._shutdown_requested = False
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            print(f"\n{Colors.YELLOW}Shutdown requested. Finishing current task...{Colors.END}")
            self._shutdown_requested = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _print_header(self):
        """Print application header."""
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("=" * 60)
        print("           MP4ToText - Video Transcription Tool")
        print("=" * 60)
        print(f"{Colors.END}")
        
        # System info
        print(f"{Colors.BLUE}System Information:{Colors.END}")
        device, device_info = self.platform_utils.detect_device()
        print(f"  Platform: {self.platform_utils.system.title()}")
        print(f"  Device: {device}")
        print(f"  Model: {self.config.processing_config.model_name}")
        print(f"  Language: {self.config.processing_config.language}")
        print()
    
    def _validate_setup(self) -> bool:
        """Validate setup and configuration."""
        print(f"{Colors.BLUE}Validating setup...{Colors.END}")
        
        # Validate configuration
        config_errors = self.config.validate_config()
        if config_errors:
            print(f"{Colors.RED}Configuration errors:{Colors.END}")
            for error in config_errors:
                print(f"  - {error}")
            return False
        
        # Validate directories
        input_issues = self.file_manager.validate_input_directory()
        output_issues = self.file_manager.validate_output_directory()
        
        if input_issues:
            print(f"{Colors.RED}Input directory issues:{Colors.END}")
            for issue in input_issues:
                print(f"  - {issue}")
            return False
        
        if output_issues:
            print(f"{Colors.RED}Output directory issues:{Colors.END}")
            for issue in output_issues:
                print(f"  - {issue}")
            return False
        
        print(f"{Colors.GREEN}✓ Setup validation successful{Colors.END}")
        return True
    
    def _load_whisper_model(self) -> bool:
        """Load Whisper model with progress indication."""
        print(f"{Colors.BLUE}Loading Whisper model...{Colors.END}")
        
        if not self.transcriber.load_model():
            print(f"{Colors.RED}✗ Failed to load Whisper model{Colors.END}")
            return False
        
        print(f"{Colors.GREEN}✓ Model loaded successfully{Colors.END}")
        return True
    
    def _get_video_files(self) -> List[Path]:
        """Get list of video files to process."""
        print(f"{Colors.BLUE}Scanning for video files...{Colors.END}")
        
        video_files = self.file_manager.scan_videos()
        
        # Filter out already processed files if requested
        if self.config.processing_config.skip_existing:
            original_count = len(video_files)
            video_files = [
                video for video in video_files 
                if not self.file_manager.is_processed(video, skip_existing=True)
            ]
            skipped = original_count - len(video_files)
            if skipped > 0:
                print(f"{Colors.YELLOW}Skipping {skipped} already processed files{Colors.END}")
        
        self.stats['total_files'] = len(video_files)
        
        if not video_files:
            print(f"{Colors.YELLOW}No video files to process{Colors.END}")
            return []
        
        print(f"{Colors.GREEN}Found {len(video_files)} video files to process{Colors.END}")
        return video_files
    
    def process_single_file(self, video_path: Path) -> bool:
        """
        Process a single video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if successful, False otherwise
        """
        if self._shutdown_requested:
            return False
        
        start_time = time.time()
        video_duration = 0.0
        
        try:
            # Validate video file
            is_valid, error_msg = self.audio_processor.validate_video_file(video_path)
            if not is_valid:
                print(f"{Colors.RED}✗ Validation failed: {error_msg}{Colors.END}")
                self.file_manager.mark_processed(
                    video_path, success=False, error=error_msg
                )
                return False
            
            # Get video info
            video_info = self.audio_processor.get_video_info(video_path)
            video_duration = video_info.get('duration', 0.0)
            
            if not self.config.processing_config.quiet:
                print(f"{Colors.CYAN}Processing: {video_path.name}{Colors.END}")
                print(f"  Duration: {video_duration:.1f}s")
            
            # Extract audio
            if not self.config.processing_config.quiet:
                print("  Extracting audio...")
            
            def audio_progress(progress):
                if not self.config.processing_config.quiet and TQDM_AVAILABLE:
                    pass  # tqdm progress bar handles this
            
            audio_path = self.audio_processor.extract_audio(
                video_path, 
                progress_callback=audio_progress
            )
            
            if self._shutdown_requested:
                self.audio_processor.cleanup_temp_audio(audio_path)
                return False
            
            # Transcribe audio
            if not self.config.processing_config.quiet:
                print("  Transcribing audio...")
            
            def transcribe_progress(progress):
                if not self.config.processing_config.quiet and TQDM_AVAILABLE:
                    pass  # tqdm progress bar handles this
            
            result = self.transcriber.transcribe(
                audio_path,
                language=self.config.processing_config.language,
                progress_callback=transcribe_progress
            )
            
            if not result.text.strip():
                error_msg = "No text extracted from audio"
                print(f"{Colors.YELLOW}⚠ Warning: {error_msg}{Colors.END}")
                self.file_manager.mark_processed(
                    video_path, success=False, error=error_msg,
                    duration=video_duration, processing_time=time.time() - start_time,
                    model_used=self.config.processing_config.model_name
                )
                self.audio_processor.cleanup_temp_audio(audio_path)
                return False
            
            # Save result
            output_path = self.file_manager.get_output_path(video_path)
            self.transcriber.save_result(result, output_path)
            
            # Clean up temp file
            if self.config.processing_config.cleanup_temp:
                self.audio_processor.cleanup_temp_audio(audio_path)
            
            # Record success
            processing_time = time.time() - start_time
            self.file_manager.mark_processed(
                video_path, success=True,
                duration=video_duration, processing_time=processing_time,
                model_used=self.config.processing_config.model_name
            )
            
            # Update statistics
            self.stats['successful'] += 1
            self.stats['total_duration'] += video_duration
            self.stats['total_processing_time'] += processing_time
            
            # Move processed file to done directory if configured
            if self.move_to_done and self.done_dir:
                if not self.config.processing_config.quiet:
                    print(f"  Moving processed file...")
                self.file_manager.move_processed_file(video_path, self.done_dir)
            
            if not self.config.processing_config.quiet:
                realtime_factor = processing_time / video_duration if video_duration > 0 else 0
                print(f"{Colors.GREEN}✓ Completed in {processing_time:.1f}s "
                      f"(RTF: {realtime_factor:.2f}){Colors.END}")
                print(f"  Output: {output_path}")
                print(f"  Text length: {len(result.text)} characters")
                if result.language != 'auto':
                    print(f"  Detected language: {result.language}")
                print()
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"{Colors.RED}✗ Error processing {video_path.name}: {error_msg}{Colors.END}")
            
            # Record failure
            self.file_manager.mark_processed(
                video_path, success=False, error=error_msg,
                duration=video_duration, processing_time=time.time() - start_time,
                model_used=self.config.processing_config.model_name
            )
            
            self.stats['failed'] += 1
            return False
        
        finally:
            self.stats['processed'] += 1
    
    def process_batch(self) -> bool:
        """Process all video files in batch."""
        if not self._validate_setup():
            return False
        
        if not self._load_whisper_model():
            return False
        
        video_files = self._get_video_files()
        if not video_files:
            return True
        
        self.stats['start_time'] = time.time()
        
        # Print processing plan
        print(f"{Colors.BLUE}Processing Plan:{Colors.END}")
        print(f"  Files to process: {len(video_files)}")
        print(f"  Max workers: {self.config.processing_config.max_workers}")
        print(f"  Skip existing: {self.config.processing_config.skip_existing}")
        print()
        
        # Process files
        if self.config.processing_config.max_workers > 1:
            success = self._process_concurrent(video_files)
        else:
            success = self._process_sequential(video_files)
        
        # Print final statistics
        self._print_final_stats()
        
        # Cleanup
        if self.config.processing_config.cleanup_temp:
            self.file_manager.cleanup_temp_files()
        
        return success
    
    def _process_sequential(self, video_files: List[Path]) -> bool:
        """Process files sequentially."""
        if TQDM_AVAILABLE and not self.config.processing_config.quiet:
            video_files = tqdm(video_files, desc="Processing videos", unit="file")
        
        for video_path in video_files:
            if self._shutdown_requested:
                print(f"{Colors.YELLOW}Processing interrupted by user{Colors.END}")
                break
            
            self.process_single_file(video_path)
        
        return not self._shutdown_requested
    
    def _process_concurrent(self, video_files: List[Path]) -> bool:
        """Process files concurrently."""
        max_workers = min(self.config.processing_config.max_workers, len(video_files))
        
        print(f"{Colors.BLUE}Starting concurrent processing with {max_workers} workers...{Colors.END}")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_video = {
                executor.submit(self.process_single_file, video_path): video_path
                for video_path in video_files
            }
            
            # Process completed tasks
            if TQDM_AVAILABLE and not self.config.processing_config.quiet:
                futures = tqdm(as_completed(future_to_video), 
                             total=len(video_files), 
                             desc="Processing videos", 
                             unit="file")
            else:
                futures = as_completed(future_to_video)
            
            for future in futures:
                if self._shutdown_requested:
                    print(f"{Colors.YELLOW}Cancelling remaining tasks...{Colors.END}")
                    for remaining_future in future_to_video:
                        remaining_future.cancel()
                    break
                
                try:
                    future.result()  # Get result to catch any exceptions
                except Exception as e:
                    video_path = future_to_video[future]
                    print(f"{Colors.RED}Error in worker processing {video_path.name}: {e}{Colors.END}")
        
        return not self._shutdown_requested
    
    def _print_final_stats(self):
        """Print final processing statistics."""
        total_time = time.time() - self.stats['start_time']
        
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("=" * 60)
        print("                   Processing Summary")
        print("=" * 60)
        print(f"{Colors.END}")
        
        print(f"Total files: {self.stats['total_files']}")
        print(f"Processed: {self.stats['processed']}")
        print(f"Successful: {Colors.GREEN}{self.stats['successful']}{Colors.END}")
        print(f"Failed: {Colors.RED}{self.stats['failed']}{Colors.END}")
        print(f"Skipped: {Colors.YELLOW}{self.stats.get('skipped', 0)}{Colors.END}")
        
        if self.stats['processed'] > 0:
            success_rate = (self.stats['successful'] / self.stats['processed']) * 100
            print(f"Success rate: {success_rate:.1f}%")
        
        print(f"\nTiming:")
        print(f"Total time: {total_time:.1f}s")
        print(f"Total audio duration: {self.stats['total_duration']:.1f}s")
        print(f"Total processing time: {self.stats['total_processing_time']:.1f}s")
        
        if self.stats['total_duration'] > 0:
            avg_rtf = self.stats['total_processing_time'] / self.stats['total_duration']
            print(f"Average RTF: {avg_rtf:.2f}")
        
        if self.stats['successful'] > 0:
            avg_time_per_file = self.stats['total_processing_time'] / self.stats['successful']
            print(f"Average time per file: {avg_time_per_file:.1f}s")
        
        print()


def setup_logging(config: ConfigManager):
    """Setup logging configuration."""
    log_level = getattr(logging, config.logging_config.level.upper(), logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    simple_formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # File handler
    if config.logging_config.file:
        try:
            log_path = Path(config.logging_config.file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=config.logging_config.max_size,
                backupCount=config.logging_config.backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Failed to setup file logging: {e}")
    
    # Console handler
    if config.logging_config.console_output and not config.processing_config.quiet:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="MP4ToText - Convert video files to text using OpenAI Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mp4_to_text.py -i ./videos -o ./texts
  python mp4_to_text.py -i ./videos -o ./texts -m large-v3 -l zh
  python mp4_to_text.py -i ./videos -o ./texts -w 2 --skip-existing
  python mp4_to_text.py --config config.ini

Supported video formats: .mp4, .avi, .mov, .mkv, .flv, .webm, .m4v
Supported models: tiny, base, small, medium, large, large-v2, large-v3
Supported languages: auto, zh, en, ja, ko, fr, de, es, ru, pt, it, ar, hi
        """)
    
    # Required arguments (but not for info commands)
    parser.add_argument('-i', '--input', type=str,
                        help='Input directory containing MP4 files')
    parser.add_argument('-o', '--output', type=str,
                        help='Output directory for text files')
    
    # Model and processing options
    parser.add_argument('-m', '--model', type=str, default='medium',
                        choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'],
                        help='Whisper model to use (default: medium)')
    parser.add_argument('-l', '--language', type=str, default='auto',
                        help='Audio language (auto/zh/en/ja/ko/fr/de/es/ru/pt/it/ar/hi)')
    parser.add_argument('-d', '--device', type=str, default='auto',
                        choices=['auto', 'cpu', 'cuda', 'mps'],
                        help='Device to use (default: auto)')
    
    # Parallel processing
    parser.add_argument('-w', '--workers', type=int, default=1,
                        help='Number of parallel workers (default: 1)')
    
    # Behavior options
    parser.add_argument('-s', '--skip-existing', action='store_true',
                        help='Skip files that have already been processed')
    parser.add_argument('--no-cleanup', action='store_true',
                        help='Do not cleanup temporary files')
    
    # Configuration
    parser.add_argument('-c', '--config', type=str,
                        help='Configuration file path')
    
    # Output options
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Quiet mode (minimal output)')
    
    # Information options
    parser.add_argument('--system-info', action='store_true',
                        help='Show system information and exit')
    parser.add_argument('--list-models', action='store_true',
                        help='List available models and exit')
    
    return parser


def main():
    """Main entry point."""
    try:
        # Parse command line arguments
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # Handle information requests
        if args.system_info:
            utils = PlatformUtils()
            utils.print_system_info()
            return 0
        
        if args.list_models:
            from core.transcriber import get_available_models, get_recommended_model
            print("Available Whisper models:")
            for model in get_available_models():
                print(f"  - {model}")
            print(f"\nRecommended model for this system: {get_recommended_model()}")
            return 0
        
        # Check required arguments for processing
        if not args.input or not args.output:
            parser.error("Input (-i) and output (-o) directories are required for processing")
        
        # Create configuration manager
        config_manager = ConfigManager(config_file=args.config)
        
        # Update configuration from command line arguments
        config_manager.update_from_args(args)
        
        # Update cleanup setting
        if args.no_cleanup:
            config_manager.processing_config.cleanup_temp = False
        
        # Setup logging
        setup_logging(config_manager)
        
        # Create and run processor
        processor = MP4ToTextProcessor(config_manager)
        processor._print_header()
        
        if not processor.config.processing_config.quiet:
            processor.config.print_config_summary()
            print()
        
        success = processor.process_batch()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Process interrupted by user{Colors.END}")
        return 130
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        if __debug__:
            import traceback
            traceback.print_exc()
        return 1
    finally:
        # Cleanup on exit
        try:
            if 'processor' in locals():
                processor.transcriber.unload_model()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main()) 