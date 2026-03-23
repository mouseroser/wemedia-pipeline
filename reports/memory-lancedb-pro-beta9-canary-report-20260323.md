# memory-lancedb-pro beta.9 canary 报告（2026-03-23）

## 结论
已按 **selective backport** 路线完成 beta.9 定向适配，并成功完成 gateway 重启后的上线验收。当前 canary 可用。

## 运行锚点（A 状态）
- Git tag: `canary-A-20260323-2126`
- Commit: `6a4c21d389b3d224b18e2268fc81bf6b82d47cf0`
- 说明：这是“已通过上线后验收”的可回退状态。

## 本次吸收内容
### 已吸收
1. `20e767d` — fix: sanitize reflection lines before prompt injection
2. `e7c2b69` — fix: declare apache-arrow as a direct runtime dependency
3. `6a4c21d` — test: align beta9 adaptation with local runtime policy

### 判定为空 cherry-pick（说明本地树已有等价实现）
- `df37c36` — sanitize cached reflection slices before injection
- `3c102df` — stop storing injectable reflection recall entries
- `d337523` — pass excludeInactive to all retrieval search paths

## 本地策略保留
- `resolveRuntimeAgentId(...) || 'main'` 保留
- Layer 3 仍走 `nlm-gateway.sh` 直调
- 默认 `sessionStrategy = none`
- reflection 对 ignore/override phrasing 保持更严格过滤

## 验收结果
### 重启前
- `memory-reflection.test.mjs`: 33 / 33 通过
- `plugin-manifest-regression.mjs`: 通过

### 重启后
- `memory_stats`: 正常
- `memory_list`: 正常
- `memory_recall`: 正常
- hybrid / FTS / scope/category 统计正常

## 回退方案（回到 A 状态）
如后续整理（B 阶段）出现问题，可回到当前已验证状态：

```bash
cd ~/.openclaw/runtime-plugins/memory-lancedb-pro
git checkout canary-A-20260323-2126
openclaw gateway restart
```

若需要连未提交改动一起回退，可参考备份：
- `~/.openclaw/backups/memory-lancedb-pro/post-canary-uncommitted-20260323-2126.diff`
- `~/.openclaw/backups/memory-lancedb-pro/post-canary-uncommitted-20260323-2126.status`

## 当前未整理项
这些是 runtime repo 里原先已存在的未提交改动，不属于本轮核心适配新增：
- `package-lock.json`
- `src/embedder.ts`
- `src/llm-client.ts`
- `src/reflection-retry.ts`
- `src/tools.ts`
- `src/embedder.ts.bak.openai`

## 建议
当前建议继续保持 canary 运行，并把本报告作为 B 阶段整理的基线。若后续继续清理 runtime 脏改动，应始终保证可以回退到 `canary-A-20260323-2126`。
