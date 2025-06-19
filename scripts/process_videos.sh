#!/bin/bash
# MP4ToText - Linux/macOS Shell脚本
# 用于在Unix系统上批量处理视频文件

set -e  # 出错时立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 使用颜色的echo函数
echo_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

echo_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示标题
echo "=========================================="
echo "       MP4ToText Video Processing"
echo "=========================================="
echo

# 默认参数
INPUT_DIR="input_videos"
OUTPUT_DIR="output_texts"
MODEL="medium"
LANGUAGE="auto"
WORKERS=1
EXTRA_ARGS=""
VERBOSE=false
QUIET=false

# 显示帮助信息
show_help() {
    echo "MP4ToText Linux/macOS Shell脚本"
    echo
    echo "用法: $0 [选项]"
    echo
    echo "选项:"
    echo "  -i, --input DIR     输入目录 (默认: input_videos)"
    echo "  -o, --output DIR    输出目录 (默认: output_texts)"
    echo "  -m, --model MODEL   Whisper模型 (默认: medium)"
    echo "  -l, --language LANG 语言代码 (默认: auto)"
    echo "  -w, --workers NUM   工作线程数 (默认: 1)"
    echo "  -s, --skip-existing 跳过已处理文件"
    echo "  -v, --verbose       详细输出"
    echo "  -q, --quiet         静默模式"
    echo "  -h, --help          显示此帮助"
    echo
    echo "示例:"
    echo "  $0"
    echo "  $0 -i /path/to/videos -o /path/to/texts"
    echo "  $0 -m large-v3 -l zh --skip-existing"
    echo
    echo "支持的模型: tiny, base, small, medium, large, large-v2, large-v3"
    echo "支持的语言: auto, zh, en, ja, ko, fr, de, es, ru, pt, it, ar, hi"
    echo
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--input)
            INPUT_DIR="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -l|--language)
            LANGUAGE="$2"
            shift 2
            ;;
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        -s|--skip-existing)
            EXTRA_ARGS="$EXTRA_ARGS --skip-existing"
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            EXTRA_ARGS="$EXTRA_ARGS --verbose"
            shift
            ;;
        -q|--quiet)
            QUIET=true
            EXTRA_ARGS="$EXTRA_ARGS --quiet"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo_warning "未知参数: $1"
            shift
            ;;
    esac
done

# 检查Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo_error "Python未找到。请安装Python 3.9或更高版本"
    echo_info "安装方法:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

# 选择Python命令
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# 检查Python版本
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if ! $PYTHON_CMD -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
    echo_error "Python版本过低: $PYTHON_VERSION (需要 >= 3.9)"
    exit 1
fi

# 检查主脚本
if [[ ! -f "mp4_to_text.py" ]]; then
    echo_error "未找到mp4_to_text.py"
    echo_info "请确保在项目根目录运行此脚本"
    exit 1
fi

# 显示配置信息
if [[ "$QUIET" != "true" ]]; then
    echo_info "配置信息:"
    echo "  输入目录: $INPUT_DIR"
    echo "  输出目录: $OUTPUT_DIR"
    echo "  模型: $MODEL"
    echo "  语言: $LANGUAGE"
    echo "  工作线程: $WORKERS"
    if [[ -n "$EXTRA_ARGS" ]]; then
        echo "  额外参数:$EXTRA_ARGS"
    fi
    echo
fi

# 检查输入目录
if [[ ! -d "$INPUT_DIR" ]]; then
    echo_error "输入目录不存在: $INPUT_DIR"
    echo_info "请创建目录或指定正确的路径"
    exit 1
fi

# 创建输出目录
if [[ ! -d "$OUTPUT_DIR" ]]; then
    echo_info "创建输出目录: $OUTPUT_DIR"
    if ! mkdir -p "$OUTPUT_DIR"; then
        echo_error "无法创建输出目录: $OUTPUT_DIR"
        exit 1
    fi
fi

# 检查FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo_warning "FFmpeg未找到"
    echo_info "安装方法:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  CentOS/RHEL: sudo yum install ffmpeg (需要EPEL)"
    echo "  macOS: brew install ffmpeg"
    echo
    
    if [[ "$QUIET" != "true" ]]; then
        read -p "是否继续？ (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo_info "处理已取消"
            exit 1
        fi
    else
        echo_warning "在静默模式下继续，但可能无法处理视频文件"
    fi
fi

# 检查输入目录中的视频文件
VIDEO_COUNT=$(find "$INPUT_DIR" -type f \( -iname "*.mp4" -o -iname "*.avi" -o -iname "*.mov" -o -iname "*.mkv" -o -iname "*.flv" \) | wc -l)
if [[ $VIDEO_COUNT -eq 0 ]]; then
    echo_warning "在输入目录中未找到支持的视频文件"
    echo_info "支持的格式: MP4, AVI, MOV, MKV, FLV"
    exit 1
else
    echo_info "找到 $VIDEO_COUNT 个视频文件"
fi

# 显示系统信息
if [[ "$VERBOSE" == "true" ]]; then
    echo_info "检查系统兼容性..."
    if ! $PYTHON_CMD mp4_to_text.py --system-info; then
        echo_error "系统兼容性检查失败"
        exit 1
    fi
    echo
fi

# 设置信号处理（Ctrl+C）
cleanup() {
    echo
    echo_warning "收到中断信号，正在清理..."
    # 这里可以添加清理逻辑
    exit 130
}
trap cleanup INT

# 开始处理
echo_info "开始处理视频文件..."
if [[ "$VERBOSE" == "true" ]]; then
    echo_info "命令: $PYTHON_CMD mp4_to_text.py -i \"$INPUT_DIR\" -o \"$OUTPUT_DIR\" -m $MODEL -l $LANGUAGE -w $WORKERS$EXTRA_ARGS"
fi
echo

# 记录开始时间
START_TIME=$(date +%s)

# 执行处理
if $PYTHON_CMD mp4_to_text.py -i "$INPUT_DIR" -o "$OUTPUT_DIR" -m "$MODEL" -l "$LANGUAGE" -w "$WORKERS" $EXTRA_ARGS; then
    # 计算处理时间
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo
    echo "=========================================="
    echo_success "         处理完成！"
    echo "=========================================="
    echo_info "输出文件保存在: $OUTPUT_DIR"
    echo_info "总处理时间: ${DURATION}秒"
    echo
    
    # 显示输出文件
    TXT_FILES=$(find "$OUTPUT_DIR" -name "*.txt" -type f | wc -l)
    if [[ $TXT_FILES -gt 0 ]]; then
        echo_info "生成了 $TXT_FILES 个文本文件:"
        find "$OUTPUT_DIR" -name "*.txt" -type f -exec basename {} \; | head -10
        if [[ $TXT_FILES -gt 10 ]]; then
            echo "  ... 还有 $((TXT_FILES - 10)) 个文件"
        fi
    else
        echo_warning "没有生成文本文件"
    fi
    echo
    
    exit 0
else
    echo
    echo_error "处理过程中出现错误 (错误代码: $?)"
    echo_info "请检查错误信息并重试"
    exit 1
fi 