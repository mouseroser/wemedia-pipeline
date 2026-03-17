# Learnings

Append structured entries:
- LRN-YYYYMMDD-XXX for corrections / best practices / knowledge gaps
- Include summary, details, suggested action, metadata, and status


## [LRN-20260308-001] best_practice

**Logged**: 2026-03-08T03:07:34.594Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
launchd plist for local services should use the actual user-installed `uv` path, not assume `/opt/homebrew/bin/uv`

### Details
While installing the local rerank sidecar as a macOS LaunchAgent, the first plist used `/opt/homebrew/bin/uv` and failed with launchd exit code EX_CONFIG. On this machine the real binary is `/Users/lucifinil_chen/.local/bin/uv`. After correcting the ProgramArguments path, the service loaded and served health checks normally.

### Suggested Action
When generating launchd plists for uv-managed services, resolve `which uv` first and template the absolute path into the plist.

### Metadata
- Source: memory-lancedb-pro/self_improvement_log
---


## [LRN-20260310-001] best_practice

**Logged**: 2026-03-10T08:52:15.586Z
**Priority**: medium
**Status**: triage
**Area**: config

### Summary
Investigate last failed tool execution and decide whether it belongs in .learnings/ERRORS.md.

### Details
The reflection pipeline fell back; confirm the failure is reproducible before treating it as a durable error record.

### Suggested Action
Reproduce the latest failed tool execution, classify it as triage or error, and then log it with the appropriate tool/file path evidence.

### Metadata
- Source: memory-lancedb-pro/reflection:memory/reflections/2026-03-10/085156808-main-63206642-007a-4908-8e29-7b386bec.md
---


## [LRN-20260311-001] best_practice

**Logged**: 2026-03-11T01:17:45.376Z
**Priority**: medium
**Status**: triage
**Area**: config

### Summary
Investigate last failed tool execution and decide whether it belongs in .learnings/ERRORS.md.

### Details
The reflection pipeline fell back; confirm the failure is reproducible before treating it as a durable error record.

### Suggested Action
Reproduce the latest failed tool execution, classify it as triage or error, and then log it with the appropriate tool/file path evidence.

### Metadata
- Source: memory-lancedb-pro/reflection:memory/reflections/2026-03-11/011636579-main-be9f44a9-b53e-45e5-965e-6b191ce3.md
---


## [LRN-20260313-001] best_practice

**Logged**: 2026-03-13T08:34:29.610Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
NotebookLM-related investigations must use the notebooklm skill/openclaw-docs notebook route, not local docs or generic web fetch.

### Details
During investigation of OpenClaw subagent announce vs message behavior, I incorrectly tried local docs/web fetch first. Correct rule: for OpenClaw questions, query openclaw-docs via the notebooklm skill. Lack of a first-class tool name is not a valid reason to bypass the skill.

### Suggested Action
When the task mentions NotebookLM or OpenClaw docs, explicitly route through ~/.openclaw/skills/notebooklm/scripts/nlm-gateway.sh (or equivalent notebooklm skill path) before considering local docs.

### Metadata
- Source: memory-lancedb-pro/self_improvement_log
---


## [LRN-20260313-002] correction

**Logged**: 2026-03-13T09:17:38.286Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
When a NotebookLM notebook is deleted/recreated, update ~/.openclaw/skills/notebooklm/config/notebooks.json immediately or gateway queries will fail against stale IDs.

### Details
The `memory` notebook registry still pointed to stale id `a8e0fa9b-8194-45fb-abb2-0c4af40ecaba`, causing `GET_NOTEBOOK` / `GET_LAST_CONVERSATION_ID` errors. Creating a new notebook and updating the registry to `74a08007-d0a9-4cad-905d-14b9116f7765` restored queries.

### Suggested Action
When NotebookLM query errors mention GET_NOTEBOOK/GET_LAST_CONVERSATION_ID, compare `notebooklm list` against `config/notebooks.json` first; if the notebook was recreated, update the registry before any further diagnosis.

### Metadata
- Source: memory-lancedb-pro/self_improvement_log
---


## [LRN-20260313-003] best_practice

**Logged**: 2026-03-13T09:17:38.293Z
**Priority**: medium
**Status**: pending
**Area**: tests

### Summary
Do not judge mdMirror health by fallback directory existence alone; verify agent workspace mirrors under agents/*/memory first.

### Details
`mdMirror.dir` is only a fallback. In normal operation the plugin prefers mapped agent workspaces like `agents/<agent>/memory/YYYY-MM-DD.md`. Absence of `~/.openclaw/memory/memory-md/` does not mean Markdown mirroring is broken.

### Suggested Action
For mdMirror checks, inspect plugin behavior/docs and verify actual mirror files under agent workspaces before concluding there is a mirror failure.

### Metadata
- Source: memory-lancedb-pro/self_improvement_log
---


## [LRN-20260313-004] correction

**Logged**: 2026-03-13T14:42:25.249Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
For OpenClaw config-related questions, consult the openclaw-docs NotebookLM notebook first before relying on local docs/schema lookups alone.

### Details
User corrected that I forgot the established workflow: anything related to OpenClaw configuration should first be checked against the openclaw-docs notebook. In the recent investigation, I went straight to local docs and config schema. While those sources were valid, I skipped the preferred first source of truth for this setup.

### Suggested Action
When asked about OpenClaw configuration, behavior, architecture, or commands, first query/check the openclaw-docs notebook context, then use local docs/schema as verification or fallback.

### Metadata
- Source: memory-lancedb-pro/self_improvement_log
---


## [LRN-20260314-001] best_practice

**Logged**: 2026-03-14T00:39:22.640Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
Cron automation scripts must be self-contained, bounded, and warning-tolerant.

### Details
Discovered several concrete failure modes in night cron jobs: (1) sync-high-priority-memories depended on a manually pre-generated JSON file instead of querying memories itself; (2) notebooklm daily-query lacked per-query timeouts, allowing one external query to hang the whole job; (3) todo-daily-check used `grep -c ... || echo 0`, which produced `0\n0` and broke arithmetic; (4) memory-quality-audit exited non-zero for expected warnings, making the automation path brittle; (5) one cron job had announce delivery without a Telegram target.

### Suggested Action
For cron-facing scripts: make inputs self-generated when possible, add explicit timeouts around external calls, avoid shell constructs that duplicate numeric output under `set -e`, treat warnings as structured output rather than fatal exits, and always validate delivery targets on cron jobs.

### Metadata
- Source: memory-lancedb-pro/self_improvement_log
---
## [LRN-20260314-002] correction

**Logged**: 2026-03-14T10:39:00+08:00
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
GitHub / upstream language should follow repo context, not a blanket English-only rule.

### Details
I overgeneralized and treated all GitHub-facing communication as English-only. User clarified that this plugin is maintained in a Chinese context, so Chinese is appropriate. The correct rule is contextual: use the language that fits the repository/maintainer environment.

### Suggested Action
For `CortexReach/memory-lancedb-pro`, default to Chinese in issue/PR/comment/commit communication unless there is a clear reason to switch to English.

### Metadata
- Source: user_feedback
- Related Files: ~/.openclaw/workspace/.learnings/LEARNINGS.md
- Tags: github, upstream, language, correction, context-sensitive

---
## [LRN-20260315-001] best_practice

**Logged**: 2026-03-15T00:51:00+08:00
**Priority**: high
**Status**: promoted
**Area**: config

### Summary
Runtime-loaded plugins must use a dedicated runtime worktree; PR branches must never share the live plugin load path.

### Details
OpenClaw was loading `memory-lancedb-pro` directly from `~/.openclaw/workspace/plugins/memory-lancedb-pro`. During PR work, switching that repository between `feat/layer3-notebooklm-fallback` and `fix/skip-claude-review-on-fork-prs` changed the live runtime plugin code. After upgrading OpenClaw to v2026.3.13, the active runtime no longer saw the `layer3Fallback` schema and the config block was stripped from `~/.openclaw/openclaw.json`.

The hardened pattern is:
- runtime loads only from `/Users/lucifinil_chen/.openclaw/runtime-plugins/memory-lancedb-pro`
- PR branches use separate worktrees
- heartbeat verifies both `plugins.load.paths` and `plugins.entries["memory-lancedb-pro"].config.layer3Fallback` after upgrades

### Suggested Action
Keep runtime and PR worktrees permanently separated. Treat version changes as a trigger to verify and, if needed, restore the protected Layer 3 config block plus gateway restart.

### Metadata
- Source: simplify-and-harden
- Related Files: HEARTBEAT.md, ~/.openclaw/openclaw.json, ~/.openclaw/state/layer3-fallback-guard.json
- Tags: openclaw, plugin-runtime, worktree, upgrade-guard, layer3Fallback
- Pattern-Key: harden.runtime-plugin-worktree-isolation
- Recurrence-Count: 1
- First-Seen: 2026-03-15
- Last-Seen: 2026-03-15

---

## [LRN-20260316-002] correction

**Logged**: 2026-03-16T12:52:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
NotebookLM / OpenClaw docs / notebook 行为排查时，必须先按既有记忆规则走 notebooklm skill / notebook 路线；不能因为手头有别的相关 skill（如 memory-architecture-manager）就先走泛化排查。

### Details
用户明确指出这次排查没有先“查记忆”。而已有 learnings 已经写明：OpenClaw/NotebookLM 相关调查应优先走 notebooklm skill / openclaw-docs notebook 路线。此次我先用了 memory-architecture-manager skill 和本地 CLI 验证，虽然最后定位出部分根因，但执行顺序错了，属于“知道规则但没执行”。

### Suggested Action
以后遇到 NotebookLM、本地 notebook CLI、OpenClaw docs / config / notebook 行为相关问题：
1. 先回看既有记忆 / learnings；
2. 优先走 notebooklm skill 或其等效脚本入口（如 `~/.openclaw/skills/notebooklm/...`）；
3. 只有在该路径不可用时，才退回到其他相关 skill 或本地泛化排查。

### Metadata
- Source: user_feedback
- Related Files: .learnings/LEARNINGS.md, ~/.openclaw/skills/notebooklm/, ~/.openclaw/skills/memory-architecture-manager/
- Tags: notebooklm, skill-selection, execution-discipline, correction
- See Also: LRN-20260313-001, LRN-20260313-004
- Recurrence-Count: 2
- First-Seen: 2026-03-13
- Last-Seen: 2026-03-16

---

## [LRN-20260317-001] correction

**Logged**: 2026-03-17T02:55:00Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
在讨论 git worktree 清理时，必须明确区分“运行态路径”和“非运行态路径”；不能用“这个 worktree”之类的模糊指代。

### Details
在解释 PR #206 / Layer 3 fallback 相关 worktree 是否可退役时，我用了“要不要把这个本地 worktree 退役、清理掉”这种不够精确的说法。实际这里至少有 3 个不同角色的路径：正在被 openclaw.json 加载的 live runtime worktree、旧 PR worktree、以及其他非运行态 worktree。模糊表达会让人误以为我在推动删除当前运行中的 live 路径，属于表述不严谨，也容易制造被“引导/操纵”的观感。

### Suggested Action
以后凡是涉及 worktree / branch / runtime path 清理：
1. 先点名具体绝对路径；
2. 明确标出是否为当前配置加载路径；
3. 先给“不可动 / 可清理 / 待确认”三色分类，再谈删除；
4. 未完成分类前，不要提出“要不要直接清理”这种总括式问题。

### Metadata
- Source: user_feedback
- Related Files: ~/.openclaw/openclaw.json, ~/.openclaw/runtime-plugins/memory-lancedb-pro, ~/.openclaw/workspace/plugins/memory-lancedb-pro, ~/.openclaw/worktrees/memory-lancedb-pro/pr-187-refresh
- Tags: worktree, runtime-path, wording, correction, execution-discipline
- Pattern-Key: clarify.runtime-vs-nonruntime-paths
- Recurrence-Count: 1
- First-Seen: 2026-03-17
- Last-Seen: 2026-03-17

---

## [LRN-20260317-002] correction

**Logged**: 2026-03-17T14:45:00+08:00
**Priority**: high
**Status**: pending
**Area**: workflow

### Summary
When I promise a titled deliverable in-chat, “continue” means I should actually produce that deliverable, not just continue adjacent execution work.

### Details
I told the user I would provide a specific follow-up artifact: 《Layer 3 后续优化路线图（本地版 / 上游版双轨）》. Later, when the user said “继续”, I continued related execution items (cron scheduling / status follow-up), but did not actually write the promised roadmap. The user had to correct me explicitly. The failure was not lack of knowledge; it was losing track of the concrete promised output.

### Suggested Action
When I explicitly promise a named artifact (roadmap, checklist, report, draft, summary), treat that artifact as an open obligation. On the next “继续” or similar prompt, first check whether the promised artifact has already been delivered. If not, deliver it before doing adjacent work.

### Metadata
- Source: user_feedback
- Related Files: reports/layer3-dual-track-roadmap-20260317.md
- Tags: follow-through, promised-deliverable, correction, workflow

---

## [LRN-20260317-003] best_practice

**Logged**: 2026-03-17T14:52:00+08:00
**Priority**: low
**Status**: pending
**Area**: tooling

### Summary
Do not combine `cmd | python3 - <<'PY'` when the Python process is supposed to consume piped JSON on stdin; the heredoc script occupies stdin and the pipe input is lost.

### Details
While trying to parse `openclaw cron list --json`, I used a shell pattern like `openclaw cron list --json | python3 - <<'PY' ... PY`. Because `python3 -` reads the script from stdin via heredoc, the piped JSON never reached the Python code as data. This produced a confusing parse failure and is a reusable shell gotcha.

### Suggested Action
When parsing piped JSON with Python, use one of these instead:
1. `openclaw cron list --json | python3 -c '...'`
2. `python3 - <<'PY'` plus explicit subprocess call inside Python
3. write the JSON to a temp file, then read it from Python

### Metadata
- Source: error
- Related Files: .learnings/LEARNINGS.md
- Tags: shell, stdin, pipe, heredoc, parsing

---

## [LRN-20260317-004] best_practice

**Logged**: 2026-03-17T15:02:00+08:00
**Priority**: medium
**Status**: pending
**Area**: workflow

### Summary
Files under `~/.openclaw/todo/` are outside the workspace git repository: they can be edited directly, but cannot be committed with `git -C ~/.openclaw/workspace`.

### Details
I updated `~/.openclaw/todo/master-execution-plan.md` and then tried to commit it from the workspace repo. Git correctly failed because the file lives outside `/Users/lucifinil_chen/.openclaw/workspace` and `~/.openclaw` itself is not a git repository. This is a recurring boundary issue between “global OpenClaw config/task files” and “workspace-tracked files”.

### Suggested Action
Before committing, check whether the edited path is inside the current repository root. For `~/.openclaw/todo/`, `~/.openclaw/scripts/`, or other global paths outside `workspace/`, either:
1. leave them as direct filesystem edits without git commit, or
2. mirror the change into a workspace-tracked report/log if a commit trail is needed.

### Metadata
- Source: error
- Related Files: ~/.openclaw/todo/master-execution-plan.md, .learnings/LEARNINGS.md
- Tags: git, workspace-boundary, todo, repo-scope

---
