# Video2Text 工具集

本目录包含 Video2Text 项目的所有工具脚本和实用程序。

## 🛠️ 工具索引

### 🎯 主要工具（推荐使用）

#### 🤖 自动化处理脚本
- **[auto_process.py](auto_process.py)** - 标准自动化处理脚本
  - 自动处理 `videos_todo` 目录中的所有视频
  - 一键运行，无需参数配置
  - 中文界面，详细进度提示

- **[auto_process_large.py](auto_process_large.py)** - 大文件智能处理脚本  
  - 专门处理 150MB 以上的大文件
  - 智能分层策略：按文件大小选择模型和超时
  - 交互式选择处理层级

### 🔧 实用工具

#### 📊 检查和测试
- **[quick_check.py](quick_check.py)** - 快速系统检查工具
  - 检查依赖安装情况
  - 验证GPU/CUDA配置
  - 测试基本功能

#### 🚀 批处理脚本
- **[process_videos.bat](process_videos.bat)** - Windows批处理脚本
- **[process_videos.sh](process_videos.sh)** - Linux/macOS Shell脚本

## 🎮 使用方法

### 从根目录运行（推荐）
```bash
# 标准自动化处理
python run_auto_process.py

# 大文件智能处理  
python run_large_process.py

# 传统命令行方式
python mp4_to_text.py -i videos_todo -o results
```

### 直接运行工具
```bash
# 进入tools目录
cd tools

# 运行自动化脚本
python auto_process.py

# 运行大文件处理
python auto_process_large.py

# 快速检查系统
python quick_check.py
```

## 📋 工具特性对比

| 工具 | 适用场景 | 特点 | 推荐度 |
|------|----------|------|--------|
| auto_process.py | 日常批量处理 | 简单易用，一键运行 | ⭐⭐⭐⭐⭐ |
| auto_process_large.py | 大文件处理 | 智能分层，超时控制 | ⭐⭐⭐⭐⭐ |
| quick_check.py | 系统诊断 | 快速检查，问题排查 | ⭐⭐⭐⭐ |
| process_videos.bat/.sh | 批处理 | 系统级脚本 | ⭐⭐⭐ |

## 🚨 注意事项

1. **目录要求**: 确保在项目根目录运行脚本
2. **权限设置**: Linux/macOS可能需要执行权限：`chmod +x *.sh`
3. **依赖检查**: 运行前建议先执行 `quick_check.py` 检查环境
4. **GPU配置**: 确保CUDA/PyTorch正确安装以获得最佳性能

---

💡 **提示**: 如果遇到问题，请查看 `../docs/` 目录中的详细文档。 