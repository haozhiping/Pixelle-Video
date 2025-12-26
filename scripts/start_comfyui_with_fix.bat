@echo off
REM 启动 ComfyUI 并修复 IndexTTS2 CUDA 内存错误
REM 使用方法：将此文件复制到 ComfyUI 根目录的上一级目录（包含 python_embeded 的目录），然后双击运行

echo ========================================
echo 启动 ComfyUI (修复 IndexTTS2 CUDA 错误)
echo ========================================
echo.

REM 设置环境变量以修复 CUDA 内存错误
set PYTORCH_CUDA_ALLOC_CONF=backend:cudaMalloc

echo 已设置环境变量: PYTORCH_CUDA_ALLOC_CONF=backend:cudaMalloc
echo.

REM 检查 python_embeded 目录
if not exist "python_embeded\python.exe" (
    echo 错误: 未找到 python_embeded\python.exe
    echo 请确保此脚本在包含 python_embeded 目录的父目录中运行
    echo.
    pause
    exit /b 1
)

REM 检查 ComfyUI 目录
if not exist "ComfyUI\main.py" (
    echo 错误: 未找到 ComfyUI\main.py 文件
    echo 请确保 ComfyUI 目录存在
    echo.
    pause
    exit /b 1
)

echo 正在启动 ComfyUI...
echo 使用独立 Python 环境: python_embeded\python.exe
echo 启动参数: --windows-standalone-build --cuda-malloc --normalvram
echo.

REM 启动 ComfyUI（使用独立 Python 环境）
.\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --cuda-malloc --normalvram

pause

