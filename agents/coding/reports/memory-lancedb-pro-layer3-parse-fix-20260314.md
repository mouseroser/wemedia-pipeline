# memory-lancedb-pro Layer 3 parse fix report

## Root cause
`openclaw agent --json` output is currently prefixed by plugin banner lines such as `[plugins] ...` before the actual JSON payload.

The old parser failed for two reasons:
1. `extractCandidateJson()` used a greedy regex for arrays/objects and preferred the earliest match.
2. Because stdout started with `[plugins] ...`, the parser treated that leading `[` as the first JSON candidate and tried to parse an invalid `[...]` slice instead of the later real JSON object.

There was also a shape mismatch in text extraction: current OpenClaw JSON output uses `result.payloads[0].text`, while the Layer 3 parser only looked at `content[0].text`, `text`, and `message`.

## Files changed
- `plugins/memory-lancedb-pro/src/tools.ts`
- `plugins/memory-lancedb-pro/test/layer3-fallback.test.mjs`

## What changed
### `src/tools.ts`
- Replaced the fragile regex-only JSON candidate extraction with balanced JSON segment scanning that respects quoted strings and escapes.
- Updated `extractCandidateJson()` to iterate candidates and return the first actually parseable JSON fragment.
- Exported `stripUnsafeControlChars`, `extractCandidateJson`, and `safeParseJson` for targeted regression testing.
- Extended Layer 3 text extraction to support current OpenClaw CLI JSON shape:
  - `result.payloads[0].text`
  - `payloads[0].text`
  - existing fallbacks remain intact

### `test/layer3-fallback.test.mjs`
- Updated default timeout assertion from `90` to `45`.
- Added regression test for banner-prefixed OpenClaw JSON output.
- Added regression test proving the parser skips `[plugins] ...` log lines and extracts the real JSON object.

## Evidence used
- Direct capture of `openclaw agent --json` stdout showed plugin banner lines before the JSON object.
- Running `safeParseJson()` against that captured stdout now succeeds in `extracted` mode and returns the expected `result.payloads[0].text` value.

## Build / test results
- `npm run build` ✅
- `node --test test/layer3-fallback.test.mjs` ✅
- Additional parser validation against captured real `openclaw agent --json` stdout ✅

## Commit
- `57e3990` — `fix layer3 notebooklm json parsing`
