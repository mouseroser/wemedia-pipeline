# 自媒体 24/7 运营系统 v1.1 — 可执行落地清单

> 基于晨星 2026-03-18 方案，选项 B 格式
> Signal → Queue → Constitution → Draft → Review → Adapt → Confirm
> 已吸收 v1.1 优化：HOT-SCAN-INBOX 单写者拆分、通知分级、Publishability Gate、JSON 状态源预留、Main 计划任务轻量化

---

## 总览：四阶段落地

| Phase | 目标 | 预计耗时 | 依赖 |
|-------|------|---------|------|
| 1 | 持续研究层 — 自动扫题 | 3-5 天 | 无 |
| 2 | 内容队列层 — 结构化选题池 | 5-7 天 | Phase 1 |
| 3 | 多平台适配 + 衍生内容强化 | 7-10 天 | Phase 2 |
| 4 | 运营复盘闭环 | 7 天 | Phase 3 |

---

## Phase 1：持续研究层（3-5 天）

### 1.1 新增文件

#### `intel/media-ops/DAILY-SIGNAL-BRIEF.md`
> 写入者：gemini | 其他 agent 只读

```markdown
# 每日信号简报 — YYYY-MM-DD

## 今日 AI 热点 Top 5
| # | 热点 | 来源 | 可信度 | 与晨星方向相关度 | 推荐平台 | 建议今天做？ |
|---|------|------|--------|-----------------|---------|------------|
| 1 | | | ⭐⭐⭐⭐⭐ | 🔴高/🟡中/🟢低 | | ✅/❌ |

## 值得关注但不紧急
- 

## 风险/敏感话题提醒
- 

## 信号来源
- X/Twitter 趋势
- Hacker News Top
- GitHub Trending
- Google AI Blog
- 最新论文
- 竞品动态

---
更新时间: HH:MM
扫描者: gemini
```

#### `intel/media-ops/HOT-QUEUE.md`
> 写入者：gemini（扫描添加）+ main（状态更新）| wemedia 只读

```markdown
# 热点内容队列

## 🔴 紧急（4h 内出稿）
| 选题 | 来源 | 发现时间 | 时效窗口 | 推荐平台 | 推荐形式 | 状态 |
|------|------|---------|---------|---------|---------|------|

## 🟡 今日可做
| 选题 | 来源 | 发现时间 | 推荐平台 | 推荐形式 | 状态 |
|------|------|---------|---------|---------|------|

## 🟢 储备（本周内可做）
| 选题 | 来源 | 推荐平台 | 优先级 | 状态 |
|------|------|---------|--------|------|

## 状态说明
- `待评估` → `已排期` → `创作中` → `审查中` → `待确认` → `已发布` / `已弃用`

---
最后更新: YYYY-MM-DD HH:MM
```

#### `shared-context/MEDIA-CONSTITUTION.md`
> 写入者：main（晨星确认后更新）| 所有 agent 只读

```markdown
# 内容宪法 — 自媒体运营系统

## 账号定位
- 核心领域：AI / Agent / 效率工具
- 定位关键词：[待晨星定义]
- 目标受众：[待晨星定义]

## 内容边界
### ✅ 写什么
- AI 工具实操
- Agent 搭建经验
- 效率提升方法论
- 行业趋势解读

### ❌ 不写什么
- 政治敏感
- 未验证的投资建议
- 攻击竞品
- 纯蹭热点无价值内容

## 风格约束
- [待晨星定义：例如 emoji 使用、语气、人称等]

## 品牌语气
- [待晨星定义]

## 平台优先级
1. [待晨星排序：小红书 / 知乎 / 抖音 / X / Newsletter]

## "值不值得发"的判断标准
1. 与核心领域相关度 ≥ 中
2. 能提供独特价值（不是纯搬运）
3. 时效性：热点 4h 窗口 / 常青无限制
4. 晨星精力：当天是否有带宽审核
```

### 1.2 新增 Cron

#### Cron 1：早间信号扫描（07:30 CST）

```yaml
name: media-signal-morning
schedule: { kind: "cron", expr: "30 7 * * *", tz: "Asia/Shanghai" }
sessionTarget: isolated
payload:
  kind: agentTurn
  message: |
    你是 gemini agent，执行每日早间信号扫描。

    任务：
    1. 搜索过去 12 小时的 AI/Agent/LLM 领域热点
    2. 使用 web_search 搜索以下关键词（每个搜 1-2 次）：
       - "AI agent" OR "LLM" site:news.ycombinator.com
       - "AI" trending on GitHub
       - 最新 AI 产品发布
    3. 读取 shared-context/MEDIA-CONSTITUTION.md 了解内容边界
    4. 按模板更新 intel/media-ops/DAILY-SIGNAL-BRIEF.md
    5. 有新的高相关度热点时，追加到 intel/media-ops/HOT-QUEUE.md
    6. 向监控群(-5131273722)推送简报摘要（Top 3 + 是否有紧急热点）

    输出原则：
    - 每个热点必须有来源链接
    - 不确定的标记 [UNVERIFIED]
    - 与晨星方向无关的不要列入
  model: gemini/gemini-3.1-pro-preview
  timeoutSeconds: 600
delivery: { mode: "announce" }
agentId: gemini
```

#### Cron 2：午间补扫（12:30 CST）

```yaml
name: media-signal-noon
schedule: { kind: "cron", expr: "30 12 * * *", tz: "Asia/Shanghai" }
sessionTarget: isolated
payload:
  kind: agentTurn
  message: |
    你是 gemini agent，执行午间信号补扫。

    任务：
    1. 读取 intel/media-ops/DAILY-SIGNAL-BRIEF.md（今日早间版）
    2. 搜索上午 08:00 至现在的新热点
    3. 如有重大新热点：
       - 更新 DAILY-SIGNAL-BRIEF.md
       - 追加到 HOT-QUEUE.md（标记"午间发现"）
       - 向监控群推送插队提醒
    4. 如无重大变化：只在 DAILY-SIGNAL-BRIEF.md 末尾追加"午间无重大更新"

    判断"重大"标准：
    - 大厂发布新模型/产品
    - GitHub 24h 内 1k+ stars 的 AI 项目
    - 行业重要人物发表重要观点
  model: gemini/gemini-3.1-pro-preview
  timeoutSeconds: 300
delivery: { mode: "announce" }
agentId: gemini
```

#### Cron 3：晚间储备（18:00 CST）

```yaml
name: media-signal-evening
schedule: { kind: "cron", expr: "0 18 * * *", tz: "Asia/Shanghai" }
sessionTarget: isolated
payload:
  kind: agentTurn
  message: |
    你是 gemini agent，执行晚间信号总结 + 明日储备。

    任务：
    1. 读取今日 DAILY-SIGNAL-BRIEF.md 全部内容
    2. 读取 HOT-QUEUE.md 当前状态
    3. 总结今日信号收获：
       - 哪些热点已被晨星采纳
       - 哪些被跳过（记录原因）
       - 哪些值得明天继续跟踪
    4. 生成明日候选选题（2-3 个），追加到 HOT-QUEUE.md 的"储备"区
    5. 向监控群推送日终信号总结（3-5 行）

    原则：
    - 聚焦"明天可以做什么"
    - 标注哪些适合深研究（NotebookLM）
    - 标注哪些适合快速出稿（S 级）
  model: gemini/gemini-3.1-pro-preview
  timeoutSeconds: 300
delivery: { mode: "announce" }
agentId: gemini
```

### 1.3 Agent 配置变更

#### gemini/AGENTS.md — 新增"自媒体信号扫描"职责

在现有职责末尾追加：

```markdown
### 自媒体运营系统 v1 — 信号扫描

#### 职责
- 每日三次信号扫描（早 07:30 / 午 12:30 / 晚 18:00）
- 维护 intel/media-ops/DAILY-SIGNAL-BRIEF.md
- 维护 intel/media-ops/HOT-QUEUE.md（添加新热点）
- 判断热点与晨星方向的相关度

#### 单写者原则
- ✅ 可写：DAILY-SIGNAL-BRIEF.md、HOT-QUEUE.md（新增条目）
- ❌ 不写：DAILY-PUBLISH-PLAN.md（main 写）、drafts/（wemedia 写）

#### 扫描原则
- 每个热点必须有来源链接
- 不确定的标记 [UNVERIFIED]
- 与晨星方向无关的不列入
- 不做内容创作判断，只做信号发现
```

### 1.4 Heartbeat 新增检查项

在 HEARTBEAT.md 追加：

```markdown
### 自媒体信号检查
检查今日信号简报是否已生成：
```bash
today=$(date +%Y-%m-%d)
grep -q "$today" ~/.openclaw/workspace/intel/media-ops/DAILY-SIGNAL-BRIEF.md 2>/dev/null && echo "SIGNAL_OK" || echo "SIGNAL_MISSING"
```

如果 `SIGNAL_MISSING` 且当前时间 > 09:00：
- 检查 `media-signal-morning` cron 是否报错
- 如报错，手动触发
```

### 1.5 Phase 1 验收标准

- [ ] 三个 cron 连续 3 天正常执行
- [ ] DAILY-SIGNAL-BRIEF.md 每天有内容更新
- [ ] HOT-QUEUE.md 有候选题积累
- [ ] MEDIA-CONSTITUTION.md 晨星已填写核心字段
- [ ] Heartbeat 能检测到信号缺失

---

## Phase 2：内容队列层（5-7 天）

### 2.1 新增文件

#### `intel/media-ops/DAILY-PUBLISH-PLAN.md`
> 写入者：main | 其他 agent 只读

```markdown
# 今日发布计划 — YYYY-MM-DD

## 计划概览
- 今日计划产出：X 条
- 优先级最高：[选题名]

## 内容任务
| # | 选题 | 级别 | 平台 | 形式 | 来源队列 | 当前 Step | 依赖 | 状态 |
|---|------|------|------|------|---------|----------|------|------|
| 1 | | S/M/L | | | Hot/Evergreen/Series | | | |

## 各任务详情

### 任务 1: [选题名]
- **Topic**: 
- **Why now**: 为什么值得今天发
- **Platform**: 
- **Goal**: 这条内容要达成什么
- **Audience**: 
- **Risk**: 
- **Grade**: S/M/L
- **Queue source**: Hot/Evergreen/Series

---
生成时间: HH:MM
生成者: main
```

#### `intel/media-ops/EVERGREEN-QUEUE.md`
> 写入者：main（添加）+ gemini（建议）

```markdown
# 常青内容队列

| 选题 | 类型 | 适合平台 | 预估级别 | 是否需要深研究 | 状态 | 备注 |
|------|------|---------|---------|-------------|------|------|
| | 方法论/案例/工具/认知 | | S/M/L | ✅/❌ | 待排期/已排期/已完成 | |

---
最后更新: YYYY-MM-DD
```

#### `intel/media-ops/SERIES-QUEUE.md`
> 写入者：main（规划）+ claude（内容策略建议）

```markdown
# 系列内容队列

## 系列 1: [系列名]
- **主题**: 
- **目标篇数**: 
- **目标平台**: 
- **内容宪法**: [链接或内联]
- **进度**: 0/N

| # | 子主题 | 状态 | 发布日期 | 链接 |
|---|--------|------|---------|------|

---
最后更新: YYYY-MM-DD
```

### 2.2 新增 Cron

#### Cron 4：主编排晨会（08:00 CST）

```yaml
name: media-morning-planning
schedule: { kind: "cron", expr: "0 8 * * *", tz: "Asia/Shanghai" }
sessionTarget: isolated
payload:
  kind: agentTurn
  message: |
    你是 main agent（小光），执行每日内容编排晨会。

    任务：
    1. 读取 intel/media-ops/DAILY-SIGNAL-BRIEF.md
    2. 读取 intel/media-ops/HOT-QUEUE.md
    3. 读取 intel/media-ops/EVERGREEN-QUEUE.md
    4. 读取 shared-context/MEDIA-CONSTITUTION.md
    5. 从队列中挑选 1-3 个今日候选选题
    6. 对每个选题判断：
       - 级别 S/M/L
       - 目标平台
       - 内容形式
       - 是否值得今天推进（用 MEDIA-CONSTITUTION.md 的判断标准）
    7. 生成 intel/media-ops/DAILY-PUBLISH-PLAN.md
    8. 向晨星 DM(1099011886) 推送今日计划摘要（不超过 10 行）
    9. 向监控群(-5131273722) 推送今日计划

    原则：
    - 不贪多，1-2 条高质量 > 5 条凑数
    - S 级可以当天完成，L 级标记"今日启动，非今日交付"
    - 如果没有值得做的题，明确写"今日无合适选题，建议休息"
  model: anthropic/claude-sonnet-4-6
  timeoutSeconds: 600
delivery: { mode: "announce" }
agentId: main
```

### 2.3 现有流水线升级：Step 2 前加判断字段

在 wemedia 和 main 的自媒体流水线触发逻辑中，Step 1 分级后、Step 2 前，加一个字段：

```markdown
### 发布价值预判（Step 1.5 新增）
- **值得今天发吗？** ✅/❌
- **原因**: [1-2 句]
- **如果不发，损失什么？** [时效性损失/无损失]
- **如果发了，期望效果**: [预期]
```

### 2.4 Phase 2 验收标准

- [ ] DAILY-PUBLISH-PLAN.md 每天 08:00 后自动生成
- [ ] 晨星每天早上能在 Telegram 看到今日计划摘要
- [ ] 选题从队列中来，而不是临时想
- [ ] 三个队列（Hot/Evergreen/Series）有内容积累

---

## Phase 3：多平台适配 + 衍生内容强化（7-10 天）

### 3.1 wemedia/AGENTS.md 升级

在 Step 3 内容创作部分，输出要求升级为"编辑部可选项包"：

```markdown
### Step 3 输出升级（运营系统 v1）

一次性产出以下可选项，不只是单一正文：

1. **主稿**（完整正文）
2. **标题备选**（3-5 个，不同风格）
3. **开头钩子版本**（3 个：悬念型/数据型/故事型）
4. **标签建议**（按平台分）
5. **封面提示词**（给 nano-banana）
6. **CTA 备选**（2-3 个）
7. **复用建议**：这份内容适合拆成哪些平台版本
```

### 3.2 Step 4 审查维度升级

gemini 在自媒体审查时，额外检查 4 项：

```markdown
### Step 4 审查扩展（运营系统 v1）

除现有维度外，增加：
1. **平台拟合度**：内容风格是否适合目标平台
2. **开头 3 秒钩子强度**：第一句话是否能抓住注意力
3. **信息密度**：是否有废话/水分
4. **可复用性**：一份主稿能衍生几个平台版本
```

### 3.3 Step 5.5 衍生内容升级

L 级默认触发衍生判断：

```markdown
### Step 5.5 衍生内容评估（L 级默认）

对每条深内容自动判断：
- [ ] 能变播客提纲？
- [ ] 能变问答卡？
- [ ] 能变思维导图？
- [ ] 能变长推 / 知乎回答 / Newsletter 小节？
- [ ] 适合拆成系列？

产出：衍生内容推荐清单（含预估工作量）
```

### 3.4 Step 6 平台策略化适配

wemedia/AGENTS.md 的 Step 6 升级，从"改写"变成"平台策略化适配"：

```markdown
### Step 6 平台适配升级

#### 小红书
- 强开头（第一行即钩子）
- 场景感（代入读者视角）
- 标题抓眼球（emoji + 数字 + 痛点）
- 标签可搜索（3-5 个高频标签）

#### 知乎
- 结构完整（问题→分析→结论）
- 推理链明确
- 背景交代充分
- 专业感（引用来源、数据支撑）

#### 抖音脚本
- 前 3 秒 hook（问题/反转/数据冲击）
- 节奏更快（每句 ≤15 字）
- 镜头提示（口播/录屏/图文切换）

#### X / Twitter（预留）
- 单点爆发
- 密度高
- thread 节奏
- 金句前置
```

### 3.5 Phase 3 验收标准

- [ ] Step 3 产出"编辑部可选项包"而非单一正文
- [ ] Step 4 有平台拟合度等扩展审查
- [ ] L 级内容自动触发衍生内容评估
- [ ] 至少跑通一次完整的多平台适配

---

## Phase 4：运营复盘闭环（7 天）

### 4.1 新增文件

#### `intel/media-ops/WEEKLY-RETRO.md`
> 写入者：main

```markdown
# 周度运营复盘 — YYYY-WXX

## 本周产出统计
- 完成内容：X 条
- 发布内容：X 条
- 打回内容：X 条
- S/M/L 分布：
- 平台分布：

## 效果最好的内容
| 内容 | 平台 | 原因分析 |
|------|------|---------|

## 效果不好 / 被打回的内容
| 内容 | 原因 | 教训 |
|------|------|------|

## 流水线效率
- 从发现到成稿平均耗时：
- 修改轮次平均值：
- 晨星直接通过率：

## 下周重点方向
1. 
2. 
3. 

## 风格记忆更新
- [记录晨星本周的偏好修正]
```

### 4.2 新增 Cron

#### Cron 5：日结复盘（21:30 CST）

```yaml
name: media-daily-retro
schedule: { kind: "cron", expr: "30 21 * * *", tz: "Asia/Shanghai" }
sessionTarget: isolated
payload:
  kind: agentTurn
  message: |
    你是 main agent（小光），执行自媒体日结复盘。

    任务：
    1. 读取今日 DAILY-PUBLISH-PLAN.md
    2. 检查每条任务的最终状态
    3. 汇总到 memory/YYYY-MM-DD.md（追加"自媒体运营"段落）
    4. 如果是周日，生成/更新 intel/media-ops/WEEKLY-RETRO.md
    5. 如有晨星反馈，更新到 wemedia 的 MEMORY.md
    6. 向监控群推送日结摘要（3-5 行）

    原则：
    - 记录"为什么被打回"比"发了几条"更重要
    - 晨星的每次修正都是学习机会
  model: anthropic/claude-sonnet-4-6
  timeoutSeconds: 300
delivery: { mode: "announce" }
agentId: main
```

### 4.3 修改循环结构化记录

Step 4.5 每轮修改必须记录：

```markdown
### 修改记录（结构化）
| 轮次 | 问题 | 修改动作 | 是否解决 | 残留问题 |
|------|------|---------|---------|---------|
| R1 | | | ✅/❌ | |
| R2 | | | ✅/❌ | |
| R3 | | | ✅/❌ | |
```

### 4.4 Phase 4 验收标准

- [ ] 日结 cron 连续 7 天运行
- [ ] 首份 WEEKLY-RETRO.md 生成
- [ ] 晨星反馈被记录到 wemedia/MEMORY.md
- [ ] 修改循环有结构化记录

---

## Step 7 交付包格式（统一）

main 在 Step 7 向晨星推送的统一格式：

```markdown
📦 内容交付 — [选题名]

📌 主题：[一句话]
💡 为什么值得今天发：[1-2 句]
📱 平台：[平台列表]

--- 各平台预览 ---
[小红书版本摘要 / 知乎版本摘要 / ...]

✅ 审查结论：[PUBLISH + 评分]
🎨 视觉资产：[封面图状态]
⏰ 建议发布时间：[时间]
⚠️ 风险备注：[如有]

请回复：
✅ 批准发布
🔄 需要修改（请说明）
⏸️ 暂存
❌ 放弃
```

---

## 单写者原则汇总

| 文件 | 唯一写入者 | 其他 agent |
|------|-----------|-----------|
| DAILY-SIGNAL-BRIEF.md | gemini | 只读 |
| HOT-QUEUE.md | gemini（添加）+ main（状态更新） | 只读 |
| EVERGREEN-QUEUE.md | main + gemini（建议） | 只读 |
| SERIES-QUEUE.md | main + claude（策略建议） | 只读 |
| DAILY-PUBLISH-PLAN.md | main | 只读 |
| WEEKLY-RETRO.md | main | 只读 |
| MEDIA-CONSTITUTION.md | main（晨星确认后） | 只读 |
| drafts/* | wemedia | 只读 |
| platforms/* | wemedia | 只读 |
| content-calendar/* | wemedia | 只读 |

---

## 新增 Cron 总览

| 名称 | 时间 | Agent | Model | 产出 |
|------|------|-------|-------|------|
| media-signal-morning | 07:30 | gemini | gemini-preview | DAILY-SIGNAL-BRIEF + HOT-QUEUE |
| media-signal-noon | 12:30 | gemini | gemini-preview | DAILY-SIGNAL-BRIEF 补更 |
| media-signal-evening | 18:00 | gemini | gemini-preview | 日终总结 + 明日候选 |
| media-morning-planning | 08:00 | main | sonnet | DAILY-PUBLISH-PLAN + 晨星 DM |
| media-daily-retro | 21:30 | main | sonnet | 日结复盘 + memory 更新 |

---

## 执行优先级

### 立即执行（Phase 1 Day 1）
1. ✅ 创建 `intel/media-ops/` 目录
2. ✅ 创建 `DAILY-SIGNAL-BRIEF.md`（模板）
3. ✅ 创建 `HOT-QUEUE.md`（模板）
4. ✅ 创建 `shared-context/MEDIA-CONSTITUTION.md`（骨架，等晨星填写）
5. ✅ 添加早间扫描 cron

### Day 2-3
6. 添加午间和晚间扫描 cron
7. gemini/AGENTS.md 追加信号扫描职责
8. HEARTBEAT.md 追加信号检查项
9. 观察 3 个 cron 运行结果，调优 prompt

### Day 4-5（Phase 1 收尾 + Phase 2 启动）
10. 创建队列文件（EVERGREEN-QUEUE, SERIES-QUEUE, DAILY-PUBLISH-PLAN）
11. 添加主编排晨会 cron
12. Step 2 前加"值不值得发"判断字段

---

## 晨星需要做的

1. **填写 MEDIA-CONSTITUTION.md**：账号定位、目标受众、风格约束、平台优先级
2. **确认 cron 时间**：07:30/08:00/12:30/18:00/21:30 是否合适
3. **确认平台优先级**：小红书 > 知乎 > 抖音？还是其他顺序？
4. **确认 MVP 范围**：先只做 Phase 1，还是 Phase 1+2 一起？

---

_文档版本: v1.0_
_创建时间: 2026-03-18_
_状态: 待晨星确认后开始执行_
