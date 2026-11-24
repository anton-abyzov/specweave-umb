# 1209 Create, publish, and apply skills in SpecWithCode

## Problem
Repeated useful instructions have no direct authoring path from SpecWithCode's Skills surfaces. Users must understand a separate authoring tool, publication and installation before reusing them. Anton wants description-driven generation with his chosen model, versioned publication through review, then immediate project or user application.

## Scope
Anton approved the recommended design defaults in this thread on November 3, 2026. V1 implementation is authorized. On November 4, 2026, Anton explicitly authorized merge, deployment and thread resolution for this feature, superseding the earlier branch/commit restriction within this scope. Preserve unrelated owners and coordinate the release dispatcher. No real user skill publication or new provider spend is implied. Increment 1208 and the active “Skills counts and agent filter” worker own the counts/filter fix; reconcile their completed contracts before any future integration.

Proposed v1: a shared Create skill sheet from composer Skills and Settings > Skills; describe/manual authoring, model choice, editable review, publish status, exact-version installation and refreshed discovery. Proposed v2: opt-in suggestions from repeated user instructions. Exclude plugin authoring, automatic publication/installation, unrestricted chat mining, fleet-wide propagation and evaluation dashboards from v1.

## Acceptance Criteria
- [ ] AC-01: The proposal traces Skill Studio generation, publication, versioning and current SpecWithCode surfaces to source evidence, distinguishing source from installed behavior and current latency from historical observations.
- [ ] AC-02: The decision page shows Describe → Review and publish → Apply, mobile and desktop mockups, error states, and explicit decisions before implementation.
- [ ] AC-03: After approval, both entry points open the same draft-preserving form; generation uses the chosen available provider instance/model without silent paid fallback and manual editing works without a model.
- [ ] AC-04: Publication shows destination/visibility/version and exact content; queued, reviewing, rejected, blocked and published remain distinct, with durable resume and no duplicate submission on retry.
- [ ] AC-05: Apply installs the published identity/version into the selected project or user scope on the selected machine and agents; readback and discovery establish readiness without sending a chat message or restarting active work.
- [ ] AC-06: If approved for v2, suggestions explain their supporting user messages, are deduplicated and dismissible, respect exclusions and never create/publish/apply automatically.

## Approach
### Research findings (November 3, 2026)
Read-only local source snapshots: vskill `460442f1daddc8963b96e89f71954fc5060a91b5`, vskill-platform `bc84b94d5f5dbf76290a9c8c1ffa6685498c141a`, specwithcode-dev `d1fd21d39f98590de2311f1337a2b3f436203d9f`. These are local source observations, not installed UI verification. The companion decision page links the evidence files.

Skill Studio's CreateSkillPage and useCreateSkill offer AI/manual modes, provider/model selection persisted in preferences, prompt, editable name/description/body, target agents, an authoring-engine selector and standalone/plugin placement. Generation passes prompt/provider/model/targets/engine. User-chosen name and standalone placement override AI suggestions. Reuse the generation contract and validation ideas; do not copy all advanced choices into the first screen. SpecWithCode should use its own live provider-instance catalog and existing model picker, not Skill Studio's provider defaults or static captions.

PublishButton and PublishDrawer perform commit/push and queue submission as separate steps, preserve successful push when submission fails, carry skillPath, privacy and publishing account, and expose structured duplicate/already-verified/requeued/blocked outcomes. The drawer's existing repository-wide staging is not appropriate for arbitrary SpecWithCode working folders. Proposed publisher uses an isolated skill bundle or explicitly scoped repository changes, never unrelated user edits. Local private-publishing gate is true; runtime availability, account entitlement and tenant access still require live checks.

The queue distinguishes RECEIVED, TIER1_SCANNING, TIER2_SCANNING, AUTO_APPROVED, PUBLISHED, rejection/failure and held/re-scan states. Approval is not yet publication. The platform stores per-version file manifests and hashes and handles declared version bumps. New documents use metadata.version as a quoted SemVer and name equal to the installed folder. Skill version, plugin version and installed version are separate identities.

Timing: no current measured publish SLA was established. Project memory reported an October 20 backlog and a private probe within two minutes; both are historical, not current queue health. The public queue web response was cached and cannot settle current latency. Show actual progress/elapsed time and permit closing the sheet; do not promise “published in seconds.” Measure submit-to-published p50/p95 before shipping an ETA. Published does not imply effective: registry security/model review and task evaluation are distinct.

ComposerSkillsPopover currently groups agent-discovered skills with project snapshot/version data, optional search, session-use information, Rescan and Open Skills settings. It has no create form. ProjectSkillsSettings handles user/project and machine context, inventory/search/filters, source/tier/version details and controls. ProjectSkillsActions previews writes, checks stale hashes, installs exact versions, respects scope and refreshes inventory/provider discovery. Extend that safety boundary rather than shelling out from the UI. Counts/filter files remain owned by 1208.

### Proposed interaction
1. Entry: “Create skill” in the popover footer and Settings header. A message overflow action “Turn into skill” seeds the same form with only the chosen user text. No full-chat attachment by default. Keep the composer draft intact.
2. Describe: one textarea (“What should this skill do?”), compact existing provider/model picker (current thread selection, otherwise last authoring selection), Generate draft; secondary Write myself. Advanced options are collapsed. Show account and billing mode in the existing picker. No generation on opening the sheet. Cancel preserves prompt; failure preserves edits; switching models requires another explicit Generate.
3. Review and publish: editable title, invocation name, When to use, instructions, example input/output and version. Show a short summary with expandable full SKILL.md and bundled files. Default proposed version 1.0.0, later patch suggestion with diff; never overwrite an existing version. Checks include name/folder, SemVer, missing prerequisites, secrets and selected-agent compatibility. Preview data leaving the machine. Explicit publishing account/repository and Public/Private choice; recommend private when entitled, otherwise keep a draft until user explicitly selects public. Never silently downgrade visibility. Publishing may require connecting an account; no sign-in needed merely to draft.
4. Status: Submitting → Queued → Checking → Published vX.Y.Z. Persist submission identity with draft; reconnect fetches it. Rejected shows findings + Edit draft; blocked shows actual reason; network failure offers status check before retry. During wait show “You can close this; we will keep the status here.” No spinner implying a short fixed duration. Keep publish state separate from apply state.
5. Apply: radio “This project” (default from composer/project Settings) or “My projects on this machine” (user scope). Show concrete project/folder, machine and compatible agents, defaulting to current agent. User Settings defaults user scope. Explain project override of a same-name user skill; conflict preview offers update or rename, never silent overwrite. Preview exact published identity/version/hash, then Apply. Re-read lock + installed file and refresh discovery. Show “Ready for the next message” only after that agent reports it; otherwise “Installed; start a new session to load” with no forced restart. “Insert into message” adds a chip and preserves unsent text; never auto-sends. No silent copying to other machines.

### Suggestions, later
Deferred from v1 by Anton's approval of the recommended defaults; off by default in any later implementation. Evaluate only user-authored messages in opted-in projects after completed interactions, excluding assistant text, quoted documents/tool output, passwords/secrets, private excluded threads and near-duplicate retries. Candidate rule to validate: same reusable intent across at least three distinct conversations on at least two days, with repeated constraints/output shape, and no equivalent installed skill. Frequency alone is insufficient: prefer successful repeated workflows, reject generic questions and one-off facts. Local normalization/dedup first; any semantic model analysis uses the opted-in selected provider with explicit data scope and a small budget, never a hidden cloud fallback.

One quiet “Make this reusable?” item inside Skills, never a modal/toast over typing. Show why, the exact supporting excerpts and a link to each accessible source. User can edit included examples, create draft, dismiss this pattern, snooze suggestions or turn them off. Initial product hypothesis: at most one new suggestion per week per project, 30-day candidate window; dismissal suppresses the intent until explicitly reset. Delete candidate data on opt-out; cross-project analysis is separately opt-in. Measure accepted-and-reused suggestions, dismissal rate and false positives, not raw impressions. These thresholds are proposed defaults, not tested results.

### Standalone versus plugin
Default to a standalone standards-compatible skill. A generation model is an authoring choice, not a runtime dependency. Disclose provider-specific tools/fields when necessary rather than forcing a plugin. Plugins are useful when a coherent bundle needs hooks, MCP, commands or coordinated distribution.

A changed bundled skill can ship through a new plugin release and its plugin update/reinstall, but it is a bundle operation, not automatic publication of an independently versioned skill. The inspected vskill update.ts explicitly skips user-level plugin entries and prints the reinstall command. SpecWithCode's inspected version action installs a versioned individual skill; plugin toggles are a separate path. Therefore do not claim the existing Skills update action universally updates plugin-contained skills. A later plugin flow must preview the bundle diff, bump/publish the plugin version, use its provider-specific updater and verify the loaded contents; sibling skills may change too. A manually edited cache or a skill-only metadata bump does not establish that delivery.

## Decisions
### Asked
- Anton answered “Yes, approved” to the recommended defaults on November 3, 2026.
- D-01 Approved: describe/generate → review and publish → apply; Save draft throughout.
- D-02 Approved: private when available; otherwise explicit public choice.
- D-03 Approved: manual creation first; opt-in suggestions later.
### Defaulted
- Shared three-step sheet; standalone first; project default from a project context; explicit apply after publication; preserve drafts and active sessions.
- No publication-in-seconds promise, no auto-apply, no silent public publication, no automatic paid fallback.
### Open
- None for the v1 design. Integration ownership must be reconciled before editing the existing Skills surfaces.

## Tasks
### T-01 Research and design the decision page
- AC: AC-01, AC-02 | Files: spec.md, decision.html, evidence.md | Test: headless html_preview at 390px and 728px in light/dark; inspect source citations

### T-02 Implement the approved authoring sheet after ownership reconciliation
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/skills/SkillAuthoringSheet.tsx, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/SkillAuthoringService.ts | Test: repository typecheck and focused authoring behavior tests; headless generate/manual/cancel/resume flow

### T-03 Connect review queue and versioned publication
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/SkillPublishingService.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/skills/SkillPublicationStatus.tsx | Test: duplicate retry, visibility refusal, rejection and reconnect tests; authorized staging submission readback

### T-04 Integrate scoped application and approved entry points
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/skills/SkillApplyPanel.tsx | Test: headless project/user scope, stale preview, conflict and agent-discovery checks

### T-05 Implement suggestions only if approved
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/SkillSuggestionsService.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/skills/SkillSuggestionCard.tsx | Test: opt-out/exclusion/dedup/cooldown tests and headless dismiss/create-draft flow

### T-06 Verify and close 1209
- AC: AC-03, AC-04, AC-05, AC-06 | Files: evidence.md | Test: specweave verify 1209; fresh-context review; specweave complete 1209

Implementation file names are proposed, not ownership claims. Before starting, resolve exact integration contracts/files with 1208 and amend this plan to cover every edited file. T-02 through T-04 are authorized; T-05 is deferred by the approved v1 scope. Preserve the counts/filter worker ownership until their handoff is explicit. T-06 closes this increment after the approved work is verified and reviewed. No future tests above are claimed as run.

## Delivery continuation, November 4, 2026

1208 integration ownership was explicitly released for the two Skills entry files after PR #1289 merged at `2b2ed0610bcf2f7e21f4870c10bd5364e7e13891`. Current shared app checkout contains active unrelated 1237 changes across transport, runtime and contracts. Coordinator asked to settle a safe checkout/integration slot and release owner. No 1209 implementation or deployment exists yet; do not resolve it from the design receipt.


## Successor implementation scope, November 4, 2026

The successor owns T-02 through T-04 in `/Users/antonabyzov/.specwithcode/m4/worktrees/specwithcode-dev/feat-1209-skill-authoring`, branch `feat/1209-skill-authoring`, based on `33977257672eca4795289991e277522d21548999`. The previous owner explicitly stopped. No shared checkout edits, stash, merge or release dispatch are authorized. Delivery in this scope ends with the verified PR against `main`; the dispatcher retains merge and release ownership.

The implementation uses three disjoint lanes under `sw:do`: authoring service and shared RPC plumbing, publication/application adapters, and web UI. The parent owns ledger updates and final integration. T-02 additionally covers the focused authoring tests and minimal contract, guarded RPC, client command and provider text-generation plumbing required to expose the selected model safely. T-03 includes publication adapter tests and guarded handler integration coordinated through the plumbing owner. T-04 additionally covers the released `apps/web/src/components/chat/ComposerSkillsPopover.tsx` and `apps/web/src/components/settings/ProjectSkillsSettings.tsx` entry points, `apps/web/src/components/skills/SkillAuthoringSheet.test.tsx`, and focused application tests. All code paths in this paragraph are relative to the owned app worktree. Exact added integration paths will be recorded with verification evidence. No `ws.ts` imports are permitted.


### Exact integration file allocation

T-02 authoring plumbing additionally owns `apps/server/src/textGeneration/TextGeneration.ts`, `apps/server/src/textGeneration/TextGenerationOperations.ts`, `apps/server/src/textGeneration/TextGenerationOperations.test.ts`, `apps/server/src/project/SkillAuthoringService.test.ts`, `apps/server/src/project/ProjectSkillsActionsRpc.ts`, `packages/contracts/src/skillAuthoring.ts`, `packages/contracts/src/index.ts`, `packages/contracts/src/projectWorkspaceRpc.ts`, `packages/contracts/src/clientRpcPermissions.ts`, and `packages/client-runtime/src/state/projectWorkspace.ts`. The plumbing owner integrates the other lanes' handlers in the existing RPC module.

T-03 publication additionally owns `packages/contracts/src/skillPublication.ts`, `apps/server/src/project/SkillPublishingService.test.ts`, and `apps/server/src/project/SkillPublishingAdapter.ts`. T-04 uses that adapter for publication-bound installation. These paths are relative to the owned app worktree named above. The planned validations remain unchanged; added files make the approved flows reachable and testable.


### Server-lifetime integration repair, November 6, 2026

T-02 additionally owns `apps/server/src/server.ts` in the assigned app worktree to construct the authoring service once per server. WebSocket clients must share draft revision locks and installation serialization. The existing RPC module consumes that server-owned service. Verification includes an isolated built-server probe with competing saves over separate WebSocket connections; no live stores, provider turns or publication are used.

T-02 also includes a minimal `apps/server/src/ws.ts` composition edit using the already-imported Skills RPC module to capture the server-owned service before request context creation. No imports are added to `ws.ts`.

T-02 regression scope includes `apps/server/scripts/skill-authoring-rpc-check.mjs`: a retained isolated live-server check for real authoring read/save and revision conflicts across 20 independent WebSocket connections.

T-06 includes the minimal `scripts/release-workflow.test.ts` CI portability repair: use `fileURLToPath` rather than URL pathname when passing the Python script to a Windows subprocess. The Windows packages gate failed on the inherited drive-letter path; current main still has the same bug. No release behavior is changed.

T-06 also includes `scripts/release/run_record.py` and `scripts/release/test-run-record.py`: defer the POSIX locking import until a write so the read-only graph command runs on Windows. Keep write locking unchanged and test graph execution with fcntl unavailable.

T-06 includes Windows fixture corrections in `apps/server/src/workspace/WorkspaceSearchRoots.test.ts`, `apps/server/src/provider/acp/AcpRegistryAuth.test.ts`, and `apps/server/src/homeUsage/walkTree.test.ts`: use the actual host platform for real symlink resolution and native path construction for mocked filesystem and credential expectations. Preserve all existing assertions.

T-06 includes `scripts/release/verify-built-app.test.mjs` portability under the release owner’s explicit handoff: preserve Windows refusal of proofs/upgraded mode, use native expected paths, and restrict POSIX shell fake suites to their supported hosts. Production verifier stays unchanged; macOS CI retains the full proof suites.

T-06 includes `apps/server/src/homeUsage/homeUsage.test.ts` and `apps/server/src/workspace/WorkspaceSearchFinder.test.ts` Windows fixture fixes: native paths for filesystem results and a POSIX-only wrapper for the macOS lsof executable fixture. Retain the Windows unknown-process assertion and cross-platform parser coverage.

T-06 also covers `apps/server/src/project/CoordinatorRearmStore.test.ts` POSIX permission assertion portability and the Linux-mock Path layer in `apps/server/src/project/SkillPublishingAdapter.test.ts`.
