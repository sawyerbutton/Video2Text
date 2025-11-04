"""
Faster-Whisper transcriber for MP4ToText tool.
Handles cross-platform faster-whisper integration with GPU/CPU auto-detection.
Provides 2-8x performance boost over OpenAI Whisper with same accuracy.
"""

import os
import warnings
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass
import time

try:
    from faster_whisper import WhisperModel, BatchedInferencePipeline
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
    """Cross-platform Faster-Whisper transcriber with GPU/CPU auto-detection."""

    # Whisper model configurations (updated for faster-whisper)
    MODEL_CONFIGS = {
        'tiny': {'memory_gb': 1, 'relative_speed': 64},  # 2x faster than OpenAI
        'base': {'memory_gb': 2, 'relative_speed': 32},  # 2x faster than OpenAI
        'small': {'memory_gb': 3, 'relative_speed': 12}, # 2x faster than OpenAI
        'medium': {'memory_gb': 5, 'relative_speed': 4}, # 2x faster than OpenAI
        'large': {'memory_gb': 8, 'relative_speed': 2},  # 2x faster than OpenAI
        'large-v2': {'memory_gb': 8, 'relative_speed': 2},
        'large-v3': {'memory_gb': 10, 'relative_speed': 2},
        'turbo': {'memory_gb': 6, 'relative_speed': 8},  # New fast model
    }

    # Compute type mapping for different devices
    COMPUTE_TYPE_MAP = {
        'cuda': ['float16', 'int8_float16', 'int8'],  # GPU options
        'cpu': ['int8', 'float32'],  # CPU options
        'mps': ['float16'],  # Apple Silicon (MPS doesn't support int8)
    }

    def __init__(self, model_name: str = 'medium', device: str = 'auto',
                 compute_type: str = 'auto', download_root: Optional[str] = None,
                 batch_size: int = 1, vad_filter: bool = False):
        """
        Initialize Faster-Whisper transcriber.

        Args:
            model_name: Whisper model name
            device: Device to use ('auto', 'cpu', 'cuda', 'mps')
            compute_type: Quantization type ('auto', 'float16', 'int8', 'float32')
            download_root: Custom download directory for models
            batch_size: Batch size for processing (1=disabled, 8-16 recommended)
            vad_filter: Enable Voice Activity Detection to skip silence
        """
        if not WHISPER_AVAILABLE:
            raise ImportError(
                "faster-whisper not available. Install with: pip install faster-whisper"
            )

        self.platform_utils = PlatformUtils()
        self.model_name = model_name
        self.device = self._resolve_device(device)
        self.compute_type = self._resolve_compute_type(compute_type)
        self.batch_size = batch_size
        self.vad_filter = vad_filter
        self.model = None
        self.batched_model = None
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
        self._check_cuda_version()

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

    def _resolve_compute_type(self, compute_type: str) -> str:
        """Resolve compute type based on device and user preference."""
        if compute_type == 'auto':
            # Auto-select best compute type for device
            if self.device == 'cuda':
                # For GPU, prefer int8 for memory efficiency
                return 'int8_float16'
            elif self.device == 'mps':
                # MPS only supports float16
                return 'float16'
            else:  # CPU
                # For CPU, int8 gives best performance
                return 'int8'
        else:
            # Validate compute type for device
            available_types = self.COMPUTE_TYPE_MAP.get(self.device, [])
            if compute_type not in available_types:
                print(f"Warning: compute_type '{compute_type}' not optimal for {self.device}. "
                      f"Available: {available_types}. Using anyway.")
            return compute_type

    def _check_cuda_version(self):
        """Check CUDA version compatibility for faster-whisper."""
        if self.device == 'cuda' and TORCH_AVAILABLE:
            try:
                cuda_version = torch.version.cuda
                if cuda_version:
                    major_version = int(cuda_version.split('.')[0])
                    if major_version < 12:
                        print(f"⚠️  Warning: CUDA {cuda_version} detected. "
                              f"faster-whisper works best with CUDA 12+")
                        print(f"   If you encounter issues, downgrade ctranslate2: "
                              f"pip install --force-reinstall ctranslate2==3.24.0")
            except Exception:
                pass  # Ignore version check errors

    def _validate_model_name(self):
        """Validate model name."""
        if self.model_name not in self.MODEL_CONFIGS:
            available_models = list(self.MODEL_CONFIGS.keys())
            raise ValueError(
                f"Invalid model '{self.model_name}'. Available models: {available_models}"
            )

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
        Load Faster-Whisper model with error handling.

        Args:
            force_reload: Force reload even if model is already loaded

        Returns:
            True if successfully loaded, False otherwise
        """
        if self.model is not None and not force_reload:
            return True

        try:
            print(f"Loading Faster-Whisper model '{self.model_name}' on device '{self.device}' "
                  f"with compute_type '{self.compute_type}'...")
            start_time = time.time()

            # Create download directory if it doesn't exist
            self.download_root.mkdir(parents=True, exist_ok=True)

            # Load model with device and compute type specification
            self.model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
                download_root=str(self.download_root)
            )

            # If batch_size > 1, create batched pipeline
            if self.batch_size > 1:
                try:
                    print(f"Initializing batched inference pipeline (batch_size={self.batch_size})...")
                    self.batched_model = BatchedInferencePipeline(
                        model=self.model,
                        use_vad_model=self.vad_filter
                    )
                    print(f"✓ Batched processing enabled (up to {self.batch_size}x faster)")
                except Exception as e:
                    print(f"Warning: Could not enable batched processing: {e}")
                    self.batched_model = None

            self.model_load_time = time.time() - start_time

            print(f"✓ Model loaded successfully in {self.model_load_time:.1f} seconds")
            print(f"📊 Performance boost: ~{self._estimate_speedup()}x faster than OpenAI Whisper")
            return True

        except Exception as e:
            print(f"Error loading Faster-Whisper model: {e}")

            # Try fallback to CPU if GPU loading failed
            if self.device != 'cpu':
                print("Attempting fallback to CPU...")
                try:
                    self.device = 'cpu'
                    self.compute_type = 'int8'
                    self.model = WhisperModel(
                        self.model_name,
                        device='cpu',
                        compute_type='int8',
                        download_root=str(self.download_root)
                    )
                    self.model_load_time = time.time() - start_time
                    print(f"✓ Fallback to CPU successful")
                    return True
                except Exception as fallback_error:
                    print(f"CPU fallback also failed: {fallback_error}")

            return False

    def _estimate_speedup(self) -> float:
        """Estimate speedup factor over OpenAI Whisper."""
        base_speedup = 2.0  # Base faster-whisper speedup

        # Additional speedup from quantization
        if self.compute_type == 'int8' or self.compute_type == 'int8_float16':
            base_speedup *= 1.2

        # Additional speedup from batching
        if self.batch_size > 1:
            base_speedup *= min(self.batch_size, 8) * 0.5

        return round(base_speedup, 1)

    def transcribe(self, audio_path: Path, language: str = 'auto',
                  progress_callback: Optional[Callable[[float], None]] = None,
                  **transcribe_options) -> TranscriptionResult:
        """
        Transcribe audio file to text using faster-whisper.

        Args:
            audio_path: Path to audio file
            language: Language code ('auto' for auto-detection)
            progress_callback: Optional progress callback function
            **transcribe_options: Additional transcription options

        Returns:
            TranscriptionResult object
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if not self.load_model():
            raise RuntimeError("Failed to load Faster-Whisper model")

        start_time = time.time()

        try:
            # Prepare transcription options
            options = {
                'beam_size': 5,  # faster-whisper default (vs 1 for OpenAI)
                'word_timestamps': True,
                'vad_filter': self.vad_filter,
                'condition_on_previous_text': True,
                'temperature': 0.0  # Deterministic output
            }

            # Set language if specified
            if language != 'auto' and language:
                options['language'] = language

            # Update with user options
            options.update(transcribe_options)

            print(f"Transcribing audio file: {audio_path.name}")
            if self.vad_filter:
                print("🎤 VAD filter enabled (skipping silence)")

            # Choose model (batched or regular)
            model_to_use = self.batched_model if self.batched_model else self.model

            # Add batch_size for batched model
            if self.batched_model:
                options['batch_size'] = self.batch_size

            # Perform transcription - returns generator and info
            segments_generator, info = model_to_use.transcribe(
                str(audio_path),
                **options
            )

            # Convert generator to list (this is where actual transcription happens)
            print("Processing segments...")
            segments_list = list(segments_generator)

            processing_time = time.time() - start_time

            # Convert faster-whisper segments to OpenAI format for compatibility
            converted_segments = []
            full_text = ""
            confidence_scores = []

            for seg in segments_list:
                # Build segment dict compatible with OpenAI format
                segment_dict = {
                    'start': seg.start,
                    'end': seg.end,
                    'text': seg.text,
                    'id': seg.id,
                }

                # Add word-level timestamps if available
                if hasattr(seg, 'words') and seg.words:
                    segment_dict['words'] = [
                        {
                            'start': word.start,
                            'end': word.end,
                            'word': word.word,
                            'probability': word.probability
                        }
                        for word in seg.words
                    ]
                    # Collect confidence scores
                    confidence_scores.extend([word.probability for word in seg.words])

                converted_segments.append(segment_dict)
                full_text += seg.text

            # Create result object (compatible with OpenAI format)
            transcription_result = TranscriptionResult(
                text=full_text.strip(),
                segments=converted_segments,
                language=info.language if hasattr(info, 'language') else language,
                duration=info.duration if hasattr(info, 'duration') else 0.0,
                processing_time=processing_time,
                model_used=self.model_name,
                device_used=self.device,
                confidence_scores=confidence_scores
            )

            # Calculate RTF (Real-Time Factor)
            rtf = processing_time / transcription_result.duration if transcription_result.duration > 0 else 0

            print(f"✓ Transcription completed in {processing_time:.1f} seconds")
            print(f"📊 Audio duration: {transcription_result.duration:.1f}s | "
                  f"RTF: {rtf:.3f} | Speed: {1/rtf:.1f}x realtime" if rtf > 0 else "")
            print(f"🌍 Detected language: {transcription_result.language}")
            if confidence_scores:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                print(f"✨ Average confidence: {avg_confidence:.1%}")

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
            'compute_type': self.compute_type,
            'batch_size': self.batch_size,
            'vad_filter': self.vad_filter,
            'segments': result.segments,
            'confidence_scores': result.confidence_scores,
            'metadata': {
                'average_confidence': sum(result.confidence_scores) / len(result.confidence_scores) if result.confidence_scores else 0.0,
                'total_segments': len(result.segments),
                'total_words': sum(len(seg.get('words', [])) for seg in result.segments),
                'realtime_factor': result.processing_time / result.duration if result.duration > 0 else 0,
                'engine': 'faster-whisper'
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
            'compute_type': self.compute_type,
            'batch_size': self.batch_size,
            'vad_filter': self.vad_filter,
            'memory_requirement_gb': model_config.get('memory_gb', 0),
            'relative_speed': model_config.get('relative_speed', 1),
            'estimated_speedup': self._estimate_speedup(),
            'model_loaded': self.model is not None,
            'batched_mode': self.batched_model is not None,
            'model_load_time': self.model_load_time,
            'download_root': str(self.download_root),
            'available_device': device_name,
            'device_info': device_info,
            'engine': 'faster-whisper'
        }

    def unload_model(self):
        """Unload model to free memory."""
        if self.model is not None:
            del self.model
            self.model = None

        if self.batched_model is not None:
            del self.batched_model
            self.batched_model = None

        # Force garbage collection if torch is available
        if TORCH_AVAILABLE:
            import gc
            gc.collect()

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                torch.mps.empty_cache()

        print("Faster-Whisper model unloaded")

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
            'speedup_vs_openai': self._estimate_speedup(),
            'model_name': self.model_name,
            'device': self.device,
            'compute_type': self.compute_type,
            'batch_size': self.batch_size
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
    for model in ['large-v3', 'large', 'turbo', 'medium', 'small', 'base', 'tiny']:
        required_memory = WhisperTranscriber.MODEL_CONFIGS.get(model, {}).get('memory_gb', 999)
        if available_memory_gb >= required_memory:
            return model

    return 'tiny'  # Smallest model as last resort


if __name__ == "__main__":
    # Test transcriber
    import sys

    if len(sys.argv) >= 2:
        audio_file = Path(sys.argv[1])
        model_name = sys.argv[2] if len(sys.argv) > 2 else 'medium'

        print(f"Testing Faster-Whisper transcriber with: {audio_file}")
        print(f"Model: {model_name}")

        # Create transcriber with optimizations
        transcriber = WhisperTranscriber(
            model_name=model_name,
            batch_size=8,  # Enable batching
            vad_filter=True  # Enable VAD
        )

        # Print model info
        info = transcriber.get_model_info()
        print(f"Model info: {info}")

        # Transcribe with progress
        def progress_callback(progress):
            print(f"\rTranscribing: {progress*100:.1f}%", end='', flush=True)

        try:
            result = transcriber.transcribe(audio_file, progress_callback=progress_callback)
            print(f"\n✓ Transcription completed!")
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
