# Memory Retrieval Observation Log — 2026-03-14 起

**观察期目标**：连续 7 天跟踪记忆召回质量，记录：
- 主链路 `memory-lancedb-pro` 的命中率、歧义、重复度
- builtin memorySearch 的可评估状态
- 是否适合继续推进 hybrid / MMR / temporalDecay / sessionMemory

---

## Day 1 — 2026-03-14

### 执行内容
- 建立基线报告
- 建立 benchmark 查询集与评分口径
- 起草配置草案（未应用）
- 排查 builtin memorySearch 阻塞点
- 排查 `memory/archive/` 目录依赖范围

### 结果摘要
#### 主链路：memory-lancedb-pro
- 状态：正常
- `memory_stats`: 324 条
- `memory_recall`: 抽样命中良好
- 已知问题：个别术语有歧义（如 scripts）

#### 影子链路：builtin memorySearch
- 状态：当前不适合公平评估
- 现象：`openclaw memory search` 多次触发
  - `Ollama embeddings HTTP 500: the input length exceeds the context length`
- 高概率根因：`memory/archive/` 中超大归档文件仍在 builtin 默认索引范围内

### 今日判断
1. 暂不应用 builtin 增强配置
2. 暂不迁移 archive 目录
3. 先把 builtin memorySearch 视为**暂缓评估的影子线**
4. 主链路继续依赖 `memory-lancedb-pro`
5. 重新评估 builtin 前，必须先满足前置条件清单（见 `reports/builtin-memorysearch-prerequisites-20260314.md`）

### 明日关注点
- 如果继续观察，优先记录：
  - 主链路是否出现误召回 / 冲突召回
  - 是否还有新的超大文件进入 `memory/` 或 `memory/archive/`
  - builtin memorySearch 是否仍稳定报同一类错误

---

## 后续填写方式
- 每天先用：`reports/memory-retrieval-scorecard-template-20260314.md`
- 填完后，把当日摘要回写到本观察日志对应日期小节
- 这样主日志保持简洁，详细评分单独留档

## Day 2 — 2026-03-15
- 待记录（使用 scorecard template）

## Day 3 — 2026-03-16
- 待记录（使用 scorecard template）

## Day 4 — 2026-03-17
- 待记录（使用 scorecard template）

## Day 5 — 2026-03-18
- 待记录（使用 scorecard template）

## Day 6 — 2026-03-19
- 待记录（使用 scorecard template）

## Day 7 — 2026-03-20
- 待记录（使用 scorecard template）

---

## 观察期最终输出（到期填写）
- 是否继续评估 builtin memorySearch
- 是否需要 archive 架构迁移
- 是否正式应用 hybrid / MMR / temporalDecay / sessionMemory
- 是否需要启动 QMD 试点