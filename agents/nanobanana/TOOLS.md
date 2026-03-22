# TOOLS.md - Nano Banana Agent

## 生图模型
- **编排模型**: anthropic/claude-sonnet-4-6
- **生图后端**: gemini/gemini-3.1-flash-image
- **协议**: `openai-completions`
- **能力**: 根据提示词生成图片并落盘到本地文件
- **限制**: 禁用 `web_search`，避免 Gemini 内建搜索与函数调用冲突

## 输入格式
从 wemedia agent 读取配图提示词：
- `~/.openclaw/workspace/intel/collaboration/media/wemedia/drafts/prompts.md`

## 输出格式
返回本地真实文件路径：
```text
/tmp/nanobanana-test.png
```

## 超时配置
- 生图模型响应慢，需要 `runTimeoutSeconds: 300`
- main agent spawn 时必须设置此参数

## 工作流程
1. 接收配图提示词
2. 调用 `proxy-generate-image.mjs` 通过代理请求 `gemini-3.1-flash-image`
3. 把返回的 `data:image/...` 解码成真实文件
4. 验证文件大小和尺寸
5. 返回本地路径给调用方

## 当前故障结论
- 历史 Google Gemini 路径曾出现配额耗尽和 API key 过期，当前已切到新的可用 key
- `openai-responses` 在该代理上不可用（`/v1/responses` 为 404）
- `openai-completions` 可用，且返回真实图片数据，但格式是 markdown 包裹的 `data:image/...`
- `anthropic-messages` 也可用，但返回形态同样是文本包裹的 `data:image/...`
- 当前修复方案是本地脚本解码保存，避免失败时返回伪造图片结果
- 当前运行时若同时带上 Gemini 内建 `google_search` 与函数调用，会收到 400；因此本 agent 禁用 `web_search`

## 标准命令
```bash
cat prompt.txt | node ~/.openclaw/workspace/agents/nanobanana/proxy-generate-image.mjs --out /tmp/nanobanana-test.png
```

---
若本目录下存在 agent/、sessions/，视为 OpenClaw 内核 runtime 子目录，不参与流水线，请勿修改。

## 多 Agent 联合工作材料
- 只要是多 agent 联合工作（流水线尤为明显），除了正式产物之外全部放到 `intel/collaboration/`
- 正式产物：报告、审查结论、修复代码、文档交付等 → 各自 agent 目录
- 非正式产物：外部 GitHub 项目、本地镜像、共享分析材料、临时脚本、调研素材等 → `intel/collaboration/`
