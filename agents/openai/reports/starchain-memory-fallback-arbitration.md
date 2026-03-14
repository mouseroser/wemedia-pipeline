# 星链打磨层 - Step 1.5F：OpenAI 仲裁决议

> **主题**：对 Layer 3（NotebookLM）降级集成中的 4 个争议点做技术裁决  
> **日期**：2026-03-14  
> **裁决人**：OpenAI Technical Arbiter

---

## 结论摘要（可直接执行）

1. **超时阈值**：裁决为 **45s 默认值**，不是 50s，也不是 60s。  
2. **重试策略**：裁决为 **时间感知的单次重试**，不是固定指数退避多次重试，也不是完全禁用。  
3. **结果截断**：裁决为 **3000 字符硬截断**，并追加明确尾注：`[TRUNCATED n chars]`。  
4. **JSON 防御**：裁决为 **分层防御解析**，不是“只靠正则提取”。顺序为：**清洗控制字符 → 尝试直接 parse → 提取 fenced/block JSON 再 parse → 失败则降级**。

这四项都应并入 **Phase 1**，不要延后到 Phase 3。

---

## 1. 超时阈值裁决

### 裁决
- `layer3Fallback.timeout = 45` 秒（默认）
- 如需配置覆盖，允许调高到 **50s 上限**，但**默认值必须是 45s**
- 代码中应保留注释：**该超时必须显著小于主 Agent 60s 工具窗口**

### 理由
- 宪法红线很清楚：**Layer 3 必须先超时，不允许主链先超时**。
- Gemini 指出的数学矛盾成立：`Layer 2 (~0.5s) + Layer 3(60s) + spawn/冷启动/网络尾延迟 > 60s`，所以 **60s 方案不可接受**。
- **50s** 虽然比 60s 安全，但缓冲仍偏薄；CLI spawn、子进程退出、stderr flush、宿主调度抖动都可能吃掉 5-8s。
- **45s** 给主链预留约 15s 的安全垫，更符合“失败边界前置收口”的宪法要求。

### 代码级修改建议
```ts
const DEFAULT_LAYER3_FALLBACK: Required<Layer3FallbackSettings> = {
  enabled: false,
  agent: "notebooklm",
  notebook: "",
  notebookId: "",
  timeout: 45,
  // timeout must stay well below the main agent 60s tool window
  ...
};
```

如存在配置校验，增加保护：
```ts
const timeout = Math.min(userConfig.timeout ?? 45, 50);
```

---

## 2. 重试策略裁决

### 裁决
采用 **时间感知的单次重试**：
- **最多 1 次重试**（总共最多 2 次尝试）
- **仅对 429 / rate limit / transient upstream unavailable** 重试
- **必须先判断剩余预算是否足够**；不足则直接降级，不重试
- 退避固定为 **1.5s-2s**，不要 2s/4s 指数退避链

### 理由
- 宪法允许“有限重试”，但前提是**不能把增强能力做成稳定性债务**。
- Claude 计划里的 `2s + 4s` 指数退避，在同步阻塞模式下太激进；若第一次已耗时较长，第二次几乎必然冲穿总预算。
- 完全禁用重试也过于保守，会放弃一部分短暂 429 的可恢复机会。
- 因此最稳妥的折中是：**有预算才重试一次；没预算立即回退**。

### 推荐预算规则
假设：
- 总 Layer 3 budget = `timeoutMs`
- 预留结束缓冲 = `reserveMs = 3000`
- 重试前至少保证：`remainingMs >= retryBackoffMs + minRetryExecutionMs`
- 建议 `minRetryExecutionMs = 12000`
- 建议 `retryBackoffMs = 1500`

若不满足，则不重试。

### 代码级修改建议
```ts
async function runNotebookLMFallbackQueryWithBudget(
  query: string,
  config?: Layer3FallbackSettings
) {
  const resolved = resolveLayer3FallbackSettings(config);
  const startedAt = Date.now();
  const timeoutMs = (resolved.timeout ?? 45) * 1000;
  const reserveMs = 3000;
  const retryBackoffMs = 1500;
  const minRetryExecutionMs = 12000;

  const first = await runNotebookLMFallbackQuery(query, config);
  if (first.ok) return { ...first, attempts: 1 };

  const retryable = isRetryableLayer3Error(first.error);
  const elapsedMs = Date.now() - startedAt;
  const remainingMs = timeoutMs - elapsedMs - reserveMs;

  if (!retryable || remainingMs < (retryBackoffMs + minRetryExecutionMs)) {
    return { ...first, attempts: 1, skippedRetry: true };
  }

  await sleep(retryBackoffMs);
  const second = await runNotebookLMFallbackQuery(query, {
    ...config,
    timeout: Math.max(1, Math.floor((remainingMs - retryBackoffMs) / 1000))
  });

  return { ...second, attempts: 2 };
}
```

---

## 3. 结果截断裁决

### 裁决
- Layer 3 返回内容做 **3000 字符硬截断**
- 追加统一尾注：`\n\n[TRUNCATED original_length=XXXX kept=3000]`
- `details` 中同步记录：
  - `layer3TextOriginalLength`
  - `layer3TextTruncated: true/false`
  - `layer3TextKeptLength`

### 理由
- **2000**：对 NotebookLM 深度补充来说偏短，容易损失关键上下文。  
- **5000**：对主链上下文压力仍偏大，尤其当最终输出还要叠加 Layer 2、监控 details、上游 prompt 时。  
- **3000**：是信息密度与上下文安全之间更均衡的默认值，符合“增强可用，但不能挤爆主链”的目标。
- 必须显式标注截断，而不是静默裁剪，否则会破坏可解释性。

### 代码级修改建议
```ts
function truncateLayer3Text(text: string, maxChars = 3000) {
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

拼接主输出前执行：
```ts
const safeLayer3 = truncateLayer3Text(layer3Result.text, 3000);
parts.push(`Layer 3 (NotebookLM):\n\n${safeLayer3.text}`);
```

---

## 4. JSON 防御裁决

### 裁决
不采用“只用正则提取 JSON”这种单点方案。采用 **四段式防御解析**：

1. **清洗控制字符**（保留 `\n\r\t`，去掉其他不可见控制字符）  
2. **尝试直接 `JSON.parse`**  
3. 若失败，再做 **代码块 / 首个 JSON 对象或数组提取** 后二次 parse  
4. 仍失败则 **记录 parse failure 并安全降级**，绝不把脏原文无保护拼进主输出

### 理由
- Gemini 提出的正则提取建议是对的，但**只能算轻量补丁的一部分**。
- 单独使用 `/\{[\s\S]*\}/` 风险很高：贪婪匹配、嵌套对象、前后噪音、数组根节点都会误伤。
- 更稳的方案是：**先 clean，再 parse；parse 不过，再有限提取；最后降级**。
- 这符合宪法的“最小改动 + 失败可收口”，且比完整流式 JSON 解析器更适合首版。

### 代码级修改建议
```ts
function stripUnsafeControlChars(raw: string): string {
  return raw.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "");
}

function extractCandidateJson(raw: string): string | null {
  const fenced = raw.match(/```(?:json)?\s*([\s\S]*?)\s*```/i);
  if (fenced?.[1]) return fenced[1].trim();

  const objectMatch = raw.match(/\{[\s\S]*\}/);
  const arrayMatch = raw.match(/\[[\s\S]*\]/);

  if (objectMatch?.[0] && arrayMatch?.[0]) {
    return objectMatch.index! < arrayMatch.index! ? objectMatch[0] : arrayMatch[0];
  }
  return objectMatch?.[0] ?? arrayMatch?.[0] ?? null;
}

function safeParseJson(raw: string) {
  const cleaned = stripUnsafeControlChars(raw).trim();
  try {
    return { ok: true, value: JSON.parse(cleaned), mode: "direct" };
  } catch {}

  const candidate = extractCandidateJson(cleaned);
  if (candidate) {
    try {
      return { ok: true, value: JSON.parse(candidate), mode: "extracted" };
    } catch {}
  }

  return { ok: false, error: "json_parse_failed" };
}
```

**重要补充**：若 parse 失败，主输出不要直接拼接完整脏原文；最多只在 `details` 记录摘要错误，并走 Layer 2 only。

---

## 最终实施指令（对 Phase 1）

Phase 1 应按以下参数落地，不再保留歧义：

- `timeout`: **45s default / 50s hard cap**
- retry: **budget-aware, max 1 retry, only retryable errors**
- truncation: **3000 chars + explicit [TRUNCATED ...] marker**
- JSON parsing: **sanitize → direct parse → extract parse → fallback**

### 不采纳项
- 不采纳 `timeout=60s`
- 不采纳固定 `2s/4s` 指数退避两次重试
- 不采纳 `5000` 字符截断
- 不采纳“只用一个正则直接抽 JSON”
- 不采纳 parse 失败后把长原文直接暴露到主输出

---

## 一句话仲裁

> Layer 3 首版必须按“**45 秒内可失败、1 次有预算重试、3000 字符有标记截断、JSON 分层防御解析**”落地；任何会把增强路径变成长阻塞、长输出、脏输出的方案，一律不通过。
