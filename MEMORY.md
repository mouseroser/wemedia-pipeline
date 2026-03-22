# MEMORY.md - 小光的长期记忆

> 精简版 (2026-03-22 22:00)。完整历史备份：`memory/archive/MEMORY-2026-03-14-before.md`
> 踩坑笔记完整版已存入 memory-lancedb-pro 向量数据库，按需召回。

---

## ⚠️ 血泪教训（永不重犯）

1. **Review 不做编排**：review 只负责审查，所有编排由 main 负责。mode=run 的 announce 有轮次限制。
2. **Agent 自推不可靠**：关键通知必须由 main 补发，不能依赖 sub-agent 自推到群。
3. **Coding 结果不可信**：coding 的 announce 不可信，必须通过 review 或 main 直接验证。
4. **memory-lancedb-pro 升级回归**：升级会覆盖本地补丁（`resolveRuntimeAgentId(...) || 'main'`），每次升级后必须检查 `memory_stats`/`memory_list` 是否正常。修复后需完整 `openclaw gateway restart`。
5. **AI 生成的脚本必须当场验证**：先 `openclaw <cmd> --help` 确认子命令存在，不要盲目信任 agent 生成的 CLI 命令。
6. **Cron isolated session 不查记忆**：prompt 里写死的路径必须经过验证；需要调用 memory 工具的任务不写 shell 脚本，用 agentTurn 直接调工具。
7. **三件套记录缺一不可**：完成重要工作后必须同时更新 (1) memory/YYYY-MM-DD.md (2) memory_store (3) .learnings/ERRORS.md（如有错误），不需要晨星提醒。
8. **小红书发布前必检 checklist**：标题 ≤20 字 / 标签 ≤10 个 / 先 content-data 检查是否已有同标题笔记（防重复发布）/ 配图 1:1 方图。
9. **MiniMax 禁止用于发布/创作**：minimax 模型禁止用于小红书发布、CDP 自动化、多步骤外部操作、wemedia 创作。必须用 Opus 或 Sonnet。
10. **卡点处理：最多重试 2 次就切方向**：遇到链路不通（如下载不落盘），最多重试 2 次，第 3 次必须切换方向，禁止停在解释/等待上。
11. **执行前必须查记忆**：发布/生图/多步骤任务执行前，先 `memory_recall` 查已知坑。
12. **多步骤任务必发 4 类通知**：开始 / 关键进度 / 错误阻塞 / 完成结果 — 不能只在后台执行。
13. **旧 PR 基于过时分支时直接重建**：不要继续修脏 diff，基于 upstream 默认分支重建干净 PR。
14. **重命名目录后必须 grep 内部引用**：否则路径全断。
15. **小红书 CDP 发布频率限制**（2026-03-22 确立）：单日≤3篇、间隔≥3小时、申诉期间暂停；main 有最高权力制止发布。

---

## ❌ 错误示范 → 正确做法

| 错误 | 正确 |
|------|------|
| 让 review 编排其他 agent | main 直接编排所有 agent |
| 依赖 agent 自推到群 | main 统一补发到监控群 |
| browser 访问 GitHub | 先 `git clone` 到本地 |
| 改配置后 gateway reload | 必须 `openclaw gateway restart` |
| 只配 OpenClaw requireMention | 同时关 Telegram Privacy Mode |
| skills 放 workspace 下 | 放 `~/.openclaw/skills/` |
| TODO 放 workspace 下 | 放 `~/.openclaw/todo/` |
| 说"要我...吗？" | 知道规则就直接执行 |
| 发现问题先报告等指令 | 发现问题立即修复再报告 |
| 用 openai SDK 当 HTTP 客户端 | 用原生 fetch 调本地 Ollama |
| minimax 跑复杂 cron 任务 | minimax 只跑脚本型，复杂判断用 Sonnet/Opus |
| 修改 plugins/*.ts 后直接重启 | 先 `rm -rf /tmp/jiti/` 再重启 |
| minimax 做小红书发布/创作 | 必须用 Opus 或 Sonnet |
| 截图落盘当配图 | 下载原图（或 NotebookLM CLI 生图） |
| 卡住了停在解释 | 自主切换到解决动作 |
| profile=openclaw 下载文件 | 用 profile="user" 连本机 Chrome |
| 用 Gemini 网页生图下载 | 优先 NotebookLM infographic CLI（绕过下载问题） |
| 连发小红书间隔 <1min | 发布间隔 ≥30 分钟（防限流） |

---

## 晨星的核心偏好

- **沟通**：简洁有力，默认执行不反复确认
- **记录**：遇到问题/修复后立即主动记录
- **原则**：每个 agent 只做本职、不走捷径、同一问题连续三次未解决必须切换方向
- **语言**：晨星↔小光中文，对外协作按仓库语境定
- **通知**：所有流水线必须有通知，Agent 自推职能群 + main 补发监控群
- **模型分工**：操作类任务（浏览器/发布/编辑/图片替换）默认 GPT；策略/编排 Opus；轻量 MiniMax
- **文档查询**：默认不读本地 docs 文件（太浪费 tokens），优先使用 NotebookLM 笔记检索
- **执行风格**：遇障碍自主解决而非停顿解释；生图结果立刻推群；下载链路第一张图就验证完整性

---

## 关于晨星

- 陈颖，时区 Asia/Shanghai，Telegram ID: 1099011886

---

## Telegram 群组

| Agent | 称呼 | Chat ID |
|-------|------|---------|
| main | 小光 | DM |
| monitor-bot | - | -5131273722 |
| docs | - | -5095976145 |
| test | - | -5245840611 |
| review | - | -5242448266 |
| coding | - | -5039283416 |
| brainstorming | - | -5231604684 |
| wemedia | - | -5146160953 |
| nanobanana | - | -5217509070 |
| gemini | 织梦 | -5264626153 |
| notebooklm | 珊瑚 | -5202217379 |
| claude | 小克 | -5101947063 |
| openai | 小曼 | -5242027093 |

---

## 模型配置

- 默认：anthropic/claude-opus-4-6
- coding: gpt-5.4 | review/test/brainstorming: sonnet | docs/monitor-bot: minimax
- 织梦: gemini-preview | 珊瑚: opus | 小克: opus | 小曼: gpt-5.4
- MiniMax：国内版 api.minimaxi.com（2026-03-20 从国际版切换）

---

## 流水线概要

### 星链 v2.8
- Main 直接编排，Review 只做审查
- 全自动推进（Rule 0），除 Step 7 晨星确认外不停顿
- 打磨层（Step 1.5）：NotebookLM(1.5B)→OpenAI(1.5C)→Claude(1.5D)→Gemini(1.5E) 证据驱动
- Brainstorming 动态模型：L1/L2 用 sonnet，L3 用 opus，关键决策始终 opus
- Spawn 失败自动重试 3 次
- 禁止 isolated session 编排（必须 Main 主会话直接 spawn 各 agent）

### 自媒体 v1.1 + 24/7 运营系统
- 选题分级(S/M/L) → Constitution-First → 创作 → 审查 → 生图 → 适配 → 交付
- ⛔ Step 7：未经晨星确认绝不发布
- **运营系统升级（2026-03-18）**：
  - Step 0 持续研究层（早/午/晚三段 Gemini 扫描）
  - Step 1 内容队列（HOT-QUEUE / EVERGREEN-QUEUE / SERIES-QUEUE）
  - Step 1.5 Publishability Gate（值不值得今天发？）
  - Step 8 日结与周复盘
- **配图方案**：优先 NotebookLM infographic CLI（`--orientation square --style bento-grid --language zh_Hans`），备选 Nanobanana2
- **发布间隔**：≥30 分钟（防小红书限流）
- **小红书内容规律**：大厂冲突感 + 数字锚点 > 纯技术分享；收藏率(5.8%) > 点赞率(3.1%)，实用型开发者受众

### 星鉴 v2.0
- gemini 扫描 → openai 宪法 → notebooklm 研究 → claude 复核 → gemini 一致性 → 仲裁 → docs 定稿

---

## 记忆系统

- **Layer 1**：MEMORY.md + memory/*.md（文件）
- **Layer 2**：memory-lancedb-pro@1.1.0-beta.8 + Ollama bge-m3 + 本地 rerank(bge-reranker-v2-m3:8765)
  - autoRecall=true, autoCapture=true, captureAssistant=true
  - Smart Extraction: openai/gpt-oss-120b（提取→去重→合并，3次LLM调用）
  - Embedding: bge-m3（本地 Ollama，1024维向量）
  - Rerank: bge-reranker-v2-m3（本地 Python sidecar:8765，MPS加速）
  - 噪音过滤已加固（屏蔽系统包络/WhatsApp状态/运营噪音）
- **Layer 3**：NotebookLM（memory-archive + openclaw-docs + troubleshooting）
  - fallback 改为直调 nlm-gateway.sh（绕过 gateway lane lock）
  - timeout: 75 秒（从 45 秒调高，2026-03-17）
  - 专用 runtime worktree: `~/.openclaw/runtime-plugins/memory-lancedb-pro`
- **4F Spec-Kit 优化（2026-03-22）**：
  - 4F.1: 超时 30s→45s+50s 上限
  - 4F.2: 时间感知单次重试
  - 4F.3: L3 结果 3000 字截断
  - 4F.4: JSON 5 层防御解析
  - 4F.5: L3 触发阈值 minScore 0.5→0.35
- **防护**：post-upgrade-guard.sh 每6小时 + 心跳检查
- **维护**：每日日志加载今天+昨天，压缩阈值 40k tokens，周日 04:00 压缩 + 22:00 MEMORY.md 维护

---

## Workspace 架构

- Main: `~/.openclaw/workspace/`
- Sub-agents: `~/.openclaw/workspace/agents/{agent-id}/`
- Skills: `~/.openclaw/skills/`（不是 workspace 下）
- TODO: `~/.openclaw/todo/`（不是 workspace 下）
- Scripts: `~/.openclaw/scripts/`
- 路径索引: `shared-context/PATHS.md`（所有核心路径汇总）
- Cron 总表: `shared-context/CRON-MATRIX.md`
- 协作产物: `workspace/intel/collaboration/`
- TODO 控制面: `~/.openclaw/todo/master-execution-plan.md`（全局 canonical 活跃队列）

---

## 核心规则

1. **流水线更新自动应用**：看到流水线更新立即更新所有相关 agent 配置，不等提醒
2. **插件更新先分析再更新**：查 CHANGELOG → 评估影响 → 制定计划 → 确认后更新
3. **OpenClaw 新版本联动**：晨星说"有新版本"→ 立即更新 openclaw-docs 笔记
4. **优化前先评估收益**：不为"看起来更好"而改动，必须有明确使用场景
5. **使用 Skill 必须完整执行**：阅读所有要求、列出所有文件、逐个更新验证
6. **约定变更后全量迁移**：修改架构/目录约定后，必须同步检查所有引用方并一次性全部迁移
7. **执行纪律**：遇到已知问题/卡点/工具链异常，main 必须自动解决→验证→继续→记录，不等晨星提醒

---

## 上游 PR 跟进

- **PR #206** (feat/layer3-notebooklm-fallback): ❌ 被 maintainer 关闭（E2E 回归 + memory_recall 契约变更）
- **PR #227** (fix/memory-list-main-default): ❌ 被关闭（测试未接入 npm test）
- **4H 上游路线**：暂缓执行。策略保留：PR-A（infra hardening）→ 接口决策 → PR-B（contract-safe fallback），等待合适时机重启

---

## 自媒体运营成果（截至 2026-03-22）

### 小红书账号数据
- 累计发布 18 篇笔记（可见 10 篇）
- 单日最高发布量：12 条（2026-03-22）
- 爆款：「Claude HUD 突破 10K」690 观看 / 12.9% 互动率
- 账号画像：收藏率(5.8%) > 点赞率(3.1%)，典型实用型开发者受众

### 技术基础设施
- 方案 C+：小红书 CDP 9223 + X OpenClaw 内置浏览器 + NLM media-research
- NotebookLM infographic：原生支持 `--orientation square`（2048x2048），全中文，绕过 Gemini 下载问题
- 浏览器策略：停用 profile=openclaw，改用 profile="user" 连本机 Chrome

### 内容规律
- 有效：大厂+冲突感、数字锚点+里程碑、媒体背书+战略叙事、个人视角+对比选择
- 无效：纯技术分享、安全议题（已封存系列）、踩坑类（需重包装为"我的选择"框架）

---

## 本周重大事件（2026-03-16 ~ 2026-03-22）

### NotebookLM infographic 路线打通（03-22）
- CLI 原生支持 `generate infographic --orientation square --style bento-grid --language zh_Hans`
- 全程 CLI，无需浏览器，绕过 Gemini 下载不落盘问题
- 流水线 Step 5 从 nanobanana 改为 NotebookLM

### 4F Spec-Kit 完成（03-22）
- L3 超时/重试/截断/JSON防御/触发阈值 5 项优化全部部署
- 4E 观察期 8 天数据：L2 可用率 80%→87%，L3 从 0% 改善到 67%

### 自媒体 12 篇日产出（03-22）
- 单日 12 条发布（史上最高），包含 Claude HUD 爆款（690 观看/12.9% 互动率）
- 发现连发限流问题（间隔 <1min），建立 ≥30min 间隔规则

### Layer 3 稳定化收口（03-16/17）
- session lock 根因修复（nlm-gateway.sh 直调绕过 lane lock）
- timeout 45→75 秒
- 5 个 NotebookLM cron 脚本全面修复

### Skills 精修（03-18）
- wemedia / todo-manager / notebooklm / starchain 四个 skill 全部对齐当前架构

### 方案 C+ 全链路验证（03-19）
- 小红书 CDP 9223 + X 采集 + NLM media-research 全部打通
- 4 个运营 cron 配置就绪

### web_search 修复（03-22）
- Google API key 过期，切换到 Brave Search（$5/月免费额度）
- 通过 `tools.web.search.apiKey` 配置

---

**最后更新**: 2026-03-22 22:00 (小光 MEMORY.md 维护)
**下次回顾**: 2026-03-29（每周日）
