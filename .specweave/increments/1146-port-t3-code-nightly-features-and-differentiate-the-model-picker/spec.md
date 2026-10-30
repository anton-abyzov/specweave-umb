# Port T3 Code nightly features and differentiate the model picker

## Problem

Upstream T3 Code shipped 163 commits between 5211acfe95 (end of the 1129 triage) and nightly v0.1.6-nightly.20261030.3904. The triage (reports/triage.md) checked 149 relevant ones plus 16 deferred Connect items: about 90 are real gaps, each re-checked by a skeptic agent. The Connect gaps include a security fix: our managed cloudflared is still 2026.5.2, while upstream pinned 2026.10.4 to drop compromised eMudhra intermediates. Pairing codes are case-sensitive and get lost after a scope rejection. Pairing links can add routes to a saved environment. Dead connection routes are probed too often. Electron 44.4.2 lacks the Node.js Brotli CVE fix in 44.10.0. Our composer model picker still uses T3 Code's look (44px icon column plus list). The owner wants it visibly ours. The T3 mention audit (reports/t3-mentions-audit.md) found no user-visible T3 branding left in the product.

## Scope

In: Connect and pairing fixes, relay fixes, security and redaction fixes, orchestration and server fixes and performance ports marked high (plus selected medium S items), Linux CLI start fixes, the Electron CVE bump, and a SpecWithCode "Weave" model picker (reports/model-picker-design.md). Out: upstream-only infra (their mobile app, EAS, Simlock, GitCafe, T3 Chat accounts, their marketing site), large medium ports left for a follow-up (fleet Stable/Nightly switch f2943ee90e, service protect 44d508fd8b, agent-made environment links 8b14660b27, SQLite read pool facaa08b36, sidebar shell perf 8bf4822f5e), and missing providers and terminal connect, which other threads own.

## Acceptance Criteria

- [ ] AC-01: Managed cloudflared is 2026.10.4 with upstream checksums. Typed pairing codes match regardless of case. A scope rejection keeps the pairing code usable. Pairing links cannot add routes to a saved environment. A pairing --base-url without http(s):// is rejected. Dead connection routes back off, and the permissions check retries after a reconnect.
- [ ] AC-02: Relay delivery attempts are pruned, tunnel cleanup keeps up with idle tunnels, and the tunnel limit counts abandoned reprovisions.
- [ ] AC-03: Clone errors, HTTP traces, provider errors and ACP stderr never show tokens, signed URLs or compound credential keys. Electron is 44.10.0.
- [ ] AC-04: Orchestration: restart continuations retry failed starts and respect a parent's stop; held queues release after a run completes; Copilot follow-ups queue without killing background agents; Cursor subagent results do not fail the parent; Claude command approvals show the command.
- [ ] AC-05: Server: run preparation and checkpoint payloads are bounded; large git status metadata and thread lists beyond the SQLite variable limit load; commits never land on a branch switched mid-action; listed medium S fixes from the triage are ported.
- [ ] AC-06: The CLI starts on a fresh Ubuntu without libatomic, SSH config includes skip directories, and CLI flag parsing stops after --.
- [ ] AC-07: The composer model picker uses the Weave design: one grouped column with provider chips instead of the icon column, sticky provider headers with account and usage chips, iris selected rows, effort words, no chevron on the button. All existing picker behaviour (favorites, legacy, fallback status, setup, multi-select, coordinator picker) still works.

## Approach

Ported per upstream commit onto our renamed code; port notes and verified evidence are in reports/triage.md. The work stays in the existing specweave-studio checkout on branch claude/project-thread-pzron9; there are no worktrees (owner's instruction). Four lanes touch disjoint files: Connect (T-01), infra/security/CLI (T-02, T-03, T-06), orchestration then server (T-04, T-05), and the web picker (T-07). One PR ships them in the next macOS release through scripts/release/release.sh.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Picker: take upstream's behaviour from bd84b1781a (no chevron, icon hides first, effort words) but not its look; use the Weave design from reports/model-picker-design.md.
- D-02 Large medium ports listed under Out wait for a follow-up increment, so this release stays reviewable.
- D-03 T3 audit: the two internal research lines in docs/research/embedded-browser-1018.md get neutral wording. Notices, provenance, fixtures and patches stay.
### Open
- none

## Tasks

### T-01 Connect and pairing fixes
- AC: AC-01 | Files: repositories/anton-abyzov/specweave-studio/packages/shared/src/relayClient.ts, repositories/anton-abyzov/specweave-studio/packages/client-runtime/src, repositories/anton-abyzov/specweave-studio/apps/server/src/auth, repositories/anton-abyzov/specweave-studio/apps/server/src/cli/auth.ts | Test: cd repositories/anton-abyzov/specweave-studio && node node_modules/vite-plus/bin/vp test run packages/shared/src/relayClient packages/client-runtime/src/connection packages/client-runtime/src/authorization apps/server/src/auth

### T-02 Relay fixes
- AC: AC-02 | Files: repositories/anton-abyzov/specweave-studio/infra/relay | Test: cd repositories/anton-abyzov/specweave-studio/infra/relay && node ../../node_modules/vite-plus/bin/vp test run

### T-03 Security, redaction and Electron
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/git, repositories/anton-abyzov/specweave-studio/apps/server/src/observability, repositories/anton-abyzov/specweave-studio/apps/server/src/provider, repositories/anton-abyzov/specweave-studio/apps/desktop/package.json, repositories/anton-abyzov/specweave-studio/pnpm-lock.yaml | Test: cd repositories/anton-abyzov/specweave-studio && node node_modules/vite-plus/bin/vp test run apps/server/src/observability apps/server/src/provider

### T-04 Orchestration fixes
- AC: AC-04 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2 | Test: cd repositories/anton-abyzov/specweave-studio && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/RestartContinuation apps/server/src/orchestration-v2/runtimeLayer

### T-05 Server fixes and performance
- AC: AC-05 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/vcs, repositories/anton-abyzov/specweave-studio/apps/server/src/persistence, repositories/anton-abyzov/specweave-studio/apps/server/src/checkpointing, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2 | Test: cd repositories/anton-abyzov/specweave-studio && node node_modules/vite-plus/bin/vp test run apps/server/src/vcs apps/server/src/persistence apps/server/src/checkpointing

### T-06 Linux CLI start fixes
- AC: AC-06 | Files: repositories/anton-abyzov/specweave-studio/packages/ssh/src, repositories/anton-abyzov/specweave-studio/packages/shared/src, repositories/anton-abyzov/specweave-studio/scripts | Test: cd repositories/anton-abyzov/specweave-studio && node node_modules/vite-plus/bin/vp test run packages/ssh packages/shared/src/cliArgs

### T-07 Weave model picker
- AC: AC-07 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/ModelPickerContent.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/ModelPickerSidebar.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/ModelListRow.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/ProviderModelPicker.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/modelPickerKeys.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/modelPickerSearch.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/modelChipFit.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/shell/shell.css, repositories/anton-abyzov/specweave-studio/docs/research/embedded-browser-1018.md | Test: cd repositories/anton-abyzov/specweave-studio/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/chat src/components/studio/shell

### T-08 Verify and close 1146
- AC: AC-01, AC-07 | Files: .specweave/increments/1146-port-t3-code-nightly-features-and-differentiate-the-model-picker/reports/verify.md, repositories/anton-abyzov/specweave-studio/UPSTREAM.md, repositories/anton-abyzov/specweave-studio/CHANGELOG.md | Test: specweave verify 1146-port-t3-code-nightly-features-and-differentiate-the-model-picker
