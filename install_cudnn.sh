#!/bin/bash
# cuDNN 安装脚本 - WSL2 Ubuntu 24.04 + CUDA 12.9
# 此脚本帮助在WSL2环境下安装cuDNN 9.x

set -e

echo "======================================"
echo "  cuDNN 安装指南 - WSL2环境"
echo "======================================"
echo ""

# 检查CUDA版本
echo "1. 检查CUDA安装..."
if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $6}' | cut -c2-)
    echo "   ✓ CUDA版本: $CUDA_VERSION"
    echo "   ✓ CUDA路径: $(which nvcc)"
else
    echo "   ✗ CUDA未安装或nvcc不在PATH中"
    exit 1
fi

# 检查CUDA安装目录
CUDA_HOME="/usr/local/cuda"
if [ -d "$CUDA_HOME" ]; then
    echo "   ✓ CUDA_HOME: $CUDA_HOME"
else
    echo "   ✗ CUDA目录不存在: $CUDA_HOME"
    exit 1
fi

echo ""
echo "2. 检查现有cuDNN安装..."
CUDNN_HEADER="$CUDA_HOME/include/cudnn.h"
if [ -f "$CUDNN_HEADER" ]; then
    echo "   ⚠ 检测到已安装的cuDNN"
    if grep -q "CUDNN_MAJOR" "$CUDNN_HEADER"; then
        CUDNN_MAJOR=$(grep "CUDNN_MAJOR" "$CUDNN_HEADER" | awk '{print $3}')
        CUDNN_MINOR=$(grep "CUDNN_MINOR" "$CUDNN_HEADER" | awk '{print $3}')
        echo "   当前版本: cuDNN $CUDNN_MAJOR.$CUDNN_MINOR"
    fi
else
    echo "   ℹ 未检测到cuDNN安装"
fi

echo ""
echo "======================================"
echo "  安装步骤"
echo "======================================"
echo ""
echo "由于faster-whisper需要cuDNN 9.x，而Ubuntu仓库只提供8.x，"
echo "我们需要从NVIDIA官网手动安装。"
echo ""
echo "方案1：使用pip安装nvidia-cudnn-cu12（推荐！最简单）"
echo "----------------------------------------"
echo "这个方案不需要从NVIDIA官网下载，直接使用pip安装："
echo ""
echo "  pip install nvidia-cudnn-cu12"
echo ""
echo "这会安装cuDNN作为Python包，faster-whisper可以直接使用。"
echo ""
echo "方案2：从NVIDIA官网下载并安装（需要注册账号）"
echo "----------------------------------------"
echo "步骤："
echo "  1. 访问: https://developer.nvidia.com/cudnn-downloads"
echo "  2. 选择: cuDNN v9.x for CUDA 12.x"
echo "  3. 下载: Linux x86_64 (Ubuntu 22.04/24.04)"
echo "  4. 选择: Tar File 或 Deb Package"
echo ""
echo "Tar文件安装步骤："
echo "  tar -xvf cudnn-linux-x86_64-9.x.x.x_cuda12-archive.tar.xz"
echo "  sudo cp cudnn-*-archive/include/cudnn*.h /usr/local/cuda/include"
echo "  sudo cp cudnn-*-archive/lib/libcudnn* /usr/local/cuda/lib64"
echo "  sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*"
echo ""
echo "Deb包安装步骤："
echo "  sudo dpkg -i cudnn-local-repo-*.deb"
echo "  sudo cp /var/cudnn-local-repo-*/cudnn-*-keyring.gpg /usr/share/keyrings/"
echo "  sudo apt-get update"
echo "  sudo apt-get install libcudnn9 libcudnn9-dev"
echo ""
echo "方案3：使用conda安装（如果使用conda环境）"
echo "----------------------------------------"
echo "  conda install -c conda-forge cudnn"
echo ""
echo "======================================"
echo "  推荐执行（最简单）"
echo "======================================"
echo ""
echo "立即执行以下命令安装cuDNN："
echo ""
echo "  pip install nvidia-cudnn-cu12"
echo ""
echo "安装后验证："
echo "  python -c \"import nvidia.cudnn; print('cuDNN version:', nvidia.cudnn.__version__)\""
echo ""
echo "======================================"

# 询问是否立即安装
read -p "是否现在使用pip安装nvidia-cudnn-cu12？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "正在安装nvidia-cudnn-cu12..."
    pip install nvidia-cudnn-cu12
    echo ""
    echo "✓ 安装完成！"
    echo ""
    echo "验证安装："
    python -c "import nvidia.cudnn; print('cuDNN version:', nvidia.cudnn.__version__)"
    echo ""
    echo "现在可以使用GPU运行faster-whisper了！"
    echo "测试命令: python mp4_to_text.py -i videos -o results -m tiny -d cuda"
else
    echo ""
    echo "你可以稍后手动安装。"
fi

echo ""
echo "安装脚本执行完毕！"
