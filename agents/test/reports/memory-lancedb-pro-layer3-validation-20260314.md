# memory-lancedb-pro Layer 3 validation — 2026-03-14

## Final conclusion
**BLOCKED** — build and gateway startup are OK, but **runtime Layer 3 fallback is not actually enabled in `~/.openclaw/openclaw.json`**, so the fallback trigger path cannot be truthfully validated end-to-end.

## Scope
Task: rerun StarChain Step 5 validation for memory-lancedb-pro Layer 3 fallback changes in:
`~/.openclaw/workspace/plugins/memory-lancedb-pro`

Target verdict requested:
- PASS = build + config load + fallback path verified
- BLOCKED = build passes, but runtime validation is blocked with clear root cause

## 1) Current repo state
### Commands executed
```bash
cd ~/.openclaw/workspace/plugins/memory-lancedb-pro
pwd
git rev-parse --short HEAD
git status --short
git diff --stat -- src/tools.ts openclaw.plugin.json
rg -n "layer3Fallback|Layer 3|layer3" src openclaw.plugin.json test package.json .
```

### Results
- HEAD: `386b82d`
- Working tree shows Layer 3 related modifications still present:
  - `M openclaw.plugin.json`
  - `M src/tools.ts`
  - `?? test/layer3-fallback.test.mjs`
  - `?? openclaw.plugin.json.backup`
  - `?? src/tools.ts.backup`
- Diff stat for key files:
  - `openclaw.plugin.json | 263 insertions / edits`
  - `src/tools.ts | 415 insertions / edits`

## 2) Build + targeted test
### Commands executed
```bash
npm run build
node --test test/layer3-fallback.test.mjs
node test/plugin-manifest-regression.mjs
```

### Results
#### Build
- `npm run build` -> **PASS**
- Build path is typecheck-only:
  - `memory-lancedb-pro@1.1.0-beta.8 build`
  - `npm run typecheck`
  - `tsc -p tsconfig.json`

#### Targeted layer3 test
- `node --test test/layer3-fallback.test.mjs` -> **FAIL (1 failing assertion)**
- Failure:
  - test name: `defaults to disabled for backward compatibility`
  - expected timeout: `90`
  - actual timeout: `45`
- Important interpretation:
  - This failure is **not evidence that runtime fallback is broken**.
  - It shows the test expectation is stale vs current code default.

#### Manifest regression test
- `node test/plugin-manifest-regression.mjs` -> **PASS**
- Output included: `OK: plugin manifest regression test passed`

## 3) Code-side config/default evidence
### Commands executed
```bash
rg -n "DEFAULT_LAYER3_FALLBACK|resolveLayer3FallbackSettings|analyzeLayer3FallbackNeed|runNotebookLMFallbackQueryWithBudget" src/tools.ts index.ts
sed -n '1,220p' src/tools.ts
sed -n '3360,3415p' index.ts
sed -n '540,590p' openclaw.plugin.json
sed -n '960,995p' openclaw.plugin.json
```

### Evidence
#### In `src/tools.ts`
Current default object contains:
```ts
const DEFAULT_LAYER3_FALLBACK = {
  enabled: false,
  agent: "notebooklm",
  notebook: "memory-archive",
  notebookId: "",
  timeout: 45,
  ...
}
```
And resolver clamps timeout:
```ts
resolved.timeout = Math.min(resolved.timeout, 50);
```

#### In `index.ts`
`parsePluginConfig(...)` does support parsing `layer3Fallback` from runtime plugin config.

#### In `openclaw.plugin.json`
Manifest/schema includes `layer3Fallback`, and the file also contains a runtime-looking example/default block with:
```json
"layer3Fallback": {
  "enabled": true,
  "agent": "notebooklm",
  "notebook": "memory-archive",
  "timeout": 45,
  ...
}
```

## 4) Full gateway restart + startup evidence
### Commands executed
```bash
openclaw gateway restart
openclaw gateway status
tail -n 80 ~/.openclaw/logs/gateway.err.log
```

### Evidence
#### Restart happened
`~/.openclaw/logs/gateway.err.log` includes:
```text
2026-03-14T21:29:02.862+08:00 [diagnostic] wait for active embedded runs timed out: activeRuns=1 timeoutMs=90000
2026-03-14T21:29:02.864+08:00 [gateway] drain timeout reached; proceeding with restart
...
2026-03-14T21:31:55.644+08:00 [diagnostic] wait for active embedded runs timed out: activeRuns=1 timeoutMs=90000
2026-03-14T21:31:55.648+08:00 [gateway] drain timeout reached; proceeding with restart
```

#### Gateway is currently healthy after restart
`openclaw gateway status` returned:
- Runtime: `running`
- PID: `74208`
- RPC probe: `ok`
- Listening: `127.0.0.1:18789`

#### Plugin startup is visible after restart
Status output included:
```text
[plugins] memory-lancedb-pro@1.1.0-beta.8: plugin registered (db: /Users/lucifinil_chen/.openclaw/memory/lancedb-pro, model: nomic-embed-text, smartExtraction: ON)
[plugins] memory-lancedb-pro: diagnostic build tag loaded (memory-lancedb-pro-diag-20260308-0058)
```

### Restart interpretation
- Full restart evidence exists.
- Plugin loads after restart.
- No obvious startup crash from the Layer 3 change itself.

## 5) Runtime config load verification (critical)
### Commands executed
```bash
node - <<'NODE'
const fs=require('node:fs');
const p=process.env.HOME + '/.openclaw/openclaw.json';
const cfg=JSON.parse(fs.readFileSync(p,'utf8'));
const entry=cfg?.plugins?.entries?.['memory-lancedb-pro'];
console.log(JSON.stringify({
  pluginLoad: cfg?.plugins?.load,
  memorySlot: cfg?.plugins?.slots?.memory,
  entryPath: entry?.path,
  hasConfig: !!entry?.config,
  layer3Fallback: entry?.config?.layer3Fallback
}, null, 2));
NODE
```

```bash
node --input-type=module - <<'NODE'
import path from 'node:path';
import { readFileSync } from 'node:fs';
import jitiFactory from 'jiti';
const pluginSdkStubPath = path.resolve('test/helpers/openclaw-plugin-sdk-stub.mjs');
const jiti = jitiFactory(import.meta.url, { interopDefault: true, alias: { 'openclaw/plugin-sdk': pluginSdkStubPath } });
const { parsePluginConfig } = jiti('./index.ts');
const all = JSON.parse(readFileSync(process.env.HOME + '/.openclaw/openclaw.json', 'utf8'));
const runtimeCfg = all.plugins.entries['memory-lancedb-pro'].config;
const parsed = parsePluginConfig(runtimeCfg);
console.log(JSON.stringify({ runtimeLayer3: runtimeCfg.layer3Fallback, parsedLayer3: parsed.layer3Fallback }, null, 2));
NODE
```

```bash
node --input-type=module - <<'NODE'
import path from 'node:path';
import { readFileSync } from 'node:fs';
import jitiFactory from 'jiti';
const pluginSdkStubPath = path.resolve('test/helpers/openclaw-plugin-sdk-stub.mjs');
const jiti = jitiFactory(import.meta.url, { interopDefault: true, alias: { 'openclaw/plugin-sdk': pluginSdkStubPath } });
const { analyzeLayer3FallbackNeed, resolveLayer3FallbackSettings } = jiti('./src/tools.ts');
const all = JSON.parse(readFileSync(process.env.HOME + '/.openclaw/openclaw.json', 'utf8'));
const runtimeCfg = all.plugins.entries['memory-lancedb-pro'].config;
const resolved = resolveLayer3FallbackSettings(runtimeCfg.layer3Fallback);
const analysis = analyzeLayer3FallbackNeed('2026-03-14 今天完成了哪些优化工作？', [{ score: 0.92 }], runtimeCfg.layer3Fallback);
console.log(JSON.stringify({ resolved, analysis }, null, 2));
NODE
```

### Results
#### Actual runtime config in `~/.openclaw/openclaw.json`
Observed:
```json
{
  "pluginLoad": {
    "paths": [
      "/Users/lucifinil_chen/.openclaw/workspace/plugins/memory-lancedb-pro"
    ]
  },
  "memorySlot": "memory-lancedb-pro",
  "hasConfig": true
}
```
Notably, **no `layer3Fallback` field was present in the active runtime config**.

#### Parsed runtime config
Observed:
```json
{}
```
(i.e. `parsed.layer3Fallback` is absent / undefined when parsing the actual runtime config)

#### Resolver + trigger analysis against the actual runtime config
Observed:
```json
{
  "resolved": {
    "enabled": false,
    "agent": "notebooklm",
    "notebook": "memory-archive",
    "notebookId": "",
    "timeout": 45,
    ...
  },
  "analysis": {
    "shouldFallback": false,
    "reasons": [],
    "metrics": {
      "resultCount": 1,
      "top1Score": 0.92,
      "avgTop3Score": null
    }
  }
}
```

### Interpretation
This is the decisive blocker:
- The code **can parse** `layer3Fallback`.
- The manifest **declares** `layer3Fallback`.
- But the **active runtime plugin config does not supply it**.
- Therefore the live plugin resolves to `enabled: false`.
- Therefore the fallback path **will not trigger in the real gateway**, no matter what is present in `openclaw.plugin.json`.

## 6) PASS or BLOCKED decision
## **BLOCKED**

### Root cause layer
**Configuration propagation / runtime config layer**

More precisely:
- `openclaw.plugin.json` contains schema/example/defaults for `layer3Fallback`
- but `~/.openclaw/openclaw.json -> plugins.entries["memory-lancedb-pro"].config` does **not** contain `layer3Fallback`
- so the gateway starts the plugin without enabling Layer 3 fallback
- so end-to-end fallback verification is blocked before the actual query-path assertion

### Secondary issue (non-primary blocker)
- `test/layer3-fallback.test.mjs` still expects default timeout `90`
- current code default is `45`
- this is a **test expectation mismatch**, not the primary runtime blocker

## 7) Next minimal action
1. Add the intended `layer3Fallback` block to the **active runtime config**:
   `~/.openclaw/openclaw.json -> plugins.entries["memory-lancedb-pro"].config.layer3Fallback`
2. Restart gateway again.
3. Re-run a minimal recall command/query that should meet fallback conditions.
4. Confirm from logs or tool response metadata that:
   - `layer3.attempted = true`
   - `layer3.fallbackTriggered = true`
   - if NotebookLM succeeds, `layer3.used = true`
   - if NotebookLM fails, the Layer 2 response still includes the explicit fallback error note
5. Separately update `test/layer3-fallback.test.mjs` to match the code default (`45`) or update code/test to a single agreed timeout value.

## 8) Short verdict for StarChain Step 5
- Build: **PASS**
- Plugin startup after restart: **PASS**
- Runtime config load for `layer3Fallback`: **FAIL / missing in active runtime config**
- Real fallback path validation: **BLOCKED by runtime config layer**

---

**Report status:** complete
**Commit checked:** `386b82d`
**Result:** **BLOCKED**
**Required phrase:** Layer 3 验证完成
