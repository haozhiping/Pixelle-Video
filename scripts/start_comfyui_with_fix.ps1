# PowerShell 脚本：启动 ComfyUI 并修复 IndexTTS2 CUDA 内存错误
# 使用方法：在 PowerShell 中运行此脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动 ComfyUI (修复 IndexTTS2 CUDA 错误)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置环境变量以修复 CUDA 内存错误
$env:PYTORCH_CUDA_ALLOC_CONF = "backend:cudaMalloc"

Write-Host "已设置环境变量: PYTORCH_CUDA_ALLOC_CONF=backend:cudaMalloc" -ForegroundColor Green
Write-Host ""

# 检查 python_embeded 目录
if (-not (Test-Path "python_embeded\python.exe")) {
    Write-Host "错误: 未找到 python_embeded\python.exe" -ForegroundColor Red
    Write-Host "请确保此脚本在包含 python_embeded 目录的父目录中运行" -ForegroundColor Red
    Write-Host ""
    Read-Host "按 Enter 键退出"
    exit 1
}

# 检查 ComfyUI 目录
if (-not (Test-Path "ComfyUI\main.py")) {
    Write-Host "错误: 未找到 ComfyUI\main.py 文件" -ForegroundColor Red
    Write-Host "请确保 ComfyUI 目录存在" -ForegroundColor Red
    Write-Host ""
    Read-Host "按 Enter 键退出"
    exit 1
}

Write-Host "正在启动 ComfyUI..." -ForegroundColor Yellow
Write-Host "使用独立 Python 环境: python_embeded\python.exe" -ForegroundColor Yellow
Write-Host "启动参数: --windows-standalone-build --cuda-malloc --normalvram" -ForegroundColor Yellow
Write-Host ""

# 启动 ComfyUI（使用独立 Python 环境）
& ".\python_embeded\python.exe" -s "ComfyUI\main.py" --windows-standalone-build --cuda-malloc --normalvram

Read-Host "按 Enter 键退出"

