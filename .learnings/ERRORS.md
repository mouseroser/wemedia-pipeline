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
- 结论：`session file locked` 已不再复现；剩余风险是 **45s timeout 偶发偏紧**，不是旧的 gateway lane 锁争用。

### Metadata
- Reproducible: yes
- Related Files: ~/.openclaw/runtime-plugins/memory-lancedb-pro/src/tools.ts, ~/.openclaw/runtime-plugins/memory-lancedb-pro/test/layer3-fallback.test.mjs
- Fix Commit: `567a59c561494e91e92f60da890839fe027d5be9`

---
