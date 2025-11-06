# Video2Text - Claude Code Reference

## Project Overview

Video2Text is a cross-platform video-to-text transcription tool using faster-whisper for high-quality speech recognition. The project provides 2-8x performance improvements over the original OpenAI Whisper implementation.

**Status:** Production Ready (v1.0.0)
**Lines of Code:** ~3,845 Python lines
**Language:** Python 3.9+
**License:** MIT

## Quick Links

### Essential Documentation

- **[README.md](README.md)** - User guide and getting started
- **[Architecture Reference](ref/architecture.md)** - System design and module documentation
- **[API Reference](ref/api-reference.md)** - Complete API documentation
- **[Model Reference](ref/models.md)** - Whisper model specifications and selection guide
- **[Workflow Guide](ref/workflows.md)** - Common usage patterns and workflows

### Project Documentation

- **[docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** - Project completion summary
- **[docs/AUTO_PROCESS_README.md](docs/AUTO_PROCESS_README.md)** - Automated processing guide
- **[tools/README.md](tools/README.md)** - Tools and utilities documentation

### Configuration

- **[config/config.ini](config/config.ini)** - Main configuration file
- **[config/models.json](config/models.json)** - Model specifications database
- **[requirements.txt](requirements.txt)** - Python dependencies

## Project Structure

```
Video2Text/
├── core/                      # Core functionality modules (2,279 lines)
│   ├── platform_utils.py     # Platform/hardware detection (246 lines)
│   ├── config_manager.py     # Configuration management (430 lines)
│   ├── file_manager.py       # File operations (462 lines)
│   ├── audio_processor.py    # Audio extraction (429 lines)
│   └── transcriber.py        # Transcription engine (692 lines)
│
├── tools/                     # Utility scripts (942 lines)
│   ├── auto_process.py       # Standard automation (313 lines)
│   ├── auto_process_large.py # Large file handler (379 lines)
│   └── quick_check.py        # System diagnostics (250 lines)
│
├── config/                    # Configuration files
│   ├── config.ini            # Main configuration
│   └── models.json           # Model specifications
│
├── docs/                      # Documentation
│   ├── PROJECT_SUMMARY.md    # Project overview
│   ├── AUTO_PROCESS_README.md # Auto-process guide
│   └── README.md             # Documentation index
│
├── ref/                       # Reference documentation (Claude Code)
│   ├── architecture.md       # System architecture
│   ├── api-reference.md      # API documentation
│   ├── models.md             # Model specifications
│   └── workflows.md          # Usage workflows
│
├── examples/                  # Usage examples
├── tests/                     # Test suite
│
├── mp4_to_text.py            # Main CLI script (624 lines)
├── run_auto_process.py       # Auto-process launcher
├── run_large_process.py      # Large file launcher
└── setup.py                  # Installation script
```

## Key Features

### Core Capabilities

1. **Cross-Platform Support**
   - Windows, macOS, Linux
   - Automatic GPU detection (CUDA/MPS)
   - CPU fallback support

2. **Performance Optimizations**
   - faster-whisper: 2-8x speed improvement
   - INT8 quantization: 62% memory reduction
   - GPU acceleration support
   - Parallel batch processing

3. **Multiple Models**
   - tiny, base, small, medium, large, large-v3, turbo
   - Auto-download and caching
   - Device-specific optimization

4. **Flexible Output**
   - TXT, SRT, VTT, JSON formats
   - Timestamp support
   - Word-level timing

5. **Automation Tools**
   - One-click batch processing
   - Smart large file handling
   - Automatic file management

## Technology Stack

### Core Dependencies

- **faster-whisper** >= 1.0.0 - Speech recognition engine
- **PyTorch** >= 2.0.0 - Deep learning framework
- **FFmpeg** (external) - Audio/video processing
- **ffmpeg-python** >= 0.2.0 - FFmpeg Python wrapper
- **torchaudio** >= 2.0.0 - Audio processing

### Supporting Libraries

- **tqdm** - Progress bars
- **colorama** - Cross-platform colored output
- **pathvalidate** - Path validation
- **configparser** - Configuration management
- **argparse** - CLI argument parsing

## Architecture Overview

### Processing Pipeline

```
Video Input → Audio Extraction → Transcription → Text Output
     ↓              ↓                   ↓              ↓
File Manager → Audio Processor → Transcriber → File Manager
     ↓              ↓                   ↓              ↓
Validation    FFmpeg (16kHz)    faster-whisper    Save Results
```

### Core Modules

1. **platform_utils.py** (246 lines)
   - Hardware detection
   - System resource monitoring
   - Device recommendations

2. **config_manager.py** (430 lines)
   - Configuration loading
   - Validation
   - Default management

3. **file_manager.py** (462 lines)
   - File discovery
   - Path management
   - Cleanup operations

4. **audio_processor.py** (429 lines)
   - FFmpeg integration
   - Audio extraction
   - Format conversion

5. **transcriber.py** (692 lines)
   - Model loading
   - Transcription engine
   - Output formatting

## Common Tasks for Claude Code

### Understanding the Codebase

**When asked about project structure:**
→ Reference [ref/architecture.md](ref/architecture.md)

**When asked about API usage:**
→ Reference [ref/api-reference.md](ref/api-reference.md)

**When asked about model selection:**
→ Reference [ref/models.md](ref/models.md)

**When asked about workflows:**
→ Reference [ref/workflows.md](ref/workflows.md)

### Key Code Locations

**Main entry point:**
- `mp4_to_text.py:624` - CLI interface

**Core processing:**
- `core/transcriber.py:1-692` - Transcription logic
- `core/audio_processor.py:1-429` - Audio extraction

**Platform detection:**
- `core/platform_utils.py:1-246` - Device detection

**Configuration:**
- `core/config_manager.py:1-430` - Config handling

**File operations:**
- `core/file_manager.py:1-462` - File management

### Important Functions

**Device Detection:**
```python
# core/platform_utils.py
detect_device() -> str  # Returns 'cuda', 'mps', or 'cpu'
get_device_info() -> dict
recommend_model(memory_gb: float) -> str
```

**Audio Processing:**
```python
# core/audio_processor.py
extract_audio(video_path, output_path, sample_rate, channels) -> Path
extract_audio_with_progress(video_path, callback) -> Path
```

**Transcription:**
```python
# core/transcriber.py
transcribe(audio_path, format, include_timestamps) -> str
transcribe_batch(audio_paths, max_workers) -> list[str]
```

## Configuration Files

### config/config.ini

Main configuration with sections:
- `[PROCESSING]` - Model, device, language settings
- `[AUDIO]` - Audio extraction parameters
- `[OUTPUT]` - Output format and options
- `[LOGGING]` - Log configuration

### config/models.json

Comprehensive model database including:
- Model specifications (size, memory, speed)
- Language support
- Device recommendations
- Compute type options

## Development Guidelines

### Code Standards

1. **Python Style:**
   - Follow PEP 8
   - Type hints where applicable
   - Docstrings for public functions

2. **Error Handling:**
   - Graceful degradation (GPU → CPU)
   - Detailed error messages
   - Proper resource cleanup

3. **Cross-Platform:**
   - Use `pathlib` for paths
   - Platform-specific code in `platform_utils.py`
   - Test on Windows/macOS/Linux

### Testing

**Test files:**
- `tests/test_platform_utils.py`
- `tests/test_config_manager.py`
- `tests/test_file_manager.py`

**Run tests:**
```bash
pytest tests/
```

**Quick system check:**
```bash
python tools/quick_check.py
```

## Recent Changes

### faster-whisper Migration

**Date:** 2024-11 (Commit: 7357135)

**Key Changes:**
- Migrated from `openai-whisper` to `faster-whisper`
- 2-8x performance improvement
- Added compute type selection (int8, float16, int8_float16)
- Updated model recommendations
- Enhanced device-specific optimizations

**Impact:**
- Faster processing across all devices
- Lower memory usage with INT8
- Better production readiness
- Maintained API compatibility

### Project Restructuring

**Date:** 2024-11 (Commit: c19c8a1)

**Changes:**
- Separated tools into `tools/` directory
- Moved documentation to `docs/`
- Added convenience launchers (`run_*.py`)
- Improved directory organization

## Git Workflow

**Current Branch:** `faster-whisper-migration`
**Main Branch:** `main`

**Recent Commits:**
```
7357135 - 迁移到 faster-whisper：2-8倍性能提升
c19c8a1 - 项目结构重构：分离工具和文档，优化用户体验
372a47c - 项目优化完成：简化音频处理、添加大文件智能处理、更新文档
```

## Command Reference

### Quick Commands

**Check system:**
```bash
python mp4_to_text.py --system-info
```

**List models:**
```bash
python mp4_to_text.py --list-models
```

**Basic processing:**
```bash
python mp4_to_text.py -i videos_todo -o results
```

**Automated processing:**
```bash
python run_auto_process.py
```

**Large file processing:**
```bash
python run_large_process.py
```

**Run tests:**
```bash
python tests/run_tests.py
```

## Debugging Tips

### Common Issues

1. **GPU not detected:**
   - Check: `python -c "import torch; print(torch.cuda.is_available())"`
   - Force CPU: `-d cpu`

2. **Out of memory:**
   - Use smaller model: `-m tiny` or `-m base`
   - Enable INT8: `--compute-type int8`

3. **Slow processing:**
   - Enable GPU: `-d cuda` or `-d mps`
   - Use turbo model: `-m turbo`

4. **Audio extraction fails:**
   - Check FFmpeg: `ffmpeg -version`
   - Verify video file integrity

### Verbose Logging

**Enable detailed logging:**
```bash
python mp4_to_text.py -i videos -o texts --verbose
```

**Check logs:**
```bash
cat logs/mp4_to_text.log
```

## Performance Benchmarks

### Model Speed (GPU CUDA)

| Model | RTF | Processing Speed |
|-------|-----|------------------|
| tiny | 0.005 | 200x real-time |
| base | 0.01 | 100x real-time |
| medium | 0.02 | 50x real-time |
| large-v3 | 0.03 | 33x real-time |
| turbo | 0.01 | 100x real-time |

### Memory Usage

| Model | float32 | float16 | int8 |
|-------|---------|---------|------|
| tiny | 200% | 100% | 62% |
| base | 200% | 100% | 62% |
| medium | 200% | 100% | 62% |
| large-v3 | 200% | 100% | 62% |

*Percentages relative to float16 baseline*

## Support and Resources

### Getting Help

1. **Check documentation:**
   - README.md for user guide
   - ref/ directory for technical reference

2. **Run diagnostics:**
   ```bash
   python tools/quick_check.py
   ```

3. **Check system info:**
   ```bash
   python mp4_to_text.py --system-info
   ```

### External Resources

- **faster-whisper:** https://github.com/guillaumekln/faster-whisper
- **OpenAI Whisper:** https://github.com/openai/whisper
- **FFmpeg:** https://ffmpeg.org/
- **PyTorch:** https://pytorch.org/

## Version Information

**Current Version:** 1.0.0
**Python Required:** 3.9+
**Platform:** Cross-platform (Windows/macOS/Linux)
**License:** MIT

---

## For Claude Code: Quick Reference

### When User Asks About...

**"How does this project work?"**
→ Explain: Video → Audio extraction (FFmpeg) → Transcription (faster-whisper) → Text output
→ Reference: [ref/architecture.md](ref/architecture.md)

**"How do I use this?"**
→ Quick start: `python run_auto_process.py`
→ Reference: [README.md](README.md), [ref/workflows.md](ref/workflows.md)

**"Which model should I use?"**
→ Default: `medium` (balanced)
→ Fast: `turbo` or `base`
→ Quality: `large-v3`
→ Reference: [ref/models.md](ref/models.md)

**"How to make it faster?"**
→ Use GPU: `-d cuda` or `-d mps`
→ Use INT8: `--compute-type int8_float16`
→ Use turbo model: `-m turbo`

**"API documentation?"**
→ Reference: [ref/api-reference.md](ref/api-reference.md)

**"How to integrate this?"**
→ Reference: [ref/workflows.md](ref/workflows.md) (Integration Workflows section)

### Key Files to Read

**For architecture understanding:**
- `core/__init__.py` - Module overview
- `mp4_to_text.py` - Main entry point

**For specific functionality:**
- `core/transcriber.py` - Transcription logic
- `core/audio_processor.py` - Audio extraction
- `core/platform_utils.py` - Device detection

**For configuration:**
- `config/config.ini` - Default configuration
- `config/models.json` - Model specifications

### Common Code Patterns

**Initialize transcriber:**
```python
from core.transcriber import Transcriber
transcriber = Transcriber(model_name='medium', device='auto')
```

**Process video:**
```python
from core.audio_processor import AudioProcessor
from core.transcriber import Transcriber

audio_proc = AudioProcessor()
transcriber = Transcriber()

audio_file = audio_proc.extract_audio('video.mp4')
text = transcriber.transcribe(audio_file)
```

**Batch processing:**
```python
transcriber = Transcriber(device='cuda')
texts = transcriber.transcribe_batch(audio_files, max_workers=2)
```

---

*Last Updated: 2024-11 (faster-whisper migration complete)*
