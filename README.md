# MP4ToText - Video to Text Transcription Tool

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Cross Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/your-username/Video2Text)

A powerful, cross-platform tool for batch processing video files and extracting text using OpenAI Whisper. Supports GPU/CPU auto-detection and multi-platform compatibility.

## ✨ Features

- 🎥 **Batch Video Processing** - Process multiple MP4/AVI/MOV/MKV files at once
- 🎙️ **High-Quality Transcription** - Powered by OpenAI Whisper for accurate speech-to-text
- 🔧 **Cross-Platform** - Runs on Windows, macOS, and Linux
- 🚀 **GPU/CPU Auto-Detection** - Automatically uses CUDA, MPS (Apple Silicon), or CPU
- 📊 **Multiple Output Formats** - TXT, SRT, VTT, and JSON output formats
- ⚡ **Parallel Processing** - Multi-threaded processing for faster batch operations
- 🎛️ **Configurable** - Extensive configuration options via CLI or config files
- 📈 **Progress Tracking** - Real-time progress indicators and detailed statistics

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/Video2Text.git
cd Video2Text
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install FFmpeg**
- **Windows**: Download from [FFmpeg website](https://ffmpeg.org/) or `choco install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)

### Basic Usage

```bash
# Basic transcription
python mp4_to_text.py -i ./input_videos -o ./output_texts

# Use specific model and language
python mp4_to_text.py -i ./videos -o ./texts -m large-v3 -l zh

# Parallel processing with 2 workers
python mp4_to_text.py -i ./videos -o ./texts -w 2 --skip-existing
```

## 📋 System Requirements

- **Python**: 3.9 or higher
- **FFmpeg**: Latest version
- **Memory**: 2GB+ (depends on Whisper model)
- **Storage**: Sufficient space for video files and transcripts
- **GPU** (optional): NVIDIA CUDA or Apple Silicon for faster processing

## 🎛️ Command Line Options

```bash
python mp4_to_text.py [OPTIONS]

Required Arguments:
  -i, --input DIR          Input directory containing video files
  -o, --output DIR         Output directory for text files

Model Options:
  -m, --model MODEL        Whisper model (tiny/base/small/medium/large/large-v3)
  -l, --language LANG      Audio language (auto/zh/en/ja/ko/fr/de/es/ru/pt/it/ar/hi)
  -d, --device DEVICE      Device to use (auto/cpu/cuda/mps)

Processing Options:
  -w, --workers NUM        Number of parallel workers (default: 1)
  -s, --skip-existing      Skip already processed files
  --no-cleanup             Keep temporary files

Configuration:
  -c, --config FILE        Configuration file path

Output Control:
  -v, --verbose            Verbose output
  -q, --quiet              Quiet mode

Information:
  --system-info            Show system information
  --list-models            List available models
  --help                   Show help message
```

## 🔧 Configuration

### Configuration File

Create a `config.ini` file for persistent settings:

```ini
[PROCESSING]
model_name = medium
language = auto
device = auto
max_workers = 1
skip_existing = false
cleanup_temp = true

[AUDIO]
format = wav
sample_rate = 16000
channels = 1
quality = high

[LOGGING]
level = INFO
file = logs/mp4_to_text.log
console_output = true
```

### Whisper Models

| Model | Size | Memory | Speed | Accuracy | Best For |
|-------|------|--------|-------|----------|----------|
| tiny | 39MB | 1GB | Very Fast | Low | Quick testing |
| base | 142MB | 2GB | Fast | Medium | General use |
| small | 244MB | 3GB | Medium | Good | Balanced performance |
| medium | 769MB | 5GB | Medium | High | **Recommended** |
| large | 1550MB | 8GB | Slow | Very High | High quality |
| large-v3 | 1550MB | 10GB | Slow | Very High | Latest & best |

## 🖥️ Platform-Specific Usage

### Windows
```cmd
# Standard usage
python mp4_to_text.py -i "C:\Videos" -o "C:\Transcripts"

# With GPU acceleration
python mp4_to_text.py -i "C:\Videos" -o "C:\Transcripts" -d cuda
```

### macOS
```bash
# Standard usage
python mp4_to_text.py -i ~/Videos -o ~/Documents/Transcripts

# With Apple Silicon GPU
python mp4_to_text.py -i ~/Videos -o ~/Documents/Transcripts -d mps
```

### Linux
```bash
# Standard usage
python mp4_to_text.py -i /home/user/Videos -o /home/user/Transcripts

# With NVIDIA GPU
python mp4_to_text.py -i /home/user/Videos -o /home/user/Transcripts -d cuda
```

## 🚀 Performance Optimization

### GPU Acceleration

**NVIDIA CUDA**
- Requires NVIDIA GPU with CUDA support
- Install CUDA toolkit and cuDNN
- Automatically detected when using `-d auto`

**Apple Silicon (MPS)**
- Available on M1/M2/M3 Macs
- Automatically detected on Apple Silicon
- Use `-d mps` to force MPS usage

### Memory Optimization

- Use smaller models for limited memory systems
- Reduce parallel workers if running out of memory
- Enable `cleanup_temp = true` to save disk space

### Processing Speed

- **Fast**: Use `tiny` or `base` models
- **Balanced**: Use `medium` model (recommended)
- **Quality**: Use `large-v3` model with GPU

## 📁 Supported Formats

**Input Video Formats:**
- MP4, AVI, MOV, MKV, FLV, WebM, M4V, WMV, 3GP, OGV

**Output Text Formats:**
- TXT (plain text)
- SRT (subtitle format)
- VTT (WebVTT format)
- JSON (detailed format with metadata)

## 🔍 Troubleshooting

### Common Issues

**FFmpeg not found**
```bash
# Check FFmpeg installation
ffmpeg -version

# Install FFmpeg if missing
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

**CUDA issues**
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Force CPU usage if GPU issues
python mp4_to_text.py -i ./videos -o ./texts -d cpu
```

**Memory issues**
```bash
# Use smaller model
python mp4_to_text.py -i ./videos -o ./texts -m tiny

# Reduce workers
python mp4_to_text.py -i ./videos -o ./texts -w 1
```

### Debug Commands

```bash
# Check system compatibility
python mp4_to_text.py --system-info

# List available models
python mp4_to_text.py --list-models

# Verbose logging
python mp4_to_text.py -i ./videos -o ./texts --verbose
```

## 📊 Example Output

```
===========================================================
           MP4ToText - Video Transcription Tool
===========================================================

System Information:
  Platform: Darwin
  Device: mps
  Model: medium
  Language: auto

✓ Setup validation successful
✓ Model loaded successfully
Found 5 video files to process

Processing Plan:
  Files to process: 5
  Max workers: 1
  Skip existing: false

Processing: video1.mp4
  Duration: 180.5s
  Extracting audio...
  Transcribing audio...
✓ Completed in 45.2s (RTF: 0.25)
  Output: ./output/video1.txt
  Text length: 2847 characters
  Detected language: en

===========================================================
                   Processing Summary
===========================================================
Total files: 5
Processed: 5
Successful: 5
Failed: 0
Success rate: 100.0%

Timing:
Total time: 245.8s
Total audio duration: 920.3s
Average RTF: 0.27
```

## 🛠️ Development

### Project Structure

```
Video2Text/
├── mp4_to_text.py          # Main execution script
├── core/                   # Core functionality modules
│   ├── __init__.py
│   ├── platform_utils.py   # Cross-platform utilities
│   ├── config_manager.py   # Configuration management
│   ├── file_manager.py     # File operations
│   ├── audio_processor.py  # Audio extraction
│   └── transcriber.py      # Whisper integration
├── config/                 # Configuration files
│   └── config.ini          # Default configuration
├── examples/               # Usage examples
├── tests/                  # Test files
├── temp/                   # Temporary files
├── logs/                   # Log files
└── requirements.txt        # Dependencies
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for the excellent speech recognition model
- [FFmpeg](https://ffmpeg.org/) for audio/video processing capabilities
- The open-source community for various tools and libraries used in this project

## 🔗 Links

- [Project Repository](https://github.com/your-username/Video2Text)
- [Issue Tracker](https://github.com/your-username/Video2Text/issues)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [FFmpeg](https://ffmpeg.org/)

---

Made with ❤️ by the Video2Text Team 
