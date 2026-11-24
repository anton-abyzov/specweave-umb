# Stop reading CLI login files where a status call or a file check is enough

## Problem

The rule set for increment 1397 on November 18, 2026: sign-in tokens stay in each CLI's own store, and nothing reads or prints them. The review of 1397 found shipped code that reads files holding tokens. None prints a token, but each loads the whole file into the app's memory to learn something a status call or a file check would give. App paths are in `repositories/anton-abyzov/specwithcode` at `be3fee857`; citations are rechecked when a task starts.

| Path | What it reads | What it needs |
|---|---|---|
| `apps/server/src/provision/probe.ts:511` | all of `~/.claude/.credentials.json` | whether it is non-empty |
| `apps/server/src/provision/probe.ts:541` | all of the Codex `auth.json` | whether it is non-empty |
| `apps/server/src/provision/probe.ts:518-520` | whether the Keychain item "Claude Code-credentials" exists (the secret is not requested) | whether Claude is signed in |
| `apps/server/src/telemetry/Identify.ts:172-190` | `~/.codex/auth.json`, for `tokens.account_id` | a stable anonymous id |
| `apps/server/src/provider/loginWatch.ts:60-85`, `:143`, `:166` | the Codex `auth.json`, decoding the id token for the email | that the account changed |

Also reading login material, for other providers: `apps/server/src/provider/cursorKeychainToken.ts:53-54` (the Cursor token from the credential store), `apps/server/src/provider/grokUsageLimits.ts:118-126` and the Cursor and OpenCode usage readers (their `auth.json`), and managed Codex, where the app is the OAuth client and holds the ChatGPT tokens (`apps/server/src/provider/CodexChatGptAuth.ts`). Those work only because they hold a token, so they are a product decision, not a cleanup.

## Scope

In: the five Claude and Codex reads in the table. Out: the other providers' readers and managed Codex, listed for Anton's decision (D-01); no behaviour change for a person.

## Acceptance Criteria

- [ ] AC-01: Provisioning decides "Claude signed in" from `claude auth status` (exit code) when the binary is present, and otherwise from the file's size without reading it. It runs no Keychain command. The `apiKeyHelper` and API-key branches of the probe are unchanged.
- [ ] AC-02: Provisioning decides "Codex signed in" from `codex login status` when the binary is present, and otherwise from the file's size without reading it.
- [ ] AC-03: The telemetry identity no longer opens `auth.json`; it uses the hashed account key the provider snapshot already carries, or no Codex id.
- [ ] AC-04: A Codex login change is noticed by watching the file's change time and then asking the CLI (`account/read`); the file is not opened. An account change is still detected within the same time as today in a test. When Codex keeps its login in the system credential store no file changes, so the watcher sees nothing, as today; the health refresh's `account/read` is what notices it.
- [ ] AC-05: A test fails when any file under `apps/server/src` outside an explicit allowlist (the other-provider readers and managed Codex in this spec) passes a path ending in `auth.json` or `.credentials.json` to a read call (`readFile`, `readFileString`, `readFileSync`, `createReadStream`, `open`), or calls a credential store. Watching, `stat` and naming such a path do not count (`apps/server/src/provider/Drivers/CodexDriver.ts:354` watches one). The allowlist is these files and no pattern: `apps/server/src/provider/cursorKeychainToken.ts`, `apps/server/src/provider/grokUsageLimits.ts`, `apps/server/src/provider/CodexChatGptAuth.ts`, `apps/server/src/provider/cursorUsageLimits.ts` and `apps/server/src/provider/openCodeUsageLimits.ts`.

## Approach

Replace content reads with `stat` and the CLIs' own status calls; keep each function's return type. Order: probe, telemetry, watcher, then the guard test with its allowlist. Risk: the watcher asks the CLI on every token refresh, since refreshes also touch the file; debounce it as the current watcher does.

## Decisions

### Asked
- D-01 Should the other providers' readers and managed Codex also stop holding tokens? → partly asked. The usage readers of Cursor, Grok and OpenCode Go were put to Anton on November 18, 2026 (1411 D-01, now 1415 D-01); he keeps them, each behind its own switch, off by default. Not asked: managed Codex, and the Muse Code login watcher, which reads Muse's `auth.json` for the email and sign-in kind and uses no token (`apps/server/src/provider/loginWatch.ts:88-112`). The three switches are built in increment 1415. Copilot's `gh auth token` read stays as it is (1411 D-05); it calls `gh` and opens no login file, so AC-05's guard and its allowlist are not affected. Whether GitHub's documented `account.getQuota` can replace it is recorded by 1411 AC-08 and planned after the result. This increment leaves all of them.

### Defaulted (change any before sw-do)
- D-02 Where a CLI is missing, a file's size is enough to say "signed in".

### Open
- none

## Tasks

### T-01 Provisioning probes without reading login files
- AC: AC-01, AC-02 | Files: apps/server/src/provision/probe.ts, apps/server/src/provision/probe.test.ts | Test: cd repositories/anton-abyzov/specwithcode && vp test run apps/server/src/provision/probe.test.ts

### T-02 Telemetry identity without the login file
- AC: AC-03 | Files: apps/server/src/telemetry/Identify.ts, apps/server/src/telemetry/Identify.test.ts | Test: cd repositories/anton-abyzov/specwithcode && vp test run apps/server/src/telemetry/Identify.test.ts

### T-03 Codex login watcher asks the CLI
- AC: AC-04 | Files: apps/server/src/provider/loginWatch.ts, apps/server/src/provider/loginWatch.test.ts, apps/server/src/provider/Drivers/CodexDriver.ts | Test: cd repositories/anton-abyzov/specwithcode && vp test run apps/server/src/provider/loginWatch.test.ts

### T-04 Guard test, verify and close 1401
- AC: AC-05 | Files: apps/server/src/provider/loginFileReads.guard.test.ts | Test: cd repositories/anton-abyzov/specwithcode && vp test run apps/server/src/provider/loginFileReads.guard.test.ts
