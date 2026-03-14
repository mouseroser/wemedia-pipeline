# 星链打磨层 - Step 1.5D：实施计划

> **任务**：基于宪法约束，制定 `memory-lancedb-pro` Layer 3 降级集成的详细实施计划  
> **作者**：Claude Subagent  
> **日期**：2026-03-14  
> **输出**：`~/.openclaw/workspace/agents/claude/reports/starchain-memory-fallback-plan.md`

---

## 执行摘要

本计划将 Layer 3 (NotebookLM) 降级集成拆解为 **4 个独立交付阶段**，每个阶段都可独立验收、独立回滚。遵循宪法约束：**主链稳定性优先、失败边界前置、可观测性内置、最小改动原则**。

**预计时间线**：
- Phase 1（稳定性补丁）：1-2 周
- Phase 2（监控增强）：1 周
- Phase 3（触发优化）：1-2 周
- Phase 4（架构演进）：延后至 v2

---

## Phase 1：稳定性补丁（P0 - 必须完成）

### 目标
确保 Layer 3 失败不会拖垮主链，建立可控的失败边界。

### 技术方案

#### 1.1 收紧超时时间

**文件**：`memory-lancedb-pro/src/tools.ts`

**修改位置**：第 60-70 行（`DEFAULT_LAYER3_FALLBACK` 常量）

**修改内容**：
```typescript
const DEFAULT_LAYER3_FALLBACK: Required<Layer3FallbackSettings> = {
  enabled: false,
  agent: "notebooklm",
  notebook: "",
  notebookId: "",
  timeout: 60,  // 从 90 降至 60，确保在主 Agent 超时前失败
  triggers: {
    timeKeywords: ["今天", "昨天", "最近", "本周", "上周", "这个月"],
    reasoningKeywords: ["为什么", "如何", "怎么", "对比", "区别"],
    explicitKeywords: ["详细", "完整", "历史", "所有"],
    minResults: 3,
    minScore: 0.5,
    minAvgScore: 0.4
  }
};
```

**理由**：
- 主 Agent 的 Tool execution limit 通常为 60s
- Layer 3 timeout 必须 < 主 Agent timeout，确保失败边界可控
- 60s 仍足够 NotebookLM 返回结果（P50 约 45-60s）

---

#### 1.2 添加重试机制

**文件**：`memory-lancedb-pro/src/tools.ts`

**新增函数**（插入到第 220 行之前）：

```typescript
/**
 * 带重试的 NotebookLM 查询（仅针对 429 / rate limit）
 */
async function runNotebookLMFallbackQueryWithRetry(
  query: string,
  config?: Layer3FallbackSettings,
  maxRetries: number = 2
): Promise<{
  ok: boolean;
  text?: string;
  error?: string;
  command?: string[];
  raw?: any;
  attempts?: number;
}> {
  const resolved = resolveLayer3FallbackSettings(config);
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    const result = await runNotebookLMFallbackQuery(query, config);
    
    // 成功直接返回
    if (result.ok) {
      return { ...result, attempts: attempt };
    }
    
    // 非 429 错误不重试
    const isRateLimit = result.error && (
      result.error.includes("429") ||
      result.error.includes("rate limit") ||
      result.error.includes("too many requests")
    );
    
    if (!isRateLimit) {
      return { ...result, attempts: attempt };
    }
    
    // 429: 指数退避重试
    if (attempt < maxRetries) {
      const delayMs = Math.pow(2, attempt) * 1000; // 2s, 4s
      console.log(`[Layer3] Rate limited (attempt ${attempt}/${maxRetries}), retrying in ${delayMs}ms...`);
      await new Promise(resolve => setTimeout(resolve, delayMs));
    }
  }
  
  return {
    ok: false,
    error: `Max retries (${maxRetries}) exceeded due to rate limiting`,
    command: [],
    attempts: maxRetries
  };
}
```

**修改调用点**（第 410 行附近）：

```typescript
// 原代码：
// layer3Result = await runNotebookLMFallbackQuery(query, runtimeContext.layer3Fallback);

// 新代码：
layer3Result = await runNotebookLMFallbackQueryWithRetry(
  query,
  runtimeContext.layer3Fallback,
  2  // 最多重试 2 次
);
```

**理由**：
- NotebookLM API 可能因并发限制返回 429
- 指数退避避免雪崩效应
- 仅重试 rate limit 错误，其他错误快速失败

---

#### 1.3 增强错误降级逻辑

**文件**：`memory-lancedb-pro/src/tools.ts`

**修改位置**：第 418-422 行

**原代码**：
```typescript
if (layer3Result?.ok) {
  parts.push(`Layer 3 (NotebookLM):\n\n${layer3Result.text}`);
} else if (layer3Decision.shouldFallback && layer3Result && !layer3Result.ok) {
  parts.push(`Layer 3 (NotebookLM) failed, returning Layer 2 only.\n\nReason: ${layer3Result.error}`);
}
```

**新代码**：
```typescript
if (layer3Result?.ok) {
  parts.push(`Layer 3 (NotebookLM):\n\n${layer3Result.text}`);
} else if (layer3Decision.shouldFallback && layer3Result && !layer3Result.ok) {
  // 降级兜底：只在 details 中记录失败，不在主输出中暴露
  // 用户看到的是正常的 Layer 2 结果，不会感知到 Layer 3 失败
  console.warn(`[Layer3] Fallback failed, returning Layer 2 only. Error: ${layer3Result.error}`);
  // 不在主输出中添加失败信息，保持用户体验一致
}
```

**理由**：
- Layer 3 是增强能力，失败不应干扰用户体验
- 错误信息记录在 details 和日志中，便于调试
- 用户看到的始终是有效的 Layer 2 结果

---

### 验收标准

#### 测试用例 1：超时场景
```bash
# 模拟 NotebookLM 超时
# 方法：临时修改 timeout 为 1s
openclaw agent --agent main --message "测试：最近三天的工作记录"
```

**预期结果**：
- Tool 在 1s 后返回 Layer 2 结果
- 不触发主 Agent 超时
- details 中记录 `layer3Timeout: true`

#### 测试用例 2：429 重试
```bash
# 模拟 rate limit（需要手动触发或 mock）
# 连续发送 5 次查询
for i in {1..5}; do
  openclaw agent --agent main --message "测试查询 $i"
done
```

**预期结果**：
- 前 2-3 次成功
- 后续触发 429 后自动重试
- 最终返回结果或降级到 Layer 2

#### 测试用例 3：NotebookLM 不可用
```bash
# 临时禁用 notebooklm agent 或修改 agent 名称为不存在的值
openclaw agent --agent main --message "测试：详细说明最近的优化"
```

**预期结果**：
- 返回 Layer 2 结果
- 不崩溃
- details 中记录 `layer3Error: "agent not found"`

---

### 回滚方案

#### 回滚步骤
1. 恢复 `tools.ts` 到修改前版本：
   ```bash
   cd ~/.openclaw/workspace/plugins/memory-lancedb-pro
   git checkout HEAD~1 src/tools.ts
   ```

2. 重新构建插件：
   ```bash
   npm run build
   ```

3. 重启 OpenClaw：
   ```bash
   openclaw gateway restart
   ```

#### 回滚触发条件
- Layer 2 召回成功率下降 > 5%
- 主 Agent 超时率上升 > 10%
- 用户报告查询响应变慢

#### 回滚验证
```bash
# 验证 Layer 3 已禁用
openclaw agent --agent main --message "测试：今天的工作"
# 检查 details 中无 layer3Decision 字段
```

---

## Phase 2：监控增强（P1 - 高优先级）

### 目标
建立完整的可观测性，量化 Layer 3 的触发率、成功率、失败原因。

### 技术方案

#### 2.1 添加监控字段

**文件**：`memory-lancedb-pro/src/tools.ts`

**修改位置**：第 430-450 行（details 构建部分）

**新增字段**：
```typescript
details: {
  // ... 现有字段
  layer3Monitoring: layer3Decision.shouldFallback ? {
    triggered: true,
    triggerReasons: layer3Decision.reasons,
    triggerMetrics: layer3Decision.metrics,
    startTimestamp: layer3StartTime,
    endTimestamp: Date.now(),
    durationMs: Date.now() - layer3StartTime,
    success: layer3Result?.ok || false,
    attempts: layer3Result?.attempts || 0,
    error: layer3Result?.ok ? null : layer3Result?.error,
    config: {
      agent: runtimeContext.layer3Fallback?.agent,
      notebook: runtimeContext.layer3Fallback?.notebook,
      timeout: runtimeContext.layer3Fallback?.timeout
    }
  } : {
    triggered: false,
    skipReasons: [
      results.length >= (runtimeContext.layer3Fallback?.triggers?.minResults || 3) ? "sufficient_results" : null,
      // ... 其他跳过原因
    ].filter(Boolean)
  }
}
```

**新增变量**（在 execute 方法开头）：
```typescript
const layer3StartTime = Date.now();
```

---

#### 2.2 添加统计日志

**文件**：`memory-lancedb-pro/src/tools.ts`

**新增函数**（插入到文件末尾）：

```typescript
/**
 * 记录 Layer 3 统计信息（可选：写入文件或发送到监控系统）
 */
function logLayer3Stats(stats: {
  triggered: boolean;
  success?: boolean;
  durationMs?: number;
  error?: string;
  reasons?: string[];
}) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    ...stats
  };
  
  // 方案 1：控制台日志（最简单）
  console.log(`[Layer3Stats] ${JSON.stringify(logEntry)}`);
  
  // 方案 2：写入文件（可选）
  // const logPath = path.join(process.cwd(), "logs", "layer3-stats.jsonl");
  // fs.appendFileSync(logPath, JSON.stringify(logEntry) + "\n");
}
```

**调用点**（在 execute 方法返回前）：
```typescript
// 记录统计
logLayer3Stats({
  triggered: layer3Decision.shouldFallback,
  success: layer3Result?.ok,
  durationMs: layer3Result ? Date.now() - layer3StartTime : undefined,
  error: layer3Result?.ok ? undefined : layer3Result?.error,
  reasons: layer3Decision.reasons
});

return {
  content: [{ type: "text", text: parts.join("\n\n---\n\n") }],
  details: { /* ... */ }
};
```

---

### 验收标准

#### 测试用例 1：监控字段完整性
```bash
openclaw agent --agent main --json --message "测试：最近的工作详细记录"
```

**预期输出**（JSON）：
```json
{
  "details": {
    "layer3Monitoring": {
      "triggered": true,
      "triggerReasons": ["time_keyword", "explicit_keyword"],
      "triggerMetrics": {
        "resultCount": 2,
        "top1Score": 0.45,
        "avgTop3Score": 0.38
      },
      "durationMs": 58234,
      "success": true,
      "attempts": 1,
      "config": {
        "agent": "notebooklm",
        "notebook": "memory-archive",
        "timeout": 60
      }
    }
  }
}
```

#### 测试用例 2：统计日志可查询
```bash
# 执行 10 次查询
for i in {1..10}; do
  openclaw agent --agent main --message "测试查询 $i: 最近的工作"
done

# 查看统计
grep "Layer3Stats" ~/.openclaw/logs/*.log | jq -s '
  {
    total: length,
    triggered: map(select(.triggered == true)) | length,
    success: map(select(.success == true)) | length,
    avgDuration: (map(.durationMs // 0) | add / length)
  }
'
```

**预期输出**：
```json
{
  "total": 10,
  "triggered": 6,
  "success": 5,
  "avgDuration": 52341
}
```

---

### 回滚方案

#### 回滚步骤
1. 移除监控字段（不影响功能）：
   ```bash
   git revert <commit-hash>
   npm run build
   ```

2. 如果日志文件过大，清理：
   ```bash
   rm ~/.openclaw/logs/layer3-stats.jsonl
   ```

#### 回滚触发条件
- 监控字段导致 details 体积过大（> 10KB）
- 日志写入影响性能（QPS 下降 > 5%）

---

## Phase 3：触发优化（P2 - 中优先级）

### 目标
基于 Phase 2 的监控数据，优化触发策略，降低误触发率和资源浪费。

### 技术方案

#### 3.1 数据驱动的阈值调整

**前置条件**：Phase 2 已运行至少 1 周，收集到足够数据

**分析步骤**：
```bash
# 1. 提取统计数据
grep "Layer3Stats" ~/.openclaw/logs/*.log > layer3-stats.jsonl

# 2. 分析触发原因分布
jq -s 'map(select(.triggered == true)) | group_by(.reasons[0]) | map({reason: .[0].reasons[0], count: length})' layer3-stats.jsonl

# 3. 分析成功率 vs 触发原因
jq -s 'map(select(.triggered == true)) | group_by(.reasons[0]) | map({reason: .[0].reasons[0], successRate: (map(select(.success == true)) | length) / length})' layer3-stats.jsonl
```

**调整决策矩阵**：

| 触发原因 | 当前阈值 | 成功率 | 调整建议 |
|---------|---------|-------|---------|
| time_keyword | N/A | > 80% | 保持 |
| reasoning_keyword | N/A | 50-80% | 增加关键词精度 |
| explicit_keyword | N/A | > 90% | 保持 |
| minResults < 3 | 3 | < 50% | 提高到 2 |
| minScore < 0.5 | 0.5 | 60-80% | 降低到 0.4 |
| minAvgScore < 0.4 | 0.4 | 50-70% | 保持 |

**配置更新**（`openclaw.plugin.json`）：
```json
{
  "layer3Fallback": {
    "triggers": {
      "timeKeywords": ["今天", "昨天", "最近", "本周"],
      "reasoningKeywords": ["为什么", "如何"],  // 移除"怎么"（误触高）
      "minResults": 2,  // 从 3 降至 2
      "minScore": 0.4,  // 从 0.5 降至 0.4
      "minAvgScore": 0.4
    }
  }
}
```

---

#### 3.2 添加触发频率限制（可选）

**目的**：防止短时间内频繁触发 Layer 3

**文件**：`memory-lancedb-pro/src/tools.ts`

**新增状态管理**（文件顶部）：
```typescript
// 简单的内存限流器
const layer3RateLimiter = {
  lastTriggerTime: 0,
  minIntervalMs: 30000,  // 30 秒内最多触发一次
  
  canTrigger(): boolean {
    const now = Date.now();
    if (now - this.lastTriggerTime < this.minIntervalMs) {
      return false;
    }
    this.lastTriggerTime = now;
    return true;
  }
};
```

**修改触发逻辑**（第 408 行附近）：
```typescript
if (layer3Decision.shouldFallback && layer3RateLimiter.canTrigger()) {
  layer3Result = await runNotebookLMFallbackQueryWithRetry(
    query,
    runtimeContext.layer3Fallback,
    2
  );
} else if (layer3Decision.shouldFallback && !layer3RateLimiter.canTrigger()) {
  console.log("[Layer3] Rate limiter blocked trigger (too frequent)");
  layer3Decision.reasons.push("rate_limited");
}
```

---

### 验收标准

#### 测试用例 1：阈值调整生效
```bash
# 使用调整后的配置
openclaw agent --agent main --message "测试：对比最近两周的工作"
```

**预期结果**：
- 触发 Layer 3（reasoning_keyword 仍有效）
- details 中记录新的触发阈值

#### 测试用例 2：频率限制生效
```bash
# 连续发送 3 次查询（间隔 < 30s）
openclaw agent --agent main --message "测试1：今天的工作"
sleep 5
openclaw agent --agent main --message "测试2：今天的工作"
sleep 5
openclaw agent --agent main --message "测试3：今天的工作"
```

**预期结果**：
- 第 1 次触发 Layer 3
- 第 2、3 次被限流，不触发 Layer 3
- details 中记录 `rate_limited`

---

### 回滚方案

#### 回滚步骤
1. 恢复配置文件：
   ```bash
   git checkout HEAD~1 openclaw.plugin.json
   ```

2. 移除限流器代码（如果影响功能）：
   ```bash
   git revert <commit-hash>
   npm run build
   ```

#### 回滚触发条件
- 触发率下降 > 50%（过度限制）
- 用户反馈深度查询不可用

---

## Phase 4：架构演进（延后至 v2）

### 目标
解决超时阻塞的根本问题，实现异步投递模式。

### 技术方案（概要）

#### 4.1 异步投递架构

**核心思路**：
1. `memory_recall` 立即返回 Layer 2 结果
2. Layer 3 查询在后台异步执行
3. 结果通过 Telegram DM 推送给用户

**组件设计**：
```
┌─────────────────────────────────────────────────────────────────┐
│                     异步投递架构 v2                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    立即返回    ┌─────────────┐                │
│  │ memory_     │ ─────────────→│  主 Agent   │                │
│  │ recall      │   Layer 2      │             │                │
│  └──────┬──────┘                └─────────────┘                │
│         │                                                       │
│         │ 派发任务                                              │
│         ↓                                                       │
│  ┌─────────────┐    存储    ┌─────────────┐                    │
│  │ Task Queue  │ ─────────→│   Redis     │                    │
│  │ (内存/Redis)│           │   /SQLite   │                    │
│  └──────┬──────┘           └─────────────┘                    │
│         │                                                       │
│         │ 异步消费                                              │
│         ↓                                                       │
│  ┌─────────────┐    调用    ┌─────────────┐                    │
│  │  Worker     │ ─────────→│ NotebookLM  │                    │
│  │ (Background)│           │   Agent     │                    │
│  └──────┬──────┘           └─────────────┘                    │
│         │                                                       │
│         │ 推送结果                                              │
│         ↓                                                       │
│  ┌─────────────┐                                               │
│  │  Telegram   │                                               │
│  │     DM      │                                               │
│  └─────────────┘                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**实现要点**：
1. 使用 Redis 或 SQLite 作为任务队列
2. Worker 进程独立运行（cron 或常驻进程）
3. 推送使用 `message` API

**预计工作量**：2-4 周

---

#### 4.2 分离 `memory_recall_deep` Tool

**目的**：让 Agent 主动选择深度查询

**Tool 定义**：
```typescript
{
  name: "memory_recall_deep",
  description: "显式调用 NotebookLM 进行深度查询（不通过自动降级）",
  parameters: {
    query: "深度查询内容",
    notebook: "Notebook 名称（可选）",
    timeout: "超时秒数（可选）"
  }
}
```

**使用场景**：
- Agent 判断需要深度查询时主动调用
- 用户显式要求"详细查询"时

**预计工作量**：1 周

---

### 验收标准（v2）

#### 测试用例 1：异步投递
```bash
openclaw agent --agent main --message "测试：最近三天的详细工作记录"
```

**预期结果**：
- 立即返回 Layer 2 结果（< 1s）
- 5-10 秒后收到 Telegram DM："🧠 深度查询结果：..."
- 不阻塞主流程

#### 测试用例 2：主动深度查询
```bash
openclaw agent --agent main --message "使用 memory_recall_deep 查询最近的优化工作"
```

**预期结果**：
- Agent 调用 `memory_recall_deep` Tool
- 返回 NotebookLM 深度结果
- 不触发自动降级

---

### 回滚方案（v2）

#### 回滚步骤
1. 禁用异步投递：
   ```json
   {
     "layer3Fallback": {
       "asyncMode": false
     }
   }
   ```

2. 回退到 v1 同步模式：
   ```bash
   git checkout v1.x
   npm run build
   ```

#### 回滚触发条件
- 异步推送失败率 > 20%
- 用户反馈体验变差（收不到结果）
- 任务队列积压严重

---

## 风险缓解措施

### 风险 1：超时阻塞主流程（P0）

**缓解措施**：
- ✅ Phase 1：收紧 timeout 到 60s
- ✅ Phase 1：增强错误降级
- 🔄 Phase 4：异步投递（根本解决）

**监控指标**：
- 主 Agent 超时率（目标：< 1%）
- Layer 3 超时率（目标：< 10%）

---

### 风险 2：NotebookLM 429 / Rate Limit（P1）

**缓解措施**：
- ✅ Phase 1：添加重试 + 指数退避
- ✅ Phase 3：频率限制（30s 间隔）
- 🔄 Phase 4：任务队列 + 限流器

**监控指标**：
- 429 错误率（目标：< 5%）
- 重试成功率（目标：> 80%）

---

### 风险 3：CLI 依赖不可用（P1）

**缓解措施**：
- ✅ Phase 1：错误降级（CLI 失败返回 Layer 2）
- 🔄 Phase 4：切换到 SDK 直连（可选）

**监控指标**：
- CLI spawn 失败率（目标：< 1%）

---

### 风险 4：JSON 解析失败（P2）

**缓解措施**：
- ✅ 当前：降级兜底（返回原始文本）
- 🔄 Phase 3：增强解析鲁棒性（正则提取）

**监控指标**：
- 解析失败率（目标：< 2%）

---

### 风险 5：触发策略误触发（P2）

**缓解措施**：
- ✅ Phase 2：监控触发原因分布
- ✅ Phase 3：数据驱动的阈值调整
- ✅ Phase 3：频率限制

**监控指标**：
- 触发率（目标：10-20%）
- 触发后成功率（目标：> 70%）

---

## 交付清单

### Phase 1 交付物
- [ ] `tools.ts` 修改（超时 + 重试 + 降级）
- [ ] 单元测试（3 个测试用例）
- [ ] 回滚脚本
- [ ] 部署文档

### Phase 2 交付物
- [ ] 监控字段实现
- [ ] 统计日志实现
- [ ] 数据分析脚本
- [ ] 监控仪表板（可选）

### Phase 3 交付物
- [ ] 阈值调整配置
- [ ] 频率限制实现
- [ ] A/B 测试报告
- [ ] 优化建议文档

### Phase 4 交付物（v2）
- [ ] 异步投递架构设计
- [ ] Task Queue 实现
- [ ] Worker 进程实现
- [ ] `memory_recall_deep` Tool
- [ ] 迁移指南

---

## 总结

本计划遵循 **稳定性优先、渐进演进** 的原则，将 Layer 3 集成拆解为 4 个独立阶段：

1. **Phase 1（1-2 周）**：建立失败边界，确保主链不受影响
2. **Phase 2（1 周）**：建立可观测性，量化优化依据
3. **Phase 3（1-2 周）**：数据驱动优化，降低资源浪费
4. **Phase 4（延后）**：架构升级，根本解决超时问题

每个阶段都可独立验收、独立回滚，符合宪法约束的 **最小改动、可控风险** 原则。

---

**计划完成** ✅
