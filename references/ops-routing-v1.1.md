# 自媒体运营系统 v1.1 — 执行路由参考

## 当前激活范围

- 当前激活平台：**小红书、抖音**
- 知乎模板保留，但默认不启动
- 主搜索策略：**Gemini 搜索优先**
- 正文抓取：`web_fetch`
- 复杂页面兜底：`browser`
- Brave Search API：暂不作为当前必需前置，仅在结构化批量搜索成为瓶颈时再引入

## 运营层总览

### Step 0：持续研究层
- gemini 负责早 / 午 / 晚三次扫描
- 产出：
  - `intel/media-tools/DAILY-SIGNAL-BRIEF.md`
  - `intel/media-tools/HOT-SCAN-INBOX.md`

### Step 1：内容队列层
- main 从收件箱拣选候选
- 维护：
  - `HOT-QUEUE.md`
  - `EVERGREEN-QUEUE.md`
  - `SERIES-QUEUE.md`
- 状态：`待评估` → `已排期` → `创作中` → `审查中` → `待确认` → `已发布` / `已弃用`

### Step 1.5：Publishability Gate
main 判断：
- 今天值不值得发
- 为什么值得 / 不值得
- 不发损失什么
- 是否进入生产

### Step 2：Constitution-First 前置链
- gemini：内容颗粒度对齐 / 热点判断 / 受众与标题方向
- GPT / OpenAI：宪法边界（must / must-not、表达边界、不可夸大点、风险边界）
- Claude Code：内容策略 / 执行计划
- gemini：一致性复核
- GPT：仅在高风险 / 明显分歧时继续做挑刺与仲裁
- **NLM 知识查询（必做，M/L 级）**：基于 media-tools 的 media-research notebook 查询竞品和行业数据，补充差异化角度
  ```bash
  bash ~/.openclaw/skills/notebooklm/scripts/nlm-gateway.sh query \
    --agent main --notebook media-research \
    --query "基于竞品数据和行业趋势，{选题}的差异化角度是什么？有哪些爆款因素可以参考？"
  ```
  > 来源：media-tools 维护的 `media-research` notebook（`~/.openclaw/skills/notebooklm/scripts/nlm-gateway.sh`）
  > 频率：M/L 级内容必须查询，S 级跳过（时效优先）

### Step 3：内容创作
- wemedia 产出主稿和配图提示词
- 默认先适配小红书

### Step 4：内容审查
- gemini 做质量 / 合规 / SEO / 偏题审查
- verdict：`PUBLISH` / `REVISE` / `REJECT`

### Step 4.5：修改循环
- 最多 3 轮
- R3 后仍不理想 → `PUBLISH_WITH_NOTES`
- 任意轮 `REJECT` → HALT

### Step 5：配图生成（NotebookLM 路线）✅
- 使用 NotebookLM CLI 生成信息图（**首选路线**）
- 生成后下载到 `intel/collaboration/media/wemedia/drafts/generated/{A|B|C}/`
- ~~nano-banana 作为备选~~（已废弃，统一使用 NotebookLM）

**NotebookLM 信息图生成标准命令**：
```bash
notebooklm use <notebook-id>                    # 切换 notebook
notebooklm source add <article.txt>             # 添加正文 source
notebooklm generate infographic \
  --orientation square \
  --style bento-grid \
  --detail detailed \
  --language zh_Hans \
  "自定义 prompt，描述图片应包含的内容"   # 生成
notebooklm artifact poll <task-id>               # 等待完成
notebooklm download infographic <task-id> \
  --artifact <artifact-id> --force              # 下载
```
- `--orientation square`：1:1 正方形（小红书最佳）
- `--style bento-grid`：信息图风格
- `--language zh_Hans`：简体中文
- 下载后用 Python PIL 裁剪黑边，保存为 JPEG（quality=95）
- 图片路径约定：`intel/collaboration/media/wemedia/drafts/generated/{A|B|C}/{文章名}_infographic_sq.jpg`

**NotebookLM 语言代码**：`zh_Hans`（简体中文）/ `zh_Hant`（繁体中文）

### Step 5.5：衍生内容（其他格式，L 级优先）
- notebooklm 生成 podcast / mind-map / quiz 等（非信息图类）
- infographic 已归入 Step 5

### Step 6：平台适配 + 排期
- 当前默认输出 `xiaohongshu.md`
- 仅在晨星明确要求时再生成 `douyin.md` / `zhihu.md`

### Step 7：晨星确认（wemedia → sessions_send → main → 晨星 DM）
- **wemedia**：Step 6 完成后，`sessions_send(sessionKey="agent:main:main", message="Step 6 完成 [{内容ID}] 等待 Step 7 确认\n标题：{标题}\n配图：{路径}\n发布包：{路径}")` 回 main
- **main**：收到后 DM 晨星确认
- **晨星确认后**：main `sessions_send(label="wemedia-pipeline", message="Step 7 确认：{内容ID} 已授权发布")` 放行
- 未经晨星确认绝不外发

### Step 7.5：wemedia 收到放行指令后执行平台发布
- wemedia 在 persistent session 收到 main 的 Step 7 放行指令后，自行执行发布
- 按平台选择执行工具：
  - 小红书：调用 `xiaohongshu/scripts/publish_pipeline.py`
  - 抖音：调用 `douyin/scripts/publish_douyin.py`
- 发布完成后 `sessions_send(sessionKey="agent:main:main", message="Step 7.5 完成 [{内容ID}]\n状态：{成功/失败}\n{详情}")` 回传 main
- **main**：收到后更新 HOT-QUEUE.md 状态，补推监控群，DM 晨星最终结果
- 失败：wemedia sessions_send 回 main 标注 BLOCKED，main 通知晨星介入

### Step 8：日结 / 周复盘
- main 记录当天运营结论和后续动作

## 分级路由

- **S 级**：Step 1.5 → **Step 2A + Step 2B**（跳过 2C/2D）→ Step 3 → Step 4 → Step 5 → Step 6 → Step 7 → **Step 7.5** → Step 8
- **M 级**：Step 1.5 → Step 2（2A+2B+2C+2D 全走）→ Step 3 → Step 4 → Step 5 → Step 6 → Step 7 → **Step 7.5** → Step 8
- **L 级**：Step 1.5 → Step 2（全四步 + GPT 仲裁）→ Step 3 → Step 4 → Step 5 → Step 5.5（衍生评估）→ Step 6 → Step 7 → **Step 7.5** → Step 8

### S级与M级在 Step 2 的差异

| 子步骤 | M/L级 | S级 | 理由 |
|---|---|---|---|
| 2A 颗粒度对齐 | ✅ spawn gemini | ✅ spawn gemini | 方向不对后面全错，不可省 |
| 2B 宪法边界 | ✅ spawn openai | ✅ spawn openai | 质量底线，没有安全网不发 |
| 2C 内容计划 | ✅ spawn claude | ❌ 跳过 | S级选题成熟，叙事结构 wemedia 自己拿捏 |
| 2D 一致性复核 | ✅ spawn gemini | ❌ 跳过 | 只有 2A+2B 时无需额外对齐 |

### S级使用条件（必须同时满足）
1. 同类选题已发过至少 2 条，有成熟范本可复用
2. 无新风险点、无敏感边界
3. 叙事结构固化（如工具测评、数据解读等固定体裁）

> S级不是「省事」，而是「在已验证的轨道上复用」。未满足上述条件的选题，一律升级为M级走完整链路。

说明：
- Step 0 / Step 1 属于持续运营层，通常在生产前已完成
- 若 Publishability Gate 不通过，可停留在队列层，不强行产出
- NLM 知识查询：M/L级必须做，S级跳过（时效优先）

## 推送与通知

- main 的通知是可靠主链路
- sub-agent 自推仅 best-effort，不能视为可靠送达
- 关键结果、失败、HALT、交付摘要必须由 main 保证可见
- main 调 `message(action="send")` 时，单发只用 `target`；不要把多个群写进 `targets`
- 若要同时发多个群，按单目标串行发送多次；`targets` 仅用于 `action="broadcast"`

## 容错规则

- 外部依赖失败（如 notebooklm / 搜索 / 认证问题）时：
  1. Warning 到监控群
  2. 降级跳过该环节
  3. 继续推进到下一步
- 绝不因单点工具失败卡死整条内容链

## 何时读哪个 reference

- 需要流程图或节点概览 → `PIPELINE_FLOWCHART_V1_1_EMOJI.md`
- 需要旧版 v1.1 合约细节 → `pipeline-wemedia-v1.1-contract.md`
- 需要当前运营系统执行路由 → **本文件**
