#!/bin/bash
# cuDNN环境变量配置脚本
# 使用方法: source setup_cudnn_env.sh

# 设置cuDNN库路径
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/miniconda3/lib/python3.13/site-packages/nvidia/cudnn/lib

# 可选：设置CUDA路径（如果需要）
export CUDA_HOME=/usr/local/cuda
export PATH=$CUDA_HOME/bin:$PATH

echo "✓ cuDNN环境变量已设置"
echo "✓ LD_LIBRARY_PATH包含cuDNN路径"
echo ""
echo "现在可以使用GPU运行faster-whisper了！"
echo "测试命令: python mp4_to_text.py -i videos -o results -m medium -d cuda"
