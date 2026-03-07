# memory-lancedb-pro 部署方案（OpenClaw JSON 架构落地版）

## 一、技术分析

### 1.1 核心功能
- **混合检索引擎**：Vector (LanceDB ANN) + BM25 (FTS) 双路召回
- **Cross-Encoder 重排**：支持 Jina / SiliconFlow / Pinecone 等兼容接口
- **多阶段打分流水线**：Recency Boost / Importance / Length Norm / Time Decay / MMR / Hard Min Score
- **多作用域隔离**：`global` / `agent:<id>` / `project:<id>` / `user:<id>` / `custom:<name>`
- **自适应检索**：跳过寒暄、命令、简单确认，命中记忆相关问题时强制检索
- **噪声过滤**：过滤拒绝回复、元提问、HEARTBEAT 等低质量记忆
- **会话策略**：`systemSessionMemory` / `memoryReflection` / `none`
- **自进化**：`.learnings/LEARNINGS.md` / `ERRORS.md` / `FEATURE_REQUESTS.md`
- **Markdown 镜像**：双写到 agent workspace 的 `memory/YYYY-MM-DD.md`
- **Auto-Capture & Auto-Recall**：`agent_end` 自动抽取 + `before_agent_start` 自动注入

### 1.2 对当前 OpenClaw 的关键适配结论
这次部署不能沿用旧版 `config.yaml` 思路，必须按当前机器的 `openclaw.json` 架构落地。

**当前环境实况（已验证）**：
- OpenClaw 主配置文件：`/Users/lucifinil_chen/.openclaw/openclaw.json`
- 主 workspace：`/Users/lucifinil_chen/.openclaw/workspace`
- 当前内置 `memory_search` 已修复为：`ollama + nomic-embed-text`
- 本机 Ollama 可用，`http://127.0.0.1:11434/v1/embeddings` 已实测可返回向量
- 当前 `plugins` 配置中尚未接入 `memory-lancedb-pro`

**最关键的兼容性判断**：
- `memory-lancedb-pro` 的插件 schema 要求 `embedding.provider = "openai-compatible"`
- 它不是原生 `gemini` / `ollama` provider 配置风格，而是统一走 OpenAI-compatible embeddings 接口
- 因此这份部署方案的第一阶段应该直接走 **本地 Ollama OpenAI-compatible 路线**，不走原生 Gemini embeddings

### 1.3 与当前内置记忆系统的关系
当前系统里已经有两层记忆能力：
1. **内置 `memory_search` 文件记忆检索层**：索引 `MEMORY.md` + `memory/**/*.md`
2. **待部署的 `memory-lancedb-pro` 插件层**：提供更强的混合检索、作用域隔离、Auto-Capture / Auto-Recall、工具与治理能力

**部署策略**：
- 不先拆当前已经修好的 `memory_search`
- 先把 `memory-lancedb-pro` 作为新的 memory plugin 接入 OpenClaw
- 第一阶段只做**稳定落地 + 基础验证**，不一开始就打开全部高级功能

## 二、落地架构（按当前目录体系）

### 2.1 目录角色划分
- `intel/collaboration/`：多 agent 联合分析阶段的共享材料目录
- `workspace/plugins/`：正式进入运行态的插件目录
- `agents/*/reports/`：正式报告产物目录

### 2.2 本项目的正确落位
当前已经有一份分析用仓库副本：
- `~/.openclaw/workspace/intel/collaboration/memory-lancedb-pro/`

这份副本应继续保留为：
- 多 agent 联合阅读 / 对比 / 复核的**共享分析材料**

真正要被 OpenClaw 加载的运行态插件，应提升到：
- `~/.openclaw/workspace/plugins/memory-lancedb-pro/`

**结论**：
- `intel/collaboration/` 放分析副本
- `workspace/plugins/` 放运行副本
- 不要让 OpenClaw 直接加载 `intel/collaboration/` 里的共享分析目录作为正式运行插件路径

## 三、推荐部署路线

### 3.1 P0 路线（推荐，先稳后强）
**目标**：先把插件稳定挂载到当前 OpenClaw，上线最小可用能力。

**P0 配置原则**：
- Embedding：本地 Ollama（`nomic-embed-text`）
- Rerank：关闭
- Session Strategy：`systemSessionMemory`
- Auto-Capture：先关
- Auto-Recall：先关
- Management Tools：先关
- Markdown Mirror：开

这样做的原因：
- 避免在第一轮引入额外外部 API 依赖
- 避免和当前已经可用的内置记忆链叠加出不可控噪声
- 先验证插件加载、存储、检索、作用域隔离、Markdown 镜像是否稳定

### 3.2 P1 路线（P0 验证通过后）
在 P0 稳定后，再逐步打开：
- `autoCapture: true`
- `autoRecall: true`
- `enableManagementTools: true`（按需）

### 3.3 P2 路线（最后再上）
如果后续确实需要更高检索质量，再考虑：
- 接入 Jina / SiliconFlow / Pinecone 的 cross-encoder rerank
- 或者单独为 rerank 增加外部 API key

**不建议第一天就上 rerank。**

## 四、可直接执行的部署步骤

### 4.1 前置检查
```bash
# 1) 检查 OpenClaw 状态
openclaw status

# 2) 检查 Ollama 是否在线
curl http://127.0.0.1:11434/api/tags

# 3) 检查 OpenAI-compatible embeddings 端点
curl http://127.0.0.1:11434/v1/embeddings \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer ollama-local' \
  --data '{"model":"nomic-embed-text","input":"test"}'
```

### 4.2 提升共享分析副本为正式运行副本
```bash
cd ~/.openclaw/workspace
mkdir -p plugins
rsync -a intel/collaboration/memory-lancedb-pro/ plugins/memory-lancedb-pro/
cd plugins/memory-lancedb-pro
npm install
```

说明：
- 这里不是重新从 GitHub 拉一份，而是把已经过星鉴阅读/分析的副本提升为运行副本
- 分析副本保留在 `intel/collaboration/`；运行副本落在 `plugins/`

### 4.3 `openclaw.json` 接入方式
在现有 `openclaw.json` 中，保留已有 `plugins.entries.telegram`，追加如下结构：

```json
{
  "plugins": {
    "load": {
      "paths": [
        "plugins/memory-lancedb-pro"
      ]
    },
    "entries": {
      "telegram": {
        "enabled": true
      },
      "memory-lancedb-pro": {
        "enabled": true,
        "config": {
          "embedding": {
            "provider": "openai-compatible",
            "apiKey": "ollama-local",
            "model": "nomic-embed-text",
            "baseURL": "http://127.0.0.1:11434/v1",
            "dimensions": 768
          },
          "dbPath": "~/.openclaw/memory/lancedb-pro",
          "autoCapture": false,
          "autoRecall": false,
          "autoRecallMinLength": 8,
          "captureAssistant": false,
          "enableManagementTools": false,
          "sessionStrategy": "systemSessionMemory",
          "retrieval": {
            "mode": "hybrid",
            "vectorWeight": 0.7,
            "bm25Weight": 0.3,
            "minScore": 0.35,
            "rerank": "none",
            "candidatePoolSize": 20,
            "recencyHalfLifeDays": 14,
            "recencyWeight": 0.1,
            "filterNoise": true,
            "lengthNormAnchor": 500,
            "hardMinScore": 0.35,
            "timeDecayHalfLifeDays": 60,
            "reinforcementFactor": 0.5,
            "maxHalfLifeMultiplier": 3
          },
          "scopes": {
            "default": "global",
            "definitions": {
              "global": { "description": "Shared knowledge" },
              "agent:main": { "description": "Main private memory" },
              "agent:claude": { "description": "Claude private memory" },
              "agent:gemini": { "description": "Gemini private memory" }
            },
            "agentAccess": {
              "main": ["global", "agent:main"],
              "claude": ["global", "agent:claude"],
              "gemini": ["global", "agent:gemini"]
            }
          },
          "mdMirror": {
            "enabled": true,
            "dir": "memory-md"
          },
          "selfImprovement": {
            "enabled": true,
            "beforeResetNote": true,
            "skipSubagentBootstrap": true,
            "ensureLearningFiles": true
          }
        }
      }
    },
    "slots": {
      "memory": "memory-lancedb-pro"
    }
  }
}
```

### 4.4 关键说明
- `embedding.provider` 必须按插件 schema 写成 `openai-compatible`
- `apiKey` 对 Ollama 可以是占位符，`ollama-local` 即可
- `baseURL` 必须指向 OpenAI-compatible 路径：`http://127.0.0.1:11434/v1`
- 第一阶段 `rerank` 设为 `none`
- 第一阶段不要打开 `autoCapture` / `autoRecall`
- 当前已经修好的 `agents.defaults.memorySearch`（内置文件记忆索引）先不动

### 4.5 重启与验证
```bash
openclaw gateway restart
openclaw plugins list
openclaw plugins info memory-lancedb-pro
openclaw plugins doctor
openclaw config get plugins.slots.memory
```

预期结果：
- `memory-lancedb-pro` 被识别为已加载插件
- `plugins.slots.memory` 指向 `memory-lancedb-pro`
- 无 schema 校验错误

## 五、验收测试（按当前环境可执行）

### 5.1 插件加载验收
```bash
openclaw plugins list
openclaw plugins info memory-lancedb-pro
openclaw logs | grep memory-lancedb-pro
```

### 5.2 基础 embeddings 验收
```bash
curl http://127.0.0.1:11434/v1/embeddings \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer ollama-local' \
  --data '{"model":"nomic-embed-text","input":"memory test"}'
```

### 5.3 最小功能验收
如果插件 CLI / tools 已暴露出来，优先做三类验证：
1. 存一条记忆
2. 按 query 召回
3. 检查 Markdown 镜像是否落盘

**验收标准**：
- 能成功写入 LanceDB
- 能按语义 + 关键词回忆
- 对应 agent workspace 下能看到镜像文件

### 5.4 作用域隔离验收
至少验证：
- `agent:claude` 的私有记忆不会被 `agent:gemini` 直接读到
- `global` 记忆可以被多个授权 agent 访问

### 5.5 第一阶段不做的测试
以下内容放到 P1 / P2：
- Cross-encoder rerank
- 大规模批量导入
- memoryReflection 深度反射链
- 自动捕获与自动召回并发验证

## 六、风险与规避

### 6.1 最大风险：把旧方案的 yaml 配置直接套到当前系统
旧报告的问题不在项目本身，而在于把部署写成了另一套配置架构。

**必须修正为**：
- 配置文件：`openclaw.json`
- 插件装载面：`plugins.load.paths` / `plugins.entries` / `plugins.slots`

### 6.2 最大兼容性风险：embedding provider 写错
旧稿把 embedding 写成原生 `gemini` / `ollama`。

但当前项目 schema 明确要求：
- `embedding.provider = "openai-compatible"`

因此：
- Ollama 路线要写 `baseURL = http://127.0.0.1:11434/v1`
- 不要写成内置 `memorySearch` 那种 provider 形式

### 6.3 当前环境最稳的路线
结合本机已验证情况，最稳路线是：
- Embedding：本地 Ollama
- Model：`nomic-embed-text`
- Rerank：先关
- Session Strategy：`systemSessionMemory`
- Auto-Capture / Auto-Recall：先关

### 6.4 jiti 缓存风险
如果后续修改插件 `.ts` 源码，必须执行：
```bash
rm -rf /tmp/jiti/
openclaw gateway restart
```

否则 restart 之后仍可能加载旧缓存代码。

## 七、最终建议

### 7.1 推荐结论
**推荐部署路线：P0 本地 Ollama 最小可用版。**

原因：
- 与当前机器已验证通过的 embeddings 能力一致
- 无需再引入新的外部 key
- 风险最低
- 能最快判断插件是否值得继续接入现有长期记忆体系

### 7.2 不推荐的路线
当前不推荐：
- 第一阶段直接走 Gemini embeddings
- 第一阶段直接开 rerank
- 第一阶段直接开 autoCapture + autoRecall
- 直接把 `intel/collaboration/` 里的分析目录当正式运行插件路径

### 7.3 上线顺序
1. 提升运行副本到 `workspace/plugins/`
2. `npm install`
3. 在 `openclaw.json` 里追加插件配置
4. `openclaw gateway restart`
5. 做最小功能验收
6. 验证稳定后再开 P1 / P2

## 八、结论

这份项目原始部署方案的方向没有问题，但落地层需要彻底切换到你现在机器的真实架构：
- **不是** `config.yaml`
- **而是** `openclaw.json`
- **不是** 直接写原生 `gemini/ollama` provider
- **而是** 插件 schema 要求的 `openai-compatible`
- **不是** 让共享分析副本直接进运行态
- **而是** `intel/collaboration/` 保留分析副本，`workspace/plugins/` 承载运行副本

按当前环境，最可执行、最稳的最终落地方案是：
- `memory-lancedb-pro` 以插件方式接入 OpenClaw
- 本地 Ollama 提供 embeddings
- 第一期只上最小可用能力
- 当前已修好的内置 `memory_search` 先保持不动

如果继续推进，下一步就不是再写报告了，而是进入：
**按这份方案实际安装、改 `openclaw.json`、重启、做验收。**
