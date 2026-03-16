# Memory Retrieval Observation - 2026-03-14

## Day 1（2026-03-14）
- 详见 `memory-retrieval-scorecard-20260314.md`
- L2 平均分：2.3/5，部分查询有效
- 参考价值：Day 1 使用的是 nomic-embed-text 模型

## Day 2 前半段（2026-03-15，nomic-embed-text）

L2+L3 联动验证（精简 5 条 + benchmark 10 条），**L2 全部 0 分**。

### 根因分析（同日完成）
1. **nomic-embed-text 中文语义分辨力极差**：所有中文 pair cosine sim 在 0.65-0.82 之间，无分辨力。"记忆系统配置" vs "我对用户的称呼是晨星" (0.732) 比 vs "记忆系统技术栈正确配置" (0.582) 还高。
2. **BM25/FTS 中文分词失效**：LanceDB Tantivy 分词器不支持中文连续词拆分，"记忆系统配置" 搜索 0 条，"记忆 系统 配置" 才能命中。
3. **Rerank 正常**：bge-reranker-v2-m3 对中文工作良好（score 0.96），但候选池里没有正确内容。

### 修复：切换 bge-m3

同日执行 embedding 模型切换：
- nomic-embed-text (768维) → **bge-m3 (1024维)**
- 376 条记忆全量重新 embedding（耗时 42 秒）
- FTS 索引重建

## Day 2 后半段（2026-03-15，bge-m3 切换后）

| # | 查询 | L2 命中 | L2 质量 (0-5) | 首条内容 | 冲突 |
|---|---|---|---:|---|---|
| 1 | 我的核心偏好是什么 | ✅ 3条 | 5 | 记忆管理原则（精确匹配） | 否 |
| 2 | 今天的待办任务 | ✅ 3条 | 3 | TODO 提醒（相关） | 否 |
| 3 | 记忆系统配置 | ✅ 3条 | 5 | 技术栈正确配置（完美匹配） | 否 |
| 4 | 最近的踩坑记录 | ✅ 3条 | 4 | 踩坑记录偏好 | 否 |
| 5 | 星链流水线的状态 | ✅ 3条 | 5 | v2.7 升级（完美匹配） | 否 |
| 6 | 晨星主要用什么渠道联系 | ✅ 3条 | 5 | 用户信息+Telegram | 否 |
| 7 | 主私聊会话有什么约束 | ✅ 3条 | 5 | 核心规则-占线约束 | 否 |
| 8 | 我的核心偏好 | ✅ 3条 | 4 | 偏好记录 | 否 |

### 汇总
- L2 命中率：**8/8 = 100%** (之前 0%)
- L2 平均质量：**4.5/5** (之前 0.0/5)
- L3 触发：1/8（因为 L2 足够好，L3 不再需要）
- 冲突率：0%

### 结论
bge-m3 切换是质变性改善。L2 从完全不可用到 100% 命中。

---

## 后续填写方式
- 每天先用：`reports/memory-retrieval-scorecard-template-20260314.md`
- 填完后，把当日摘要回写到本观察日志对应日期小节
- Day 2 详细评分：`reports/memory-retrieval-scorecard-20260315.md`

## Day 3（2026-03-17，按 master-execution-plan 口径）
- 详见 `memory-retrieval-scorecard-20260317.md`
- L2 可用命中：**12/15 = 80%**
- L2 平均质量：**4.1/5**
- L3 触发：**5/15**，其中 **3 次显式失败**（NotebookLM session lock / gateway timeout），其余 2 次未形成有效补充
- 冲突率：**0%**
- 结论：长期规则与稳定事实召回已经够稳，但短期/会话型记忆（文件名、当前策略）仍弱；Layer 3 fallback 当前可用性受 notebooklm session lock 影响，需要单独排查

## Day 4 — 2026-03-18
- 待记录

## Day 5 — 2026-03-19
- 待记录

## Day 6 — 2026-03-20
- 待记录

## Day 7 — 2026-03-21
- 待记录

---

## 观察期最终输出（到期填写）
- 是否继续评估 builtin memorySearch
- 是否需要 archive 架构迁移
- 是否正式应用 hybrid / MMR / temporalDecay / sessionMemory
- 是否需要启动 QMD 试点
