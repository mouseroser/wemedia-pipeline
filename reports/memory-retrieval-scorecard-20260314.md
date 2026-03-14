# Memory Retrieval Scorecard — 2026-03-14 (Day 1)

## 每日摘要
| 项目 | 结果 |
|---|---|
| 主链路总分 | 11 / 12（已测 6 条中的 6 条） |
| builtin 总分 | 不计入正式评分 |
| 主链路主要问题 | `scripts` 查询存在术语歧义 |
| builtin 主要问题 | `memory/archive/` 超长文件导致 sync/search context-length error |
| 是否出现误召回 | 未见明显误召回 |
| 是否出现冲突召回 | 未见明显冲突召回 |
| 是否出现新超大文件 | 未新增，但已确认 archive 中已有超大文件 |
| 是否继续观察 builtin | 是，但仅作为影子线 |

## Day 1 Scorecard
| # | 查询 | 主链路 Hit | 主链路 Rank | 主链路 Dup | 主链路 Fresh | builtin 结果 | 备注 |
|---|---|---:|---:|---:|---:|---|---|
| 1 | 晨星主要用什么渠道联系？ | N/A | N/A | N/A | N/A | 未测 | 当日未跑 |
| 2 | 主私聊会话有什么约束？ | 2 | 2 | 2 | 2 | 未测 | 直接命中 |
| 3 | 同一问题三次未解决怎么办？ | 2 | 2 | 2 | 2 | 未测 | 直接命中 |
| 4 | OpenClaw 有新版本时要做什么联动？ | 2 | 2 | 2 | 2 | 未测 | 直接命中 |
| 5 | TODO 文件应该放在哪里？ | 2 | 2 | 1 | 2 | 失败 | builtin: No matches + sync failed |
| 6 | 系统级 scripts 应该放在哪里？ | 1 | 1 | 1 | 1 | 未测 | 同时召回系统级脚本与 skill 脚本规则，术语歧义 |
| 7 | skill 自带脚本应该放在哪里？ | N/A | N/A | N/A | N/A | 未测 | 当日未跑 |
| 8 | monitor-bot 的 chat id 是多少？ | N/A | N/A | N/A | N/A | 部分命中 | builtin 可命中 monitor-bot 旧日志，但伴随 sync failed |
| 9 | 当前主记忆插件是什么？ | N/A | N/A | N/A | N/A | 未测 | 当日未跑 |
| 10 | beta.8 后出现了什么回归？ | 2 | 2 | 2 | 2 | 未测 | 直接命中 |
| 11 | 什么时候必须完整 gateway restart？ | N/A | N/A | N/A | N/A | 未测 | 当日未跑 |
| 12 | 记忆压缩检查的阈值是多少？ | N/A | N/A | N/A | N/A | 未测 | 当日未跑 |
| 13 | 新建的记忆检索优化 TODO 文件叫什么？ | N/A | N/A | N/A | N/A | 未测 | 会话记忆专项，待后续 |
| 14 | builtin 新阻塞点是什么？ | N/A | N/A | N/A | N/A | 失败 | 已定位为 archive 超长文件导致 context-length error |
| 15 | 当前策略是什么？ | N/A | N/A | N/A | N/A | 未测 | 会话记忆专项，待后续 |

## Day 1 结论
1. 主链路 `memory-lancedb-pro` 在已测 6 条里整体表现稳定，只有 `scripts` 一项因术语歧义被拉低。
2. builtin memorySearch 当前不适合计入正式评分；其主要问题在索引范围冲突，而非纯排序质量。
3. Day 2 应优先补测未跑的主链路查询，并验证是否出现误召回/冲突召回。 
4. 如果 builtin 继续报同类错误，后续只保留“错误是否持续复现”的观察，不再浪费时间重复跑完整查询。 
