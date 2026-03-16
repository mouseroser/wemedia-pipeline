# MEMORY-ARCHITECTURE.md - 记忆系统架构说明

## 两套架构的关系

我们有两套"三层架构"，它们服务不同场景，保持独立但相互配合。

---

## 架构 A：文件架构（Agent 启动时加载）

**用途**：Agent 每次启动时的"必读清单"

### Layer 1: Identity Layer（身份层）
- `SOUL.md` — 我是谁
- `IDENTITY.md` — 快速参考卡
- `USER.md` — 我服务谁

### Layer 2: Operations Layer（操作层）
- `AGENTS.md` — 我怎么工作
- `HEARTBEAT.md` — 自愈检查
- 角色专属指南（写作风格、格式参考）

### Layer 3: Knowledge Layer（知识层）
- `MEMORY.md` — 精华长期记忆（只在 main session 加载）
- `memory/YYYY-MM-DD.md` — 每日原始日志（今天 + 昨天）
- `shared-context/` — 跨 agent 知识（THESIS、FEEDBACK-LOG、SIGNALS）
- `intel/` — agent 协作文件（单写者原则）

**启动流程**：
```
1. 读取 SOUL.md（我是谁）
2. 读取 USER.md（我服务谁）
3. 读取 AGENTS.md（我怎么工作）
4. 读取 MEMORY.md（血泪教训 + 错误示范 + 核心偏好）
5. 读取 memory/今天+昨天.md（最近发生了什么）
6. 读取 shared-context/（当前关注什么、有哪些纠正、追踪什么趋势）
```

---

## 架构 B：记忆系统架构（运行时检索）

**用途**：运行时的"检索引擎"

### Layer 1: 本地文件（底层 - 原始记录）
- **文件**：memory/YYYY-MM-DD.md, MEMORY.md
- **用途**：原始记录、可追溯、人类可读
- **特点**：持久化存储，永不丢失

### Layer 2: memory-lancedb-pro（中层 - 快速检索）
- **技术**：向量检索 + BM25 + Rerank
- **用途**：日常快速检索（90% 场景）
- **特点**：语义搜索，自动捕获
- **状态**：P1（autoRecall=true, autoCapture=true）

### Layer 3: Memory Archive (NotebookLM)（顶层 - 深度理解）
- **Notebook ID**：94f8f2c3-55a7-4f51-94eb-df65cc835b53
- **用途**：深度理解、长期归档、跨会话分析
- **特点**：AI 辅助理解，生成摘要和洞察

**检索流程**：
```
1. 优先使用 memory-lancedb-pro（memory_recall）
2. 如果需要深度理解，查询 Memory Archive (NotebookLM)
3. 如果需要原始记录，直接读取本地文件
```

---

## 映射关系

| 文件架构 | 记忆系统架构 | 说明 |
|----------|--------------|------|
| MEMORY.md | Layer 1 + Layer 2 | 精华记忆同时存在文件和向量数据库 |
| memory/YYYY-MM-DD.md | Layer 1 + Layer 2 | 每日日志自动捕获到向量数据库 |
| shared-context/ | Layer 1 only | 跨 agent 知识层，不需要向量检索 |
| intel/ | Layer 1 only | Agent 协作文件，单写者原则 |
| - | Layer 3 (NotebookLM) | 长期归档，深度理解 |

---

## 使用场景

### 场景 1：Agent 启动
- **使用**：文件架构（Architecture A）
- **目的**：快速加载身份、职责、核心偏好
- **文件**：SOUL.md, USER.md, AGENTS.md, MEMORY.md, memory/今天+昨天.md, shared-context/

### 场景 2：运行时检索
- **使用**：记忆系统架构（Architecture B）
- **目的**：语义搜索、快速召回相关记忆
- **工具**：memory_recall（memory-lancedb-pro）

### 场景 3：深度理解
- **使用**：记忆系统架构 Layer 3（NotebookLM）
- **目的**：跨会话分析、生成洞察、长期归档
- **工具**：NotebookLM notebook query

### 场景 4：跨 agent 协作
- **使用**：文件架构 Layer 3（shared-context/ + intel/）
- **目的**：共享知识、单写者原则、避免冲突
- **文件**：THESIS.md, FEEDBACK-LOG.md, SIGNALS.md, intel/collaboration/

---

## 维护规则

### 文件架构维护
- **MEMORY.md**：手动维护，提炼精华
- **memory/YYYY-MM-DD.md**：自动捕获 + 手动补充
- **shared-context/**：每周日回顾更新
- **intel/**：单写者原则，谁写谁维护

### 记忆系统维护
- **Layer 1（本地文件）**：每周日压缩检查（40k tokens 阈值）
- **Layer 2（memory-lancedb-pro）**：自动捕获，按需补充原子记忆
- **Layer 3（NotebookLM）**：每月归档一次，生成月度摘要

---

## 优化建议

### 短期（1-2 周）
- ✅ 文件架构已优化完成
- ⚠️ 记忆系统观察期（监控漏召回）
- ⚠️ NotebookLM 归档流程待建立

### 中期（1-3 个月）
- 🎯 建立自动归档流程（memory → NotebookLM）
- 🎯 优化原子记忆补充策略
- 🎯 探索 Layer 2 和 Layer 3 的协同

### 长期
- 🎯 实现知识积累和经验传承的自动化
- 🎯 建立跨会话的洞察生成机制
- 🎯 探索更多本地化记忆方案

---

**最后更新**: 2026-03-12 15:16
**维护者**: main (小光)
