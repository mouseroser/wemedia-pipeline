# 每周故障排查清理报告

**报告周期**: 2026-03-16 (周一) ~ 2026-03-22 (周日)
**生成时间**: 2026-03-22 23:30 CST
**上周综合健康评分**: 72/100
**本周综合健康评分**: 68/100 ⬇️

---

## 一、错误日志统计

### 总量趋势
| 日期 | 错误数 | 趋势 |
|------|--------|------|
| 03-16 (一) | 374 | 基线 |
| 03-17 (二) | 492 | ↑ |
| 03-18 (三) | 979 | ⬆️ |
| 03-19 (四) | 986 | ⬆️ |
| 03-20 (五) | 971 | ⬆️ |
| 03-21 (六) | 2,137 | 🔴 峰值 |
| 03-22 (日) | 1,710 | 🔴 |
| **本周总计** | **7,649** | vs 上周 2,609 ↑193% |

### 错误分类
| 错误类型 | 数量 | 占比 | 变化 |
|----------|------|------|------|
| API Rate Limit | 1,162 | 15.2% | ⬆️ 198% (vs 上周 389) |
| Model Fallback | 957 | 12.5% | ⬆️ |
| web_fetch/search Blocked | 721 | 9.4% | 🆕 新增 |
| Timeout | 661 | 8.6% | ⬆️ 94% (vs 上周 341) |
| WhatsApp | 455 | 5.9% | 🆕 新增 |
| Telegram | 189 | 2.5% | — |
| Gateway Draining | 3 | <1% | ⬇️ |

### 3/21-22 峰值根因
- **小红书发布密集操作**：3 篇连发 + 多次重试 + MiniMax 反复空跑 → 大量 timeout + rate limit
- **web_fetch blocked**：721 次 private/internal IP 拦截（OpenClaw 安全策略阻止非公网 URL）
- **WhatsApp 未连接**：xhs-content-data-sync cron 尝试用 WhatsApp 发消息失败

---

## 二、本周已解决问题 ✅

### 1. Layer 3 Session Lock 彻底修复 (P0→Resolved)
- **03-17**: Layer 3 fallback 调用从 `openclaw agent --agent notebooklm` 改为直接调用 `nlm-gateway.sh`
- **连续 6 天无 session lock**，确认修复稳定
- 同时修复 `memory-lancedb-pro` 的 typecheck 错误（`src/llm-client.ts` response typing）

### 2. MiniMax 国内 API 切换 (P1→Resolved)
- **03-20**: 从国际版 `api.minimax.io` 切换到国内版 `api.minimaxi.com`
- 所有 8 个 agent 的 minimax profile key 已更新
- 验证通过

### 3. CDP 发布链路多处修复 (P1→Resolved)
- **03-19**: Chrome IPv6 绑定问题（`[::1]` vs `127.0.0.1`），修复 cdp_publish.py 默认连 `localhost`
- **03-19**: CDP 端口从 9222→9223（避免与主 Chrome 冲突）
- **03-20**: `_evaluate` 中 `arguments` 关键字在箭头函数 IIFE 不存在的 bug
- **03-21**: 小红书话题标签 ≤10 个限制写入规则

### 4. Layer 3 Fallback 阈值微调 (P2→Resolved)
- **03-22**: minScore 0.5→0.35, minAvgScore 0.4→0.3
- 弱查询（top1 0.35-0.5 区间）现在更容易触发 L3

### 5. PR #227 收口 (P2→Resolved)
- **03-17**: maintainer 回复后关闭（PR 只有测试文件，未连入 CI）
- 改跟踪 PR #206

### 6. web_search 修复 (P2→Resolved)
- **03-22**: Brave Search API 已接入，替代之前缺 `BRAVE_API_KEY` 的退化状态

### 7. Cron 稳态优化完成 (P2→Resolved)
- 所有 minimax cron 收敛为"单脚本/单动作/少判断"格式
- memory-compression 改 Sonnet，memory-archive-weekly-sync 简化为直接调用脚本

---

## 三、未解决 / 持续观察问题 🔴🟡

### 🔴 P0: API Rate Limit 激增
- 1,162 次限流，比上周增长 198%
- 主要发生在密集操作期间（小红书发布 + cron 并行）
- **建议**: 评估 Anthropic API 配额/tier；考虑高峰错峰

### 🔴 P0: WhatsApp 通道未连接
- 455 个 WhatsApp 错误："No active WhatsApp Web listener"
- xhs-content-data-sync cron 因此失败（consecutiveErrors: 1）
- **需要**: 重新连接 WhatsApp (`openclaw channels login --channel whatsapp`)

### 🟡 P1: web_fetch 被安全策略阻止 (721 次)
- `Blocked: resolves to private/internal/special-use IP address`
- 与之前的踩坑记录一致（openai.datas.systems 图片 URL）
- **缓解**: 已知 workaround（curl 下载到本地再用 filePath）

### 🟡 P1: MiniMax 复杂任务不可靠
- 03-20/21: MiniMax 执行小红书发布流程多次空跑、跳步
- 已建硬性规则：外部发布/CDP/多步骤 → 禁用 MiniMax
- **持续观察**: 确保规则执行到位

### 🟡 P1: Cron 超时问题
- 03-22: minimax cron 运行 10 分钟超时 (600000ms)
- memory-observation-day6/day7 两个 cron 因 edit 操作失败（已 disabled）
- **建议**: 监控 cron 超时率

### 🟡 P2: NotebookLM Layer 3 超时
- 本次报告生成时 L3 查询 SIGTERM (timeout 50000ms)
- 不影响主功能（L2 正常），但 L3 可用性约 60-70%
- **持续观察**

### 🟡 P2: Telegram sendChatAction 间歇失败
- 189 次失败，非关键（不影响消息发送）
- 可能与 rate limit 或网络波动有关

---

## 四、Cron 健康状况

**总计 37 个 cron 任务**

| 状态 | 数量 | 说明 |
|------|------|------|
| ✅ 正常运行 | 31 | consecutiveErrors=0 |
| ⚠️ 错误但不严重 | 2 | memory-observation-day6/7 (已 disabled) |
| 🔴 需要关注 | 1 | xhs-content-data-sync (WhatsApp 未连接) |
| ⏳ 待首次运行 | 3 | memory-optimization-daily-20260323/24/25 |

**本周各 cron 最近运行状态**:
- ✅ layer2-health-check: ok
- ✅ memory-quality-audit: ok
- ✅ sync-high-priority-memories: ok
- ✅ NotebookLM 记忆同步: ok
- ✅ daily-memory-report: ok
- ✅ notebooklm-daily-query: ok
- ✅ todo-daily-check: ok
- ✅ media-signal-morning: ok
- ✅ media-morning-planning: ok
- ✅ media-signal-noon: ok
- ✅ media-signal-evening: ok
- ✅ media-daily-retro: ok
- ✅ openclaw-runtime-audit: ok
- ✅ check-memory-lancedb-pr-status: ok
- ✅ todo-autopilot-v1: ok
- ✅ post-upgrade-guard: ok
- ✅ MEMORY.md 维护: ok
- ✅ 记忆压缩检查: ok
- ✅ memory-archive-weekly-sync: ok
- ✅ troubleshooting-weekly-memory-update: ok
- ✅ openclaw-docs-update: ok
- ✅ layer1-compress-check: ok
- ✅ nlm-media-source-cleanup: ok
- 🔴 xhs-content-data-sync: **error** (WhatsApp)

---

## 五、记忆系统健康

| 指标 | 值 |
|------|-----|
| 总记忆数 | 388 |
| Scope | 1 (agent:main) |
| fact | 137 (35.3%) |
| decision | 160 (41.2%) |
| preference | 36 (9.3%) |
| reflection | 29 (7.5%) |
| entity | 18 (4.6%) |
| other | 8 (2.1%) |
| 检索模式 | hybrid (vector + keyword) |
| FTS 支持 | ✅ |
| Layer 2 可用性 | ✅ 正常 |
| Layer 3 可用性 | ⚠️ 间歇超时 |

---

## 六、本周重要教训

1. **MiniMax 模型边界**: 复杂多步骤 + 外部操作 = 禁区。已建硬性规则。
2. **小红书平台限制**: 标题 ≤20 字 + 话题 ≤10 个 + 连发需间隔。
3. **发布前必须 memory_recall**: 已有踩坑记录但 MiniMax 不查就执行。
4. **重复发布风险**: 发布前检查是否已有同标题笔记。
5. **通知可见性**: 涉及外部操作必须主动推送状态（开始/进度/错误/完成）。

---

## 七、下周关注项

1. [ ] WhatsApp 重新连接（xhs-content-data-sync 恢复）
2. [ ] 监控 rate limit 趋势（本周激增 198%）
3. [ ] 记忆优化观察期 Day 9-11（03-23/24/25 自动验证）
4. [ ] PR #206 状态跟踪
5. [ ] web_fetch blocked 持续监控

---

**综合评估**: 本周错误量显著上升（+193%），主因是小红书自媒体运营密集操作 + API 限流。核心基础设施（记忆系统、cron 编排、Layer 2）保持稳定。风险集中在 WhatsApp 通道和 API 配额。

_报告推送目标: 监控群 (-5131273722)_
