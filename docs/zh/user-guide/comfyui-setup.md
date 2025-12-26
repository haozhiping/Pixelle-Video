# ComfyUI 配置指南

## 📋 概述

Pixelle-Video 基于 ComfyUI 架构，支持两种模式：

1. **RunningHub（云端）** - 无需本地配置，使用云端服务
2. **SelfHost（本地）** - 需要本地 ComfyUI 环境

## 🚀 快速开始

### 方案 A：使用 RunningHub（推荐新手）

**优点**：
- ✅ 无需下载模型（模型在云端）
- ✅ 无需本地 GPU（使用云端 GPU）
- ✅ 开箱即用，配置简单

**配置步骤**：

1. 在 Web 界面中，展开「⚙️ 系统配置」
2. 在「图像配置」中，填入 RunningHub API Key
3. 选择 `runninghub/*.json` 工作流（如 `runninghub/image_flux.json`）
4. 点击「保存配置」

**注意**：需要 RunningHub API Key（可能需要付费）

---

### 方案 B：使用 SelfHost（推荐有 GPU 的用户）

**优点**：
- ✅ 完全免费（除了电费）
- ✅ 数据隐私保护
- ✅ 无网络依赖
- ✅ 可自定义模型

**配置步骤**：

#### 1. 安装 ComfyUI

```bash
# 克隆 ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# 安装依赖

.\python_embeded\python.exe -m pip install 
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

#### 2. 安装必要的自定义节点

根据你使用的工作流，安装相应的节点：

**TTS 工作流（如 `tts_edge.json`）**：
```bash
cd ComfyUI/custom_nodes

# EdgeTTS 节点（已在 mysoaiVideo 文件夹中）
# 确保 F:\rick-comfyui\shipin\RICK_VIDEO_KING\RICK_VIDEO_KING\ComfyUI\custom_nodes\mysoaiVideo 存在

# ComfyUI-Easy-Use（用于参数输入）
git clone https://github.com/yolain/ComfyUI-Easy-Use.git

# ComfyUI-Primitive（用于文本输入）
git clone https://github.com/pythongosssss/ComfyUI-Primitive-Nodes.git

# ComfyUI-Audio（用于音频保存）
git clone https://github.com/pythongosssss/ComfyUI-Audio.git
```

**图像生成工作流（如 `image_flux.json`）**：
```bash
cd ComfyUI/custom_nodes

# ComfyUI-Easy-Use
git clone https://github.com/yolain/ComfyUI-Easy-Use.git
```

#### 3. 下载模型文件

根据你使用的工作流，下载相应的模型：

**FLUX 模型（用于 `image_flux.json`）**：
- `flux1-dev.safetensors` - 主模型
- `clip_l.safetensors` - CLIP 模型
- `t5xxl_fp8_e4m3fn.safetensors` - T5 模型
- `ae.safetensors` - VAE 模型

**Qwen 模型（用于 `image_qwen.json`）**：
- `qwen_image_fp8_e4m3fn.safetensors` - UNET 模型
- `qwen_2.5_vl_7b_fp8_scaled.safetensors` - CLIP 模型
- `qwen_image_vae.safetensors` - VAE 模型
- `Qwen-Image-Lightning-4steps-V1.0.safetensors` - LoRA 模型

**WAN 模型（用于视频生成）**：
- `Wan2_1-T2V-14B_fp8_e4m3fn.safetensors` - 文本到视频模型
- `wan_2.1_vae.safetensors` - VAE 模型
- `umt5_xxl_fp8_e4m3fn_scaled.safetensors` - CLIP 模型

**模型放置位置**：
- UNET/主模型：`ComfyUI/models/unet/`
- CLIP 模型：`ComfyUI/models/clip/`
- VAE 模型：`ComfyUI/models/vae/`
- LoRA 模型：`ComfyUI/models/loras/`

#### 4. 启动 ComfyUI

```bash
cd ComfyUI
python main.py
```

ComfyUI 会在 `http://127.0.0.1:8188` 启动

#### 5. 在 Pixelle-Video 中配置

1. 在 Web 界面中，展开「⚙️ 系统配置」
2. 在「图像配置」中，填入 ComfyUI URL：`http://127.0.0.1:8188`
3. 点击「测试连接」确认服务可用
4. 选择 `selfhost/*.json` 工作流（如 `selfhost/image_flux.json`）
5. 点击「保存配置」

---

## 🔧 工作流配置

### 工作流文件位置

工作流文件位于 `workflows/` 目录：

```
workflows/
├── selfhost/          # 本地工作流
│   ├── tts_edge.json
│   ├── tts_index2.json
│   ├── image_flux.json
│   ├── image_qwen.json
│   └── image_nano_banana.json
└── runninghub/        # 云端工作流
    ├── tts_edge.json
    ├── image_flux.json
    └── video_wan2.1_fusionx.json
```

### 工作流选择建议

**图像生成**：
- 有 FLUX 模型 → 使用 `selfhost/image_flux.json`
- 有 Qwen 模型 → 使用 `selfhost/image_qwen.json`
- 无模型 → 使用 `runninghub/image_flux.json` 或 `runninghub/image_qwen.json`（云端服务，需要 RunningHub API Key）
- 或使用 `selfhost/image_nano_banana.json`（使用 Google Gemini，需要 comfy.org 账户认证，参考 [GeminiImageNode 认证配置](../../troubleshooting/gemini-image-node-auth.md)）

**⚠️ 如果遇到模型文件缺失错误，请参考 [图像生成模型下载指南](../../troubleshooting/image-model-download.md)**

**TTS**：
- 本地 EdgeTTS → 使用 `selfhost/tts_edge.json`
- 声音克隆 → 使用 `selfhost/tts_index2.json`
- 云端服务 → 使用 `runninghub/tts_edge.json`

---

## ⚠️ 常见问题

### 问题 1：模型文件不存在

**错误信息**：
```
Value not in list: 'flux1-dev.safetensors' not in [...]
```

**解决方案**：
1. 检查模型文件是否已下载到正确目录
2. 检查文件名是否完全匹配（区分大小写）
3. 如果模型不存在，可以：
   - 使用 `runninghub/*.json` 工作流（云端服务）
   - 使用 `selfhost/image_nano_banana.json`（无需模型，但需要 comfy.org 账户认证，参考 [GeminiImageNode 认证配置](../../troubleshooting/gemini-image-node-auth.md)）
   - 修改工作流 JSON 文件，使用你已有的模型

### 问题 2：节点不存在

**错误信息**：
```
Cannot execute because node EdgeTTS does not exist.
```

**解决方案**：
1. 检查自定义节点是否已安装
2. 检查节点目录是否正确
3. 重启 ComfyUI 服务器

### 问题 3：参数验证失败

**错误信息**：
```
Parameter `unet_name` has no default value but not marked as required
```

**解决方案**：
- 工作流 JSON 文件中的 `_meta.title` 不应包含参数占位符（如 `$unet_name.value`）
- 如果工作流需要参数，应通过 ComfyKit 的参数替换机制传递

### 问题 4：ComfyUI 连接失败

**错误信息**：
```
Connection refused
```

**解决方案**：
1. 确认 ComfyUI 已启动
2. 检查 ComfyUI URL 是否正确（默认 `http://127.0.0.1:8188`）
3. 检查防火墙设置
4. 查看 ComfyUI 启动日志

### 问题 5：IndexTTS2 CUDA 内存错误

**错误信息**：
```
IndexTTS2 synthesis failed: cudaMallocAsync does not yet support checkPoolLiveAllocations
```

**解决方案**：
这是 PyTorch 的 CUDA 内存管理问题。在启动 ComfyUI 前设置环境变量：

**Windows (PowerShell)**：
```powershell
$env:PYTORCH_CUDA_ALLOC_CONF="backend:cudaMalloc"
```

**Windows (CMD)**：
```cmd
set PYTORCH_CUDA_ALLOC_CONF=backend:cudaMalloc
```

详细解决方案请参考：[IndexTTS2 CUDA 错误解决方案](../troubleshooting/indextts2-cuda-error.md)

---

## 📚 更多资源

- [ComfyUI 官方文档](https://github.com/comfyanonymous/ComfyUI)
- [Pixelle-Video GitHub](https://github.com/AIDC-AI/Pixelle-Video)
- [工作流定制指南](./workflows.md)

---

## 💡 提示

1. **首次使用建议使用 RunningHub**：无需配置，开箱即用
2. **有 GPU 的用户建议使用 SelfHost**：更灵活，可自定义
3. **不需要所有工作流**：只安装你实际使用的工作流所需的节点和模型
4. **模型文件很大**：FLUX 模型约 23GB，Qwen 模型约 14GB，请确保有足够空间



