# MEMORY.md - 小光的长期记忆

## 关于晨星
- 名字：陈颖，称呼：晨星
- 时区：Asia/Shanghai
- 使用 Telegram 作为主要通讯渠道

## Telegram 群组与子 Agent
| Agent ID | 群名 | Chat ID |
|----------|------|---------|
| monitor-bot | 监控告警 | -5131273722 |
| docs | 项目文档 | -5095976145 |
| test | 代码测试 | -5245840611 |
| review | 交叉审核 | -5242448266 |
| coding | 代码编程 | -5039283416 |
| brainstorming | 灵感熔炉 | -5231604684 |
| wemedia | 自媒体 | -5146160953 |
| nano-banana | 生图 | -5217509070 |
| gemini | 织梦 | -5264626153 |
| notebooklm | 珊瑚 | -5202217379 |
| claude | 小克 | -5101947063 |

## 自媒体管家（wemedia agent）
- 模型：minimax/MiniMax-M2.5，thinking: high
- ⚠️ spawn 时必须带 `thinking: "high"`（per-agent thinkingDefault 不支持，只能 spawn 时传参）
- 示例：`sessions_spawn(agentId: "wemedia", thinking: "high", task: "...")`
- workspace: ~/.openclaw/workspace-wemedia/
- 职责：内容创作、排期发布、数据监控、多平台分发、评论互动
- 管理平台：小红书、TikTok/抖音、知乎
- 已创建完整工作流文件结构（platforms/、templates/、content-calendar/、analytics/）
- 安全规则：未经晨星确认不得发布内容到外部平台
- 下属 agent：nano-banana（生图）、gemini（文本生成/分析）
- 架构：生图、gemini、自媒体都属于自媒体管家的工作流，由 wemedia 统筹调度

## 模型配置
- 默认模型：authropic/claude-opus-4-6
- 代理端点：want.eat99.top（Gemini 3.1 Pro Preview）
- 也有 MiniMax、GPT Codex 等配置
- 建议过将 openai provider 改名为 gemini-proxy 避免混淆
- 星链流水线（starchain，原 agent-teams-openclaw）已启用 Gemini、Claude、GPT 三模型交叉审核思路：Gemini 负责研究/诊断加速，Claude 与 GPT 参与交叉审查与不同阶段校验；后续按三模型交叉审核口径执行，不再把 gemini 仅视为可选辅助
- skill 路径：~/.openclaw/skills/starchain/

## 偏好
- 遇到问题和解决方案要自动记录到记忆中
- 语言规则：晨星 ↔ 小光 对话使用中文；小光与 claude（opus/sonnet）和 gpt 模型交流使用英文；其他场景使用中文
- ⚠️ 踩坑即记：遇到任何问题及其解决方案，必须立即写入 memory/YYYY-MM-DD.md 和 MEMORY.md 踩坑笔记，防止重复踩坑
- ⚠️ 主动记录：不用问晨星是否需要记录，发现问题/完成工作后直接写入 memory
- ⚠️ 新偏好（2026-03-06）：以后默认主动记录所有重要决定、偏好、踩坑、解决方案和完成结果；除非晨星明确说不要记录，否则直接写入记忆
- ⚠️ 新偏好（2026-03-06）：以后默认自动操作；对内部可安全执行的事项直接执行，不再额外等待晨星确认，除非涉及外部发送、公开发布、危险修改或晨星明确要求先问
- ⚠️ 新边界（2026-03-06）：不要走捷径；每个智能体只做自己的本职工作。main 只做 main 自己的本职工作，不越位代做其他智能体的执行过程、产物归属或职责范围内工作
- ⚠️ 新边界（2026-03-06）：所有智能体的职责边界都要明确；编排、执行、审查、测试、研究、文案、推送补发等边界必须清晰，避免角色串位和责任漂移
- ⚠️ 新纠偏（2026-03-06）：当晨星说“让星链……”时，含义是启动星链自动化流水线本身，不是 main 代读、代做、代汇总。main 负责触发与编排流水线，产出应由星链流程自然给出，不要把结果表述成“main 再汇总给晨星”
- ⚠️ 新规则（2026-03-06）：主私聊会话禁止承载长编排。main 在晨星私聊中只做自己的本职工作：收任务、分发、汇总、补发通知；长任务必须外包到对应智能体或独立链路，避免把私聊会话占住导致“像不可用”
- ⚠️ 新规则（2026-03-06）：通知机制不只适用于正式流水线。凡是 main 发起了多智能体编排、swap、委派执行，都必须有通知。
- ⚠️ 新规则（2026-03-06）：通知粒度随编排复杂度升级——简单委派用开始 / 完成 / 失败；多智能体编排必须带关键阶段；正式流水线和复杂多阶段编排按实际阶段逐段通知，不能一刀切压成三段式
- ⚠️ 新纠偏（2026-03-06）：之前把通知链路一味收口到 `main` 是错误方向。对有消息能力的 agent，应恢复其向自己职能群发送开始/关键进度/完成/失败消息；`main` 负责监控群、缺失补发和最终交付，而不是替代 agent 的可见性职责。
- ⚠️ 新规则（2026-03-06）：同一问题若在同一解决方向上连续三次未解决，必须切换方向，重新定义问题；不能在错误方向上越走越远。
- **Telegram 群组访问控制**：使用 `groupPolicy: "allowlist"` + `groupAllowFrom: ["1099011886"]`，只允许晨星在群里使用 bot

## 流水线

### 星链新增工作模式
- **外部方案产品化模式**：当晨星给出网上方案，希望星链“读方案并开发出适合小光的产品”时，不做照搬，而是执行：外部方案吸收 → 内部约束对齐 → 产品定义 → 分阶段实现 → 结果沉淀
- 三层处理原则：方案层（理念与结构）、产品层（适合小光体系的功能边界与协作方式）、实现层（代码、配置、通知、记忆、回滚）
- 优先级原则：若外部方案与当前系统冲突，优先保证系统稳定、可回滚、可演进

### 星链 StarChain v2.2（原 agent-teams-openclaw）
- 全自动推进，除 Step 7 晨星确认外不停顿（Rule 0）
- Spawn 重试机制：失败自动重试 3 次（第 2 次等 10 秒），3 次都失败才 BLOCKED + 告警
- 所有 agent 推送规范统一：开始 + 完成 + 失败，推送到职能群 + 监控群
- sub-agent 推送不可靠（depth-2 限制），关键推送由 main 补发
- coding agent 可能谎报完成，必须通过 review 验证
- **打磨层（Step 1.5）**：gemini 问题宪法 → claude 实施计划 → review/gemini 复核 → review/gpt 仲裁（L3）
- **Type A/B 动态模型切换**：
  - Type A (业务/架构): coding(sonnet/medium) + review(gpt/high) + review/gemini(medium 快速复核) + test(gpt/medium)
  - Type B (算法/性能): coding(gpt/medium) + review/gemini(medium 算法分析) + test(sonnet/medium)
  - 分歧仲裁: review(opus/medium) + coding(gpt/xhigh)
  - main 在 Step 1 判断 Type 后，通过 spawn 参数动态覆盖模型
- **Step 4 增加 gemini 预审**：每轮修复后先用 review/gemini/low 快速预审，预审 PASS 才进入正式审查，预计降本 15-20%
- **Step 5.5 增强诊断与仲裁（v2.2 新增）**：
  - 1️⃣ gemini/high → 诊断 memo
  - 2️⃣ review/gemini/medium → 复核诊断
  - 3️⃣ brainstorming/opus/high → 根因分析 + 回滚决策
  - 4️⃣ review/gpt/high → 仲裁回滚决策（按需：Epoch>=2 / 回滚到S1 / 信心度<0.7）
  - Epoch 成功率提升 15-20%（原 10-15%）
- **openclaw.json 默认配置**（Type B 为基准）：
  - coding: gpt (gpt-5.4)
  - review: sonnet
  - test: sonnet
  - brainstorming: sonnet（R3/TF-3/Step 5.5 动态切换到 opus）
  - main: opus
  - docs: minimax
  - monitor-bot: minimax
  - 织梦(gemini): gemini-preview
  - 珊瑚(notebooklm): opus
  - 小克(claude): opus
- **优化收益**：
  - Thinking Level 优化降本 10-15%
  - Gemini 预审降本 15-20%
  - 总计降本约 25-35%
  - 提升效率 30-40%
  - Epoch 成功率提升 15-20%

## 自动更新规则
⚠️ **流水线更新自动应用**：
- 当星链或自媒体流水线的 SKILL.md、流程图或合约更新时
- main (小光) 必须自动更新所有相关智能体的 AGENTS.md 配置
- 确保所有智能体了解最新的流程、职责和协作方式
- 更新完成后重启 gateway 让配置生效
- 更新记录写入 memory/YYYY-MM-DD.md

### wemedia v1.0（已集成 NotebookLM）
- Step 2 调研：gemini 快速调研 + NotebookLM 深度调研（M/L 级）
- Step 5.5（新增）：NotebookLM 衍生内容生成（音频播客/思维导图/问答卡片/信息图），L 级推荐，M 级可选
- S 级流程：Step 1→3→5→6→7
- M 级流程：Step 1→2(含NLM)→3→4→5→6→7
- L 级流程：Step 1→2(含NLM)→3→4→5→5.5(衍生)→6→7

### NotebookLM Skill
- 路径：~/.openclaw/skills/notebooklm/
- 3 个 notebook：memory, openclaw-docs, media-research
- `openclaw-docs` 只用于 OpenClaw 故障、配置、架构、命令，以及 NotebookLM/OpenClaw 集成自身的问题
- 其他场景不要默认连接 `openclaw-docs`；优先直接使用 NotebookLM 当前登录态或目标 notebook
- 如果 `openclaw-docs` 被删除并重建，必须立即同步更新 `config/notebooks.json`，否则网关会继续打旧 ID
- 代理必须走支持的节点（如美国、台湾），且 Surge 增强模式默认开启
- Cron：健康检查每 6h + 文档刷新每天 04:00
- Gateway 自动从 settings.json 读取 proxy 配置
- CLI：notebooklm v0.3.3，认证文件 ~/.notebooklm/storage_state.json
- GitHub 仓库：mouseroser/starchain, mouseroser/wemedia

## 约定
- （生图流程约定已取消，待重新定义）

## 踩坑笔记（OpenClaw 配置）

### GitHub 项目一律先 clone 到本地，再分析
- **问题**：直接用 browser 访问 GitHub 网页容易触发限流（Too many requests）
- **原因**：限流针对 OpenClaw browser 的具体会话，不是全局限流；短时间内反复打开同一仓库页面尤其容易触发
- **正确做法**：遇到 GitHub 项目，优先本地 clone，再读 README / docs / 代码
  ```bash
  git clone https://github.com/user/repo.git /tmp/repo-name
  cat /tmp/repo-name/README.md
  ```
- **适用范围**：星链、StarEval、自媒体；凡是涉及“阅读 GitHub 项目 / 吸收外部方案 / 分析开源仓库”，默认都先本地 clone
- **优势**：
  - 避免 GitHub 网页限流
  - 可访问完整仓库内容，不只 README
  - 可查看源码、配置、目录结构、脚本细节
  - 更快、更稳定，可重复读取
  - 下载后可离线分析，便于多 agent 复用
- **临时解决方案**：如果已经触发 GitHub 网页限流，可重启 OpenClaw browser：`openclaw browser stop && openclaw browser start`

### 多 agent 联合工作的非正式材料统一放 `intel/collaboration/`
- **原始定义不变**：`intel/` 仍然是 Agent 间协作目录，遵守单写者原则
- **规则**：只要是多 agent 联合工作（流水线尤为明显），除了正式产物之外全部放到 `intel/collaboration/`
- **正式产物**：报告、审查结论、修复代码、文档交付等 → 放各自 agent 目录
- **非正式产物**：外部 GitHub 项目、本地镜像、共享分析材料、临时脚本、调研素材等 → 放 `intel/collaboration/`
- **首选目录**：`~/.openclaw/workspace/intel/collaboration/`
- **示例**：`~/.openclaw/workspace/intel/collaboration/memory-lancedb-pro/`
- **为什么不冲突**：
  - `intel/collaboration/` 是多 agent 联合工作的非正式材料集中地
  - 单写者原则仍成立：谁 clone / 更新，谁负责维护该目录；其他 agent 只读
- **边界**：
  - `intel/collaboration/` 放非正式产物、共享输入、协作素材
  - agent 的正式工作产物仍放各自 agent 目录，不放 `intel/`
- **临时场景**：一次性快速查看可先 clone 到 `/tmp/`；任务升级为多 agent 联合后统一转到 `intel/collaboration/`

### Sub-agent depth-2 无 workspace context 注入
- depth-2 sub-agent（review spawn 的 coding/test/brainstorming/docs）不会注入 AGENTS.md
- 但 message 工具可用
- 解决方案：review spawn 时在 task 中附带推送指令（chat ID + message 用法）
- 每个 agent 自己推送到自己的群，review 不代劳

### Review 与 Main 编排硬性约束
- **Review 约束**：绝不自己写代码或跑测试，必须 spawn coding/test agent。即使 L1 最简单的任务也必须 spawn。
- **Main 编排约束 (小光)**：在执行流水线时，绝不允许自己直接编辑、修改或修复应用代码与脚本。如遇工具或脚本阻塞，必须 spawn `coding` agent 处理，或在手动修改前必须明确请求晨星授权。

### Telegram 群白名单
- ❌ `channels.telegram.allowGroups` 不存在，会导致启动失败
- ✅ 用 `channels.telegram.groups: { "<chatId>": { ... } }` 同时充当白名单和群配置
- ✅ **支持通配符 `"*"`**：`groups: { "*": { requireMention: false } }` 可以为所有群设置默认配置
- 具体群 ID 配置会覆盖通配符配置

### Telegram 群消息响应
- 默认 `requireMention: true`，需要 @bot 才响应
- 要自动响应所有消息：`"requireMention": false`

### Telegram bindings peer.id 格式
- 使用 `"tg:-xxxxxxxxxx"` 格式（带 tg: 前缀）

### 获取 Telegram 群 Chat ID
- polling 模式下 getUpdates 可能为空（已被消费）
- 从 `/tmp/openclaw/openclaw-YYYY-MM-DD.log` 日志 grep `chatId` 最可靠

### openclaw doctor
- `openclaw doctor --fix` 会自动清除未知配置字段
- 改配置前先确认字段名正确
- ❌ 不支持的字段：`agents.list[].label`、`agents.list[].timeoutSeconds`、`channels.telegram.groups[chatId].label`
- ✅ agent 超时只能在 spawn 时传 `runTimeoutSeconds`，不能在 openclaw.json 配置

### sessions_spawn 是非阻塞的
- `sessions_spawn` 立即返回 `{ status: "accepted", runId }` ，不等子 agent 完成
- `mode=run` 下 announce 机制会重新唤醒 parent session 继续处理下一步
- 多轮串行循环（如 Step 4 R1→R2→R3）在 mode=run 下可以工作

### 子 agent API 失败导致 review 违规
- coding agent API 凭证错误时，review 会违反硬性约束自己改代码
- 解决：review AGENTS.md 加硬性约束 — 子 agent 失败必须重试 spawn（最多3次），绝不自己代替
- 3次仍失败 → 推送监控群 + HALT

### model fallback 配置
- `agents.defaults.model.fallbacks` 数组，按顺序尝试
- 全局 fallback 会被所有 agent 继承
- 单个 agent 可通过 `agents.list[].model` 覆盖

### Step 7 通知晨星缺失
- pipeline 流程图画了 review → main → 晨星，但 review AGENTS.md 没写通知指令
- 导致 review 只推监控群就结束，晨星收不到交付通知
- 修复：Step 7 加硬性通知指令（监控群 + 晨星 DM target:1099011886）
- 教训：流程图和执行指令必须一一对应

### 获取新群 Chat ID（groupPolicy 临时开放法）
- 新群没在白名单时，日志不记录消息，getUpdates 也抓不到
- 解决：临时把 `channels.telegram.groupPolicy` 改为 `"open"`，重启 gateway，发消息后从日志 grep 负数 ID
- 抓到后改回 `"allowlist"`

### groups 配置不支持 agentId
- ❌ `channels.telegram.groups[chatId].agentId` 不存在，会报 Unrecognized key
- ✅ agent 绑定必须用 `bindings` 数组：`{"agentId": "xxx", "match": {"channel": "telegram", "peer": {"kind": "group", "id": "tg:<chatId>"}}}`

### groups/bindings 变更需要 gateway restart
- groups 和 bindings 的变更不是 dynamic reload，需要 `openclaw gateway restart`

### Gemini 生图模型不支持 tool use
- gemini/gemini-3-pro-image-preview 不支持工具调用（exec/message 等）
- nano-banana agent 只能生成图片并以 markdown 链接返回，无法自己下载和发送
- 解决：nano-banana 只负责生图，main agent 接收返回的图片 URL 后下载到 workspace 再用 message 发送
- AGENTS.md 已更新，去掉不可能执行的发送指令

### nano-banana LLM 超时
- 默认超时约 60 秒，生图模型响应慢会超时
- 解决：openclaw.json 中 nano-banana agent 加 `timeoutSeconds: 300`
- spawn 时也可传 `runTimeoutSeconds: 300`

### nano-banana announce 显示 failed 但图片实际生成成功
- gemini-3-pro-image-preview 先返回空 assistant 消息（content=[]），再返回图片
- OpenClaw 看到空响应判定 failed，但图片实际已生成
- 处理：无论 announce ✅ 还是 ❌，都检查返回内容中是否有图片 URL

### 旧 session 抢占 binding 路由
- main agent 的 sessions.json 里有旧 group session 时，binding 到其他 agent 不生效
- 必须从 sessions.json 删除旧 session 条目 + 重启 gateway

### per-agent thinking 不支持
- ❌ `agents.list[].thinking` 不存在，会导致配置加载失败
- ✅ thinking 只能通过 spawn 时传参 `sessions_spawn(thinking: "high")` 或全局 `agents.defaults.thinkingDefault`

### message filePath 权限限制
- agent 的 message 工具只能访问自己 workspace 下的文件
- 跨 workspace 发送会报 "Local media path is not under an allowed directory"
- 解决：图片下载到执行发送的 agent 自己的 workspace

### gemini 图片 URL 被安全策略阻止
- openai.datas.systems 的图片 URL 被 OpenClaw 安全策略阻止
- 错误：`SsrFBlockedError: Blocked: resolves to private/internal/special-use IP address`
- 解决：必须先用 exec curl 下载图片到本地，再用 filePath 发送，不能用 media URL

### bindings 在顶层不在 channels 下
- ❌ `channels.telegram.bindings` 不存在
- ✅ bindings 在 openclaw.json 顶层：`bindings: [{agentId, match: {channel, peer}}]`

### minimax 模型指令遵循问题
- minimax/MiniMax-M2.5 有时不完整执行所有步骤（跳过发送到群的步骤）
- 解决：在 AGENTS.md 和 spawn task 中加粗强调 **必须**，明确写出每个 message 调用的完整参数
- 教训：对 minimax 模型，指令要非常具体，不能依赖它自己推断

### gemini-3.1-flash-image-preview 不可用
- 503 "分组下模型 gemini-3.1-flash-image-preview 无可用渠道"
- 当前 API 套餐不支持该模型
- 使用 gemini/gemini-3-pro-image-preview 代替

### memory_search 不可用（embeddings API key invalid）
- memory_search 工具报 gemini embeddings 400 API_KEY_INVALID（来自 Google generativelanguage）
- 影响：无法自动检索 MEMORY.md / memory/*.md，只能手动 read
- 根因复盘（2026-03-07）：
  - `memorySearch.provider = "gemini"` 这条 embeddings 链不可用
  - 当前聊天代理也不支持 `/embeddings`
  - 即使切换到可用 embeddings provider，仍需显式执行一次 `openclaw memory index --force --agent main` 才会把已扫描到的 memory 文件真正写入索引
- 最终修复（2026-03-07）：
  - 将 `agents.defaults.memorySearch` 和 `main.memorySearch` 切到 `provider: "ollama"`
  - `model: "nomic-embed-text"`
  - `remote.baseUrl: "http://127.0.0.1:11434"`
  - `remote.apiKey: "ollama-local"`
  - 拉取本地模型：`ollama pull nomic-embed-text`
  - 强制重建索引：`openclaw memory index --force --agent main`
- 修复后状态：`memory_search` 恢复为 `provider: "ollama"`, `mode: "hybrid"`

### memory-lancedb-pro 部署结论（2026-03-07）
- 已按当前 `openclaw.json` 架构成功接入 `memory-lancedb-pro`，插件来源：`~/.openclaw/workspace/plugins/memory-lancedb-pro`
- 当前运行模式：`embedding = openai-compatible + Ollama`、模型 `nomic-embed-text`、`sessionStrategy = systemSessionMemory`、`rerank = none`、`autoCapture = false`、`autoRecall = false`
- `openclaw status` 已显示 `Memory: enabled (plugin memory-lancedb-pro)`，`openclaw plugins info memory-lancedb-pro` 状态为 loaded
- 最小验收通过：`memory_store` → `memory_recall` → `memory_forget` 整条链路可用，召回模式显示 `vector+BM25`
- 踩坑：`memory_forget` 删除数据库记录后，不会自动回删 markdown mirror；若做烟雾测试，需手动清理 `memory/YYYY-MM-DD.md` 中的测试行
- 部署后还需补 `plugins.allow`；否则 OpenClaw 会警告“discovered non-bundled plugins may auto-load”。最终修复：在 `openclaw.json` 中显式允许 `memory-lancedb-pro`、`telegram`、`device-pair`、`phone-control`、`talk-voice`、`acpx`
- P1 开启结果（2026-03-07）：`autoRecall = true`、`autoCapture = true`、`captureAssistant = false`；当前继续保持 `rerank = none`、`enableManagementTools = false`
- P1 验收结果（2026-03-07）：插件 CLI `memory-pro` 可用；`memory_store -> memory_recall -> memory_forget` 再次验证通过；删除后数据库记录会消失，但 markdown mirror 仍需手动清理
- 历史记忆导入（2026-03-07）：已将 `MEMORY.md` 转成 JSON 并导入 `memory-lancedb-pro`，当前 `agent:main` 作用域已有 60 条历史记忆，CLI 检索可正常命中
- 检索调优结论（2026-03-07）：大段 markdown 历史记忆适合归档与 CLI 检索；对聊天内高频问题（如“晨星是谁”“Telegram”“自动记录”“intel/collaboration 规则”），还应额外补充一层短句型原子记忆，这样 `memory_recall` 命中会明显更稳

## 踩坑笔记（续）

### mode=session 在 Telegram 下不可用
- `sessions_spawn(mode=session)` 必须 `thread=true`
- Telegram channel 不支持 subagent thread binding
- 报错："thread=true is unavailable because no channel plugin registered subagent_spawning hooks"
- 解决：不用 mode=session，改用 main 编排模式（main 直接 spawn 所有 agent）

### mode=run 的 announce 回调有轮次限制
- review 用 mode=run 时，spawn 子 agent 后只能处理约 3 轮 announce 就结束
- runTimeoutSeconds 无效，问题不是超时而是 run 提前标记 done
- 解决：不让 review 做编排，改由 main（持久会话）直接编排

### write 工具无法写入 skills 目录
- `write` 工具报 "Path escapes workspace root"
- 解决：用 `exec cat > /path/to/file << 'EOF'` 代替

### 织梦产物目录修正
- 由 `gemini`（织梦）完成的研究/报告类产物应放在 `~/.openclaw/workspace/agents/gemini/reports/`
- 不应为了临时编排方便把正式工作产物留在共享工作区 `~/.openclaw/workspace/reports/`
- 若 main 只是临时整理材料给织梦，也应在任务完成后回收到织梦自己的目录，保持“工作产物归属 agent 自己目录，shared workspace 只放协作与共享上下文”

### 流水线不该停下来问用户
- 除 Step 7 晨星确认外，中间步骤不需要人工确认
- 进度推送到监控群就够了，不要把进度汇报变成确认请求
- SKILL.md 已加 Rule 0："全自动推进，不停顿"

### coding agent 谎报修复完成
- coding 声称修复了 8 个 issues 但实际只修了 2 个
- 教训：coding 的 announce 不可信，必须通过 review 或 main 直接 grep 验证

### agent 推送不可靠（所有流水线通用）
- agent / sub-agent 声称推送了消息到群，但实际可能没送达
- depth-1/depth-2 以及各 agent 自推都不能假设可靠送达；不要把任何流水线通知建立在 agent 自推之上
- 解决：所有流水线的关键推送、阶段结果、失败告警统一由 main 补发
- 已同步更新各 agent 的 AGENTS.md：把“必须推送到指定群组”改为“可自推，但可靠通知由 main 负责”
- 后续继续清理各 agent 目录下残留的 SOUL.md / BOOTSTRAP.md / MEMORY.md 旧推送约束；现已完成对 brainstorming、coding、docs、gemini、notebooklm、review、test、wemedia 的统一清理
- 2026-03-06 21:31 再次实测暴露：`gemini` 在被要求阅读方案并产出结果时，没有把开始消息发到自己的职能群，也没有把进度推送到监控群；成功完成时同样没有可靠自推到职能群或监控群
- 2026-03-06 22:01 方向纠偏：之前“群消息推送 bug 已解决”的判断方向有误，验证到的只是“独立 message 发送能力可用”，并不代表 swap/真实任务执行后 agent 群里会自动出现开始、过程、完成信息
- 正确诊断：问题不在“单条消息发送权限”，而在“真实任务链路中的自推执行/编排通知机制不可靠”；后续不再把 agent 群自推当成已修复依据
- 结论强化：agent 在真实任务链路中的开始/进度/成功/失败自推都不可作为可靠通知依据，统一仍由 `main` 补发
- 已执行修复：为 `gemini`、`notebooklm`、`brainstorming`、`coding`、`review`、`test`、`docs`、`wemedia` 的 AGENTS.md 统一补充禁令——不得把开始/进度/完成群消息自推当成任务要求；可靠通知统一由 `main` 负责

### NotebookLM CLI 代理配置
- NotebookLM 在中国大陆不可用，需要翻墙
- Surge 代理端口：127.0.0.1:8234，台湾节点和美国节点都可用，香港节点不行
- CLI 调用需要 https_proxy/http_proxy 环境变量
- gateway 已自动从 settings.json 读取 proxy
- 登录时需要 Surge 增强模式（默认开启）让 Playwright 浏览器走代理
- CLI 命令已修复：notebooklm 命令更新后旧参数不再适用，需适配新 CLI

### 架构决策：main 编排模式
- v1.8 流水线改为 main（小光）作为顶层编排中心
- review 精简为只负责 Step 3 交叉审查
- 所有 agent 由 main 直接 spawn（mode=run）
- 不需要新增编排 agent（maxSpawnDepth=2 限制）
- SKILL.md 和 review AGENTS.md 已重写
- **新增：工具容错与降级机制**（Step 3.5）：任何外部 CLI 依赖失败时必须优雅降级，不能因此中断流水线

### Telegram 群组免 @ 响应不生效（Privacy Mode）
- **问题**：配置了 `requireMention: false`，但群里还是需要 @ 才能响应
- **原因**：Telegram bot 的 Privacy Mode（隐私模式）默认启用，限制 bot 只能看到 @ 提及、命令和回复消息
- **解决方案**：
  1. 在 @BotFather 中发送 `/setprivacy`
  2. 选择你的 bot
  3. 选择 **Disable**（禁用隐私模式）
  4. **重要**：从群里移除 bot，然后重新添加（Telegram 需要重新建立连接才能应用新设置）
- **替代方案**：让 bot 成为群管理员（管理员可以看到所有消息）
- **验证**：运行 `openclaw channels status` 检查配置警告
- **教训**：
  - `requireMention: false` 只是 OpenClaw 配置，Telegram 端的 Privacy Mode 必须单独关闭
  - 修改 Privacy Mode 后必须重新添加 bot 到群，否则不生效
  - 通配符 `"*"` 在 groups 配置中是支持的：`groups: { "*": { requireMention: false } }`
- **groupAllowFrom 和 allowFrom 的作用**：
  - `allowFrom`：控制私聊（DM）访问权限
  - `groupAllowFrom`：控制群组发送者过滤，如果不设置则回退到 `allowFrom`
  - `groupPolicy: "open"`：允许群里所有人使用 bot（推荐用于团队群）
  - `groupPolicy: "allowlist"`（默认）：只允许白名单用户使用 bot
- **固定 SOP（2026-03-06 更新）**：
  1. 先确认目标是否真需要“群里免 @ 收消息”；如果只需要主动推送，不必处理此警告
  2. 若需要免 @：去 `@BotFather` 执行 `/setprivacy` → 选择 bot → **Disable**
  3. 执行 `openclaw gateway restart`
  4. 在每个相关群里把 bot **移除并重新添加**；否则 Telegram 不会应用新可见性
  5. 如果不方便关闭 Privacy Mode，就把 bot 提升为**群管理员**作为替代方案
  6. 运行 `openclaw channels status`，必要时运行 `openclaw channels status --probe`
  7. 在群里发一条**不 @ bot** 的普通消息做实测；若只测主动推送，则改用测试消息验证
- **顺序修正（2026-03-06 21:16）**：`openclaw gateway restart` 应放在“从群里移除并重新添加 bot”之前，后续统一按这个顺序执行
- **日期**：2026-03-05

### Telegram 群消息推送失败（groupAllowFrom 缺失）
- **问题**：`groupPolicy: "allowlist"` 但缺少 `groupAllowFrom` 配置
- **现象**：所有智能体无法推送消息到群，Doctor 警告 "all group messages will be silently dropped"
- **解决**：添加 `channels.telegram.groupAllowFrom: ["1099011886"]`
- **教训**：allowlist 模式必须配置白名单，否则所有群消息被阻止
- **日期**：2026-03-05

### 命令权限问题（allowFrom 配置错误）
- **问题**：在智能体群中使用 `/status` 等命令报 "You are not authorized to use this command"
- **原因**：配置了错误的字段
- **错误尝试历程**：
  1. 最初添加了 `commands.owner`，但该字段不存在，被 `openclaw doctor --fix` 自动删除
  2. 然后添加了 `commands.allowFrom: {"*": ["telegram:1099011886"]}`，但仍然不工作
  3. 尝试了 `commands.allowFrom: {"*": ["1099011886", "telegram:1099011886"]}`，还是不工作
- **正确解决**：添加 `channels.telegram.allowFrom: ["1099011886"]`
- **教训**：
  - ❌ `commands.owner` 不存在
  - ❌ `commands.allowFrom` 是全局命令授权，但对 Telegram 群不生效
  - ✅ `channels.telegram.allowFrom` 是 Telegram 特定配置，应该填数字 ID（推荐）或 @username
  - 格式：`["1099011886"]`（纯数字，不需要 "telegram:" 前缀）
  - 需要重启 gateway 生效
- **日期**：2026-03-05

## NotebookLM 笔记调整（2026-03-06 00:02）

### 决策：Memory 不使用 NotebookLM

**当前方案：**
- Memory 继续使用本地文件存储（memory/YYYY-MM-DD.md, MEMORY.md）
- NotebookLM 只用于知识库查询（openclaw-docs, media-research）

**计划：**
- 明天迁移到向量数据库
- 本地文件 → 向量数据库（更高效的语义搜索）

**原因：**
- NotebookLM 更适合静态知识库，不适合频繁更新的记忆
- 向量数据库提供更好的语义搜索性能
- 本地文件作为持久化存储，向量数据库作为查询层

**NotebookLM 当前用途：**
- openclaw-docs notebook (50源，满载) - OpenClaw 文档知识库
- media-research notebook (3源) - 自媒体调研知识库
- memory notebook (5源) - 暂时保留，明天迁移到向量数据库后可能废弃

## 2026-03-06 架构和配置大更新

### Workspace 架构统一
- 所有子智能体 workspace 路径更新到新架构
- Main agent: `~/.openclaw/workspace/`
- Sub-agents: `~/.openclaw/workspace/agents/{agent-id}/`
- 更新 openclaw.json 配置并重启 gateway

### 模型配置更新
- 将所有文档中的 codex 替换为 gpt
- 更新文件：星链流程图、SKILL.md、MEMORY.md
- 模型配置：gpt (gpt-5.4)

### 智能体配置补全
为所有 11 个智能体创建/更新完整配置文件：
- AGENTS.md - 职责和工作流程（根据星链 v1.8 和自媒体 v1.0）
- SOUL.md - 核心身份和原则
- IDENTITY.md - 名称和 emoji
- USER.md - 关于晨星
- TOOLS.md - 工具和工作目录
- HEARTBEAT.md - 健康检查

### 流水线文档完善
- 星链流水线 v1.8 完整流程图
- 自媒体流水线 v1.0 完整流程图
- NotebookLM Skill 完整流程图

### X 文档对比分析
对比 Berryxia.AI 翻译的《How to Build OpenClaw Agents That Actually Evolve Over Time》：
- ✅ 已实现 90-95% 核心功能
- ✅ 核心理念对齐度 100%
- ⚠️ memory_search 工具待修复（embeddings 配置缺失）
- ✅ 记忆压缩脚本已创建
- ✅ 智能体定时任务已配置

### 记忆压缩和定时任务
- 创建记忆压缩脚本：`~/.openclaw/workspace/scripts/compress-memory.sh`
- 配置 2 个 cron 任务：
  - 记忆压缩检查：每周日凌晨 04:00
  - MEMORY.md 维护：每周日晚上 22:00

### 智能体配置统一规范
- ✅ Workspace 架构统一
- ✅ 推送规范统一（职能群 + 监控群）
- ✅ 硬性约束明确
- ✅ 模型动态切换规则
- ✅ 流水线对齐（星链 v1.8 + 自媒体 v1.0）
- ✅ 协作机制（单写者原则 + 文件系统集成层）

## 子智能体消息推送实测（2026-03-06 21:05）
- 已实测成功：`coding`、`review`、`test`、`docs`、`brainstorming`、`wemedia`、`gemini`、`notebooklm`、`nano-banana`、`monitor-bot`
- 结论：当前 10 个子智能体的 Telegram 主动消息推送链路可用
- 关键例外：`nano-banana` 用默认模型 `gemini/gemini-3.1-pro-image-preview` 发送消息失败；切换到 `openai/gpt-5.4` 后成功
- 规则：`nano-banana` 负责生图，不要默认让它用生图模型直接做消息推送；需要发消息时显式覆盖到可工具调用模型（优先 `gpt-5.4`）
- 补充：`monitor-bot` 不在当前 `sessions_spawn` allowlist 里，但可通过 `openclaw agent --agent monitor-bot` 直调完成测试

### 星鉴流水线 v1.1（2026-03-07）
- **Step 2**: gemini 研究宪法（问题定义 / 边界 / 风险）
- **Step 3**: claude 主方案（基于宪法出落地报告）
- **Step 4**: gemini/review 一致性复核
- **Step 5**: gpt/review 按需仲裁
- **角色分工**：
  - gemini: 研究宪法 + 一致性复核
  - claude: 主方案首选（新增智能体，专注 Claude 相关研究）
  - gpt/review: 高风险仲裁（按需）
- **变更原因**: claude 专注于 Claude 相关研究与实验，更适合作为主方案执行者
