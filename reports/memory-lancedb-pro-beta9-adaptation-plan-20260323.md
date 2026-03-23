# memory-lancedb-pro beta.9 适配实施清单（2026-03-23）

## 目标
在不破坏当前 runtime 自定义补丁（Layer 3 fallback / rerank sidecar / runtime worktree）的前提下，定向吸收 v1.1.0-beta.9 中对当前实例最有价值的修复。

## 采用策略
**Selective backport**：不整包升级，不直接 reset 到 beta.9；仅 cherry-pick 安全增益 commits，并保留本地运行时补丁。

## 必吸收 commits
1. `a4f9b8d` — sanitize reflection lines before prompt injection
2. `df37c36` — sanitize cached reflection slices before injection
3. `3c102df` — stop storing injectable reflection recall entries
4. `d337523` — pass excludeInactive to all retrieval search paths
5. `1a3e0a4` — declare apache-arrow as a direct runtime dependency

## 有条件吸收
6. `d868fe3` — temporal supersede semantics for mutable facts
7. `3e8d0b1` — route memory_update through supersede for temporal-versioned categories

## 本地补丁保留点
- Layer 3 fallback 直调 `nlm-gateway.sh`
- timeout 保持 75 秒（不能退回 upstream 默认 45 秒）
- 4F trigger 阈值保持本地配置
- runtime worktree: `runtime/layer3-fallback-active`
- 任何 `resolveRuntimeAgentId(... ) || 'main'` 类兼容补丁不能丢
- 本地 rerank sidecar: `127.0.0.1:8765` + `BAAI/bge-reranker-v2-m3`

## 验收清单
1. `memory_stats` 正常
2. `memory_list` 正常
3. `memory_recall` 不混入 superseded / inactive 条目
4. Layer 3 fallback 仍可触发，且 timeout / trigger 维持本地口径
5. rerank sidecar 正常工作
6. gateway restart 后无启动回归

## 回滚
- 备份目录：`~/.openclaw/backups/memory-lancedb-pro/`
- 当前适配分支：`adapt/beta9-selective-20260323`
- 原运行分支：`runtime/layer3-fallback-active`
