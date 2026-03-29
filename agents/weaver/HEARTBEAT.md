# HEARTBEAT.md - 织梭

## 原则
织梭没有主动 heartbeat 职责。
如果收到 heartbeat，只检查当前是否有挂起任务未完成，有则上报 main，无则回 HEARTBEAT_OK。

## 检查项

```bash
# 是否有未完成的流水线任务
ls ~/.openclaw/workspace/intel/collaboration/media/wemedia/drafts/A/*.txt 2>/dev/null && echo DRAFT_PENDING || echo NO_DRAFT
```

## 输出格式

有挂起任务：
```
⚠️ 织梭有未完成任务
- 内容ID：{id}
- 当前阶段：{step}
- 需要 main 介入：是/否
```

无任务：
```
HEARTBEAT_OK
```
