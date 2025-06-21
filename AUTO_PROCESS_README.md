# 自动化视频转文本处理脚本

## 概述

`auto_process.py` 是一个自动化的视频转文本处理脚本，它会：

1. 🎬 自动检测 `videos_todo` 目录中的视频文件
2. 🔄 将视频转换为文本并保存到 `results` 目录 
3. 📁 将处理完的视频文件移动到 `videos_done` 目录

## 使用方法

### 基本使用

1. **将视频文件放入待处理目录：**
   ```bash
   # 将您的视频文件复制到 videos_todo 目录
   cp your_video.mp4 videos_todo/
   ```

2. **运行自动处理脚本：**
   ```bash
   python auto_process.py
   ```

3. **查看结果：**
   - 转换后的文本文件将在 `results/` 目录中
   - 处理完的视频文件会自动移动到 `videos_done/` 目录

### 高级选项

```bash
# 使用特定模型和语言
python auto_process.py --model large-v3 --language zh

# 跳过已处理的文件
python auto_process.py --skip-existing

# 使用多线程处理（适合多个文件）
python auto_process.py --workers 2

# 不移动处理完的文件
python auto_process.py --no-move

# 静默模式
python auto_process.py --quiet

# 详细输出
python auto_process.py --verbose
```

## 目录结构

运行脚本后，会自动创建以下目录结构：

```
Video2Text/
├── videos_todo/          # 📥 放置待处理的视频文件
├── results/              # 📄 转换后的文本文件
├── videos_done/          # ✅ 已处理完的视频文件
├── auto_process.py       # 🚀 自动处理脚本
└── mp4_to_text.py       # 📦 原始处理脚本
```

## 支持的文件格式

### 输入视频格式
- `.mp4` - MP4视频
- `.avi` - AVI视频  
- `.mov` - QuickTime视频
- `.mkv` - Matroska视频
- `.flv` - Flash视频
- `.webm` - WebM视频
- `.m4v` - iTunes视频
- `.wmv` - Windows媒体视频
- `.3gp` - 3GP视频
- `.ogv` - Ogg视频

### 输出格式
- `.txt` - 纯文本文件（默认）

## 可用的Whisper模型

| 模型 | 大小 | 内存 | 速度 | 准确度 | 适用场景 |
|------|------|------|------|--------|----------|
| tiny | 39MB | 1GB | 很快 | 低 | 快速测试 |
| base | 142MB | 2GB | 快 | 中等 | 一般使用 |
| small | 244MB | 3GB | 中等 | 好 | 平衡性能 |
| **medium** | 769MB | 5GB | 中等 | 高 | **推荐** |
| large | 1550MB | 8GB | 慢 | 很高 | 高质量 |
| large-v3 | 1550MB | 10GB | 慢 | 很高 | 最新最佳 |

## 支持的语言

- `auto` - 自动检测（推荐）
- `zh` - 中文
- `en` - 英文  
- `ja` - 日文
- `ko` - 韩文
- `fr` - 法文
- `de` - 德文
- `es` - 西班牙文
- `ru` - 俄文
- `pt` - 葡萄牙文
- `it` - 意大利文
- `ar` - 阿拉伯文
- `hi` - 印地语

## 命令行选项

```
用法: python auto_process.py [选项]

模型和处理选项:
  -m, --model MODEL         Whisper模型 (默认: medium)
  -l, --language LANG       音频语言 (默认: auto)
  -d, --device DEVICE       处理设备 (auto/cpu/cuda/mps, 默认: auto)

并行处理:
  -w, --workers NUM         并行处理数量 (默认: 1)

行为选项:
  -s, --skip-existing       跳过已经处理过的文件
  --no-cleanup             不清理临时文件
  --no-move                不移动处理完的文件到videos_done目录

输出控制:
  -v, --verbose            详细输出
  -q, --quiet              静默模式

信息选项:
  --system-info            显示系统信息并退出
  --list-models            列出可用模型并退出
  --help                   显示帮助信息
```

## 示例使用场景

### 1. 批量处理会议录音
```bash
# 将多个会议录音文件放入 videos_todo/
cp meeting_*.mp4 videos_todo/

# 使用中文语言设置处理
python auto_process.py --language zh --verbose
```

### 2. 高质量转录
```bash
# 使用最高质量模型处理重要内容
python auto_process.py --model large-v3 --language auto
```

### 3. 快速处理
```bash
# 使用小模型快速处理大量文件
python auto_process.py --model small --workers 2
```

## 处理流程

1. **检查环境** - 验证依赖和目录结构
2. **扫描文件** - 查找 `videos_todo/` 中的视频文件
3. **加载模型** - 根据设置加载Whisper模型
4. **处理文件** - 逐个或并行处理视频文件
   - 提取音频
   - 语音转文本
   - 保存结果到 `results/`
   - 移动原文件到 `videos_done/`
5. **生成报告** - 显示处理统计信息

## 故障排除

### 常见问题

**Q: 提示"No module named 'whisper'"**
```bash
A: 请安装OpenAI Whisper：
pip install openai-whisper
```

**Q: 处理速度很慢**
```bash
A: 尝试以下优化：
# 使用GPU加速（如果有NVIDIA显卡）
python auto_process.py --device cuda

# 使用更小的模型
python auto_process.py --model small

# 使用Apple Silicon加速（Mac M1/M2）
python auto_process.py --device mps
```

**Q: 转录准确度不高**
```bash
A: 尝试以下改进：
# 使用更大的模型
python auto_process.py --model large-v3

# 指定具体语言
python auto_process.py --language zh  # 中文
python auto_process.py --language en  # 英文
```

**Q: 文件没有被移动到 videos_done**
```bash
A: 检查是否使用了 --no-move 选项，或者权限问题
python auto_process.py --verbose  # 查看详细信息
```

## 性能优化建议

### 硬件配置
- **CPU**: 多核处理器（推荐8核以上）
- **内存**: 8GB以上（large模型需要更多）
- **GPU**: NVIDIA CUDA或Apple Silicon（可选，大幅提升速度）
- **存储**: SSD硬盘（提升文件读写速度）

### 软件优化
```bash
# 1. 使用合适的模型大小
python auto_process.py --model medium  # 平衡性能和质量

# 2. 启用并行处理（适合多文件）
python auto_process.py --workers 2

# 3. 启用GPU加速
python auto_process.py --device cuda   # NVIDIA GPU
python auto_process.py --device mps    # Apple Silicon

# 4. 跳过已处理文件
python auto_process.py --skip-existing
```

## 更新日志

### v1.0.0
- ✨ 新功能：自动化视频转文本处理
- 🚀 新功能：自动文件移动管理
- 📁 新功能：智能目录结构创建
- 🎨 新功能：中文界面和提示
- ⚡ 优化：批量处理性能
- 🔧 修复：跨平台兼容性问题

---

## 技术支持

如果您在使用过程中遇到问题，请：

1. 查看控制台输出的错误信息
2. 使用 `--verbose` 参数获取详细日志
3. 检查 `logs/` 目录中的日志文件
4. 参考项目主README.md中的故障排除部分

**祝您使用愉快！** 🎉 