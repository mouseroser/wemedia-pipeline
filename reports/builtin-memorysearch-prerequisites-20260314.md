# Re-evaluate builtin memorySearch — Prerequisites Checklist (2026-03-14)

## 目的
明确：**只有满足哪些前置条件后，才值得重新认真评估 OpenClaw builtin memorySearch。**

当前结论：**暂不满足。**

---

## A. 必须满足的前置条件

### A1. 先确认“还要不要继续评估 builtin”
在真正动目录或配置前，先确认 builtin memorySearch 是否仍值得投入：
- 如果只是跟进最新能力、做影子评估，可以继续保留观察
- 如果近期没有明确收益目标，则不值得为了它做架构迁移

### A2. builtin 索引范围必须恢复到“可正常搜索”状态
当前 builtin `openclaw memory search` 会稳定触发：
- `Ollama embeddings HTTP 500: the input length exceeds the context length`

**未解决这个问题前，任何 recall 评分都不可信。**

### A3. `memory/archive/` 冲突要先有明确策略
必须先在两种路径里选一条：
1. **保持现状**：builtin 暂缓评估，继续做影子线
2. **架构迁移**：把 archive 移出 `memory/`，并同步改文档/脚本/skill

> 不允许一边保留当前冲突，一边继续认真 benchmark builtin。

### A4. 只以 main 为评估对象
重新评估 builtin 时，先只看 `main`：
- 不给所有 agent 补 memory 目录
- 不把多 agent dirty/missing 状态混进主评估里

### A5. benchmark 查询集和评分口径固定
必须沿用已建的 benchmark：
- `reports/memory-retrieval-benchmark-20260314.md`

否则前后结果不可比。

### A6. 如果要测 session recall，必须真正启用 sessionMemory
当前 config 虽写了 `sources: ["memory", "sessions"]`，但实际 status 只看到 `memory`。

所以如果后续要认真评估“短期会话记忆”，必须：
- 开启 `experimental.sessionMemory = true`
- 重新检查 status 确认 sessions 真被纳入

### A7. 变更后必须重新 warm-up / reindex
如果后续应用配置或调整目录：
- 要重新检查 `openclaw memory status --deep`
- 必要时执行 reindex / warm-up
- 确认不再出现 context length 错误

---

## B. 重新评估的停止条件（Stop Conditions）

一旦出现以下任意情况，立即停止 builtin 正式评估，回到影子线状态：

1. `openclaw memory search` 仍出现：
   - context length error
   - sync failed
   - 大量 rate limit + 无有效结果
2. 开了 sessionMemory 后，status 仍不显示 `sessions`
3. benchmark 结果比 `memory-lancedb-pro` 明显更差，且没有补偿收益
4. 为了 builtin 需要做的架构改动明显超过收益

---

## C. 达标标准（Go / No-Go）

### Go（可以继续推进 builtin）
必须同时满足：
- 搜索稳定，无 context length 错误
- benchmark 至少能稳定跑完
- 主观和客观评分都不明显差于现有主链路
- 改动成本可控

### No-Go（继续保持影子线）
满足任一项即可：
- 仍依赖大规模目录迁移
- 仍需要为 builtin 单独兜很多异常
- benchmark 收益不明显
- 继续维护会带来额外噪音

---

## D. 当前建议
**当前建议：No-Go（暂缓 builtin 正式评估）**

原因：
1. 主链路 `memory-lancedb-pro` 已正常
2. builtin 仍被 archive 冲突拖住
3. archive 迁移是架构动作，不是低风险小修
4. 当前收益还不足以支撑这个迁移成本

---

## 一句话结论
> 只有在 builtin memorySearch 先脱离 `memory/archive/` 冲突、能稳定完成搜索、且 sessionMemory 真正启用后，才值得重新进入正式 benchmark 阶段。