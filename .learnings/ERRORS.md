# ERRORS.md

## 2026-03-29 exec 内嵌 python3 -c 含特殊字符时 zsh 误解析
- **现象**：python3 -c 字符串里含反引号、中文引号、箭头等特殊字符，zsh 会把它们当 shell 语法解析，报 `command not found` / `unknown file attribute`
- **修复**：改用 `python3 << 'PYEOF' ... PYEOF` heredoc 形式，单引号 PYEOF 阻止 zsh 展开
- **预防**：凡是 python3 -c 内容含特殊字符，一律改用 heredoc

## 2026-03-29 edit 工具替换含特殊字符的文本失败
- **现象**：edit oldText/newText 含中文引号、特殊字符时，报 `No changes made / identical content`，实际是字符编码不完全匹配
- **修复**：改用 python3 heredoc 读文件 → str.replace → 写回，绕过 edit 工具的字符匹配限制
- **预防**：文本含中文引号/特殊符号时，优先用 python3 heredoc 处理，不用 edit 工具

## 2026-03-29 workspace git remote 未配置
- **现象**：`git push` 报「没有配置推送目标」，commit 只落本地
- **原因**：workspace repo 初始化时未绑定 remote
- **修复**：`git remote add origin https://github.com/mouseroser/wemedia-skill.git && git push -u origin master`
- **预防**：新建 repo 后立即 `git remote add origin <url>` + `git push -u origin master` - 错误日志

## [ERR-20260327-003] Gemini subagent returns empty output because tool schema is rejected by provider

**Logged**: 2026-03-27T10:02:00+08:00
**Priority**: high
**Status**: confirmed_root_cause
**Area**: Gemini provider / subagent runtime

### Summary
Gemini subagent 的“空输出”不是模型没回答，而是请求在生成前被 provider 400 拒绝；subagent announce 没把错误显式冒泡，表现成 completed with no output。

### Evidence
会话文件：
`/Users/lucifinil_chen/.openclaw/agents/gemini/sessions/fef9b862-8926-4f96-a2b1-58f28e02ac0b.jsonl`

核心报错：
```text
400 ... tools[0].function_declarations[0].name: Invalid function name
400 ... tools[0].function_declarations[1].name: Invalid function name
...
```

### Root Cause
Gemini provider 走的是 `openai-completions` 兼容层（`https://max.openai365.top/v1`），但 OpenClaw 发送的工具 schema 中有若干 function name 不符合 Gemini 那侧的 function_declarations 命名规则，导致整个请求在生成前被拒绝。由于 announce 层把这类失败折叠成“completed successfully + empty output”，主会话误以为 Gemini 在空输出。

### Impact
- Gemini 1.5A 空输出
- Gemini 1.5E 空输出
- Gemini Step 2 初稿 空输出
- Claude / OpenAI 正常，说明不是任务 prompt 本身问题

### Workaround
1. 暂停把 Gemini 用于带工具的 subagent 写作/复核任务
2. 改用 Claude / OpenAI 执行这些步骤
3. 如必须用 Gemini，尝试为 gemini agent 配最小 tools allowlist 或 no-tools 专用 agent

### Fix Direction
- 在 Gemini 适配层规范化 tool function name（保证符合 Gemini function_declarations 规则）
- 或让 Gemini 子 agent 默认不暴露整套工具，仅暴露白名单工具
- 或在 announce 层正确上报 provider error，不要伪装成 completed/no output

---

## [ERR-20260327-001] nlm-gateway artifact generate fails: notebooklm -n flag not supported

**Logged**: 2026-03-27T09:53:00+08:00
**Priority**: medium
**Status**: known_bug
**Area**: notebooklm skill / nlm-gateway

### Summary
`nlm-gateway.sh artifact generate` 失败，因为底层调用 `notebooklm generate -n "$nb_id"` 时，`notebooklm generate` 命令不接受 `-n` 参数（NotebookLM CLI 的 `generate` 子命令不需要 notebook ID 指定）。

### Error
```
Error: No such option: -n
artifact generate failed
```

### Root Cause
gateway 脚本里 `cmd_artifact()` 对 `generate` 操作使用 `notebooklm generate -n "$nb_id"`，但 `notebooklm generate` 命令没有 `-n` 选项（需要先用 `notebooklm use <nb_id>` 切换 notebook）。`-n` 是 `notebooklm` 全局选项，不是 `generate` 子命令的选项。

### Workaround
直接用 CLI 绕过 gateway：
```bash
notebooklm use "$nb_id"
notebooklm generate infographic "..." --orientation square --style bento-grid --language zh_Hans
```

### Fix
修改 `nlm-gateway.sh` 的 `cmd_artifact()` 函数，对 `generate` 操作不使用 `-n "$nb_id"`，改用先 `notebooklm use "$nb_id"` 再 `generate` 的方式；或者 NotebookLM CLI 新版本已支持 `notebooklm generate -n <id>` 直接指定。

---

## [ERR-20260327-002] notebooklm generate RPC null result

**Logged**: 2026-03-27T09:54:00+08:00
**Priority**: medium
**Status**: intermittent
**Area**: notebooklm CLI

### Summary
在已有内容的 notebook 上调用 `notebooklm generate infographic` 返回 RPC null result，可能是 source太少（notebook几乎是空的）或 query 参数格式不兼容。

### Error
```
Error: RPC rLM1Ne returned null result data (possible server error or parameter mismatch)
```

### Workaround
1. 先往 notebook 添加一个有实质内容的 source（不是 /dev/null 或空文件）
2. 使用更简单的 query 字符串
3. 用临时干净 notebook 生成（`notebooklm create` 后直接生成，不先添加 source）

### Investigate
在 `agent-kernel-cover` notebook（已有 1 个 source）上复现，在新建的 `DeerFlow-OpenClaw-Cover-Temp`（0 source）上也复现。可能是 infographic 子命令本身在当前 NotebookLM 版本中的行为有变化。

---

## [ERR-20260326-001] read-path-tilde-enoent

**Logged**: 2026-03-26T07:35:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
`read` 工具对 `~` 路径不保证做 shell 式展开，直接传 `~/.openclaw/...` 可能触发 `ENOENT`。

### Error
```
[read] ENOENT: no such file or directory, access '[REDACTED]'
```

### Context
- 触发操作：读取 skill 文件时传入 `~/.openclaw/skills/.../SKILL.md`
- 现象：工具报 `ENOENT`
- 实际根因：OpenClaw `read` 工具参数不是 shell，`~` 不一定自动展开

### Suggested Fix
统一对 `read` / `write` / `edit` 使用绝对路径，不依赖 `~` 展开。

### Metadata
- Reproducible: yes
- Related Files: TOOLS.md

### Resolution
- **Resolved**: 2026-03-26T07:35:00+08:00
- **Notes**: 已在 `TOOLS.md` 增加规则：文件工具优先使用绝对路径，避免 `~` 导致 ENOENT。

---

## [ERR-20260326-002] pyarrow-table-to-list-attributeerror

**Logged**: 2026-03-26T07:38:00+08:00
**Priority**: low
**Status**: resolved
**Area**: config

### Summary
在用 Python 直接读取 LanceDB 底表时，把 `pyarrow.Table` 当成有 `to_list()` 方法，实际应使用 `to_pylist()`。

### Error
```
Traceback (most recent call last):
  File "<stdin>", line 5, in <module>
AttributeError: 'pyarrow.lib.Table' object has no attribute 'to_list'. Did you mean: 'to_pylist'?
```

### Context
- 触发操作：通过 LanceDB / PyArrow 直接检查 Layer 2 底表
- 现象：调用 `pyarrow.Table.to_list()` 报 AttributeError
- 根因：`to_list()` 不是 `pyarrow.Table` 的方法；正确方法是 `to_pylist()`

### Suggested Fix
读取 Arrow 表时统一使用 `table.to_pylist()`，不要误用 `to_list()`。

### Metadata
- Reproducible: yes
- Related Files: /Users/lucifinil_chen/.openclaw/memory/lancedb-pro

### Resolution
- **Resolved**: 2026-03-26T07:38:00+08:00
- **Notes**: 已改用 `to_pylist()` 完成底表扫描与噪音复查。

---

## [ERR-20260326-003] openclaw-cron-subcommand-mismatch

**Logged**: 2026-03-26T07:40:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
误把 cron 即时执行命令写成 `openclaw cron trigger`，但当前 CLI 正确子命令是 `openclaw cron run`。

### Error
```
error: unknown command 'trigger'
```

### Context
- 触发操作：按 HEARTBEAT.md 想手动触发异常 cron
- 现象：CLI 返回 unknown command `trigger`
- 实际根因：HEARTBEAT.md 中命令写的是旧口径；当前 `openclaw cron --help` 显示正确命令为 `run`

### Suggested Fix
更新心跳与运维文档：手动触发 cron 一律使用 `openclaw cron run --id <job-id>`。

### Metadata
- Reproducible: yes
- Related Files: /Users/lucifinil_chen/.openclaw/workspace/HEARTBEAT.md

### Resolution
- **Resolved**: 2026-03-26T07:40:00+08:00
- **Notes**: 已改用 `openclaw cron run 95a2ac7d-b275-44ca-9049-a26ac19dd52d` 成功补跑 `media-signal-morning`。

---

## [ERR-20260326-004] edit-exact-match-fragile

**Logged**: 2026-03-26T07:41:00+08:00
**Priority**: low
**Status**: resolved
**Area**: docs

### Summary
`edit` 工具要求 oldText 完全精确匹配；当目标文本上下文或空白略有变化时，替换会失败。

### Error
```
Could not find the exact text in [REDACTED]
The old text must match exactly including all whitespace and newlines.
```

### Context
- 触发操作：向 `.learnings/ERRORS.md` 插入新错误条目
- 现象：`edit` 因 oldText 未精确命中而失败
- 根因：`edit` 是精确替换，不适合在长文件中做脆弱锚点插入

### Suggested Fix
对长日志文件追加/重写时，优先先 `read` 精确定位；若锚点不稳，直接用 `write` 全量重写，避免反复失败。

### Metadata
- Reproducible: yes
- Related Files: /Users/lucifinil_chen/.openclaw/workspace/.learnings/ERRORS.md

### Resolution
- **Resolved**: 2026-03-26T07:41:00+08:00
- **Notes**: 本次改为 `write` 全量重写 ERRORS.md，已成功保留旧内容并追加新条目。

---

## [ERR-20260326-005] xhs-tags-became-body-text

**Logged**: 2026-03-26T11:12:00+08:00
**Priority**: high
**Status**: resolved
**Area**: xiaohongshu

### Summary
小红书发布时，pack 里的标签行被当作正文末尾一起发布，没有进入话题选择器，导致后台看到“所有标签都变成正文”。

### Error
```
发布后发现 pack 里的 #标签 行出现在正文中，未正确作为话题标签选入。
```

### Context
- 触发操作：使用 `publish_with_guard.py --pack ... --step full` 发布两条小红书内容
- 现象：pack 的正文末尾标签行（如 `#AI安全 #LiteLLM ...`）被直接灌入编辑器，变成正文文本
- 根因：`publish_with_guard.py` 之前直接调用 `cdp_publish.py publish`，绕过了 `publish_pipeline.py` 中的 `_extract_topic_tags_from_last_line()` + `_select_topics()` 逻辑；因此标签没有被识别并注入话题选择器，只作为普通正文保留

### Suggested Fix
1. `publish_with_guard.py` 不再直调 `cdp_publish.py publish`，统一改走 `publish_pipeline.py`
2. 包装器在发布前从 `标签：` 字段重建最终标签行，并自动剥离正文末尾已有的 `#标签` 行，避免重复
3. 以后不要直接把带标签的正文传给 `cdp_publish.py publish`；有标签的发布统一走 `publish_with_guard.py` / `publish_pipeline.py`

### Metadata
- Reproducible: yes
- Related Files:
  - /Users/lucifinil_chen/.openclaw/skills/xiaohongshu/scripts/publish_with_guard.py
  - /Users/lucifinil_chen/.openclaw/skills/xiaohongshu/scripts/publish_pipeline.py

### Resolution
- **Resolved**: 2026-03-26T11:12:00+08:00
- **Notes**: 已热修 `publish_with_guard.py`：改为调用 `publish_pipeline.py`，并在包装器内重建 tags last line + 去重剥离旧标签行。未来 pack 中的 `标签：` 会进入话题选择器，而不是落成正文文本。

---

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
            continue
        
        if os.path.exists(task["output_path"]):
            mtime = os.path.getmtime(task["output_path"])
            if time.time() - mtime < 120:  # 2 分钟内更新
                result = read_file(task["output_path"])
                process_result(result)
                completed_sessions.add(session_key)
```

**优先级**: P0 - 架构级修复

---

## [ERR-20260326-006] rerank-sidecar-broken-venv-libpython

**Logged**: 2026-03-26T20:29:00+08:00
**Priority**: high
**Status**: resolved
**Area**: infra

### Summary
本地 rerank sidecar 健康检查失败，根因不是端口或 launchctl，而是 sidecar `.venv/bin/python3` 绑定的 Python 运行时损坏，缺失 `libpython3.12.dylib`，导致 launchd 反复拉起失败。

### Error
```
dyld: Library not loaded: @executable_path/../lib/libpython3.12.dylib
Referenced from: .../.venv/bin/python3
Reason: tried: .../.venv/lib/libpython3.12.dylib (no such file)
```

### Context
- 触发操作：heartbeat 检查 `http://127.0.0.1:8765/health`
- 现象：health 无响应，launchctl 任务存在但没有监听端口
- 根因：launchd log 显示 `.venv/bin/python3` 启动即 SIGABRT，缺少 `libpython3.12.dylib`

### Suggested Fix
1. 删除损坏的 `.venv`
2. 在 `services/local-rerank-sidecar/` 下重新 `uv sync`
3. 重启 `com.openclaw.local-rerank-sidecar`
4. 重新验证 `8765/health`

### Metadata
- Reproducible: yes
- Related Files:
  - /Users/lucifinil_chen/.openclaw/workspace/services/local-rerank-sidecar
  - /Users/lucifinil_chen/Library/LaunchAgents/com.openclaw.local-rerank-sidecar.plist

### Resolution
- **Resolved**: 2026-03-26T20:30:45+08:00
- **Notes**: 已删除损坏 `.venv`，在 `services/local-rerank-sidecar/` 下重新执行 `uv sync`，随后重启 `com.openclaw.local-rerank-sidecar`。日志显示模型加载完成，`GET /health` 已连续返回 `200`。

---

---

## [ERR-20260326-007] message-send-schema-buttons-required-workaround

**Logged**: 2026-03-26T22:32:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: infra

### Summary
`message(action=send)` 在部分调用路径下会被 schema 校验误要求提供 `buttons` 字段；即使只是普通文本发送，也可能因缺少 `buttons` 被拦下。

### Error
```
message(action=send) schema validation unexpectedly required `buttons`
```

### Context
- 触发操作：cron / agent 在 Telegram 渠道发送普通文本通知
- 现象：发送纯文本时仍被校验层要求传 `buttons`
- 根因：工具 schema / 调用适配层对 `buttons` 的必填判断过严，和“纯文本发送无需按钮”的预期不一致

### Suggested Fix
普通文本发送若遇到该校验，显式传空数组 `buttons=[]` 作为兼容绕过；后续再修 schema 本身。

### Metadata
- Reproducible: yes
- Related Files:
  - message tool send path
  - cron delivery / agent message send flows

### Resolution
- **Resolved**: 2026-03-26T22:32:00+08:00
- **Notes**: 今晚已通过传 `buttons=[]` 成功绕过，后续遇到同类报错优先采用该兼容写法。

---

### Error: `openclaw cron run --id` 使用了错误的 flag
```
unknown option '--id'
```

### Context
- 触发操作：HEARTBEAT.md 中引用 `openclaw cron run --id <job-id>`
- 现象：`--id` 不是有效选项
- 根因：OpenClaw CLI 的 cron run 子命令使用 positional argument `<id>`，不是 `--id` flag

### Suggested Fix
HEARTBEAT.md 中已修正为 `openclaw cron run <job-id>`（positional）。

### Metadata
- **Reproducible**: yes
- **Related Files**: HEARTBEAT.md

### Resolution
- **Resolved**: 2026-03-27T05:22:00+08:00
- **Notes**: HEARTBEAT.md 已修正。CLI 正确用法是 `openclaw cron run <id>`（positional），不是 `--id <job-id>`。

## [ERR-20260327-004] xiaohongshu-publish-manual-browser-fallback-corrupts-final-content

**Logged**: 2026-03-27T20:08:00+08:00
**Priority**: critical
**Status**: promoted
**Area**: docs

### Summary
小红书正式发布中，`publish_pipeline.py` 因页面结构变化失效后，main 改走 browser 手工补发，导致正文被覆盖、标签漂移、实际上传配图与发布包不一致。

### Error
```text
1. publish_pipeline.py 无法找到“上传图文”tab
2. browser tool 出现 element not found / locator.fill timeout / fields are required
3. browser 富文本框手工补标签后，正文被替换成仅剩 hashtags
4. 最终提交时未做标题/正文/标签/素材路径四项一致性强校验
```

### Context
- 目标平台：小红书
- 正确 owner：Step 7.5 应由 wemedia 执行，不应由 main 直接手工发布
- 发布包声明封面：`2026-03-27-deerflow-vs-openclaw_sq_v3.jpg`
- 实际上传素材：`2026-03-27-deerflow-vs-openclaw_sq.jpg`
- 正文一度出现 `1267/1000` 超限，说明 Step 6 平台适配并未完全收口

### Suggested Fix
1. 平台脚本/CDP/页面结构异常时，正式发布必须直接 `BLOCKED`
2. 禁止 main 用 browser 富文本表单临场补救正式发布
3. Step 7.5 只允许 wemedia 按最终发布包调用平台 skill
4. 提交前强校验：标题/正文/标签/素材路径与发布包一致；小红书额外校验标题≤20、正文≤1000、标签≤10
5. “发布成功”页面不能代替内容正确性验收

### Metadata
- Reproducible: yes
- Related Files: /Users/lucifinil_chen/.openclaw/workspace/AGENTS.md, /Users/lucifinil_chen/.openclaw/workspace/agents/wemedia/AGENTS.md, /Users/lucifinil_chen/.openclaw/workspace/TOOLS.md, /Users/lucifinil_chen/.openclaw/workspace/MEMORY.md
- See Also: ERR-20260327-003

### Resolution
- **Resolved**: 2026-03-27T20:08:00+08:00
- **Notes**: 已将该事故规则提升到主 AGENTS、wemedia AGENTS、TOOLS、MEMORY；后续正式发布禁止 main/browser 手工补发。

---

## 2026-03-27 — 版本化 skill 文档未以上一正式版为底稿，导致结构漂移

- 症状：`starchain` v2.9 contract / flowchart 与 v2.8 不共享同一章节骨架；exact-text edit 多次失败；通知规则与旧 reference 容易漂移。
- 根因：v2.9 采用了重新撰写/抽象重构，而不是从 v2.8 正式版复制后做 delta 修改。
- 证据：`pipeline-v2-8-contract.md` 552 行 → `pipeline-v2-9-contract.md` 197 行；`PIPELINE_FLOWCHART_V2_8_EMOJI.md` 324 行 → `V2_9` 122 行；语言、结构、抽象层级整体重写。
- 教训：新版本 contract / flowchart 必须以上一正式版为底稿复制演进，保留稳定锚点（通知、重试、路径、回滚、Step 定义），再做差量修改。
- 修复：已将该规则写入 `skills/starchain/SKILL.md` 与 `skills/stareval/SKILL.md` 的 Version Policy。


## 2026-03-27 — NotebookLM 配图流程违规 + gateway artifact 参数兼容问题

### 现象
- DeerFlow × OpenClaw 这条内容的配图没有按 Step 5 硬规则使用 NotebookLM 生成。
- 没有执行“临时 notebook → 单一干净 source → 生成 → 下载 → 删除临时 notebook”的完整生命周期。
- 尝试用 `~/.openclaw/skills/notebooklm/scripts/nlm-gateway.sh artifact --subcmd generate` 生成时失败，报错：`No such option: -n`。

### 根因
1. 执行时越过了 wemedia / NotebookLM 的既定生图规范，直接用了非 NotebookLM 产物顶替。
2. `nlm-gateway.sh` 当前 `artifact generate` 封装与现版 `notebooklm` CLI 不兼容：脚本内部调用形态相当于 `notebooklm generate -n <id> ...`，但现版 CLI 需要 `notebooklm generate infographic -n <id> ...`。

### 正确做法
- 必须严格走：
  1. `notebooklm create temp-*`
  2. 向临时 notebook 添加 **单一干净 source**
  3. `notebooklm generate infographic -n <temp_id> ... --wait`
  4. `notebooklm download infographic ...`
  5. 删除临时 notebook
- 如 gateway 的 artifact 封装未修复，允许在**仅此环节**改走原生 `notebooklm` CLI，但不能跳过临时 notebook 生命周期。
- 生成完后要把发布包图片路径更新到真实的 NotebookLM 产物路径，并保留最小审计记录。

### 本次修复落点
- 新图：`intel/collaboration/media/wemedia/xiaohongshu/2026-03-27-deerflow-vs-openclaw_sq_nlm.jpg`
- 审计：`intel/collaboration/media/wemedia/xiaohongshu/2026-03-27-deerflow-vs-openclaw_nlm_audit.md`
- 已删除临时 notebook，完成清理。

## 2026-03-27 — message(action=send) + targets 静默回退到当前私聊

### 现象
- 使用 `message(action="send")` 时误传 `targets` 数组，没有报错。
- 消息未发送到预期群，而是静默落回当前私聊会话。

### 根因
- OpenClaw 的单发动作 `send` 只接受 `target`（内部转为 `to`）。
- `targets` 仅适用于 `action="broadcast"`。
- 旧运行时缺少对 `send + targets` 的硬拦截，导致没有显式目标时，`normalizeMessageActionInput()` 把目标回退为 `toolContext.currentChannelId`，于是消息发回当前私聊。

### 修复
1. 在本机运行时热修 `channel-actions-*.js`：`send` 遇到 `targets` 直接报错：
   `Use \`target\` for single-recipient actions. \`targets\` is only valid with action=\`broadcast\`.`
2. 重启 gateway 使补丁生效。
3. 在 `TOOLS.md` 记录硬规则：单发用 `target`，多目标必须串行单发或改用 `broadcast`。

### 验证
- 负向验证：`send + targets` 现在会直接返回错误，不再静默回退。
- 正向验证：`send + target` 已成功发到监控群 `-5131273722`（messageId `28836`）。

### 备注
- 这是本机安装包层的热修，未来 OpenClaw 升级可能覆盖，需要保留此经验并在升级后复验。

---

## [ERR-20260328-001] openclaw CLI structured output polluted by plugin preamble

**Logged**: 2026-03-28T11:22:00+08:00
**Priority**: medium
**Status**: known_quirk
**Area**: exec / openclaw CLI parsing

### Summary
通过 `exec` 调 `openclaw browser status`、`openclaw cron runs`、`openclaw cron list` 等命令时，命令实际输出前会先打印多行 plugin preamble（例如 memory-lancedb-pro / mdMirror / memory-reflection 注册日志），导致直接按 JSON 或固定首行解析时失败。

### Symptom
- `python -c 'json.load(sys.stdin)'` 解析失败
- 预期第一行是状态 / JSON，实际前面混入 `[plugins] ...` 多行日志
- 需要额外 `grep` / `awk` / `tail` 过滤才能拿到结构化正文

### Root Cause
OpenClaw CLI 启动时会输出 runtime plugin 注册日志；这些日志与真正命令结果共用 stdout / stderr，导致 `exec` 场景下的结构化解析不稳定。

### Workaround
1. 不要假设 `openclaw ...` 输出从第一行就是正文
2. 对结构化结果先过滤 plugin preamble，再做 JSON 解析
3. 类似 `cron runs` 场景优先用 `tail -40` / `awk 'BEGIN{show=0} ...'` 等方式截取正文

### Preventive Rule
凡是用 `exec` 调 `openclaw` CLI 且要做解析时，默认先考虑 preamble 污染；不要直接把整段 stdout 送进 JSON parser。

## 2026-03-28 wemedia sessions_spawn model not allowed: opus

- **错误**: `sessions_spawn(agentId="wemedia", model="anthropic/claude-opus-4-6")` → `model not allowed`
- **原因**: wemedia agent 的 allowedModels 列表不含 opus，只含 sonnet 及以下
- **修复**: 改用 `anthropic/claude-sonnet-4-6`，spawn 成功
- **防止重犯**: spawn wemedia 时默认用 sonnet；如需 opus，先用 `agents_list` 或查 openclaw.json 确认 allowedModels

## 2026-03-28 NotebookLM infographic 已知限制

1. **只输出横图（2752×1536）**，不支持方图；需要 padding 补白边转为 1:1
2. **语言不可控**：即使 prompt 写"全中文"，生成结果可能仍为英文或中英混杂
3. **乱码风险**：部分文字段落可能生成乱码（Latin 字符替换中文）
4. **缓解措施**：prompt 中反复强调"ALL TEXT IN SIMPLIFIED CHINESE"；若仍出英文，视情况接受或重生成

## 2026-03-28 NotebookLM infographic 方图参数

- **正确命令**：`notebooklm generate infographic --orientation square --style bento-grid --language zh_Hans --detail detailed --wait "..."`
- **关键**：必须加 `--orientation square`，否则默认输出横图（2752×1536）
- **语言**：提前执行 `notebooklm language set zh_Hans`，或在 generate 时加 `--language zh_Hans`
- **不要用 padding 补白边**：直接生成原生方图，padding 方案会损失布局完整性

## 2026-03-28 wemedia 配图走捷径 + announce 不可靠

### 根因1：配图命令错误导致 agent 走捷径
- `--json --wait` 连用报错 → agent 放弃走 NotebookLM，复用目录旧图
- `notebooklm delete -n <id> -y` 语法错误（不支持此格式）
- 修复：AGENTS.md Step 5 已更新为今晚验证通过的正确命令格式

### 根因2：announce 不触达 main 主会话
- mode=run isolated session 的 announce 是 best-effort，不保证到达 main
- 今晚至少3次 wemedia 完成但 main 未收到通知
- 修复：AGENTS.md 推送规范加注 ⚠️，要求 Step 7.5 完成后必须主动 message 自媒体群

### 正确的 notebooklm 命令（已验证）
```bash
notebooklm create "temp-{主题}-$(date +%s)"   # 创建
notebooklm use <id>                             # 切换
notebooklm source add /tmp/file.txt            # 加 source
notebooklm language set zh_Hans               # 设语言
notebooklm generate infographic \
  --orientation square \                        # 必须加，否则出横图
  --style bento-grid \
  --language zh_Hans \
  --detail detailed \
  --wait "..."                                  # 只用 --wait，不加 --json
cd /output/dir && notebooklm download infographic filename.png --force
notebooklm use <id> && notebooklm delete -y   # 删除方式
```

## 2026-03-29 persistent session 在 Telegram 直聊不可用

- `mode="session"` 需要 `thread=true`，但 Telegram 直聊没有注册 subagent_spawning hooks
- `thread=true` 只在 Discord thread 环境下可用
- **结论**：Telegram 主通道只能用 `mode="run"` isolated session
- **替代方案**：mode=run + 任务里硬性要求 sessions_send 回 main（Step 6/7.5 完成时）


## 2026-03-29 新建 agent 必须显式配置 tools.allow + subagents.allowAgents
- **现象**：织梭（weaver）spawn 后，用 gateway CLI 尝试调用 sessions_spawn/sessions_send，报 `unknown method: sessions.spawn`
- **根因**：openclaw.json 里 weaver agent 没有配置 tools 字段，默认只有基础工具（read/write/exec/browser），没有 sessions_spawn/sessions_send/message
- **修复**：在 openclaw.json weaver agent 条目加 tools.allow 和 subagents.allowAgents，gateway restart
- **预防**：新建需要编排其他 agent 的 agent，必须同时配置：
  1. agents.list 条目（id/workspace/model）
  2. bindings（群绑定）
  3. allowAgents（主 agent 的 subagents.allowAgents）
  4. **tools.allow（含 sessions_spawn/sessions_send/message）**
  5. **subagents.allowAgents（可 spawn 的子 agent 列表）**


## 2026-03-29 新建 agent 必须调用 agent-config-generator skill
- **现象**：新建 weaver agent 时，IDENTITY/SOUL/HEARTBEAT/USER/TOOLS 全部用了系统默认空壳模板
- **根因**：只写了 AGENTS.md，没有调用 agent-config-generator skill 生成配置三件套
- **修复**：手动补写五件套文件
- **预防**：新建任何 agent 时，必须先读 agent-config-generator SKILL.md，用它生成 SOUL/IDENTITY/HEARTBEAT，再手写 AGENTS.md


## 2026-03-29 编排型 agent 必须配置 maxSpawnDepth:2
- **现象**：织梭 sessions_spawn 调用报 `Tool sessions_spawn not found`
- **根因**：OpenClaw 默认 maxSpawnDepth:1，depth-1 subagent 无法 spawn depth-2 子 agent；tools.allow 里加 sessions_spawn 无效，必须通过 maxSpawnDepth 控制
- **修复**：在 weaver agent 条目的 subagents 里加 `maxSpawnDepth: 2`
- **预防**：新建需要 spawn 子 agent 的编排型 agent，必须在 openclaw.json 对应 agent 条目加 `subagents.maxSpawnDepth: 2`
- **注意**：maxSpawnDepth 范围 1-5，推荐用 2（main→织梭→worker），不要超过需要


## 2026-03-29 织梭 spawn 子 agent 后必须调用 sessions_yield
- **现象**：织梭 spawn 2A 后等待 2B，session 自动结束，流程中断
- **根因**：OpenClaw auto-announce 是 push-based，子 agent 完成时推回给织梭，织梭 session 必须保持活跃才能接收；不调用 sessions_yield 则 session 结束，announce 无人接收
- **修复**：在 weaver tools.allow 加入 sessions_yield；每次 sessions_spawn 后立即调用 sessions_yield 挂起等待
- **预防**：编排型 agent 在 spawn 子 agent 后必须调用 sessions_yield，不得依赖 auto-announce 被动等待
