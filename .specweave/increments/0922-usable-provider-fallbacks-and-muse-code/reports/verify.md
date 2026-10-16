# Verify — 0922-usable-provider-fallbacks-and-muse-code

PASS · 2026-10-14T13:44:46.326Z · commands from explicit

## Commands

### `cd /Users/antonabyzov/Projects/github/studio-muse-fallback && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH node apps/server/scripts/cli.ts build` → exit 0 (4s)

```
[09:44:40.290] INFO (#1): [cli] Running tsdown...
[09:44:43.691] INFO (#1): [cli] Applied development icon overrides to dist/client
[09:44:43.691] INFO (#1): [cli] Bundled web app into dist/client
```

### `cd /Users/antonabyzov/Projects/github/studio-muse-fallback && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH STUDIO_CHROMIUM_EXECUTABLE="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" node scripts/studio-verify/muse-picker.mjs` → exit 0 (3s)

```
{"passed":4,"output":"/Users/antonabyzov/Projects/github/studio-muse-fallback/.artifacts/muse-picker/evidence"}
```

## Acceptance criteria

4/4 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | Suggested fallbacks require authenticated, fresh positive usage evidence and a listed model; unknown, denied, stale and exhausted accounts are excluded. |
| AC-02 | x (tasks) | Muse Code is a configurable provider using the official session protocol, with streaming turns, cancellation and approval handling. |
| AC-03 | x (tasks) | Wonder Full appears only when the native account exposes it; API-key access does not imply Full entitlement. Missing CLI/auth have actionable setup guidance. |
| AC-04 | x (tasks) | Focused tests and relevant builds pass; headless UI evidence is saved and credit-recovery integration is reconciled without overwriting its work. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex-muse@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/studio-muse-fallback … |  |
| T-02 | done | codex-muse@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/studio-muse-fallback … |  |

2/2 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
