---
increment: 0706-vskill-cli-windows-compat
title: "Windows compatibility fixes for vskill install/update/studio"
---

# Implementation Plan: Windows compatibility fixes for vskill install/update/studio

## Design

### Files Touched (all in `repositories/anton-abyzov/vskill/`)

```
src/agents/agents-registry.ts         [modify ~30 rows + copilot row]
src/installer/canonical.ts            [modify path guard + symlink fallback]
src/commands/update.ts                [modify path startsWith → path.relative]
src/commands/eval/serve.ts            [replace lsof/ps with HTTP probe]
src/utils/resolve-binary.ts           [reuse existing which/where helper; extend if needed]
src/agents/__tests__/registry-platform.test.ts      [NEW unit test]
src/installer/__tests__/canonical-platform.test.ts  [NEW unit test]
src/commands/__tests__/update-platform.test.ts      [NEW unit test]
src/commands/eval/__tests__/serve-port-probe.test.ts [NEW unit test]
.github/workflows/ci.yml              [add windows-latest matrix entry]
```

### Phase A — Agent detection (US-001)

**A1. Extract a `detectCommand` helper in `src/utils/resolve-binary.ts`** (already has `where`/`which` logic — reuse):

```ts
export function buildDetectCommand(binary: string): string {
  return process.platform === "win32"
    ? `where ${binary}`
    : `which ${binary}`;
}

export async function detectBinary(binary: string): Promise<boolean> {
  try {
    await execAsync(buildDetectCommand(binary));
    return true;
  } catch {
    return false;
  }
}
```

**A2. Migrate `agents-registry.ts` entries.** Two flavors:

1. Rows with `detectInstalled: 'which <bin>'` → replace with a detection function:
   ```ts
   // Before
   detectInstalled: 'which claude'
   // After
   detectInstalled: () => detectBinary("claude")
   ```
2. The copilot row (current line ~139) replace the shell pipe with a pure-Node check:
   ```ts
   detectInstalled: async () => {
     if (!(await detectBinary("code"))) return false;
     const extDir = path.join(os.homedir(), ".vscode", "extensions");
     if (!fs.existsSync(extDir)) return false;
     const entries = fs.readdirSync(extDir);
     return entries.some(e => e.startsWith("github.copilot-"));
   }
   ```

If the registry's type signature currently expects a string, widen it to `string | (() => Promise<boolean>)` and update the consumer in `detectInstalledAgents()` to handle both.

### Phase B — Path-traversal guard (US-002)

**B1. `src/installer/canonical.ts:47`** — replace:

```ts
// Before
if (!resolved.startsWith(normalizedRoot + "/")) {
  throw new Error(`Path traversal: ${target}`);
}

// After
if (path.relative(normalizedRoot, resolved).startsWith("..")) {
  throw new Error(`Path traversal: ${target}`);
}
```

**B2. Same swap in `src/commands/update.ts:43` and `:56`** — both are ghost-file cleanup guards with the same bug.

### Phase C — Symlink fallback (US-003)

**C1. `src/installer/canonical.ts:83`** — current code symlinks, with a hardcoded list `COPY_FALLBACK_AGENTS` for claude-code:

```ts
// Before (sketch)
if (COPY_FALLBACK_AGENTS.has(agentName)) {
  copyRecursive(target, linkPath);
} else {
  symlinkSync(relTarget, linkPath, "dir");
}

// After
try {
  if (COPY_FALLBACK_AGENTS.has(agentName)) {
    copyRecursive(target, linkPath);
  } else {
    symlinkSync(relTarget, linkPath, "dir");
  }
} catch (err: any) {
  if (err.code === "EPERM" || err.code === "EACCES") {
    if (!warnedAboutSymlinkFallback) {
      console.error(
        "Symlinks not available — copying files (enable Developer Mode to use symlinks)",
      );
      warnedAboutSymlinkFallback = true;
    }
    copyRecursive(target, linkPath);
  } else {
    throw err;
  }
}
```

`warnedAboutSymlinkFallback` is a module-scoped flag so the warning appears once per install.

### Phase D — Port-probe replacement (US-004)

**D1. `src/commands/eval/serve.ts:83,86`** — replace `execSync("lsof …")` + `ps` with a pure Node probe:

```ts
// Before (sketch)
const pid = execSync(`lsof -ti:${port}`).toString().trim();
const cmd = execSync(`ps -p ${pid} -o command=`).toString().trim();
if (cmd.includes("vskill")) { return existingServer; }
else { throw new Error("port in use"); }

// After
const identity = await probeVskillServer(port, 1000);
if (identity?.ok) {
  return { port, url: `http://localhost:${port}`, pid: null };
}
console.error(`Port ${port} is in use by a non-vskill process — please free it manually`);
process.exit(1);
```

`probeVskillServer` already exists (returns `{ok: true, version: ...}` when it hits a vskill `/api/config`, null otherwise).

### Phase E — CI matrix (US-005)

**E1. `.github/workflows/ci.yml`** — add matrix entry:

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22' }
      - run: npm ci
      - run: npm run build
      - run: npm test
      - name: Smoke tests
        shell: bash
        run: |
          npx vskill --version
          npx vskill install --help
          npx vskill update --help
          npx vskill studio --help
```

The `shell: bash` key makes the same smoke script run on Windows (via Git Bash, pre-installed on windows-latest runners).

## Rationale

### Why `path.relative` over manual separator juggling

`path.relative(base, target).startsWith("..")` is the canonical Node idiom for detecting "target escapes base". It handles:
- Mixed separators (Windows paths that mix `/` and `\`).
- Case-insensitive comparisons on NTFS.
- Symlinked base directories.
- Trailing slash edge cases.

Any bespoke string-comparison guard is more fragile.

### Why pure-Node probe over `lsof`/`ps` replacement

We could detect `process.platform === "win32"` and swap in `netstat -ano | findstr :port` + `tasklist /FI "PID eq ..."`. But:
- It's two platform branches to maintain.
- PID discovery doesn't actually help the user — if the port is occupied by a non-vskill process, telling them "PID 4723 is 'node.exe'" isn't actionable.
- The existing `probeVskillServer` already distinguishes our server from any other. That's the only discrimination we need.

Skipping PID discovery entirely is simpler and better for the user.

### Why the copy fallback is generalized

Today only `COPY_FALLBACK_AGENTS` (just claude-code) copies instead of symlinking. This was done because Claude Code doesn't resolve symlinks reliably on Windows. The same reasoning applies to every agent without Developer Mode — Cursor, Codex, Copilot, Windsurf, etc. all fail identically on `EPERM`. Instead of maintaining an allow-list, catch the error and fall back uniformly.

### Why detection uses function (not command string)

The registry's current `detectInstalled: 'which code'` format encodes a shell dependency. Functions sidestep that entirely — they can do `fs.existsSync`, `process.platform` branches, `exec` + `where`, whatever the detection actually needs. The change is backward-compatible if we widen the type to `string | () => Promise<boolean>`.

## Rollout

- All changes are surgical and no-op on Unix.
- Deploy as a single patch release of vskill CLI.
- Windows CI green BEFORE merging.
- Post-release: ask a Windows user (or run on our own Windows VM) to verify `vskill install scout` installs into Claude Code + Cursor without errors.
