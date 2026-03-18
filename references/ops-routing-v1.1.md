# 自媒体运营系统 v1.1 — 执行路由参考

## 当前激活范围

- 当前激活平台：**仅小红书**
- 抖音 / 知乎模板保留，但默认不启动
- 主搜索策略：**Gemini 搜索优先**
- 正文抓取：`web_fetch`
- 复杂页面兜底：`browser`
- Brave Search API：暂不作为当前必需前置，仅在结构化批量搜索成为瓶颈时再引入

## 运营层总览

### Step 0：持续研究层
- gemini 负责早 / 午 / 晚三次扫描
- 产出：
  - `intel/media-ops/DAILY-SIGNAL-BRIEF.md`
  - `intel/media-ops/HOT-SCAN-INBOX.md`

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
- Claude Code：内容策略 / 执行计划
- gemini：一致性复核
- GPT：仅 L 级 / 高风险 / 明显分歧时做挑刺与仲裁
- notebooklm：按需补专题知识，不是固定必经

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

### Step 5：配图生成（可选）
- nano-banana 按需生成配图

### Step 5.5：衍生内容（L 级优先）
- notebooklm 推荐并生成 podcast / mind-map / quiz / infographic 等

### Step 6：平台适配 + 排期
- 当前默认输出 `xiaohongshu.md`
- 仅在晨星明确要求时再生成 `douyin.md` / `zhihu.md`

### Step 7：晨星确认
- main 汇总交付
- 未经确认绝不外发

### Step 8：日结 / 周复盘
- main 记录当天运营结论和后续动作

## 分级路由

- **S 级**：Step 1.5 → Step 3 → Step 4（轻审）→ Step 6 → Step 7
- **M 级**：Step 1.5 → Step 2 → Step 3 → Step 4 → Step 6 → Step 7
- **L 级**：Step 1.5 → Step 2（+ GPT 仲裁）→ Step 3 → Step 4 → Step 5.5（按需）→ Step 6 → Step 7

说明：
- Step 0 / Step 1 属于持续运营层，通常在生产前已完成
- 若 Publishability Gate 不通过，可停留在队列层，不强行产出

## 推送与通知

- main 的通知是可靠主链路
- sub-agent 自推仅 best-effort，不能视为可靠送达
- 关键结果、失败、HALT、交付摘要必须由 main 保证可见

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
