# 路径索引 (PATHS.md)

> 所有 agent 共享的路径参考。路径找不到时先查这里。
> **单写者**: main

## 核心文档

| 文件 | 路径 |
|------|------|
| AGENTS.md | `~/.openclaw/workspace/AGENTS.md` |
| MEMORY.md | `~/.openclaw/workspace/MEMORY.md` |
| SOUL.md | `~/.openclaw/workspace/SOUL.md` |
| USER.md | `~/.openclaw/workspace/USER.md` |
| THESIS.md | `~/.openclaw/workspace/shared-context/THESIS.md` |
| FEEDBACK-LOG.md | `~/.openclaw/workspace/shared-context/FEEDBACK-LOG.md` |
| PATHS.md | `~/.openclaw/workspace/shared-context/PATHS.md` |
| CRON-MATRIX.md | `~/.openclaw/workspace/shared-context/CRON-MATRIX.md` |

## 配置

| 文件 | 路径 |
|------|------|
| openclaw.json | `~/.openclaw/openclaw.json` |
| notebooks.json | `~/.openclaw/skills/notebooklm/config/notebooks.json` |

## Skill 脚本

| Skill | 路径前缀 |
|-------|---------|
| notebooklm | `~/.openclaw/skills/notebooklm/scripts/` |
| nlm-gateway.sh | `~/.openclaw/skills/notebooklm/scripts/nlm-gateway.sh` |
| memory-manager | `~/.openclaw/skills/memory-architecture-manager/scripts/` |
| starchain | `~/.openclaw/skills/starchain/scripts/` |
| stareval | `~/.openclaw/skills/stareval/scripts/` |
| todo-manager | `~/.openclaw/skills/todo-manager/scripts/` |
| arch-generator | `~/.openclaw/skills/architecture-generator/scripts/` |
| update-openclaw-docs.sh | `~/.openclaw/skills/notebooklm/scripts/update-openclaw-docs.sh` |

## 守护 & 运维脚本

| 路径 | 说明 |
|------|------|
| `~/.openclaw/scripts/post-upgrade-guard.sh` | 升级后配置守护 |
| `~/.openclaw/scripts/start-local-rerank-sidecar.sh` | 启动 rerank sidecar |
| `~/.openclaw/scripts/status-local-rerank-sidecar.sh` | 检查 rerank 状态 |

## 插件 & 服务

| 组件 | 路径 |
|------|------|
| memory-lancedb-pro (runtime) | `~/.openclaw/runtime-plugins/memory-lancedb-pro/` |
| memory-lancedb-pro (workspace) | `~/.openclaw/workspace/plugins/memory-lancedb-pro/` |
| local-rerank-sidecar | `~/.openclaw/workspace/services/local-rerank-sidecar/` |

## 自媒体协作产物（intel/collaboration/media）

> **单写者原则**：每个子目录只有一个 agent 写，其他只读。

| 目录 | 负责 agent | 说明 |
|------|-----------|------|
| `intel/collaboration/media/wemedia/drafts/{A,B,C}/` | wemedia | 待发布内容草稿 |
| `intel/collaboration/media/wemedia/review/` | wemedia | 审查反馈存放 |
| `intel/collaboration/media/gemini/reviews/` | gemini | 审查报告 |
| `intel/collaboration/media/constitution/briefs/` | openai | 宪法简报 |
| `intel/collaboration/media/images/` | wemedia | 配图（NotebookLM 产出） |

## 星链协作产物（intel/collaboration/starchain）

> **单写者原则**：每个子目录只有一个 agent 写，其他只读。
> **所有星链流水线产物默认存放在此**，不再散落在各 agent 目录。

| 目录 | 负责 agent | 说明 |
|------|-----------|------|
| `intel/collaboration/starchain/specs/` | claude, openai, brainstorming | 宪法、计划、Spec-Kit、代码产出 |
| `intel/collaboration/starchain/reviews/` | gemini, claude | 扫描、一致性复核、Step3 双审报告 |
| `intel/collaboration/starchain/arbitration/` | openai, claude | 仲裁结论 |
| `intel/collaboration/starchain/research/` | notebooklm | 历史经验调研 |
| `intel/collaboration/starchain/test/` | test | 测试报告 |
| `intel/collaboration/starchain/docs/` | docs | 交付文档 |

> **读取规则**：消费者 agent 到对应目录读取，不在自己目录存星链产物。

## 数据目录

| 目录 | 说明 |
|------|------|
| `~/.openclaw/memory/` | 日志 (memory/YYYY-MM-DD.md) |
| `~/.openclaw/memory/lancedb-pro/` | LanceDB 向量数据库 |
| `~/.openclaw/todo/` | 执行计划 |
| `~/.openclaw/workspace/intel/` | Agent 间信息交换 |
| `~/.openclaw/workspace/shared-context/` | 跨 agent 共享知识 |
| `~/.openclaw/state/` | 状态文件 |
| `~/.openclaw/config-backups/` | 配置备份 |

## Telegram 群 ID

| Agent | 群名 | Chat ID |
|-------|------|---------|
| monitor-bot | 监控告警 | -5131273722 |
| coding | 代码编程 | -5039283416 |
| test | 代码测试 | -5245840611 |
| review | 交叉审核 | -5242448266 |
| brainstorming | 灵感熔炉 | -5231604684 |
| docs | 项目文档 | -5095976145 |
| gemini | 织梦 | -5264626153 |
| claude | 小克 | -5101947063 |
| openai | 小曼 | -5242027093 |
| notebooklm | 珊瑚 | -5202217379 |
| wemedia | 自媒体 | -5146160953 |
| nanobanana | 生图 | -5217509070 |
| 晨星 DM | 直接对话 | 1099011886 |

## ⚠️ 常见错误路径

| ❌ 错误 | ✅ 正确 |
|---------|---------|
| `~/.openclaw/skills/notebooklm/nlm-gateway.sh` | `~/.openclaw/skills/notebooklm/scripts/nlm-gateway.sh` |
| `~/.openclaw/scripts/layer2-health-check.sh` | `~/.openclaw/skills/memory-architecture-manager/scripts/layer2-health-check.sh` |
| `openclaw memory-pro` | `openclaw memory search` |
| `openclaw notebooklm` | 直接用 `notebooklm` CLI 或 `nlm-gateway.sh` |
