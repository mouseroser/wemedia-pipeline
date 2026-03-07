# Memory Rollout Changelog - 2026-03-07

## Goal
Repair OpenClaw memory search, deploy `memory-lancedb-pro`, import historical memory, stabilize chat-side recall, and leave a clean local audit trail.

## Final Result
- Built-in `memory_search` repaired and back to hybrid vector retrieval
- `memory-lancedb-pro` deployed as the active runtime memory plugin
- Plugin running in P1 mode with local Ollama embeddings
- Historical long-term memory imported into plugin storage
- Chat-side recall stabilized by adding atomic memories for high-frequency facts, preferences, and rules
- Workspace ignore rules cleaned so runtime/plugin copies do not pollute Git

## Runtime State At End
- OpenClaw memory: `enabled (plugin memory-lancedb-pro)`
- Plugin version: `memory-lancedb-pro@1.1.0`
- Embedding model: `nomic-embed-text`
- Retrieval mode: `hybrid`
- Scope count: `1`
- Total memories in plugin store: `79`

## What Changed

### 1. Collaboration architecture rule landed
Rule standardized across workspace, agents, and pipeline docs:
- multi-agent non-formal materials -> `intel/collaboration/`
- formal outputs -> agent directories

Related local commit:
- `38ea4da` - Update: multi-agent collaboration material rules

### 2. Built-in memory search repaired
Problem:
- `memory_search` had degraded to `provider: none`, `mode: fts-only`

Fix:
- switched built-in file memory embeddings to local Ollama
- model: `nomic-embed-text`
- forced index rebuild with `openclaw memory index --force --agent main`

Related local commit:
- `71a96ef` - Fix memory search with local Ollama embeddings

### 3. Workspace repo cleaned
Fixes:
- added root `.gitignore`
- ignored `.DS_Store`, `plugins/`, `intel/collaboration/`
- removed tracked `.DS_Store` noise from index

Related local commit:
- `f1bb9d7` - Clean workspace ignores and record memory plugin rollout

### 4. memory-lancedb-pro deployed
Deployment:
- runtime copy promoted to `~/.openclaw/workspace/plugins/memory-lancedb-pro`
- plugin loaded via `openclaw.json`
- plugin slot switched to `memory-lancedb-pro`
- plugin trust allowlist added

Effective plugin direction:
- embeddings via local Ollama OpenAI-compatible endpoint
- `autoRecall` and `autoCapture` enabled in P1
- `captureAssistant = false`
- `rerank = none`
- `enableManagementTools = false`

Related local commit:
- `4207a4f` - Record P1 memory plugin validation

### 5. Chat recall tuned with atomic memories
Reason:
- imported long-form markdown memories were good for archive and CLI search
- chat-side `memory_recall` became much more reliable once high-frequency knowledge was duplicated into short atomic memories

Three tuning waves were added:
- personal facts and preferences
- pipeline boundaries and working rules
- runtime meta-rules and config habits

Related local commits:
- `41364cd` - Tune memory recall with atomic memories
- `4ac1a8e` - Add more atomic memory rules
- `335b790` - Record third round atomic memory tuning

### 6. Documentation snapshot added
Artifacts written:
- `reports/memory-system-status-2026-03-07.md`
- this changelog file

Related local commit:
- `bbef643` - Add memory system status snapshot

## Key Files
- Config: `/Users/lucifinil_chen/.openclaw/openclaw.json`
- Plugin runtime: `~/.openclaw/workspace/plugins/memory-lancedb-pro`
- Shared analysis copy: `~/.openclaw/workspace/intel/collaboration/memory-lancedb-pro`
- Long-term memory file: `MEMORY.md`
- Daily log: `memory/2026-03-07.md`
- Status snapshot: `reports/memory-system-status-2026-03-07.md`

## Known Boundaries
- `memory_forget` does not auto-delete markdown mirror lines
- rerank is still disabled
- management tools are still disabled
- plugin is stable enough for use, but further tuning should happen only after real misses in normal conversation

## Recommendation
Do not keep tuning blindly.

Best next mode:
- use the system normally
- only add new atomic memories when a real miss happens
- keep long-form memory for archive, and short-form memory for repeated conversational recall
