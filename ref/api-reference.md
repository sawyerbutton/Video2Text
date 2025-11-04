# Video2Text API Reference

## Core Modules API

### platform_utils.py

#### `get_system_info() -> dict`
Get comprehensive system information including platform, architecture, and available resources.

**Returns:**
```python
{
    'system': str,          # OS name (Windows/Darwin/Linux)
    'machine': str,         # Architecture (x86_64/arm64)
    'python_version': str,  # Python version
    'architecture': str     # 32bit/64bit
}
```

**Example:**
```python
from core.platform_utils import get_system_info
info = get_system_info()
print(f"Running on {info['system']} {info['machine']}")
```

#### `detect_device() -> str`
Automatically detect the best available processing device.

**Returns:** `'cuda'`, `'mps'`, or `'cpu'`

**Detection Logic:**
1. Check for NVIDIA CUDA GPU
2. Check for Apple Silicon MPS
3. Fallback to CPU

**Example:**
```python
from core.platform_utils import detect_device
device = detect_device()
print(f"Using device: {device}")
```

#### `get_device_info() -> dict`
Get detailed device information and capabilities.

**Returns:**
```python
{
    'recommended_device': str,     # cuda/mps/cpu
    'ffmpeg_available': bool,      # FFmpeg installed
    'ffmpeg_version': str,         # FFmpeg version
    'available_memory_gb': float,  # Available RAM
    'gpu_info': dict              # GPU details (if available)
}
```

#### `get_memory_info() -> dict`
Get system memory statistics.

**Returns:**
```python
{
    'total_gb': float,      # Total system memory
    'available_gb': float,  # Available memory
    'used_gb': float,       # Used memory
    'percent': float        # Usage percentage
}
```

#### `recommend_model(available_memory_gb: float) -> str`
Recommend optimal Whisper model based on available memory.

**Parameters:**
- `available_memory_gb` (float): Available system memory in GB

**Returns:** Model name (`'tiny'`, `'base'`, `'small'`, `'medium'`, `'large'`, `'large-v3'`)

**Recommendations:**
- < 2GB → tiny
- 2-4GB → base
- 4-6GB → small
- 6-10GB → medium
- > 10GB → large or large-v3

### config_manager.py

#### `class ConfigManager`
Manages application configuration from multiple sources.

##### `__init__(config_file: str = None)`
Initialize configuration manager.

**Parameters:**
- `config_file` (str, optional): Path to INI config file

**Example:**
```python
from core.config_manager import ConfigManager
config = ConfigManager('config/config.ini')
```

##### `load_config() -> dict`
Load configuration from file.

**Returns:** Dictionary with configuration sections

##### `get(section: str, key: str, fallback=None) -> Any`
Get configuration value with fallback.

**Parameters:**
- `section` (str): Config section name
- `key` (str): Config key name
- `fallback` (Any): Default value if key not found

**Example:**
```python
model = config.get('PROCESSING', 'model_name', 'medium')
language = config.get('PROCESSING', 'language', 'auto')
```

##### `validate_model(model_name: str) -> bool`
Validate if model name is supported.

**Parameters:**
- `model_name` (str): Model name to validate

**Returns:** `True` if valid, `False` otherwise

**Valid Models:**
- `tiny`, `base`, `small`, `medium`, `large`, `large-v2`, `large-v3`, `turbo`

##### `validate_device(device: str) -> bool`
Validate device name.

**Parameters:**
- `device` (str): Device name to validate

**Returns:** `True` if valid

**Valid Devices:**
- `auto`, `cpu`, `cuda`, `mps`

##### `get_compute_type(device: str) -> str`
Get recommended compute type for device.

**Parameters:**
- `device` (str): Target device

**Returns:** Compute type string

**Device-Specific Defaults:**
- CUDA: `'int8_float16'` (best performance)
- MPS: `'float16'` (Apple Silicon optimized)
- CPU: `'int8'` (memory efficient)

### file_manager.py

#### `class FileManager`
Handles file operations and directory management.

##### `__init__(input_dir: str, output_dir: str, cleanup_temp: bool = True)`
Initialize file manager.

**Parameters:**
- `input_dir` (str): Directory containing video files
- `output_dir` (str): Directory for output text files
- `cleanup_temp` (bool): Auto-cleanup temporary files

##### `scan_video_files() -> list[Path]`
Scan input directory for video files.

**Returns:** List of Path objects for video files

**Supported Extensions:**
`.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`, `.webm`, `.m4v`, `.wmv`, `.3gp`, `.ogv`

**Example:**
```python
from core.file_manager import FileManager
fm = FileManager('videos_todo', 'results')
videos = fm.scan_video_files()
print(f"Found {len(videos)} videos")
```

##### `validate_video_file(file_path: Path) -> bool`
Validate video file format and integrity.

**Parameters:**
- `file_path` (Path): Path to video file

**Returns:** `True` if valid

##### `get_output_path(video_path: Path, format: str = 'txt') -> Path`
Generate output file path for video.

**Parameters:**
- `video_path` (Path): Input video path
- `format` (str): Output format (`'txt'`, `'srt'`, `'vtt'`, `'json'`)

**Returns:** Path object for output file

##### `move_processed_file(video_path: Path, dest_dir: str) -> None`
Move processed video to destination directory.

**Parameters:**
- `video_path` (Path): Video file to move
- `dest_dir` (str): Destination directory

##### `cleanup_temp_files(temp_dir: str = 'temp') -> None`
Remove temporary files.

**Parameters:**
- `temp_dir` (str): Temporary directory path

### audio_processor.py

#### `class AudioProcessor`
Handles audio extraction and processing using FFmpeg.

##### `__init__(ffmpeg_path: str = 'ffmpeg')`
Initialize audio processor.

**Parameters:**
- `ffmpeg_path` (str): Path to FFmpeg executable

##### `extract_audio(video_path: Path, output_path: Path = None, sample_rate: int = 16000, channels: int = 1) -> Path`
Extract audio from video file.

**Parameters:**
- `video_path` (Path): Input video file
- `output_path` (Path, optional): Output audio file path
- `sample_rate` (int): Audio sample rate in Hz (default: 16000)
- `channels` (int): Number of audio channels (default: 1 for mono)

**Returns:** Path to extracted audio file

**Audio Format:** WAV, 16-bit PCM

**Example:**
```python
from core.audio_processor import AudioProcessor
processor = AudioProcessor()
audio_file = processor.extract_audio('video.mp4')
```

##### `extract_audio_with_progress(video_path: Path, callback: callable = None) -> Path`
Extract audio with progress monitoring.

**Parameters:**
- `video_path` (Path): Input video file
- `callback` (callable): Progress callback function `callback(progress: float)`

**Returns:** Path to extracted audio file

##### `normalize_audio(audio_path: Path) -> Path`
Normalize audio levels.

**Parameters:**
- `audio_path` (Path): Audio file to normalize

**Returns:** Path to normalized audio

##### `get_audio_info(video_path: Path) -> dict`
Get audio stream information from video.

**Parameters:**
- `video_path` (Path): Video file path

**Returns:**
```python
{
    'duration': float,      # Duration in seconds
    'sample_rate': int,     # Sample rate in Hz
    'channels': int,        # Number of channels
    'codec': str           # Audio codec name
}
```

### transcriber.py

#### `class Transcriber`
Handles speech-to-text transcription using faster-whisper.

##### `__init__(model_name: str = 'medium', device: str = 'auto', compute_type: str = None, language: str = None)`
Initialize transcriber.

**Parameters:**
- `model_name` (str): Whisper model name
- `device` (str): Processing device (`'auto'`, `'cuda'`, `'mps'`, `'cpu'`)
- `compute_type` (str): Computation precision (see compute types below)
- `language` (str): Audio language code or `'auto'`

**Compute Types:**
- `'int8'` - Fast, memory efficient (CPU/CUDA)
- `'float16'` - Balanced (CUDA/MPS)
- `'int8_float16'` - Best performance (CUDA only)
- `'float32'` - Highest quality, slowest (CPU)

**Example:**
```python
from core.transcriber import Transcriber

# Auto configuration
transcriber = Transcriber()

# Manual configuration
transcriber = Transcriber(
    model_name='large-v3',
    device='cuda',
    compute_type='int8_float16',
    language='zh'
)
```

##### `load_model() -> None`
Load the Whisper model into memory.

**Note:** Called automatically on first transcription if not called explicitly.

##### `transcribe(audio_path: Path, format: str = 'txt', include_timestamps: bool = False) -> str`
Transcribe audio file to text.

**Parameters:**
- `audio_path` (Path): Path to audio file
- `format` (str): Output format (`'txt'`, `'srt'`, `'vtt'`, `'json'`)
- `include_timestamps` (bool): Include timestamp information

**Returns:** Transcribed text string

**Example:**
```python
text = transcriber.transcribe('audio.wav', format='txt')
print(text)
```

##### `transcribe_with_progress(audio_path: Path, callback: callable = None) -> str`
Transcribe with progress monitoring.

**Parameters:**
- `audio_path` (Path): Audio file path
- `callback` (callable): Progress callback `callback(segment: int, total: int)`

**Returns:** Transcribed text

##### `transcribe_batch(audio_paths: list[Path], max_workers: int = 1) -> list[str]`
Transcribe multiple audio files.

**Parameters:**
- `audio_paths` (list[Path]): List of audio file paths
- `max_workers` (int): Number of parallel workers

**Returns:** List of transcribed texts

**Example:**
```python
texts = transcriber.transcribe_batch(
    ['audio1.wav', 'audio2.wav'],
    max_workers=2
)
```

##### `get_model_info() -> dict`
Get information about loaded model.

**Returns:**
```python
{
    'model_name': str,
    'device': str,
    'compute_type': str,
    'language': str,
    'memory_usage_mb': float
}
```

## CLI Interface

### mp4_to_text.py

Main command-line interface for video transcription.

#### Command-Line Arguments

**Input/Output:**
```bash
-i, --input DIR          Input directory with video files (required)
-o, --output DIR         Output directory for text files (required)
```

**Model Configuration:**
```bash
-m, --model NAME         Whisper model (default: medium)
                        Options: tiny, base, small, medium, large,
                                large-v2, large-v3, turbo
-l, --language CODE      Language code (default: auto)
                        Examples: en, zh, ja, ko, fr, de, es, ru
-d, --device DEVICE      Processing device (default: auto)
                        Options: auto, cpu, cuda, mps
--compute-type TYPE      Compute precision
                        Options: int8, float16, int8_float16, float32
```

**Processing Options:**
```bash
-w, --workers NUM        Number of parallel workers (default: 1)
-s, --skip-existing      Skip already processed files
--timeout SECONDS        Processing timeout per file
```

**Output Options:**
```bash
-f, --format FORMAT      Output format (default: txt)
                        Options: txt, srt, vtt, json
--timestamps            Include timestamps in output
--word-timestamps       Include word-level timestamps
```

**Audio Options:**
```bash
--sample-rate RATE      Audio sample rate (default: 16000)
--normalize-audio       Normalize audio levels
```

**Behavior:**
```bash
--cleanup-temp          Remove temporary files (default: true)
--no-cleanup            Keep temporary files
--move-processed        Move processed videos to done folder
```

**Information:**
```bash
--system-info           Display system information and exit
--list-models           List available models and exit
--version               Show version information
-h, --help              Show help message
```

#### Usage Examples

**Basic Usage:**
```bash
python mp4_to_text.py -i videos_todo -o results
```

**High Quality Transcription:**
```bash
python mp4_to_text.py -i videos -o texts \
    -m large-v3 \
    -l zh \
    -d cuda \
    --compute-type int8_float16
```

**Batch Processing:**
```bash
python mp4_to_text.py -i videos -o texts \
    -w 2 \
    --skip-existing \
    --move-processed
```

**SRT Subtitle Generation:**
```bash
python mp4_to_text.py -i videos -o subtitles \
    -f srt \
    --timestamps
```

## Automation Tools

### auto_process.py

Automated video processing with smart defaults.

**Usage:**
```bash
python tools/auto_process.py [OPTIONS]
```

**Key Features:**
- Automatically processes videos_todo/ directory
- Moves processed files to videos_done/
- Saves results to results/ directory
- Chinese interface with detailed progress

**Options:**
```bash
-m, --model NAME         Model name (default: medium)
-l, --language CODE      Language (default: auto)
-d, --device DEVICE      Device (default: auto)
-w, --workers NUM        Parallel workers (default: 1)
-s, --skip-existing      Skip processed files
--no-move               Don't move processed files
-v, --verbose           Verbose output
-q, --quiet             Quiet mode
```

### auto_process_large.py

Smart processing for large video files (150MB+).

**Usage:**
```bash
python tools/auto_process_large.py
```

**Size-Based Strategies:**
- SMALL (150-200MB): base model, 30min timeout
- MEDIUM (200-300MB): base model, 45min timeout
- LARGE (300-500MB): tiny model, 60min timeout
- HUGE (>500MB): tiny model, 120min timeout

**Interactive Mode:**
User can select processing level based on file sizes found.

## Configuration Files

### config/config.ini

INI-format configuration file.

**Sections:**

**[PROCESSING]**
```ini
model_name = medium          # Whisper model
language = auto             # Language code
device = auto               # Processing device
compute_type = auto         # Computation type
max_workers = 1             # Parallel workers
skip_existing = true        # Skip processed files
cleanup_temp = true         # Cleanup temp files
timeout = 3600              # Timeout in seconds
```

**[AUDIO]**
```ini
format = wav                # Audio format
sample_rate = 16000         # Sample rate (Hz)
channels = 1                # Audio channels
normalize_audio = false     # Normalize levels
```

**[OUTPUT]**
```ini
format = txt                # Output format
include_timestamps = false  # Add timestamps
word_level_timestamps = false  # Word timestamps
move_processed = false      # Move processed files
processed_dir = videos_done # Processed file destination
```

**[LOGGING]**
```ini
level = INFO                # Log level
file = logs/mp4_to_text.log # Log file path
console_output = true       # Console logging
```

### config/models.json

Model specifications and device recommendations.

**Structure:**
```json
{
  "whisper_models": {
    "model_name": {
      "size_mb": 142,
      "memory_requirement_gb": 2,
      "speed": "fast",
      "accuracy": "medium",
      "recommended_for": "日常使用",
      "description": "平衡速度和准确性"
    }
  },
  "supported_languages": {...},
  "device_recommendations": {...},
  "compute_types": {...}
}
```

## Return Codes

### Exit Codes

- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - Missing dependencies
- `4` - File not found
- `5` - Processing error
- `6` - Model loading error
- `7` - Audio extraction error
- `8` - Transcription error

## Error Handling

### Common Exceptions

**`FileNotFoundError`**
- Raised when input files/directories don't exist
- Handle by checking paths before processing

**`ValueError`**
- Invalid configuration values
- Invalid model or device names

**`RuntimeError`**
- Model loading failures
- Processing errors
- Device initialization errors

**`TimeoutError`**
- Processing exceeds timeout limit
- Can be configured via `--timeout` option

### Error Recovery

All modules implement graceful error handling:
- Automatic fallback to CPU if GPU fails
- Skip corrupted files and continue batch
- Cleanup resources on error
- Detailed error messages for debugging

## Performance Optimization

### Best Practices

1. **Use appropriate model for your needs:**
   - Quick tests: tiny/base
   - Production: medium/turbo
   - High quality: large-v3

2. **Enable GPU acceleration:**
   ```python
   transcriber = Transcriber(device='cuda', compute_type='int8_float16')
   ```

3. **Use INT8 quantization for speed:**
   ```python
   transcriber = Transcriber(compute_type='int8')
   ```

4. **Batch processing for multiple files:**
   ```python
   texts = transcriber.transcribe_batch(audio_files, max_workers=2)
   ```

5. **Specify language when known:**
   ```python
   transcriber = Transcriber(language='zh')  # Faster than auto-detect
   ```

## Version History

**v1.0.0** - Initial release with faster-whisper
- Migration from OpenAI Whisper to faster-whisper
- 2-8x performance improvement
- INT8 quantization support
- Enhanced cross-platform support
