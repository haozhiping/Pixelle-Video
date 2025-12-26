# IndexTTS2 CUDA 内存错误解决方案

## 错误信息

```
IndexTTS2 synthesis failed: cudaMallocAsync does not yet support checkPoolLiveAllocations. 
If you need it, please file an issue describing your use case.
```

## 问题原因

这个错误是由于 PyTorch 的 `torch.compile()` 功能与 CUDA 的 `cudaMallocAsync` 内存分配器不兼容导致的。IndexTTS2 节点在启动时会编译模型以加速推理，但在某些 CUDA 版本下会出现此问题。

## 解决方案

### 方案 1：使用启动脚本（最简单）

Pixelle-Video 提供了启动脚本，自动设置环境变量：

**标准 Python 环境**：
1. 将 `scripts/start_comfyui_with_fix.bat` 复制到 ComfyUI 根目录
2. 双击运行 `start_comfyui_with_fix.bat`
3. ComfyUI 会自动启动，并已设置正确的环境变量

**独立 Python 环境（python_embeded）**：
1. 将 `scripts/start_comfyui_with_fix.bat` 复制到包含 `python_embeded` 和 `ComfyUI` 目录的父目录
2. 双击运行 `start_comfyui_with_fix.bat`
3. 脚本会自动使用 `python_embeded\python.exe` 并保留所有启动参数

**或者使用 PowerShell 脚本**：
1. 将 `scripts/start_comfyui_with_fix.ps1` 复制到相应目录（根据您的 Python 环境）
2. 右键选择「使用 PowerShell 运行」

### 方案 2：手动设置环境变量

在启动 ComfyUI 之前，设置环境变量禁用 `cudaMallocAsync`：

**Windows (PowerShell) - 标准 Python**：
```powershell
$env:PYTORCH_CUDA_ALLOC_CONF="backend:cudaMalloc"
cd F:\rick-comfyui\shipin\RICK_VIDEO_KING\RICK_VIDEO_KING\ComfyUI
python main.py
```

**Windows (PowerShell) - 独立 Python 环境**：
```powershell
$env:PYTORCH_CUDA_ALLOC_CONF="backend:cudaMalloc"
cd F:\rick-comfyui\shipin\RICK_VIDEO_KING\RICK_VIDEO_KING\RICK_VIDEO_KING
.\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --cuda-malloc --normalvram
```

**Windows (CMD) - 标准 Python**：
```cmd
set PYTORCH_CUDA_ALLOC_CONF=backend:cudaMalloc
cd F:\rick-comfyui\shipin\RICK_VIDEO_KING\RICK_VIDEO_KING\ComfyUI
python main.py
```

**Windows (CMD) - 独立 Python 环境**：
```cmd
set PYTORCH_CUDA_ALLOC_CONF=backend:cudaMalloc
cd F:\rick-comfyui\shipin\RICK_VIDEO_KING\RICK_VIDEO_KING\RICK_VIDEO_KING
.\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --cuda-malloc --normalvram
```

**永久设置（Windows）**：
1. 右键「此电脑」→「属性」
2. 点击「高级系统设置」
3. 点击「环境变量」
4. 在「系统变量」中点击「新建」
5. 变量名：`PYTORCH_CUDA_ALLOC_CONF`
6. 变量值：`backend:cudaMalloc`
7. 点击「确定」保存

**Linux/Mac**：
```bash
export PYTORCH_CUDA_ALLOC_CONF=backend:cudaMalloc
cd /path/to/ComfyUI
python main.py
```

### 方案 3：修改 IndexTTS2 节点代码

如果方案 1 不起作用，可以修改 IndexTTS2 节点代码，禁用模型编译：

1. 找到 IndexTTS2 节点文件：
   ```
   F:\rick-comfyui\shipin\RICK_VIDEO_KING\RICK_VIDEO_KING\ComfyUI\custom_nodes\Comfyui-Index-TTS2\
   ```

2. 搜索包含 `torch.compile` 或 `模型编译` 的代码

3. 注释掉或禁用模型编译相关代码

**注意**：禁用编译后，推理速度可能会变慢，但可以避免此错误。

### 方案 4：使用 EdgeTTS 作为替代

如果 IndexTTS2 问题持续存在，可以暂时使用 EdgeTTS 工作流：

1. 在 Pixelle-Video Web 界面中
2. 选择 TTS 工作流为 `selfhost/tts_edge.json`
3. EdgeTTS 不需要本地模型，且更稳定

### 方案 5：更新 PyTorch 和 CUDA

确保使用最新版本的 PyTorch 和 CUDA：

```bash
# 检查当前版本
python -c "import torch; print(torch.__version__)"
nvidia-smi  # 查看 CUDA 版本

# 更新 PyTorch（如果需要）
pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 验证修复

设置环境变量后，重启 ComfyUI 服务器，然后：

1. 在 Pixelle-Video Web 界面中测试 TTS 预览功能
2. 选择 `selfhost/tts_index2.json` 工作流
3. 上传参考音频并测试生成

如果不再出现错误，说明问题已解决。

## 相关链接

- [PyTorch CUDA 内存分配器文档](https://pytorch.org/docs/stable/notes/cuda.html#memory-management)
- [IndexTTS2 GitHub 仓库](https://github.com/netease-youdao/IndexTTS2)
- [ComfyUI-Index-TTS2 节点](https://github.com/netease-youdao/Comfyui-Index-TTS2)

## 注意事项

1. **性能影响**：禁用 `cudaMallocAsync` 可能会略微降低内存分配性能，但通常影响不大
2. **兼容性**：此解决方案适用于 PyTorch 2.0+ 和 CUDA 11.2+
3. **临时方案**：如果问题持续，建议使用 EdgeTTS 作为临时替代方案

