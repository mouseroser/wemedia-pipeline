# NotebookLM 自动降级触发规则

## 触发条件（满足任一即触发）

### 1. 查询类型检测

**时间敏感查询**：
- 关键词：今天、昨天、最近、本周、上周、这个月、过去X天
- 示例：
  - "今天完成了什么"
  - "最近三天的工作"
  - "本周的优化重点"

**深度推理查询**：
- 关键词：为什么、如何、对比、演进、冲突、关系、影响
- 示例：
  - "为什么选择这个方案"
  - "对比两次架构调整"
  - "这个决策和之前是否冲突"

**中文语义查询**（复杂句式）：
- 包含动词+名词组合
- 非精确关键词
- 示例：
  - "我们在记忆系统上做过哪些优化"
  - "星链流水线的核心改进是什么"

### 2. Layer 2 召回质量检测

**召回不足**：
- 返回结果 < 3 条
- 且查询长度 > 5 个字（排除简单查询）

**相关性低**：
- Top 1 结果的 score < 0.5
- 或 Top 3 平均 score < 0.4

### 3. 显式触发

**用户明确要求**：
- 查询包含：详细、完整、历史、所有、全部
- 示例：
  - "详细说明记忆系统的演进"
  - "列出所有关于 XXX 的讨论"

---

## 不触发条件（快速路径）

### 1. 精确查询
- 单个实体名（晨星、小光、Gemini）
- 技术术语（memory-lancedb-pro、openclaw.json）
- ID/路径（chat ID、文件路径）

### 2. Layer 2 召回充分
- 返回 ≥ 5 条
- Top 1 score ≥ 0.6
- Top 3 平均 score ≥ 0.5

### 3. 简单事实查询
- "XXX 是什么"
- "XXX 的版本"
- "XXX 的路径"

---

## 实现伪代码

```python
def needs_notebooklm(query: str, layer2_results: list) -> bool:
    # 1. 时间敏感
    time_keywords = ["今天", "昨天", "最近", "本周", "上周", "这个月", "过去"]
    if any(kw in query for kw in time_keywords):
        return True
    
    # 2. 深度推理
    reasoning_keywords = ["为什么", "如何", "对比", "演进", "冲突", "关系", "影响"]
    if any(kw in query for kw in reasoning_keywords):
        return True
    
    # 3. 召回不足
    if len(layer2_results) < 3 and len(query) > 5:
        return True
    
    # 4. 相关性低
    if layer2_results:
        top1_score = layer2_results[0].get("score", 0)
        if top1_score < 0.5:
            return True
        
        if len(layer2_results) >= 3:
            avg_score = sum(r.get("score", 0) for r in layer2_results[:3]) / 3
            if avg_score < 0.4:
                return True
    
    # 5. 显式触发
    explicit_keywords = ["详细", "完整", "历史", "所有", "全部"]
    if any(kw in query for kw in explicit_keywords):
        return True
    
    return False
```

---

## 测试用例

| 查询 | Layer 2 结果 | 触发? | 原因 |
|---|---|---|---|
| 晨星的核心偏好 | 3条, score 0.7 | ❌ | 召回充分 |
| 记忆系统优化 | 0条 | ✅ | 召回不足 |
| 今天完成任务 | 1条, score 0.3 | ✅ | 时间敏感 + 相关性低 |
| 最近三天工作 | 0条 | ✅ | 时间敏感 + 召回不足 |
| Ollama 性能 | 5条, score 0.8 | ❌ | 召回充分 |
| 为什么选择这个方案 | 2条, score 0.5 | ✅ | 深度推理 |
| memory-lancedb-pro 版本 | 1条, score 0.9 | ❌ | 精确查询 |
| 详细说明记忆演进 | 3条, score 0.6 | ✅ | 显式触发 |

---

## 性能考虑

**NotebookLM 调用成本**：
- 延迟：3-10 秒
- API 成本：~$0.01/次
- Token 消耗：~2000 tokens

**优化策略**：
- 只在真正需要时触发（预计 20-30% 查询）
- 缓存常见查询结果（1 小时 TTL）
- 异步调用（不阻塞 Layer 2 结果返回）

---

## 下一步

1. 实现 `needs_notebooklm()` 判断函数
2. 实现 NotebookLM API 调用封装
3. 实现结果合并逻辑
4. 测试 baseline 查询集
5. 部署到生产
