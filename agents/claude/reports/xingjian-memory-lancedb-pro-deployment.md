# memory-lancedb-pro 部署方案（OpenClaw JSON 架构最终统一版）

## 结论
NodeSeek 这套“三层物理记忆 + 脱水打标 + 时序防僵尸 + 人工审核”的思路，已经可以和当前这台机器的 OpenClaw 架构对齐，而且大部分核心能力已经落地。

这份文档不再把 `memory-lancedb-pro` 视为“待设计、待接入”的插件方案，而是把旧部署稿与 2026-03-08 的本地化最终方案合并成一份统一口径的最终部署报告。

**当前这台机器的最终落地形态应定义为：**
- **Tier-0 权威热区**：`SOUL.md` / `IDENTITY.md` / `USER.md` / `MEMORY.md`
- **Tier-1 深度长期记忆**：`memory-lancedb-pro`（LanceDB Pro）
- **Tier-2 日志与暂存层**：`memory/YYYY-MM-DD.md`
- **治理层**：原子记忆补强 + 观察期检查单 + 回滚手册 + 人工修订

**一句话结论：**
NodeSeek 那套三层记忆，在这台机器上已经大部分落地；当前只差外部 rerank，才算进入真正的 P2 高质量检索阶段。

## 一、从旧部署稿到当前统一口径

### 1.1 旧部署稿解决了什么
旧稿的价值主要在两点：
- 明确必须按当前机器的 `openclaw.json` 架构落地，而不是沿用旧版 `config.yaml`
- 明确 `memory-lancedb-pro` 的 embedding 配置要走插件 schema 要求的 `openai-compatible`，并通过本地 Ollama 提供 `nomic-embed-text`

这些判断仍然成立，而且已经被当前机器的实际运行状态验证过。

### 1.2 为什么现在要改写成“最终统一版”
旧稿的问题不是方向错，而是阶段判断偏早：
- 当时它把系统视为 **P0/P1 待上线方案**
- 但当前机器实际上已经完成了插件接入、基础验证、历史记忆导入、原子记忆补强和观察/回滚文档建设

因此，当前更准确的表述应该是：
- **不是继续写“如何接入”**
- **而是承认当前系统已经处于本地化落地后的运行态**

## 二、把 NodeSeek 原方案翻译成当前机器的架构

### 2.1 Tier-0：权威热区（Absolute Override）
NodeSeek 原文强调：身份、用户、长期记忆要成为“启动必读、不可跳过”的唯一真相来源。

落到当前机器上，对应的是：
- `~/.openclaw/workspace/SOUL.md`
- `~/.openclaw/workspace/IDENTITY.md`
- `~/.openclaw/workspace/USER.md`
- `~/.openclaw/workspace/MEMORY.md`

而且 main agent 的启动规则本来就已经这么设计：
- 先读 `SOUL.md`
- 再读 `USER.md`
- 再读当天/昨天 `memory/*.md`
- 主私聊再读 `MEMORY.md`

**结论**：Tier-0 在当前机器上已经存在，不需要重建；只需要继续保持“数据库记忆不得覆盖 Tier-0 文件记忆”的原则。

### 2.2 Tier-1：深度长期记忆层
NodeSeek 原方案的核心组件是：
- LanceDB Pro 向量数据库
- Embedding
- Hybrid Retrieval
- Rerank
- 噪声过滤
- Auto Recall

当前机器的对应实现是：
- 运行时插件：`memory-lancedb-pro`
- 数据库路径：`~/.openclaw/memory/lancedb-pro`
- 向量模型：`nomic-embed-text`
- Embedding 通路：本地 Ollama 的 OpenAI-compatible 端点
- 检索模式：`hybrid`
- 当前状态：已启用并接管运行时 `memory` slot

### 2.3 Tier-2：日常流水账 / 暂存层
NodeSeek 把 `memory/YYYY-MM-DD.md` 定义为“原始对话缓存 + 等待脱水整理”的海马体层。

当前机器上，这层已经天然存在：
- `~/.openclaw/workspace/memory/YYYY-MM-DD.md`

而且当前插件也启用了 Markdown 镜像，会把记忆镜像写回 Markdown。

**结论**：Tier-2 也已经存在，不需要额外再起一套系统。

## 三、当前机器的最终部署形态

### 3.1 当前三层记忆架构

```text
┌──────────────────────────────────────────────────────┐
│ Tier-0  权威热区                                     │
│ SOUL.md / IDENTITY.md / USER.md / MEMORY.md          │
│ 启动必读，优先级最高，不被数据库覆盖                 │
└───────────────────────┬──────────────────────────────┘
                        │ 按需召回 / 规则约束
                        ▼
┌──────────────────────────────────────────────────────┐
│ Tier-1  深度长期记忆层                               │
│ memory-lancedb-pro + LanceDB + Ollama embeddings     │
│ autoRecall + autoCapture + hybrid retrieval          │
└───────────────────────┬──────────────────────────────┘
                        │ 镜像 / 人工整理 / 复盘
                        ▼
┌──────────────────────────────────────────────────────┐
│ Tier-2  日志与暂存层                                 │
│ memory/YYYY-MM-DD.md                                 │
│ 原始记录、流水日志、人工脱水前素材                   │
└──────────────────────────────────────────────────────┘
```

### 3.2 当前已生效配置摘要
配置文件：`/Users/lucifinil_chen/.openclaw/openclaw.json`

当前 `memory-lancedb-pro` 的统一口径应理解为：
- `embedding.provider = "openai-compatible"`
- `embedding.model = "nomic-embed-text"`
- `embedding.baseURL = "http://127.0.0.1:11434/v1"`
- `dbPath = "~/.openclaw/memory/lancedb-pro"`
- `sessionStrategy = "systemSessionMemory"`
- `enableManagementTools = true`
- `autoCapture = true`
- `autoRecall = true`
- `captureAssistant = true`
- `retrieval.rerank = "none"`
- 已接管 `plugins.slots.memory`
- 已配置插件加载路径 `plugins.load.paths`
- 已配置 `plugins.allow` 白名单

这意味着旧稿里“先走 P0 最小接入、暂不开 recall/capture”的建议，已经完成历史使命；当前系统已经处于更靠后的运行阶段。

### 3.3 当前状态
按当前机器的统一口径，已经达到：
- `Memory: enabled (plugin memory-lancedb-pro)`
- `memory-lancedb-pro` 正常加载
- `memory_store / memory_recall / memory_forget / memory_update / memory_stats / memory_list` 可用
- 插件 CLI `openclaw memory-pro` 可用
- 检索模式为 `hybrid`
- 作用域为 `agent:main`
- 历史记忆已导入数据库
- 高频规则、偏好、事实已做多轮原子化补强

## 四、对 NodeSeek 方案的本地化改写

### 4.1 “脱水打标”在当前机器上的正确实现
NodeSeek 的“脱水打标”思路，在当前机器上不应该再另起一套新系统，而应该对应成：
- **长篇记忆归档**：保留在 `MEMORY.md` / `memory/*.md`
- **数据库长期记忆**：导入 `memory-lancedb-pro`
- **高频问题补强**：用短句型原子记忆补齐聊天态 recall
- **人工修订**：通过 `memory_update` / `memory_forget` / `memory_list` / `memory_stats` 做治理

这就是当前已经验证可行的“脱水打标”实现。

### 4.2 “时序防僵尸”在当前机器上的正确实现
NodeSeek 提到“旧知识、新知识打架”这个问题。

当前机器上的防僵尸机制，不应该靠重新造轮子，而应该依赖这几层：
- Tier-0 权威文件优先
- `memory_update` 用于修订旧记忆，而不是一味追加
- 原子记忆优先承载高频稳定规则
- 观察期只在真实漏召回时补，不盲目加记忆
- 回滚优先回滚配置，不直接删数据库

### 4.3 “人工审核”在当前机器上的正确实现
NodeSeek 的人工审核思想，在当前机器上已经落成以下治理文档：
- `reports/memory-observation-checklist-2026-03-07.md`
- `reports/memory-rollback-runbook-2026-03-07.md`
- `reports/memory-system-status-2026-03-07.md`
- `reports/memory-rollout-changelog-2026-03-07.md`
- `reports/memory-report-index-2026-03-07.md`

也就是说，人工审核不是嘴上说“以后手工看”，而是已经有了操作文档和回滚路径。

## 五、哪些地方已经完成，哪些还没做

### 5.1 已完成
- Tier-0 文件层已存在并在 main 启动路径中生效
- Tier-1 `memory-lancedb-pro` 插件已部署并接管 `memory` slot
- Tier-2 每日日志层已存在
- 本地 Ollama embeddings 已接通
- 内置 `memory_search` 链路也已修复
- 历史 `MEMORY.md` 已导入数据库
- 高频规则 / 偏好 / 事实已做多轮原子化补强
- 观察、回滚、状态、索引文档已齐
- 系统已经进入“自然使用观察期”

### 5.2 还没完成
只剩最后一个大块还没开：
- **P2 rerank**

原因不是没做，而是当前插件 schema 对 rerank 只支持外部 provider，例如：
- `jina`
- `siliconflow`
- `voyage`
- `pinecone`

当前不支持：
- `ollama` 直接作为 rerank provider

因此现在的系统状态是：
- **除外部 rerank 外，其他核心能力已基本到位**

## 六、对后续路线的统一建议

### 6.1 当前最推荐的运行姿态
当前建议维持为：
- `memory-lancedb-pro` 持续作为主运行时记忆插件
- 本地 Ollama 持续负责 embeddings
- 保持 `autoRecall = true`
- 保持 `autoCapture = true`
- 保持当前治理文档体系
- 保持 `rerank = none`
- 继续自然使用观察期

### 6.2 未来唯一值得推进的大项
如果以后要继续升级，最值得推进的是：
- 补一个外部 rerank provider 的 key
- 再从当前状态升级到真正的 P2 高质量检索模式

在这一步之前，不建议再盲目加新层、加新机制或重写整套记忆系统。

### 6.3 当前不推荐的路线
当前不推荐：
- 再重新搭一套独立于现有体系的新记忆系统
- 回退到“仅写 P0 接入方案、尚未上线”的口径
- 在没有真实漏召回证据前继续盲目补原子记忆
- 在没有 rerank provider 的情况下假装系统已经到了 P2

## 七、最终结论
这份统一版报告的结论很明确：
- **不要重新搭一套新记忆系统**
- **直接承认当前这台机器已经落在 NodeSeek 方案的本地化完成态**
- 其中：
  - Tier-0 = 文件权威层
  - Tier-1 = `memory-lancedb-pro`
  - Tier-2 = `memory/YYYY-MM-DD.md`
  - 治理层 = 原子记忆 + 观察清单 + 回滚手册 + 人工修订

因此，当前最准确的一句话总结是：

**NodeSeek 那套“三层物理记忆”方案，在这台机器上已经不是待设计状态，而是 Tier-0 / Tier-1 / Tier-2 三层都已落地；当前只差外部 rerank，才算真正进入 P2 高质量检索阶段。**
