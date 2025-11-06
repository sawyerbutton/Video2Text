# Video2Text 核心能力集成指南

## 概述

本文档提供Video2Text项目的核心视频转文字能力的技术参考，用于集成到其他项目中。Video2Text基于faster-whisper实现，提供2-8倍性能提升的GPU加速语音转写服务。

**适用场景**：
- 需要将视频/音频转换为文字的自动化工作流
- 需要GPU加速的高性能转写服务
- 需要跨平台支持的转写解决方案
- 需要API化的转写服务

**技术栈**：
- **核心引擎**：faster-whisper >= 1.0.0
- **深度学习**：PyTorch >= 2.0.0
- **音频处理**：FFmpeg, ffmpeg-python
- **语言**：Python 3.9+
- **GPU支持**：CUDA/MPS/CPU

---

## 目录

1. [核心架构](#核心架构)
2. [模块说明](#模块说明)
3. [API设计参考](#api设计参考)
4. [部署方案](#部署方案)
5. [配置管理](#配置管理)
6. [性能优化](#性能优化)
7. [错误处理](#错误处理)
8. [集成示例](#集成示例)

---

## 核心架构

### 处理流程

```
视频文件输入
    ↓
平台/硬件检测 (platform_utils.py)
    ↓
音频提取 (audio_processor.py)
    ↓  FFmpeg → 16kHz WAV
faster-whisper转写 (transcriber.py)
    ↓  GPU/CPU加速
文本输出 (TXT/SRT/VTT/JSON)
    ↓
文件管理 (file_manager.py)
```

### 核心组件

| 模块 | 代码行数 | 功能 | 依赖 |
|------|---------|------|------|
| `platform_utils.py` | 246 | 硬件检测、设备推荐 | torch |
| `audio_processor.py` | 429 | 音频提取、格式转换 | ffmpeg-python |
| `transcriber.py` | 692 | 转写引擎、格式化输出 | faster-whisper |
| `config_manager.py` | 430 | 配置加载、验证 | configparser |
| `file_manager.py` | 462 | 文件发现、路径管理 | pathlib |

### 技术优势

| 特性 | 说明 | 性能指标 |
|------|------|---------|
| **GPU加速** | CUDA/MPS支持 | 2-8x速度提升 |
| **INT8量化** | 低内存模式 | 62%内存减少 |
| **批量处理** | 并行转写 | 线性扩展 |
| **跨平台** | Windows/macOS/Linux | 自动适配 |
| **多模型** | tiny到large-v3 | 灵活选择 |

---

## 模块说明

### 1. 平台检测模块 (platform_utils.py)

**功能**：自动检测系统硬件，推荐最佳配置

**核心API**：

```python
from core.platform_utils import (
    detect_device,
    get_device_info,
    recommend_model,
    recommend_compute_type
)

# 检测可用设备
device = detect_device()
# 返回: 'cuda' | 'mps' | 'cpu'

# 获取设备详细信息
device_info = get_device_info()
# 返回: {
#     'device': 'cuda',
#     'device_name': 'NVIDIA GeForce RTX 4060',
#     'memory_gb': 8.0,
#     'cuda_version': '12.1',
#     'driver_version': '535.54.03'
# }

# 推荐模型
model = recommend_model(memory_gb=8.0)
# 返回: 'large-v3' (内存充足时)

# 推荐计算类型
compute_type = recommend_compute_type(device='cuda', memory_gb=8.0)
# 返回: 'float16' (GPU) | 'int8' (低内存)
```

**集成要点**：
```python
# 在服务启动时调用一次
device_info = get_device_info()
recommended_model = recommend_model(device_info['memory_gb'])
compute_type = recommend_compute_type(
    device_info['device'],
    device_info['memory_gb']
)

# 存储为服务配置
config = {
    'device': device_info['device'],
    'model': recommended_model,
    'compute_type': compute_type
}
```

---

### 2. 音频处理模块 (audio_processor.py)

**功能**：从视频提取音频，转换为Whisper所需格式

**核心API**：

```python
from core.audio_processor import AudioProcessor

# 初始化处理器
processor = AudioProcessor(
    sample_rate=16000,    # Whisper要求16kHz
    channels=1,           # 单声道
    temp_dir='./temp'     # 临时文件目录
)

# 提取音频（简单模式）
audio_path = processor.extract_audio(
    video_path='input.mp4',
    output_path='output.wav'  # 可选，自动生成
)

# 提取音频（带进度回调）
def progress_callback(progress_data):
    """
    progress_data = {
        'percent': 45.5,
        'speed': '2.5x',
        'eta': '00:30',
        'status': 'processing'
    }
    """
    print(f"Progress: {progress_data['percent']:.1f}%")

audio_path = processor.extract_audio_with_progress(
    video_path='input.mp4',
    callback=progress_callback
)

# 获取音频信息
info = processor.get_audio_info('input.mp4')
# 返回: {
#     'duration': 120.5,      # 秒
#     'codec': 'aac',
#     'bitrate': '128k',
#     'sample_rate': 44100
# }

# 清理临时文件
processor.cleanup()
```

**FFmpeg配置**：
```python
# 自定义FFmpeg参数
processor = AudioProcessor(
    sample_rate=16000,
    channels=1,
    ffmpeg_params={
        'ar': 16000,           # 采样率
        'ac': 1,               # 声道数
        'acodec': 'pcm_s16le', # 编码器
        'loglevel': 'error'    # 日志级别
    }
)
```

**错误处理**：
```python
from core.audio_processor import AudioProcessingError

try:
    audio_path = processor.extract_audio(video_path)
except AudioProcessingError as e:
    # 处理音频提取失败
    print(f"Audio extraction failed: {e}")
    # e.details 包含FFmpeg错误信息
except FileNotFoundError:
    # 视频文件不存在
    print("Video file not found")
```

---

### 3. 转写引擎模块 (transcriber.py)

**功能**：faster-whisper转写引擎封装，支持多种输出格式

**核心API**：

```python
from core.transcriber import Transcriber

# 初始化转写器
transcriber = Transcriber(
    model_name='medium',          # 模型选择
    device='auto',                # 设备：'auto' | 'cuda' | 'mps' | 'cpu'
    compute_type='auto',          # 计算类型：'auto' | 'float16' | 'int8'
    language='zh',                # 语言：'zh' | 'en' | 'auto'
    download_root='./models'      # 模型缓存目录
)

# 转写音频文件
result = transcriber.transcribe(
    audio_path='input.wav',
    output_format='txt',          # 输出格式：'txt' | 'srt' | 'vtt' | 'json'
    include_timestamps=True,      # 是否包含时间戳
    word_timestamps=False         # 是否包含词级时间戳
)

# result 结构:
# {
#     'text': '完整文本内容',
#     'segments': [
#         {
#             'start': 0.0,
#             'end': 5.2,
#             'text': '第一段文本',
#             'words': [...]  # 如果启用word_timestamps
#         },
#         ...
#     ],
#     'language': 'zh',
#     'duration': 120.5
# }

# 保存结果
transcriber.save_result(
    result=result,
    output_path='output.txt',
    format='txt'
)
```

**批量处理**：
```python
# 批量转写多个文件
audio_files = ['video1.wav', 'video2.wav', 'video3.wav']

results = transcriber.transcribe_batch(
    audio_paths=audio_files,
    output_format='txt',
    max_workers=2,              # 并行工作线程数
    progress_callback=lambda i, total, file:
        print(f"Processing {i+1}/{total}: {file}")
)

# results: List[dict] - 每个文件的转写结果
```

**流式转写**（适用于长视频）：
```python
# 分段处理大文件
def segment_callback(segment):
    """实时处理每个转写片段"""
    print(f"[{segment['start']:.1f}s - {segment['end']:.1f}s]: {segment['text']}")

result = transcriber.transcribe_stream(
    audio_path='long_video.wav',
    segment_callback=segment_callback,
    beam_size=5,                 # 搜索宽度
    vad_filter=True,             # 启用语音活动检测
    vad_parameters={
        'threshold': 0.5,
        'min_speech_duration_ms': 250,
        'max_speech_duration_s': 30
    }
)
```

**高级选项**：
```python
transcriber = Transcriber(
    model_name='large-v3',
    device='cuda',
    compute_type='float16',
    language='zh',

    # 性能选项
    num_workers=4,               # 特征提取工作线程
    cpu_threads=8,               # CPU线程数

    # 质量选项
    beam_size=5,                 # 解码搜索宽度（1-10）
    best_of=5,                   # 候选数
    temperature=0.0,             # 采样温度（0=贪婪）

    # VAD选项
    vad_filter=True,             # 过滤非语音
    vad_threshold=0.5,

    # 其他选项
    condition_on_previous_text=True,  # 使用上下文
    compression_ratio_threshold=2.4,  # 重复检测
    log_prob_threshold=-1.0,          # 置信度阈值
    no_speech_threshold=0.6           # 静音检测
)
```

---

### 4. 配置管理模块 (config_manager.py)

**功能**：统一配置管理，支持多环境

**核心API**：

```python
from core.config_manager import ConfigManager

# 加载配置
config = ConfigManager(config_path='config/config.ini')

# 获取配置值
model = config.get('PROCESSING', 'model', default='medium')
device = config.get('PROCESSING', 'device', default='auto')
language = config.get('PROCESSING', 'language', default='zh')

# 获取并转换类型
batch_size = config.getint('PROCESSING', 'batch_size', default=1)
vad_enabled = config.getboolean('PROCESSING', 'vad_filter', default=True)
temperature = config.getfloat('PROCESSING', 'temperature', default=0.0)

# 获取整个section
processing_config = config.get_section('PROCESSING')
# 返回: {'model': 'medium', 'device': 'auto', ...}

# 验证配置
if not config.validate():
    errors = config.get_validation_errors()
    print(f"Configuration errors: {errors}")

# 运行时更新配置
config.set('PROCESSING', 'model', 'large-v3')
config.save()  # 保存到文件
```

**配置文件示例** (`config/config.ini`):
```ini
[PROCESSING]
model = medium
device = auto
compute_type = auto
language = zh
batch_size = 1
num_workers = 4

[AUDIO]
sample_rate = 16000
channels = 1
format = wav

[OUTPUT]
format = txt
include_timestamps = true
word_timestamps = false

[TRANSCRIPTION]
beam_size = 5
best_of = 5
temperature = 0.0
vad_filter = true
vad_threshold = 0.5

[PATHS]
temp_dir = ./temp
output_dir = ./output
model_cache_dir = ./models

[LOGGING]
level = INFO
log_file = ./logs/transcriber.log
```

---

### 5. 文件管理模块 (file_manager.py)

**功能**：文件发现、验证、路径管理、清理

**核心API**：

```python
from core.file_manager import FileManager

# 初始化
file_manager = FileManager(
    input_dir='./videos',
    output_dir='./texts',
    temp_dir='./temp',
    supported_formats=['.mp4', '.avi', '.mkv', '.mov', '.webm']
)

# 发现视频文件
video_files = file_manager.discover_videos()
# 返回: [Path('video1.mp4'), Path('video2.avi'), ...]

# 发现未处理的视频
unprocessed = file_manager.find_unprocessed_videos()
# 自动排除已有对应文本文件的视频

# 生成输出路径
output_path = file_manager.get_output_path(
    input_path='videos/2024-01-15/video.mp4',
    format='txt',
    create_dirs=True  # 自动创建目录
)
# 返回: Path('texts/2024-01-15/video.txt')

# 验证文件
if file_manager.validate_video_file('input.mp4'):
    # 文件存在且格式正确
    pass

# 获取文件大小
size_mb = file_manager.get_file_size('video.mp4', unit='MB')

# 清理临时文件
file_manager.cleanup_temp_files(older_than_days=1)

# 归档已处理文件
file_manager.archive_processed(
    video_path='video.mp4',
    archive_dir='./archive'
)
```

---

## API设计参考

### RESTful API设计

基于Video2Text核心能力的Flask API服务设计：

#### 1. 服务端点

```python
from flask import Flask, request, jsonify
from core.transcriber import Transcriber
from core.audio_processor import AudioProcessor
from core.platform_utils import get_device_info
import os
from pathlib import Path

app = Flask(__name__)

# 全局初始化
device_info = get_device_info()
transcriber = Transcriber(
    model_name=os.getenv('WHISPER_MODEL', 'medium'),
    device=device_info['device'],
    compute_type=os.getenv('WHISPER_COMPUTE_TYPE', 'auto')
)
audio_processor = AudioProcessor()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'device': device_info['device'],
        'model': transcriber.model_name,
        'memory_available': device_info.get('memory_gb', 0)
    })

@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    """
    转写视频文件

    请求体:
    {
        "video_path": "/path/to/video.mp4",
        "output_format": "txt",  // txt | srt | vtt | json
        "language": "zh",        // zh | en | auto
        "include_timestamps": true,
        "word_timestamps": false
    }

    响应:
    {
        "success": true,
        "text": "转写文本内容...",
        "segments": [...],
        "language": "zh",
        "duration": 120.5,
        "processing_time": 15.3
    }
    """
    import time
    start_time = time.time()

    try:
        data = request.json
        video_path = data.get('video_path')
        output_format = data.get('output_format', 'txt')
        language = data.get('language', 'zh')
        include_timestamps = data.get('include_timestamps', True)
        word_timestamps = data.get('word_timestamps', False)

        # 验证输入
        if not video_path or not Path(video_path).exists():
            return jsonify({
                'success': False,
                'error': 'Video file not found'
            }), 400

        # 1. 提取音频
        audio_path = audio_processor.extract_audio(video_path)

        # 2. 转写
        result = transcriber.transcribe(
            audio_path=audio_path,
            output_format=output_format,
            language=language,
            include_timestamps=include_timestamps,
            word_timestamps=word_timestamps
        )

        # 3. 清理临时文件
        audio_processor.cleanup()

        processing_time = time.time() - start_time

        return jsonify({
            'success': True,
            'text': result['text'],
            'segments': result['segments'] if include_timestamps else None,
            'language': result['language'],
            'duration': result['duration'],
            'processing_time': processing_time
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/transcribe/batch', methods=['POST'])
def transcribe_batch():
    """
    批量转写多个视频

    请求体:
    {
        "video_paths": ["/path/to/video1.mp4", "/path/to/video2.mp4"],
        "output_format": "txt",
        "language": "zh",
        "max_workers": 2
    }

    响应:
    {
        "success": true,
        "results": [
            {"video": "video1.mp4", "success": true, "text": "..."},
            {"video": "video2.mp4", "success": true, "text": "..."}
        ],
        "total_processing_time": 45.2
    }
    """
    import time
    start_time = time.time()

    try:
        data = request.json
        video_paths = data.get('video_paths', [])
        output_format = data.get('output_format', 'txt')
        language = data.get('language', 'zh')
        max_workers = data.get('max_workers', 1)

        # 1. 提取所有音频文件
        audio_paths = []
        for video_path in video_paths:
            if Path(video_path).exists():
                audio_path = audio_processor.extract_audio(video_path)
                audio_paths.append(audio_path)

        # 2. 批量转写
        results = transcriber.transcribe_batch(
            audio_paths=audio_paths,
            output_format=output_format,
            language=language,
            max_workers=max_workers
        )

        # 3. 清理临时文件
        audio_processor.cleanup()

        processing_time = time.time() - start_time

        return jsonify({
            'success': True,
            'results': [
                {
                    'video': Path(vp).name,
                    'success': True,
                    'text': r['text'],
                    'duration': r['duration']
                }
                for vp, r in zip(video_paths, results)
            ],
            'total_processing_time': processing_time
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/models', methods=['GET'])
def list_models():
    """列出可用模型"""
    from core.config_manager import ConfigManager

    config = ConfigManager()
    models = config.get_available_models()

    return jsonify({
        'models': models,
        'current_model': transcriber.model_name,
        'device': device_info['device']
    })

@app.route('/device', methods=['GET'])
def get_device():
    """获取设备信息"""
    return jsonify(device_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
```

#### 2. 异步任务API（适用于长视频）

```python
from flask import Flask, request, jsonify
from celery import Celery
import redis

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task(bind=True)
def transcribe_video_task(self, video_path, options):
    """异步转写任务"""
    from core.transcriber import Transcriber
    from core.audio_processor import AudioProcessor

    # 更新任务状态
    self.update_state(state='PROCESSING', meta={'progress': 0})

    try:
        audio_processor = AudioProcessor()
        transcriber = Transcriber(**options)

        # 提取音频
        self.update_state(state='PROCESSING', meta={'progress': 30, 'status': 'Extracting audio'})
        audio_path = audio_processor.extract_audio(video_path)

        # 转写
        self.update_state(state='PROCESSING', meta={'progress': 60, 'status': 'Transcribing'})
        result = transcriber.transcribe(audio_path)

        # 清理
        audio_processor.cleanup()

        return {
            'success': True,
            'result': result,
            'progress': 100
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/transcribe/async', methods=['POST'])
def transcribe_async():
    """
    异步转写接口

    响应:
    {
        "task_id": "abc123...",
        "status": "PENDING"
    }
    """
    data = request.json
    video_path = data.get('video_path')
    options = {
        'model_name': data.get('model', 'medium'),
        'language': data.get('language', 'zh'),
        'device': 'auto'
    }

    task = transcribe_video_task.apply_async(args=[video_path, options])

    return jsonify({
        'task_id': task.id,
        'status': 'PENDING'
    }), 202

@app.route('/transcribe/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    查询任务状态

    响应:
    {
        "task_id": "abc123...",
        "status": "PROCESSING",
        "progress": 60,
        "result": null
    }
    """
    task = transcribe_video_task.AsyncResult(task_id)

    if task.state == 'PENDING':
        response = {
            'task_id': task_id,
            'status': 'PENDING',
            'progress': 0
        }
    elif task.state == 'PROCESSING':
        response = {
            'task_id': task_id,
            'status': 'PROCESSING',
            'progress': task.info.get('progress', 0),
            'message': task.info.get('status', '')
        }
    elif task.state == 'SUCCESS':
        response = {
            'task_id': task_id,
            'status': 'SUCCESS',
            'progress': 100,
            'result': task.info
        }
    else:
        response = {
            'task_id': task_id,
            'status': task.state,
            'error': str(task.info)
        }

    return jsonify(response)
```

---

## 部署方案

### 1. Docker部署（推荐）

#### Dockerfile

```dockerfile
# whisper-service/Dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制Video2Text核心模块
COPY core/ /app/core/
COPY config/ /app/config/

# 复制API服务
COPY whisper-service/app.py /app/
COPY whisper-service/requirements.txt /app/

# 安装Python依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 创建必要目录
RUN mkdir -p /app/models /app/temp /app/logs

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8000/health')"

# 启动服务
CMD ["python3", "app.py"]
```

#### requirements.txt

```txt
# whisper-service/requirements.txt

# 核心依赖
faster-whisper>=1.0.0
torch>=2.0.0
torchaudio>=2.0.0

# 音频处理
ffmpeg-python>=0.2.0

# Web服务
flask>=2.3.0
gunicorn>=21.2.0

# 异步任务（可选）
celery>=5.3.0
redis>=5.0.0

# 工具库
tqdm>=4.65.0
colorama>=0.4.6
pathvalidate>=3.0.0
python-dotenv>=1.0.0

# 日志和监控
prometheus-client>=0.17.0
```

#### docker-compose.yml

```yaml
# docker-compose.yml (添加到YouTube项目)

services:
  whisper-service:
    build:
      context: .
      dockerfile: whisper-service/Dockerfile
    container_name: whisper-service
    restart: unless-stopped

    # GPU支持
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
        limits:
          memory: 8G

    # 环境变量
    environment:
      - WHISPER_MODEL=${WHISPER_MODEL:-medium}
      - WHISPER_DEVICE=cuda
      - WHISPER_COMPUTE_TYPE=${WHISPER_COMPUTE_TYPE:-float16}
      - WHISPER_LANGUAGE=${WHISPER_LANGUAGE:-zh}
      - FLASK_ENV=production
      - LOG_LEVEL=INFO

    # 端口映射
    ports:
      - "8000:8000"

    # 卷挂载
    volumes:
      - ./whisper-service/models:/app/models
      - ./storage/LLM-X:/app/storage
      - ./whisper-service/logs:/app/logs

    # 健康检查
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

    # 网络
    networks:
      - automation-network

networks:
  automation-network:
    driver: bridge
```

### 2. 生产环境部署

#### Gunicorn配置

```python
# whisper-service/gunicorn_config.py

import multiprocessing

# 服务器配置
bind = "0.0.0.0:8000"
workers = 1  # GPU服务通常使用单worker
worker_class = "sync"
worker_connections = 1000
timeout = 600  # 长视频处理需要更长超时
keepalive = 5

# 日志
accesslog = "/app/logs/access.log"
errorlog = "/app/logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程名
proc_name = "whisper-service"

# 预加载应用
preload_app = True

# 优雅重启
graceful_timeout = 30
max_requests = 1000
max_requests_jitter = 50

# 钩子函数
def on_starting(server):
    """服务器启动时"""
    print("Whisper service is starting...")

def when_ready(server):
    """服务器准备就绪时"""
    print("Whisper service is ready to accept connections")

def on_exit(server):
    """服务器退出时"""
    print("Whisper service is shutting down...")
```

启动命令：
```bash
gunicorn -c gunicorn_config.py app:app
```

### 3. 性能监控

#### Prometheus指标

```python
# whisper-service/app.py (添加监控)

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from flask import Response

# 定义指标
transcription_requests = Counter(
    'transcription_requests_total',
    'Total transcription requests',
    ['status', 'format']
)

transcription_duration = Histogram(
    'transcription_duration_seconds',
    'Transcription processing time',
    ['model', 'language']
)

active_transcriptions = Gauge(
    'active_transcriptions',
    'Number of active transcriptions'
)

gpu_memory_usage = Gauge(
    'gpu_memory_usage_bytes',
    'GPU memory usage'
)

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), mimetype='text/plain')

@app.before_request
def before_request():
    """请求开始时"""
    active_transcriptions.inc()

@app.after_request
def after_request(response):
    """请求结束时"""
    active_transcriptions.dec()
    return response

# 在transcribe_video函数中添加指标记录
@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    import time
    start_time = time.time()

    try:
        # ... 转写逻辑 ...

        # 记录成功指标
        transcription_requests.labels(status='success', format=output_format).inc()
        transcription_duration.labels(model=transcriber.model_name, language=language).observe(
            time.time() - start_time
        )

        return jsonify(result)
    except Exception as e:
        # 记录失败指标
        transcription_requests.labels(status='error', format=output_format).inc()
        raise
```

---

## 配置管理

### 环境变量

```bash
# .env (添加到YouTube项目)

# Whisper服务配置
WHISPER_MODEL=medium              # tiny | base | small | medium | large | large-v3 | turbo
WHISPER_DEVICE=cuda               # cuda | mps | cpu | auto
WHISPER_COMPUTE_TYPE=float16      # float16 | int8 | int8_float16 | auto
WHISPER_LANGUAGE=zh               # zh | en | auto
WHISPER_NUM_WORKERS=4             # 特征提取工作线程
WHISPER_BEAM_SIZE=5               # 解码搜索宽度

# VAD配置
WHISPER_VAD_FILTER=true           # 启用语音活动检测
WHISPER_VAD_THRESHOLD=0.5         # VAD阈值
WHISPER_VAD_MIN_SPEECH_MS=250     # 最小语音片段（毫秒）

# 性能配置
WHISPER_BATCH_SIZE=1              # 批处理大小
WHISPER_MAX_WORKERS=2             # 最大并行工作数
WHISPER_TIMEOUT=3600              # 单个任务超时（秒）

# 存储配置
WHISPER_MODEL_CACHE=/app/models   # 模型缓存目录
WHISPER_TEMP_DIR=/app/temp        # 临时文件目录
WHISPER_LOG_DIR=/app/logs         # 日志目录

# 音频处理配置
AUDIO_SAMPLE_RATE=16000           # 采样率
AUDIO_CHANNELS=1                  # 声道数
AUDIO_FORMAT=wav                  # 音频格式

# API配置
WHISPER_API_HOST=0.0.0.0
WHISPER_API_PORT=8000
WHISPER_API_WORKERS=1             # Gunicorn workers
WHISPER_API_TIMEOUT=600           # API超时

# 日志配置
LOG_LEVEL=INFO                    # DEBUG | INFO | WARNING | ERROR
LOG_FORMAT=json                   # json | text
```

### 模型选择指南

| 模型 | 参数量 | 内存需求 (float16) | 内存需求 (int8) | 相对速度 | 推荐场景 |
|------|--------|-------------------|----------------|---------|---------|
| tiny | 39M | ~1GB | ~600MB | 32x | 快速预览、低资源 |
| base | 74M | ~1GB | ~700MB | 16x | 快速处理、一般质量 |
| small | 244M | ~2GB | ~1GB | 6x | 平衡速度和质量 |
| medium | 769M | ~5GB | ~2.5GB | 2x | **推荐：生产环境** |
| large | 1550M | ~10GB | ~5GB | 1x | 最高质量（英文） |
| large-v3 | 1550M | ~10GB | ~5GB | 1x | **最高质量（多语言）** |
| turbo | 809M | ~6GB | ~3GB | 8x | **快速+高质量** |

**GPU VRAM推荐**：
- 4GB: tiny, base
- 6GB: small, medium (int8)
- 8GB: **medium (float16)**, large (int8)
- 12GB+: large-v3 (float16), turbo

**RTX 4060 (8GB) 推荐配置**：
```env
WHISPER_MODEL=medium              # 或 turbo（更快）
WHISPER_COMPUTE_TYPE=float16
WHISPER_DEVICE=cuda
```

---

## 性能优化

### 1. GPU优化

```python
# 启用TensorFloat-32 (Ampere架构及以上)
import torch
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# CUDA优化
torch.cuda.set_per_process_memory_fraction(0.9)  # 限制90% GPU内存
torch.backends.cudnn.benchmark = True  # 自动优化卷积算法
```

### 2. 批处理优化

```python
# 并行处理多个短视频
from concurrent.futures import ThreadPoolExecutor
import queue

class TranscriptionPool:
    def __init__(self, max_workers=2):
        self.transcriber = Transcriber()
        self.audio_processor = AudioProcessor()
        self.max_workers = max_workers
        self.task_queue = queue.Queue()

    def process_batch(self, video_paths):
        """批量处理视频"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for video_path in video_paths:
                future = executor.submit(self._process_single, video_path)
                futures.append(future)

            results = [f.result() for f in futures]
        return results

    def _process_single(self, video_path):
        """处理单个视频"""
        audio_path = self.audio_processor.extract_audio(video_path)
        result = self.transcriber.transcribe(audio_path)
        return result
```

### 3. 缓存策略

```python
from functools import lru_cache
import hashlib

class CachedTranscriber:
    def __init__(self):
        self.transcriber = Transcriber()
        self.cache_dir = Path('./cache')
        self.cache_dir.mkdir(exist_ok=True)

    def get_cache_key(self, video_path, options):
        """生成缓存键"""
        # 使用文件hash + 选项作为键
        with open(video_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        option_str = json.dumps(options, sort_keys=True)
        cache_key = f"{file_hash}_{hashlib.md5(option_str.encode()).hexdigest()}"
        return cache_key

    def transcribe(self, video_path, **options):
        """带缓存的转写"""
        cache_key = self.get_cache_key(video_path, options)
        cache_file = self.cache_dir / f"{cache_key}.json"

        # 检查缓存
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)

        # 执行转写
        result = self.transcriber.transcribe(video_path, **options)

        # 保存缓存
        with open(cache_file, 'w') as f:
            json.dump(result, f)

        return result
```

### 4. VAD优化

```python
# 使用VAD跳过静音片段，减少处理时间
transcriber = Transcriber(
    vad_filter=True,
    vad_parameters={
        'threshold': 0.5,           # 降低阈值以保留更多语音
        'min_speech_duration_ms': 250,  # 最小语音片段
        'max_speech_duration_s': 30,    # 最大语音片段
        'min_silence_duration_ms': 2000,  # 最小静音时长
        'speech_pad_ms': 400        # 语音前后填充
    }
)
```

### 5. 长视频分段处理

```python
from pydub import AudioSegment
from pydub.silence import split_on_silence

def transcribe_long_video(video_path, segment_duration=600):
    """
    分段处理长视频

    Args:
        video_path: 视频路径
        segment_duration: 分段时长（秒），默认10分钟
    """
    # 提取音频
    audio_path = audio_processor.extract_audio(video_path)
    audio = AudioSegment.from_wav(audio_path)

    # 按静音分割
    segments = split_on_silence(
        audio,
        min_silence_len=2000,      # 2秒静音
        silence_thresh=-40,         # 静音阈值
        keep_silence=500            # 保留静音
    )

    # 合并小片段到目标时长
    merged_segments = []
    current_segment = AudioSegment.empty()

    for segment in segments:
        if len(current_segment) + len(segment) < segment_duration * 1000:
            current_segment += segment
        else:
            merged_segments.append(current_segment)
            current_segment = segment

    if len(current_segment) > 0:
        merged_segments.append(current_segment)

    # 转写每个片段
    results = []
    for i, segment in enumerate(merged_segments):
        segment_path = f"/tmp/segment_{i}.wav"
        segment.export(segment_path, format="wav")

        result = transcriber.transcribe(segment_path)
        results.append(result)

        os.remove(segment_path)

    # 合并结果
    full_text = "\n\n".join([r['text'] for r in results])
    return full_text
```

### 6. 性能基准测试

```python
import time
import statistics

def benchmark_transcription(video_paths, model='medium', device='cuda'):
    """
    性能基准测试

    返回:
    {
        'model': 'medium',
        'device': 'cuda',
        'total_duration': 600.0,  # 视频总时长
        'total_time': 120.0,      # 处理总时间
        'avg_rtf': 0.2,           # 平均实时因子
        'throughput': 5.0         # 吞吐量（videos/min）
    }
    """
    transcriber = Transcriber(model_name=model, device=device)
    audio_processor = AudioProcessor()

    processing_times = []
    video_durations = []

    start_time = time.time()

    for video_path in video_paths:
        # 获取视频时长
        info = audio_processor.get_audio_info(video_path)
        duration = info['duration']
        video_durations.append(duration)

        # 转写
        t0 = time.time()
        audio_path = audio_processor.extract_audio(video_path)
        result = transcriber.transcribe(audio_path)
        t1 = time.time()

        processing_times.append(t1 - t0)

    total_time = time.time() - start_time
    total_duration = sum(video_durations)

    # 计算实时因子 (RTF = processing_time / video_duration)
    rtfs = [pt / vd for pt, vd in zip(processing_times, video_durations)]

    return {
        'model': model,
        'device': device,
        'num_videos': len(video_paths),
        'total_duration': total_duration,
        'total_time': total_time,
        'avg_processing_time': statistics.mean(processing_times),
        'avg_rtf': statistics.mean(rtfs),
        'min_rtf': min(rtfs),
        'max_rtf': max(rtfs),
        'throughput': len(video_paths) / (total_time / 60)  # videos/min
    }

# 使用示例
results = benchmark_transcription(
    video_paths=['video1.mp4', 'video2.mp4', 'video3.mp4'],
    model='medium',
    device='cuda'
)
print(json.dumps(results, indent=2))
```

---

## 错误处理

### 1. 异常类定义

```python
# core/exceptions.py

class TranscriptionError(Exception):
    """转写基础异常"""
    pass

class AudioProcessingError(TranscriptionError):
    """音频处理异常"""
    def __init__(self, message, video_path=None, ffmpeg_error=None):
        self.video_path = video_path
        self.ffmpeg_error = ffmpeg_error
        super().__init__(message)

class ModelLoadError(TranscriptionError):
    """模型加载异常"""
    def __init__(self, message, model_name=None):
        self.model_name = model_name
        super().__init__(message)

class DeviceError(TranscriptionError):
    """设备异常"""
    def __init__(self, message, requested_device=None):
        self.requested_device = requested_device
        super().__init__(message)

class TranscriptionTimeout(TranscriptionError):
    """转写超时异常"""
    def __init__(self, message, elapsed_time=None):
        self.elapsed_time = elapsed_time
        super().__init__(message)
```

### 2. 错误处理示例

```python
from core.exceptions import *
import logging

logger = logging.getLogger(__name__)

def safe_transcribe(video_path, max_retries=3, retry_delay=5):
    """
    带重试和错误处理的安全转写

    Args:
        video_path: 视频路径
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）

    Returns:
        dict: 转写结果或错误信息
    """
    for attempt in range(max_retries):
        try:
            # 提取音频
            audio_path = audio_processor.extract_audio(video_path)

            # 转写
            result = transcriber.transcribe(audio_path)

            # 清理
            audio_processor.cleanup()

            return {
                'success': True,
                'result': result,
                'attempts': attempt + 1
            }

        except AudioProcessingError as e:
            logger.error(f"Audio extraction failed for {video_path}: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                return {
                    'success': False,
                    'error': 'audio_extraction_failed',
                    'message': str(e),
                    'video_path': e.video_path
                }

        except ModelLoadError as e:
            logger.error(f"Model load failed: {e}")
            return {
                'success': False,
                'error': 'model_load_failed',
                'message': str(e),
                'model_name': e.model_name
            }

        except DeviceError as e:
            logger.error(f"Device error: {e}")
            # 尝试降级到CPU
            if attempt == 0 and e.requested_device != 'cpu':
                logger.info("Falling back to CPU...")
                transcriber = Transcriber(device='cpu')
                continue
            else:
                return {
                    'success': False,
                    'error': 'device_error',
                    'message': str(e)
                }

        except TranscriptionTimeout as e:
            logger.error(f"Transcription timeout: {e}")
            return {
                'success': False,
                'error': 'timeout',
                'message': str(e),
                'elapsed_time': e.elapsed_time
            }

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return {
                    'success': False,
                    'error': 'unexpected_error',
                    'message': str(e)
                }

    return {
        'success': False,
        'error': 'max_retries_exceeded'
    }
```

### 3. API错误响应

```python
# Flask错误处理器
from flask import jsonify

@app.errorhandler(AudioProcessingError)
def handle_audio_error(error):
    return jsonify({
        'success': False,
        'error': 'audio_processing_error',
        'message': str(error),
        'video_path': error.video_path
    }), 400

@app.errorhandler(ModelLoadError)
def handle_model_error(error):
    return jsonify({
        'success': False,
        'error': 'model_load_error',
        'message': str(error),
        'model_name': error.model_name
    }), 500

@app.errorhandler(DeviceError)
def handle_device_error(error):
    return jsonify({
        'success': False,
        'error': 'device_error',
        'message': str(error),
        'requested_device': error.requested_device
    }), 500

@app.errorhandler(TranscriptionTimeout)
def handle_timeout_error(error):
    return jsonify({
        'success': False,
        'error': 'timeout',
        'message': str(error),
        'elapsed_time': error.elapsed_time
    }), 504

@app.errorhandler(Exception)
def handle_generic_error(error):
    logger.exception("Unhandled exception")
    return jsonify({
        'success': False,
        'error': 'internal_server_error',
        'message': 'An unexpected error occurred'
    }), 500
```

---

## 集成示例

### YouTube Content Automation Pipeline集成

#### 步骤1：集成核心模块

```bash
# 在YouTube项目根目录
cd /path/to/YouTube-Content-Automation-Pipeline

# 创建whisper-service目录
mkdir -p whisper-service

# 复制Video2Text核心模块
cp -r /path/to/Video2Text/core whisper-service/
cp -r /path/to/Video2Text/config whisper-service/

# 创建API服务文件
touch whisper-service/app.py
touch whisper-service/Dockerfile
touch whisper-service/requirements.txt
touch whisper-service/gunicorn_config.py
```

#### 步骤2：实现Flask API（参考前面的API设计）

```python
# whisper-service/app.py
# （使用前面"API设计参考"章节的完整代码）
```

#### 步骤3：更新docker-compose.yml

```yaml
# 在现有的docker-compose.yml中添加whisper-service
services:
  # ... 现有的n8n服务 ...

  whisper-service:
    build:
      context: .
      dockerfile: whisper-service/Dockerfile
    container_name: whisper-service
    restart: unless-stopped

    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
        limits:
          memory: 8G

    environment:
      - WHISPER_MODEL=${WHISPER_MODEL:-medium}
      - WHISPER_DEVICE=cuda
      - WHISPER_COMPUTE_TYPE=${WHISPER_COMPUTE_TYPE:-float16}
      - WHISPER_LANGUAGE=${WHISPER_LANGUAGE:-zh}

    ports:
      - "8000:8000"

    volumes:
      - ./whisper-service/models:/app/models
      - ./storage/LLM-X:/app/storage
      - ./whisper-service/logs:/app/logs

    networks:
      - automation-network
```

#### 步骤4：配置N8N工作流调用

在N8N的video-processor工作流中，添加HTTP Request节点调用Whisper服务：

**节点配置**：
- **Method**: POST
- **URL**: `http://whisper-service:8000/transcribe`
- **Body**:
```json
{
  "video_path": "{{ $json.video_path }}",
  "output_format": "txt",
  "language": "zh",
  "include_timestamps": true
}
```

**响应处理**：
```javascript
// 在Function节点中处理响应
const response = $input.first().json;

if (response.success) {
  return {
    video_id: items[0].json.video_id,
    text: response.text,
    duration: response.duration,
    language: response.language,
    processing_time: response.processing_time
  };
} else {
  throw new Error(`Transcription failed: ${response.error}`);
}
```

#### 步骤5：更新.env配置

```bash
# 添加到.env文件

# Whisper服务配置
WHISPER_MODEL=medium
WHISPER_DEVICE=cuda
WHISPER_COMPUTE_TYPE=float16
WHISPER_LANGUAGE=zh
WHISPER_API_URL=http://whisper-service:8000
```

#### 步骤6：部署和测试

```bash
# 构建并启动服务
docker-compose up -d --build whisper-service

# 查看日志
docker-compose logs -f whisper-service

# 测试健康检查
curl http://localhost:8000/health

# 测试转写API
curl -X POST http://localhost:8000/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/app/storage/videos/test.mp4",
    "output_format": "txt",
    "language": "zh"
  }'
```

#### 步骤7：监控和优化

```bash
# 监控GPU使用
watch -n 1 nvidia-smi

# 监控容器资源
docker stats whisper-service

# 查看Prometheus指标
curl http://localhost:8000/metrics
```

---

## 最佳实践

### 1. 生产环境建议

- ✅ 使用`medium`或`turbo`模型（平衡速度和质量）
- ✅ 启用GPU加速（`device=cuda`）
- ✅ 使用float16计算类型（GPU）或int8（低内存）
- ✅ 启用VAD过滤减少处理时间
- ✅ 设置合理的超时时间（根据视频长度）
- ✅ 实现错误重试机制（最多3次）
- ✅ 添加Prometheus监控
- ✅ 配置日志滚动和归档
- ✅ 定期清理临时文件
- ✅ 使用Gunicorn作为生产服务器

### 2. 性能调优建议

| 场景 | 推荐配置 | 预期性能 |
|------|---------|---------|
| 实时转写 | model=turbo, device=cuda, compute_type=float16 | ~8x实时速度 |
| 高质量批处理 | model=large-v3, device=cuda, batch_size=2 | 最高质量 |
| 低内存环境 | model=medium, compute_type=int8, vad_filter=true | 2.5GB显存 |
| CPU环境 | model=small, device=cpu, compute_type=int8 | ~1x实时速度 |

### 3. 安全建议

- 🔒 验证所有输入路径（防止路径遍历攻击）
- 🔒 限制文件大小（防止DoS）
- 🔒 使用速率限制（防止滥用）
- 🔒 添加身份验证（API Key或JWT）
- 🔒 敏感信息使用环境变量
- 🔒 启用HTTPS（生产环境）
- 🔒 日志脱敏（不记录敏感路径）

### 4. 扩展性建议

- 📈 使用消息队列（Celery + Redis）处理长任务
- 📈 实现负载均衡（多个Whisper服务实例）
- 📈 添加缓存层（Redis）避免重复处理
- 📈 使用对象存储（S3/MinIO）替代本地存储
- 📈 实现优雅降级（GPU不可用时切换CPU）

---

## 故障排查

### 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| GPU不可用 | nvidia-docker未安装 | 安装nvidia-docker2并重启Docker |
| 内存溢出 | 模型太大 | 使用更小模型或int8计算类型 |
| 转写速度慢 | 使用CPU | 启用GPU加速 |
| 音频提取失败 | FFmpeg未安装 | 安装FFmpeg |
| 模型下载失败 | 网络问题 | 配置代理或手动下载模型 |
| API超时 | 视频太长 | 增加timeout设置或分段处理 |

### 调试命令

```bash
# 检查GPU
nvidia-smi

# 测试Docker GPU支持
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# 进入容器调试
docker-compose exec whisper-service bash

# 测试faster-whisper
python3 -c "from faster_whisper import WhisperModel; model = WhisperModel('tiny', device='cuda'); print('OK')"

# 测试音频提取
ffmpeg -i test.mp4 -ar 16000 -ac 1 test.wav

# 查看详细日志
docker-compose logs --tail=200 whisper-service
```

---

## 版本兼容性

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.9+ | 推荐3.10 |
| faster-whisper | 1.0.0+ | 核心依赖 |
| PyTorch | 2.0.0+ | 深度学习框架 |
| CUDA | 11.8+ | GPU加速 |
| FFmpeg | 4.0+ | 音频处理 |
| Docker | 20.10+ | 容器化 |
| nvidia-docker | 2.0+ | GPU容器支持 |

---

## 参考资源

- **Video2Text项目**：https://github.com/yourusername/Video2Text
- **faster-whisper**：https://github.com/guillaumekln/faster-whisper
- **OpenAI Whisper**：https://github.com/openai/whisper
- **FFmpeg**：https://ffmpeg.org/
- **PyTorch**：https://pytorch.org/
- **Flask**：https://flask.palletsprojects.com/
- **Gunicorn**：https://gunicorn.org/
- **Docker**：https://docs.docker.com/

---

## 支持

如有技术问题或集成疑问，请参考：
- Video2Text README: `README.md`
- 架构文档: `ref/architecture.md`
- API文档: `ref/api-reference.md`
- 模型文档: `ref/models.md`
- 工作流文档: `ref/workflows.md`

---

**文档版本**: 1.0.0
**最后更新**: 2024-11
**作者**: Video2Text Team

