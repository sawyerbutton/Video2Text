# Video2Text - 智能视频转文本工具

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Cross Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/your-username/Video2Text)

一个强大的跨平台视频转文本工具，使用OpenAI Whisper进行高质量语音识别。支持GPU/CPU自动检测、批量处理和智能文件管理。

## ✨ 核心特性

- 🎥 **批量视频处理** - 一次处理多个MP4/AVI/MOV/MKV文件
- 🎙️ **高质量转录** - 基于OpenAI Whisper的精准语音识别
- 🔧 **跨平台支持** - Windows、macOS、Linux全平台兼容
- 🚀 **智能硬件检测** - 自动使用CUDA、MPS(Apple Silicon)或CPU
- 📊 **多种输出格式** - 支持TXT、SRT、VTT、JSON格式
- ⚡ **并行处理** - 多线程处理提升批量操作速度
- 🎛️ **高度可配置** - 通过CLI或配置文件灵活配置
- 📈 **实时进度跟踪** - 详细的进度指示器和性能统计
- 🤖 **全自动化处理** - 新增一键自动化脚本，支持智能文件分层处理

## 🚀 快速开始

### 安装

1. **克隆仓库**
```bash
git clone https://github.com/your-username/Video2Text.git
cd Video2Text
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **安装FFmpeg**
- **Windows**: 从[FFmpeg官网](https://ffmpeg.org/)下载或使用 `choco install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) 或 `sudo yum install ffmpeg` (CentOS/RHEL)

### 🎯 推荐使用方式：自动化脚本

#### 1. 标准自动化处理
```bash
# 一键处理所有视频文件（推荐）
python auto_process.py

# 这个脚本会：
# - 自动处理 videos_todo 目录中的所有视频文件
# - 将转录结果保存到 results 目录
# - 将处理完的视频移动到 videos_done 目录
# - 提供详细的中文进度提示和性能统计
```

#### 2. 大文件智能分层处理
```bash
# 处理大文件（150MB以上）
python auto_process_large.py

# 智能分层策略：
# - SMALL (150-200MB): base模型, 30分钟超时
# - MEDIUM (200-300MB): base模型, 45分钟超时  
# - LARGE (300-500MB): tiny模型, 60分钟超时
# - HUGE (>500MB): tiny模型, 120分钟超时
```

### 传统使用方式

```bash
# 基础转录
python mp4_to_text.py -i ./input_videos -o ./output_texts

# 指定模型和语言
python mp4_to_text.py -i ./videos -o ./texts -m large-v3 -l zh

# 并行处理
python mp4_to_text.py -i ./videos -o ./texts -w 2 --skip-existing
```

## 📁 目录结构

```
Video2Text/
├── videos_todo/          # 待处理视频文件目录
├── videos_large/         # 大文件处理目录（150MB+）
├── videos_done/          # 已完成处理的视频文件
├── results/              # 转录文本输出目录
├── config/               # 配置文件目录
├── core/                 # 核心模块
├── auto_process.py       # 🌟 自动化处理脚本（推荐）
├── auto_process_large.py # 🌟 大文件智能处理脚本
└── mp4_to_text.py        # 传统命令行工具
```

## 🎛️ 配置选项

### Whisper模型选择

| 模型 | 大小 | 内存需求 | 速度 | 准确度 | 适用场景 |
|------|------|----------|------|--------|----------|
| tiny | 39MB | 1GB | 极快 | 较低 | 快速测试 |
| base | 142MB | 2GB | 快速 | 中等 | **推荐日常使用** |
| small | 244MB | 3GB | 中等 | 良好 | 平衡性能 |
| medium | 769MB | 5GB | 中等 | 高 | 高质量需求 |
| large | 1550MB | 8GB | 较慢 | 很高 | 专业用途 |
| large-v3 | 1550MB | 10GB | 较慢 | 最高 | 最新最佳 |

### 性能优化建议

**GPU加速**
- **NVIDIA CUDA**: 需要支持CUDA的NVIDIA显卡
- **Apple Silicon (MPS)**: M1/M2/M3 Mac自动支持
- **自动检测**: 使用 `-d auto` 自动选择最佳设备

**内存优化**
- 内存有限时使用较小模型
- 减少并行worker数量
- 启用临时文件清理

**处理速度**
- **追求速度**: 使用 `tiny` 或 `base` 模型
- **平衡选择**: 使用 `medium` 模型（推荐）
- **追求质量**: 使用 `large-v3` 模型配合GPU

## 📊 性能表现

### 实际测试数据
- **音频提取**: 通常1-3秒完成（基于FFmpeg优化）
- **转录速度**: RTF 0.02-0.03（实时因子，越小越快）
- **GPU利用率**: 85-94%（NVIDIA RTX 4060测试）
- **批量处理**: 支持连续处理数十个文件，100%成功率

### 处理时间估算
- **小文件** (<100MB): 通常30-60秒
- **中等文件** (100-300MB): 通常1-3分钟  
- **大文件** (300MB-1GB): 通常3-10分钟
- **超大文件** (>1GB): 可能需要10-30分钟

## 🔧 高级配置

### 配置文件示例 (config/config.ini)
```ini
[PROCESSING]
model_name = base
language = auto
device = auto
max_workers = 1
skip_existing = true
cleanup_temp = true

[AUDIO]
format = wav
sample_rate = 16000
channels = 1
normalize_audio = false

[OUTPUT]
format = txt
include_timestamps = false
word_level_timestamps = false

[LOGGING]
level = INFO
file = logs/mp4_to_text.log
console_output = true
```

## 🚨 故障排除

### 常见问题

**1. GPU未被检测**
```bash
# 检查CUDA安装
nvidia-smi

# 检查PyTorch CUDA支持
python -c "import torch; print(torch.cuda.is_available())"

# 重新安装支持CUDA的PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**2. 音频提取失败**
- 确认FFmpeg已正确安装
- 检查视频文件是否损坏
- 确认有足够的磁盘空间

**3. 内存不足**
- 使用更小的Whisper模型
- 减少并行处理数量
- 关闭其他占用内存的程序

**4. 处理速度慢**
- 启用GPU加速
- 使用更快的模型（tiny/base）
- 确认硬件配置满足要求

## 📋 支持格式

**输入视频格式:**
- MP4, AVI, MOV, MKV, FLV, WebM, M4V, WMV, 3GP, OGV

**输出文本格式:**
- TXT (纯文本)
- SRT (字幕格式)
- VTT (WebVTT格式)
- JSON (包含元数据的详细格式)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 强大的语音识别模型
- [FFmpeg](https://ffmpeg.org/) - 多媒体处理框架
- 所有贡献者和用户的支持

---

**🌟 如果这个项目对你有帮助，请给个Star支持！**
