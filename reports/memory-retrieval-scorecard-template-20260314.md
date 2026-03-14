# Memory Retrieval Daily Scorecard Template

**用途**：给 7 天观察期每日打分使用。  
**配套文件**：
- `reports/memory-retrieval-observation-20260314.md`
- `reports/memory-retrieval-benchmark-20260314.md`

---

## 每日填写说明

### 评分维度（单条满分 8）
- Hit（命中率）：0-2
- Rank（排名质量）：0-2
- Dup（重复度）：0-2
- Fresh（时效性）：0-2

### 每日汇总指标
- 主链路总分（15 条 × 8 = 120 分）
- builtin 总分（如果当天不可评估，直接写 N/A）
- builtin 错误类型
- 新增误召回 / 冲突召回
- 是否有新超大文件进入 `memory/` / `memory/archive/`

---

## Daily Scorecard Template

### 日期
- Date: YYYY-MM-DD
- 主链路：memory-lancedb-pro
- 影子链路：builtin memorySearch

### 每日摘要
| 项目 | 结果 |
|---|---|
| 主链路总分 |  |
| builtin 总分 |  |
| 主链路主要问题 |  |
| builtin 主要问题 |  |
| 是否出现误召回 |  |
| 是否出现冲突召回 |  |
| 是否出现新超大文件 |  |
| 是否继续观察 builtin |  |

### Query Scorecard
| # | 查询 | 期望 | 主链路 Hit | 主链路 Rank | 主链路 Dup | 主链路 Fresh | builtin Hit | builtin Rank | builtin Dup | builtin Fresh | 备注 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 晨星主要用什么渠道联系？ | Telegram / 1099011886 |  |  |  |  |  |  |  |  |  |
| 2 | 主私聊会话有什么约束？ | main 不承载长时间编排 |  |  |  |  |  |  |  |  |  |
| 3 | 同一问题三次未解决怎么办？ | 必须切换方向 |  |  |  |  |  |  |  |  |  |
| 4 | OpenClaw 有新版本时要做什么联动？ | 更新 openclaw-docs notebook |  |  |  |  |  |  |  |  |  |
| 5 | TODO 文件应该放在哪里？ | ~/.openclaw/todo/ |  |  |  |  |  |  |  |  |  |
| 6 | 系统级 scripts 应该放在哪里？ | ~/.openclaw/scripts/ |  |  |  |  |  |  |  |  |  |
| 7 | skill 自带脚本应该放在哪里？ | skill 自己的 scripts/ |  |  |  |  |  |  |  |  |  |
| 8 | monitor-bot 的 chat id 是多少？ | -5131273722 |  |  |  |  |  |  |  |  |  |
| 9 | 当前主记忆插件是什么？ | memory-lancedb-pro |  |  |  |  |  |  |  |  |  |
| 10 | beta.8 后出现了什么回归？ | memory_list / memory_stats 默认 0 |  |  |  |  |  |  |  |  |  |
| 11 | 什么时候必须完整 gateway restart？ | 插件源码修复后 |  |  |  |  |  |  |  |  |  |
| 12 | 记忆压缩检查的阈值是多少？ | 40k tokens |  |  |  |  |  |  |  |  |  |
| 13 | 刚才新建的记忆检索优化 TODO 文件叫什么？ | memory-retrieval-optimization-2026-03-14.md |  |  |  |  |  |  |  |  |  |
| 14 | builtin memorySearch 新阻塞点是什么？ | archive 超长文件导致 context-length error |  |  |  |  |  |  |  |  |  |
| 15 | 当前策略是什么？ | 先 benchmark / 不改配置 / 不切主插件 |  |  |  |  |  |  |  |  |  |

### 当日结论
- 主链路是否稳定：
- builtin 是否可评估：
- 是否需要调整 benchmark：
- 次日重点：
