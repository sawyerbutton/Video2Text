# MP4转文字工具技术方案（简化版）

## 📋 项目概述

基于现有Bili2Text项目的核心技术栈，开发一个简单高效的Python脚本工具，用于批量处理指定文件夹中的MP4文件，将视频中的音频内容转录为文字并保存到指定文件夹。

## 🎯 核心功能

### 主要功能
- 📁 **批量文件处理** - 扫描指定文件夹中的所有MP4文件
- 🎵 **音频提取** - 使用FFmpeg从MP4文件中提取音频轨道
- 🎙️ **语音识别** - 基于OpenAI Whisper进行高精度转录
- 📝 **文本输出** - 将转录结果保存为TXT文件
- 🔄 **进度显示** - 命令行实时显示处理进度
- 📊 **批量处理** - 支持多文件顺序或并发处理

### 扩展功能
- 🌍 **多语言支持** - 自动检测或手动指定音频语言
- 🎛️ **音频预处理** - 可选的音频降噪和优化
- 📈 **处理统计** - 输出处理成功率和耗时统计
- 🔧 **灵活配置** - 支持配置文件和命令行参数

## 🏗️ 技术架构

### 系统架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   命令行界面    │◄──►│   核心处理器     │◄──►│   文件系统      │
│  (参数/进度)    │    │  (Python脚本)   │    │ (输入/输出文件) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │   FFmpeg引擎    │    │  Whisper引擎    │
                    │   (音频提取)    │    │   (语音识别)    │
                    └─────────────────┘    └─────────────────┘
```

### 技术栈选择

#### 核心技术
- **Python 3.9+** - 主要开发语言
- **OpenAI Whisper** - 语音识别引擎
  - 支持多种模型：tiny, base, medium, large-v3
  - 高精度多语言支持
  - GPU加速可选
- **FFmpeg-python** - 音频视频处理
  - 音频提取和格式转换
  - 音频预处理和优化

#### 辅助库
- **pathlib** - 文件路径处理
- **argparse** - 命令行参数解析
- **configparser** - 配置文件管理
- **tqdm** - 进度条显示
- **logging** - 日志记录
- **concurrent.futures** - 并发处理（可选）

## 📁 项目结构

```
MP4ToText/
├── 🎯 mp4_to_text.py             # 主执行脚本
├── 🧠 core/                      # 核心功能模块
│   ├── __init__.py              # 模块初始化
│   ├── audio_processor.py       # 音频处理引擎
│   ├── transcriber.py           # 转录引擎封装
│   ├── file_manager.py          # 文件管理工具
│   └── config_manager.py        # 配置管理
├── 📋 config/                    # 配置文件目录
│   ├── config.ini               # 默认配置文件
│   └── models.json              # Whisper模型配置
├── 📂 temp/                      # 临时文件目录
│   └── audio/                   # 提取的音频文件
├── 📊 logs/                      # 日志文件目录
├── 🧪 tests/                     # 测试文件
│   ├── test_audio_processor.py  # 音频处理测试
│   ├── test_transcriber.py      # 转录功能测试
│   └── test_file_manager.py     # 文件管理测试
├── 📝 examples/                  # 示例文件
│   ├── sample_config.ini        # 配置示例
│   └── usage_examples.py        # 使用示例
├── requirements.txt             # Python依赖
├── setup.py                     # 安装脚本
└── README.md                    # 项目说明
```

## 🔧 核心模块设计

### 1. 文件管理模块 (file_manager.py)
```python
class FileManager:
    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.supported_formats = {'.mp4', '.avi', '.mov', '.mkv', '.flv'}
    
    def scan_videos(self):
        """扫描输入目录中的视频文件"""
        pass
    
    def get_output_path(self, video_path):
        """生成对应的输出文件路径"""
        pass
    
    def is_processed(self, video_path):
        """检查视频是否已经处理过"""
        pass
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        pass
```

### 2. 音频处理模块 (audio_processor.py)
```python
class AudioProcessor:
    def __init__(self, temp_dir):
        self.temp_dir = Path(temp_dir)
        self.output_format = 'wav'
        self.sample_rate = 16000
        self.channels = 1
    
    def extract_audio(self, video_path, progress_callback=None):
        """从视频文件提取音频"""
        pass
    
    def get_video_duration(self, video_path):
        """获取视频时长"""
        pass
    
    def preprocess_audio(self, audio_path):
        """音频预处理（可选）"""
        pass
```

### 3. 转录引擎模块 (transcriber.py)
```python
class WhisperTranscriber:
    def __init__(self, model_name='medium', device='auto'):
        self.model_name = model_name
        self.device = device
        self.model = None
    
    def load_model(self):
        """加载Whisper模型"""
        pass
    
    def transcribe(self, audio_path, language='auto', progress_callback=None):
        """执行语音转录"""
        pass
    
    def save_result(self, text, output_path):
        """保存转录结果为TXT文件"""
        pass
```

### 4. 主处理脚本 (mp4_to_text.py)
```python
class MP4ToTextProcessor:
    def __init__(self, config):
        self.config = config
        self.file_manager = FileManager(config.input_dir, config.output_dir)
        self.audio_processor = AudioProcessor(config.temp_dir)
        self.transcriber = WhisperTranscriber(config.model_name, config.device)
    
    def process_single_file(self, video_path):
        """处理单个视频文件"""
        pass
    
    def process_batch(self, max_workers=1):
        """批量处理所有视频文件"""
        pass
    
    def show_progress(self, current, total, filename):
        """显示处理进度"""
        pass
```

## 🔄 处理流程设计

### 1. 程序启动流程
```
解析命令行参数 → 加载配置文件 → 验证输入输出目录 → 初始化处理组件 → 扫描视频文件
```

### 2. 单文件处理流程
```
检查文件是否已处理 → 提取音频轨道 → 加载Whisper模型 → 语音识别 → 保存TXT结果 → 清理临时文件
```

### 3. 批量处理流程
```
获取待处理文件列表 → 显示处理计划 → 逐个/并发处理 → 实时显示进度 → 输出处理统计
```

### 4. 错误处理流程
```
捕获异常 → 记录错误日志 → 清理临时文件 → 跳过当前文件 → 继续处理下一个文件
```

## 💻 命令行接口设计

### 基本使用方式
```bash
# 基本用法：处理单个目录
python mp4_to_text.py --input /path/to/videos --output /path/to/texts

# 指定Whisper模型
python mp4_to_text.py --input ./videos --output ./texts --model medium

# 启用并发处理
python mp4_to_text.py --input ./videos --output ./texts --workers 2

# 指定语言
python mp4_to_text.py --input ./videos --output ./texts --language zh

# 跳过已处理文件
python mp4_to_text.py --input ./videos --output ./texts --skip-existing
```

### 命令行参数说明
```bash
--input, -i          输入目录路径（包含MP4文件）
--output, -o         输出目录路径（保存TXT文件）  
--model, -m          Whisper模型名称 (tiny/base/medium/large-v3)
--language, -l       音频语言 (auto/zh/en/ja/ko等)
--workers, -w        并发处理数量 (默认1)
--config, -c         配置文件路径
--skip-existing, -s  跳过已处理的文件
--cleanup            处理完成后清理临时文件
--verbose, -v        详细输出模式
--quiet, -q          静默模式
--help, -h           显示帮助信息
```

### 使用示例
```bash
# 示例1：处理单个目录，使用默认配置
python mp4_to_text.py -i ./input_videos -o ./output_texts

# 示例2：使用大模型，启用并发，中文语言
python mp4_to_text.py -i ./videos -o ./texts -m large-v3 -w 2 -l zh

# 示例3：使用配置文件
python mp4_to_text.py --config ./config/my_config.ini

# 示例4：静默模式，跳过已处理文件
python mp4_to_text.py -i ./videos -o ./texts -q -s
```

## 📋 配置文件设计

### 默认配置文件 (config.ini)
```ini
[DEFAULT]
# 基本设置
model_name = medium
device = auto
language = auto
max_workers = 1

# 文件处理设置
supported_formats = .mp4,.avi,.mov,.mkv,.flv
skip_existing = false
cleanup_temp = true

# 音频处理设置
audio_format = wav
sample_rate = 16000
channels = 1

# 日志设置
log_level = INFO
log_file = logs/mp4_to_text.log
log_max_size = 10485760
log_backup_count = 5

[WHISPER_MODELS]
# Whisper模型配置
tiny = 39MB,1GB,很快,低精度
base = 142MB,2GB,快速,中等精度
medium = 769MB,5GB,中等,高精度
large-v3 = 1550MB,10GB,较慢,最高精度

[DIRECTORIES]
# 目录设置
temp_dir = temp
log_dir = logs
```

### 处理状态记录 (JSON格式)
```json
{
  "processed_files": {
    "video1.mp4": {
      "processed_at": "2024-01-15T14:30:22Z",
      "output_file": "video1.txt",
      "duration": 1800,
      "model_used": "medium",
      "success": true
    },
    "video2.mp4": {
      "processed_at": "2024-01-15T14:35:10Z", 
      "output_file": "video2.txt",
      "duration": 3600,
      "model_used": "medium",
      "success": false,
      "error": "音频提取失败"
    }
  },
  "statistics": {
    "total_processed": 25,
    "successful": 23,
    "failed": 2,
    "total_duration": 45600,
    "total_processing_time": 7200
  }
}

## ⚙️ 配置管理

### Whisper模型配置
```python
WHISPER_MODELS = {
    'tiny': {
        'size': '39MB',
        'memory_required': '1GB',
        'speed': 'very_fast',
        'accuracy': 'low',
        'recommended_for': '快速测试'
    },
    'base': {
        'size': '142MB', 
        'memory_required': '2GB',
        'speed': 'fast',
        'accuracy': 'medium',
        'recommended_for': '日常使用'
    },
    'medium': {
        'size': '769MB',
        'memory_required': '5GB',
        'speed': 'medium', 
        'accuracy': 'high',
        'recommended_for': '推荐使用',
        'default': True
    },
    'large-v3': {
        'size': '1550MB',
        'memory_required': '10GB',
        'speed': 'slow',
        'accuracy': 'very_high',
        'recommended_for': '最高质量'
    }
}
```

### 支持的文件格式和语言
```python
# 支持的视频格式
SUPPORTED_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.flv']

# 支持的语言
SUPPORTED_LANGUAGES = {
    'auto': '自动检测',
    'zh': '中文',
    'en': '英文',
    'ja': '日文',
    'ko': '韩文',
    'fr': '法文',
    'de': '德文',
    'es': '西班牙文',
    'ru': '俄文'
}
```

## 🚀 部署和安装

### 系统要求
- **Python**: 3.9+ (推荐3.11)
- **FFmpeg**: 最新版本
- **内存**: 4GB+ (取决于选择的Whisper模型)
- **存储**: 足够存储视频文件和转录结果的空间

### 快速安装
```bash
# 1. 克隆或下载项目
git clone https://github.com/your-repo/MP4ToText.git
cd MP4ToText

# 2. 安装Python依赖
pip install -r requirements.txt

# 3. 安装FFmpeg
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS: brew install ffmpeg
# Windows: choco install ffmpeg

# 4. 创建必要的目录
mkdir -p temp/audio logs

# 5. 测试安装
python mp4_to_text.py --help
```

### 使用pip安装
```bash
# 使用setup.py安装
pip install -e .

# 安装后可直接使用命令
mp4-to-text --input ./videos --output ./texts
```

## 🔧 性能优化策略

### 1. 音频处理优化
- **内存管理**: 大文件流式处理，避免内存溢出
- **缓存机制**: 避免重复处理相同文件
- **格式优化**: 选择最适合Whisper的音频格式和参数

### 2. Whisper模型优化
- **模型预加载**: 程序启动时预加载模型，避免重复加载
- **GPU加速**: 自动检测并使用CUDA加速（如果可用）
- **内存优化**: 处理完成后及时释放模型内存

### 3. 批量处理优化
- **并发控制**: 根据系统资源动态调整并发数
- **进度显示**: 使用tqdm显示详细的处理进度
- **错误恢复**: 单个文件失败不影响其他文件处理

## 🔒 错误处理和日志

### 1. 错误处理策略
- **文件验证**: 检查文件格式、大小、完整性
- **异常捕获**: 捕获并记录所有处理异常
- **优雅降级**: 处理失败时清理临时文件
- **重试机制**: 网络或临时错误自动重试

### 2. 日志管理
- **分级日志**: DEBUG、INFO、WARNING、ERROR
- **文件输出**: 自动轮转的日志文件
- **控制台输出**: 根据详细级别控制输出内容
- **处理统计**: 记录成功率、耗时等统计信息

## 🧪 测试策略

### 1. 单元测试
- **音频处理测试**: FFmpeg音频提取功能测试
- **转录引擎测试**: Whisper模型加载和转录测试
- **文件管理测试**: 文件扫描、路径处理、清理功能测试
- **配置管理测试**: 配置文件读取和参数验证测试

### 2. 集成测试
- **端到端测试**: 完整的MP4到TXT转换流程测试
- **批量处理测试**: 多文件并发处理测试
- **错误恢复测试**: 异常情况处理和恢复测试

### 3. 性能测试
- **内存使用测试**: 大文件处理时的内存使用情况
- **处理速度测试**: 不同模型的转录速度对比
- **并发性能测试**: 多文件同时处理的效率

## 📋 开发计划

### 第一阶段 (核心功能 - 1周)
- ✅ 项目结构搭建和依赖配置
- ✅ 音频提取模块开发（FFmpeg集成）
- ✅ Whisper转录模块开发
- ✅ 基础命令行界面

### 第二阶段 (功能完善 - 1周)
- ✅ 文件管理和批量处理
- ✅ 配置文件和参数管理
- ✅ 进度显示和日志系统
- ✅ 错误处理和恢复机制

### 第三阶段 (优化完善 - 1周)
- ✅ 性能优化和内存管理
- ✅ 并发处理支持
- ✅ 测试用例编写
- ✅ 文档和使用说明

## 🎯 技术难点和解决方案

### 1. 大文件处理
**难点**: 大体积视频文件的内存管理
**解决方案**: 
- 流式音频提取，避免一次性加载整个文件
- 分段处理长音频，降低内存峰值
- 及时清理临时文件

### 2. 进度监控
**难点**: 准确显示处理进度
**解决方案**:
- FFmpeg进度回调获取音频提取进度
- Whisper模型内置进度监控
- 使用tqdm显示命令行进度条

### 3. 并发处理
**难点**: 多文件同时处理时的资源控制
**解决方案**:
- 使用concurrent.futures控制并发数
- 根据系统内存动态调整并发数
- 单个文件失败不影响其他文件

### 4. 模型加载优化
**难点**: Whisper模型首次加载耗时较长
**解决方案**:
- 程序启动时预加载模型
- 复用已加载的模型实例
- 提供模型切换选项

## 📊 预期效果和指标

### 性能指标
- **处理速度**: 1小时视频约5-15分钟转录（取决于模型）
- **内存使用**: tiny模型~2GB, medium模型~6GB, large模型~12GB
- **并发处理**: 根据内存自动调整，通常1-3个文件并发

### 使用体验指标
- **启动时间**: < 30秒（包含模型加载）
- **进度精度**: ±5%的进度显示误差
- **错误恢复**: 100%任务失败有明确错误信息
- **文件支持**: 支持主流视频格式MP4/AVI/MOV/MKV/FLV

---

## 📄 总结

本简化版技术方案专注于MP4转文字的核心功能，去除了复杂的Web界面和数据库依赖，通过简洁的Python脚本实现高效的批量视频转录。

### 方案优势：
- 🚀 **简单易用**: 一个命令行工具即可完成所有操作
- 🎯 **功能专注**: 专注核心转录功能，无多余复杂性
- 📦 **部署简便**: 只需Python环境和FFmpeg，无需Web服务器
- 🔧 **配置灵活**: 支持命令行参数和配置文件两种方式
- 💰 **成本低廉**: 无需服务器，本地运行即可

### 适用场景：
- 个人用户批量处理视频文件
- 小团队内部视频转录需求
- 自动化脚本集成
- 科研和学习用途