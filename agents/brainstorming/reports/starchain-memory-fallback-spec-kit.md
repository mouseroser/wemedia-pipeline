## Phase 1 完整代码

### 修改 1：调整超时阈值

**文件**：`src/tools.ts`  
**位置**：第 60-70 行（`DEFAULT_LAYER3_FALLBACK` 常量）

```typescript
const DEFAULT_LAYER3_FALLBACK: Required<Layer3FallbackSettings> = {
  enabled: false,
  agent: "notebooklm",
  notebook: "",
  notebookId: "",
  timeout: 45,  // 从 90 降至 45，确保在主 Agent 60s 超时前失败
  // timeout must stay well below the main agent 60s tool window
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

**配置校验**（如果存在 `resolveLayer3FallbackSettings` 函数）：
```typescript
function resolveLayer3FallbackSettings(config?: Layer3FallbackSettings): Required<Layer3FallbackSettings> {
  const resolved = {
    ...DEFAULT_LAYER3_FALLBACK,
    ...config,
    triggers: {
      ...DEFAULT_LAYER3_FALLBACK.triggers,
      ...config?.triggers
    }
  };
  
  // 强制上限 50s
  resolved.timeout = Math.min(resolved.timeout, 50);
  
  return resolved;
}
```

---

### 修改 2：时间感知的单次重试

**文件**：`src/tools.ts`  
**位置**：插入到第 220 行之前

```typescript
/**
 * 判断是否为可重试的 Layer 3 错误
 */
function isRetryableLayer3Error(error?: string): boolean {
  if (!error) return false;
  const retryablePatterns = [
    "429",
    "rate limit",
    "too many requests",
    "temporarily unavailable",
    "service unavailable"
  ];
  return retryablePatterns.some(pattern => 
    error.toLowerCase().includes(pattern)
  );
}

/**
 * 带时间感知的单次重试
 * 仅对 429 / rate limit 错误重试，且必须有足够预算
 */
async function runNotebookLMFallbackQueryWithBudget(
  query: string,
  config?: Layer3FallbackSettings
): Promise<{
  ok: boolean;
  text?: string;
  error?: string;
  command?: string[];
  raw?: any;
  attempts: number;
  skippedRetry?: boolean;
}> {
  const resolved = resolveLayer3FallbackSettings(config);
  const startedAt = Date.now();
  const timeoutMs = resolved.timeout * 1000;
  const reserveMs = 3000;  // 预留 3s 缓冲
  const retryBackoffMs = 1500;  // 重试前等待 1.5s
  const minRetryExecutionMs = 12000;  // 重试至少需要 12s 预算

  // 第一次尝试
  const first = await runNotebookLMFallbackQuery(query, config);
  if (first.ok) {
    return { ...first, attempts: 1 };
  }

  // 判断是否可重试
  const retryable = isRetryableLayer3Error(first.error);
  const elapsedMs = Date.now() - startedAt;
  const remainingMs = timeoutMs - elapsedMs - reserveMs;

  // 预算不足或不可重试，直接返回
  if (!retryable || remainingMs < (retryBackoffMs + minRetryExecutionMs)) {
    console.log(`[Layer3] Skipping retry: retryable=${retryable}, remainingMs=${remainingMs}`);
    return { 
      ...first, 
      attempts: 1, 
      skippedRetry: true 
    };
  }

  // 有预算，执行单次重试
  console.log(`[Layer3] Retrying after ${retryBackoffMs}ms (remaining budget: ${remainingMs}ms)`);
  await new Promise(resolve => setTimeout(resolve, retryBackoffMs));

  const second = await runNotebookLMFallbackQuery(query, {
    ...config,
    timeout: Math.max(1, Math.floor((remainingMs - retryBackoffMs) / 1000))
  });

  return { 
    ...second, 
    attempts: 2 
  };
}
```

**修改调用点**（第 410 行附近）：
```typescript
// 原代码：
// layer3Result = await runNotebookLMFallbackQuery(query, runtimeContext.layer3Fallback);

// 新代码：
layer3Result = await runNotebookLMFallbackQueryWithBudget(
  query,
  runtimeContext.layer3Fallback
);
```

---

### 修改 3：结果截断防御

**文件**：`src/tools.ts`  
**位置**：插入到第 220 行之前

```typescript
/**
 * 截断 Layer 3 返回内容，防止上下文爆炸
 */
function truncateLayer3Text(text: string, maxChars: number = 3000): {
  text: string;
  originalLength: number;
  keptLength: number;
  truncated: boolean;
} {
  const originalLength = text.length;
  
  if (originalLength <= maxChars) {
    return {
      text,
      originalLength,
      keptLength: originalLength,
      truncated: false
    };
  }

  const kept = text.slice(0, maxChars);
  return {
    text: `${kept}\n\n[TRUNCATED original_length=${originalLength} kept=${maxChars}]`,
    originalLength,
    keptLength: maxChars,
    truncated: true
  };
}
```

**修改拼接逻辑**（第 418-422 行附近）：
```typescript
// 原代码：
// if (layer3Result?.ok) {
//   parts.push(`Layer 3 (NotebookLM):\n\n${layer3Result.text}`);
// }

// 新代码：
if (layer3Result?.ok) {
  const safeLayer3 = truncateLayer3Text(layer3Result.text, 3000);
  parts.push(`Layer 3 (NotebookLM):\n\n${safeLayer3.text}`);
  
  // 记录截断信息到 details
  layer3TruncationInfo = {
    originalLength: safeLayer3.originalLength,
    keptLength: safeLayer3.keptLength,
    truncated: safeLayer3.truncated
  };
}
```

---

### 修改 4：JSON 分层防御解析

**文件**：`src/tools.ts`  
**位置**：修改 `runNotebookLMFallbackQuery` 函数中的 JSON 解析部分（第 248-262 行附近）

```typescript
/**
 * 清洗不安全的控制字符（保留 \n\r\t）
 */
function stripUnsafeControlChars(raw: string): string {
  return raw.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "");
}

/**
 * 提取候选 JSON（从代码块或首个对象/数组）
 */
function extractCandidateJson(raw: string): string | null {
  // 尝试提取 ```json ... ``` 或 ``` ... ``` 代码块
  const fenced = raw.match(/```(?:json)?\s*([\s\S]*?)\s*```/i);
  if (fenced?.[1]) {
    return fenced[1].trim();
  }

  // 提取首个 JSON 对象或数组
  const objectMatch = raw.match(/\{[\s\S]*\}/);
  const arrayMatch = raw.match(/\[[\s\S]*\]/);

  if (objectMatch?.[0] && arrayMatch?.[0]) {
    // 两者都存在，取出现更早的
    return objectMatch.index! < arrayMatch.index! 
      ? objectMatch[0] 
      : arrayMatch[0];
  }

  return objectMatch?.[0] ?? arrayMatch?.[0] ?? null;
}

/**
 * 分层防御 JSON 解析
 */
function safeParseJson(raw: string): {
  ok: boolean;
  value?: any;
  mode?: "direct" | "extracted";
  error?: string;
} {
  // 第一层：清洗控制字符
  const cleaned = stripUnsafeControlChars(raw).trim();

  // 第二层：尝试直接 parse
  try {
    return { 
      ok: true, 
      value: JSON.parse(cleaned), 
      mode: "direct" 
    };
  } catch {}

  // 第三层：提取候选 JSON 再 parse
  const candidate = extractCandidateJson(cleaned);
  if (candidate) {
    try {
      return { 
        ok: true, 
        value: JSON.parse(candidate), 
        mode: "extracted" 
      };
    } catch {}
  }

  // 第四层：降级失败
  return { 
    ok: false, 
    error: "json_parse_failed" 
  };
}
```

**修改 `runNotebookLMFallbackQuery` 中的解析逻辑**：
```typescript
// 原代码：
// try {
//   const raw = JSON.parse(trimmed);
//   // 提取 text 字段
// } catch {
//   // 降级兜底：返回原始文本
//   resolve({ ok: true, text: trimmed, raw: trimmed });
// }

// 新代码：
const parseResult = safeParseJson(trimmed);

if (parseResult.ok) {
  // 成功解析，提取 text 字段
  const text = parseResult.value?.content?.[0]?.text 
    || parseResult.value?.text 
    || parseResult.value?.message 
    || "";
  
  resolve({ 
    ok: true, 
    text, 
    raw: parseResult.value,
    parseMode: parseResult.mode
  });
} else {
  // 解析失败，记录错误并降级
  console.warn(`[Layer3] JSON parse failed: ${parseResult.error}`);
  resolve({ 
    ok: false, 
    error: `json_parse_failed: ${parseResult.error}`,
    command 
  });
}
```

---

## 测试用例

### 测试环境准备

```bash
# 1. 备份原文件
cd ~/.openclaw/workspace/plugins/memory-lancedb-pro
cp src/tools.ts src/tools.ts.backup

# 2. 应用修改（手动复制上述代码）

# 3. 重新构建
npm run build

# 4. 重启 OpenClaw
openclaw gateway restart
```

---

### 测试用例 1：超时边界验证

**目标**：验证 45s 超时先于主 Agent 超时触发

**步骤**：
```bash
# 临时修改 timeout 为 5s（模拟超时）
# 修改 openclaw.plugin.json:
{
  "layer3Fallback": {
    "enabled": true,
    "timeout": 5
  }
}

# 重启
openclaw gateway restart

# 执行查询
openclaw agent --agent main --json --message "测试：最近三天的详细工作记录"
```

**预期结果**：
- Tool 在 5s 后返回 Layer 2 结果
- 不触发主 Agent 超时
- `details.layer3Monitoring.error` 包含 "timeout"
- 主流程不崩溃

---

### 测试用例 2：时间感知重试

**目标**：验证预算不足时跳过重试

**步骤**：
```bash
# 1. 模拟 429 错误（需要修改代码或 mock）
# 2. 设置较短的 timeout（如 15s）
# 3. 第一次调用耗时 10s
# 4. 剩余预算 = 15 - 10 - 3 = 2s < 1.5 + 12 = 13.5s
```

**预期结果**：
- 不执行重试
- `details.layer3Monitoring.attempts` = 1
- `details.layer3Monitoring.skippedRetry` = true

---

### 测试用例 3：结果截断

**目标**：验证 3000 字符截断生效

**步骤**：
```bash
# 执行会触发 Layer 3 的查询
openclaw agent --agent main --json --message "详细说明最近一个月的所有工作"
```

**预期结果**：
- 如果 NotebookLM 返回 > 3000 字符
- 输出被截断到 3000 字符
- 末尾包含 `[TRUNCATED original_length=XXXX kept=3000]`
- `details.layer3Monitoring.truncated` = true

---

### 测试用例 4：JSON 防御（直接 parse）

**目标**：验证正常 JSON 可以直接解析

**步骤**：
```bash
# 正常查询
openclaw agent --agent main --message "今天做了什么"
```

**预期结果**：
- JSON 成功解析
- `details.layer3Monitoring.parseMode` = "direct"

---

### 测试用例 5：JSON 防御（提取 parse）

**目标**：验证混入噪音的 JSON 可以提取后解析

**步骤**：
```bash
# 需要 mock NotebookLM 返回带噪音的输出
# 例如：
# "Here is the result:\n```json\n{\"text\": \"...\"}\n```\nDone."
```

**预期结果**：
- JSON 成功解析
- `details.layer3Monitoring.parseMode` = "extracted"

---

### 测试用例 6：JSON 防御（降级）

**目标**：验证无法解析时安全降级

**步骤**：
```bash
# 需要 mock NotebookLM 返回完全无效的输出
# 例如：纯文本、HTML、损坏的 JSON
```

**预期结果**：
- 返回 Layer 2 结果
- `details.layer3Monitoring.success` = false
- `details.layer3Monitoring.error` 包含 "json_parse_failed"
- 主流程不崩溃

---

## 部署清单

### 前置检查

- [ ] 已备份 `src/tools.ts`
- [ ] 已阅读所有 6 份报告
- [ ] 已理解 4 个核心修改
- [ ] 已准备测试环境

### 实施步骤

1. **应用代码修改**（预计 30 分钟）
   - [ ] 修改 1：调整超时阈值
   - [ ] 修改 2：时间感知重试
   - [ ] 修改 3：结果截断
   - [ ] 修改 4：JSON 防御

2. **构建插件**（预计 5 分钟）
   ```bash
   cd ~/.openclaw/workspace/plugins/memory-lancedb-pro
   npm run build
   ```

3. **重启 OpenClaw**（预计 2 分钟）
   ```bash
   openclaw gateway restart
   ```

4. **执行测试**（预计 1 小时）
   - [ ] 测试用例 1：超时边界
   - [ ] 测试用例 2：时间感知重试
   - [ ] 测试用例 3：结果截断
   - [ ] 测试用例 4：JSON 直接 parse
   - [ ] 测试用例 5：JSON 提取 parse
   - [ ] 测试用例 6：JSON 降级

5. **验收确认**（预计 30 分钟）
   - [ ] 所有测试用例通过
   - [ ] Layer 2 功能未受影响
   - [ ] 监控字段正确记录
   - [ ] 无崩溃或异常

6. **生产部署**（预计 10 分钟）
   - [ ] 更新配置文件
   - [ ] 启用 Layer 3
   - [ ] 监控首批查询

---

## 回滚方案

### 触发条件

- Layer 2 召回成功率下降 > 5%
- 主 Agent 超时率上升 > 10%
- 用户报告查询响应变慢
- 发现严重 bug

### 回滚步骤

1. **立即禁用 Layer 3**（1 分钟）
   ```bash
   # 修改 openclaw.plugin.json
   {
     "layer3Fallback": {
       "enabled": false
     }
   }
   
   openclaw gateway restart
   ```

2. **恢复原代码**（5 分钟）
   ```bash
   cd ~/.openclaw/workspace/plugins/memory-lancedb-pro
   cp src/tools.ts.backup src/tools.ts
   npm run build
   openclaw gateway restart
   ```

3. **验证回滚**（10 分钟）
   ```bash
   # 执行正常查询
   openclaw agent --agent main --message "测试查询"
   
   # 检查 details 中无 layer3Decision 字段
   ```

4. **通知相关方**
   - 推送回滚通知到监控群
   - 记录回滚原因和时间
   - 安排问题分析会议

---

## 监控指标

### Phase 1 关键指标

| 指标 | 目标值 | 告警阈值 |
|------|--------|---------|
| Layer 3 触发率 | 5-10% | > 20% 或 < 2% |
| Layer 3 成功率 | > 80% | < 70% |
| Layer 3 超时率 | < 10% | > 20% |
| Layer 3 平均耗时 | 30-45s | > 50s |
| Layer 2 成功率 | > 95% | < 90% |
| 主 Agent 超时率 | < 1% | > 5% |

### 监控方式

```bash
# 查看统计日志
grep "Layer3Stats" ~/.openclaw/logs/*.log | jq -s '
{
  total: length,
  triggered: map(select(.triggered == true)) | length,
  success: map(select(.success == true)) | length,
  timeout: map(select(.error | contains("timeout"))) | length,
  avgDuration: (map(.durationMs // 0) | add / length)
}
'
```

---

## 附录：完整文件清单

### 修改的文件

1. `~/.openclaw/workspace/plugins/memory-lancedb-pro/src/tools.ts`
   - 修改行数：约 150 行
   - 新增函数：5 个
   - 修改函数：2 个

### 新增的文件

无（所有修改都在现有文件中）

### 配置文件

1. `~/.openclaw/workspace/plugins/memory-lancedb-pro/openclaw.plugin.json`
   - 需要添加 `layer3Fallback` 配置

### 测试文件

无（测试用例通过 CLI 执行）

---

## 总结

**Phase 1 实施完成后，将实现**：
- ✅ 超时边界可控（45s 默认，50s 上限）
- ✅ 重试策略智能（时间感知，单次重试）
- ✅ 结果截断防御（3000 字符硬截断）
- ✅ JSON 解析鲁棒（分层防御）

**下一步**：
- Phase 2：监控增强（1 周）
- Phase 3：触发优化（1-2 周）
- Phase 4：架构演进（延后至 v2）

**关键原则**：
- 主链稳定性优先
- 失败边界前置
- 可观测性内置
- 最小改动原则

---

**Spec-Kit 状态**：✅ 完成  
**下一步**：提交给晨星确认，准备实施
