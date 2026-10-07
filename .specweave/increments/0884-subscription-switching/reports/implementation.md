# SpecWeave Switch — installed fleet and implementation evidence

Verified 7 October 2026. **The companion, provider CLIs and proxy components are installed on all three Macs. Real native Codex runs passed on M4, M1 and M3.** Seven main-host profile slots exist; two distinct Codex quota identities are proven across the fleet. M1 and M3 share one identity, so adding a Mac does not create another subscription allowance.

Source is isolated at `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0884-switch`, branch `codex/0884-subscription-switch`, commit `00fafd0eddfd9f0ace1660ef7e14fbbc3da04d7f`, based on current `origin/develop` 77e6ebb1a. All three operational users run immutable companion bundle `45b0ae98559b5fbd2837d7a3869cab70a790eba502da0ffa4e74a90a23d4c53d` in gui/501. The shared SpecWeave CLI remains verified stable3.0.3. Dirty original repositories, other sessions, native stores and prior bundles were preserved.

Draft source review: [SpecWeave PR #1980](https://github.com/anton-abyzov/specweave/pull/1980). Source is pushed; no product merge/global release/increment closure is claimed. GitHub unit, E2E, smoke, results and supply-chain checks passed. The automated Claude reviewer failed before producing findings; its hidden native error does not establish a specific OAuth/quota cause. [Diagnosis](ci-review-37592029270/diagnosis.md).

## Connections and installed components

| Mac | Verified native SSH identity | Proven native availability | Private services |
|---|---|---|---|
| M4 main, 192.168.40.201 | local Anton account | Codex real run passed; default Claude reached weekly limit | T3 stable3773, isolated nightly3774, CLIProxyAPI8317, Switch8318 |
| M1 Max, 192.168.40.134 | `anton`, UID501, home `/Users/antonabyzov`; `admin` also authenticates under UID502 | Codex real run passed; Claude actual run failed `Credit balance is too low` and its consumer identity is blocked as unverified | Fresh Anton T3 stable3773 and Switch8318 in gui/501; independent admin proxy8317 retained in user/502 |
| M3, 192.168.40.66 | `antonabyzov`, UID501, home `/Users/antonabyzov` | Codex real run passed; Claude requires sign-in | T3 stable3773, Switch8318 and proxy8317 |

Node22.20.0, official Codex0.160.1, Claude2.1.292, CLIProxyAPI8.0.17, VibeProxy1.8.325, Tailscale1.102.4 and AnyModel1.17.0 are installed on all three. Worker providers and Node are independent protected prefixes. Older active native installs were preserved. VibeProxy is installed and inactive while CLIProxyAPI owns8317. AnyModel has no API keys or running9090 service. T3 stable is0.0.45; M4 also has official isolated nightly0.0.46-nightly.20261007.2761, verified by digest, codesign/Gatekeeper, version, launchd, loopback startup and headless UI capture. Nightly uses its beta mobile client. Theo's private fork was not publicly available in the verified sources.

The SSH helper uses the dedicated restricted key and pinned host keys in `~/.local/share/specweave/fleet`, with protected factual references. Passwords remain in the protected Obsidian credential note; original fields were preserved and verified usernames appended. Existing authorized keys and global SSH trust were preserved.

## Implemented behavior and corrected issues

SpecWeave Switch selects native coding profiles using fresh observed quota, with balanced/reset-first/spend-first policies. Unknown and expired measurements remain Unknown. A weekly-only Codex primary limit is displayed as weekly. Native usage-denied/spend-control flags and prior real quota failures exclude accounts until a newer observation establishes eligibility. Selection applies to new managed runs. Native default Claude leaves `CLAUDE_CONFIG_DIR` unset; isolated slots have separate config homes.

Legacy Claude `oauth_token` alone does not prove a consumer subscription or a separate isolated identity. M1's empty slots reported the same ambient auth method, and its default actual run returned a billing failure. All those identities are now gated; stale authenticated flags, manual observations and explicit `--allow-unknown` cannot bypass the gate. Isolated login is preflighted and blocked when its scope is unverified. The UI explains both blocked conditions, disables selection and avoids a misleading isolated login command. Verified modern M4 `claude.ai` remains recognized, while its actual weekly failure remains visible.

Managed native runs hold an exclusive canonical workspace lease, recheck full policy under the reservation lock, preserve failed/time-out receipts and require native successful completion. Automatic failover is bounded and read-only; it starts after the previous process closes. Dirty tracked changes require an explicit file allowlist before failover. Write work uses explicit checkpoint/restoration and a new run. This does not transfer a live conversation or hidden reasoning.

Checkpoint/restoration verifies base/hash/index state, additions, deletions and executable modes, rejects unsafe paths/symlinks/secret content, and restores into a fresh worktree. Sensitive omitted paths are filtered before writing a manifest. Nested escaped native output is credential-redacted. The dashboard is loopback only, has no execution HTTP route, guards Host/Origin/JSON/schema/body size, sorts newest receipts first, supports automatic selection reset, and displays actual native failure reasons. Forwarded dashboard ports accept only their explicit `127.0.0.1` aliases and matching Origins; literal `localhost` aliases return403.

CLIProxyAPI has separate protected client/management keys, local management, 1h affinity with subagent inheritance, round-robin routing and bounded retries/cooldowns. Request-body logging, debug, cloaking, discovery, plugins and external management are disabled. Missing/wrong client and management auth returned401 on all hosts; correct discovery returned200 with zero models. Unconfigured inference failed400 honestly. A sentinel request body was absent from service logs. Upstream auth directories are empty; no native OAuth tokens were copied into this gateway.

Updates now verify prior bundle, exact launcher/plist/domain/job identity, use exclusive locking and recoverable backups, and wait for confirmed exact-job teardown. The original main update failure was retained and rollback restored its old service. Subsequent reviewed updates passed on all three. Future worker bootstrap requires the verified native username/hostname and uses the same guarded installer.

## Verification and retained evidence

- Companion:30/30 Node22 tests, zero failures/skips; **93.82% library lines,83.62% branches,88.60% functions**. Real Git restoration and tamper rejection, quota/auth gates, launch-race rejection, leases, failed native outcomes, bounded failover and HTTP guards are covered. [Coverage log](backend-reviewed-coverage.log).
- Installer:14/14 tests including Python3.9, unsafe archive members, identity validation, rollback and delayed launchd removal. Independent extraction7/7 and SSH argument/transport9/9 passed. [Installer log](installer-reviewed-checks.log), [independent review](independent-review.md).
- AnyModel:532/532 exact1.17.0 release tests,102 suites, zero skips, isolated empty HOME/no native/API auth and validated loopback-only network guard. Source tree and16 installed runtime files matched; source/install hashes remained unchanged. This proves the release tests, not paid hosted inference. [Source audit](anymodel-source-audit.json).
- Real Codex: M4 `9012661d-9f49-47a9-b223-140a4a630912`, M1 `aedf6464-aa12-4936-acf7-37b6b3e46830`, M3 `4a100955-625d-42f3-8dd1-ccfca71c94b8`: exact markers, native `turn.completed`, exit0, unchanged fixtures and released leases. Model IDs were not emitted and remain unknown. [M4 proof](real-codex-proof.json), [M1 proof](m1-anton-native-run-readback.json), [M3 proof](m3-real-codex-proof.json).
- Restoration: checkpoint `29e1efaa-82db-4da8-8c39-433b15847a70`, base `e27871f6b0fd0d5d2d6593554a29d0ba423c02a0`, fresh [live-restored](live-restored/) worktree, source preserved. Staged addition/deletion, content hashes and executable modes matched; M4's real Codex run used this restoration. [Restore receipt](live-restore-receipt.json).
- Native failures retained: M4 Claude weekly limit, resets8 October at10pm America/New_York; M1 Claude billing failure with unchanged scratch and released lease. These are observed account results. [M4 failure](real-claude-run.json), [M1 failure](m1-anton-claude-native-run-readback.json).
- Headless only: desktop/phone and light/dark fixture checks including XSS/RTL/overflow/errors/blocked auth; 12 real current DTO captures across all three Macs with no interception; both SSH forwards GET200 and same-Origin POST200 preserving policy. [Real UI evidence](ui-live/live-ui-check.json), [SSH dashboard evidence](ui-tunnels/tunnel-ui-check.json). Initial selector, missing-runtime, reduced-PATH and update failures remain preserved. Worker host configuration was corrected to actual m1/m3 IDs; the final screenshots show the own Worker card as Local host/Companion installed and other unknown host state remains unknown.

Latest installation/readback files are [M4 install](companion-install-reviewed.stdout.json), [M4 doctor](companion-doctor-reviewed.json), [M1](m1-companion-reviewed.json) and [M3](m3-companion-reviewed.json). Earlier files named final are historical and were preserved. [Completion proof](completion-proof.json) is the current aggregate. Full unrelated SpecWeave suites were not claimed; this standalone companion has no separate build step.

## Use it

Main dashboard: [SpecWeave Switch](http://127.0.0.1:8318). Worker dashboards are [M1](http://127.0.0.1:18318) and [M3](http://127.0.0.1:28318) while their dedicated foreground SSH tunnels are running. Restart them with `specweave-mac m1 dashboard` or `specweave-mac m3 dashboard`.

```sh
specweave-switch refresh
specweave-switch policy spend-first
specweave-switch policy reset-first
specweave-switch select automatic
specweave-switch run --cwd /absolute/git/worktree --provider codex --prompt 'Read the project brief' --failover --max-attempts 4
specweave-mac m1 status
specweave-mac m3 run --cwd /absolute/worker/git/worktree --account codex-1 --prompt 'Read the project brief'
specweave-switch checkpoint --cwd /absolute/git/worktree --files src/a.js,src/b.js
specweave-switch restore CHECKPOINT_ID --to /absolute/new/worktree --base EXPECTED_COMMIT
```

Sign in each additional account with its own native interactive command, for example `specweave-switch account login codex-2`, then refresh. Unknown Claude quota requires an explicit verified account plus `--allow-unknown`, or a fresh manually observed quota; unverified identity gates still apply. Use `--model` only with an actual native model ID. The SSH helper selects the worker's own account and checkout; it does not automatically copy a project or migrate a running session.

## Remaining activation and acceptance

Five additional main-host slots need native sign-ins. M1 Claude needs native consumer login correction and independently verified isolated scope. The fleet currently proves two Codex pools, one exhausted modern M4 Claude identity, and no other ready Claude subscription. Real automatic switching between two separately authenticated profiles on one host remains gated by those sign-ins; failover logic is tested with controlled native fixtures. Cross-machine checkpoint import is not implemented or claimed.

Tailscale is installed/notarized on all three, but macOS extension consent and native tailnet login remain. M4's native setup screen is at Required permissions: VPN Configuration Granted, System Extension Approval Required, Login Required. Computer Use requires action-time confirmation before granting new system networking access; that approval request is pending. No tailnet connectivity is claimed. Until enrollment, this setup uses verified LAN SSH; the dedicated key restricts the current M4 LAN source. CLIProxyAPI requires separate upstream provider login before proxy inference. VibeProxy remains inactive to prevent a port collision. Awake host availability and mobile pairing are separate future acceptance checks.

The new UI requires Anton's manual acceptance before increment0884 closes, under [AGENTS.md](/Users/antonabyzov/Projects/github/specweave-umb/AGENTS.md:101): “Ask user for manual acceptance: new UI, auth, payments, data migrations.” Source can be reviewed as a draft; no global npm release, product merge or increment closure is claimed.

## Research, concept and naming

The complete66:36 transcript has2003 timestamped lines/14307 words. The recovered report covers34 sources and156 research files, and distinguishes installed results from prior plans. See [full transcript](/Users/antonabyzov/Projects/research/claude-projects-2026-10-06/evidence/timestamped-transcript.txt), [prior report](/Users/antonabyzov/Projects/research/claude-projects-2026-10-06/report.md), [current source findings](research-findings.md) and [Obsidian contentions](vault-context.md). The attached screenshot and document instructions were treated as source material.

Keep **SpecWeave** for durable specification, project context and work evidence. Use **SpecWeave Switch** for native account selection and reviewed restoration. T3 supplies native task UI; Tailscale supplies private transport after enrollment; CLIProxyAPI/AnyModel serve separately configured gateway use cases. No global rebrand was applied. The focused Obsidian synthesis links the six related knowledge pages and keeps credentials outside the wiki: [synthesis](/Users/antonabyzov/Projects/Obsidian/personal-docs/wiki/synthesis/specweave-subscription-switching.md).
