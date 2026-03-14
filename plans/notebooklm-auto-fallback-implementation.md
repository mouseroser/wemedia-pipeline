# NotebookLM 自动降级 - 实现方案

## 方案对比

### ❌ 方案 A：直接调用 nlm-gateway.sh
```python
subprocess.run([
    "nlm-gateway.sh", "query",
    "--agent", "main",
    "--notebook", "memory-archive",
    "--query", query
])
```

**问题**：
- nlm-gateway.sh 内部调用 `notebooklm` CLI
- `notebooklm ask` 命令超时（>30s）
- 所有 notebook 都超时

---

### ✅ 方案 B：通过 sessions_spawn 调用 notebooklm agent（推荐）

```python
sessions_spawn({
    "agentId": "notebooklm",
    "mode": "run",
    "runtime": "subagent",
    "task": f"查询 Memory Archive notebook：{query}\n\n使用 notebook: memory-archive (94f8f2c3-55a7-4f51-94eb-df65cc835b53)\n\n请直接返回查询结果。",
    "runTimeoutSeconds": 90
})
```

**优势**：
- ✅ notebooklm agent 内部有更好的错误处理
- ✅ 可以设置更长的超时时间（90s）
- ✅ 返回结构化结果
- ✅ 已验证成功（60s 返回详细结果）

---

## 集成到 OpenClaw

### 选项 1：扩展 memory_recall tool

在 `memory-lancedb-pro` 插件中添加自动降级逻辑：

```typescript
async function memory_recall(query: string, limit: number = 5) {
  // Step 1: Layer 2 快速召回
  const layer2Results = await lancedb_search(query, limit);
  
  // Step 2: 判断是否需要 NotebookLM
  if (needs_notebooklm(query, layer2Results)) {
    // Step 3: Spawn notebooklm agent
    const notebooklmResult = await spawn_notebooklm_query(query);
    
    // Step 4: 合并结果
    return {
      layer2: layer2Results,
      layer3: notebooklmResult,
      sources: ['Layer 2', 'Layer 3 (NotebookLM)']
    };
  }
  
  return { layer2: layer2Results, layer3: null, sources: ['Layer 2'] };
}
```

**优点**：
- 对用户透明（仍然调用 memory_recall）
- 自动降级，无需手动判断

**缺点**：
- 需要修改 memory-lancedb-pro 插件
- 增加插件复杂度

---

### 选项 2：创建新 tool（推荐）

创建独立的 `enhanced_memory_recall` tool：

```typescript
// 在 OpenClaw 核心或新插件中
async function enhanced_memory_recall(query: string, limit: number = 5) {
  // 同上逻辑
}
```

**优点**：
- 不修改现有插件
- 可以独立测试和优化
- 用户可以选择使用哪个 tool

**缺点**：
- 需要用户显式调用新 tool
- 或者需要在 AGENTS.md 中说明何时使用

---

### 选项 3：在 AGENTS.md 中指导使用（临时方案）

在 `AGENTS.md` 中添加规则：

```markdown
## 记忆召回策略

### 何时使用 memory_recall（Layer 2）
- 精确关键词查询
- 实体查询（人名、项目名）
- 快速查询（<500ms）

### 何时 spawn notebooklm agent（Layer 3）
- 时间敏感查询（今天、最近、本周）
- 深度推理查询（为什么、如何、对比）
- Layer 2 返回 0 条或相关性低
- 需要完整历史记录

### 示例
```bash
# Layer 2 快速查询
memory_recall query:"晨星的核心偏好"

# Layer 3 深度查询
sessions_spawn(
  agentId: "notebooklm",
  task: "查询 Memory Archive：2026-03-14 完成了哪些优化工作"
)
```
```

**优点**：
- 无需修改代码
- 立即可用
- 灵活性高

**缺点**：
- 需要 agent 手动判断
- 不是自动降级

---

## 推荐方案

**短期（本周）**：选项 3（AGENTS.md 指导）
- 立即可用
- 验证触发频率和效果

**中期（本月）**：选项 2（新 tool）
- 开发 `enhanced_memory_recall` tool
- 集成到 OpenClaw 核心或新插件

**长期（下季度）**：选项 1（扩展现有 tool）
- 提 PR 到 memory-lancedb-pro
- 或 fork 并维护自己的版本

---

## 触发逻辑（Python 参考实现）

```python
def needs_notebooklm(query: str, layer2_results: list) -> bool:
    """判断是否需要调用 NotebookLM"""
    
    # 1. 时间敏感查询
    time_keywords = ["今天", "昨天", "最近", "本周", "上周", "这个月", "过去"]
    if any(kw in query for kw in time_keywords):
        return True
    
    # 2. 深度推理查询
    reasoning_keywords = ["为什么", "如何", "对比", "演进", "冲突", "关系", "影响", "区别"]
    if any(kw in query for kw in reasoning_keywords):
        return True
    
    # 3. 召回不足
    if len(layer2_results) < 3 and len(query) > 5:
        return True
    
    # 4. 相关性低
    if layer2_results:
        top1_score = layer2_results[0].get("score", 1.0)
        if top1_score < 0.5:
            return True
        
        if len(layer2_results) >= 3:
            scores = [r.get("score", 1.0) for r in layer2_results[:3]]
            avg_score = sum(scores) / len(scores)
            if avg_score < 0.4:
                return True
    
    # 5. 显式触发
    explicit_keywords = ["详细", "完整", "历史", "所有", "全部", "列出"]
    if any(kw in query for kw in explicit_keywords):
        return True
    
    return False
```

---

## 性能优化

### 1. 缓存机制
```typescript
const cache = new Map<string, {result: any, timestamp: number}>();
const CACHE_TTL = 3600000; // 1 hour

function getCachedResult(query: string) {
  const cached = cache.get(query);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.result;
  }
  return null;
}
```

### 2. 异步调用
```typescript
// 不阻塞 Layer 2 结果返回
const layer2Promise = lancedb_search(query);
const layer3Promise = needs_notebooklm(query) 
  ? spawn_notebooklm_query(query) 
  : Promise.resolve(null);

const [layer2, layer3] = await Promise.all([layer2Promise, layer3Promise]);
```

### 3. 流式返回
```typescript
// 先返回 Layer 2，再补充 Layer 3
yield { layer2: await layer2Promise, layer3: null };
if (layer3Promise) {
  yield { layer2: null, layer3: await layer3Promise };
}
```

---

## 监控指标

需要记录的指标：
- 触发频率（每日 NotebookLM 调用次数）
- 触发原因分布（时间敏感 vs 深度推理 vs 召回不足）
- 响应时间（Layer 2 vs Layer 3）
- 成功率（NotebookLM 查询成功 vs 超时）
- 用户满意度（Layer 3 结果是否有价值）

---

## 下一步行动

1. **立即**：更新 AGENTS.md，添加记忆召回策略指导
2. **本周**：监控实际使用情况，验证触发频率
3. **下周**：开发 `enhanced_memory_recall` tool
4. **本月**：集成到 OpenClaw，添加缓存和监控
