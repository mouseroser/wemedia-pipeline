# 🎨 自媒体内容流水线 v1.1 — Constitution-First Content Delivery

```
┌─────────────────────────────────────────────────────────┐
│  🌐 Global State                                        │
│  内容级别: S / M / L                                     │
│  修改轮次: R1 / R2 / R3 (max 3)                         │
│  平台: 小红书 / 抖音 / 知乎 / 多平台                      │
│  HALT_TIMEOUT = 10min                                   │
└─────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════
  🗂️ 协作材料规则
═══════════════════════════════════════════════════════════

  - 多 agent 联合工作的非正式产物
    （外部 GitHub 项目、本地镜像、共享分析素材、临时脚本等）
    → 统一放到 `intel/collaboration/`
  - 正式产物
    （报告、审查结论、修复代码、文档交付等）
    → 放各自 agent 目录
  - `intel/` 继续作为协作层，遵守单写者原则

═══════════════════════════════════════════════════════════
  📥 Step 1 — 选题分级 + 平台分析
═══════════════════════════════════════════════════════════

  ☀️ main（小光）/model opus /think high

  1. 📋 判断内容类型 → S / M / L
  2. 📋 确定目标平台 → 小红书 / 抖音 / 知乎 / 多平台
  3. 📋 确定内容形式 → 图文 / 视频脚本 / 问答 / 种草笔记
  4. 输出选题单 → main 推送 → 自媒体群 + 监控群

       ┌──── S 级 ────┐
       │ ⚡ 快速通道   │────────────────────────────► Step 3
       └──────────────┘

       ┌──── M/L ────┐
       │ 🧭 前置链    │────────────────────────────► Step 2
       └──────────────┘

═══════════════════════════════════════════════════════════
  🧭 Step 2 — Constitution-First 选题前置链（M/L）
  Orchestrator: ☀️ main
═══════════════════════════════════════════════════════════

  核心思想：
    先由 Gemini 对齐“内容问题定义”
    再由 Claude Code 产出内容策略与执行计划
    再由 Gemini 复核是否跑偏
    仅在 L 级 / 高风险 / 明显分歧时启用 GPT 做审查/仲裁

  M 级：
    1️⃣ Gemini → 内容颗粒度对齐
       • 目标受众
       • 平台定位
       • 选题角度
       • 风格边界
       • 合规风险
       → 输出「内容宪法」
       → main 推送 → 织梦群 + 监控群

    2️⃣ Claude Code → 内容策略/执行计划
       • 内容结构
       • 论点展开顺序
       • 平台适配策略
       • 素材/证据需求
       → main 推送 → 小克群 + 监控群

    3️⃣ Gemini → 一致性复核
       → 输出：ALIGN / DRIFT / MAJOR_DRIFT
       → main 推送 → 织梦群 + 监控群

       ALIGN ✅      → Step 3
       DRIFT ⚠️      → Claude Code 修订 1 次 → Gemini 再复核
       MAJOR_DRIFT ❌ → 升级 GPT 审核位

  L 级：
    1️⃣ Gemini → 内容宪法
    2️⃣ Claude Code → 内容策略/执行计划
    3️⃣ Gemini → 一致性复核
    4️⃣ GPT → 风险挑刺 / 反方审查 / 仲裁
       → 输出：GO / REVISE / BLOCK
       → main 推送 → 小曼群 + 监控群

       GO ✅      → Step 3
       REVISE ⚠️  → Claude Code 修订 1 次 → Gemini 复核
       BLOCK ❌   → HALT / 通知晨星

  规则：
    - 🚫 不新增晨星中途确认节点
    - ✅ Step 2 只升级前置策划层，不替换后续创作 / 审查 / 适配主干

═══════════════════════════════════════════════════════════
  ✍️ Step 3 — 内容创作
  Executor: ✍️ wemedia /thinking high
  Orchestrator: ☀️ main
═══════════════════════════════════════════════════════════

  输入：
    • 选题
    • 内容宪法
    • 内容计划
    • 平台模板
    • NotebookLM 知识补充（如有）

  创作任务：
    1. 文案正文 → drafts/draft.md
    2. 配图提示词 → drafts/prompts.md（如需生图）

  📋 → main 推送 → 自媒体群 + 监控群

═══════════════════════════════════════════════════════════
  🔍 Step 4 — 内容审查（S 级可轻量）
  Executor: 🧵 织梦(gemini)
  Orchestrator: ☀️ main
═══════════════════════════════════════════════════════════

  审查任务：
    • 内容质量评分（1-10）
    • 平台合规检查
    • SEO / 标题 / 标签建议
    • 吸引力与可读性评估
    • 是否偏离内容宪法

  输出 verdict：
    ✅ PUBLISH
    ⚠️ REVISE
    ❌ REJECT

  PUBLISH → Step 5
  REVISE  → Step 4.5
  REJECT  → HALT + 通知晨星

  📋 → main 推送 → 织梦群 + 监控群

═══════════════════════════════════════════════════════════
  🔧 Step 4.5 — 修改循环（max 3 rounds）
  Orchestrator: ☀️ main
  Executor: ✍️ wemedia
  Reviewer: 🧵 gemini
═══════════════════════════════════════════════════════════

  每轮：
    1. wemedia 修改
    2. gemini 复审

  轮次：
    R1 / R2 → 常规修改
    R3 仍 REVISE → PUBLISH_WITH_NOTES
       • 自动生成审阅要点摘要
       • 高亮未完全解决的问题

  任意轮次 REJECT → HALT

═══════════════════════════════════════════════════════════
  🎨 Step 5 — 配图生成（可选）
  Executor: 🪸 notebooklm
  Orchestrator: ☀️ main
═══════════════════════════════════════════════════════════

  使用 NotebookLM generate infographic 命令（square 方向，bento-grid 风格）
  保存路径：`intel/collaboration/media/wemedia/drafts/generated/{A|B|C}/{文章标识}_infographic_sq.jpg`
  命令示例：
    notebooklm generate infographic --orientation square --style bento-grid \
      --detail detailed --language zh_Hans "内容摘要"
    notebooklm download infographic <task-id> --artifact <artifact-id> --force \
      --output intel/collaboration/media/wemedia/drafts/generated/{A|B|C}/{文章标识}_infographic_sq.jpg

  无配图需求 → 跳过

  📋 → main 推送 → 自媒体群 + 监控群

═══════════════════════════════════════════════════════════
  🎭 Step 5.5 — 衍生内容生成（L 级推荐）
  Executor: 🪸 notebooklm
  Orchestrator: ☀️ main
═══════════════════════════════════════════════════════════

  珊瑚按内容特征推荐并生成：
    • podcast
    • mind-map
    • quiz
    • infographic

  📋 → main 推送 → 自媒体群 + 监控群

═══════════════════════════════════════════════════════════
  📱 Step 6 — 多平台适配 + 排期
  Executor: ✍️ wemedia /thinking high
  Orchestrator: ☀️ main
═══════════════════════════════════════════════════════════

  任务：
    • 生成各平台版本
    • 调整字数 / 标签 / 排版
    • 更新 content-calendar
    • 给出发布时间建议

  📋 → main 推送 → 自媒体群 + 监控群

═══════════════════════════════════════════════════════════
  📦 Step 7 — 晨星确认 + 交付
  Executor: ☀️ main
═══════════════════════════════════════════════════════════

  交付摘要必须包含：
    ✅ 选题 + 目标平台
    🧭 内容宪法 / 内容计划摘要
    📊 审查评分 + 状态
    📱 各平台版本预览
    🎨 配图 / 衍生内容（如有）
    🗓️ 建议发布时间

  → 自媒体群 (-5146160953)
  → 监控群 (-5131273722)
  → 晨星 (1099011886)

  ⛔ 未经晨星确认，绝不发布到外部平台

  ✅ 晨星确认后 → main 调用 media-tools 发布：

    1. 读取 wemedia 交付内容（`drafts/{A|B|C}/{标识}.txt`）
    2. 读取配图路径（如有）
    3. 拼装 publish_pipeline 命令
       ```bash
       cd ~/.openclaw/skills/media-tools
       python3 scripts/publish_pipeline.py \
         --title "标题" \
         --content "正文" \
         --image-urls "配图路径" \
         --headless
       ```
    4. 发布成功后更新 HOT-QUEUE.md 状态为 ✅ 已发布
    5. 记录帖子 ID 到监控群通知

═══════════════════════════════════════════════════════════
  📦 Step 7.5 — main 调用 media-tools 发布
  Executor: ☀️ main
═══════════════════════════════════════════════════════════

  main 从 wemedia 交付物读取：
    • 标题（≤20字）
    • 正文（≤1000字）
    • 标签（≤10个）
    • 配图路径

  执行发布（调用 media-tools）：
    ```bash
    cd ~/.openclaw/skills/media-tools
    python3 scripts/publish_pipeline.py \
      --title "..." --content "..." \
      --image-urls "..." \
      --headless
    ```

  收尾动作：
    • 更新 HOT-QUEUE.md 状态 → ✅ 已发布
    • 记录帖子 ID → 监控群通知
    • 触发 Step 8 日结（如需要）

  失败降级：
    • CDP 报错 → 降级为手动发布（晨星介入）
    • 配图失败 → 询问晨星是否跳过配图继续发布

═══════════════════════════════════════════════════════════
  🏁 END
═══════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════
  📢 Push Rules
═══════════════════════════════════════════════════════════

  默认原则：
    • sub-agent：静默执行，结果返回 main，不自行推群
    • main：唯一可靠通知节点，向职能群 + 监控群双推
    • 原因：sessions_spawn 创建 isolated session，无法推送 Telegram 群消息

  完成通知要求：
    • 方案类 / 调研类 / 审查类任务完成时不得只发 done
    • 必须附带摘要 / 结论 / 下一步

═══════════════════════════════════════════════════════════
```
