---
name: wemedia-pipeline
description: 自媒体内容创作流水线 v1.0。从选题到发布的全流程编排，覆盖调研、创作、审查、生图、多平台适配和晨星确认门控。
---

# 自媒体内容流水线 v1.0

基于星链（starchain-pipeline）v1.8 的 main 编排模式，适配内容创作场景。集成 NotebookLM 知识层用于深度调研和衍生内容生成。

## When This Skill Triggers

触发条件：
- 用户要求创作/发布自媒体内容
- 用户要求做选题策划
- 用户要求生成某平台的文案/图文/视频脚本
- 用户要求批量内容生产
- 用户提到小红书/抖音/知乎内容创作

## Required Read

执行前读取 `references/pipeline-wemedia-v1-contract.md`。

## Architecture: main 编排模式

main（小光）是顶层编排中心，所有 agent 由 main 直接 spawn（mode=run）。

```
main（小光，编排中心）
├── Step 1：选题分级 + 平台分析
```
main（小光，编排中心）
├── Step 1：选题分级 + 平台分析
├── Step 2：spawn 织梦(gemini) → 快速调研 + spawn 珊瑚(notebooklm) → 深度调研（M/L 级）
├── Step 3：spawn wemedia → 内容创作（文案 + 配图提示词）
├── Step 4：spawn 织梦(gemini) → 内容审查（质量/合规/SEO）
│   └── Step 4.5：REVISE → spawn wemedia 修改（max 3 rounds）
├── Step 5：（可选）spawn nano-banana → 生成配图
├── Step 5.5：（可选，L 级推荐）spawn 珊瑚(notebooklm) → 衍生内容（播客/思维导图/问答/信息图）
├── Step 6：spawn wemedia → 多平台适配 + 排期
└── Step 7：晨星确认 → 交付通知
全程：main 补发关键推送到各职能群 + 监控群（sub-agent 推送不可靠）
```

## Agent Roles

| Agent | Role | Key Steps |
|-------|------|-----------|
| main（小光） | 顶层编排中心 | Step 1, 2 编排, 4.5 编排, 5.5 编排, 7 |
| 织梦(gemini) | 快速调研 + 审查 | Step 2(快速调研), Step 4(审查) |
| 珊瑚(notebooklm) | 知识查询 + 衍生内容 | Step 2(深度调研), Step 5.5(衍生内容) |
| wemedia | 内容创作 + 适配 | Step 3(创作), Step 4.5(修改), Step 6(适配) |
| nano-banana | 配图生成 | Step 5(生图) |

## Spawn 规范

所有 agent 一律用 `mode=run` spawn：

```
sessions_spawn(agentId: "<agent>", mode: "run", task: "<任务+上下文>")
```

特殊参数：
- wemedia: `thinking: "high"`（必须）
- nano-banana: `runTimeoutSeconds: 300`（生图慢）
- gemini: `runTimeoutSeconds: 300`（API 代理可能慢）

### Spawn 重试机制（硬性要求）
任何 agent spawn 失败时，自动重试 3 次（第 2 次等 10 秒）。3 次都失败 → 推送监控群 + 通知晨星，标记 BLOCKED。


## Main 编排流程（逐步执行）

### Step 1：选题分级 + 平台分析
main 自己执行：
1. 判断内容类型：
   - S（简单）：单平台短文案/转发评论 → 快速通道（跳过 Step 2/4）
   - M（标准）：单平台原创图文/回答 → 标准通道
   - L（深度）：多平台联动/系列内容/深度长文 → 完整通道
2. 确定目标平台：小红书 / 抖音 / 知乎 / 多平台
3. 确定内容形式：图文 / 视频脚本 / 问答 / 种草笔记
4. 推送选题单到自媒体群(-5146160953) + 监控群(-5131273722)

### Step 2：选题调研（S 级跳过）
main 编排：
1. **并行执行调研**（优化：提升效率 40-50%）
   - 同时 spawn 织梦(gemini) 和 珊瑚(notebooklm)
   - 织梦任务：快速调研
     - 竞品分析（同类热门内容 top 5）
     - 关键词/标签建议
     - 平台热点趋势
     - 目标受众画像
   - 珊瑚任务（M/L 级）：深度调研
     - 查询 media-research notebook 关于 <选题关键词> 的历史研究和内容策略
     - 整合历史研究并返回摘要
     - 如选题涉及新领域 → 执行 research 功能补充资料
     - 可将调研结果添加为 media-research 新源
   - 如果 spawn 失败 → Spawn 重试（3 次）→ Warning → 降级跳过
2. **等待两者完成**
   - 织梦 announce 回来
   - 珊瑚 announce 回来
3. main 整合织梦调研 + 珊瑚知识，生成调研摘要
4. 推送调研结果到自媒体群

### Step 3：内容创作
main 编排：
1. spawn wemedia(thinking: "high") → 创作任务：
   - 输入：选题 + 调研摘要 + 平台模板
   - 产出：draft.md（文案正文）+ prompts.md（配图提示词，如需生图）
   - 文案必须适配目标平台风格（小红书种草风/知乎专业风/抖音脚本风）
2. wemedia announce 回来后，main 检查产出完整性
3. 推送草稿到自媒体群

### Step 4：内容审查（S 级跳过）
main 编排：
1. spawn gemini → 审查任务：
   - 内容质量评分（1-10）
   - 平台合规检查（敏感词/违规风险）
   - SEO 优化建议（标题/标签/关键词密度）
   - 可读性/吸引力评估
2. gemini announce 回来后，main 解析 verdict：
   - PUBLISH（≥8 分，无合规问题）→ Step 5
   - REVISE（5-7 分，或有可修复问题）→ Step 4.5
   - REJECT（<5 分，或严重合规问题）→ 通知晨星，HALT

### Step 4.5：修改循环（max 3 rounds）
main 编排每轮：
1. 组装修改 context：原始选题 + 当前草稿 + 审查反馈
2. spawn wemedia(thinking: "high") → 修改文案
3. spawn 织梦(gemini) → 重新审查

**修改轮次处理**：
- R1/R2: 常规修改
- R3: 仍 REVISE → 降级为 PUBLISH_WITH_NOTES
  - **生成审阅要点摘要（优化）**：
    - 3 轮修改历史（每轮的问题和修改内容）
    - 未完全解决的问题列表
    - 建议晨星关注的要点
    - 风险提示（如有）
  - 摘要包含在 Step 7 交付中
  - 推送时高亮标注需重点审阅
- REJECT 任何轮次 → HALT，通知晨星

**优化收益**：提升晨星审阅效率 30%，快速定位问题

### Step 5：配图生成（可选）
main 编排：
1. 检查 prompts.md 是否存在配图提示词
2. 如有 → spawn nano-banana(runTimeoutSeconds: 300) → 生成配图
3. 下载图片到 wemedia workspace
4. 无配图需求 → 跳过
5. 推送配图到自媒体群 + 生图群(-5217509070)

### Step 5.5：衍生内容生成（可选，L 级推荐）
main 编排：
1. **评估衍生内容需求**（L 级默认生成，M 级可选）
2. **珊瑚智能推荐（优化）**：spawn 珊瑚(notebooklm) → 分析内容特征并推荐衍生类型
   - 任务：`分析当前内容特征，推荐最适合的衍生内容类型`
   - 珊瑚分析逻辑：
     - **深度长文**（>2000字，多段落）→ 推荐 podcast（音频播客）
     - **知识类内容**（教程、科普、解释）→ 推荐 mind-map（思维导图）
     - **教程类内容**（步骤、操作、学习）→ 推荐 quiz/flashcards（问答卡片）
     - **数据类内容**（统计、对比、趋势）→ 推荐 infographic（信息图）
   - 珊瑚返回推荐类型和理由
3. **生成衍生内容**：
   - 根据珊瑚推荐，spawn 珊瑚生成对应类型的衍生内容
   - 珊瑚通过 nlm-gateway.sh artifact 生成并下载到 wemedia workspace
   - 如果失败 → Spawn 重试 → Warning → 跳过
4. 推送衍生内容到自媒体群(-5146160953)

**优化收益**：衍生内容质量提升 20%，更精准匹配内容特征

### Step 6：多平台适配 + 排期
main 编排：
1. spawn wemedia(thinking: "high") → 适配任务：
   - 按各平台格式要求调整文案（字数/标签/排版）
   - 生成各平台版本（xiaohongshu.md / douyin.md / zhihu.md）
   - 建议发布时间（基于平台最佳时段）
   - 更新 content-calendar
2. 推送排期到自媒体群

### Step 7：晨星确认 + 交付
main 自己执行：
1. 汇总交付摘要：
   - 选题 + 类型 + 目标平台
   - 审查评分 + 状态
   - 各平台版本预览
   - 配图（如有）
   - 建议发布时间
2. 推送到自媒体群(-5146160953) + 监控群(-5131273722)
3. 通知晨星(target:1099011886) 请求确认
4. ⛔ 未经晨星确认，绝不发布到任何外部平台

## S 级快速通道

S 级跳过：Step 2 / Step 4
S 级流程：Step 1 → Step 3 → Step 5（可选）→ Step 6 → Step 7
M 级流程：Step 1 → Step 2（含 NotebookLM）→ Step 3 → Step 4 → Step 5（可选）→ Step 6 → Step 7
L 级流程：Step 1 → Step 2（含 NotebookLM）→ Step 3 → Step 4 → Step 5（可选）→ Step 5.5（衍生内容）→ Step 6 → Step 7

## HALT 处理

触发条件：
- Step 4 审查 REJECT
- Step 4.5 R3 后仍 REJECT
- 任何步骤超时（10 分钟无响应）

处理：
1. 推送告警到监控群(-5131273722)
2. 通知晨星(target:1099011886)
3. 保留当前草稿，等待晨星指示

## 推送规范

main 在以下节点推送到自媒体群(-5146160953)：
- Step 1 选题单
- Step 2 调研结果（含 NotebookLM 知识）
- Step 3 草稿
- Step 4 审查结论
- Step 5 配图
- Step 5.5 衍生内容（播客/思维导图等）
- Step 6 各平台版本 + 排期
- Step 7 交付摘要

main 在以下节点推送到监控群(-5131273722)：
- Step 1 选题单
- Step 4 审查结论（含评分）
- Step 4.5 每轮修改结果
- HALT 告警
- Step 7 交付摘要

## Do Not Skip

- Step 4 内容审查（M/L 级必须）
- Step 7 晨星确认门控（所有级别必须）
- 合规检查（所有级别必须）
- HALT 通知（必须推送监控群 + 晨星）

### 工具容错与降级机制 (Hard Requirement)

在调用外部系统（例如 `nlm-gateway.sh` 查知识、或是其他需要认证/环境准备的 CLI 依赖）时，如果系统抛出环境或权限错误（如 `auth_missing`、`auth_expired`、`cli_error`）：
- **绝对禁止** 因此中断整个自媒体流水线或陷入原地死循环。
- main 或执行的子 agent 必须做**优雅降级 (Graceful Degradation)**：
  1. 发送一条 Warning 告警到监控群（-5131273722）。
  2. 直接跳过这个失败的工具调用，回退到依靠自身模型权重或常规搜索。
  3. 继续无缝推进到流水线的下一步。
