# Layer 3 后续优化路线图（本地版 / 上游版双轨）

**创建时间**: 2026-03-17
**适用周期**: 2026-03-18 ~ 2026-03-24（1 周）
**背景**:
- 本地 Layer 3 fallback 已从“反复失败”收口到“可用 + 观察期”
- PR #206 已被关闭，说明上游不接受“大一统改造 + 改 response contract”的并入方式
- PR #227 属于独立小修线，继续按“小而兼容”的方式推进

---

## 一句话总目标

- **本地版目标**：把 Layer 3 从“现在能跑”推进到“触发可控、收益可量化、输出可兼容”。
- **上游版目标**：停止推进大而全 PR，改成“兼容优先、行为收敛、拆小 PR”的渐进路线。

---

## 这 1 周不做什么

### 本地版不做
- 不再大改 live runtime 插件加载路径
- 不把 PR worktree 指回 runtime 路径
- 不再把关键词单独触发直接视为合理默认行为
- 不在没有 benchmark 证据时继续叠加复杂机制

### 上游版不做
- 不再尝试复活 PR #206 这种大一统 PR
- 不修改现有 `memory_recall` 的默认 response contract
- 不把本地 NotebookLM / nlm-gateway 的私有运行假设直接当成上游默认前提
- 不把 Layer 3 作为关键词驱动的默认增强路径推进到 master

---

# Track A — 本地版（03-18 ~ 03-24）

## North Star
把本地 Layer 3 收敛成一个**严格 fallback、可观察、可解释收益**的能力，而不是模糊的“有时增强一下”。

## 成功标准（本地）
1. 能明确回答：**为什么触发了 L3**
2. 能明确回答：**L3 这次是否真的比 L2 多提供了有效信息**
3. 能明确回答：**哪些查询值得进 L3，哪些不值得**
4. 输出形态不再对已有调用方造成潜在兼容风险

---

## Day 1 — 03-18：补齐可观测性

### 任务清单
- [ ] 给 Layer 3 fallback 补“触发理由”分类
  - `low_results`
  - `low_top1_score`
  - `low_avg_score`
  - `keyword_hint_only`
  - `manual_deep_query`
- [ ] 给每次 L3 调用补“结果状态”分类
  - `success_with_new_info`
  - `success_but_duplicate`
  - `timeout`
  - `empty`
  - `parse_error`
  - `upstream_tool_error`
- [ ] 给每次 L3 调用补“耗时”与“是否新增有效信息”标记
- [ ] 确认 Day 4 cron 跑完后，scorecard 能体现：触发率 / 成功率 / 有效补充率

### 输出物
- 观测字段清单（可以先写到 report/注释，不一定当天就上游化）
- Day 4 scorecard + observation 更新

### 判定标准
- 之后看到一次 L3 触发，不能只知道“触发了”，必须知道**为什么触发、花了多久、值不值**

---

## Day 2 — 03-19：收紧触发门（Strict Fallback v1）

### 任务清单
- [ ] 明确本地 L3 触发门改成“两级门”

#### 一级门（主门）
只有满足以下之一才允许进入 L3：
- `results.length === 0`
- `results.length < minResults`
- `top1Score < minScore`
- `avgTop3Score < minAvgScore`

#### 二级门（辅门）
一级门成立后，再参考：
- 时间相关关键词
- 解释 / 原因 / 总结 / 详细 等深度查询信号
- 手动强制深查意图

- [ ] 取消“关键词单独就能触发 L3”的默认逻辑
- [ ] 给当前阈值做一版显式记录（先写成文档/注释，避免口头配置漂移）

### 输出物
- `Strict Fallback v1` 规则说明
- Day 5 验证结果

### 判定标准
- Layer 3 不能再是“像增强版默认链路”，而必须是“低置信度时才介入”

---

## Day 3 — 03-20：定义“L3 是否有价值”

### 任务清单
- [ ] 为 L3 增加“added value”判断标准
- [ ] 将 L3 结果分成三类：
  - **A 类**：补到了 L2 没给出的关键信息
  - **B 类**：只是重述 / 换表达
  - **C 类**：无效 / 空 / 误导
- [ ] 形成最小判断规则：如果结果属于 B/C，后续可以不展示 L3 块或标为“无新增信息”
- [ ] 用 Day 6 的当日验证统计 A/B/C 分布

### 输出物
- Added Value Rubric（轻量版）
- Day 6 scorecard + observation 更新

### 判定标准
- 以后说“L3 有帮助”，必须能落到 A/B/C 统计，而不是凭感觉

---

## Day 4 — 03-21：完成 4E 收口 + 阶段判断

### 任务清单
- [ ] 跑完 Day 7 benchmark
- [ ] 输出 4E 七天阶段结论
- [ ] 回答四个问题：
  1. L2 是否已经足够承担主链路？
  2. L3 的真实有效补充率是多少？
  3. 哪一类查询最值得进 L3？
  4. 现有 timeout=75 是否足够？
- [ ] 基于 4E 数据，先做阶段判断：
  - 保持当前 timeout
  - 是否要继续收紧 trigger
  - 是否需要 notebook 自动刷新机制

### 输出物
- 4E 阶段总结
- 对 4F.5 / 4F.6 的预判输入

### 判定标准
- 4E 结束后，不能还停留在“再观察看看”；必须得出至少一版阶段结论

---

## Day 5 — 03-22：把兼容性问题彻底切清

### 任务清单
- [ ] 明确本地输出模式：
  - **默认**：人类友好、可看 L2/L3 分层
  - **兼容**：保留旧式首行 / 旧式 contract 兼容头
- [ ] 决定是否采用“双层输出”策略：
  - 第一层：兼容旧调用方的简洁主结果
  - 第二层：可选 L3 appendix / diagnostics
- [ ] 明确：本地 richer output 可以保留，但不要再和“上游默认输出”绑定

### 输出物
- 本地输出策略说明（legacy-compatible / layered-readable）

### 判定标准
- 本地体验优化和上游兼容风险要彻底解耦

---

## Day 6 — 03-23：评估是否值得做预计算 / 缓存

### 任务清单
- [ ] 用前几天数据看 L3 高频触发问题是否集中在少数 query 类别
- [ ] 如果触发集中，评估方案 C（异步投递 / 预计算缓存）是否值得进入下一阶段
- [ ] 如果触发分布分散，则维持 on-demand，不额外上缓存复杂度

### 决策门槛（建议）
- 若 L3 高频触发 > 20% 且查询模式稳定 → 进入缓存可行性评估
- 若 L3 真正有效补充率 < 15% → 不做缓存，继续收紧 trigger
- 若 median L3 latency > 25s 且 added value 不高 → 继续把 L3 保持在稀疏 fallback

### 输出物
- 方案 C go / no-go 初判

---

## Day 7 — 03-24：冻结本地 v1 策略

### 任务清单
- [ ] 形成 `Local Layer 3 Policy v1`
- [ ] 固定这四件事：
  1. trigger gate
  2. timeout
  3. output mode
  4. added-value判定
- [ ] 明确下一周如果继续做，只做：
  - 阈值微调
  - 缓存评估
  - 观测字段补强
  - 不再重写主链路

### 输出物
- 本地 v1 政策定稿

### 判定标准
- 到 03-24，本地版应该从“实验期”进入“有边界的可维护状态”

---

# Track B — 上游版（03-18 ~ 03-24）

## North Star
把上游推进方式从“大功能导向”改成“兼容性导向 + 小 PR 序列化”。

## 成功标准（上游）
1. 不再碰 `memory_recall` 默认 contract
2. 所有提案都能一句话说清：**这不会破坏现有调用方**
3. Layer 3 如果继续推进，也只能以**受控、稀疏、可选**的方式推进

---

## Day 1 — 03-18：正式放弃大一统并入思路

### 任务清单
- [ ] 把 PR #206 视为“路线校正证据”，不再尝试救这条 PR
- [ ] 整理 maintainer / reviewer 的约束清单：
  - 不改 response contract
  - L3 必须是 strict fallback
  - CLI runner 需要 hardened path
- [ ] 写成一句上游原则：
  - **compat first, fallback strict, rollout small**

### 输出物
- 上游约束摘要（内部说明即可）

---

## Day 2 — 03-19：继续只推进 PR #227 这条小修线

### 任务清单
- [ ] 继续盯 PR #227 reviewer 回复
- [ ] 如果 reviewer 再提意见，只做最小修正，不捎带其它 Layer 3 内容
- [ ] 目标是把“runtime agent id 默认回 main”这条线独立合掉

### 输出物
- PR #227 的状态推进（不是新方向设计）

---

## Day 3 — 03-20：准备 PR-A（CLI runner hardening）

### 任务清单
- [ ] 设计一个**纯基础设施、无行为变化**的 PR-A
- [ ] 范围只包括 reviewer 明确点过的 runner hardening：
  - `OPENCLAW_CLI_BIN` override
  - workspace-aware `cwd`
  - `NO_COLOR`
  - outer timeout/watchdog
- [ ] 不引入 Layer 3 触发逻辑变化
- [ ] 不改任何 response contract

### 输出物
- PR-A scope 草案

### 判定标准
- maintainer 一眼能看出：这是“稳定性修补”，不是“功能改道”

---

## Day 4 — 03-21：准备 PR-B（strict fallback 机制，但不改 contract）

### 任务清单
- [ ] 设计一个 contract-safe 的 PR-B
- [ ] 核心是：
  - L3 只能在低置信度时触发
  - 关键词不能单独触发
- [ ] 但注意：
  - 不改 `memory_recall` 默认输出格式
  - 最好 behind flag / internal helper / non-default path

### 输出物
- PR-B 设计草案（可发 issue / comment / 本地文档先行）

### 判定标准
- reviewer 再看时，不会第一眼担心“你又要改默认行为”

---

## Day 5 — 03-22：决定“新工具 vs 旧工具 behind flag”

### 任务清单
- [ ] 二选一做出倾向判断：

#### 方案 1：新工具
- `enhanced_memory_recall`
- `memory_recall_v2`
- `memory_recall_explain`

#### 方案 2：旧工具 behind flag
- 默认仍保持老 contract
- 开 flag 才进入 layered / enhanced 模式

- [ ] 评估哪条更容易被 maintainer 接受

### 我的当前倾向
- **上游更可能接受“新工具”或“behind flag”**，而不是重写旧工具默认行为

### 输出物
- 工具边界决策草案

---

## Day 6 — 03-23：准备证据包，但只拿可泛化证据

### 任务清单
- [ ] 整理可以给上游看的证据类型：
  - 为什么 strict fallback 是必要的
  - 为什么 runner hardening 是有价值的
  - 哪些 query 类别在低置信度下确实受益于深查
- [ ] 不把以下内容直接当上游默认前提：
  - 本地 Notebook ID
  - 本地 nlm-gateway 私有脚本细节
  - 本地 cron / worktree / runtime 特殊编排

### 输出物
- Upstream-safe evidence list

---

## Day 7 — 03-24：锁定上游未来两步

### 任务清单
- [ ] 锁定上游接下来只做两步：
  1. 合小 bugfix / hardening PR
  2. 再提 strict fallback / new tool 方案
- [ ] 明确不上游的内容：
  - richer output 默认化
  - 本地私有 gateway 路线绑定
  - 激进关键词触发

### 输出物
- 上游两步走计划

### 判定标准
- 上游路线必须变成“先小后大、先稳后强”

---

# 两条线的最终分工

## 本地版负责
- 真实效果最大化
- 快速验证 NotebookLM 深查价值
- 触发门和输出模式迭代
- timeout / 观测 / 缓存策略的工程优化

## 上游版负责
- 保兼容
- 保默认语义稳定
- 让公共仓库能逐步接受基础设施改进
- 避免把你的私有高配方案强塞给所有用户

---

# 这周结束时必须回答的 6 个问题

1. L3 的真实有效补充率到底是多少？
2. 哪些查询类型最值得进 L3？
3. 是否已经证明“关键词单独触发”应该被废弃？
4. 本地是否需要 legacy-compatible 输出层？
5. 上游更适合新工具，还是 behind flag？
6. 下一步优先做 runner hardening，还是 strict fallback 机制？

---

# 最终判断

> **本地版继续做强，但要收边界。**
> **上游版继续推进，但只能拆小步。**

如果这一周按这张路线图走完，Layer 3 这条线就会从“能跑的实验”变成：
- 本地：有规则、有指标、有决策门槛
- 上游：有节奏、有边界、有合并路径
