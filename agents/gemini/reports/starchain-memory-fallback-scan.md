# Memory Layer 3 (NotebookLM) 降级集成扫描报告

## 1. 源码探索
目标插件：`memory-lancedb-pro`

核心拦截点位于 `src/tools.ts` 中 `registerMemoryRecallTool` 的 `execute` 方法内。
召回逻辑现已支持基于评分和搜索词特征的后置评估。
核心类：
- `analyzeLayer3FallbackNeed`: 用于评估是否需要触发Layer 3。
- `runNotebookLMFallbackQuery`: 负责执行具体的 NotebookLM 调用并获取结果。

在插件的 `index.ts` 中，`layer3Fallback` 配置项已经被正确地从 `openclaw.plugin.json` 读取并传递。

## 2. 集成分析
目前 `src/tools.ts` 中通过使用 `child_process.spawn` 直接调用 OpenClaw 的 CLI 实现了与 NotebookLM Agent 的交互：
```typescript
const command = [
  "agent",
  "--agent", resolved.agent,
  "--json",
  "--timeout", String(resolved.timeout),
  "--message", task,
];
const child = spawn("openclaw", command, { stdio: ["ignore", "pipe", "pipe"] });
```
这是个有效的方案，它绕过了插件沙箱限制，直接利用系统安装的 `openclaw` CLI 调用目标 Agent (`notebooklm`)，将查询发送至对应的 Notebook。它同时正确解析了标准输出并处理了错误和超时。

另一种替代方案是通过 `api` 直接调用 `sessions_spawn`，但直接 spawn process 提供了一致的 JSON 解析。

## 3. 降级策略
分析表明，`src/tools.ts` 中已实现了 `analyzeLayer3FallbackNeed`，其触发条件如下（均可由配置注入）：
- **时间敏感词 (`timeKeywords`)**: 如 "今天", "昨天", "最近", "本周"
- **推理敏感词 (`reasoningKeywords`)**: 如 "为什么", "如何", "对比"
- **显式深度要求词 (`explicitKeywords`)**: 如 "详细", "完整", "历史"
- **召回结果数 (`minResults`)**: 如果 Layer 2 召回结果数低于阈值（如默认 3 条）
- **最高分阈值 (`minScore`)**: 如果 Layer 2 召回的 top1 score 低于阈值（如 0.5）
- **前三平均分 (`minAvgScore`)**: 如果 Layer 2 top3 的平均得分低于阈值（如 0.4）

这些条件完全满足背景中提到的策略：基于时间敏感查询或深度推理进行触发，以及在 Layer 2 表现差时触发。

## 4. 风险评估
目前检测到以下风险和潜在阻塞点：
- **CLI 依赖风险**: 插件使用 `spawn("openclaw")`，依赖于 host 环境中 `openclaw` 在系统 `PATH` 内可用，如果部署在沙盒化环境可能失败。
- **异步超时风险**: NotebookLM 查询速度较慢（60-90s）。`openclaw` spawn 进程支持通过 `--timeout` 设置超时。但是，主调 Agent（调用 memory_recall 的 Agent）可能因为 `memory_recall` Tool 的调用时间过长而发生超时（通常 Tool execution limit 可能在 60s 内）。如果 `runNotebookLMFallbackQuery` 需要 90 秒，可能会阻塞或导致主流程直接崩溃。
- **并发 / 速率限制**: NotebookLM 并没有为高频并发设计，频繁 fallback 可能会 hit rate limits。
- **JSON 解析脆弱性**: CLI 调用的 JSON 解析依赖于输出格式：`try { const raw = JSON.parse(trimmed); ... }`，若 CLI 返回了带有多余控制字符或提示前缀的信息，解析可能失败。

**建议**: 如果 `memory_recall` 在某些通道中因超时而抛错，可考虑将 Layer 3 Recall 的逻辑转变为**异步投递模式**（返回“已派发查询”并在查询结束时以 Message 返回），或者增加 `memory_recall_deep` 工具给 Agent 主动调用。
