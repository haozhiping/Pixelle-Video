# GeminiImageNode 认证配置指南

## 问题描述

使用 `image_nano_banana.json` 工作流时，出现以下错误：

```
Unauthorized: Please login first to use this node.
```

## 原因分析

`image_nano_banana.json` 工作流使用了 `GeminiImageNode`（Nano Banana），该节点通过 `comfy.org` 的 API 服务代理访问 Google Gemini API。因此需要：

1. **Comfy.org 账户认证**：在 ComfyUI 前端登录 comfy.org 账户
2. **或使用 API Key**：生成并配置 comfy.org API key

## 解决方案

### 方案 1：在 ComfyUI 前端登录（推荐）

1. **启动 ComfyUI**：
   ```bash
   .\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --cuda-malloc --normalvram
   ```

2. **打开 ComfyUI 前端界面**：
   - 在浏览器中访问 `http://127.0.0.1:8188`
   - 或使用 ComfyUI 桌面版

3. **登录 Comfy.org 账户**：
   - 在 ComfyUI 界面中找到登录/账户设置
   - 使用您的 comfy.org 账户登录
   - 如果没有账户，请访问 [comfy.org](https://comfy.org) 注册

4. **验证登录状态**：
   - 登录成功后，`GeminiImageNode` 会自动使用您的认证信息
   - 无需额外配置

### 方案 2：使用 API Key

如果您不想使用前端登录，可以生成 API Key：

1. **访问 Comfy.org**：
   - 访问 [comfy.org](https://comfy.org)
   - 登录您的账户

2. **生成 API Key**：
   - 进入账户设置/API 设置
   - 生成新的 API Key
   - 复制保存 API Key

3. **配置 API Key**：
   - 在 ComfyUI 的配置文件中设置 API Key
   - 或通过环境变量设置：
     ```bash
     set COMFY_API_KEY=your_api_key_here
     ```

### 方案 3：使用其他图像生成工作流（无需认证）

如果您不想使用 comfy.org 服务，可以使用其他工作流：

#### 选项 A：使用 Qwen 模型（本地）
- **工作流**：`selfhost/image_qwen.json`
- **要求**：需要下载 Qwen 模型文件
- **优点**：完全本地运行，无需网络和认证
- **配置**：参考 [ComfyUI 设置指南](../user-guide/comfyui-setup.md)

#### 选项 B：使用 FLUX 模型（本地）
- **工作流**：`selfhost/image_flux.json`
- **要求**：需要下载 FLUX 模型文件
- **优点**：完全本地运行，无需网络和认证
- **配置**：参考 [ComfyUI 设置指南](../user-guide/comfyui-setup.md)

#### 选项 C：使用云端 FLUX（RunningHub）
- **工作流**：`runninghub/image_flux.json`
- **要求**：需要配置 RunningHub API Key
- **优点**：无需本地模型，使用云端服务
- **配置**：在 Pixelle-Video 配置文件中设置 `runninghub_api_key`

## 工作流对比

| 工作流 | 模型要求 | 认证要求 | 网络要求 | 推荐场景 |
|--------|---------|---------|---------|---------|
| `image_nano_banana.json` | 无需模型 | 需要 comfy.org 账户 | 需要 | 快速测试，无需下载模型 |
| `image_qwen.json` | 需要 Qwen 模型 | 无需 | 无需 | 本地运行，完全离线 |
| `image_flux.json` | 需要 FLUX 模型 | 无需 | 无需 | 本地运行，高质量图像 |
| `runninghub/image_flux.json` | 无需模型 | 需要 RunningHub API Key | 需要 | 云端服务，无需本地模型 |

## 常见问题

### Q1: 如何检查是否已登录？

A: 在 ComfyUI 前端界面中，查看右上角是否有账户信息或登录状态显示。

### Q2: 登录后仍然报错？

A: 请检查：
1. 账户是否有足够的配额/积分
2. 网络连接是否正常
3. ComfyUI 版本是否支持 API 节点

### Q3: 不想使用 comfy.org 服务怎么办？

A: 使用其他工作流（如 `image_qwen.json` 或 `image_flux.json`），这些工作流完全本地运行，无需外部认证。

### Q4: 如何切换工作流？

A: 在 Pixelle-Video 的 Web 界面中：
1. 进入「设置」页面
2. 找到「图像生成」配置
3. 选择不同的工作流文件

## 相关文档

- [ComfyUI 设置指南](../user-guide/comfyui-setup.md)
- [工作流自定义指南](../user-guide/workflows.md)
- [配置文件说明](../../reference/config-schema.md)

