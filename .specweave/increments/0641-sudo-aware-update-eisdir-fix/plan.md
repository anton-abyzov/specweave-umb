---
increment: 0641-sudo-aware-update-eisdir-fix
title: "Sudo-aware self-update and EISDIR fix"
type: bug
status: planned
---

# Architecture Plan: Sudo-aware self-update and EISDIR fix

## Overview

Two targeted bug fixes in 2 source files, zero new dependencies:

1. **EISDIR fix** — `computePluginHash()` crashes with noisy warnings when `readdirSync({ recursive: true })` returns entries that vanish between readdir and stat (ENOENT race). Fix: use `statSync(path, { throwIfNoEntry: false })?.isFile()`.
2. **Sudo-aware self-update** — `specweave update` fails with EACCES on systems where npm global prefix is root-owned (default Homebrew/system Node). Fix: detect write permission, retry install with `sudo` prefix + `stdio: 'inherit'` for password prompt.

## Files Changed

| File | Change |
|------|--------|
| `src/utils/plugin-copier.ts` | Fix `computePluginHash()` line 115 — safe stat check |
| `src/cli/commands/update.ts` | Add `isGlobalNpmWritable()`, `isSudoAvailable()`, `npmPublicInstall()`; update `installWithFallback()` and error message |
| `tests/unit/utils/plugin-copier.test.ts` | Add EISDIR/ENOENT resilience test |
| `tests/unit/cli/commands/update.test.ts` | Add sudo detection and install tests |

## Detailed Design

### 1. EISDIR Fix — `computePluginHash()` (plugin-copier.ts:115)

**Problem**: `readdirSync(dir, { recursive: true })` returns all entries. The current code calls `statSync(fullPath).isFile()` which can throw ENOENT if entries vanish between readdir and stat (concurrent plugin installs, race conditions). The inner try/catch handles this but logs a noisy debug message each time.

**Current code** (line 115):
```typescript
if (!statSync(fullPath).isFile()) continue;
```

**New code**:
```typescript
if (!statSync(fullPath, { throwIfNoEntry: false })?.isFile()) continue;
```

- `{ throwIfNoEntry: false }` returns `undefined` instead of throwing ENOENT when the entry disappears
- Optional chain `?.isFile()` evaluates to `undefined` (falsy) when stat returns undefined
- The `continue` fires, silently skipping the vanished entry
- `statSync` on a directory returns stats where `isFile()` returns `false` — no EISDIR throw
- This eliminates noisy debug log entries from the existing catch block for this common race

### 2. Sudo-Aware Self-Update (update.ts)

#### 2a. `isGlobalNpmWritable(): boolean` (new helper)

Checks if the current user can write to npm's global prefix:

```typescript
function isGlobalNpmWritable(): boolean {
  try {
    const prefix = execSync('npm prefix -g', {
      encoding: 'utf-8',
      timeout: 10000,
      stdio: ['pipe', 'pipe', 'pipe'],
    }).trim();
    const libDir = path.join(prefix, 'lib', 'node_modules');
    fs.accessSync(libDir, fs.constants.W_OK);
    return true;
  } catch {
    return false;
  }
}
```

- Uses `npm prefix -g` to find the global prefix (respects nvm, Homebrew, system Node)
- Tests write permission on `lib/node_modules/` via `fs.accessSync(W_OK)`
- Returns `false` on any error (npm not found, permission denied, timeout)

#### 2b. `isSudoAvailable(): boolean` (new helper)

Checks if `sudo` binary exists on the system:

```typescript
function isSudoAvailable(): boolean {
  if (process.platform === 'win32') return false;
  try {
    execSync('which sudo', {
      encoding: 'utf-8',
      timeout: 5000,
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    return true;
  } catch {
    return false;
  }
}
```

- Returns `false` on Windows (no sudo concept)
- Returns `false` on systems without sudo (some Docker containers, minimal Linux installs)

#### 2c. `npmPublicInstall(packageSpec: string, timeout: number): string` (new function)

Dedicated install function that can escalate to sudo. Unlike `npmPublicExec` which always captures stdio, this uses `stdio: 'inherit'` when sudo is needed so the password prompt is visible:

```typescript
function npmPublicInstall(packageSpec: string, timeout: number): string {
  const baseCmd = `npm install -g ${packageSpec} ${npmRegistryFlag()}`;
  const env = buildPublicRegistryEnv();

  try {
    return execSync(baseCmd, {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe'],
      timeout,
      env,
    }).trim();
  } catch (error: any) {
    const stderr = error.stderr?.toString() || error.message || '';

    // Only retry with sudo for permission errors
    if (
      !stderr.includes('EACCES') &&
      !stderr.includes('permission denied') &&
      !stderr.includes('EPERM')
    ) {
      throw error;
    }

    if (!isSudoAvailable()) {
      throw error;
    }

    // Retry with sudo + inherited stdio for password prompt
    execSync(`sudo ${baseCmd}`, {
      stdio: 'inherit',
      timeout,
      env,
    });
    return '';
  }
}
```

Design decisions:
- **Try without sudo first** — don't escalate unnecessarily (nvm users don't need sudo)
- **Only retry on EACCES/EPERM** — don't mask other errors (ETARGET, network, etc.)
- **`stdio: 'inherit'`** on sudo retry — user sees the password prompt and npm progress
- Clean `buildPublicRegistryEnv()` is passed via `env` — sudo inherits it automatically

#### 2d. Update `installWithFallback()`

Replace the two `npmPublicExec('npm install ...')` calls with `npmPublicInstall(...)`:

**Line 759** — change:
```typescript
npmPublicExec(`npm install -g specweave@${targetVersion}`, 120000);
```
To:
```typescript
npmPublicInstall(`specweave@${targetVersion}`, 120000);
```

**Line 793** — change:
```typescript
npmPublicExec(`npm install -g specweave@${fallbackVersion}`, 120000);
```
To:
```typescript
npmPublicInstall(`specweave@${fallbackVersion}`, 120000);
```

`npmPublicExec` remains for non-install commands (`npm view ...`) since those don't need sudo.

#### 2e. Update error message

In `selfUpdateSpecWeave()` catch block (line 955-956), change:
```
'Permission denied. Try: sudo npm install -g specweave@latest'
```
To:
```
'Permission denied. Try: sudo specweave update'
```

`sudo specweave update` is more user-friendly since it runs all update steps, not just npm install.

## Architecture Decisions

1. **No new dependencies** — uses only Node.js built-ins (`fs.accessSync`, `child_process.execSync`) and existing `npmRegistryFlag()`
2. **No new files** — all changes are in existing source files
3. **Graceful degradation** — if sudo detection fails, falls through to existing error message
4. **Platform safety** — `isSudoAvailable()` returns false on Windows; no sudo paths taken
5. **Try-first pattern** — always attempt without sudo first; only escalate on EACCES/EPERM
6. **Inherited stdio for sudo** — user must see the password prompt; `stdio: 'inherit'` is the only correct choice
7. **Separate `npmPublicInstall` from `npmPublicExec`** — install commands need sudo retry + inherited stdio; view/query commands don't. Keeping them separate avoids leaking sudo logic into read-only operations

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| `npm prefix -g` hangs | 10s timeout in `isGlobalNpmWritable()` |
| `which sudo` not found | Returns false, falls through to existing error path |
| sudo password wrong | User sees the prompt, can Ctrl-C; timeout kills after 120s |
| Windows has no sudo | `process.platform === 'win32'` early return |
| Concurrent stat race in hash | `throwIfNoEntry: false` returns undefined, skip gracefully |
| sudo not in PATH | `which sudo` fails, returns false — same as "not available" |

## Test Plan

### plugin-copier.test.ts
- Test that `computePluginHash` handles mixed file/directory entries from recursive readdir (no crash, valid hash)
- Test that `computePluginHash` handles entries deleted between readdir and stat (no crash, valid hash)

### update.test.ts
- Test `installWithFallback` succeeds without sudo when npm is writable
- Test `installWithFallback` retries with sudo on EACCES
- Test `installWithFallback` does NOT retry with sudo on non-EACCES errors (ETARGET, network)
- Test `installWithFallback` does NOT retry with sudo when `isSudoAvailable()` returns false
- Test error message says "sudo specweave update" not "sudo npm install -g specweave@latest"
