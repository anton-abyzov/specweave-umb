# Vault context and current AnyModel inventory

Recorded 2026-10-07, America/New_York. Read-only Obsidian Brain Query across personal-docs, engineering-docs, and ai-power. No notes, indexes, credentials, schedules, claims, or existing checkout files were altered. Credentials-Secrets-Passwords and .obsidian were excluded from searches. Query logging was omitted because this lane was explicitly instructed not to alter notes.

## Result

The vault has useful historical context for AnyModel, local inference, three Macs, and portable SpecWeave handoff. It does not contain T3 Code, Claude Projects, CLIProxyAPI, CLI Proxy, or portable coordinator installation records. The screenshots' October 6 report/transcript must be recovered from the research/chat artifacts rather than assumed to exist in Obsidian. Tailscale appears only as an unrelated comparison in AWS notes; there is no vault evidence that it is installed or configured on these Macs.

AnyModel is a separate repository, not a nested repository in specweave-umb. Its local source is behind the registry and upstream. The May proxy failure list is historical: most listed failures already have implementation and tests in the local June source. AnyModel's current local code is an API/local inference bridge, not a seven-subscription quota router. SpecWeave's existing portable handoff/project hub is the appropriate durable context layer for switching official CLI sessions.

## Sources consulted

Primary index: `/Users/antonabyzov/Projects/Obsidian/personal-docs/wiki/index.md`, catalog updated 2026-09-30 with 445 pages. Focused searches then consulted these relevant pages:

- [[anymodel]] — entity/proxy summary, updated 2026-05-30; source `/Users/antonabyzov/Projects/Obsidian/personal-docs/wiki/anymodel.md`.
- [[2026-05-30-anymodel-improvement-plan]] — dated P0/P1/P2 failure list, baseline and proposed fixes; source `wiki/sources/2026-05-30-anymodel-improvement-plan.md`.
- [[2026-05-30-qwen3-coder-tool-calling-mcp-handover]] — Anthropic/OpenAI translation, tool IDs, local-server parser, MCP boundary; source `wiki/sources/2026-05-30-qwen3-coder-tool-calling-mcp-handover.md`.
- [[local-agentic-coding-stack]] — Qwen/LM Studio/AnyModel routes and performance caveats; source `wiki/synthesis/local-agentic-coding-stack.md`.
- [[anton-mac-fleet]] — three physical Macs, changing browser identifiers, M3 identity correction; source `wiki/entities/anton-mac-fleet.md`.
- [[claude-code-ultracode-fable-default]] — dated desired model/effort settings and Desktop picker drift; source `wiki/concepts/claude-code-ultracode-fable-default.md`.
- [[ai-resets]] and [[ai-rate-limit-resets]] — rate-limit product and historical quota/reset concepts; sources `wiki/entities/ai-resets.md` and `wiki/concepts/ai-rate-limit-resets.md`.
- [[specweave-team-lead-patterns]] — May orchestration/closure lessons and BYOK interpretation; source `wiki/specweave-team-lead-patterns.md`.
- [[openclaw]] — draft April orchestrator note with ClawdBot alias; source `wiki/concepts/openclaw.md`.

Cross-vault searches found no current installation or switching evidence in engineering-docs or ai-power. This is a search result, not proof that no unpublished material exists elsewhere.

## Contentions and stale claims

| Source claim | Current finding | Consequence |
|---|---|---|
| [[anymodel]] first says pure stateless OpenRouter passthrough and zero authentication, then describes a five-provider bridge with a shared proxy token. | The page itself has a May update that supersedes its opening. Current local source exposes five providers plus transport translation and optional shared-token auth. | Interpret zero auth as no user-account system; do not advertise no proxy access control. |
| May improvement plan says EOF-without-DONE, stalled upstream, parallel tool fragments, multimodal loss, body limits, and credential stripping are broken. | Local 1.16.2 contains implementations and named regression tests for these areas. They have not been rerun in this read-only lane. | Re-audit the verified 1.17.0 release and run tests before proposing new fixes; do not duplicate old work. |
| Installed AnyModel development skill describes three providers and stripping all Ollama tools. | `cli.mjs:21-22` lists openrouter/openai/ollama/lmstudio/llamacpp. `test/ollama-tool-passthrough.test.mjs` and current local-provider docs show later behavior. | Skill content is stale; source/release readback outranks the skill's old implementation description. |
| [[anton-mac-fleet]] May map assigns GUID 9b2664a6 to M1. | The same page's September 11 correction assigns it to M3 and marks old M4 GUID absent. It also says all browsers report isLocal. | Verify device identity through live authenticated host facts; never select Mac by slot or isLocal. |
| Claude model/effort note records Fable as every-session default. | Its September screenshot shows Opus 5; the source cannot say if that was drift or deliberate. | Read current CLI/account model entitlement and actual returned model, and test fresh Desktop/CLI sessions. Avoid copying historical config keys blindly. |
| [[openclaw]] describes ClawdBot; memory says Clawd can mean Claude Code. | These are distinct contextual uses of an ambiguous name. | Screenshot/chat titles do not alone identify the product. The October transcript/research identifies it. |
| Old AnyModel 0008 and 0004 metadata remain active. | Later 0017 is completed, code includes earlier fixes, all parsed ledger final events contain no outstanding claim, but old metadata persists. | Do not run pickup or seize old work based on stale flags. New authorized work belongs in a separately owned checkout with current evidence. |
| SpecWeave 0881 excludes a second agent runtime and background scheduler. | Current hub says native tools own execution and scheduling. Portable intent/handoff and briefs are already shipped. | Add switching coordination through adapters/native official CLIs, retaining the existing intent/ledger authority. |
| Historical AI Resets pages give quota window/reset mechanics and a low-confidence forecast. | They are September snapshots; this lane did not verify provider policies. | They can inform UX vocabulary, not account eligibility or reliable quota prediction. Get fresh account readbacks. |

## Current AnyModel source inventory

Local umbrella: `/Users/antonabyzov/Projects/github/anymodel-umb`.
Source: `/Users/antonabyzov/Projects/github/anymodel-umb/repositories/antonoly/anymodel`.
Local branch: `main`; clean working tree; one local Git worktree.
Local commit: `48dfcea084968f349b713b1efaae5bad904ea11d` (2026-06-04); package `1.16.2`.
Registry latest: `1.17.0`, verified with npm on 2026-10-07; gitHead `a0fe2077fbc28602c0f0e0d308355daff8b4d1c0`; integrity `sha512-ezmaF9wBUTXSb2LkamN/KWGF2jLN6Da0f0GIxsonw8i2X8mFwX9APRIKBH2Hq0qwozSx8vBRun0ac1X3C9H2rg==`.
Authenticated GitHub API main readback: `f0639894c85408bb1d81143f2ca63530d3a1c324`, committed 2026-06-11T02:50:03Z, title `chore: ignore vercel link artifacts`.
SSH `git ls-remote origin` failed with Permission denied (publickey); authenticated `gh api` succeeded. No shared remote config was changed.

| Area | Current source evidence |
|---|---|
| Five providers | `cli.mjs:21-22`; `providers/{openrouter,openai,ollama,lmstudio,llamacpp}.mjs` |
| EOF flush | `proxy.mjs:1032`, `providers/openai.mjs:682`; `test/stream-flush.test.mjs` |
| Text tool-call recovery | `providers/openai.mjs:310`, `:493`, `:571`; `test/{text-toolcall-recovery,stream-text-toolcall-recovery,stream-recovery-followups}.test.mjs` |
| Parallel tool-call correlation | per-index tool maps in `providers/openai.mjs:588`; `test/stream-parallel-toolcalls.test.mjs` |
| Upstream idle timeout | `proxy.mjs:378-381`; `test/upstream-timeout.test.mjs` |
| Loopback and credential guard | `proxy.mjs:77-97`, `:1631`; `test/security-defaults.test.mjs` |
| Body cap | `proxy.mjs:102-104`; requests produce 413/502; same security tests |
| Images/tool results/sampling | `test/{content-translation,image-attachments,tool-result-multimodal,sampling-and-finish}.test.mjs` |
| Codex/local OpenAI wire | local-provider-only `/v1/responses`, `/v1/chat/completions`, `/v1/models` branch at `proxy.mjs:1510-1537`; `providers/responses.mjs`; `test/{responses-bridge,openai-passthrough}.test.mjs` |
| Universal skills | `providers/{skill-bridge,skill-catalog}.mjs`, CLI launcher bridge, `.agents/.codex/.gemini/.agent` roots; `test/{skill-bridge,skill-catalog}.test.mjs` |
| Effort | completed increment 0017 maps compatible OpenAI reasoning/codex models, keeps local defaults safe; README and LOCAL_SETUP explain restrictions |
| Normal test command | `npm test` invokes `node --test test/*.test.mjs worker/test/*.test.mjs` |

No subscription OAuth provider, account pool, usage-aware selection, cooldown router, or cross-subscription handoff exists in the inspected local AnyModel source. Cloud OpenAI wire support is not established by its local-only Codex bridge.

`proxy.mjs` is 1657 lines, already over the 1500-line project limit. New changes there require extraction rather than further growth. `cli.mjs` is 747, `providers/openai.mjs` 922, `providers/responses.mjs` 264.

## Ownership and architecture constraints

SpecWeave installed and registry stable are both 3.0.3, freshly checked. Jev route returned exit 4 because no configured API key; continuation without Jev is allowed. No pickup, handoff, claim, fetch, checkout, test process, or source mutation was run in this lane.

SpecWeave umbrella is `main` at `b8c349902e6873408a1864a61e3665aae8cd031f` with existing dirty package/config/report/state files and many unrelated untracked reports. Preserve it. The hub's goal is portable intent/shared context/verified progress; it explicitly delegates agent execution and scheduling to native tools.

Read applicable decisions:

- SpecWeave ADR `0867-01-portable-handoff-document-as-cross-tool-context-boundary.md`: handoff document and scrubbed diff are the cross-tool boundary; proprietary transcript transcoding was rejected.
- Completed increment `0881-portable-project-hub/spec.md`: native executors, existing IntentStore/ledger, revision guards, bounded secret-scrubbed briefs, no second runtime.
- Completed increment `0877-portable-intent-product-redesign/spec.md`: developers/small teams switching coding tools; context harness-neutral; observed use is not causal quality ranking.
- AnyModel ADR `0002-pure-proxy-mode-strategy.md`: stock client through custom endpoint is additive and avoids bundled-client version lock; existing fork retained for compatibility.
- AnyModel ADR `0003-adaptive-branding-and-universal-skill-loader.md`: reproducible drift-checked branding for the bundled client, launcher-level skill bridge for stock-client compatibility.

## Safe implementation scope proposed

1. Refreshed, isolated AnyModel checkout anchored to verified registry/upstream source; compare 1.17.0 tree before touching old P0 areas. Install/test release as API/local model bridge. Preserve source root and provider credentials. Prefer stock official CLI entrypoints for subscription work.
2. New SpecWeave switching adapter lane in its own checkout, using current official CLI sessions per account with separate config homes/keychain identities. Registry stores nonsecret account labels/provider/host, not credentials. Usage-aware selection uses authoritative account telemetry; unknown stays unknown. Selection must exclude busy sessions and retain explicit account pinning.
3. Atomic handoff capture with repo/worktree/branch/commit/task owner, evidence, blockers, and next step; persist portable brief/scrubbed diff before switching. Resume only a safe owned checkout. An interrupted tool turn must not cause a second worker to execute the same task.
4. Capability and quota tests: fresh official CLI run per configured account; actual returned model; a deliberate synthetic exhausted-account signal; choose available eligible account; retain task edits/evidence; prevent repeated replay after tool side effects; prove reconnect after host sleep/restart. Local model fallback is a separate selectable route.
5. T3 UI/restoration work should live in a T3 fork/wrapper lane once the transcript and current installation identify the actual upstream/fork, with screenshots of existing state first and saved headless evidence afterward. Pair only verified authenticated hosts; fleet/browser GUIDs are insufficient.

SpecWeave remains a good top-level name for portable task intent and verified continuity. AnyModel should retain the proxy/runtime routing identity. A narrower feature label such as Subscription Switcher can communicate the new capability without rebranding the whole product; naming remains a product recommendation, not a completed change.

## Limits of this report

Current source inspection confirms code/test presence, not passing runtime behavior. It does not establish that three hosts can authenticate over SSH, seven subscription profiles are logged in, Tailscale is installed, provider-specific OAuth reuse is supported, or T3 restoration works. Those require fresh installation/account/host tests in the implementation lane.
