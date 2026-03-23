# 4H.4 — 接口边界决策：新工具 vs Behind Flag

**日期**: 2026-03-23  
**作者**: 小光（todo-autopilot）  
**关联任务**: master-execution-plan.md 4H.4  
**类型**: 非 coding 决策文档 / 接口边界固化  
**状态**: ✅ 决策已收口

---

## 背景

4H 上游兼容路线定义了 strict fallback（Layer 3 NotebookLM 触发）应以何种方式上游化。  
4H.2 收口后，接口边界决策（新工具 vs behind flag）是 PR-B 草案的前置条件。  
本文档固化决策，作为 PR-B 起草时的接口约束依据。

---

## 决策依据（数据支撑）

来自 4E 观察期（7天 + 延伸观察期 Day 1-2，共 9 天数据）：

| 指标 | 数据 | 说明 |
|------|------|------|
| L3 触发率 | ~12-27%（Day 1-9，均值约 18%） | 低于 20% 预计算缓存触发门槛 |
| L3 成功率 | Day 6-9 连续 100% | 稳态可靠 |
| L2 平均质量 | 4.4-4.5/5 | L2 已可满足大多数场景，L3 是补充而非主链 |
| 冲突记忆出现率 | 0%（连续 9 天） | 无噪音污染风险 |
| Q13 缺口 | sessionMemory 架构缺口 | 新工具或 flag 均无法在短期填补 |

核心结论：**L3 触发率（~18%均值）处于边界区间（预计算缓存门槛 20%），且 L2 质量已高（4.4/5），不需要新工具大幅扩展默认接口契约。**

---

## 方案分析

### 方案 A：新工具（enhanced_memory_recall / memory_recall_v2）

**优点**：
- 旧工具保持默认契约 100% 不变
- 新工具可自由定义 richer output 格式
- maintainer 接受风险最低（不改线上用户体验）

**缺点**：
- 需要用户/代理主动改用新工具名，迁移成本存在
- 上游需维护两套工具（版本并行期长）
- 工具发现性较低（新名字不如 flag 直观）

### 方案 B：旧工具 + opt-in flag

**优点**：
- 用户无需更换工具名，只需设一个 flag 即可开启增强模式
- API surface 不增加，上游 namespace 更清晰
- 与现有 PR #227 关闭经验对齐（opt-in / behind flag 是 maintainer 接受边界内）

**缺点**：
- 旧工具 response contract 需明确区分 default/enhanced 两条路径
- 需要仔细设计 flag 名和文档，避免歧义

---

## 决策：**方案 B（旧工具 + opt-in flag）**

### 理由

1. **接受边界优先**：4H.2 已收口确认，maintainer 接受 opt-in / behind flag 方式；新工具路线在接受边界内但额外引入迁移摩擦。
2. **L3 触发率不足以证明需要新工具**：平均 ~18% 的 L3 触发率，意味着 82% 的请求 L2 即可满足，没有充分理由用新工具名拆分接口。
3. **PR-A 先行原则**：PR-A（纯基础设施加固）优先，PR-B（strict fallback）是 follow-up，新工具路会增加 PR-A 阶段的复杂度。
4. **向后兼容性**：旧工具加 opt-in flag，零迁移成本，maintainer 审核时无 API breaking change 顾虑。

---

## 接口约束规范（用于 PR-B 草案）

```
工具名: memory_recall（保持不变）

新增 opt-in flag（参考名）:
  - fallback: "layer3" | "none" | "auto"（默认 "none"，保持当前行为）
  - 或更简单: enhanced: true | false（默认 false）

触发条件（仅当 flag 显式指定 layer3/enhanced=true 后）:
  - L2 minScore 未达阈值时，自动降级 L3
  - 关键词不能单独触发（避免误触发）
  - 低置信度（L2 score < 配置阈值）才触发

输出格式（enhanced 模式）:
  - 标准输出格式保持兼容
  - 可附加 metadata（source, confidence, layer）
  - 不改变默认（非 enhanced）模式的 response schema

禁止事项:
  - 不默认开启 L3 触发
  - 不改变无 flag / flag=none 时的任何行为
  - 不在 PR-A 阶段引入此 flag（仅 PR-B 起）
```

---

## 后续步骤

| 步骤 | 状态 | 说明 |
|------|------|------|
| 4H.3 PR-A（纯基础设施） | ⏳ 等待恢复 | 前置；当前本轮不启动 |
| 4H.5 PR-B 草案（with 本文约束） | ⏳ 等待 PR-A 合并 | 依赖 4H.3 完成 |
| 4H.6 evidence skeleton | ⏳ 等待恢复 | 随 PR-B 起草一并输出 |

---

## 不做（边界约束继承自 4H.2）

- ❌ 新建 `enhanced_memory_recall` / `memory_recall_v2` 工具
- ❌ 默认改变 `memory_recall` 的 response contract
- ❌ 在 PR-A 阶段捆绑此决策
- ❌ 因 L3 触发率（~18%）未超 20% 门槛而实现预计算缓存（4F.7 已跳过）

---

## 参考文件

- `reports/4H2-pr227-upstream-closure-note-20260321.md`
- `reports/layer3-dual-track-roadmap-20260317.md`
- `reports/layer3-upstream-priority-reset-20260317.md`
- `reports/memory-retrieval-observation-20260314.md`（4E 观察期全数据）
- master-execution-plan.md 4H 区块
