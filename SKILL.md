---
name: wemedia-pipeline
description: 自媒体运营系统 v1.1。用于 24/7 内容运营：Gemini 持续扫描 → main 维护队列 → Publishability Gate → Constitution-First → wemedia subagent 端到端创作/配图/平台适配 → 晨星确认门控 → main 在 Step 7.5 调用发布执行 skill（如 douyin）。适用于选题发现、内容计划、单条内容生产和日结复盘。
---

# 自媒体运营系统 v1.1

把这项 skill 视为 **运营系统 skill**，不是单次内容生成器。

## Required Read

先读：
1. `references/ops-routing-v1.1.md` - 当前正式执行路由（优先）
2. `references/PIPELINE_FLOWCHART_V1_1_EMOJI.md` - 流程图

按需再读：
- `references/pipeline-wemedia-v1.1-contract.md` - 旧版 v1.1 详细合约，仅在需要核对历史设计时读取

## 职责边界

**wemedia = 自媒体运营（端到端负责内容与平台适配），发布 skill = 平台执行（工具层）**

| 归 wemedia（运营/创作层） | 归发布 skill（执行层） |
|-----------|---------------|
| 选题发现与评估 | CDP / Browser 发布脚本执行 |
| 内容队列维护（HOT/EVERGREEN/SERIES）| 登录态复用与页面自动化 |
| Publishability Gate | 平台提交流程 |
| Constitution-First 内容创作 | 审核等待 / 状态回传 |
| 正文/标题/标签生成 | 平台控件交互 |
| 配图生成指令（**NotebookLM**）| 平台规则驱动的最终执行 |
| 平台内容适配（格式/结构）| - |

**main 的角色**：编排 + 监控 + 确认门控，不做具体创作，也不直接越位替代平台执行细节。

**硬边界**：wemedia 只产出发布包，不直接调用任何 CDP 发布脚本；Step 7.5 必须由 main 调具体平台 skill（如 douyin）。

## Current Scope

- 当前激活平台：**小红书、抖音**
- 知乎 / X 模板保留，但默认不启动
- 搜索策略：**Gemini 搜索优先**；`web_fetch` 抓正文；`browser` 做复杂页面兜底
- Brave Search API 不是当前必需前置
- 未经晨星确认，绝不外发

## 内容交付物格式（wemedia → main → platform skill）

wemedia agent 完成创作后，必须输出**平台化发布包**。默认分两类：

### A. 小红书发布包

```
平台：xiaohongshu
标题：{≤20字}
标签：{≤10个，用逗号分隔}
配图路径：{图片文件路径，无配图写"无"}
正文：
{正文内容，≤1000字}
```

### B. 抖音发布包

```
平台：douyin
内容ID：{唯一标识}
标题：{≤30字}
描述：
{正文内容，末尾带 #标签}
视频路径：{绝对路径}
竖封面路径：{绝对路径，9:16}
横封面路径：{绝对路径，4:3}
音乐：{默认 热门}
可见性：{private|public，默认 private}
备注：{可选}
```

**统一 schema**：`~/.openclaw/workspace/shared-context/DOUYIN-PUBLISH-PACK-SCHEMA.md`

**保存位置**：
- 小红书：`~/.openclaw/workspace/intel/collaboration/media/wemedia/drafts/{A|B|C}/{标识}.txt`
- 抖音：`~/.openclaw/workspace/intel/collaboration/media/wemedia/douyin/{content_id}.md`

**禁止**在正文/描述中混入额外控制元信息；路径、音乐、可见性必须独立字段给出。

## Trigger Guide

## Trigger Guide

在以下场景触发本 skill：
- 用户要求做自媒体内容运营、选题、排期、日更系统
- 用户要求维护热点队列 / 常青队列 / 系列队列
- 用户要求生成小红书/抖音内容或启动内容生产链
- 用户要求判断"今天值不值得发什么"
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
- Step 6：平台适配 + 发布包生成
- Step 7：晨星确认
- **Step 7.5：main 调用平台发布 skill** ← wemedia 交付发布包 → main 执行发布
- Step 8：日结 / 周复盘

## Agent Roles

- `main`：唯一编排中心；维护队列、计划、确认与通知
- `gemini`：持续扫描、前置对齐、复核、审查
- `claude` / Claude Code：内容策略与执行计划（Step 2B）
- `openai`：仅在高风险 / 明显分歧时仲裁（Step 2D）
- `notebooklm`：按需深研 + **配图生成**（infographic，bento-grid 风格）
- `wemedia`：正文创作、改稿、平台适配
- ~~`nanobanana`~~：已废弃（统一使用 NotebookLM）

## Model Rule of Thumb

- **Step 2B 执行计划**：`claude` agent，专注内容策略和叙事结构
- **日常内容生产**：默认 `minimax` 足够，小红书正文、改写、标题、摘要、标签均可
- 不要把整条链路压成单模：前置定义、搜索判断、风险挑刺、合规复核仍交给 `gemini / Claude Code / gpt`
- 高推理模型优先用在"定方向、抓偏差、控风险"

## Delivery Rules

- main 的通知是可靠主链路
- sub-agent 自推仅 best-effort
- 关键进度、失败、HALT、交付摘要必须由 main 保证可见
- 所有级别都必须经过晨星确认门控

## Hard Rules

- 不要把"持续研究 / 队列层"跳过后伪装成完整运营系统
- 不要为了凑产出跳过 Publishability Gate
- 不要未经确认自动发布
- 不要因单点工具失败卡死全链路；必须优雅降级
- 不要默认同时启动多平台分发；需按当前任务明确选择小红书或抖音

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
1. wemedia spawn 的子 agent 不得直接调用任何发布脚本或 CDP 脚本（那是 main + 平台 skill 的职责）
2. wemedia 的正文/描述输出不得混入发布控制元信息（使用上方标准发布包格式）
3. wemedia 不得直接越位执行平台发布；必须交由 main 在 Step 7.5 调用平台 skill

## Notification Rules

**核心原则**：sub-agent 只返回结果给 main，**不自己推群**。所有群通知由 main 统一发出。

**根因**：`sessions_spawn` 创建的 isolated session 默认没有 `message` 工具权限，配置干预也无法恢复。sub-agent 推群从架构上不可行。

### main 通知规则

- main 是唯一可靠通知节点
- 向职能群 + 监控群 + 晨星DM 三推
- 负责：监控群可见性、补发缺失通知、最终交付通知、告警通知

### 通知类型（三类必须覆盖）

| 类型 | 触发时机 | 发往 |
|------|---------|------|
| **START** | agent 开始执行本步骤时 | main 推送到职能群 + 监控群 + 晨星DM |
| **COMPLETION** | agent 完成本步骤时（含结果摘要） | main 推送到职能群 + 监控群 + 晨星DM |
| **FAILURE** | agent 遇到错误/卡点时 | main 推送到职能群 + 监控群 + 晨星DM |

### 通知内容要求
- START/COMPLETION 必须包含：步骤名称、本步骤做了什么、下一步是什么
- FAILURE 必须包含：步骤名称、错误原因、已尝试的解决措施
- 不得只发"done"、"开始"等空内容

### 步骤对应通知表

| 步骤 | 发往职能群 | 发往监控群 | 发往晨星DM | 发送时机 |
|------|-----------|-----------|---------|---------|
| Step 2A Gemini | ✅ 织梦群 (-5264626153) | ✅ 监控群 (-5131273722) | ✅ 1099011886 | main 代发 |
| Step 2B Claude | ✅ 小克群 (-5101947063) | ✅ 监控群 (-5131273722) | ✅ 1099011886 | main 代发 |
| Step 2C Gemini | ✅ 织梦群 (-5264626153) | ✅ 监控群 (-5131273722) | ✅ 1099011886 | main 代发 |
| Step 2D GPT | ✅ 小曼群 (-5242027093) | ✅ 监控群 (-5131273722) | ✅ 1099011886 | main 代发（L 级）|
| Step 3 wemedia | ✅ 自媒体群 (-5217757957) | ✅ 监控群 (-5131273722) | ✅ 1099011886 | main 代发 |
| Step 4 Gemini | ✅ 织梦群 (-5264626153) | ✅ 监控群 (-5131273722) | ✅ 1099011886 | main 代发 |
| Step 5 配图 | ✅ 自媒体群 (-5217757957) | ✅ 监控群 (-5131273722) | ✅ 1099011886 | main 代发 |

## When To Go Deeper

出现以下情况时，继续读取 reference：
- 需要完整运营路由和分级规则 → `references/ops-routing-v1.1.md`
- 需要老版细节对照或迁移核验 → `references/pipeline-wemedia-v1.1-contract.md`
- 需要流程图辅助理解 → `references/PIPELINE_FLOWCHART_V1_1_EMOJI.md`

---

## 与平台发布 Skills 的联动关系

**本质**：wemedia = 自媒体运营 / 创作 / 平台适配层；平台 skill（如 douyin、xiaohongshu）= 最终发布执行层。

**联动链路**：

```text
wemedia（Step 2-6）
    → 完成选题、创作、改稿、配图、平台适配
    → 产出平台化发布包
    ↓
main（Step 7）
    → 向晨星请求确认
    ↓
main（Step 7.5）
    → 按平台选择具体 skill：
      - 小红书 → xiaohongshu skill
      - 抖音 → douyin skill
    ↓
platform skill
    → 执行上传 / 填表 / 封面 / 提交 / 审核等待
    ↓
main
    → 回报结果 + 进入 Step 8 日结/复盘
```

### NotebookLM 配图规则

配图仍由 wemedia 编排、NotebookLM 执行，且必须使用**临时 notebook**：
1. `notebooklm notebooks add --name "temp-{标识}" --desc "配图临时notebook"`
2. 获取临时 notebook ID
3. `notebooklm source add --notebook {temp_id} --path {正文.txt}`
4. `notebooklm generate infographic --notebook {temp_id} --orientation square --style bento-grid --language zh_Hans --detail detailed --wait "{配图描述}"`
5. 下载并重命名产物
6. 删除临时 notebook

**禁止**：不得使用共享 notebook 直接生成发布配图，必须走临时 notebook 流程。

### 抖音联动
- wemedia 负责产出 `Douyin Publish Pack`
- main 读取并校验 `shared-context/DOUYIN-PUBLISH-PACK-SCHEMA.md`
- main 调用 `douyin/scripts/publish_douyin.py`
- douyin skill 只做执行，不重写内容

### 小红书联动
- wemedia 继续产出小红书标准交付物
- main 调用小红书执行 skill 完成发布

**wemedia 维护什么**：内容队列、Constitution-First 创作流程、平台适配、发布包定义。

**平台 skill 维护什么**：平台脚本、登录态、页面控件交互、提交流程、审核/结果回传。

**main 的职责**：唯一编排中心；负责确认门控、通知、调用执行层、汇总结果。
