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

## 2026-03-14: Ollama batch embedding 热修复

**问题**: OpenClaw 的 Ollama embedding provider 使用旧 `/api/embeddings` 端点（单条），`embedBatch` 实现为 `Promise.all(texts.map(embedOne))`，N 条 = N 次 HTTP 请求。

**根因**: Ollama 2024 年就支持了 `/api/embed` batch 端点，但 OpenClaw 的 `embeddings-ollama.ts` 没有更新。

**修复**: 热修复 `dist/reply-BEN3KNDZ.js`，新增 `embedBatchNative` 函数使用 `/api/embed`，带 graceful fallback。

**文件**: `~/.openclaw/runtime-overrides/ollama-batch-embed-hotfix/`
- `hotfix-patch.py` — 检测 / 应用 / 回滚（三模式）
- `check-hotfix.sh` — cron 调用，自动检测 + 重新应用 + 重启
- `apply-hotfix.sh` — 手动应用

**Issue**: https://github.com/openclaw/openclaw/issues/45944
**Cron**: `hotfix-check-after-update` (9ec9bae9)，每 6 小时检查一次
**性能**: 2.4x 加速（10 条文本 227ms → 95ms）

**教训**: `set -e` + 非零退出码 = 脚本提前终止。对于"检测到需要修复"这种正常的非零退出，不能用 `set -e`。

## 2026-03-15: layer2-health-check.sh 使用不存在的 CLI 命令 `openclaw memory-pro`

**问题**: Layer 2 健康检查脚本持续报 "缺少 openai 模块" + "unknown command 'memory-pro'"，连续 4 天（3/12~3/15）召回测试要么跳过要么失败。

**根因链（为什么总是用错误的 CLI）**:
1. **脚本是 AI agent（cron isolated session）自动生成的**，不是人写的
2. 生成时 agent 把 memory-lancedb-pro 的**插件名**当成了 **CLI 子命令名**，臆造了 `openclaw memory-pro search --scope agent:main --limit 3` 这个完全不存在的命令
3. OpenClaw 正确的 CLI 是 `openclaw memory search`（builtin memory search），不是 `openclaw memory-pro`
4. **脚本生成后没有做过验证测试**——第一次跑就报错（3/12），但因为 `|| true` 吞掉了退出码，只是在报告里写了 "⚠️ memory-pro CLI 不可用，跳过召回测试"
5. 3/13 和 3/14 恰好不知道怎么通过了（可能 agent 在 session 内做了不同的事），但 3/15 再次爆出 `Cannot find module 'openai'` + `error: unknown command 'memory-pro'`
6. 报错信息 "缺少 openai 模块" 具有误导性——实际上 openai npm 包已装好且 Gateway 内插件完全正常；是**错误的 CLI 命令触发了插件在错误上下文重新加载**才找不到模块

**根本教训**:
- **AI agent 自动生成的脚本必须立即验证**：生成后至少跑一次 dry-run
- **不要把插件名当 CLI 子命令臆造**：先 `openclaw help` 确认可用子命令
- **`|| true` 吞错误 + 报告里只写 warning = 问题被静默化**：重要错误应该有显式告警机制
- **cron 的 agentTurn 每次是全新 session**：agent 没有上次跑的记忆，每次都可能犯同样的错误——所以**依赖的脚本必须是确定性的、经过验证的**

**修复**: 将 `openclaw memory-pro search --scope agent:main "晨星" --limit 3` 改为 `openclaw memory search "晨星"`，并适配输出格式解析（分数行 `0.621 memory/file.md:1-33`）。修复后立即测试通过，召回 8 条结果，健康评分恢复到 75/100。

**预防措施**:
- 新建/修改 cron 依赖脚本后，必须在当前 session 内立即执行一次验证
- 对于 CLI 命令，先 `openclaw <cmd> --help` 确认存在再写入脚本
- 考虑在脚本开头加 `openclaw memory search --help >/dev/null 2>&1 || { echo "FATAL: CLI not available"; exit 1; }` 的前置检查

**优先级**: P1 - 已修复

## 2026-03-15 凌晨: OpenClaw 升级 + PR 分支切换导致 Layer 3 完全失效

**问题**: Layer 3 (NotebookLM fallback) 完全不工作，既没有配置也没有代码。

**根因（双重叠加）**:
1. **升级裁掉配置**：OpenClaw 升级到 v2026.3.13 后，`openclaw.json` 中 `plugins.entries["memory-lancedb-pro"].config.layer3Fallback` 配置块被自动清掉
2. **分支切换影响 runtime**：workspace 插件工作树（也是 live runtime 加载路径）停留在 `fix/skip-claude-review-on-fork-prs` 分支，该分支不含 layer3Fallback 代码
3. 两个问题各自就能导致 Layer 3 失效，叠加后更难排查

**影响**: 严重 — Layer 3 深度记忆检索完全不可用

**解决方案**:
1. 切回正确分支 `feat/layer3-notebooklm-fallback`
2. 通过 `gateway config.patch` 恢复 layer3Fallback 配置
3. **建立防护机制**：
   - 专用 runtime worktree `~/.openclaw/runtime-plugins/memory-lancedb-pro`（分支 `runtime/layer3-fallback-active`），与 PR 工作树完全分离
   - PR 开发用独立 worktree `~/.openclaw/worktrees/memory-lancedb-pro/pr-xxx`
   - HEARTBEAT.md 增加守护规则
   - 状态文件 `~/.openclaw/state/layer3-fallback-guard.json`

**教训**:
- **不要用同一个 worktree 既跑 runtime 又做 PR 开发** — 切分支会直接影响生产
- **OpenClaw 升级可能裁掉自定义插件配置** — 升级后必须检查 layer3Fallback 配置是否还在
- 心跳检查应该同时验证：版本号、runtime load path、layer3Fallback 配置存在性

**优先级**: P0 - 已修复并建立防护

---

## 2026-03-15 10:30 - Cron delivery 缺少 target 导致假 error

**问题**: `记忆压缩检查` 和 `layer3-deep-insights` 两个 cron 任务实际执行成功，但状态显示 `error`

**根因**: delivery 配置里有 `mode: announce` 但没有 `to` 字段，Telegram 投递时报 "Delivering to Telegram requires target \<chatId\>"

**影响**: 低 — 任务本身完成了，只是通知没发出去 + 状态显示 error

**解决**: 补上 `delivery.to: "1099011886"`

**教训**: 
- 新建 cron 任务时，如果设了 `delivery.mode: announce`，必须同时设 `to` 和 `channel`
- 心跳检查应把 "delivery error" 和 "task error" 区分开
- 这类 delivery error 会导致 `consecutiveErrors` 计数增长，掩盖真正的任务错误

**优先级**: P2 - 已修复

---

## 2026-03-15 23:50 - LanceDB API / 手工导入记忆的两个坑

**问题 1**: 排障时把 Python LanceDB API 当成 JS API 使用，调用了不存在的 `table.query()`。

**根因**:
1. 直接类比插件源码（JS/TS）里的 `table.query()`
2. 没先在 Python 环境里确认实际 API
3. 结果报错：`AttributeError: 'LanceTable' object has no attribute 'query'`

**正确做法**:
- Python 版先用 `table.search().where(...).select(...).to_list()`
- 跨语言排障时，不要假设同名库 API 完全一致

**问题 2**: 通过底层 LanceDB 手工导入后，部分旧 memory 记录虽然可检索，但 `memory_update` / `memory_forget` 可能提示 `outside accessible scopes`。

**根因**:
1. 绕过了插件正常写入链路，直接操作底层表
2. 工具层的可访问性 / 作用域校验与手工导入记录之间存在不一致

**正确做法**:
- 优先通过 `memory_store` / `memory_update` / `memory_forget` 维护记忆
- 只有在数据恢复场景才直接操作 LanceDB
- 恢复后要额外验证：检索、stats、update、forget 四条链路都正常

**影响**: 中等 - 容易在恢复后留下“能搜到但改不掉/删不掉”的脏数据

**预防措施**:
1. 先确认库的真实 API，再写迁移/恢复脚本
2. 底层恢复完成后，必须补做工具层 CRUD 验证
3. 如需批量迁移，优先找插件官方 import/upgrade 路径，而不是直接写表

**优先级**: P1 - 重要，后续恢复/迁移场景高概率复现

## [ERR-20260317-001] layer3-fallback-notebooklm-session-lock

**Logged**: 2026-03-17T00:00:00Z
**Priority**: high
**Status**: fixed
**Area**: memory

### Summary
`memory_recall` 的 Layer 3 fallback 在 2026-03-17 的 Day 3 benchmark 中连续 3 次出现 `notebooklm session file locked + gateway timeout`，导致本应作为补充的 NotebookLM 深查链路失效。

### Error
```text
Layer 3 fallback failed 3 times with notebooklm session file locked + gateway timeout
lock path: ~/.openclaw/agents/notebooklm/sessions/...jsonl.lock
```

### Context
- Command/operation attempted: `memory_recall` 自动触发 Layer 3 fallback
- Environment: OpenClaw runtime plugin `memory-lancedb-pro`
- Observed behavior:
  - Layer 2 正常返回
  - Layer 3 在 5/15 次 benchmark 查询中被动触发
  - 其中 3 次显式失败，错误集中在 NotebookLM agent session lock + timeout
- Related Files:
  - `~/.openclaw/runtime-plugins/memory-lancedb-pro/src/tools.ts`
  - `~/.openclaw/runtime-plugins/memory-lancedb-pro/test/layer3-fallback.test.mjs`

### Root Cause
最初判断成“缺少 `--session-id`”只对了一半，**真正根因是 `openclaw agent --agent notebooklm` 会按 agent lane 固定路由到 `session:agent:notebooklm:main`**。也就是说，即使显式传了唯一 `--session-id`，也只会改变 transcript id，**不会改变 gateway 的 lane / sessionKey**；请求仍可能撞上同一把 NotebookLM session 文件锁。

### Fix
1. 放弃继续在 `openclaw agent --agent notebooklm` 这条路上打补丁。
2. 将 `src/tools.ts` 的 Layer 3 fallback 改为**直接调用** `~/.openclaw/skills/notebooklm/scripts/nlm-gateway.sh query --agent notebooklm --notebook memory-archive --query ...`，彻底绕开 gateway lane。
3. 同步更新回归测试：不再断言 `--session-id`，改为断言 fallback 命令直接落到 `nlm-gateway.sh query`。
4. 复测时又发现当前配置里的 `layer3Fallback.timeout` 实际是 `45` 秒；新链路虽然打通，但偶发会被 `SIGTERM (timeout 45000ms)` 提前砍掉。于是继续修复代码，让直连 `nlm-gateway` 的路径**尊重配置 timeout**，不再套用旧 `openclaw agent` 路径遗留的 50s cap，并把 `code null` 改成携带 signal/timeout 的明确错误信息。
5. 每次代码变更后都按既有规则清 `rm -rf /tmp/jiti` 并完整 `openclaw gateway restart`，确保 live runtime 真正吃到新代码。

### Validation
- runtime worktree commits：
  - `36d6c4a` — `fix: use nlm-gateway.sh for layer3 fallback to avoid gateway lane lock`
  - `687420d` — `fix: honor configured timeout for nlm gateway layer3 fallback`
- `node --test test/layer3-fallback.test.mjs` ✅
- 真实 `memory_recall` 复测：
  - `当前 Layer 2 和 Layer 3 的策略对比，完整一点` ✅
  - `本周记忆系统有哪些重要变化？请详细说明` ✅
  - `为什么之前会出现 memory-lancedb-pro beta.8 回归？` 第一次偶发 `SIGTERM (timeout 45000ms)`，手工 `nlm-gateway` 同题仅 22.97s，随后二次 `memory_recall` 复测成功 ✅
  - `昨天的工作总结详细历史` ✅
- 结论：`session file locked` 已不再复现；剩余风险一度变成 **45s timeout 偶发偏紧**，不是旧的 gateway lane 锁争用。
- 2026-03-17 10:43 已将 `plugins.entries.memory-lancedb-pro.config.layer3Fallback.timeout` 从 `45` 调高到 `75`，并完成真实验证：
  - `nlm-gateway.sh query --no-cache` 新重 query 实测 `46.607s`（旧配置会越界）
  - 同题 `memory_recall` 在新配置下成功返回 Layer 3 ✅
- 当前结论：这条故障链已从“session lock + 45s timeout”收口为**已修复并通过边界查询验证**。

### Metadata
- Reproducible: yes
- Related Files: ~/.openclaw/runtime-plugins/memory-lancedb-pro/src/tools.ts, ~/.openclaw/runtime-plugins/memory-lancedb-pro/test/layer3-fallback.test.mjs
- Fix Commit: `567a59c561494e91e92f60da890839fe027d5be9`

---

## [ERR-20260317-002] read-offset-beyond-eof

**Logged**: 2026-03-17T06:22:00Z
**Priority**: low
**Status**: pending
**Area**: docs

### Summary
在继续读取 `memory/2026-03-17.md` 时，给了超出文件总行数的 offset，触发 `read` 工具错误：`Offset 120 is beyond end of file (66 lines total)`。

### Error
```text
Offset 120 is beyond end of file (66 lines total)
```

### Context
- Command/operation attempted: 对 `memory/2026-03-17.md` 做分段续读
- Input used: `offset=120`
- Actual file size at the time: `66` lines
- Root pattern: 先按经验猜测后续 offset，而不是先基于上一段输出或当前文件长度确认续读位置。

### Suggested Fix
1. 对短文件续读前，先看上一段 `read` 的实际结束位置，或先确认当前文件总行数。
2. 当文件行数明显较短时，优先从较小 offset 继续读，而不是预设一个大 offset。
3. 如果只是想验证 append 是否成功，直接从文件尾附近读（例如最近 20-40 行），不要盲目跳到远超文件长度的位置。

### Metadata
- Reproducible: yes
- Related Files: `memory/2026-03-17.md`
- See Also: `ERR-20260311-001`, `ERR-20260313-001`

---

---

## [ERR-20260317-EDIT-UNIQUE]

**Logged**: 2026-03-17T08:48:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
`edit` 工具在目标文本出现多次时会直接失败；在重复段落/脏尾巴文件上不能假设匹配唯一。

### Details
修改 `shared-context/THESIS.md` 时，直接用较短的 `old_string` 替换“PR #206 跟进与合并”段落，结果命中 2 处重复文本，`edit` 返回：`Found 2 occurrences of the text ... The text must be unique.` 根因是文件尾部存在一段重复内容/乱码残留，导致同一块文本出现两次。

### Suggested Action
在对可能有重复块的文件使用 `edit` 前，先用 `grep -n` / `read` 定位重复区间；必要时带上更大上下文做唯一匹配，或先清掉重复尾巴再替换。不要在未确认唯一性的情况下用短片段直接 edit。

### Metadata
- Source: manual/main-session

---

## [ERR-20260318-X-PUBLIC-FETCH]

**Logged**: 2026-03-17T16:30:00Z
**Priority**: medium
**Status**: pending
**Area**: web

### Summary
抓取 X/Twitter 公开链接时，`web_fetch` 可能因目标解析到 private/internal/special-use IP 而被 SSRF 策略拦截，不能把它当成稳定读取 X 内容的默认方案。

### Details
尝试读取 `https://x.com/Saboo_Shubham_/status/2022014147450614038` 时，`web_fetch` 返回：`Blocked: resolves to private/internal/special-use IP address`。同一任务中 Brave 搜索也因缺少 API key 不可用。最终改用 `browser open + browser evaluate(document.body.innerText)` 成功拿到正文文本。

### Suggested Action
读取公开 X 帖时优先顺序改为：
1. 若 `xurl auth status` 可用 → 用 `xurl read`
2. 若无鉴权且只是阅读公开内容 → 直接用 `browser` 打开并 `evaluate`/snapshot 提取文本
3. 不把 `web_fetch` 作为读取 X 公链的主路径

### Metadata
- Source: manual/main-session

---

## [ERR-20260318-IMAGE-MINIMAX-VLM]

**Logged**: 2026-03-17T16:31:00Z
**Priority**: medium
**Status**: pending
**Area**: image

### Summary
当前 image 工具背后的 MiniMax VLM 计划不支持所请求模型/能力，不能假设截图 OCR/理解一定可用。

### Details
对浏览器截图调用 `image` 试图抽取 X 页面文本时，返回：`MiniMax VLM API error (2061): your current code plan not support model, coding-plan-vlm`。这说明当前账户/套餐下，image 工具不适合作为通用网页截图 OCR fallback。

### Suggested Action
当任务目标是“从网页提文本”时，优先使用：
1. `browser act evaluate(() => document.body.innerText)`
2. DOM snapshot / aria snapshot
3. 仅在页面文本确实不可直接提取时，再考虑 image 工具
不要把 `image` 作为网页文本抽取的默认后备路径。

### Metadata
- Source: manual/main-session

## [ERR-20260318-LDB] lancedb_to_lance_missing_dependency

**Logged**: 2026-03-17T23:56:45.314107+00:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Attempted to use `lancedb.Table.to_lance()` for memory inspection, but the optional `lance` Python package was not installed.

### Error
```
Traceback (most recent call last):
  File ".../lancedb/table.py", line 1840, in to_lance
    import lance
ModuleNotFoundError: No module named 'lance'
ImportError: The lance library is required to use this function. Please install with `pip install pylance`.
```

### Context
- Operation attempted: inspect LanceDB memories table for duplicate/noise cleanup
- Initial approach: `table.to_lance().to_table(...)`
- Working fallback: use `table.to_arrow()` instead; it is already available and sufficient for row scanning / dedupe work

### Suggested Fix
Prefer `to_arrow()` for inspection scripts in this environment unless `lance`/`pylance` is explicitly installed and verified.

### Metadata
- Reproducible: yes
- Related Files: ~/.openclaw/memory/lancedb-pro

---

## [ERR-20260318-CHERRYPICK-PACKAGEJSON] cherry_pick_test_script_conflict

**Logged**: 2026-03-18T00:38:48.844339+00:00
**Priority**: medium
**Status**: learned
**Area**: git/worktree

### Summary
Cherry-picking runtime plugin commits into other worktrees repeatedly conflicted in `package.json` on the `scripts.test` line, because each branch carried a different test suite baseline.

### Pattern
- code files often auto-merge cleanly
- `package.json` test script conflicts
- correct resolution is to preserve branch-local tests and append newly added regression tests

### Fix Pattern
When cherry-picking test-related commits across memory-lancedb-pro worktrees:
1. inspect conflicted `package.json`
2. keep branch-specific existing test entries
3. append new regression test(s) from the incoming commit
4. `git add ... && git cherry-pick --continue`

---

## [ERR-20260318-EDIT-EXACT-MATCH] edit_exact_text_mismatch

**Logged**: 2026-03-18T00:38:48.844339+00:00
**Priority**: low
**Status**: learned
**Area**: tooling

### Summary
`edit` failed because the requested old text did not match the file exactly (including whitespace / conflict markers / indentation).

### Fix Pattern
Before retrying `edit` on a conflicted or partially changed file:
1. `read` the precise local slice again
2. copy exact current text including whitespace and conflict markers
3. apply the replacement against that exact block

---
## [ERR-20260318-001] read-tool-offset-beyond-end

**Logged**: 2026-03-18T14:33:00Z
**Priority**: low
**Status**: resolved
**Area**: docs

### Summary
`read` tool was called with an offset beyond the end of `notebooklm/SKILL.md`, causing a non-fatal tool error during skill audit.

### Error
```
Offset 261 is beyond end of file (253 lines total)
```

### Context
- Operation: read remaining lines of `~/.openclaw/skills/notebooklm/SKILL.md`
- Cause: used a fixed follow-up offset without checking file length from prior `wc -l`
- Impact: no user-facing failure; work continued normally

### Suggested Fix
When paging file reads, use the known total line count first, or increment from the previous read result instead of assuming another page exists.

### Metadata
- Reproducible: yes
- Related Files: /Users/lucifinil_chen/.openclaw/skills/notebooklm/SKILL.md
- See Also: none

### Resolution
- **Resolved**: 2026-03-18T14:33:00Z
- **Commit/PR**: n/a
- **Notes**: Logged as a recurring hygiene reminder; no code change required.

---
## [ERR-20260318-002] cron-check-memory-pr-status-timeout

**Logged**: 2026-03-18T14:48:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
`check-memory-lancedb-pr-status` cron has timed out repeatedly in main-session systemEvent mode.

### Error
```
cron: job execution timed out
```

### Context
- Job: `check-memory-lancedb-pr-status`
- Recent pattern: 2 consecutive timeout runs, each close to ~16 minutes
- Current shape: `sessionTarget=main` + `payload.kind=systemEvent`
- Likely issue: prompt shape is too open-ended for a lightweight status-check reminder

### Suggested Fix
Convert the job to a lighter isolated run or tighten the reminder scope so it does not stall in the main session.

### Metadata
- Reproducible: yes
- Related Files: cron job `496eeea6-7e88-4b03-b11c-df18149507c7`
- See Also: ERR-20260318-003

---

## [ERR-20260318-003] cron-todo-autopilot-instability

**Logged**: 2026-03-18T14:48:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
`todo-autopilot-v1` cron is unstable under current prompt size and workload, showing timeout and provider-side failures.

### Error
```
cron: job execution timed out
Error: All models failed (2): anthropic/claude-sonnet-4-6: LLM request timed out. (timeout) | openai/gpt-5.4: LLM request timed out. (timeout)
An error occurred while processing your request... request ID 196cca68-3d4c-41ee-b6df-deaa25565a12
```

### Context
- Job: `todo-autopilot-v1`
- Recent pattern: cron timeout + dual-model timeout + provider 5xx/platform failure
- Current prompt reads many files and asks for multi-step execution + dual sync + reporting
- Earlier runs succeeded when the task stayed narrow and sync-oriented

### Suggested Fix
Shrink the prompt scope, reduce required file reads, bias toward lightweight sync/closure work, and avoid turning a recurring cron into a heavy general-purpose execution loop.

### Metadata
- Reproducible: yes
- Related Files: cron job `5bdd1d4d-62d9-4403-aafb-fc260a7189ec`
- See Also: ERR-20260318-002

---

### 2026-03-19 creator-ops CDP 连接问题
- **问题**: macOS Chrome 用 `--remote-debugging-port=9222` 启动后绑定到 IPv6 `[::1]:9222`，但脚本默认连 `127.0.0.1:9222`（IPv4），导致 404
- **修复**: 将 `cdp_publish.py` 的 `CDP_HOST` 从 `"127.0.0.1"` 改为 `"localhost"`
- **问题2**: 小红书创作者中心 (`creator.xiaohongshu.com`) 和主站 (`www.xiaohongshu.com`) 是独立登录态，需要分别扫码
- **问题3**: `cdp_publish.py` 的 `--headless` 是全局参数，必须放在子命令前面（`--headless check-login`），不能放后面
- **影响**: creator-ops skill
- **状态**: ✅ 已修复

### 2026-03-19 publish_pipeline.py 也有 127.0.0.1 硬编码
- **问题**: cdp_publish.py 修了 CDP_HOST，但 publish_pipeline.py 的 argparse default 也硬编码了 127.0.0.1
- **修复**: 同样改为 `localhost`
- **教训**: 同一个项目多个入口文件可能有相同的硬编码，修一处不够，要 grep 全局检查
- **状态**: ✅ 已修复

### 2026-03-19 NLM media-research notebook 已失效
- **问题**: notebooks.json 中的 media-research ID (cfb2b01d) 指向的 notebook 不在 notebooklm list 中，可能已被清理/过期
- **修复**: 新建 notebook (032a95b5)，更新 notebooks.json
- **教训**: NLM notebook 可能会意外失效，应定期用 `notebooklm list` 验证
- **状态**: ✅ 已修复

### 2026-03-19 chrome_launcher is_port_open IPv4 检测失败
- **问题**: macOS Chrome 用 `--remote-debugging-port` 绑定到 IPv6 `[::1]:9222`，但 `is_port_open()` 用 IPv4 `AF_INET` 检测，连接被拒但 Chrome 实际在跑 → launcher 误判"Chrome 已在跑"不启动，脚本连不上
- **修复**: 改为 IPv6 `AF_INET6` 检测，macOS 上 `AF_INET6` 可以同时连接 IPv6 和 IPv4 地址
- **macOS 特殊性**: macOS 的 `AF_INET6` 是 dual-stack，connect 时会自动选择；Linux 上则需要 `AF_UNSPEC`
- **状态**: ✅ 已修复 chrome_launcher.py

### 2026-03-19 CDP 端口 9222 被主 Chrome 占用
- **问题**: 晨星的主 Chrome (PID 637) 已经监听 9222 (teamcoherence 协议)，XiaohongshuProfiles 的 Chrome 启动时报 `bind() failed: Address already in use`
- **根因**: macOS 上 Chrome 单实例，同一个 profile 不能并行；但用不同 `--user-data-dir` 可以启动多个实例，只是调试端口必须不同
- **修复**: 将 creator-ops 脚本的 CDP_PORT 从 9222 改为 9223，chrome_launcher 启动到 9223，主 Chrome 的 9222 不冲突
- **副作用**: 两个 Chrome 实例现在各自用独立端口（9222 主 Chrome / 9223 小红书），不影响使用
- **状态**: ✅ 已修复（cdp_publish.py + chrome_launcher.py + publish_pipeline.py 全部改为 CDP_PORT=9223）

### 2026-03-19 小红书标题字数限制 + CDP 发布按钮点击问题
- **标题限制**: 小红书标题最多 20 个字，原标题 26 字被截断导致无法发布
- **CDP 按钮点击**: `cdp_publish.py` 报 `PUBLISH_STATUS: PUBLISHED` 但实际未发布。根因待查（可能坐标偏移或弹窗拦截），第二次重试后成功
- **教训**: (1) 标题生成时必须控制在 20 字以内 (2) 发布后应验证页面 URL 是否跳转到笔记管理页（而不是仍在编辑页）
- **状态**: 标题问题已知，按钮点击问题需后续修复 cdp_publish.py 添加发布后验证逻辑

### 2026-03-19 nano-banana 模型名
- `google/gemini-3-pro-image-preview` 不可用（model not allowed），正确名称是 `google/gemini-3.1-pro-image-preview`（NanobananaPro）
- 默认模型 `google/gemini-3.1-flash-image-preview`（Nanobanana2）效果反而更好
## [ERR-20260321-001] web-search-gemini-unsupported-filters

**Logged**: 2026-03-21T05:25:00Z
**Priority**: low
**Status**: pending
**Area**: web

### Summary
在当前 gemini provider 下调用 `web_search` 时，误传了 `country` 和 `language` 参数，导致工具直接返回 unsupported filter 错误。

### Error
```text
unsupported_country
unsupported_language
Only Brave and Perplexity support country/language filtering.
```

### Context
- Operation attempted: daily AI/Agent/LLM signal scan
- Initial parameters included: `country: "US"`, `language: "en"`
- Actual provider behavior: gemini provider rejects these filters instead of ignoring them

### Suggested Fix
在不确定底层 provider 时，先使用最小兼容参数集（query/count/freshness/date_after/date_before）。只有确认 provider 支持时再加 `country` 或 `language`。

### Metadata
- Reproducible: yes
- Related Files: n/a
- See Also: none

---

## [ERR-20260319-001] creator-ops-path-drift

**Logged**: 2026-03-19T13:02:00Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
creator-ops skill 文档中的小红书脚本目录仍指向 ~/.openclaw/skills/xiaohongshu-unified，但实际脚本已迁移到 ~/.openclaw/skills/creator-ops/scripts。

### Error
```
zsh:cd:1: no such file or directory: /Users/lucifinil_chen/.openclaw/skills/xiaohongshu-unified
```

### Context
- Command attempted: cd ~/.openclaw/skills/xiaohongshu-unified && python3 scripts/cdp_publish.py content-data --csv-file /tmp/xhs_data.csv
- Resolved path: ~/.openclaw/skills/creator-ops/scripts/cdp_publish.py
- Impact: cron task would fail until path is corrected manually or in skill docs.

### Suggested Fix
更新 ~/.openclaw/skills/creator-ops/SKILL.md 中所有 xiaohongshu-unified 路径，统一改为 creator-ops 实际目录，避免后续 cron 任务继续踩坑。

### Metadata
- Reproducible: yes
- Related Files: /Users/lucifinil_chen/.openclaw/skills/creator-ops/SKILL.md

---

## 2026-03-19 21:28 - 事实核查过度泛化导致误判

**问题**: 晨星提出黄仁勋 CNBC 采访称 OpenClaw 是"下一个 ChatGPT"的选题，小光两次拒绝发布，判定为假消息。

**根因**: 推理错误——过度泛化（不是搜索范围问题）
1. YouTube 视频标题混淆了 OpenShell 和 OpenClaw → 正确判定该视频有误
2. 错误地将"来源A有误"泛化为"所有黄仁勋+OpenClaw说法都是假的"
3. CNBC 采访是独立来源，Jensen 确实在采访中说了 OpenClaw 是"下一个 ChatGPT"
4. 第三次搜索用更精准关键词才找到

**修复**:
- persona.md 新增「事实核查规则」4 条：
  1. 每个来源独立验证（来源A有误 ≠ 所有相关说法都有误）
  2. 不凭知识截止日期否定用户来源
  3. 多关键词多来源搜索
  4. 名人背书必须验证原文
- memory_store 已记录

### Metadata
- Severity: HIGH（连续两次错误拒绝用户合理请求）
- Reproducible: yes（任何知识截止后的真实事件都可能触发）
- Related Files: ~/.openclaw/skills/creator-ops/persona.md

---

## 2026-03-23: NotebookLM CLI 命令语法错误

**错误 1**: `notebooklm notebook create` → 正确: `notebooklm create`（没有 `notebook` 子命令前缀）
**错误 2**: `notebooklm delete <id> --yes` → 正确: `notebooklm delete` 不接位置参数，需要 `notebooklm use <id>` 后 `notebooklm delete`（或查 `notebooklm delete --help` 确认用法）
**根因**: 凭印象调用，未先 `--help` 验证语法
**教训**: 任何不确定的 CLI 先跑 `--help`（MEMORY.md 血泪教训 #5）

## 2026-03-23: sub-agent message 工具配置用错 key

**错误**：在 openclaw.json 中错误使用 `alsoAllow: ["message"]` 而非文档中规定的 `allow: ["message"]`。

**症状**：sub-agent 反馈 "没有 message 工具权限"，无法向 Telegram 群发送通知。

**根因**：schema lookup 返回的数据中同时包含 `allow`、`alsoAllow`、`deny` 三个字段（都是数组），我错误地判断 `alsoAllow` 是"允许"的意思并使用它。但官方文档（docs/tools/subagents.md）明确指出正确 key 是 `allow` 和 `deny`，其中 `deny` 优先。`alsoAllow` 在 schema 中存在但未被系统正确处理（形同无效 key）。

**教训**：
1. 配置类修改必须对照官方文档（docs/）而非仅凭 schema raw data 推断
2. 遇到"不起作用"的配置，优先检查 key 名称是否与文档一致
3. 官方文档示例：`tools.subagents.tools.allow: ["message"]`

**修复**：将 `tools.subagents.tools.alsoAllow` 改为 `tools.subagents.tools.allow`

## 2026-03-23: sub-agent message 工具配置 — 最终结论

**错误**：
1. 错误使用 `alsoAllow: ["message"]`（非有效 key）
2. 改为 `allow: ["message"]` 后，sub-agent 反而只剩 message 工具，exec/read 等全被屏蔽
3. 删除配置后测试确认：sub-agent 默认工具集里根本没有 `message`

**最终结论**：`sessions_spawn` 创建的 isolated session 没有 `message` 工具，这是 OpenClaw 的架构限制，配置无法改变。

**正确架构**：sub-agent 只返回结果，main 统一推送通知到职能群 + 监控群。

**教训**：
1. 配置更改后必须实测验证，不能只凭文档推断
2. 当配置不起作用时，直接问用户/查源码
3. 接受系统限制比绕过更高效

**已更新**：
- wemedia SKILL.md ✅
- starchain pipeline-v2-8/7-contract.md ✅
- stareval SKILL.md ✅

## 2026-03-23 下午

### browser act 常见错误
1. `ref or selector is required` — 使用 x/y 坐标点击时必须提供 ref 或 selector，不能用坐标
2. `fields are required` — kind=fill 时需要 fields 数组格式，不能用 ref+text 分开传
3. `Error: Element "eXX" not found or not visible` — 页面已刷新，ref 失效，需要重新 snapshot
4. `TimeoutError: locator.click: Timeout 8000ms exceeded` — Playwright locator 超时，ref 格式不匹配，改用 selector 字符串

### WhatsApp Echo 问题
- 现象：消息被重复发送/收到，疑似 gateway wspp 协议问题
- 影响：干扰正常对话，晨星决定迁移到 Telegram
- 状态：未解决，属于 OpenClaw WhatsApp gateway bug


## MiniMax API 持续离线 (2026-03-24 00:32 - 持续中)
- **现象**: `minimax/MiniMax-M2.7` 所有请求超时 120-300s，profile `minimax:cn`
- **影响**: 8 个 cron 任务 ERROR (post-upgrade-guard, layer2-health-check, memory-quality-audit, sync-high-priority-memories, media-signal-noon/evening, media-daily-retro, todo-daily-check)
- **Failover 行为**: 先切 minimax:cn 再切 openai/gpt-5.4，两个都超时
- **调查**: api.minimaxi.com 返回 404 Not Found，疑似 API endpoint 变更
- **状态**: 已报告晨星，等待指示

## 2026-03-24 Gemini agentTurn + tool call 400（thought_signature 缺失）

- **现象**: `media-signal-evening` 在多通道 `channel` 问题修复后，改为再次手动重跑时，Gemini provider 返回 400：`Function call is missing a thought_signature in functionCall parts`。
- **关键信号**: 报错点明确落在工具调用（`default_api:read`），不是文件不存在，也不是路径错误。
- **现场验证**:
  - `DAILY-SIGNAL-BRIEF.md` / `HOT-SCAN-INBOX.md` / `HOT-QUEUE.md` 三个路径都存在且可读。
  - 同一批路径改用 Sonnet 跑 cron 时可继续执行，因此不是 workspace 路径配置问题。
- **结论**: 这是 Gemini provider / tool-calling 兼容性问题，不是用户配置文件里的路径写错。
- **临时处置**: 对需要稳定 `read`/`edit`/`message` 工具链的 cron，先切到 Sonnet / GPT；Gemini 更适合纯搜索/轻推理、少工具调用场景。
- **教训**:
  1. 看到 `thought_signature` 相关 400，优先判定为 provider/tool 协议问题，不要先怀疑文件路径。
  2. 多通道问题修掉后，如果仍报 Gemini 400，要直接切模型验证，不要在原模型上空转重试。

## 2026-03-24 抖音 Smoke Test 踩坑记录

### 问题 1：browser tool upload 路径限制
**现象**：`browser(action=upload)` 要求文件必须在 `/tmp/openclaw/uploads/` 目录下
**错误**：`Invalid path: must stay within uploads directory (/tmp/openclaw/uploads)`
**解决**：测试视频/封面等文件必须先 cp 到该目录，或直接在该目录生成

### 问题 2：browser tool act 的 ref 不稳定
**现象**：对话框中的按钮 ref 在每次 snapshot 后可能变化（如 e20 在上一次 snapshot 里有，下一次就没了）
**解决**：用 `evaluate` + JS 查找元素（className、textContent 定位），比 ref 更可靠

### 问题 3：CDP WebSocket origin 被拒绝
**现象**：`cdp_client.py` 的 websocket 连接被 Chrome 拒绝（403 Forbidden - Rejected incoming WebSocket connection from http://127.0.0.1:18800）
**原因**：openclaw 托管的 Chrome 启动时没有 `--remote-allow-origins=*` 参数
**影响**：自定义 CDP 脚本无法复用 openclaw browser 的登录态，必须另开 Playwright 独立 browser
**绕过方法**：见问题 4

### 问题 4：Playwright 独立 browser 无法复用登录态
**现象**：用 Playwright 新开的 browser（即使指定了 douyin_auth.json cookies）仍然是未登录状态
**原因**：抖音的 httpOnly cookie 无法通过 Playwright add_cookies 设置；且可能检测到 automation 控制
**解决**：用 openclaw browser（已登录）做上传，用 Playwright 独立 browser 做封面设置

### 问题 5：browser tool 上传文件后无法在 file input 中设置真实文件
**现象**：通过 `browser(action=upload)` 触发文件选择后，JS 的 DataTransfer API 无法设置真实文件路径（安全限制）
**解决**：openclaw browser 的 `browser(action=upload)` + 点击触发 是正确路径；问题在于 openclaw browser 的 upload 机制和 CDP upload command 是两条独立链路

### 验证成功的方法
1. **视频上传**：`openclaw browser upload <path>` + 点击上传按钮（e9/e10）→ 成功
2. **标题填写**：`browser(action=act, kind=fill, fields=[{ref, value}])` → 成功（注意要用 fields 数组格式）
3. **隐私设置**：checkbox click → 成功
4. **发布**：`browser(action=act, kind=click, ref=e16)` → 成功
5. **封面对话框**：用 evaluate JS 查找并点击元素比 ref 更可靠

### 关键路径
- 视频文件：必须放在 `/tmp/openclaw/uploads/`
- 封面文件：同上
- OpenClaw Browser targetId：需要先 navigate 获取当前 tab 的 targetId

## 2026-03-24 gemini agent 工具缺失错误：html2text

- **现象**: gemini agent 在执行 web research 时，`html2text` 命令不存在，导致工具调用失败，最终 agent 超时退出。
- **错误信息**: `zsh:1: command not found: html2text`
- **影响**: gemini agent 搜索任务完全失败，无任何输出。
- **教训**:
  1. gemini agent 的 tool-calling 环境可能缺少系统 CLI 工具（如 html2text、lynx 等）
  2. 建议在 cron 脚本或 tool calling 环境里用之前先检查依赖是否存在，或改用纯 JSON 输出的 web_fetch
  3. 这个错误导致研究层失败，整个 M 级流水线卡在 Step 1.5
- **处置**: 需要重新运行研究步骤，考虑改用 web_fetch 或在 gemini 侧使用其他工具


## 2026-03-24 小红书流水线 / cron 多坑记录

### 坑1：gemini agent html2text 缺失
- **现象**：gemini agent 在执行 web research 时调用 `html2text` CLI 工具失败，导致整条搜索链断裂，最终 agent 超时退出。
- **根因**：gemini 模型在 tool calling 时自动选择了 `html2text` 做 HTML→markdown 转换，但运行环境里没有安装。
- **已处置**：晨星已安装 `html2text`。
- **教训**：gemini agent 的工具链对系统 CLI 有隐式依赖，需确保环境中所有常用 CLI 工具可用。

### 坑2：gemini 模型 allowlist 限制
- **现象**：spawn 时用 `gemini/gemini-3.1-pro-high` 报 "model not allowed"。
- **根因**：OpenClaw 配置里 gemini 只允许 `-preview` 后缀的模型，不允许 `-high`。
- **教训**：gemini agent spawn 统一用 `gemini/gemini-3.1-pro-preview`，不要用 `-high`。

### 坑3：小红书标题逐字计数
- **现象**：`publish_pipeline.py` 标题验证失败，"23字"实际算出来更多（Latin 字母逐字计算）。
- **根因**：脚本逐字计数，中文字符=1，Latin 字符也=1（不是按字节），导致看似接近的字数实际超限。
- **示例**："效率的反噬：OpenClaw核心漏洞与升级实录" → 23字 → 超限
- **教训**：中文标题先手动压缩到 18 字以内，预留余量；最终用脚本验证。
- **已记录**：未来创作流程中，wemedia subagent 输出标题前先压缩到 ≤18 字。

### 坑4：media-signal crons 超时问题
- **现象**：
  - `media-signal-noon`：error（Gemini 400 thought_signature → 已切 Sonnet）
  - `media-signal-evening`：超时 1062s（远超 300s 配置）仍未完成 → 模型切 MiniMax → 仍超时
- **根因**：cron payload 里的 prompt 任务量超过 5 分钟预算，但 cron 系统的硬超时 (300s) 在 job timeout 之前就杀掉了进程。
- **已处置**：
  - 两个 cron 均已更新为 `anthropic/claude-sonnet-4-6` + 300s timeout
  - 后续需要重新评估 prompt 任务量，或延长 timeout 到 600s
- **教训**：信号扫描类 crons 的 prompt 需要严格控制任务范围，避免单轮跑太多搜索+写入操作。

## 2026-03-25

### OpenClaw cron 子命令错误

**错误**：
- `openclaw cron logs` → `error: unknown command 'logs'`
- `openclaw cron info` → `error: unknown command 'info'`

**正确子命令**：
- `openclaw cron list` — 列出所有 cron 任务
- `openclaw cron runs --id <job-id> --limit N` — 查看指定任务的历史运行记录
- `openclaw cron run <job-id>` — 立即运行任务（debug）
- `openclaw cron status` — 查看调度器状态

**教训**：
不要猜测 CLI 子命令，先 `openclaw cron --help` 确认可用命令。
## [ERR-20260325-001] memory_forget_scope_requirement

**Logged**: 2026-03-25T07:47:22.523217+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
`memory_forget(memoryId=...)` can fail with "outside accessible scopes" unless `scope="agent:main"` is passed explicitly, even for IDs returned by `memory_list`/`memory_recall`.

### Error
```
Memory deletion failed: Memory <id> is outside accessible scopes
```

### Context
- Operation attempted: deleting duplicate memories by exact ID
- Initial call omitted `scope`
- Same deletion succeeded after retrying with `scope: "agent:main"`

### Suggested Fix
When deleting known memories in the main scope, always pass `scope="agent:main"` with `memory_forget` to avoid ambiguous/default-scope failures.

### Metadata
- Reproducible: yes
- Related Files: ~/.openclaw/workspace/.learnings/ERRORS.md
- See Also: 783cc26d-18b3-416f-a023-b5204939fdd4

---

## [ERR-20260326-001] openclaw_cron_cli_wrong_flags

**Logged**: 2026-03-26T00:55:00+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Tried `openclaw cron run <job-id> --dry-run`, but the CLI does not support `--dry-run` for `cron run`.

### Error
```
error: unknown option '--dry-run'
```

### Context
- Operation attempted: inspect/debug `post-upgrade-guard` cron execution without actually triggering a real run
- Assumption was based on common CLI patterns, not OpenClaw's actual cron interface
- Similar prior mistake: guessed `openclaw cron logs` / `info`, which also do not exist

### Suggested Fix
Before using less-common OpenClaw cron subcommands/options, run `openclaw cron --help` (or the specific subcommand help) and use only documented flags.

### Metadata
- Reproducible: yes
- Related Files: ~/.openclaw/workspace/.learnings/ERRORS.md
- See Also: 2026-03-25 cron command guessing entry above

---

## [ERR-20260326-002] memory_plugin_merge_residue_duplicate_createLlmClient

**Logged**: 2026-03-26T00:55:30+08:00
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
During the memory-lancedb-pro beta.10 upgrade, merge residue in `src/llm-client.ts` left two `createLlmClient` declarations, causing the runtime plugin to fail to load after restart.

### Error
```
[plugins] memory-lancedb-pro failed to load ...
Error: ParseError: Identifier 'createLlmClient' has already been declared.
```

### Context
- Operation attempted: upgrade runtime plugin to `memory-lancedb-pro@1.1.0-beta.10`
- A merge conflict had been resolved incompletely: old local JSON-hardening implementation and beta.10 OAuth/factory implementation both remained in the same file
- Failure surfaced only after gateway restart, when the runtime plugin recompiled/loaded

### Suggested Fix
After resolving upgrade merges in runtime plugins, grep for duplicate exported symbols in touched files and do one post-restart plugin-load smoke check (`openclaw status` / gateway logs) before considering the upgrade complete.

### Metadata
- Reproducible: yes
- Related Files: ~/.openclaw/runtime-plugins/memory-lancedb-pro/src/llm-client.ts, ~/.openclaw/logs/gateway.err.log
- See Also: memory-lancedb-pro beta.10 upgrade work on 2026-03-25

### Resolution
- **Resolved**: 2026-03-25T21:33:00+08:00
- **Commit/PR**: runtime worktree local fix
- **Notes**: Removed duplicate `createLlmClient` block, kept beta.10 OAuth/factory implementation plus local JSON-defense behavior, restarted gateway, and verified `memory_stats` / `memory_list` / `memory_recall` / isolated write smoke all passed.

---
## [ERR-20260326-003] git_add_pathspec_deleted_untracked_files

**Logged**: 2026-03-26T01:20:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: infra

### Summary
After deleting a mixed set of tracked and untracked workspace files, `git add -A -- <paths...>` failed because the path list still included untracked files that no longer existed (for example `.DS_Store`).

### Error
```
致命错误：路径规格 '.DS_Store' 未匹配任何文件
subprocess.CalledProcessError: ... git add -A -- <paths...> returned non-zero exit status 128
```

### Context
- Operation attempted: batch-clean temporary workspace artifacts, then stage only that cleanup as an isolated commit
- The deletion list mixed tracked files with untracked files
- Once deleted, some untracked files no longer matched any git pathspec, which caused `git add` to abort

### Suggested Fix
When staging deletions from a mixed file set, first filter with `git ls-files --error-unmatch` and run `git add -u -- <tracked-paths>` only on paths that are actually tracked.

### Metadata
- Reproducible: yes
- Related Files: ~/.openclaw/workspace/.learnings/ERRORS.md
- See Also: ERR-20260326-001

### Resolution
- **Resolved**: 2026-03-26T01:16:00+08:00
- **Commit/PR**: 9d2205c
- **Notes**: Re-ran staging with a tracked-only filter and committed the cleanup successfully.

---
## [ERR-20260326-004] edit_tool_non_unique_anchor_match

**Logged**: 2026-03-26T01:24:00+08:00
**Priority**: low
**Status**: resolved
**Area**: infra

### Summary
Tried to use the `edit` tool with an `old_string` anchor that appeared many times in the file, so the edit failed with a non-unique match error.

### Error
```
Found 28 occurrences of the text ... The text must be unique. Please provide more context to make it unique.
```

### Context
- Operation attempted: append a new error entry into `.learnings/ERRORS.md`
- Used a generic anchor (`---`) that appears repeatedly between entries
- The edit tool requires an exact unique match, so generic separators are unsafe anchors in append-heavy markdown logs

### Suggested Fix
For append-heavy files, avoid `edit` with generic separators. Use either:
1. `exec` with shell append (`cat >> file <<'EOF' ... EOF`), or
2. `edit` with a longer unique trailer block from the file tail.

### Metadata
- Reproducible: yes
- Related Files: ~/.openclaw/workspace/.learnings/ERRORS.md
- See Also: ERR-20260326-003

### Resolution
- **Resolved**: 2026-03-26T01:18:00+08:00
- **Commit/PR**: c5a8511
- **Notes**: Switched to shell append and then staged/committed normally.

---
