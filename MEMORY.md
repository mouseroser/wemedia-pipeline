# MEMORY.md - 小光的长期记忆

> 精简版 (2026-03-14)。完整历史备份：`memory/archive/MEMORY-2026-03-14-before.md`
> 踩坑笔记完整版已存入 memory-lancedb-pro 向量数据库，按需召回。

---

## ⚠️ 血泪教训（永不重犯）

1. **Review 不做编排**：review 只负责审查，所有编排由 main 负责。mode=run 的 announce 有轮次限制。
2. **Agent 自推不可靠**：关键通知必须由 main 补发，不能依赖 sub-agent 自推到群。
3. **Coding 结果不可信**：coding 的 announce 不可信，必须通过 review 或 main 直接验证。
4. **memory-lancedb-pro 升级回归**：升级会覆盖本地补丁（`resolveRuntimeAgentId(...) || 'main'`），每次升级后必须检查 `memory_stats`/`memory_list` 是否正常。修复后需完整 `openclaw gateway restart`。

---

## ❌ 错误示范 → 正确做法

| 错误 | 正确 |
|------|------|
| 让 review 编排其他 agent | main 直接编排所有 agent |
| 依赖 agent 自推到群 | main 统一补发到监控群 |
| browser 访问 GitHub | 先 `git clone` 到本地 |
| 改配置后 gateway reload | 必须 `openclaw gateway restart` |
| 只配 OpenClaw requireMention | 同时关 Telegram Privacy Mode |
| skills 放 workspace 下 | 放 `~/.openclaw/skills/` |
| TODO 放 workspace 下 | 放 `~/.openclaw/todo/` |
| 说"要我...吗？" | 知道规则就直接执行 |
| 发现问题先报告等指令 | 发现问题立即修复再报告 |

---

## 晨星的核心偏好

- **沟通**：简洁有力，默认执行不反复确认
- **记录**：遇到问题/修复后立即主动记录
- **原则**：每个 agent 只做本职、不走捷径、同一问题连续三次未解决必须切换方向
- **语言**：晨星↔小光中文，对外协作按仓库语境定
- **通知**：所有流水线必须有通知，Agent 自推职能群 + main 补发监控群

---

## 关于晨星

- 陈颖，时区 Asia/Shanghai，Telegram ID: 1099011886

---

## Telegram 群组

| Agent | 称呼 | Chat ID |
|-------|------|---------|
| main | 小光 | DM |
| monitor-bot | - | -5131273722 |
| docs | - | -5095976145 |
| test | - | -5245840611 |
| review | - | -5242448266 |
| coding | - | -5039283416 |
| brainstorming | - | -5231604684 |
| wemedia | - | -5146160953 |
| nano-banana | - | -5217509070 |
| gemini | 织梦 | -5264626153 |
| notebooklm | 珊瑚 | -5202217379 |
| claude | 小克 | -5101947063 |
| openai | 小曼 | -5242027093 |

---

## 模型配置

- 默认：anthropic/claude-opus-4-6
- coding: gpt-5.4 | review/test/brainstorming: sonnet | docs/monitor-bot: minimax
- 织梦: gemini-preview | 珊瑚: opus | 小克: opus | 小曼: gpt-5.4

---

## 流水线概要

### 星链 v2.6
- Main 直接编排，Review 只做审查
- 全自动推进（Rule 0），除 Step 7 晨星确认外不停顿
- 打磨层（Step 1.5）：gemini→openai→claude→review 多轮交叉
- Spawn 失败自动重试 3 次

### 自媒体 v1.1
- 选题分级(S/M/L) → Constitution-First → 创作 → 审查 → 生图 → 适配 → 交付
- ⛔ Step 7：未经晨星确认绝不发布

### 星鉴 v1.2
- gemini 研究宪法 → claude 主方案 → review/gemini 复核 → review/gpt 仲裁 → docs 交付

---

## 记忆系统

- **Layer 1**：MEMORY.md + memory/*.md（文件）
- **Layer 2**：memory-lancedb-pro@1.1.0-beta.8 + Ollama nomic-embed-text + 本地 rerank(bge-reranker-v2-m3:8765)
  - autoRecall=true, autoCapture=true, captureAssistant=true
- **Layer 3**：NotebookLM（memory-archive + openclaw-docs + troubleshooting）
- **维护**：每日日志加载今天+昨天，压缩阈值 40k tokens，周日 04:00 压缩 + 22:00 MEMORY.md 维护

---

## Workspace 架构

- Main: `~/.openclaw/workspace/`
- Sub-agents: `~/.openclaw/workspace/agents/{agent-id}/`
- Skills: `~/.openclaw/skills/`（不是 workspace 下）
- TODO: `~/.openclaw/todo/`（不是 workspace 下）
- Scripts: `~/.openclaw/scripts/`
- 协作产物: `workspace/intel/collaboration/`

---

## 核心规则

1. **流水线更新自动应用**：看到流水线更新立即更新所有相关 agent 配置，不等提醒
2. **插件更新先分析再更新**：查 CHANGELOG → 评估影响 → 制定计划 → 确认后更新
3. **OpenClaw 新版本联动**：晨星说"有新版本"→ 立即更新 openclaw-docs 笔记
4. **优化前先评估收益**：不为"看起来更好"而改动，必须有明确使用场景
5. **使用 Skill 必须完整执行**：阅读所有要求、列出所有文件、逐个更新验证
