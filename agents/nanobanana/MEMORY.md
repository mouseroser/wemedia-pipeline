# MEMORY.md - Nano Banana Agent (生图)

## 关于我
- **Agent ID**: nanobanana
- **角色**: 配图生成
- **编排模型**: anthropic/claude-sonnet-4-6
- **生图后端**: gemini/gemini-3.1-flash-image（代理）
- **Telegram 群**: 生图 (-5217509070)

## 工作记录

### 2026-03-06 配置更新
- 创建完整的配置文件（AGENTS.md, SOUL.md, IDENTITY.md, USER.md, TOOLS.md, HEARTBEAT.md）
- 对齐自媒体 v1.0 流水线规范
- 明确职责：Step 5 根据提示词生成配图
- 模型限制：不支持工具调用

### 2026-03-21 代理生图链路修正
- 主配置不再默认走 `google/gemini-3.1-flash-image-preview`
- 代理 `gemini/gemini-3.1-flash-image` + `openai-completions` 可以真实返回图片数据
- 真实问题在于代理返回的是文本包裹的 `data:image/...`
- 新方案：通过 `proxy-generate-image.mjs` 解码并保存为真实文件
- `openai-responses` 在该代理上不可用；`anthropic-messages` 可用但默认不用
- 为避免 Gemini `google_search` 与函数调用冲突，本 agent 禁用 `web_search`

## 关键约束
- 只负责生成图片
- 不执行对外发送任务（交给 main agent）
- 不执行内容创作/审查任务
- 生成结果必须是本地真实文件路径

## 自媒体流水线职责

### Step 5 配图生成
1. 接收配图提示词（从 wemedia agent 的 `drafts/prompts.md`）
2. 优先通过 `proxy-generate-image.mjs` 调用代理 `gemini/gemini-3.1-flash-image`
3. 返回本地真实文件路径

## 模型限制
- 当前默认编排模型为 `anthropic/claude-sonnet-4-6`
- 代理 `gemini/gemini-3.1-flash-image` + `openai-completions` 为当前主路径
- `openai-responses` 不可用
- `anthropic-messages` 可用但返回形态同样需要本地解码
- 只能生成图片并返回本地路径
- 为避免 Gemini `google_search` 与函数调用冲突，本 agent 禁用 `web_search`

## 已知问题
- 旧 Google key 曾出现配额耗尽和 API key 过期，当前已切到新的可用 key
- 代理模型会返回 `data:image/...` 文本，需要本地解码
- Main agent 会检查返回文件是否真实存在，而不是只看 announce 文本

## Spawn 参数
- **runTimeoutSeconds: 300** (必须)
- 生图模型响应慢，需要延长超时
- Main agent spawn 时必须设置此参数

## 输入格式
从 wemedia agent 读取配图提示词：
- `~/.openclaw/workspace/intel/collaboration/media/wemedia/drafts/prompts.md`

## 输出格式
返回本地真实文件路径：
```text
/tmp/nanobanana-test.png
```

## 踩坑笔记
- 历史 remote URL 曾被安全策略阻止（`SsrFBlockedError`）
- 当前代理路径直接返回 data URL，不再依赖外部图片链接
- 解决：必须先用本地脚本解码到本地文件，再由 main agent 发送
