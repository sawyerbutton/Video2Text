# Video2Text Model Reference

## Whisper Models Overview

Video2Text uses faster-whisper, an optimized implementation of OpenAI's Whisper models. This implementation provides 2-8x speed improvements over the original while maintaining accuracy.

## Available Models

### Model Comparison Table

| Model | Size | Memory | Speed | Accuracy | RTF* | Best For |
|-------|------|--------|-------|----------|------|----------|
| tiny | 39 MB | 1 GB | ⚡⚡⚡⚡⚡ | ⭐⭐ | 0.01 | Quick testing, low resources |
| base | 142 MB | 2 GB | ⚡⚡⚡⚡ | ⭐⭐⭐ | 0.02 | Daily use, general purpose |
| small | 244 MB | 3 GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | 0.03 | Balanced performance |
| medium | 769 MB | 5 GB | ⚡⚡ | ⭐⭐⭐⭐ | 0.05 | **Recommended default** |
| large | 1550 MB | 8 GB | ⚡ | ⭐⭐⭐⭐⭐ | 0.08 | High quality transcription |
| large-v2 | 1550 MB | 8 GB | ⚡ | ⭐⭐⭐⭐⭐ | 0.08 | Improved large model |
| large-v3 | 1550 MB | 10 GB | ⚡ | ⭐⭐⭐⭐⭐ | 0.08 | **Latest, best accuracy** |
| turbo | 809 MB | 6 GB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | 0.02 | **Fast production use** |

*RTF = Real-Time Factor (lower is better, 0.02 means 50x faster than real-time)

## Detailed Model Specifications

### tiny

**Specifications:**
- Download Size: 39 MB
- Disk Size: 73 MB
- Memory Requirement: 1 GB
- Parameters: ~39M

**Characteristics:**
- Fastest processing speed
- Lowest memory footprint
- Basic accuracy
- Good for rapid prototyping

**Supported Languages:** 9 languages
- English, Chinese, Japanese, Korean, French, German, Spanish, Russian

**Use Cases:**
- Quick testing and validation
- Low-resource environments
- Real-time processing requirements
- Preview/draft transcriptions

**Performance:**
- CPU: ~100x real-time
- GPU: ~200x real-time

**Command:**
```bash
python mp4_to_text.py -i videos -o texts -m tiny
```

---

### base

**Specifications:**
- Download Size: 142 MB
- Disk Size: 290 MB
- Memory Requirement: 2 GB
- Parameters: ~74M

**Characteristics:**
- Fast processing
- Good accuracy for common use cases
- Balanced performance
- Recommended for daily use

**Supported Languages:** 11 languages
- All tiny languages plus Portuguese, Italian

**Use Cases:**
- General-purpose transcription
- Content creation workflows
- Meeting transcriptions
- Podcast processing

**Performance:**
- CPU: ~50x real-time
- GPU: ~100x real-time

**Command:**
```bash
python mp4_to_text.py -i videos -o texts -m base
```

---

### small

**Specifications:**
- Download Size: 244 MB
- Disk Size: 488 MB
- Memory Requirement: 3 GB
- Parameters: ~244M

**Characteristics:**
- Medium processing speed
- Good accuracy
- Better multi-language support
- Balanced quality/performance

**Supported Languages:** 13 languages
- All base languages plus Arabic, Hindi

**Use Cases:**
- Professional transcription
- Multi-language content
- Educational materials
- Documentary processing

**Performance:**
- CPU: ~30x real-time
- GPU: ~70x real-time

**Command:**
```bash
python mp4_to_text.py -i videos -o texts -m small
```

---

### medium (Recommended Default)

**Specifications:**
- Download Size: 769 MB
- Disk Size: 1.5 GB
- Memory Requirement: 5 GB
- Parameters: ~769M

**Characteristics:**
- High accuracy
- Good multi-language support
- Reasonable speed with GPU
- **Default recommended model**

**Supported Languages:** 15+ languages
- All small languages plus Thai, Vietnamese

**Use Cases:**
- **Recommended for most users**
- Professional transcription services
- Broadcast media processing
- High-quality subtitle generation
- Academic research

**Performance:**
- CPU: ~20x real-time
- GPU (CUDA): ~50x real-time
- GPU (MPS): ~40x real-time

**Command:**
```bash
python mp4_to_text.py -i videos -o texts -m medium
```

**Optimization:**
```bash
# With INT8 quantization for faster processing
python mp4_to_text.py -i videos -o texts -m medium --compute-type int8
```

---

### large

**Specifications:**
- Download Size: 1550 MB
- Disk Size: 3.0 GB
- Memory Requirement: 8 GB
- Parameters: ~1550M

**Characteristics:**
- Very high accuracy
- Comprehensive language support
- Slower processing
- GPU recommended

**Supported Languages:** 17+ languages
- All medium languages plus Dutch, Polish

**Use Cases:**
- Professional media production
- Legal transcriptions
- Medical transcriptions
- High-stakes accuracy requirements

**Performance:**
- CPU: ~12x real-time
- GPU (CUDA): ~30x real-time

**Command:**
```bash
python mp4_to_text.py -i videos -o texts -m large -d cuda
```

---

### large-v2

**Specifications:**
- Download Size: 1550 MB
- Disk Size: 3.0 GB
- Memory Requirement: 8 GB
- Parameters: ~1550M

**Characteristics:**
- Improved version of large model
- Better multi-language performance
- Enhanced accuracy for difficult audio
- Same size as large

**Supported Languages:** 19+ languages
- All large languages plus Swedish, Danish

**Use Cases:**
- Same as large model
- Preferred over original large
- Better for noisy audio
- Improved punctuation

**Performance:**
- Similar to large model
- Slightly better quality

**Command:**
```bash
python mp4_to_text.py -i videos -o texts -m large-v2 -d cuda
```

---

### large-v3 (Latest & Best)

**Specifications:**
- Download Size: 1550 MB
- Disk Size: 3.0 GB
- Memory Requirement: 10 GB
- Parameters: ~1550M

**Characteristics:**
- **Latest and most accurate model**
- Best multi-language support
- Improved handling of complex audio
- State-of-the-art accuracy

**Supported Languages:** 20+ languages
- All large-v2 languages plus Norwegian, Finnish

**Use Cases:**
- **Best quality transcription**
- Multi-language international content
- Challenging audio conditions
- Production workflows requiring highest quality

**Performance:**
- CPU: ~12x real-time
- GPU (CUDA): ~30x real-time
- GPU (MPS): ~25x real-time

**Command:**
```bash
python mp4_to_text.py -i videos -o texts -m large-v3 -d cuda --compute-type int8_float16
```

**Recommended Configuration:**
```bash
# Maximum quality with GPU acceleration
python mp4_to_text.py \
    -i videos -o texts \
    -m large-v3 \
    -d cuda \
    --compute-type int8_float16 \
    -l auto
```

---

### turbo (Optimized for Production)

**Specifications:**
- Download Size: 809 MB
- Disk Size: 1.6 GB
- Memory Requirement: 6 GB
- Parameters: ~809M

**Characteristics:**
- **Optimized for faster-whisper**
- 8x speed improvement over large-v3
- Accuracy close to large models
- Best for production environments

**Supported Languages:** 17+ languages
- Major languages with optimized performance

**Use Cases:**
- **Production deployments**
- Real-time or near-real-time processing
- High-throughput batch processing
- Cost-sensitive applications

**Performance:**
- CPU: ~50x real-time
- GPU (CUDA): ~100x real-time
- **Fastest high-quality option**

**Command:**
```bash
python mp4_to_text.py -i videos -o texts -m turbo -d cuda
```

**Recommended for:**
- High-volume processing
- Time-sensitive transcription
- API services
- Automated pipelines

---

## Model Selection Guide

### By Use Case

**Quick Testing / Prototyping:**
- Use: `tiny` or `base`
- Reason: Fast feedback, low resource usage

**General Daily Use:**
- Use: `base` or `medium`
- Reason: Good balance of speed and quality

**Professional Work:**
- Use: `medium` or `large-v3`
- Reason: High accuracy, reliable results

**Production Services:**
- Use: `turbo` or `medium` with INT8
- Reason: Speed + quality balance

**Highest Quality:**
- Use: `large-v3`
- Reason: State-of-the-art accuracy

### By Hardware

**CPU Only (No GPU):**
```bash
# Best options
tiny, base, small with int8

# Command
python mp4_to_text.py -i videos -o texts -m small --compute-type int8
```

**NVIDIA GPU (CUDA):**
```bash
# Best options
medium, large-v3, turbo with int8_float16

# Command
python mp4_to_text.py -i videos -o texts -m turbo -d cuda --compute-type int8_float16
```

**Apple Silicon (M1/M2/M3):**
```bash
# Best options
medium, large with float16

# Command
python mp4_to_text.py -i videos -o texts -m medium -d mps --compute-type float16
```

### By Available Memory

**< 2 GB RAM:**
- Model: `tiny`
- Compute: `int8`

**2-4 GB RAM:**
- Model: `base`
- Compute: `int8`

**4-6 GB RAM:**
- Model: `small` or `medium`
- Compute: `int8`

**6-10 GB RAM:**
- Model: `medium` or `turbo`
- Compute: `float16` or `int8`

**> 10 GB RAM:**
- Model: `large-v3`
- Compute: `int8_float16` (GPU) or `float16`

### By Language

**English Only:**
- Any model works well
- `turbo` recommended for speed

**Chinese/Japanese/Korean:**
- `medium` or higher recommended
- `large-v3` for best results

**Multiple Languages:**
- `medium` minimum
- `large-v3` for best multi-language support

**Rare Languages:**
- `large-v3` only
- Check language support in models.json

## Compute Types

### Overview

faster-whisper supports different compute types for performance optimization:

| Compute Type | Speed | Memory | Quality | Devices |
|--------------|-------|--------|---------|---------|
| float32 | Slow | 200% | Highest | CPU |
| float16 | Fast | 100% | High | CUDA, MPS |
| int8 | Very Fast | 62% | Good | CPU, CUDA |
| int8_float16 | Very Fast | 62% | High | CUDA only |

### float32 (Full Precision)

**Characteristics:**
- 32-bit floating point
- Highest numerical precision
- Slowest processing
- Highest memory usage

**When to Use:**
- Rarely needed
- Research purposes
- When accuracy is paramount
- Debugging quality issues

**Command:**
```bash
python mp4_to_text.py -i videos -o texts --compute-type float32
```

---

### float16 (Half Precision)

**Characteristics:**
- 16-bit floating point
- 2x faster than float32
- 50% memory savings
- Minimal quality loss

**When to Use:**
- Apple Silicon (MPS) - **default**
- CUDA GPUs with good FP16 support
- Balanced speed/quality

**Command:**
```bash
python mp4_to_text.py -i videos -o texts -d mps --compute-type float16
```

---

### int8 (Integer Quantization)

**Characteristics:**
- 8-bit integer quantization
- 4x faster than float32
- 62% memory usage
- Good quality retention

**When to Use:**
- CPU processing - **default**
- Memory-constrained systems
- Batch processing
- Production deployments

**Command:**
```bash
python mp4_to_text.py -i videos -o texts --compute-type int8
```

**Performance:**
- 2-4x faster on CPU
- Enables larger models on limited hardware

---

### int8_float16 (Mixed Precision)

**Characteristics:**
- INT8 weights, FP16 activations
- Best performance on CUDA
- 62% memory usage
- High quality

**When to Use:**
- NVIDIA GPU (CUDA) - **default**
- Production with GPU
- Maximum throughput

**Command:**
```bash
python mp4_to_text.py -i videos -o texts -d cuda --compute-type int8_float16
```

**Performance:**
- 6-8x faster than float32
- Best option for GPU processing

## Language Support

### Supported Languages by Model

#### All Models (20+ languages)
- **Auto-detect** (recommended)
- English (en)
- Chinese (zh) - Mandarin
- Japanese (ja)
- Korean (ko)
- French (fr)
- German (de)
- Spanish (es)
- Russian (ru)
- Portuguese (pt)
- Italian (it)
- Arabic (ar)
- Hindi (hi)
- Thai (th)
- Vietnamese (vi)
- Dutch (nl)
- Polish (pl)
- Swedish (sv)
- Danish (da)
- Norwegian (no)
- Finnish (fi)

### Language-Specific Recommendations

**Chinese (zh):**
- Minimum: `small`
- Recommended: `medium`
- Best: `large-v3`

**Japanese (ja):**
- Minimum: `small`
- Recommended: `medium`
- Best: `large-v3`

**English (en):**
- Any model works well
- `base` sufficient for most cases
- `turbo` for speed

**Multi-language Content:**
- Use `auto` detection
- `large-v3` recommended
- May need manual language hints

### Language Detection

**Auto-detect (default):**
```bash
python mp4_to_text.py -i videos -o texts -l auto
```

**Specific Language:**
```bash
# Chinese
python mp4_to_text.py -i videos -o texts -l zh

# Japanese
python mp4_to_text.py -i videos -o texts -l ja

# English
python mp4_to_text.py -i videos -o texts -l en
```

**Why Specify Language:**
- 10-20% faster processing
- Better accuracy for specified language
- Skips language detection step

## Performance Benchmarks

### Speed Comparison (RTF - Lower is Better)

**CPU (Intel i7):**
| Model | RTF | Speed |
|-------|-----|-------|
| tiny | 0.01 | 100x real-time |
| base | 0.02 | 50x real-time |
| small | 0.03 | 33x real-time |
| medium | 0.05 | 20x real-time |
| large-v3 | 0.08 | 12x real-time |
| turbo | 0.02 | 50x real-time |

**NVIDIA GPU (RTX 4060):**
| Model | RTF | Speed |
|-------|-----|-------|
| tiny | 0.005 | 200x real-time |
| base | 0.01 | 100x real-time |
| small | 0.015 | 67x real-time |
| medium | 0.02 | 50x real-time |
| large-v3 | 0.03 | 33x real-time |
| turbo | 0.01 | 100x real-time |

**Apple Silicon (M2):**
| Model | RTF | Speed |
|-------|-----|-------|
| tiny | 0.008 | 125x real-time |
| base | 0.015 | 67x real-time |
| small | 0.025 | 40x real-time |
| medium | 0.025 | 40x real-time |
| large-v3 | 0.04 | 25x real-time |
| turbo | 0.015 | 67x real-time |

### Processing Time Examples

**1-hour video file:**

| Model | CPU | CUDA GPU | Apple M2 |
|-------|-----|----------|----------|
| tiny | 36 sec | 18 sec | 29 sec |
| base | 72 sec | 36 sec | 54 sec |
| medium | 3 min | 72 sec | 90 sec |
| large-v3 | 5 min | 109 sec | 144 sec |
| turbo | 72 sec | 36 sec | 54 sec |

## Model Download and Storage

### Download Process

Models are automatically downloaded on first use:

1. Model requested via command or config
2. faster-whisper checks local cache
3. Downloads from Hugging Face if not cached
4. Validates download integrity
5. Loads into memory

### Cache Location

**Default cache directories:**
- Linux: `~/.cache/huggingface/hub/`
- macOS: `~/Library/Caches/huggingface/hub/`
- Windows: `%USERPROFILE%\.cache\huggingface\hub\`

### Manual Download

```bash
# Pre-download models
python -c "from faster_whisper import WhisperModel; WhisperModel('medium')"
```

### Disk Space Requirements

| Model | Download | Disk | Total |
|-------|----------|------|-------|
| tiny | 39 MB | 73 MB | 112 MB |
| base | 142 MB | 290 MB | 432 MB |
| small | 244 MB | 488 MB | 732 MB |
| medium | 769 MB | 1.5 GB | 2.3 GB |
| large | 1550 MB | 3.0 GB | 4.5 GB |
| turbo | 809 MB | 1.6 GB | 2.4 GB |

## Best Practices

### 1. Start Small, Scale Up
```bash
# Test with tiny
python mp4_to_text.py -i videos -o texts -m tiny

# If quality insufficient, try base
python mp4_to_text.py -i videos -o texts -m base

# For production, use medium or turbo
python mp4_to_text.py -i videos -o texts -m turbo
```

### 2. Use GPU When Available
```bash
# Let system auto-detect
python mp4_to_text.py -i videos -o texts -d auto

# Or explicitly specify
python mp4_to_text.py -i videos -o texts -d cuda
```

### 3. Specify Language When Known
```bash
# Faster and more accurate
python mp4_to_text.py -i videos -o texts -l zh
```

### 4. Use INT8 for Production
```bash
# CPU
python mp4_to_text.py -i videos -o texts --compute-type int8

# GPU
python mp4_to_text.py -i videos -o texts -d cuda --compute-type int8_float16
```

### 5. Monitor Memory Usage
```bash
# Check before running
python mp4_to_text.py --system-info
```

## Troubleshooting

### Model Won't Load
- Check available memory
- Try smaller model
- Verify internet connection for download

### Slow Performance
- Enable GPU acceleration
- Use INT8 quantization
- Try smaller model
- Specify language explicitly

### Poor Accuracy
- Use larger model
- Specify correct language
- Check audio quality
- Try different compute type

### Out of Memory
- Use smaller model
- Enable INT8 quantization
- Close other applications
- Reduce worker count
