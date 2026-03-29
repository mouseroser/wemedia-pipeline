---
name: wemedia-pipeline
description: 自媒体运营系统 v1.1。用于 24/7 内容运营：Gemini 持续扫描 → main 维护队列 → Publishability Gate → Constitution-First（S级：2A颗粒度对齐+2B宪法边界；M/L级：2A+2B+2C内容计划+2D复核，必要时GPT仲裁）→ wemedia subagent 端到端创作/配图/平台适配 → 晨星确认门控 → main 通知 wemedia 执行 Step 7.5 发布，wemedia 再调用平台执行 skill（如 xiaohongshu / douyin）。适用于选题发现、内容计划、单条内容生产和日结复盘。
---

# 自媒体运营系统 v1.1

把这项 skill 视为 **运营系统 skill**，不是单次内容生成器。

## Required Read

先读：
1. `references/ops-routing-v1.1.md` - 当前正式执行路由（优先）
2. `references/PIPELINE_FLOWCHART_V1_1_EMOJI.md` - 流程图

按需再读：
- `references/pipeline-wemedia-v1.1-contract.md` - 旧版 v1.1 详细合约，仅在需要核对历史设计时读取
- `~/.openclaw/workspace/shared-context/DOUYIN-PUBLISH-PACK-SCHEMA.md` - 需要产出抖音发布包时读取
- `~/.openclaw/workspace/shared-context/XIAOHONGSHU-PUBLISH-PACK-SCHEMA.md` - 需要产出小红书发布包时读取
- `~/.openclaw/workspace/shared-context/WEMEDIA-SKILL-MAP.md` - 三层调用关系与路径约定

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

**main 的角色**：编排 + 监控 + 确认门控；Step 7 确认后，由 main 向 wemedia 下发发布指令并负责结果回报。

**硬边界**：Step 7 之前，wemedia 只产出发布包，不得擅自发布；Step 7 确认后，由 wemedia 执行 Step 7.5，并调用具体平台 skill（如 xiaohongshu / douyin）。main 不直接越位替代平台执行细节。

## Current Scope

- 当前激活平台：**小红书、抖音**
- 知乎 / X 模板保留，但默认不启动
- 搜索策略：**Gemini 搜索优先**；`web_fetch` 抓正文；`browser` 做复杂页面兜底
- Brave Search API 不是当前必需前置
- 未经晨星确认，绝不外发

## 内容交付物格式（wemedia Step 6 产出 → main 确认门控 → wemedia Step 7.5 执行）

wemedia agent 完成创作后，必须输出**平台化发布包**。默认分两类：

### A. 小红书发布包

```
平台：xiaohongshu
内容ID：{唯一标识}
标题：{≤20字}
正文：
{正文内容，≤1000字}
图片路径：
- {绝对路径1}
- {绝对路径2}
标签：{≤10个，用逗号分隔}
可见性：{public|private，默认 public}
备注：{可选}
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

**统一 schema**：
- 小红书：`~/.openclaw/workspace/shared-context/XHS-PUBLISH-PACK-SCHEMA.md`
- 抖音：`~/.openclaw/workspace/shared-context/DOUYIN-PUBLISH-PACK-SCHEMA.md`

**保存位置**：
- 小红书：`~/.openclaw/workspace/intel/collaboration/media/wemedia/xiaohongshu/{content_id}.md`
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
  - Step 2A：Gemini 颗粒度对齐
  - Step 2B：GPT/OpenAI 宪法边界
  - Step 2C：Claude 计划
  - Step 2D：Gemini 复核
  - Step 2E：按需仲裁
- Step 3：wemedia 创作
- Step 4：gemini 审查
- Step 4.5：修改循环
- Step 5：配图生成（**NotebookLM 统一路线**）
- Step 5.5：notebooklm 衍生内容（其他格式：podcast/mind-map/quiz）
- Step 6：平台适配 + 发布包生成
- Step 7：晨星确认
- **Step 7.5：wemedia 收到 main sessions_send 放行指令后，自行执行平台发布，完成后 sessions_send 回 main**
- Step 8：日结 / 周复盘

## Agent Roles

- `main`：守两个门（Step 1.5 Publishability Gate + Step 7 晨星确认门控）；通过 `sessions_send` 触发 wemedia persistent session，不再逐步编排 Step 2-6
- `gemini`：持续扫描、Step 2A 颗粒度对齐、Step 2D 复核、Step 4 审查
- `openai`：Step 2B 宪法边界；必要时参与高风险仲裁
- `claude` / Claude Code：Step 2C 内容策略与执行计划
- `notebooklm`：按需深研 + **配图生成**（infographic，bento-grid 风格）— **由 wemedia spawn 调用，完成后自推珊瑚群 (-5202217379)**
- `wemedia`：**编排协调者**，自己执行 Step 3（创作）/ Step 4.5（修改）/ Step 6（发布包）/ Step 7.5（发布），spawn 各职能 agent 执行 Step 2A/2B/2C/2D/4/5；Step 6 完成后 `sessions_send` 回 main 等待确认，收到 Step 7 放行后执行发布，结果 `sessions_send` 回 main
- ~~`nanobanana`~~：已废弃（统一使用 NotebookLM）

## Model Rule of Thumb

- **Step 2A 颗粒度对齐**：`gemini` agent，负责受众定义、平台定位、标题方向、内容颗粒度与问题 framing
- **Step 2B 宪法边界**：`openai` agent，负责 must / must-not、表达边界、风险边界、不可夸大点
- **Step 2C 执行计划**：`claude` agent，专注内容策略和叙事结构
- **Step 2D 一致性复核**：`gemini` agent，检查是否偏离前两步定义
- **日常内容生产**：默认 `minimax` 足够，小红书正文、改写、标题、摘要、标签均可
- 不要把整条链路压成单模：颗粒度对齐交给 `gemini`，宪法边界交给 `openai/gpt`，执行计划交给 `Claude Code`，复核交给 `gemini`
- 高推理模型优先用在"定边界、抓偏差、控风险"

## Delivery Rules

- **sessions_send 是可靠通道**：wemedia Step 6/7.5 完成必须 sessions_send 回 main，不依赖 announce
- **职能群通知**：wemedia 在每个步骤完成时主动推对应职能群（织梦/小曼/小克/珊瑚/自媒体），best-effort
- **监控群**：由 main 在终态/异常时统一推送，wemedia 不推
- 所有级别都必须经过晨星确认门控（Step 7）

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
1. Step 7 之前，wemedia spawn 的子 agent 不得直接调用任何发布脚本或 CDP 脚本；只有收到 main 的确认后发布指令，才可执行 Step 7.5
2. wemedia 的正文/描述输出不得混入发布控制元信息（使用上方标准发布包格式）
3. Step 7.5 的 owner 是 wemedia：由 main 通知、wemedia 执行、平台 skill 落地；main 不直接代跑平台发布

## Notification Rules

**核心原则**：sub-agent 只返回结果给 main，**不自己推群**。所有群通知由 main 统一发出。

**根因**：`sessions_spawn` 创建的 isolated session 默认没有稳定的 `message` 能力；即使表面可用，也不应把 sub-agent 自推当作可靠送达。**因此流程图 / reference 中的推送定义只是路由说明，不是执行 owner 定义。**

**执行口径**：职能群由各 agent 自推（best-effort）；`main` 只负责监控群终态 / 异常、最终交付与告警。

### main 通知规则

- main 是**监控群 + 晨星 DM**的可靠通知节点
- **职能群**：默认由各 agent 自推步骤级 START / COMPLETION / FAILURE（best-effort）
- **监控群**：只承接终态 / 异常
- **晨星DM**：只用于 Step 7 确认、BLOCKED/FAILURE 需介入、最终结果、L级/长任务关键阶段摘要
- 如果任务本身就在晨星 DM 中进行，默认直接在当前对话回复，不再重复主动 DM
- 负责：监控群终态/异常可见性、最终交付通知、告警通知
- 调 `message(action="send")` 时，**单发必须用 `target`**，不要用 `targets`
- 需要发多个群时，必须按**单目标串行发送多次**；`targets` 只允许用于 `action="broadcast"`
- 禁止把多个群 id 塞进一次 `send`，否则运行时可能误判为“无显式目标”，回退到当前会话

### 通知类型（三类必须覆盖）

| 类型 | 触发时机 | 发往 |
|------|---------|------|
| **START** | agent 开始执行本步骤时 | agent 自推职能群（best-effort）；main 仅在终态/异常时推监控群；晨星DM 仅按条件触发 |
| **COMPLETION** | agent 完成本步骤时（含结果摘要） | agent 自推职能群（best-effort）；main 仅在终态/异常时推监控群；晨星DM 仅按条件触发 |
| **FAILURE** | agent 遇到错误/卡点时 | agent 可自推职能群；main 推监控群；晨星DM 在需要介入时必发 |

### 通知内容要求
- START/COMPLETION 必须包含：步骤名称、本步骤做了什么、下一步是什么
- FAILURE 必须包含：步骤名称、错误原因、已尝试的解决措施
- 不得只发"done"、"开始"等空内容

### 步骤对应通知表（完整流水线）

| 步骤 | 发往职能群 | 发往监控群 | 发往晨星DM | 发送时机 |
|------|-----------|-----------|---------|---------|
| Step 0 持续研究层 | ✅ 织梦群 (-5264626153) | ✅ 监控群 (-5131273722) | 按需（仅长任务/关键摘要） | agent 自推 + main 在终态/异常时推监控群 |
| Step 1 内容队列层 | ✅ 自媒体群 (-5146160953) | ✅ 监控群 (-5131273722) | 否 | agent 自推 + main 在终态/异常时推监控群 |
| Step 1.5 Publishability Gate | ✅ 自媒体群 (-5146160953) | ✅ 监控群 (-5131273722) | 按需（仅方向变化/不开工结论） | agent 自推 + main 在终态/异常时推监控群 |
| Step 2A Gemini（颗粒度对齐） | ✅ 织梦群 (-5264626153) | ✅ 监控群 (-5131273722) | 否 | agent 自推 + main 在终态/异常时推监控群 |
| Step 2B GPT/OpenAI（宪法边界） | ✅ 小曼群 (-5242027093) | ✅ 监控群 (-5131273722) | 否 | agent 自推 + main 在终态/异常时推监控群 |
| Step 2C Claude（执行计划） | ✅ 小克群 (-5101947063) | ✅ 监控群 (-5131273722) | 否 | agent 自推 + main 在终态/异常时推监控群 |
| Step 2D Gemini（复核） | ✅ 织梦群 (-5264626153) | ✅ 监控群 (-5131273722) | 否 | agent 自推 + main 在终态/异常时推监控群 |
| Step 2E 仲裁（按需） | ✅ 小曼群 / 小克群（视实际执行者） | ✅ 监控群 (-5131273722) | 按需（仅重大分歧/升级） | agent 自推 + main 在终态/异常时推监控群（仅需要时） |
| Step 3 wemedia 创作 | ✅ 自媒体群 (-5146160953) | ✅ 监控群 (-5131273722) | 否 | agent 自推 + main 在终态/异常时推监控群 |
| Step 4 Gemini 审查 | ✅ 织梦群 (-5264626153) | ✅ 监控群 (-5131273722) | 否 | agent 自推 + main 在终态/异常时推监控群 |
| Step 4.5 wemedia 修改循环 | ✅ 自媒体群 (-5146160953) | ✅ 监控群 (-5131273722) | 否 | agent 自推 + main 在终态/异常时推监控群（每轮或关键轮次） |
| Step 5 NotebookLM 配图 | ✅ 自媒体群 (-5146160953) | ✅ 监控群 (-5131273722) | 否 | agent 自推 + main 在终态/异常时推监控群 |
| Step 5.5 NotebookLM 衍生内容 | ✅ 自媒体群 (-5146160953) | ✅ 监控群 (-5131273722) | 按需 | agent 自推 + main 在终态/异常时推监控群（按需） |
| Step 6 平台适配 + 发布包 | ✅ 自媒体群 (-5146160953) | ✅ 监控群 (-5131273722) | 按需（仅长任务阶段摘要） | agent 自推 + main 在终态/异常时推监控群 |
| Step 7 晨星确认 | ✅ 自媒体群 (-5146160953) | ✅ 监控群 (-5131273722) | ✅ 必发 | main 统一交付（并推监控群） |
| Step 7.5 wemedia 发布执行 | ✅ 自媒体群 (-5146160953) | ✅ 监控群 (-5131273722) | 仅 FAILURE / 最终结果 | main 负责开始/结果/失败通知 |
| Step 8 日结 / 周复盘 | ✅ 自媒体群 (-5146160953) | ✅ 监控群 (-5131273722) | 按需（仅重要复盘摘要） | agent 自推 + main 在终态/异常时推监控群 |

**说明**：
- `wemedia` 职能群统一使用 **-5146160953**；旧的 `-5217757957` 视为历史遗留，不再使用。
- Step 7.5 的执行 owner 是 `wemedia`，但**可靠通知 owner 仍是 `main`**。

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
main（Step 7.5 触发）
    → 确认后向 wemedia 下发发布指令
    ↓
wemedia（Step 7.5 执行）
    → 按平台选择具体 skill：
      - 小红书 → xiaohongshu skill
      - 抖音 → douyin skill
    ↓
platform skill
    → 执行上传 / 填表 / 封面 / 提交 / 审核等待
    ↓
wemedia → main
    → 回传结果；main 负责监控通知与 Step 8 日结/复盘
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

### 可执行发布包自动落盘
- wemedia 可使用：`scripts/build_publish_pack.py`
- 用途：把标题/正文/素材路径组装成可执行发布包，并自动落盘到协作目录
- 支持平台：`douyin` / `xiaohongshu`
- 输出结果：JSON `{ ok, platform, path }`

### 抖音联动
- wemedia 负责产出 `Douyin Publish Pack`
- 产出模板见：`references/douyin-publish-pack-template.md`
- main 在 Step 7 确认后通知 wemedia 执行
- wemedia 读取并校验 `shared-context/DOUYIN-PUBLISH-PACK-SCHEMA.md`
- wemedia 调用 `douyin/scripts/publish_douyin.py --pack <path>`
- douyin skill 只做执行，不重写内容

### 小红书联动
- wemedia 产出 `Xiaohongshu Publish Pack`
- 产出模板见：`references/xiaohongshu-publish-pack-template.md`
- main 在 Step 7 确认后通知 wemedia 执行
- wemedia 读取并校验 `shared-context/XHS-PUBLISH-PACK-SCHEMA.md`
- wemedia 调用小红书执行 skill 完成发布

**wemedia 维护什么**：内容队列、Constitution-First 创作流程、平台适配、发布包定义，以及确认后的发布执行。

**平台 skill 维护什么**：平台脚本、登录态、页面控件交互、提交流程、审核/结果回传。

**main 的职责**：唯一编排中心；负责确认门控、向 wemedia 下发发布指令、监控通知与结果汇总。
