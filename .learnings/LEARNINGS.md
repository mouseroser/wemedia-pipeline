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
