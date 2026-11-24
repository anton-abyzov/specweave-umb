# Fix auth storage races and service token exposure

Repository: `anton-abyzov/specwithcode-dev` (public mirror `anton-abyzov/specwithcode`), branch `fix/auth-storage-races`.

## Problem

1. The web connection catalog (`makeCatalogStore`, `apps/web/src/connection/storage.ts`) loads the catalog once per renderer, caches it in memory, and writes the whole cached document back on every update under a per-renderer semaphore. Two renderers of one desktop app (or two browser tabs) each write their stale copy, so one renderer's saved Connect token or DPoP token is overwritten by the other's. Each renderer then exchanges for a new `cloud-connect` sign-in. Suspected cause of a Linux app making 87 sign-ins in 12 hours (project memory `project_open_product_gaps.md`).
2. On Linux, `systemctl --user status studio.service` and `ps` show the service's MCP bearer token. Checked on ministorm (November 12, 2026): the unit file and the `__service-launcher`/`serve` processes carry no token. The token is in the Claude provider child's command line: the Agent SDK serializes `mcpServers` into `--mcp-config '{"mcpServers":{"studio-code":{"headers":{"Authorization":"Bearer …"}}}}'`, and that process is in the service's cgroup, so `systemctl status` lists it. Codex receives its header over JSON-RPC, not argv.
3. "Unknown auth state is mapped to `signedIn=true`" in the readiness checklist.

## Scope

In: re-read the catalog inside the lock before each read and read-modify-write, plus a cross-renderer Web Lock when available; keep the Claude MCP bearer out of argv; record the readiness finding.

Out: changing routing semantics for providers that cannot report auth (ACP agents); multi-user storage.

## Acceptance Criteria

- [ ] AC-01: A test with two catalog stores on one shared backend reproduces the clobber on the old code (one store's token disappears after the other's update) and passes on the new code: both tokens survive, and each store reads the other's latest write.
- [ ] AC-02: Catalog updates from two stores serialize through a cross-renderer lock (Web Locks `navigator.locks`) when the runtime has it, and still work without it.
- [ ] AC-03: The Claude query's `--mcp-config` (the SDK `mcpServers` option) carries no bearer token; the token reaches Claude only through the child environment and Claude Code expands it into the header.
- [ ] AC-04: Rotating a thread's MCP credential still replaces the live Claude process (the query key changes with the credential), without putting the raw token in the key.
- [ ] AC-05: The readiness finding is recorded: the checklist already shows unknown auth as "sign-in not reported" (gray), and the remaining `signedIn: true` for unknown is intentional routing; project memory updated.

## Approach

- `apps/web/src/connection/storage.ts`: drop the in-memory cache; `read` and `update` load from the backend inside the lock every time. The lock is the local semaphore wrapped in `navigator.locks.request("studio:connection-catalog", …)` when available.
- `apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts`: `claudeMcpQueryOverrides` returns the header as `${SPECWITHCODE_STUDIO_MCP_AUTHORIZATION}` plus `mcpEnvironment` with the real value; the query builder merges `mcpEnvironment` into the SDK `env`; `claudeEffectiveQueryPolicyKey` adds a SHA-256 fingerprint of the credential.
- Verified on ministorm that Claude Code 2.1.322 expands `${VAR}` in an inline `--mcp-config` header (scratch HTTP server on port 18777 received the expanded value). No restart of the live service was needed: the unit file never held the token, so old installs need no migration.
- Rejected: a 0600 temp file for the MCP config (needs per-session cleanup, same exposure to the same user as `/proc/<pid>/environ`).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Env var expansion instead of a 0600 file for the MCP header (reversible).
- D-02 Item 3 not changed in code: the checklist already handles unknown; routing keeps treating unknown as usable.
### Open
- none

## Tasks

### T-01 Re-read the catalog inside a cross-renderer lock
- AC: AC-01, AC-02 | Files: apps/web/src/connection/storage.ts, apps/web/src/connection/storage.test.ts | Test: cd apps/web && npx vitest run src/connection/storage.test.ts

### T-02 Keep the Claude MCP bearer out of argv
- AC: AC-03, AC-04 | Files: apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts | Test: cd apps/server && npx vitest run src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts

### T-03 Record the readiness finding and update gaps memory
- AC: AC-05 | Files: project memory project_open_product_gaps.md | Test: manual: read MachineReadinessChecklist.tsx:247-256
