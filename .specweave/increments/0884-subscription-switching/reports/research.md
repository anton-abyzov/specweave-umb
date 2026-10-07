# Subscription switching, T3 Code, and SpecWeave — recovered research

Checked 7 October 2026. This is a read-only research receipt. It recovers the earlier results, rechecks official upstream sources, and separates demonstrated behavior from designs and untested releases. Documents and transcript instructions were treated as source material, not execution instructions.

## Recommendation

Keep **SpecWeave** as the umbrella name. Position the new layer as **SpecWeave Control — portable coordination for your coding agents**. The useful promise is that a project, accepted work, and recovery state survive changing an execution account. T3 supplies the immediate client/runtime experience; SpecWeave supplies durable intent, ownership, handoff, and verified completion. A token pool alone does not solve project continuity.

Use current official CLIProxyAPI for the requested proxy evaluation, preserve the installed T3 stable service, and evaluate the official T3 nightly separately if its newer orchestration and portable restart features are needed. Theo's customized proxy fork was described in the video but no public release location was recovered. Reproduce the behavior with explicit tests rather than claiming to install his private dashboard.

## Everything recovered

The previous workspace is `/Users/antonabyzov/Projects/research/claude-projects-2026-10-06`. It contains 156 files, including 34 source snapshots, the full timestamped English transcript, research/design/setup documents, installation helpers, and saved UI evidence. Counts were read from the local files on 7 October.

| Result | Authoritative local artifact | What it establishes |
|---|---|---|
| Full product/competitor research | [report.md](/Users/antonabyzov/Projects/research/claude-projects-2026-10-06/report.md) | Claude Projects, T3, alternatives, seven-account design, three-Mac design, limitations |
| Full-video assessment | [video-analysis.md](/Users/antonabyzov/Projects/research/claude-projects-2026-10-06/video-analysis.md) | The whole 66:36 video, not just the originally linked 47:06 segment |
| Complete readable transcript | [timestamped-transcript.txt](/Users/antonabyzov/Projects/research/claude-projects-2026-10-06/evidence/timestamped-transcript.txt) | 2,003 caption lines; 14,307 words using this run's lexical count |
| Structured transcript | [video-transcript.json](/Users/antonabyzov/Projects/research/claude-projects-2026-10-06/evidence/video-transcript.json) | Machine-readable timing/context |
| Original caption data | [youtube.en.json3](/Users/antonabyzov/Projects/research/claude-projects-2026-10-06/evidence/youtube.en.json3) | Recoverable automatic-caption source; names can be misheard |
| Portable coordinator proposal | [specweave-design.md](/Users/antonabyzov/Projects/research/claude-projects-2026-10-06/specweave-design.md) | Identity/storage, adapters, messages, owner fencing, account transfer, fleet, acceptance checks; proposal status |
| Local installation receipt | [installation-receipt.md](/Users/antonabyzov/Projects/research/claude-projects-2026-10-06/installation-receipt.md) | T3 .45, isolated provider versions, actual Codex success, Claude quota failure |
| Operator/setup guide | [setup-guide.md](/Users/antonabyzov/Projects/research/claude-projects-2026-10-06/setup-guide.md) | Account directories, service paths, pairing and worker prerequisites |
| Source manifest | [manifest.json](/Users/antonabyzov/Projects/research/claude-projects-2026-10-06/evidence/sources/manifest.json) | 34 snapshotted source records |
| Native Claude project observations | [claude-desktop-observations.md](/Users/antonabyzov/Projects/research/claude-projects-2026-10-06/evidence/claude-desktop-observations.md) | Real coordinator/worker observations, account-specific state |

The three previously saved Pages are [research report](https://chatgpt.com/space/page_c36463de23c48191b6baf14ea45dfdf6), [implementation design](https://chatgpt.com/space/page_1ad7ff925f3081919f67d1a35590967c), and [seven accounts/three Macs setup](https://chatgpt.com/space/page_a6ab0e6bf8d0819194901ee9584f0b88). Their IDs came from the earlier local Page-link receipt; this lane did not verify current Page contents or edit them.

## The product and the exact concept

The video is Theo's **If you have a Claude sub, watch this**, uploaded 2 October 2026, lasting 66:36. It primarily demonstrates **T3 Code**, not T3 Chat. [Video](https://www.youtube.com/watch?v=D8PikZ1KhUo).

The demonstrated arrangement has four layers:

1. Subscriptions provide separate model entitlements and usage windows.
2. CLIProxyAPI/VibeProxy normalize inference endpoints and route requests between authenticated accounts.
3. T3 Code organizes agent threads, worktrees, host selection, an attention inbox, and remote clients.
4. A private fleet runs coding tools/builds; the model inference remains remote.

SpecWeave adds a fifth responsibility: portable project intent, exact task ownership, evidence, and recovery across tools/accounts. Keep project, task, logical thread, native conversation, run, account, host, and attention request distinct. An account change can require a new native run while the task and project remain the same.

The original Claude Projects observation is a useful interface reference: the coordinator sent one instruction to eight workers, routed another to one existing worker, and workers could receive relayed messages. T3's video inbox is more human directed; the video's Orchestrator V2 was still forthcoming at 41:09. Newer public T3 code now includes orchestration, but this must be judged by the installed release and actual test behavior.

## Transcript revisited: relevant sections

| Time | Actual subject | Implementation lesson |
|---|---|---|
| 00:00–02:43 | Opening, claims and Parallel sponsorship | Measure accepted output/review cost; anecdotes are not operating guarantees |
| 02:43–05:23 | Workflow framing and objections | Generated PR count does not establish deployed correctness |
| 05:23–12:41 | Subscription economics, margin/privacy speculation | Inventory real plans/windows; avoid treating API-equivalent value as cash/quota |
| 12:41–15:16 | Shared account auth and residential proxy argument | Separate credential routing from remote tool execution |
| 15:16–17:50 | CLIProxyAPI and the VibeProxy starting point | These are exact product names; T3 Chat/Cursor/OpenCode economics are separate |
| 17:50–18:22 | Theo's extensively customized proxy dashboard | The stock dashboard will differ; screenshot-driven customization was an invitation, not a public fork announcement |
| 18:22–20:38 | Account priority by next reset | Prefer earliest known reset only among eligible accounts for new work; retain an established account binding |
| 19:37–20:23 | Inserted update about a newer Opus model | The video revises its earlier model advice; avoid a permanently hard-coded Claude/model preference |
| 20:38–20:53 | Codex WebSocket changes | Both client and chosen upstream credential must support WebSocket; verify actual traffic and result |
| 20:55–22:01 | Session/account affinity and cache reuse | Bind logical sessions; do not rebalance each prompt/tool call |
| 22:03–23:05 | Tailscale/tailnet private connection | The user phrase “tailgate” refers to **Tailscale/tailnet** in this context |
| 23:11–24:50 | Fleet-management repository and reproducible host bootstrap | Record tools, machine identity, workspace roots, transport and installed receipts |
| 25:13–26:13 | Codex desktop endpoint behavior and parallel native/router profiles | Preserve current account directories and active shared CLI installs |
| 26:18–29:08 | Provider reset behavior and promotional resets | Only observed reset timestamps/credits belong in routing; no invented guarantees |
| 29:08–38:35 | Complete outcome delegation | Bounded scope, checks, review, evidence and recoverable work |
| 38:35–50:06 | T3 inbox, snooze/settle, hosts, worktrees, PR follow-up | Attention state is separate from verification/completion |
| 41:09–41:40 | Forthcoming orchestrator and queue/steer feature request | This was not shipped behavior in the video |
| 43:05–43:40 | Capture the whole current UI and ask an agent | Save baseline screenshots before customization; compare later against exact UI state |
| 46:21–47:06 | Preview, PR, and continued PR follow-up | Original linked 47:06 is a PR readiness example, not Claude Projects coordination |
| 50:06–59:05 | Broader experiments and inbox-based review | Useful spare-capacity tasks include independent research/review, not arbitrary token burn |
| 53:05–54:46 | T3 Connect or direct Tailscale transport | Native service/transport, inference routing, and project persistence are separate |
| 59:05–66:36 | Always-on remote tools | Awake host availability matters; extra Macs add tool capacity, not model quota |

The video makes account-ban/IP-detection claims, model-value comparisons, and provider-reset explanations that were not independently established. The transcript also contains a direct caveat at 14:45 that the setup may violate terms or cause bans. Those statements are evidence of what was said; they are not reliable configuration guarantees.

## Prior results: completed versus pending

These are recovered 6–7 October receipts, not a fresh installation/readback by this lane.

| Item | Recovered result |
|---|---|
| T3 desktop/CLI | Official Alpha 0.0.45 installed; download hashes verified, codesign/Gatekeeper checks passed |
| Provider binaries | Isolated Codex 0.160.1 and Claude Code 2.1.292; shared Codex 0.153.4 / Claude 2.1.291 preserved for active work |
| Local service | Own data root `~/.local/share/t3-anton`, loopback `127.0.0.1:3773`, requires logged-in awake Mac |
| Real Codex task | Completed a read-only sandbox instruction and returned its exact README sentence; README unchanged; about 123 seconds, not a speed benchmark |
| Real Claude task | Installed/authenticated Max profile reached weekly quota; turn error, no changed files; reported reset 8 October 10pm New York |
| Remaining native accounts | Two extra Claude profiles prepared but unsigned-in; three extra Codex sign-ins still required in prior receipt |
| M4 | Selected main host, `Antons-MacBook-M4MAX.local`, prior LAN `192.168.40.201` |
| M1 | `Antons-MacBook-Pro-M1MAX-2.local`, prior LAN `192.168.40.134`; SSH reachable after Remote Login enabled |
| M3/Olympus | `Antons-MacBook-Pro.local`, prior LAN `192.168.40.66`, user confirmed identity; SSH reachable after Remote Login enabled |
| Worker gates | Usernames, authenticated SSH and remote pairing remained pending; no worker installation proven |
| Sleep | Persistent keep-awake not changed; installation alone did not establish overnight availability |
| Coordinator | Detailed design existed; no implemented/released coordinator was claimed |
| Browser evidence | Headless screenshots/receipts saved; temporary verification browser sessions revoked and their pairing/cookie files removed |

The initial fleet paragraph in the installation receipt says SSH refused; its final connectivity update supersedes that observation. Do not treat the early paragraph as the final state. `.255` is the subnet broadcast address, not a fourth worker. The desktop Claude account and CLI profile showed different reset times; map identities before attributing quota.

The original source pin was T3 main `bfec2387b8102975c84690f99be0f5f834fd0cbe`, installed release `v0.0.45`, and shared-context commit `4729f774f7f918f1baa18209c6f3fb2fab0cc9ca` at `2026-10-07T01:44:43Z`. These pins preserve provenance, not current versions.

## Official upstream recheck on 7 October

| Product | Fresh result | Adoption boundary |
|---|---|---|
| SpecWeave | Local `specweave --version` and `npm view specweave version` both returned **3.0.3** | No upgrade required by this check |
| T3 stable | GitHub latest non-prerelease remains **v0.0.45**, published 2 October | Already-installed release is still current stable |
| T3 official nightly | **v0.0.46-nightly.20261007.2761**, commit `10f39eb9ac80c9a4b7f5097575dd2addc3b6f631` | Optional isolated evaluation; prerelease, not proof of production stability |
| T3 main | `f60367b8cb5e4a7e5e12dd01dc3889618151b1be` observed, committed `2026-10-07T06:49:18Z` | Moving source; pin any implementation reference |
| CLIProxyAPI | **v8.0.17**, published `2026-10-07T01:32:41Z`; darwin arm64/amd64 assets and checksums exist | Latest current official proxy core |
| VibeProxy | **v1.8.325**, published 6 October, bundles **CLIProxyAPI 8.0.16** | Native Mac launcher/GUI, one core release behind standalone latest |
| Management UI | `router-for-me/Cli-Proxy-API-Management-Center`, active official project | Stock customizable WebUI; not Theo's personalized UI |
| Theo fork | Public lookup for `t3dotgg/CLIProxyAPI`, `t3dotgg/vibeproxy` returned 404; repo searches under Theo/Ping returned no match | No recoverable public custom fork established; do not claim nonexistent/private access |

Sources: [T3 stable](https://github.com/pingdotgg/t3code/releases/tag/v0.0.45), [T3 nightly](https://github.com/pingdotgg/t3code/releases/tag/v0.0.46-nightly.20261007.2761), [CLIProxyAPI 8.0.17](https://github.com/router-for-me/CLIProxyAPI/releases/tag/v8.0.17), [VibeProxy 1.8.325](https://github.com/automazeio/vibeproxy/releases/tag/v1.8.325), [VibeProxy changelog](https://github.com/automazeio/vibeproxy/blob/v1.8.325/CHANGELOG.md), [Management UI](https://github.com/router-for-me/Cli-Proxy-API-Management-Center).

GitHub release digests for isolated T3 nightly evaluation:

```text
t3-0.0.46-nightly.20261007.2761-darwin-arm64.tar.gz
SHA256 02c191e2a3ed5c3d8c9808d6039884cda18e72426130d062bfbd1b024a5dc3fe

T3-Code-0.0.46-nightly.20261007.2761-arm64.dmg
SHA256 e6db35ff0f6b8d780c6237115a8cdc906f28316a5bf3cc85b731e60312f133c6
```

These were read from release metadata; this lane did not download or verify those binaries.

## Requested customizations mapped to current source

| Customization | Current evidence | Required verification |
|---|---|---|
| Dashboard resembling video | Video describes a customized VibeProxy starting point, not stock T3 UI | Baseline and after screenshots, actual account labels/window data, phone/desktop, light/dark |
| Prefer earliest reset | CLIProxyAPI supports priority plus round-robin, weighted-round-robin and fill-first; source selector does not show automatic weekly-reset sorting | Deterministic selection over fresh eligible observations; unknown reset stays unknown; priority applies to new binding/failover |
| Session/account affinity | v8 config defaults **false**, unlike the video's broad default claim; when enabled an existing binding outranks a recovered higher-priority account | Same-session reuse; subagent behavior; cooldown failover; no churn per tool call |
| WebSocket acceleration | Upstream executor uses WebSocket only when downstream is WebSocket and selected credential has `websockets` enabled; HTTP fallback exists | Capture observed transport, completed real turn and measured latency; do not claim speed from a flag |
| Tailscale access | Private transport makes chosen hosts reachable; device enrollment/access policy still determines who may connect | Exact three host identities, explicit access, connection test; API authentication remains separate |
| Fleet bootstrap | Own host-local installs/config/database/worktrees, checked against native active owners | Version/readback plus real sandbox task on each host; no shared live SQLite/worktree |
| Account exhaustion switch | Native compatibility determines resume; otherwise new run from checkpoint | Old owner paused, exact dirty state preserved, target identity known, no duplicate writer |
| Latest fork from T3 | Official nightly contains newer orchestration and portable handoff docs | Separate pinned install/data root, recovery/transport smoke tests, rollback receipt |

Pinned configuration/source: [v8.0.17 example config](https://github.com/router-for-me/CLIProxyAPI/blob/v8.0.17/config.example.yaml), [credential selector](https://github.com/router-for-me/CLIProxyAPI/blob/v8.0.17/sdk/cliproxy/auth/selector.go), [credential priority metadata](https://github.com/router-for-me/CLIProxyAPI/blob/v8.0.17/sdk/cliproxy/auth/priority.go), [Codex WebSocket executor](https://github.com/router-for-me/CLIProxyAPI/blob/v8.0.17/internal/runtime/executor/codex_websockets_executor.go).

Current operational defaults matter: an empty server host binds all interfaces, the proxy port is 8317, management is local-only by default and requires a configured key, and a client key authenticates the inference API separately. Set loopback explicitly for local evaluation. Do not infer that a tailnet makes an unauthenticated API harmless. [Configuration](https://github.com/router-for-me/CLIProxyAPI/blob/v8.0.17/config.example.yaml), [Tailscale access control](https://tailscale.com/docs/features/access-control).

The source defaults also include upstream identity cloaking. Its presence is a compatibility mechanism in third-party code, not provider authorization. This is a specific source-level limitation of that integration, not a reason to block native account handoffs.

## Native account and gateway boundaries

Current T3 Codex docs allow compatible accounts to continue the same thread. For multiple native CLI logins, shared `CODEX_HOME` plus separate shadow login directories share sessions/config while isolating auth. Copying a whole Codex home into the shadow is explicitly discouraged. Fully separate homes cannot continue the same native conversation. [Pinned Codex provider guide](https://github.com/pingdotgg/t3code/blob/v0.0.46-nightly.20261007.2761/docs/user/providers-codex.md).

Claude profiles use `CLAUDE_CONFIG_DIR`, preserving `HOME` and native keychain behavior. Existing threads can switch only between instances sharing the same config directory; separate account directories isolate native conversation state. A router preset uses its own config directory and environment variables. [Pinned Claude guide](https://github.com/pingdotgg/t3code/blob/v0.0.46-nightly.20261007.2761/docs/user/providers-claude.md).

The nightly handoff selects bounded historical messages, retains retrieval references and leaves the new user input intact. It excludes hidden reasoning, tool-call state and attachments. Default history cap is 16,000; operators can configure a 1,024–64,000 bound. This is context continuity with disclosed omissions, not lossless session transplantation. [Pinned portable-handoff guide](https://github.com/pingdotgg/t3code/blob/v0.0.46-nightly.20261007.2761/docs/user/portable-handoffs.md).

Anthropic's current authentication rules distinguish native self-login from a third-party service collecting/intermediating subscription credentials. They explicitly preserve an end user signing into an unmodified Claude Code binary, while prohibiting developers from collecting/storing/intermediating Claude.ai credentials or routing consumer subscription credentials for users. Keep native CLI authentication as the supported baseline; proxy feature claims do not override these rules. [Anthropic authentication rules](https://code.claude.com/docs/en/legal-and-compliance).

OpenAI documents ChatGPT-plan access through Codex app-server and its authorized token flow. A model catalog is not an entitlement check; a successfully completed turn is the access receipt. The documented example uses `supports_websockets=false`, so WebSocket support must be checked for the actual authentication/provider path rather than blindly forced. [OpenAI app-server integration](https://developers.openai.com/siwc/token-sharing-open-source/codex-app-server).

Vercel separately documents a Claude Code Max passthrough arrangement: native Claude login, the `/claude-code` base URL, and a separate gateway header. This is a documented Vercel path, not evidence that CLIProxyAPI's account pooling is sanctioned by Anthropic. Vercel's automatic setup configures API-key billing only; the subscription flow requires manual custom-header configuration. [Vercel Claude Code Max integration](https://vercel.com/docs/ai-gateway/coding-agents/claude-code#with-claude-code-max).

## Adjacent products and what to borrow

These are the prior report's researched comparisons; this lane did not install competitors or reverify every live claim.

| Product | Useful mechanism | What SpecWeave should own |
|---|---|---|
| Claude Projects | One coordinator, reusable workers, decisions and memory index | Portable project/task identity across account-scoped hosted projects |
| T3 Code | Inbox, worktrees, remote hosts, native providers, PR follow-up | Intent ledger, verified handoff and completion evidence |
| BridgeMind One | Persistent named teammates, agent messages and approved folders | Cross-account portable briefs; original-account native resume remains distinct |
| Superset | Explicit coordinator through CLI and isolated remote workspaces | Reuse execution interface rather than adopt a competing task store |
| Conductor | Isolated Mac workspaces/branches and review UX | Portable task continuity and cross-host coordination |
| Paseo / Happy | Headless/mobile remote control | Durable project and ownership semantics |
| cmux | Native operator cockpit and notifications | Task truth and recovery |
| Vibe Kanban | Board, workspaces and PR lifecycle | Keep verified SpecWeave state authoritative |
| Gas Town | Explicit workers, mail, merge/coordinator roles | Borrow patterns while preserving the existing ledger |
| OpenHands | Control versus execution separation | Existing subscription entitlement semantics |
| Superconductor / Cursor / Devin | Managed/cloud task and review experience | User-owned repo/fleet and provider portability |
| Dots | Persistent assistant, delegated work and decisions | Three-host coding coordination remains separate |

Full linked primary references and limitations remain in the recovered [competitor comparison](/Users/antonabyzov/Projects/research/claude-projects-2026-10-06/report.md:171).

## Name and positioning

**SpecWeave remains a good name for the durable engineering layer.** “Spec” signals accepted intent; “Weave” fits connecting tasks, agents, hosts and evidence. Its weakness is that it sounds like a specification writer when the product is expanding into execution and recovery. Address that with a clear descriptor before considering a costly umbrella rebrand.

Recommended architecture: **SpecWeave** umbrella, **SpecWeave Control** coordinator/attention surface, **SpecWeave Handoff** continuation/recovery, and **AnyModel** only for the separate provider-routing capability if the existing product already owns that name. Keep CLIProxyAPI/T3 implementation names in integration settings, not core product promises.

Suggested public sentence: **Your coding project keeps going when its tools or accounts change.** Supporting proof should show the same accepted task, preserved Git state, a visible new execution run, and verified completion. Avoid promises of merged subscriptions, unlimited usage, invisible account switching, or lossless native-session migration.

This is a product-positioning recommendation, not trademark/domain clearance. No rename was applied.

## Concrete next verification order

1. Preserve baseline UI, account/host inventory and exact source/runtime pins.
2. Finish native sign-ins and authenticated host connection without copying secrets into the research artifacts.
3. Prove one completed sandbox task per enabled provider/account/host combination.
4. Test earliest-reset selection with deterministic observations, then real eligible accounts; verify affinity wins for existing work.
5. Test a quota interruption and stopped-writer checkpoint/restore into an isolated target; compare tracked/untracked artifact hashes and actual tests.
6. Test coordinator crash/restart and repeated message delivery without duplicate execution.
7. Verify UI at desktop/phone widths in both themes; all automated browser launches explicitly headless, `PWDEBUG=0`, `PLAYWRIGHT_HTML_OPEN=never`.
8. Record source, installed version, enabled account, host, completed runtime result and rollback independently.

Jev routing was attempted and returned exit 4 because no provider key was configured. Research continued without it. No pickup, task claim, owner takeover, provider authentication mutation, visible browser session, or message to another Codex chat was performed in this lane.
