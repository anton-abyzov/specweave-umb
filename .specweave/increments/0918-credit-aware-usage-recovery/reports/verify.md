# Verify — 0918-credit-aware-usage-recovery

PASS · 2026-10-14T13:50:45.552Z · commands from explicit

## Commands

### `python3 .specweave/increments/0918-credit-aware-usage-recovery/reports/verify-release.py` → exit 0 (0s)

```
m1: installed 1.0.14, sealed readback verified
m3: installed 1.0.14, sealed readback verified
Mac app: installed 1.0.14
Public release: 1.0.14, 11 assets, anonymous readback receipt verified
Live paid inference and six-route handoff acceptance are not asserted.
```

## Acceptance criteria

4/4 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | A funded eligible Codex account exposes its balance and explicit Continue using credits action with existing account/model/freshness checks. |
| AC-02 | x (tasks) | A later started run resolves the earlier usage warning; queued or pre-start failed requests do not. |
| AC-03 | x (tasks) | Instructions and regression/headless checks cover credits, unavailable permissions, and recovery. |
| AC-04 | x (tasks) | Reviewed source is released and deployment readback records exact version; manual UI acceptance remains explicit. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/studio-credit-recover… |  |
| T-02 | done | codex@antons-macbook-m4max | python3 .specweave/increments/0918-credit-aware-usage-recov… |  |

2/2 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
