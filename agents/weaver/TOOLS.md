# TOOLS.md — 织梭环境坑位

## 工具权限
- 可用：read / write / exec / sessions_spawn / sessions_send / sessions_list / subagents / message
- 不可用：browser / tts / canvas / nodes

## 关键群 ID
| 群 | ID |
|---|---|
| 织梭群（自己）| `-5121683303` |
| 织梦群（gemini）| `-5264626153` |
| 小曼群（openai）| `-5242027093` |
| 小克群（claude）| `-5101947063` |
| 珊瑚群（notebooklm）| `-5202217379` |
| 自媒体群（wemedia）| `-5146160953` |
| 监控群 | `-5131273722` |

## sessions_send 路由
- 回传 main：`sessionKey="agent:main:main"`
- 下发 wemedia：`label="wemedia-pipeline"`
- 下发 review：`sessionKey="agent:review:review"`

## 注意
- `message(action="send")` 单发必须用 `target`，不用 `targets`
- 配图生成必须用 `--orientation square`，临时 notebook 用完即删
