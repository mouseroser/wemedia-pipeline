---
name: wemedia-pipeline
description: 自媒体运营系统 v1.1。用于 24/7 内容运营：Gemini 持续扫描 → main 维护 Hot/Evergreen/Series 队列 → Publishability Gate 决定是否今天推进 → Constitution-First 前置链 → wemedia 创作/适配 → 审查/生图/确认门控。适用于选题发现、内容计划、单条内容生产和日结复盘。
---

# 自媒体运营系统 v1.1

把这项 skill 视为 **运营系统 skill**，不是单次内容生成器。

## Required Read

先读：
1. `references/ops-routing-v1.1.md` — 当前正式执行路由（优先）
2. `references/PIPELINE_FLOWCHART_V1_1_EMOJI.md` — 流程图

按需再读：
- `references/pipeline-wemedia-v1.1-contract.md` — 旧版 v1.1 详细合约，仅在需要核对历史设计时读取

## 职责边界

**wemedia = 自媒体运营（策略层），creator-ops = 自媒体执行（工具层）**

| 归 wemedia（自媒体运营） | 归 creator-ops（自媒体执行） |
|-----------|---------------|
| 选题发现与评估 | CDP 脚本执行（publish_pipeline / cdp_publish）|
| 内容队列维护（HOT/EVERGREEN/SERIES）| 竞品数据采集（search-feeds）|
| Publishability Gate | 数据看板（content-data）|
| Constitution-First 内容创作 | 评论回复 |
| 正文/标题/标签生成 | 登录管理 |
| 配图生成指令（**NotebookLM**）| NLM 知识采集管道 |
| 平台内容适配（格式/结构）| 平台规则驱动 |

**main 的角色**：编排中心。wemedia 输出内容 + 执行指令 → main 调用 creator-ops 完成发布。

**禁止**：wemedia agent 不得直接调用 `python3 scripts/publish_pipeline.py`；那是 main 的职责。

## Current Scope

- 当前激活平台：**仅小红书**
- 抖音 / 知乎模板保留，但默认不启动
- 搜索策略：**Gemini 搜索优先**；`web_fetch` 抓正文；`browser` 做复杂页面兜底
- Brave Search API 不是当前必需前置
- 未经晨星确认，绝不外发

## 内容交付物格式（wemedia → main → creator-ops）

wemedia agent 完成创作后，必须输出以下标准格式，供 main 调用 creator-ops：

```
标题：{≤20字}
标签：{≤10个，用逗号分隔}
配图路径：{图片文件路径，无配图写"无"}
正文：
{正文内容，≤1000字}
```

**保存位置**：`~/.openclaw/workspace/agents/wemedia/drafts/{A|B|C}/{标识}.txt`

**禁止**在正文中混入元信息。配图路径独立一行，由 main 决定是否传入 `--image-urls`。

## Trigger Guide

## Trigger Guide

在以下场景触发本 skill：
- 用户要求做自媒体内容运营、选题、排期、日更系统
- 用户要求维护热点队列 / 常青队列 / 系列队列
- 用户要求生成小红书内容或启动内容生产链
- 用户要求判断“今天值不值得发什么”
- 用户要求对单条内容做前置策划、创作、审查、适配、确认

## Core Route

### 运营层
- Step 0：持续研究层（Gemini 扫描）
- Step 1：内容队列层（main 维护队列）
- Step 1.5：Publishability Gate

### 生产层
- Step 2：Constitution-First 前置链
- Step 3：wemedia 创作
- Step 4：gemini 审查
- Step 4.5：修改循环
- Step 5：配图生成（**NotebookLM 统一路线**）
- Step 5.5：notebooklm 衍生内容（其他格式：podcast/mind-map/quiz）
- Step 6：平台适配 + 排期
- Step 7：晨星确认
- **Step 7.5：main 调用 creator-ops 发布** ← wemedia 交付内容 → main 执行发布
- Step 8：日结 / 周复盘

## Agent Roles

- `main`：唯一编排中心；维护队列、计划、确认与通知
- `gemini`：持续扫描、前置对齐、复核、审查
- `claude` / Claude Code：内容策略与执行计划
- `openai`：仅在高风险 / 明显分歧时仲裁
- `notebooklm`：按需深研 + **配图生成**（infographic，bento-grid 风格）
- `wemedia`：正文创作、改稿、平台适配
- ~~`nano-banana`~~：已废弃（统一使用 NotebookLM）

## Model Rule of Thumb

- 日常内容生产默认 `minimax` 足够，尤其适合小红书正文、改写、标题、摘要、标签
- 不要把整条链路压成单模：前置定义、搜索判断、风险挑刺、合规复核仍交给 `gemini / Claude Code / gpt`
- 高推理模型优先用在“定方向、抓偏差、控风险”

## Delivery Rules

- main 的通知是可靠主链路
- sub-agent 自推仅 best-effort
- 关键进度、失败、HALT、交付摘要必须由 main 保证可见
- 所有级别都必须经过晨星确认门控

## Hard Rules

- 不要把“持续研究 / 队列层”跳过后伪装成完整运营系统
- 不要为了凑产出跳过 Publishability Gate
- 不要未经确认自动发布
- 不要因单点工具失败卡死全链路；必须优雅降级
- 不要默认同时启动多平台分发；当前默认只做小红书

## Spawn Rules

统一使用：

```text
sessions_spawn(agentId: "<agent>", mode: "run", task: "<任务+上下文>")
```

补充：
- `wemedia`：`thinking: "high"`
- `gemini`：`runTimeoutSeconds: 300`
- 失败自动重试 3 次；仍失败则告警 + 降级 / BLOCKED

**⚠️ 禁止项**：
1. wemedia spawn 的子 agent 不得直接调用 `python3 scripts/publish_pipeline.py` 或任何 CDP 脚本（那是 main 的职责）
2. wemedia 的正文输出不得混入标题、标签、配图路径等元信息（使用上方标准交付物格式）
3. wemedia 不得直接读 creator-ops 的竞品数据文件（应由 main 分析后传递结论）

## When To Go Deeper

出现以下情况时，继续读取 reference：
- 需要完整运营路由和分级规则 → `references/ops-routing-v1.1.md`
- 需要老版细节对照或迁移核验 → `references/pipeline-wemedia-v1.1-contract.md`
- 需要流程图辅助理解 → `references/PIPELINE_FLOWCHART_V1_1_EMOJI.md`

---

## 与 creator-ops Skill 的联动关系

**本质**：wemedia = 自媒体运营（策略层），creator-ops = 自媒体执行（工具层）。

**联动链路**：

```
wemedia（Step 2 NLM 查询）
    → 调用 creator-ops 维护的 media-research notebook
    ↓
wemedia（Step 3 创作 + Step 5 配图）
    → 输出标准交付物到 drafts/{A|B|C}/{标识}.txt
    ↓
main（Step 7.5）
    → 读取 wemedia 交付物
    → 调用 creator-ops 的 publish_pipeline.py 发布
    ↓
creator-ops（Step 8 日结）
    → content-data 抓取数据
    → 写入日结 + 喂入 media-research notebook
```

**creator-ops 维护什么**：CDP 脚本、竞品数据、media-research notebook（NLM 知识库）、发布执行。

**wemedia 维护什么**：内容队列（ HOT/EVERGREEN/SERIES）、Constitution-First 创作流程、平台内容适配。

**main 的职责**：编排调度，从 wemedia 接收内容 + 向 creator-ops 下发执行指令。
