# HEARTBEAT.md - 自愈检查清单

## 健康检查（每次心跳时运行）

### 浏览器状态
检查 OpenClaw 托管浏览器是否在运行：
```bash
openclaw browser status
```
如果 `running: false`，启动它：
```bash
openclaw browser start
```

### 本地 rerank sidecar
检查本地记忆重排服务是否在线：
```bash
curl -s http://127.0.0.1:8765/health
```
如果健康检查失败，检查 launchd 服务状态：
```bash
launchctl list | grep rerank
```

### 定时任务监控
检查关键任务的 `lastRunAtMs` 是否超时（>26 小时）：
```bash
openclaw cron list
```

需要监控的任务：
- starchain 相关任务
- wemedia 相关任务
- NotebookLM 健康检查和文档刷新

如果超时，通过 CLI 强制触发：
```bash
openclaw cron trigger <task-id>
```

### 记忆维护
每周一次（周日晚上）：
1. 回顾本周 `memory/YYYY-MM-DD.md` 文件
2. 提取重要内容到 `MEMORY.md`
3. 压缩或归档超过 40k tokens 的日志
4. 更新 `shared-context/THESIS.md` 的进度

### 文件系统检查
确保关键目录存在：
- `shared-context/` (THESIS.md, FEEDBACK-LOG.md, SIGNALS.md)
- `intel/` (agent 协作文件)
- `memory/` (每日日志)

### TODO 跟进
检查 `~/.openclaw/todo/` 目录下的活跃任务：
```bash
find ~/.openclaw/todo/ -name "*.md" -mtime -7 -type f
```

**检查规则**：
- 如果有标记为"立即执行（今天）"且未完成的项 → 提醒晨星
- 如果有"本周执行"项接近周末且未完成 → 提醒晨星
- 如果有"观察期"任务需要验证 → 提醒晨星

**报告格式**（简洁）：
```
📋 TODO 提醒：<任务名>
⏰ Deadline: <时间>
📊 当前状态: <简述>
```

**同步机制**：
- 主执行计划：`~/.openclaw/todo/master-execution-plan.md`（统一视图）
- 原 TODO 文件：保持实时同步更新
- **新建 TODO 计划时**：必须立即加入主执行计划，不能遗漏
- **完成任务时**：同时更新主计划和原文件的 `[ ]` → `[x]`
- **原则**：主计划纳入 + 双向同步，确保一致性

**原则**：
- 只在需要时提醒，不产生噪音
- 如果所有 TODO 都在正常推进，回复 HEARTBEAT_OK

---

**故障模式记录：**
- 2026-03-05: 添加此文件，基于 Shubham Saboo 的实践经验
- 2026-03-08: 本地 rerank sidecar 首次接入；launchd plist 初版因 `uv` 路径写错启动失败，修正为实际路径后恢复

**原则：**
- 第一天不需要复杂的监控
- 在第一次遇到故障之后再建立检查
- 你会清楚地知道该监控什么，因为你已经亲身感受过什么会崩
