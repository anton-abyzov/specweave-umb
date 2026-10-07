# 0884 Subscription switching and verified local proxy fleet

## Problem
Anton has three Claude and four Codex subscriptions across three Macs. T3 stable works locally but account switching, quota-aware choice and safe restoration are incomplete. The research transcript describes CLIProxyAPI, a private VibeProxy fork and Tailscale. Historical setup receipts must not be mistaken for current fleet access or successful inference.

## Scope
In: recover transcript/results, verified public proxy installations, isolated T3 nightly evaluation, a locally installed SpecWeave Switch companion using native CLIs and separate profiles, quota observations and reset-first/spend-first choice, portable Git checkpoints and isolated restoration, private dashboard, automated headless checks, reproducible worker bootstrap and exact access gates.
Out: replacing active sessions, copying subscription OAuth credentials into third-party gateways, guessing account entitlements, claiming full Claude Projects parity or silently scheduling tasks. Pending sign-ins and missing authenticated worker access remain explicit external gates.

## Acceptance Criteria
- [ ] AC-01: Research maps transcript claims to current primary sources, names exact products/forks, resolves Obsidian contradictions, and evaluates SpecWeave naming.
- [ ] AC-02: CLIProxyAPI and VibeProxy install with verified digests; proxy binds loopback, authenticates clients, keeps management local, enables session affinity and bounded retry, and exposes no credentials in receipts.
- [ ] AC-03: Seven native profile slots preserve existing authentication; refreshed quota observations separate window/weekly limits, remain unknown when unavailable, and eligible selection supports reset-first/spend-first while avoiding exhausted profiles.
- [ ] AC-04: Native runs hold an exclusive workspace lease, record actual outcomes, can fail over only after the prior run ends with a quota error, and never turn a failed run into success.
- [ ] AC-05: A dirty tracked workspace can checkpoint and restore into a fresh isolated worktree with hashes/base verification; unsafe paths, symlinks, secrets and arbitrary untracked files are rejected.
- [ ] AC-06: Loopback dashboard displays account/host/service state, refresh and policy controls with same-origin guarded mutations; desktop/phone/light/dark checks run explicitly headless.
- [ ] AC-07: T3 nightly installs separately from stable and passes version/startup/headless state capture; selected native Codex completes a real read-only run through the companion.
- [ ] AC-08: Authenticated installation and readback on M1/M3 complete, or exact missing external authorization/access is documented with a reproducible bootstrap; no unreachable worker is represented as installed.

## Approach
Source changes live only in contrib/subscription-switch in isolated SpecWeave worktrees from origin/develop 77e6ebb1a. Install as specweave-switch, without replacing the shared SpecWeave 3.0.3 CLI or active provider installations. The umbrella ledger remains task completion authority; companion state records runtime references and account observations only. ADR 0867's portable document boundary and 0881's native execution boundary apply. Credentials stay in native profile stores; no transcript transcoding. Native quota selection occurs at run boundaries, with current source observations and deterministic policy. Existing live sessions and dirty umbrella are preserved. UI acceptance remains a final human review gate; installation and automated verification are independently reportable.

## Tasks
### T-01 Recover source context and product evidence
- AC: AC-01 | Files: reports/research.md, reports/vault-context.md | Test: test -s reports/research.md && test -s reports/vault-context.md
### T-02 Implement native profile routing, managed execution and restoration
- AC: AC-03, AC-04, AC-05 | Files: contrib/subscription-switch/package.json, contrib/subscription-switch/bin/, contrib/subscription-switch/lib/, contrib/subscription-switch/test/ | Test: node --test contrib/subscription-switch/test/*.test.mjs
### T-03 Build the private account dashboard
- AC: AC-06 | Files: contrib/subscription-switch/public/, contrib/subscription-switch/scripts/ui-check.py | Test: python3 contrib/subscription-switch/scripts/ui-check.py
### T-04 Install proxies, companion and isolated T3 nightly; verify real behavior
- AC: AC-02, AC-07 | Files: contrib/subscription-switch/scripts/install-local.py, contrib/subscription-switch/README.md, reports/install.json, reports/real-run.json | Test: node contrib/subscription-switch/bin/specweave-switch.mjs doctor
### T-05 Verify fleet and prepare worker bootstrap
- AC: AC-08 | Files: contrib/subscription-switch/scripts/worker-bootstrap.sh, reports/fleet.md | Test: bash -n contrib/subscription-switch/scripts/worker-bootstrap.sh
