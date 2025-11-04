# Video2Text Architecture Reference

## Overview

Video2Text is a cross-platform video-to-text transcription tool using faster-whisper (previously OpenAI Whisper) for high-quality speech recognition. The project follows a modular architecture with clear separation of concerns.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ CLI Scripts  │  │ Auto Process │  │  Large Process   │  │
│  │mp4_to_text.py│  │    Tools     │  │     Tools        │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             │
┌─────────────────────────────────────────────────────────────┐
│                      Core Module Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Platform   │  │    Config    │  │   File Manager   │  │
│  │    Utils     │  │   Manager    │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │    Audio     │  │ Transcriber  │                        │
│  │  Processor   │  │   (Whisper)  │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                             │
┌─────────────────────────────────────────────────────────────┐
│                   External Dependencies                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │faster-whisper│  │    FFmpeg    │  │    PyTorch       │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Modules

### 1. Platform Utils (`core/platform_utils.py`)
**Lines:** 246
**Purpose:** Cross-platform hardware detection and system information

**Key Functions:**
- Auto-detect GPU (CUDA/MPS) and CPU capabilities
- System resource monitoring (memory, disk space)
- Platform-specific optimizations
- Device recommendation based on available hardware

**Supported Platforms:**
- Windows (CUDA GPU detection)
- macOS (Apple Silicon MPS detection)
- Linux (CUDA GPU detection)

### 2. Config Manager (`core/config_manager.py`)
**Lines:** 430
**Purpose:** Configuration management and validation

**Key Features:**
- INI-based configuration files
- Command-line argument parsing
- Model and device validation
- Default value management
- Configuration priority: CLI args > config file > defaults

**Configuration Sections:**
- `[PROCESSING]` - Model, device, workers, language
- `[AUDIO]` - Audio extraction settings
- `[OUTPUT]` - Output format and timestamps
- `[LOGGING]` - Log levels and file locations

### 3. File Manager (`core/file_manager.py`)
**Lines:** 462
**Purpose:** File and directory operations

**Key Functions:**
- Cross-platform path handling (using pathlib)
- Video file discovery and validation
- Output file management
- Temporary file cleanup
- File moving and archiving

**Supported Video Formats:**
MP4, AVI, MOV, MKV, FLV, WebM, M4V, WMV, 3GP, OGV

**Output Formats:**
TXT, SRT, VTT, JSON

### 4. Audio Processor (`core/audio_processor.py`)
**Lines:** 429
**Purpose:** Audio extraction and processing

**Key Features:**
- FFmpeg-based audio extraction
- Progress monitoring during extraction
- Audio format conversion (WAV, 16kHz mono)
- Audio normalization (optional)
- Batch audio processing

**Performance:**
- Typical extraction time: 1-3 seconds per file
- Optimized FFmpeg parameters for speed

### 5. Transcriber (`core/transcriber.py`)
**Lines:** 692
**Purpose:** Speech-to-text transcription using faster-whisper

**Key Features:**
- faster-whisper integration (2-8x faster than original Whisper)
- Multi-model support (tiny, base, small, medium, large, large-v3, turbo)
- GPU acceleration (CUDA/MPS)
- Compute type optimization (int8, float16, int8_float16)
- Real-time progress tracking
- Multiple output formats
- Batch processing with parallel workers

**Performance Improvements:**
- GPU: 2-8x faster than CPU
- INT8 quantization: 62% memory usage
- faster-whisper: 2-8x faster than original Whisper

## Data Flow

### Standard Processing Flow

```
1. User Input
   ├─> Video files placed in videos_todo/
   └─> Command line arguments

2. Configuration Loading
   ├─> CLI arguments parsed
   ├─> Config file loaded (config/config.ini)
   └─> Defaults applied

3. System Detection
   ├─> Platform identified (Windows/macOS/Linux)
   ├─> GPU detected (CUDA/MPS/none)
   ├─> Memory and resources checked
   └─> Optimal device selected

4. File Discovery
   ├─> Scan videos_todo/ directory
   ├─> Validate video files
   └─> Filter already-processed files (optional)

5. Model Loading
   ├─> Download model if needed
   ├─> Load with optimal compute type
   └─> Initialize on selected device

6. Processing Loop (for each video)
   ├─> Extract audio (FFmpeg)
   │   └─> Convert to 16kHz mono WAV
   ├─> Transcribe audio (faster-whisper)
   │   ├─> Load audio
   │   ├─> Process with model
   │   └─> Generate text output
   └─> Save results
       ├─> Save to results/ directory
       └─> Move video to videos_done/

7. Cleanup
   ├─> Remove temporary audio files
   ├─> Generate processing report
   └─> Display statistics
```

## Directory Structure

```
Video2Text/
├── core/                      # Core functionality modules
│   ├── __init__.py           # Package initialization (20 lines)
│   ├── platform_utils.py     # Platform detection (246 lines)
│   ├── config_manager.py     # Configuration (430 lines)
│   ├── file_manager.py       # File operations (462 lines)
│   ├── audio_processor.py    # Audio extraction (429 lines)
│   └── transcriber.py        # Transcription engine (692 lines)
│
├── tools/                     # Utility scripts
│   ├── auto_process.py       # Standard automation (313 lines)
│   ├── auto_process_large.py # Large file handler (379 lines)
│   ├── quick_check.py        # System diagnostics (250 lines)
│   ├── process_videos.bat    # Windows batch script
│   └── process_videos.sh     # Linux/macOS shell script
│
├── config/                    # Configuration files
│   ├── config.ini            # Main configuration
│   └── models.json           # Model specifications
│
├── docs/                      # Project documentation
│   ├── PROJECT_SUMMARY.md    # Project overview
│   ├── AUTO_PROCESS_README.md # Auto-process guide
│   └── README.md             # Documentation index
│
├── examples/                  # Usage examples
│   └── usage_examples.py     # Example scripts
│
├── tests/                     # Test suite
│   ├── test_platform_utils.py
│   ├── test_config_manager.py
│   └── test_file_manager.py
│
├── ref/                       # Reference documentation
│   ├── architecture.md       # This file
│   ├── api-reference.md      # API documentation
│   ├── models.md             # Model specifications
│   └── workflows.md          # Usage workflows
│
├── videos_todo/              # Input directory (user-created)
├── videos_large/             # Large file input (user-created)
├── videos_done/              # Processed videos (auto-created)
├── results/                  # Output texts (auto-created)
│
├── mp4_to_text.py            # Main CLI script (624 lines)
├── run_auto_process.py       # Auto-process launcher
├── run_large_process.py      # Large file launcher
├── requirements.txt          # Python dependencies
├── setup.py                  # Installation script
└── README.md                 # Main documentation
```

## Technology Stack

### Core Technologies
- **Python**: 3.9+ (primary language)
- **faster-whisper**: 1.0.0+ (2-8x faster than original Whisper)
- **PyTorch**: 2.0.0+ (deep learning framework)
- **FFmpeg**: External dependency (audio/video processing)

### Key Libraries
- **ffmpeg-python**: Python FFmpeg wrapper
- **torchaudio**: Audio processing for PyTorch
- **tqdm**: Progress bars
- **colorama**: Cross-platform colored output
- **pathvalidate**: Cross-platform path validation
- **configparser**: Configuration file parsing
- **argparse**: Command-line argument parsing

### Platform-Specific
- **pywin32** (Windows): Windows API access
- **pyobjc** (macOS): macOS API access

## Performance Characteristics

### faster-whisper Performance Improvements

#### Speed Comparison (vs. original Whisper)
- **CUDA GPU**: 2-8x faster
- **Apple Silicon MPS**: 2-4x faster
- **CPU with INT8**: 2-4x faster

#### Memory Usage with Quantization
- **float32**: 200% (baseline)
- **float16**: 100% (50% reduction)
- **int8**: 62% (38% reduction)
- **int8_float16**: 62% with better quality

### Model Performance

| Model | Size | Memory | Speed | RTF* | Use Case |
|-------|------|--------|-------|------|----------|
| tiny | 39MB | 1GB | Very Fast | 0.01 | Quick testing |
| base | 142MB | 2GB | Fast | 0.02 | Daily use |
| small | 244MB | 3GB | Medium | 0.03 | Balanced |
| medium | 769MB | 5GB | Medium | 0.05 | Recommended |
| large | 1550MB | 8GB | Slow | 0.08 | High quality |
| large-v3 | 1550MB | 10GB | Slow | 0.08 | Best quality |
| turbo | 809MB | 6GB | Very Fast | 0.02 | Production |

*RTF = Real-Time Factor (lower is faster)

### Processing Time Estimates

#### With GPU (CUDA/MPS)
- Small files (<100MB): 30-60 seconds
- Medium files (100-300MB): 1-3 minutes
- Large files (300MB-1GB): 3-10 minutes

#### CPU Only
- Small files: 1-2 minutes
- Medium files: 3-8 minutes
- Large files: 10-30 minutes

## Design Patterns

### 1. Modular Architecture
Each core module has a single, well-defined responsibility following SOLID principles.

### 2. Configuration Hierarchy
CLI args → Config file → Defaults (with proper precedence)

### 3. Cross-Platform Abstraction
Platform-specific code isolated in `platform_utils.py`

### 4. Resource Management
Automatic cleanup of temporary files and proper error handling

### 5. Progress Feedback
Real-time progress bars and detailed logging throughout processing

## Extension Points

### Adding New Models
1. Update `config/models.json` with model specifications
2. faster-whisper automatically supports all Whisper model variants

### Adding New Output Formats
1. Extend `transcriber.py` output formatting methods
2. Update `file_manager.py` for new file extensions

### Adding New Platforms
1. Add detection logic in `platform_utils.py`
2. Update platform-specific dependencies in `setup.py`

### Custom Processing Pipelines
1. Extend `audio_processor.py` for custom audio preprocessing
2. Extend `transcriber.py` for custom post-processing

## Migration Notes: OpenAI Whisper → faster-whisper

### Key Changes
- **Package**: `openai-whisper` → `faster-whisper`
- **Performance**: 2-8x faster processing
- **Memory**: More efficient with INT8 quantization
- **API**: Similar but optimized for CTranslate2 backend

### Benefits
1. Significant speed improvements (2-8x)
2. Lower memory usage with quantization
3. Better production readiness
4. Maintained API compatibility

### Configuration Updates
- Added compute type selection (int8, float16, int8_float16)
- Enhanced device-specific optimizations
- Updated model recommendations in `config/models.json`

## Security Considerations

### File Validation
- Video file format validation
- Path traversal prevention (using pathvalidate)
- File size limits configurable

### Temporary Files
- Automatic cleanup after processing
- Configurable temp directory location
- Secure file permissions

### Error Handling
- Graceful degradation on GPU failure
- Proper exception handling throughout
- Detailed error messages for debugging

## Future Architecture Considerations

### Potential Enhancements
1. Web API interface (REST/GraphQL)
2. Database integration for batch management
3. Distributed processing across multiple machines
4. Real-time streaming transcription
5. Custom model fine-tuning support
6. Plugin architecture for extensibility

### Scalability
- Current design supports single-machine processing
- Can be extended to distributed systems
- Batch processing already optimized
- Resource management allows for long-running operations
