# ERRORS.md - 错误日志

## 2026-03-11 00:00 - 流水线 announce 不可靠

**问题**: Main agent 在等待 Gemini Step 4 完成时，虽然 Gemini 已完成并生成报告（23:53），但 main 一直在等待 announce 消息，以为任务还没完成。

**根因**:
1. 子 agent 的 announce 消息可能不会到达 main
2. Main 盲目等待 announce，没有主动检查输出文件
3. 导致流水线卡住，用户体验极差

**影响**: 严重 - 流水线可靠性问题，用户体验极差

**解决方案**:
1. Main 不能盲目等待 announce
2. Spawn 后记录预期输出路径和 spawn 时间
3. 定期检查文件是否存在且时间戳新鲜（< 5 分钟）
4. 如果文件存在，直接读取并推进，不等 announce
5. 如果超过预期时间（如 2x timeout），主动检查并告警

**预防措施**:
- 在 AGENTS.md 中添加"主动检查输出文件"的强制规则
- 在流水线 SKILL.md 中添加文件检查逻辑
- 不要依赖 announce 作为唯一的完成信号

**优先级**: P0 - 必须立即修复

---

## 2026-03-11 00:03 - 流水线重复消息问题

**问题**: Gemini Step 4 的完成消息出现了 2 次：
1. 第一次：Gemini 在 23:53 完成时自己发送
2. 第二次：Announce 延迟 7 分钟后到达，触发重复处理

**根因**:
1. Gemini 执行耗时 7 分 51 秒
2. Main 在 23:53 通过文件检查发现完成，已处理
3. Announce 消息在任务真正结束时才发送（00:00）
4. Main 收到延迟 announce 后，没有去重机制，导致重复处理

**影响**: 中等 - 用户看到重复消息，体验不佳

**解决方案**:
1. Main 维护已完成任务的 session key 集合
2. 收到 announce 时先检查是否已处理
3. 如果已处理，直接 NO_REPLY，不做任何操作
4. 如果未处理，正常处理并记录到集合

**实现方案**:
```python
# 伪代码
completed_sessions = set()

def handle_announce(session_key, result):
    if session_key in completed_sessions:
        return "NO_REPLY"  # 已处理，跳过
    
    # 正常处理
    process_result(result)
    completed_sessions.add(session_key)
```

**预防措施**:
- 在 AGENTS.md 中添加去重机制
- 在流水线 SKILL.md 中添加去重逻辑
- 每次收到 announce 前先检查是否已处理

**优先级**: P1 - 重要但不紧急

---

## 2026-03-11 00:07 - 根本原因确认：announce 是 best-effort

**问题**: 几乎所有子 agent 完成后，announce 消息都没有到达 main。

**根本原因（OpenClaw 官方文档确认）**:
1. ✅ Announce 本身就是 **best-effort**（尽力而为），不保证到达
2. ✅ 文档原话："Sub-agent announce is best-effort. If the gateway restarts, pending announce back work is lost."
3. ✅ `sessions_spawn` 是非阻塞的，立即返回 runId，不等待完成
4. ❌ Main 盲目等待 announce，导致流水线卡住

**真相**:
- 子 agent 的 announce 机制设计上就不保证可靠性
- 不是 bug，是设计特性
- Main 必须完全放弃依赖 announce 作为唯一信号

**唯一可靠的解决方案**:
1. **主动轮询检查输出文件**
2. Spawn 后记录：
   - 预期输出路径
   - Spawn 时间
   - 预期完成时间（timeout）
3. 每 30 秒检查一次：
   - 文件是否存在
   - 文件时间戳是否新鲜（< 2 分钟）
4. 如果文件存在且新鲜：
   - 立即读取
   - 推进到下一步
   - 记录到已完成集合
5. 如果超过 timeout 还没文件：
   - 告警
   - 考虑重试

**实现方案**:
```python
# 伪代码
spawned_tasks = {
    session_key: {
        "output_path": "...",
        "spawn_time": timestamp,
        "timeout": 900,
        "expected_completion": timestamp + 900
    }
}

# 每 30 秒检查一次
while True:
    for session_key, task in spawned_tasks.items():
        if session_key in completed_sessions:
            continue  # 已完成，跳过
        
        # 检查文件
        if file_exists(task["output_path"]):
            file_age = now() - file_mtime(task["output_path"])
            if file_age < 120:  # < 2 分钟
                # 文件新鲜，立即处理
                process_output(task["output_path"])
                completed_sessions.add(session_key)
                continue
        
        # 检查超时
        if now() > task["expected_completion"]:
            alert("Task timeout", session_key)
    
    sleep(30)
```

**预防措施**:
- 在 AGENTS.md 中添加"主动轮询检查"的强制规则
- 在流水线 SKILL.md 中实现轮询逻辑
- 完全放弃依赖 announce
- Announce 只作为"加速通知"，不作为"唯一信号"

**优先级**: P0 - 必须立即修复，这是流水线可靠性的根本

**教训**:
- 不要相信 announce 会到达
- 不要被动等待
- 主动检查是唯一可靠的方案

---


## [ERR-20260311-001]

**Logged**: 2026-03-11T06:36:57.249Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
Misused read/write tools during Step 3 report generation by reading a directory path and repeatedly calling write without required content

### Details
Encountered read EISDIR when attempting to read manuscript directory directly instead of enumerating files first. Then repeatedly triggered write validation errors by omitting the required content field while creating the report file.

### Suggested Action
When target path may be a directory, list files first via exec/find and read specific files. Before any write call, verify required schema fields are present, especially content. After first validation failure, stop retrying identical invalid calls and correct arguments immediately.

### Metadata
- Source: memory-lancedb-pro/self_improvement_log
---


## [ERR-20260313-001]

**Logged**: 2026-03-13T06:39:12.747Z
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
陷入 write 工具调用循环 - 连续忘记提供 content 参数

### Details
在执行星鉴流水线 Step 2B 时，连续多次调用 write 工具但始终忘记提供必需的 content 参数。这是一个严重的执行模式问题，违反了"方向切换规则"。

### Suggested Action
在调用 write 工具前，必须先准备好完整的 content 内容。如果内容很长，应该先在内存中构建，然后一次性写入。

### Metadata
- Source: memory-lancedb-pro/self_improvement_log
---


## [ERR-20260313-002]

**Logged**: 2026-03-13T20:17:47.255Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
sync-high-priority-memories cron script fails because it depends on a missing pre-generated JSON file and manual Telegram intervention

### Details
Ran `bash ~/.openclaw/workspace/scripts/sync-high-priority-memories.sh` at 2026-03-14 04:17 Asia/Shanghai. Script logs that it cannot actually query memory data itself, asks for manual Telegram triggering, then exits with code 1 because `~/.openclaw/workspace/.tmp/high-priority-memories.json` does not exist. Root issue: the automation script is not end-to-end; it does not invoke memory tools directly and therefore cannot fulfill the cron task autonomously.

### Suggested Action
Replace the script/cron flow with a real isolated agentTurn that calls memory tools directly, or rewrite the script to use a supported non-interactive interface for exporting importance >= 0.9 memories before attempting NotebookLM sync.

### Metadata
- Source: memory-lancedb-pro/self_improvement_log
---


## [ERR-20260313-003]

**Logged**: 2026-03-13T22:54:41.242Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
NotebookLM daily query cron was interrupted by SIGTERM during execution

### Details
Cron task notebooklm-daily-query (dd9cb82e-d4b3-4ffa-b8c7-f122ddd23ddf) started and reached Step 2, then exec session gentle-haven was terminated with signal SIGTERM at 2026-03-14 06:52 Asia/Shanghai. This prevented report generation in the main session.

### Suggested Action
Check cron/task timeout or parent session interruption behavior for long-running NotebookLM queries; consider longer timeout or splitting the script into resumable steps.

### Metadata
- Source: memory-lancedb-pro/self_improvement_log
---


## [ERR-20260314-001]

**Logged**: 2026-03-14T00:47:27.766Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
Forced cron rerun of NotebookLM memory sync completed the script successfully but final run status stayed error because a post-run exact edit to memory/2026-03-14.md failed.

### Details
During forced rerun of cron job `NotebookLM 记忆同步` (jobId 39618059-570d-402e-86f8-752891e8e480), the summary showed script success: 77 files synced and latest memory files updated. However run history recorded status=error with `⚠️ 📝 Edit: in ~/.openclaw/workspace/memory/2026-03-14.md (31 chars) failed`. Root pattern: the isolated agent likely tried an exact-text edit against a changing daily memory file after successful core work, causing overall cron status to be marked as error even though the data sync itself succeeded.

### Suggested Action
For cron agents that log results into daily memory files, prefer append/write-safe logging instead of exact-text edit against volatile files. Separate core task success from optional logging so post-run log-write failures do not poison overall cron status.

### Metadata
- Source: memory-lancedb-pro/self_improvement_log
---


---

## 2026-03-14 16:18 - builtin memorySearch 被 memory/archive 超长文件拖垮

**问题**: 使用 `openclaw memory search` 测 builtin memorySearch 时，搜索反复出现 rate limit 重试，随后报错：
- `Ollama embeddings HTTP 500: {"error":"the input length exceeds the context length"}`
- `sync failed (session-start)`
- `sync failed (search)`

部分长命令因此长时间无有效输出，最终只能手动终止进程（SIGTERM）。

**根因**:
1. builtin memorySearch 默认索引 `MEMORY.md` + `memory/**/*.md`
2. 当前 `memory/archive/` 目录仍位于默认索引范围内
3. 归档目录中存在超大 markdown 文件（如 notebooklm-daily 395KB / 256KB）
4. 这些超长文件在 builtin sync / embedding 阶段触发 Ollama context length 错误

**影响**:
- builtin memorySearch 当前不适合公平 benchmark
- `openclaw memory search` 结果会失真（No matches / sync failed / 卡住）
- 误导人以为是排序质量问题，实际上先是索引范围冲突问题

**解决方案**:
1. 先把 builtin memorySearch 视为影子线，不作为正式主检索评估对象
2. 在 archive 冲突未解决前，不应用 builtin 的 hybrid / MMR / temporalDecay / sessionMemory 增强配置
3. 如果后续要认真评估 builtin：
   - 先决定是否执行 archive 架构迁移
   - 再做 reindex / warm-up / benchmark

**预防措施**:
- 大型归档文件不要默认留在 builtin memorySearch 的索引范围内
- 评估 builtin 前先检查 `openclaw memory status --deep` + 实测 search 是否稳定
- 先排“索引范围冲突”，再谈“排序策略优化”

**优先级**: P1 - 重要，但当前不应直接修成架构迁移
