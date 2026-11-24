# Verify — 0907-m4-portable-continuation-proof

PASS · 2026-10-13T15:28:14.730Z · commands from explicit

## Commands

### `python3 -c 'import json;from pathlib import Path;d=json.loads(Path('"'"'.specweave/increments/0907-m4-portable-continuation-proof/reports/m4-source.json'"'"').read_text());assert d['"'"'status'"'"']=='"'"'passed'"'"' and d['"'"'host'"'"']=='"'"'m4'"'"' and d['"'"'mode'"'"']=='"'"'source'"'"' and d['"'"'key'"'"']=='"'"'specweave'"'"';assert d['"'"'baseline'"'"'][1]['"'"'sha'"'"']=='"'"'a7bd43cabd0b241cea9a3c7cd8bc22fbe3ba9c9a'"'"';assert d['"'"'marker'"'"'] and d['"'"'decision'"'"'];assert d['"'"'outcome'"'"']['"'"'workerThreadId'"'"'] and d['"'"'outcome'"'"']['"'"'automaticWakeRunId'"'"'] and d['"'"'outcome'"'"']['"'"'workerText'"'"'] and d['"'"'outcome'"'"']['"'"'relayText'"'"'];assert d['"'"'temporarySessionRevoked'"'"'] is True'` → exit 0 (0s)

```
(no output)
```

### `python3 -c 'import json;from pathlib import Path;d=json.loads(Path('"'"'.specweave/increments/0907-m4-portable-continuation-proof/reports/m1-continuation.json'"'"').read_text());assert d['"'"'status'"'"']=='"'"'passed'"'"' and d['"'"'host'"'"']=='"'"'m1'"'"' and d['"'"'mode'"'"']=='"'"'destination'"'"' and d['"'"'key'"'"']=='"'"'specweave'"'"';assert d['"'"'baseline'"'"'][1]['"'"'sha'"'"']=='"'"'a7bd43cabd0b241cea9a3c7cd8bc22fbe3ba9c9a'"'"';assert d['"'"'marker'"'"'] and d['"'"'decision'"'"'];assert d['"'"'outcome'"'"']['"'"'workerThreadId'"'"'] and d['"'"'outcome'"'"']['"'"'automaticWakeRunId'"'"'] and d['"'"'outcome'"'"']['"'"'workerText'"'"'] and d['"'"'outcome'"'"']['"'"'relayText'"'"'];assert d['"'"'temporarySessionRevoked'"'"'] is True;s=json.loads(Path('"'"'.specweave/increments/0907-m4-portable-continuation-proof/reports/m4-source.json'"'"').read_text());assert d['"'"'marker'"'"']==s['"'"'marker'"'"'] and d['"'"'decision'"'"']==s['"'"'decision'"'"']'` → exit 0 (0s)

```
(no output)
```

### `python3 -c 'import json;from pathlib import Path;d=json.loads(Path('"'"'.specweave/increments/0907-m4-portable-continuation-proof/reports/m3-continuation.json'"'"').read_text());assert d['"'"'status'"'"']=='"'"'passed'"'"' and d['"'"'host'"'"']=='"'"'m3'"'"' and d['"'"'mode'"'"']=='"'"'destination'"'"' and d['"'"'key'"'"']=='"'"'specweave'"'"';assert d['"'"'baseline'"'"'][1]['"'"'sha'"'"']=='"'"'a7bd43cabd0b241cea9a3c7cd8bc22fbe3ba9c9a'"'"';assert d['"'"'marker'"'"'] and d['"'"'decision'"'"'];assert d['"'"'outcome'"'"']['"'"'workerThreadId'"'"'] and d['"'"'outcome'"'"']['"'"'automaticWakeRunId'"'"'] and d['"'"'outcome'"'"']['"'"'workerText'"'"'] and d['"'"'outcome'"'"']['"'"'relayText'"'"'];assert d['"'"'temporarySessionRevoked'"'"'] is True;s=json.loads(Path('"'"'.specweave/increments/0907-m4-portable-continuation-proof/reports/m4-source.json'"'"').read_text());assert d['"'"'marker'"'"']==s['"'"'marker'"'"'] and d['"'"'decision'"'"']==s['"'"'decision'"'"']'` → exit 0 (0s)

```
(no output)
```

## Acceptance criteria

3/3 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | An actual M4 coordinator delegates a read-only source discovery to one native worker; the worker and automatically resumed coordinator report the pinned nested commit, a concrete code finding, a fresh marker and a continuation decision in a passed source receipt. |
| AC-02 | x (tasks) | An actual M1 coordinator and native worker load the transported M4 checkpoint, independently inspect the same nested code commit, preserve its marker and decision, and finish through automatic coordinator continuation with a passed destination receipt. |
| AC-03 | x (tasks) | An actual M3 coordinator and native worker load the transported M4 checkpoint, independently inspect the same nested code commit, preserve its marker and decision, and finish through automatic coordinator continuation with a passed destination receipt. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex-source-proof@antons-macbook-m4max | python3 -c 'import json;from pathlib import Path;d=json.loa… |  |
| T-02 | done | codex-source-proof@antons-macbook-m4max | python3 -c 'import json;from pathlib import Path;d=json.loa… |  |
| T-03 | done | codex-source-proof@antons-macbook-m4max | python3 -c 'import json;from pathlib import Path;d=json.loa… |  |

3/3 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
