# 图像生成模型下载指南

## 问题描述

使用 `image_qwen.json` 或 `image_flux.json` 工作流时，出现以下错误：

```
Value not in list: 'qwen_image_fp8_e4m3fn.safetensors' not in [...]
Value not in list: 'flux1-dev.safetensors' not in [...]
```

**原因**：ComfyUI 中缺少图像生成所需的模型文件。

## 解决方案

### 方案 1：下载 Qwen Image 模型（推荐用于 image_qwen.json）

#### 所需模型文件

1. **UNET 模型**：`qwen_image_fp8_e4m3fn.safetensors`
   - 位置：`ComfyUI/models/unet/`
   - 大小：约 4-5 GB

2. **CLIP 模型**：`qwen_2.5_vl_7b_fp8_scaled.safetensors`
   - 位置：`ComfyUI/models/clip/`
   - 大小：约 3-4 GB

3. **VAE 模型**：`qwen_image_vae.safetensors`
   - 位置：`ComfyUI/models/vae/`
   - 大小：约 200-300 MB

4. **LoRA 模型**：`Qwen-Image-Lightning-4steps-V1.0.safetensors`
   - 位置：`ComfyUI/models/loras/`
   - 大小：约 100-200 MB

#### 下载方式

**方式 A：从 HuggingFace 下载（推荐）**

1. **访问 HuggingFace 模型页面**：
   - Qwen Image 官方仓库：https://huggingface.co/Qwen/Qwen2-VL-7B-Instruct
   - 或搜索 "Qwen Image ComfyUI"

2. **下载模型文件**：
   ```bash
   # 使用 huggingface-cli 下载（需要先安装：pip install huggingface_hub）
   huggingface-cli download Qwen/Qwen2-VL-7B-Instruct --local-dir ./models
   ```

3. **手动下载**：
   - 访问模型页面，点击 "Files and versions"
   - 下载对应的 `.safetensors` 文件
   - 放置到对应的目录

**方式 B：从国内镜像下载**

1. **使用 HuggingFace 镜像**：
   - 访问：https://hf-mirror.com/
   - 搜索 "Qwen Image" 或 "Qwen2-VL"
   - 下载对应文件

2. **使用其他镜像站点**：
   - 搜索 "Qwen Image 模型下载" 或 "ComfyUI Qwen 模型"

#### 目录结构

下载后，确保文件结构如下：

```
ComfyUI/
├── models/
│   ├── unet/
│   │   └── qwen_image_fp8_e4m3fn.safetensors
│   ├── clip/
│   │   └── qwen_2.5_vl_7b_fp8_scaled.safetensors
│   ├── vae/
│   │   └── qwen_image_vae.safetensors
│   └── loras/
│       └── Qwen-Image-Lightning-4steps-V1.0.safetensors
```

---

### 方案 2：下载 FLUX 模型（用于 image_flux.json）

#### 所需模型文件

1. **UNET 模型**：`flux1-dev.safetensors`
   - 位置：`ComfyUI/models/unet/`
   - 大小：约 23 GB（完整版）或 12 GB（精简版）

2. **CLIP 模型**：
   - `clip_l.safetensors` - 位置：`ComfyUI/models/clip/`
   - `t5xxl_fp8_e4m3fn.safetensors` - 位置：`ComfyUI/models/clip/`
   - 大小：约 2-3 GB 每个

3. **VAE 模型**：`ae.safetensors`
   - 位置：`ComfyUI/models/vae/`
   - 大小：约 300-400 MB

#### 下载方式

**方式 A：从 HuggingFace 下载**

1. **访问 FLUX 官方仓库**：
   - FLUX.1-dev：https://huggingface.co/black-forest-labs/FLUX.1-dev
   - 或搜索 "FLUX ComfyUI"

2. **下载模型文件**：
   ```bash
   # 使用 huggingface-cli
   huggingface-cli download black-forest-labs/FLUX.1-dev --local-dir ./models
   ```

**方式 B：从 CivitAI 或其他社区下载**

1. 访问 CivitAI：https://civitai.com/
2. 搜索 "FLUX" 或 "FLUX.1-dev"
3. 下载对应的模型文件

**注意**：FLUX 模型文件较大，建议使用下载工具（如 aria2、wget）或支持断点续传的下载器。

#### 目录结构

```
ComfyUI/
├── models/
│   ├── unet/
│   │   └── flux1-dev.safetensors
│   ├── clip/
│   │   ├── clip_l.safetensors
│   │   └── t5xxl_fp8_e4m3fn.safetensors
│   └── vae/
│       └── ae.safetensors
```

---

### 方案 3：使用云端工作流（无需下载模型）

如果您不想下载大型模型文件，可以使用云端工作流：

1. **切换到 RunningHub 工作流**：
   - 在 Pixelle-Video 设置中选择 `runninghub/image_qwen.json`
   - 或 `runninghub/image_flux.json`

2. **配置 RunningHub API Key**：
   - 在配置文件中设置 `runninghub_api_key`
   - 或通过环境变量设置

3. **优点**：
   - 无需下载模型（节省磁盘空间）
   - 无需本地 GPU
   - 自动使用最新模型版本

---

## 验证模型安装

### 方法 1：在 ComfyUI 中检查

1. 启动 ComfyUI
2. 打开工作流文件（`image_qwen.json` 或 `image_flux.json`）
3. 查看模型加载节点：
   - `UNETLoader` 节点应显示可用的模型列表
   - `CLIPLoader` 节点应显示可用的 CLIP 模型
   - `VAELoader` 节点应显示可用的 VAE 模型
4. 如果模型出现在列表中，说明安装成功

### 方法 2：通过 API 检查

访问 ComfyUI API 端点查看可用模型：

```bash
# 查看 UNET 模型
curl http://127.0.0.1:8188/object_info | jq '.unet'

# 查看 CLIP 模型
curl http://127.0.0.1:8188/object_info | jq '.clip'

# 查看 VAE 模型
curl http://127.0.0.1:8188/object_info | jq '.vae'
```

---

## 常见问题

### Q1: 模型文件很大，下载很慢怎么办？

A: 
- 使用国内镜像站点（如 hf-mirror.com）
- 使用下载工具支持断点续传（如 aria2、IDM）
- 考虑使用云端工作流（RunningHub）

### Q2: 下载的模型文件名不匹配怎么办？

A: 
- 重命名模型文件以匹配工作流中的名称
- 或修改工作流 JSON 文件中的模型名称

### Q3: 模型下载后仍然报错？

A: 检查：
1. 文件是否放在正确的目录
2. 文件名是否完全匹配（区分大小写）
3. 文件是否完整（检查文件大小）
4. ComfyUI 是否已重启

### Q4: 可以使用其他版本的模型吗？

A: 可以，但需要：
1. 修改工作流 JSON 文件中的模型名称
2. 确保模型版本兼容（可能需要调整其他参数）

### Q5: 如何选择 Qwen 还是 FLUX？

A: 
- **Qwen Image**：模型较小（约 8-10 GB），生成速度快，适合快速测试
- **FLUX**：模型较大（约 25-30 GB），生成质量更高，适合高质量图像生成

---

## 相关资源

- [ComfyUI 官方文档](https://github.com/comfyanonymous/ComfyUI)
- [HuggingFace 模型库](https://huggingface.co/models)
- [CivitAI 模型库](https://civitai.com/)
- [ComfyUI 设置指南](../user-guide/comfyui-setup.md)

---

## 快速开始（推荐）

如果您是第一次使用，建议：

1. **先尝试云端工作流**（`runninghub/image_qwen.json`）
   - 无需下载模型
   - 快速验证功能

2. **如果需要本地运行**：
   - 优先下载 Qwen Image 模型（文件较小）
   - 或根据您的 GPU 显存选择合适的模型

3. **下载完成后**：
   - 重启 ComfyUI
   - 在 Pixelle-Video 中选择对应的工作流
   - 测试图像生成功能

