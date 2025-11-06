# Video2Text Workflows Reference

## Common Workflows

This document provides step-by-step workflows for common Video2Text use cases.

## Quick Start Workflow

### 1. First-Time Setup

**Step 1: Install Dependencies**
```bash
# Clone repository (if not already done)
cd Video2Text

# Install Python dependencies
pip install -r requirements.txt

# Install FFmpeg
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

**Step 2: Verify Installation**
```bash
# Check system and dependencies
python mp4_to_text.py --system-info

# List available models
python mp4_to_text.py --list-models
```

**Step 3: Process First Video**
```bash
# Create directories
mkdir -p videos_todo results

# Copy a test video
cp /path/to/test_video.mp4 videos_todo/

# Process with default settings
python mp4_to_text.py -i videos_todo -o results
```

## Automated Workflow (Recommended)

### Standard Automation

**Best for:** Daily batch processing of videos

**Steps:**

1. **Place videos in todo directory:**
```bash
cp *.mp4 videos_todo/
```

2. **Run automated processor:**
```bash
python run_auto_process.py
```

3. **Check results:**
```bash
ls results/          # Text files
ls videos_done/      # Processed videos
```

**What happens automatically:**
- ✓ Scans `videos_todo/` for all video files
- ✓ Processes each video with optimal settings
- ✓ Saves transcripts to `results/`
- ✓ Moves processed videos to `videos_done/`
- ✓ Shows progress in Chinese with detailed status
- ✓ Generates summary report

**Customization:**
```bash
# Use specific model
python run_auto_process.py --model large-v3

# Chinese language
python run_auto_process.py --language zh

# Multiple workers
python run_auto_process.py --workers 2

# Skip already processed
python run_auto_process.py --skip-existing
```

### Large File Workflow

**Best for:** Processing large video files (150MB+)

**Steps:**

1. **Place large videos in special directory:**
```bash
cp large_video.mp4 videos_large/
```

2. **Run large file processor:**
```bash
python run_large_process.py
```

3. **Select processing tier:**
```
Found files in categories:
1. SMALL (150-200MB): 2 files
2. MEDIUM (200-300MB): 1 file
3. LARGE (300-500MB): 0 files
4. HUGE (>500MB): 1 file

Select tier to process (1-4):
```

**Processing tiers:**
- **SMALL** (150-200MB): base model, 30min timeout
- **MEDIUM** (200-300MB): base model, 45min timeout
- **LARGE** (300-500MB): tiny model, 60min timeout
- **HUGE** (>500MB): tiny model, 120min timeout

## Manual CLI Workflow

### Basic Processing

**Step 1: Prepare directories**
```bash
mkdir -p input_videos output_texts
cp *.mp4 input_videos/
```

**Step 2: Process videos**
```bash
python mp4_to_text.py -i input_videos -o output_texts
```

**Step 3: Review results**
```bash
cat output_texts/video1.txt
```

### High-Quality Processing

**For professional transcription:**

```bash
python mp4_to_text.py \
    -i input_videos \
    -o output_texts \
    -m large-v3 \
    -l zh \
    -d cuda \
    --compute-type int8_float16 \
    -f txt
```

**Parameters explained:**
- `-m large-v3`: Best quality model
- `-l zh`: Chinese language
- `-d cuda`: Use NVIDIA GPU
- `--compute-type int8_float16`: Fastest GPU mode
- `-f txt`: Plain text output

## Subtitle Generation Workflow

### Creating SRT Subtitles

**Step 1: Process with SRT format**
```bash
python mp4_to_text.py \
    -i videos \
    -o subtitles \
    -f srt \
    --timestamps
```

**Step 2: Review subtitle file**
```bash
cat subtitles/video.srt
```

**Output example:**
```srt
1
00:00:00,000 --> 00:00:03,500
Hello and welcome to our presentation

2
00:00:03,500 --> 00:00:07,200
Today we'll discuss video transcription
```

### Creating WebVTT Subtitles

**For web video players:**
```bash
python mp4_to_text.py \
    -i videos \
    -o subtitles \
    -f vtt \
    --timestamps
```

### Word-Level Timestamps

**For precise timing:**
```bash
python mp4_to_text.py \
    -i videos \
    -o subtitles \
    -f json \
    --word-timestamps
```

**JSON output includes:**
```json
{
  "segments": [
    {
      "start": 0.0,
      "end": 3.5,
      "text": "Hello and welcome",
      "words": [
        {"word": "Hello", "start": 0.0, "end": 0.5},
        {"word": "and", "start": 0.6, "end": 0.8},
        {"word": "welcome", "start": 0.9, "end": 3.5}
      ]
    }
  ]
}
```

## Batch Processing Workflow

### Processing Multiple Videos

**Method 1: Using Workers**
```bash
# Process 2 videos at a time
python mp4_to_text.py \
    -i videos \
    -o texts \
    -w 2
```

**Method 2: Skip Already Processed**
```bash
# Resume interrupted batch
python mp4_to_text.py \
    -i videos \
    -o texts \
    --skip-existing
```

**Method 3: Automated Script**
```bash
# Process everything automatically
python tools/auto_process.py --workers 2 --skip-existing
```

### Processing by Language

**Chinese videos:**
```bash
python mp4_to_text.py \
    -i chinese_videos \
    -o chinese_texts \
    -l zh \
    -m medium
```

**English videos:**
```bash
python mp4_to_text.py \
    -i english_videos \
    -o english_texts \
    -l en \
    -m base
```

**Multi-language (auto-detect):**
```bash
python mp4_to_text.py \
    -i mixed_videos \
    -o mixed_texts \
    -l auto \
    -m large-v3
```

## Production Workflow

### High-Throughput Processing

**Setup for maximum speed:**

```bash
# Using turbo model with GPU
python mp4_to_text.py \
    -i input \
    -o output \
    -m turbo \
    -d cuda \
    --compute-type int8_float16 \
    -w 2 \
    --skip-existing \
    --cleanup-temp
```

**Key optimizations:**
- `turbo` model: 8x faster than large
- `cuda` + `int8_float16`: Maximum GPU performance
- `-w 2`: Parallel processing
- `--skip-existing`: Resume capability
- `--cleanup-temp`: Save disk space

### Quality-First Processing

**Setup for maximum quality:**

```bash
python mp4_to_text.py \
    -i input \
    -o output \
    -m large-v3 \
    -l zh \
    -d cuda \
    --compute-type float16 \
    --normalize-audio \
    -f json \
    --word-timestamps
```

**Key settings:**
- `large-v3`: Best accuracy
- Specific language: Better results
- `float16`: Better quality than int8
- `--normalize-audio`: Improve audio quality
- `json` + `--word-timestamps`: Maximum detail

## Meeting Transcription Workflow

### Single Meeting

**Step 1: Record meeting** (external)

**Step 2: Transcribe**
```bash
python mp4_to_text.py \
    -i meeting.mp4 \
    -o meeting_transcript.txt \
    -l zh \
    -m medium
```

**Step 3: Post-process** (optional)
```bash
# Add formatting, speaker labels, etc.
```

### Multiple Meetings

**Step 1: Organize meetings**
```bash
mkdir meetings/2024-01
cp meeting_*.mp4 meetings/2024-01/
```

**Step 2: Batch transcribe**
```bash
python mp4_to_text.py \
    -i meetings/2024-01 \
    -o transcripts/2024-01 \
    -l zh \
    -m medium \
    -w 2
```

**Step 3: Archive**
```bash
mv meetings/2024-01/*.mp4 archive/
```

## Podcast Processing Workflow

### Single Episode

```bash
python mp4_to_text.py \
    -i podcast_episode.mp4 \
    -o podcast_transcripts/ \
    -l en \
    -m medium \
    -f txt
```

### Podcast Series

**Directory structure:**
```
podcasts/
├── episode_001.mp4
├── episode_002.mp4
└── episode_003.mp4
```

**Processing:**
```bash
python mp4_to_text.py \
    -i podcasts \
    -o transcripts \
    -l en \
    -m medium \
    --skip-existing
```

**With subtitles for YouTube:**
```bash
python mp4_to_text.py \
    -i podcasts \
    -o subtitles \
    -l en \
    -m medium \
    -f srt \
    --timestamps
```

## Video Course Workflow

### Processing Course Materials

**Step 1: Organize by module**
```bash
course/
├── module_01/
│   ├── lesson_01.mp4
│   └── lesson_02.mp4
└── module_02/
    ├── lesson_01.mp4
    └── lesson_02.mp4
```

**Step 2: Process each module**
```bash
for module in course/module_*; do
    python mp4_to_text.py \
        -i "$module" \
        -o "transcripts/$(basename $module)" \
        -l en \
        -m medium
done
```

**Step 3: Generate searchable transcripts**
```bash
# All in JSON for easy searching
python mp4_to_text.py \
    -i course \
    -o course_transcripts \
    -l en \
    -m medium \
    -f json \
    --word-timestamps
```

## Live Streaming Archive Workflow

### YouTube/Twitch Archives

**Step 1: Download archives** (using yt-dlp or similar)
```bash
yt-dlp -o "stream_%(upload_date)s.mp4" <URL>
```

**Step 2: Transcribe**
```bash
python mp4_to_text.py \
    -i stream_*.mp4 \
    -o stream_transcripts \
    -l auto \
    -m small \
    --skip-existing
```

**Step 3: Generate searchable index**
```bash
# Using JSON format for indexing
python mp4_to_text.py \
    -i stream_*.mp4 \
    -o stream_index \
    -f json
```

## Testing and Quality Check Workflow

### Test Different Models

**Create test script:**
```bash
#!/bin/bash
# test_models.sh

VIDEO="test_video.mp4"

for model in tiny base small medium; do
    echo "Testing $model..."
    time python mp4_to_text.py \
        -i "$VIDEO" \
        -o "test_${model}.txt" \
        -m "$model"
done
```

**Run comparison:**
```bash
chmod +x test_models.sh
./test_models.sh
```

### Quality Assessment

**Step 1: Process with multiple models**
```bash
python mp4_to_text.py -i test.mp4 -o test_base.txt -m base
python mp4_to_text.py -i test.mp4 -o test_medium.txt -m medium
python mp4_to_text.py -i test.mp4 -o test_large.txt -m large-v3
```

**Step 2: Compare results**
```bash
diff test_base.txt test_medium.txt
diff test_medium.txt test_large.txt
```

**Step 3: Choose optimal model**

## Troubleshooting Workflow

### Diagnose Issues

**Step 1: System check**
```bash
python mp4_to_text.py --system-info
```

**Step 2: Quick check tool**
```bash
python tools/quick_check.py
```

**Step 3: Test with tiny model**
```bash
python mp4_to_text.py \
    -i problem_video.mp4 \
    -o test_output.txt \
    -m tiny \
    --verbose
```

### GPU Issues

**Check GPU availability:**
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

**Force CPU mode:**
```bash
python mp4_to_text.py -i videos -o texts -d cpu
```

**Test GPU with small model:**
```bash
python mp4_to_text.py \
    -i test.mp4 \
    -o test.txt \
    -m tiny \
    -d cuda
```

## Integration Workflows

### Integration with Python Scripts

**Example: Automated pipeline**
```python
#!/usr/bin/env python3
from pathlib import Path
from core.platform_utils import detect_device
from core.audio_processor import AudioProcessor
from core.transcriber import Transcriber

# Setup
device = detect_device()
audio_processor = AudioProcessor()
transcriber = Transcriber(model_name='medium', device=device)

# Process videos
video_dir = Path('videos_todo')
for video_file in video_dir.glob('*.mp4'):
    print(f"Processing {video_file.name}...")

    # Extract audio
    audio_file = audio_processor.extract_audio(video_file)

    # Transcribe
    text = transcriber.transcribe(audio_file)

    # Save result
    output_file = Path('results') / f"{video_file.stem}.txt"
    output_file.write_text(text)

    print(f"Saved to {output_file}")
```

### Integration with Web Applications

**Flask API example:**
```python
from flask import Flask, request, jsonify
from core.transcriber import Transcriber

app = Flask(__name__)
transcriber = Transcriber(model_name='turbo', device='cuda')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    video_file = request.files['video']
    # ... process video ...
    text = transcriber.transcribe(audio_path)
    return jsonify({'transcript': text})

if __name__ == '__main__':
    app.run()
```

## Optimization Workflows

### Maximize Speed

**Configuration for fastest processing:**
```bash
# Option 1: Turbo model
python mp4_to_text.py \
    -i videos \
    -o texts \
    -m turbo \
    -d cuda \
    --compute-type int8_float16 \
    -w 2

# Option 2: Tiny model
python mp4_to_text.py \
    -i videos \
    -o texts \
    -m tiny \
    -d cuda \
    -w 4
```

### Maximize Quality

**Configuration for best quality:**
```bash
python mp4_to_text.py \
    -i videos \
    -o texts \
    -m large-v3 \
    -l zh \
    -d cuda \
    --compute-type float16 \
    --normalize-audio \
    -f json \
    --word-timestamps
```

### Balance Speed and Quality

**Recommended configuration:**
```bash
python mp4_to_text.py \
    -i videos \
    -o texts \
    -m medium \
    -l auto \
    -d cuda \
    --compute-type int8_float16 \
    -w 2 \
    --skip-existing
```

## Backup and Archive Workflow

### Archive Processed Files

**Step 1: Process videos**
```bash
python run_auto_process.py
```

**Step 2: Archive results**
```bash
DATE=$(date +%Y-%m-%d)
mkdir -p archive/$DATE
mv videos_done/* archive/$DATE/videos/
cp -r results/* archive/$DATE/transcripts/
```

**Step 3: Compress archives**
```bash
tar -czf archive_$DATE.tar.gz archive/$DATE
```

### Restore from Archive

**Extract archive:**
```bash
tar -xzf archive_2024-01-15.tar.gz
```

**Verify transcripts:**
```bash
ls archive/2024-01-15/transcripts/
```

## Scheduled Workflow (Cron/Task Scheduler)

### Linux/macOS Cron

**Edit crontab:**
```bash
crontab -e
```

**Add scheduled task:**
```bash
# Process videos daily at 2 AM
0 2 * * * cd /path/to/Video2Text && python run_auto_process.py >> logs/cron.log 2>&1
```

### Windows Task Scheduler

**Create batch file** (`scheduled_process.bat`):
```batch
@echo off
cd C:\Video2Text
python run_auto_process.py
```

**Schedule in Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily, weekly, etc.)
4. Set action: Run `scheduled_process.bat`

## Best Practices Summary

### General Recommendations

1. **Start with automation scripts** for simplicity
2. **Use appropriate model** for your needs
3. **Enable GPU** when available
4. **Specify language** when known
5. **Use INT8** for production
6. **Enable skip-existing** for resumability
7. **Clean temp files** to save space
8. **Monitor system resources** during processing
9. **Test on small samples** before large batches
10. **Archive processed files** regularly

### Performance Tips

1. **GPU acceleration**: 2-8x faster
2. **INT8 quantization**: 2-4x faster
3. **Specify language**: 10-20% faster
4. **Turbo model**: 8x faster than large-v3
5. **Parallel workers**: Process multiple files simultaneously
6. **Skip existing**: Save time on re-runs

### Quality Tips

1. **Use large-v3** for best quality
2. **Specify language** for better accuracy
3. **Normalize audio** for poor quality sources
4. **Use float16** over int8 for quality
5. **Test different models** to find optimal
6. **Check audio quality** before processing
