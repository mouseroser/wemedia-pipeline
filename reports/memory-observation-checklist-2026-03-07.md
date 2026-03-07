# Memory Observation Checklist - 2026-03-07

## Purpose
Use the current memory system normally, then only adjust it when a real miss appears.

This checklist exists to prevent two bad patterns:
- blind over-tuning
- forgetting what counts as a real problem

## Current Baseline
- runtime memory plugin: `memory-lancedb-pro`
- embeddings: local Ollama + `nomic-embed-text`
- plugin stage: P1
- `autoRecall = true`
- `autoCapture = true`
- `captureAssistant = false`
- `rerank = none`
- `enableManagementTools = false`

## What Counts As Healthy
The system is healthy if most day-to-day recall works for:
- user identity and naming facts
- strong user preferences
- pipeline hard rules
- recently fixed operational decisions
- repeated environment facts

It does not need to perfectly recall every long paragraph from old markdown in natural chat.
That is normal. Long-form memory is mainly for archive and deeper lookup.

## What Counts As A Real Recall Miss
Treat it as a real miss only if all of these are true:
- the fact/rule matters in actual conversation or execution
- it has already been written to memory files or stored before
- the miss changes behavior, causes delay, or leads to a wrong answer
- the same or similar miss happens more than once, or is clearly high-impact

## When To Add Atomic Memories
Add short atomic memories when the missed content is:
- a stable fact about 晨星
- a stable preference
- a recurring workflow rule
- a hard boundary for main / coding / review / pipeline execution
- an environment fact that affects repeated decisions

Preferred form:
- one rule or fact per sentence
- direct wording
- no extra storytelling

Examples:
- `和晨星对话默认使用中文。`
- `主私聊会话里，main 不承载长时间编排。`
- `生产 openclaw.json 默认只留本机，不直接推 GitHub。`

## When Not To Add Atomic Memories
Do not add atomic memories for:
- one-off tasks
- temporary experiments
- noisy logs
- low-value observations that will not affect future behavior
- details already easy to retrieve from docs or files and rarely needed in chat

## When To Update Long-Form Memory Instead
Prefer updating `MEMORY.md` or daily logs when the content is:
- a timeline of what happened
- a multi-step incident
- a deployment narrative
- a large troubleshooting note
- a detailed postmortem

## Quick Triage Flow
1. Did a real miss happen in normal use?
2. Was the missing fact already recorded somewhere?
3. Is it high-frequency or high-impact?
4. If yes, add one short atomic memory.
5. If the miss is about long historical detail, keep it in long-form memory instead.
6. If recall quality drops broadly, check plugin/runtime health before adding more content.

## Quick Verification Commands
```bash
openclaw status
openclaw plugins info memory-lancedb-pro
openclaw memory-pro stats
openclaw memory-pro search --limit 5 'your query here'
openclaw memory search --query 'your query here' --json
```

## Known Boundaries To Remember
- `memory_forget` does not auto-delete markdown mirror lines
- chat recall is strongest for short atomic memories
- long-form imported markdown is still useful, but better for archive and CLI lookup than fast chat recall
- rerank is still off, so retrieval quality should be judged with that in mind

## Recommended Mode From Now On
Normal use first.

Only tune when:
- a real miss appears
- the miss matters
- the fix is obvious and small

That keeps the memory system useful instead of bloated.
