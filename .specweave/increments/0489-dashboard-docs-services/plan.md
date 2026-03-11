# Architecture Plan: 0489-dashboard-docs-services

## Overview

Fix the dashboard Services page to correctly represent Internal Docs and Public Docs as separate services with correct ports, scope-specific start/stop commands, configurable client timeout, and data-driven service controls.

This is a focused 4-file change with no new modules, patterns, or ADRs needed.

## Approach

### 1. command-runner.ts -- Scope-specific commands

Replace the 2 generic entries (`docs-preview-start`, `docs-preview-stop`) with 4 scope-specific entries.

**Start commands** use existing CLI scope support:
- `docs-internal-start` -> `specweave docs preview` (default scope = internal, port 3015)
- `docs-public-start` -> `specweave docs preview --scope public` (port 3016)

**Stop commands** -- `specweave docs kill` kills ALL Docusaurus processes with no scope support. Rather than modifying the CLI kill command (out of scope), use a direct in-process approach:
- Add an optional `handler` function to the command spec type that runs `killProcessOnPort(port)` instead of spawning a child process
- `docs-internal-stop` -> calls `killProcessOnPort(3015)` in-process
- `docs-public-stop` -> calls `killProcessOnPort(3016)` in-process

The command spec type becomes:
```ts
Record<string, { cmd: string; args: string[] } | { handler: () => Promise<void> }>
```

The `execute()` method checks for `handler` vs `cmd+args` and dispatches accordingly. This avoids shell commands, avoids modifying the CLI's kill command, and reuses the existing `killProcessOnPort` utility.

**Alternative considered**: Using `lsof -ti :3015 | xargs kill` as a shell command. Rejected -- platform-dependent, fragile, and the utility function already exists in the codebase.

### 2. dashboard-server.ts -- Correct service listing

Replace the single "Docs Preview" entry with two entries. Import `SCOPE_PORTS` from `utils/docs-preview/types.js`.

Current (wrong):
```ts
const docsPort = config?.documentation?.previewPort ?? 3000;
{ name: 'Docs Preview', status: ..., port: docsPort }
```

New:
```ts
import { SCOPE_PORTS } from '../../utils/docs-preview/types.js';
// ...
{ name: 'Internal Docs', status: await isPortReachable(SCOPE_PORTS.internal) ? 'running' : 'stopped',
  detail: `http://localhost:${SCOPE_PORTS.internal}`, port: SCOPE_PORTS.internal,
  startCommand: 'docs-internal-start', stopCommand: 'docs-internal-stop' },
{ name: 'Public Docs', status: await isPortReachable(SCOPE_PORTS.public) ? 'running' : 'stopped',
  detail: `http://localhost:${SCOPE_PORTS.public}`, port: SCOPE_PORTS.public,
  startCommand: 'docs-public-start', stopCommand: 'docs-public-stop' },
```

Each service now includes optional `startCommand`/`stopCommand` fields. Dashboard Server omits these (no start/stop controls).

### 3. useCommand.ts -- Configurable timeout

Change `execute` signature from:
```ts
execute(commandName: string, queryParams?: Record<string, string>)
```
to:
```ts
execute(commandName: string, options?: { queryParams?: Record<string, string>; timeoutMs?: number })
```

Default timeout remains 60000ms. The timeout message uses the actual duration:
```ts
const timeout = options?.timeoutMs ?? 60000;
setError(`Command timed out after ${timeout / 1000} seconds`);
```

This is backward-compatible -- callers passing `undefined` get the same behavior as before.

### 4. ServicesPage.tsx -- Data-driven controls

**Remove**: All `svc.name === 'Docs Preview'` conditionals and the separate `svc.name !== 'Docs Preview'` Open link block.

**Add**: `startCommand` and `stopCommand` optional fields to the `ServiceInfo` interface.

**Replace** the hardcoded rendering logic with data-driven checks:
```tsx
{svc.startCommand && svc.stopCommand && (
  svc.status === 'running' ? (
    <div className="flex items-center gap-1">
      <a href={svc.detail} ...>Open</a>
      <button onClick={() => handleStop(svc.stopCommand!)} ...>Stop</button>
    </div>
  ) : (
    <button onClick={() => handleStart(svc.startCommand!)} ...>
      {running ? 'Starting...' : 'Start'}
    </button>
  )
)}
{svc.status === 'running' && !svc.startCommand && (
  <a href={svc.detail} ...>Open</a>
)}
```

The `handleStart` and `handleStop` wrappers pass `{ timeoutMs: 300000 }` for controllable services (docs commands need ~5 minutes for npm install + Docusaurus startup).

## Data Flow

```
/api/services (dashboard-server.ts)
  |-- returns [{name, status, port, detail, startCommand?, stopCommand?}]
  v
ServicesPage.tsx
  |-- renders controls based on startCommand/stopCommand presence
  |-- calls useCommand.execute(commandName, { timeoutMs: 300000 })
  v
POST /api/commands/:name (dashboard-server.ts -> command-runner.ts)
  |-- looks up ALLOWED_COMMANDS[name]
  |-- if handler: runs in-process function
  |-- if cmd+args: spawns child process
```

## Files Changed

| File | Change |
|------|--------|
| `src/dashboard/server/command-runner.ts` | Replace 2 generic entries with 4 scope-specific entries; add handler-based dispatch for stop commands |
| `src/dashboard/server/dashboard-server.ts` | Import SCOPE_PORTS; return 3 services with correct ports and startCommand/stopCommand fields |
| `src/dashboard/client/src/hooks/useCommand.ts` | Add optional `timeoutMs` param to `execute()` options object |
| `src/dashboard/client/src/pages/ServicesPage.tsx` | Add startCommand/stopCommand to ServiceInfo; replace name-hardcoded conditionals with data-driven rendering |

## No ADRs Needed

This change follows existing patterns (command runner, service API, React hooks). No new architectural decisions or trade-offs warrant an ADR.

## Risk Assessment

- **Low risk**: All changes are isolated to the dashboard module
- **No breaking changes**: The `execute()` signature change is backward-compatible (new optional param)
- **Testability**: Each change is independently verifiable -- port checks, command execution, timeout behavior, UI rendering
