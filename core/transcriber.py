"""
Whisper transcriber for MP4ToText tool.
Handles cross-platform OpenAI Whisper integration with GPU/CPU auto-detection.
"""

import os
import warnings
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass
import time

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from .platform_utils import PlatformUtils


@dataclass
class TranscriptionResult:
    """Result of transcription process."""
    text: str = ""
    segments: List[Dict] = None
    language: str = ""
    duration: float = 0.0
    processing_time: float = 0.0
    model_used: str = ""
    device_used: str = ""
    confidence_scores: List[float] = None
    
    def __post_init__(self):
        if self.segments is None:
            self.segments = []
        if self.confidence_scores is None:
            self.confidence_scores = []


class WhisperTranscriber:
    """Cross-platform Whisper transcriber with GPU/CPU auto-detection."""
    
    # Whisper model configurations
    MODEL_CONFIGS = {
        'tiny': {'memory_gb': 1, 'relative_speed': 32},
        'base': {'memory_gb': 2, 'relative_speed': 16},
        'small': {'memory_gb': 3, 'relative_speed': 6},
        'medium': {'memory_gb': 5, 'relative_speed': 2},
        'large': {'memory_gb': 8, 'relative_speed': 1},
        'large-v2': {'memory_gb': 8, 'relative_speed': 1},
        'large-v3': {'memory_gb': 10, 'relative_speed': 1},
    }
    
    def __init__(self, model_name: str = 'medium', device: str = 'auto', 
                 download_root: Optional[str] = None):
        """
        Initialize Whisper transcriber.
        
        Args:
            model_name: Whisper model name
            device: Device to use ('auto', 'cpu', 'cuda', 'mps')
            download_root: Custom download directory for models
        """
        if not WHISPER_AVAILABLE:
            raise ImportError("OpenAI Whisper not available. Install with: pip install openai-whisper")
        
        self.platform_utils = PlatformUtils()
        self.model_name = model_name
        self.device = self._resolve_device(device)
        self.model = None
        self.model_load_time = 0.0
        
        # Set download root
        if download_root:
            self.download_root = Path(download_root)
        else:
            self.download_root = self.platform_utils.get_whisper_model_cache_dir()
        
        # Suppress warnings for cleaner output
        warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
        warnings.filterwarnings("ignore", message="The parameter 'token'")
        
        # Initialize model info
        self._validate_model_name()
        self._check_system_requirements()
    
    def _resolve_device(self, device: str) -> str:
        """Resolve device based on system capabilities."""
        if device == 'auto':
            detected_device, device_info = self.platform_utils.detect_device()
            
            # Additional validation for detected device
            if detected_device == 'cuda':
                if TORCH_AVAILABLE and torch.cuda.is_available():
                    return 'cuda'
                else:
                    print("Warning: CUDA detected but not available, falling back to CPU")
                    return 'cpu'
            elif detected_device == 'mps':
                if TORCH_AVAILABLE and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    return 'mps'
                else:
                    print("Warning: MPS detected but not available, falling back to CPU")
                    return 'cpu'
            else:
                return 'cpu'
        else:
            # Validate requested device
            if device == 'cuda' and not (TORCH_AVAILABLE and torch.cuda.is_available()):
                raise ValueError("CUDA requested but not available")
            elif device == 'mps' and not (TORCH_AVAILABLE and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
                raise ValueError("MPS requested but not available")
            
            return device
    
    def _validate_model_name(self):
        """Validate model name."""
        if self.model_name not in self.MODEL_CONFIGS:
            available_models = list(self.MODEL_CONFIGS.keys())
            raise ValueError(f"Invalid model '{self.model_name}'. Available models: {available_models}")
    
    def _check_system_requirements(self):
        """Check if system meets requirements for selected model."""
        model_config = self.MODEL_CONFIGS[self.model_name]
        required_memory = model_config['memory_gb']
        
        available_memory = self.platform_utils.check_available_memory()
        if available_memory and available_memory < required_memory:
            print(f"Warning: Model '{self.model_name}' requires {required_memory}GB memory, "
                  f"but only {available_memory:.1f}GB available. Performance may be affected.")
    
    def load_model(self, force_reload: bool = False) -> bool:
        """
        Load Whisper model with error handling.
        
        Args:
            force_reload: Force reload even if model is already loaded
            
        Returns:
            True if successfully loaded, False otherwise
        """
        if self.model is not None and not force_reload:
            return True
        
        try:
            print(f"Loading Whisper model '{self.model_name}' on device '{self.device}'...")
            start_time = time.time()
            
            # Create download directory if it doesn't exist
            self.download_root.mkdir(parents=True, exist_ok=True)
            
            # Load model with device specification
            self.model = whisper.load_model(
                self.model_name, 
                device=self.device,
                download_root=str(self.download_root)
            )
            
            self.model_load_time = time.time() - start_time
            
            print(f"Model loaded successfully in {self.model_load_time:.1f} seconds")
            return True
            
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            
            # Try fallback to CPU if GPU loading failed
            if self.device != 'cpu':
                print("Attempting fallback to CPU...")
                try:
                    self.device = 'cpu'
                    self.model = whisper.load_model(
                        self.model_name,
                        device='cpu',
                        download_root=str(self.download_root)
                    )
                    self.model_load_time = time.time() - start_time
                    print(f"Fallback to CPU successful")
                    return True
                except Exception as fallback_error:
                    print(f"CPU fallback also failed: {fallback_error}")
            
            return False
    
    def transcribe(self, audio_path: Path, language: str = 'auto',
                  progress_callback: Optional[Callable[[float], None]] = None,
                  **transcribe_options) -> TranscriptionResult:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Language code ('auto' for auto-detection)
            progress_callback: Optional progress callback function
            **transcribe_options: Additional Whisper transcription options
            
        Returns:
            TranscriptionResult object
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if not self.load_model():
            raise RuntimeError("Failed to load Whisper model")
        
        start_time = time.time()
        
        try:
            # Prepare transcription options
            options = {
                'verbose': False,
                'word_timestamps': True,
                'condition_on_previous_text': True,
                'temperature': 0.0  # Deterministic output
            }
            
            # Set language if specified
            if language != 'auto' and language:
                options['language'] = language
            
            # Update with user options
            options.update(transcribe_options)
            
            # Progress callback wrapper
            if progress_callback:
                def whisper_progress_hook(current_segment, total_segments):
                    if total_segments > 0:
                        progress = current_segment / total_segments
                        progress_callback(progress)
            else:
                whisper_progress_hook = None
            
            print(f"Transcribing audio file: {audio_path.name}")
            
            # Perform transcription
            result = self.model.transcribe(
                str(audio_path),
                **options
            )
            
            processing_time = time.time() - start_time
            
            # Extract confidence scores if available
            confidence_scores = []
            if 'segments' in result and result['segments']:
                for segment in result['segments']:
                    if 'words' in segment and segment['words']:
                        word_confidences = [word.get('probability', 0.0) for word in segment['words']]
                        confidence_scores.extend(word_confidences)
            
            # Create result object
            transcription_result = TranscriptionResult(
                text=result.get('text', '').strip(),
                segments=result.get('segments', []),
                language=result.get('language', language),
                processing_time=processing_time,
                model_used=self.model_name,
                device_used=self.device,
                confidence_scores=confidence_scores
            )
            
            # Get audio duration from result if available
            if result.get('segments'):
                last_segment = result['segments'][-1]
                transcription_result.duration = last_segment.get('end', 0.0)
            
            print(f"Transcription completed in {processing_time:.1f} seconds")
            print(f"Detected language: {transcription_result.language}")
            
            if progress_callback:
                progress_callback(1.0)
            
            return transcription_result
            
        except Exception as e:
            error_msg = f"Transcription failed: {e}"
            print(error_msg)
            
            # Return empty result with error info
            return TranscriptionResult(
                text="",
                processing_time=time.time() - start_time,
                model_used=self.model_name,
                device_used=self.device
            )
    
    def save_result(self, result: TranscriptionResult, output_path: Path, 
                   format_type: str = 'txt', include_timestamps: bool = False):
        """
        Save transcription result to file.
        
        Args:
            result: TranscriptionResult object
            output_path: Output file path
            format_type: Output format ('txt', 'srt', 'vtt', 'json')
            include_timestamps: Whether to include timestamps in text output
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if format_type == 'txt':
                self._save_txt(result, output_path, include_timestamps)
            elif format_type == 'srt':
                self._save_srt(result, output_path)
            elif format_type == 'vtt':
                self._save_vtt(result, output_path)
            elif format_type == 'json':
                self._save_json(result, output_path)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to save transcription result: {e}")
    
    def _save_txt(self, result: TranscriptionResult, output_path: Path, include_timestamps: bool):
        """Save as plain text file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            if include_timestamps and result.segments:
                for segment in result.segments:
                    start_time = self._format_timestamp(segment.get('start', 0))
                    end_time = self._format_timestamp(segment.get('end', 0))
                    text = segment.get('text', '').strip()
                    f.write(f"[{start_time} --> {end_time}] {text}\n")
            else:
                f.write(result.text)
                if result.text and not result.text.endswith('\n'):
                    f.write('\n')
    
    def _save_srt(self, result: TranscriptionResult, output_path: Path):
        """Save as SRT subtitle file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            if result.segments:
                for i, segment in enumerate(result.segments, 1):
                    start_time = self._format_timestamp_srt(segment.get('start', 0))
                    end_time = self._format_timestamp_srt(segment.get('end', 0))
                    text = segment.get('text', '').strip()
                    
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")
    
    def _save_vtt(self, result: TranscriptionResult, output_path: Path):
        """Save as WebVTT subtitle file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            
            if result.segments:
                for segment in result.segments:
                    start_time = self._format_timestamp_vtt(segment.get('start', 0))
                    end_time = self._format_timestamp_vtt(segment.get('end', 0))
                    text = segment.get('text', '').strip()
                    
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")
    
    def _save_json(self, result: TranscriptionResult, output_path: Path):
        """Save as JSON file with detailed information."""
        import json
        
        # Convert result to dictionary
        result_dict = {
            'text': result.text,
            'language': result.language,
            'duration': result.duration,
            'processing_time': result.processing_time,
            'model_used': result.model_used,
            'device_used': result.device_used,
            'segments': result.segments,
            'confidence_scores': result.confidence_scores,
            'metadata': {
                'average_confidence': sum(result.confidence_scores) / len(result.confidence_scores) if result.confidence_scores else 0.0,
                'total_segments': len(result.segments),
                'total_words': sum(len(seg.get('words', [])) for seg in result.segments)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp for text output."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _format_timestamp_srt(self, seconds: float) -> str:
        """Format timestamp for SRT format."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def _format_timestamp_vtt(self, seconds: float) -> str:
        """Format timestamp for WebVTT format."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about current model."""
        model_config = self.MODEL_CONFIGS.get(self.model_name, {})
        device_name, device_info = self.platform_utils.detect_device()
        
        return {
            'model_name': self.model_name,
            'device': self.device,
            'memory_requirement_gb': model_config.get('memory_gb', 0),
            'relative_speed': model_config.get('relative_speed', 1),
            'model_loaded': self.model is not None,
            'model_load_time': self.model_load_time,
            'download_root': str(self.download_root),
            'available_device': device_name,
            'device_info': device_info
        }
    
    def unload_model(self):
        """Unload model to free memory."""
        if self.model is not None:
            del self.model
            self.model = None
            
            # Force garbage collection if torch is available
            if TORCH_AVAILABLE:
                import gc
                gc.collect()
                
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    torch.mps.empty_cache()
            
            print("Whisper model unloaded")
    
    def benchmark_transcription(self, test_audio_path: Path, num_runs: int = 3) -> Dict[str, float]:
        """
        Benchmark transcription performance.
        
        Args:
            test_audio_path: Path to test audio file
            num_runs: Number of benchmark runs
            
        Returns:
            Dictionary with benchmark results
        """
        if not test_audio_path.exists():
            raise FileNotFoundError(f"Test audio file not found: {test_audio_path}")
        
        if not self.load_model():
            raise RuntimeError("Failed to load model for benchmarking")
        
        print(f"Benchmarking {self.model_name} on {self.device} ({num_runs} runs)...")
        
        times = []
        for run in range(num_runs):
            print(f"Run {run + 1}/{num_runs}...")
            result = self.transcribe(test_audio_path)
            times.append(result.processing_time)
        
        # Calculate statistics
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        return {
            'average_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'audio_duration': result.duration,
            'realtime_factor': avg_time / result.duration if result.duration > 0 else 0,
            'model_name': self.model_name,
            'device': self.device
        }


def get_available_models() -> List[str]:
    """Get list of available Whisper models."""
    return list(WhisperTranscriber.MODEL_CONFIGS.keys())


def get_recommended_model(available_memory_gb: Optional[float] = None) -> str:
    """Get recommended model based on available memory."""
    if available_memory_gb is None:
        utils = PlatformUtils()
        available_memory_gb = utils.check_available_memory()
    
    if available_memory_gb is None:
        return 'medium'  # Safe default
    
    # Find largest model that fits in memory
    for model in ['large-v3', 'large', 'medium', 'small', 'base', 'tiny']:
        required_memory = WhisperTranscriber.MODEL_CONFIGS[model]['memory_gb']
        if available_memory_gb >= required_memory:
            return model
    
    return 'tiny'  # Smallest model as last resort


if __name__ == "__main__":
    # Test transcriber
    import sys
    
    if len(sys.argv) >= 2:
        audio_file = Path(sys.argv[1])
        model_name = sys.argv[2] if len(sys.argv) > 2 else 'medium'
        
        print(f"Testing transcriber with: {audio_file}")
        print(f"Model: {model_name}")
        
        # Create transcriber
        transcriber = WhisperTranscriber(model_name=model_name)
        
        # Print model info
        info = transcriber.get_model_info()
        print(f"Model info: {info}")
        
        # Transcribe with progress
        def progress_callback(progress):
            print(f"\rTranscribing: {progress*100:.1f}%", end='', flush=True)
        
        try:
            result = transcriber.transcribe(audio_file, progress_callback=progress_callback)
            print(f"\nTranscription completed!")
            print(f"Text: {result.text[:200]}...")
            print(f"Language: {result.language}")
            print(f"Duration: {result.duration:.1f}s")
            print(f"Processing time: {result.processing_time:.1f}s")
            
            # Save result
            output_path = audio_file.with_suffix('.txt')
            transcriber.save_result(result, output_path)
            print(f"Result saved to: {output_path}")
            
        except Exception as e:
            print(f"\nError: {e}")
        finally:
            transcriber.unload_model()
    else:
        print("Usage: python transcriber.py <audio_file> [model_name]")
        print(f"Available models: {get_available_models()}")
        print(f"Recommended model: {get_recommended_model()}") 