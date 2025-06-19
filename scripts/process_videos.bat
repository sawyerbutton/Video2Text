@echo off
REM MP4ToText - Windows批处理脚本
REM 用于在Windows系统上批量处理视频文件

setlocal enabledelayedexpansion

echo ==========================================
echo        MP4ToText Video Processing
echo ==========================================
echo.

REM 设置默认参数
set INPUT_DIR=input_videos
set OUTPUT_DIR=output_texts
set MODEL=medium
set LANGUAGE=auto
set WORKERS=1
set EXTRA_ARGS=

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python不存在或未添加到PATH
    echo 请安装Python 3.9或更高版本
    pause
    exit /b 1
)

REM 检查是否存在主脚本
if not exist "mp4_to_text.py" (
    echo ERROR: 未找到mp4_to_text.py
    echo 请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 解析命令行参数
:parse_args
if "%~1"=="" goto :start_processing
if "%~1"=="-i" (
    set INPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--input" (
    set INPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-o" (
    set OUTPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--output" (
    set OUTPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-m" (
    set MODEL=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--model" (
    set MODEL=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-l" (
    set LANGUAGE=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--language" (
    set LANGUAGE=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-w" (
    set WORKERS=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--workers" (
    set WORKERS=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--skip-existing" (
    set EXTRA_ARGS=!EXTRA_ARGS! --skip-existing
    shift
    goto :parse_args
)
if "%~1"=="--verbose" (
    set EXTRA_ARGS=!EXTRA_ARGS! --verbose
    shift
    goto :parse_args
)
if "%~1"=="--quiet" (
    set EXTRA_ARGS=!EXTRA_ARGS! --quiet
    shift
    goto :parse_args
)
if "%~1"=="--help" (
    goto :show_help
)
REM 未知参数，跳过
shift
goto :parse_args

:start_processing
REM 显示配置信息
echo 配置信息:
echo   输入目录: %INPUT_DIR%
echo   输出目录: %OUTPUT_DIR%
echo   模型: %MODEL%
echo   语言: %LANGUAGE%
echo   工作线程: %WORKERS%
if not "%EXTRA_ARGS%"=="" echo   额外参数: %EXTRA_ARGS%
echo.

REM 检查输入目录
if not exist "%INPUT_DIR%" (
    echo ERROR: 输入目录不存在: %INPUT_DIR%
    echo 请创建目录或指定正确的路径
    pause
    exit /b 1
)

REM 创建输出目录
if not exist "%OUTPUT_DIR%" (
    echo 创建输出目录: %OUTPUT_DIR%
    mkdir "%OUTPUT_DIR%" 2>nul
    if errorlevel 1 (
        echo ERROR: 无法创建输出目录: %OUTPUT_DIR%
        pause
        exit /b 1
    )
)

REM 检查FFmpeg
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: FFmpeg未找到或未添加到PATH
    echo 请安装FFmpeg以处理视频文件
    echo.
    echo 安装方法:
    echo   1. 从 https://ffmpeg.org/download.html 下载
    echo   2. 使用 choco install ffmpeg
    echo.
    set /p continue="是否继续？ (y/N): "
    if /i not "!continue!"=="y" (
        echo 处理已取消
        pause
        exit /b 1
    )
)

REM 显示系统信息
echo 检查系统兼容性...
python mp4_to_text.py --system-info
if errorlevel 1 (
    echo ERROR: 系统兼容性检查失败
    pause
    exit /b 1
)
echo.

REM 开始处理
echo 开始处理视频文件...
echo 命令: python mp4_to_text.py -i "%INPUT_DIR%" -o "%OUTPUT_DIR%" -m %MODEL% -l %LANGUAGE% -w %WORKERS% %EXTRA_ARGS%
echo.

python mp4_to_text.py -i "%INPUT_DIR%" -o "%OUTPUT_DIR%" -m %MODEL% -l %LANGUAGE% -w %WORKERS% %EXTRA_ARGS%

REM 检查处理结果
if errorlevel 1 (
    echo.
    echo ERROR: 处理过程中出现错误 (错误代码: %errorlevel%^)
    echo 请检查错误信息并重试
    pause
    exit /b 1
) else (
    echo.
    echo ==========================================
    echo          处理完成！
    echo ==========================================
    echo 输出文件保存在: %OUTPUT_DIR%
    echo.
    
    REM 显示输出目录内容
    echo 输出文件列表:
    dir /b "%OUTPUT_DIR%\*.txt" 2>nul
    if errorlevel 1 (
        echo   (没有找到文本文件)
    )
    echo.
)

pause
exit /b 0

:show_help
echo MP4ToText Windows批处理脚本
echo.
echo 用法: process_videos.bat [选项]
echo.
echo 选项:
echo   -i, --input DIR     输入目录 (默认: input_videos^)
echo   -o, --output DIR    输出目录 (默认: output_texts^)
echo   -m, --model MODEL   Whisper模型 (默认: medium^)
echo   -l, --language LANG 语言代码 (默认: auto^)
echo   -w, --workers NUM   工作线程数 (默认: 1^)
echo   --skip-existing     跳过已处理文件
echo   --verbose           详细输出
echo   --quiet             静默模式
echo   --help              显示此帮助
echo.
echo 示例:
echo   process_videos.bat
echo   process_videos.bat -i "C:\Videos" -o "C:\Texts"
echo   process_videos.bat -m large-v3 -l zh --skip-existing
echo.
echo 支持的模型: tiny, base, small, medium, large, large-v2, large-v3
echo 支持的语言: auto, zh, en, ja, ko, fr, de, es, ru, pt, it, ar, hi
echo.
pause
exit /b 0 