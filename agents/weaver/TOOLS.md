# TOOLS.md - 织梭环境坑位

## 工具权限
织梭在 openclaw.json 中配置的 tools.allow：
```
read, write, exec, sessions_spawn, sessions_send, sessions_list, subagents, message, sessions_yield
```

## sessions_spawn 规范
- **严禁用 exec/CLI** 代替 sessions_spawn/sessions_send
- spawn 后必须立即 sessions_yield，不轮询
- thinking 默认 off，不传或显式 thinking="off"
- 子 agent 回传给织梭：`sessions_send(sessionKey="agent:weaver:subagent:{当前织梭runId前8位}", message=...)`
  - ⚠️ 注意：sessionKey 是运行时动态生成的，必须在任务 prompt 里明确告知子 agent 当前织梭的 sessionKey

## 文件路径规范
- 草稿：`/Users/lucifinil_chen/.openclaw/workspace/intel/collaboration/media/wemedia/drafts/A/{内容ID}.txt`
- 配图：`/Users/lucifinil_chen/.openclaw/workspace/intel/collaboration/media/wemedia/images/{内容ID}-cover.png`
- 发布包：`/Users/lucifinil_chen/.openclaw/workspace/intel/collaboration/media/wemedia/publish/{内容ID}/`
- 所有路径传给子 agent 时必须用绝对路径

## 群组 ID
- 织梭群（进度通知）：`-5121683303`
- 织梦群（gemini）：`-5264626153`
- 小曼群（openai）：`-5242027093`
- 小克群（claude）：`-5101947063`
- 珊瑚群（notebooklm）：`-5202217379`
- 自媒体群：`-4671481614`

## 已知坑位
- **gateway 重启会丢失 yield 状态**：若 gateway 在织梭 yield 期间重启，织梭被唤醒后可能提前结束，main 需手动 spawn 新 session 从断点继续
- **notebooklm 语言代码**：必须用 `zh_Hans`，不能用 `zh`
- **配图默认横版**：必须加 `--orientation square` 才输出 1:1 方图
- **message 单发用 target**：不要用 targets，多目标串行发送
