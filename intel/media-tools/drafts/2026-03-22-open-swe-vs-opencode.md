# 小红书草稿：Open-SWE vs OpenCode — 开源 Coding Agent 分化

**创建时间**: 2026-03-22
**流水线**: M级
**状态**: 待晨星确认

---

## 标题（≤20字）

开源 Coding Agent 开始分叉了

---

## 正文

同样是"开源 Coding Agent"，两个项目正在走向完全不同的未来。

**Open-SWE（LangChain 刚发布）**
是给工程团队构建"内部 Coding Agent"的框架。
不是工具，是架构蓝图。

Stripe 有 Minions，Ramp 有 Inspect，Coinbase 有 Cloudbot——
这些大厂的内部 Coding Agent 都不对外。

Open-SWE 把这套架构开源了：
- 在 Slack / Linear 里 @ 它，它去开一个隔离的云沙箱
- 帮你改代码、跑测试、自动提 PR
- 你盯着 Linear 票，它异步跑完回来汇报

适合：懂 LangGraph、想给团队定制工作流的工程师

---

**OpenCode（120K stars，月活 500 万）**
是直接给开发者用的 AI 编程代理。
装好就能用，终端 / 桌面 / IDE 全覆盖。

Ramp 构建 Inspect 时，底层直接 Composed on OpenCode——
换句话说，Open-SWE 对标的那些大厂，有人是用 OpenCode 起家的。

支持 75+ LLM 提供商，LSP 智能补全，多会话并行，
还有桌面版 Beta（macOS/Windows/Linux 全平台）

适合：独立开发者 / 中小团队，开箱即用

---

**为什么说这是"分化"而不是竞争？**

Open-SWE 的假设是：你需要深度定制，工作流比界面更重要
OpenCode 的假设是：你需要立刻上手，产品体验比架构控制更重要

两者不是同一个跑道的选手。

开源不等于同路。
一个在卖工程能力，一个在卖产品体验。

如果你是个人开发者——OpenCode，现在就装
如果你在给团队搭内部工具——Open-SWE 值得研究

---

**一个有意思的细节**
Open-SWE 的 README 里，Ramp 的对比列是 "Composed (OpenCode)"
也就是说，OpenCode 已经成了大厂拿来"二次开发"的底层了。

同一个开源项目，既是终端用户的工具，也是企业开发者的脚手架。
这才是 120K stars 的真实含义。

---

## 标签（≤10个）

#AI编程 #Coding Agent #开源工具 #LangChain #OpenCode #程序员 #AI工具 #开发者工具 #工程效率 #软件工程

---

## 图片建议

一张对比图（简洁）：
- 左：Open-SWE → 框架 → 异步工程流 → 面向团队
- 右：OpenCode → 产品 → 即开即用 → 面向个人

或用 NotebookLM 生成 infographic。

---

## 数据来源（发布不用放，内部存档）

- Open-SWE: github.com/langchain-ai/open-swe，发布时约 7.9K stars，34 个活跃 PR
- OpenCode: opencode.ai，GitHub 120K stars，月活 500万
- Ramp Inspect 对 OpenCode 的引用：Open-SWE README 对比表格
