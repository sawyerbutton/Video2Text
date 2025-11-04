# Video2Text Quick Start Guide

## 30-Second Quick Start

```bash
# 1. Place videos in directory
cp *.mp4 videos_todo/

# 2. Run automated processor
python run_auto_process.py

# 3. Check results
ls results/          # Text files here
ls videos_done/      # Processed videos here
```

Done! Your videos have been transcribed.

## 5-Minute Setup

### Installation

```bash
# Clone and enter directory
git clone https://github.com/your-username/Video2Text.git
cd Video2Text

# Install Python dependencies
pip install -r requirements.txt

# Install FFmpeg (choose your platform)
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

### First Run

```bash
# Check installation
python mp4_to_text.py --system-info

# Process your first video
python mp4_to_text.py -i videos_todo -o results
```

## Common Commands

### Automated Processing (Recommended)

```bash
# Standard batch processing
python run_auto_process.py

# With custom model
python run_auto_process.py --model large-v3

# Skip already processed files
python run_auto_process.py --skip-existing
```

### Manual Processing

```bash
# Basic usage
python mp4_to_text.py -i INPUT_DIR -o OUTPUT_DIR

# With specific model and language
python mp4_to_text.py -i videos -o texts -m medium -l zh

# High quality with GPU
python mp4_to_text.py -i videos -o texts -m large-v3 -d cuda
```

### Generate Subtitles

```bash
# SRT format
python mp4_to_text.py -i videos -o subtitles -f srt --timestamps

# VTT format
python mp4_to_text.py -i videos -o subtitles -f vtt --timestamps
```

## Model Selection Quick Guide

| Need | Model | Command |
|------|-------|---------|
| Fastest | tiny | `-m tiny` |
| Daily use | base | `-m base` |
| **Recommended** | medium | `-m medium` |
| High quality | large-v3 | `-m large-v3` |
| Fast + Quality | turbo | `-m turbo` |

## Device Selection

```bash
# Auto-detect (recommended)
-d auto

# Force GPU (NVIDIA)
-d cuda

# Force GPU (Apple Silicon)
-d mps

# Force CPU
-d cpu
```

## Output Formats

```bash
# Plain text (default)
-f txt

# SRT subtitles
-f srt --timestamps

# VTT subtitles
-f vtt --timestamps

# JSON with details
-f json --word-timestamps
```

## Common Options

```bash
# Parallel processing (2 videos at once)
-w 2

# Skip already processed files
--skip-existing

# Specify language
-l zh     # Chinese
-l en     # English
-l ja     # Japanese
-l auto   # Auto-detect

# Faster GPU processing
--compute-type int8_float16
```

## Troubleshooting

### GPU Not Working?

```bash
# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"

# Force CPU mode
python mp4_to_text.py -i videos -o texts -d cpu
```

### Out of Memory?

```bash
# Use smaller model
python mp4_to_text.py -i videos -o texts -m tiny

# Or use INT8
python mp4_to_text.py -i videos -o texts --compute-type int8
```

### Too Slow?

```bash
# Use GPU
python mp4_to_text.py -i videos -o texts -d cuda

# Use faster model
python mp4_to_text.py -i videos -o texts -m turbo

# Specify language (10-20% faster)
python mp4_to_text.py -i videos -o texts -l zh
```

## Complete Examples

### Example 1: Quick Test

```bash
# Copy one video
cp test.mp4 videos_todo/

# Process with default settings
python run_auto_process.py

# Check result
cat results/test.txt
```

### Example 2: High-Quality Chinese Transcription

```bash
python mp4_to_text.py \
    -i chinese_videos \
    -o chinese_texts \
    -m large-v3 \
    -l zh \
    -d cuda \
    --compute-type int8_float16
```

### Example 3: Batch English Subtitles

```bash
python mp4_to_text.py \
    -i english_videos \
    -o english_subtitles \
    -m medium \
    -l en \
    -f srt \
    --timestamps \
    -w 2 \
    --skip-existing
```

### Example 4: Fast Production Processing

```bash
python mp4_to_text.py \
    -i production_videos \
    -o production_texts \
    -m turbo \
    -d cuda \
    --compute-type int8_float16 \
    -w 2
```

## Directory Structure

After first run, you'll have:

```
Video2Text/
├── videos_todo/      # Put videos here (input)
├── results/          # Text files appear here (output)
├── videos_done/      # Processed videos moved here (archive)
└── logs/            # Log files (for debugging)
```

## Getting Help

```bash
# Show all options
python mp4_to_text.py --help

# System information
python mp4_to_text.py --system-info

# List available models
python mp4_to_text.py --list-models

# Quick system check
python tools/quick_check.py
```

## Next Steps

- Read [README.md](../README.md) for full documentation
- Check [ref/workflows.md](workflows.md) for detailed workflows
- See [ref/models.md](models.md) for model comparison
- Review [ref/api-reference.md](api-reference.md) for API usage

## Most Common Use Cases

### Use Case 1: Meeting Transcription
```bash
cp meeting.mp4 videos_todo/
python run_auto_process.py --language zh
cat results/meeting.txt
```

### Use Case 2: Podcast Processing
```bash
python mp4_to_text.py \
    -i podcasts \
    -o transcripts \
    -m medium \
    -l en \
    -w 2
```

### Use Case 3: YouTube Subtitles
```bash
python mp4_to_text.py \
    -i youtube_videos \
    -o youtube_subtitles \
    -f srt \
    --timestamps
```

### Use Case 4: Multiple Language Videos
```bash
python mp4_to_text.py \
    -i mixed_languages \
    -o transcripts \
    -m large-v3 \
    -l auto
```

## Performance Tips

1. **Use GPU** when available: `-d cuda` or `-d mps`
2. **Specify language** when known: `-l zh` (10-20% faster)
3. **Use INT8** for production: `--compute-type int8_float16`
4. **Use turbo model** for speed: `-m turbo`
5. **Enable parallel processing**: `-w 2` (for multiple files)
6. **Skip existing files**: `--skip-existing` (for re-runs)

## Quality Tips

1. **Use large-v3** for best quality: `-m large-v3`
2. **Specify language**: `-l zh` (better accuracy)
3. **Use float16**: `--compute-type float16` (over int8)
4. **Normalize audio**: `--normalize-audio` (for poor audio)
5. **Get word timestamps**: `--word-timestamps` (detailed)

---

**Ready to transcribe? Start with:**
```bash
python run_auto_process.py
```
