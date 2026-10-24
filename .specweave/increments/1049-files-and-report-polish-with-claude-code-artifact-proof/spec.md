# 1049 Files and report polish with Claude Code artifact proof

## Problem

Successor to 1035 (completed, PR specwithcode-dev#651) and 1043 (completed, PR specwithcode-dev#661 at `12d8775f0`, awaiting merge by Complete screenshot sessions). Anton asked for a deep check of Claude Code native artifacts and a polished, provider-independent Files and report experience (screenshot `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-41458206-6cf2-415f-97dc-1aac8f3cf784.png`).

1. **Native artifact capability is unproven live.** 1019 (`/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1019-investigate-claude-native-artifacts/reports/findings.md`) found the experimental Artifact tool contracts in Claude Code 2.1.302 and Agent SDK 0.3.276 (still the installed versions on October 24, 2026), an `sdk_default_off` gate and an undocumented `CLAUDE_CODE_ARTIFACT` opt-in. It proved offline transcript recovery only: no init roster, publish, read or update was observed, and entitlement was not checked. The app lists no native Artifact result anywhere: the Files list reads only links in message text (`apps/web/src/threadArtifacts.ts`).
2. **The Files popover hides what tells files apart.** `apps/web/src/components/chat/ArtifactShelfList.tsx:167` truncates the folder hint at the end, so `increments/1041-fix-d…` loses the distinguishing part. Pin and hide appear only on hover or focus (`:178`). A row has no source message, time or kind label. A file on an unreachable machine is not distinguished from one deleted from disk (`artifactShelf.ts:158` knows only `missing`).
3. **Property cards break paths mid-word.** The `kv` card (`apps/web/src/components/chat/StructuredBlocks.tsx:259-270`) uses `break-words`, so long paths and IDs split anywhere ("specweav / e-umb" in the screenshot).
4. **File links add a third column with a hidden close.** A chat file link opens in the right panel beside the coordinator and worker panes. The close action replaces the tab icon only on hover or keyboard focus (`apps/web/src/components/ui/panel-tab-close-button.tsx`). The 1035 owner's proposal (October 24, 2026, 01:31) recommends focused reading by default, a persistent labeled Close and opening beside the conversation only on request.
5. **Pins and hides do not travel.** They live in browser localStorage under `studio:artifact-shelf:v1:<environmentId>:<threadId>` (`useArtifactShelfState.ts:17-20`), so another device or a migrated thread starts empty.

## Scope

In: a current, cited capability record for the Claude Code Artifact tool versus claude.ai and desktop artifacts; display-only native Artifact references in Files, parsed from existing tool output; Files popover rows and file states (missing, unreachable machine, remote-only); path-aware wrapping in property cards; a persistent close and width-aware opening for the file reader; continuity of Files entries and choices across reloads, app updates, provider switches and machine migration; focused tests, headless fixture screenshots and interactions.

Out:
- Hosted publishing, live Artifact publish/read/update, and turning on `CLAUDE_CODE_ARTIFACT` in app-launched sessions. These need Anton's consent and a separate capability (1019 recommendation 4).
- Server and adapter edits, including `ClaudeAdapterV2` (1048, #643 and #477 touch it). Snapshotting native sources into attachments is a later server increment.
- `ChatMarkdown.tsx` and code styling (1038).
- Question cards and answers (1042); design workspace (1041, 1046); account-change resume (1047).
- 1043 behaviors (F-05, evidence links, worker message fold).
- Rewriting stored messages or historical reports.
- Merge, release, restart and installed acceptance, which stay with Complete screenshot sessions.

## Acceptance Criteria

- [x] AC-01: A capability record at `reports/native-artifacts-2026-10-24.md` in this increment states each claim with a source: Anthropic documentation or changelog URLs, the installed CLI and SDK versions, a credential-free init tool roster (isolated home, no login, no model call), and an offline replay of `ArtifactOutput` variants (publish, list, read, asset, subscription, error, interrupted). A table separates the Claude Code Artifact tool, claude.ai chat artifacts and Claude desktop/Cowork artifacts by where each runs, what produces it and what the app can observe. Anything not observed is marked unverified. No account artifact is read or published without Anton's consent.
- [x] AC-02: A completed native Artifact publish result in a thread appears in Files as one entry with title, version and local path. Its remote URL is labeled as a private claude.ai link tied to the account that published it, and it opens in the system browser, never embedded. Failed, interrupted, non-publish and malformed results produce no entry, and a non-https URL is dropped. Fixture-proven only, with no claim of live availability.
- [x] AC-03: Each Files row shows its kind and name. The folder hint is truncated in the middle and keeps the last segment. The full path appears on focus or hover and copies exactly, and the row names its source message and time. Pinned state is always visible, and pin and hide can be reached by keyboard with targets of at least 24 px. Rows work at 360 px and 1280 px wide, at 200% zoom, and in light and dark themes.
- [x] AC-04: Files distinguishes four states, each labeled, and never offers a broken open:
  - **missing**: not on disk;
  - **unreachable**: the owning machine is offline or the check failed;
  - **remote-only**: a native artifact whose local source is gone and whose remote link remains;
  - **unknown**: not yet checked.

  Opening a missing file shows an explained empty state with the last known path, not an error toast.
- [x] AC-05: Property card values wrap only at path and identifier separators (`/`, `\`, `-`, `_`, `.`, `:`), keys never wrap below their minimum width, and selecting or copying a value yields the exact original text. A single unbroken segment wider than its column, such as a long hash, may still break inside the segment as a last resort. This is checked at 360 px, 1280 px and 200% zoom.
- [x] AC-06: The file reader always shows a labeled Close, Escape closes it, and focus returns to the link that opened it. A file link opens in the focused viewer when the conversation and reader cannot both stay readable side by side (D-05). "Open beside" is available when they can.
- [x] AC-07: Files entries, pins and hides survive a reload and an app update, a provider switch in the same thread (Claude, Codex, Claude), and migration of the thread to another machine. After migration, file states re-resolve on the new machine. Tests drive each case. Pins and hides are stored on the client, so another device or browser profile starts empty; the criterion does not cover cross-device continuity.
- [x] AC-08: Delivery meets all of these:
  - focused tests pass;
  - web typecheck and production build pass;
  - headless fixture captures (light and dark, 360 px and 1280 px, 200% zoom) and interaction checks run;
  - a fresh-context review passes;
  - exact-head evidence goes to Complete screenshot sessions.

  Delivery separates source and CI proof from installed acceptance.

## Approach

Research first (T-01, Fable 5.1), in parallel with a scenario matrix and a static design proposal (T-02). Implementation is web-only and follows that order: native references (T-03), rows and states (T-04), property cards (T-05), reader dismissal (T-06), continuity (T-07). Native references reuse the generic `dynamic_tool` output the adapter already keeps (1019) and feed the existing shelf model, so the UI does not depend on the provider. If T-01 finds the Artifact tool absent or gated off for app-launched sessions, T-03 still ships, because it renders only results that actually appear. Rejected options:
- enabling the native tool by default, which invents capability;
- embedding claude.ai URLs, which needs auth and leaks across accounts;
- moving pins to the server in this increment. The server owns no shelf state today, so T-07 adds a portable key and a migration path instead.

Risks:
- The reachability check must not add a request per row; it batches the existing missing-file query.
- Width-aware opening must preserve existing editor workflows and the 1043 linked pane.

## Decisions

### Asked
- D-06 Allow one isolated, consented live publish? Anton, October 24, 2026: "YES, run it once", following the recommendations. Run at 07:28 UTC with a synthetic page, auto-open off, Artifact/Read/Edit only. It published v1, updated in place to v2 (same URL, `seq` 2), read back once, and confirmed that an unauthenticated GET serves only a generic shell. Receipt: `/Users/antonabyzov/.specwithcode/m4/evidence/1049-files-report-polish/live-publish/receipt.json`. The artifact remains in the account; the tool has no delete operation.
- D-07 Implementation binding ("work autonomously"): implement in the bound worktree as commits stacked on `12d8775f0`. Push only to the new remote branch `feat/files-artifacts-1049`, never to `feat/report-experience-1035`, and open a draft PR based on it. Retarget to `main` and rebase after #661 merges.
### Defaulted (change any before sw-do)
- D-01 Research ownership: a Fable 5.1 subagent (`claudeAgent` `claude-fable-5-1`, high effort) delegated from the bound writer thread does T-01 read-only and writes only to this increment's `reports/` folder and `/Users/antonabyzov/.specwithcode/m4/evidence/1049-files-report-polish/research/`. Implementation stays native Opus 5.5 Ultracode in the bound writer thread. If Fable 5.1 is unavailable, the task stops and reports it; there is no substitute model.
- D-02 The only live account action is the single D-06 run. App-launched sessions stay at the SDK default (`sdk_default_off`), and enabling the tool there is a later opt-in.
- D-03 Native entries are display-only references. There is no source snapshot and no account-wide import.
- D-04 This increment is web-only. It parses existing tool output and makes no adapter or server edits.
- D-05 Width rule: a file link opens in the focused viewer when the right panel would leave the conversation under 560 px or the reader under 480 px. Otherwise it opens in the right panel with a persistent Close. The rule is reversible.
### Open
- none

## Tasks

### T-01 Native artifact capability record (Fable 5.1)
- AC: AC-01 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1049-files-and-report-polish-with-claude-code-artifact-proof/reports/native-artifacts-2026-10-24.md, /Users/antonabyzov/.specwithcode/m4/evidence/1049-files-report-polish/research/ | Test: the record exists. Every capability row cites a URL or a receipt in the research folder, and the roster and replay receipts are JSON with the command that produced them.

### T-02 Scenario matrix and design proposal
- AC: AC-03, AC-04, AC-05, AC-06, AC-07 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/1049-files-report-polish/design/ | Test: the matrix lists each state and transition with its expected UI. Headless `html_preview` captures of the popover, property card and reader cover light and dark at 360 px and 1280 px.

### T-03 Native Artifact references in Files
- AC: AC-02 | Files: apps/web/src/nativeArtifacts.ts, apps/web/src/nativeArtifacts.test.ts, apps/web/src/threadArtifacts.ts, apps/web/src/artifactShelf.ts, apps/web/src/components/chat/ThreadArtifacts.tsx, apps/web/src/components/chat/useNativeArtifacts.ts | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/nativeArtifacts.test.ts apps/web/src/artifactShelf.test.ts

### T-04 Files rows and file states
- AC: AC-03, AC-04 | Files: apps/web/src/components/chat/ArtifactShelfList.tsx, apps/web/src/components/chat/ThreadArtifacts.tsx, apps/web/src/artifactShelf.ts, apps/web/src/components/chat/ArtifactShelfList.test.tsx, apps/web/src/components/chat/useMissingArtifactFiles.ts (+test), apps/web/src/components/chat/MissingFileNotice.tsx (+test) | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/ArtifactShelfList.test.tsx apps/web/src/artifactShelf.test.ts

### T-05 Path-aware property cards
- AC: AC-05 | Files: apps/web/src/components/chat/StructuredBlocks.tsx, apps/web/src/components/chat/structuredBlocks.logic.ts, apps/web/src/components/chat/structuredBlocks.logic.test.ts, apps/web/src/components/chat/StructuredBlocks.test.tsx, apps/web/src/components/find/conversationFind.logic.ts (+test: Cmd+F matches across wrap points) | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/StructuredBlocks.test.tsx apps/web/src/components/chat/structuredBlocks.logic.test.ts apps/web/src/components/studio/RoutineRunCard.test.tsx

### T-06 File reader close and width-aware opening
- AC: AC-06 | Files: apps/web/src/components/RightPanelTabs.tsx, apps/web/src/components/ui/panel-tab-close-button.tsx, apps/web/src/components/ViewerOverlayHost.tsx, apps/web/src/lib/openInFront.ts (D-05 decided where a link opens a file), apps/web/src/index.css (viewer header wraps at phone width), apps/web/src/components/ChatView.tsx (two one-line additions), apps/web/tests/report-experience/files.tsx (fixture links open through openInFront), apps/web/src/components/RightPanelTabs.test.tsx, apps/web/src/components/RightPanelTabs.keyboard.test.tsx, apps/web/src/components/ViewerOverlayRouteGuard.test.tsx, apps/web/src/lib/openInFront.placement.test.ts. Escape from a framed document is handled by the panel's message listener, so FilePreviewPanel.tsx is unchanged | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/lib/openInFront.test.ts apps/web/src/lib/openInFront.placement.test.ts apps/web/src/components/RightPanelTabs.test.tsx apps/web/src/components/RightPanelTabs.keyboard.test.tsx apps/web/src/components/ViewerOverlayRouteGuard.test.tsx

### T-07 Continuity across reloads, updates, providers and machines
- AC: AC-07 | Files: apps/web/src/components/chat/useArtifactShelfState.ts, apps/web/src/components/chat/useArtifactShelfState.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/useArtifactShelfState.test.ts

### T-08 Headless fixture and exact-head evidence
- AC: AC-08 | Files: apps/web/tests/report-experience/files-check.mjs, apps/web/tests/report-experience/files.html, apps/web/tests/report-experience/files.tsx, apps/web/tests/report-experience/stubs.ts, apps/web/tests/report-experience/vite.config.ts, /Users/antonabyzov/.specwithcode/m4/evidence/1049-files-report-polish/ | Test: node apps/web/tests/report-experience/files-check.mjs with UI_EVIDENCE_DIR set to a new directory (headless: true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never)

### T-09 Verify and close 1049
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: this spec | Test: specweave verify 1049 with the focused test command, fresh-context review subagent, then specweave complete 1049
- Delivery (October 24, 2026, PR-resolution owner, option B): 1049 lands inside #661 at `cb861f6602`, together with 1035/1043, as one squash merge. D-07's separate PR is superseded. #683 shows merged and is not replaced. T-09 and installed acceptance run after the release.
- Fresh review at `cb861f6602`: `/Users/antonabyzov/.specwithcode/m4/evidence/1049-files-report-polish/review/fresh-review-cb861f6602.md`. It found 0 high or medium code defects. Follow-ups, on a branch off main after the release:
  - L1: closing a background file tab returns focus to its old link only when focus is in the reader.
  - L2: the reader content takes focus after the file editor dismisses on Escape.
  - L3: the native row note wraps instead of truncating at 360 px.
- Accepted:
  - L4: a native row's origin line shows the remote note, and a carried row names its machine.
  - L5: latent placement edges (a second view's layout report, the 5-second click window, `aria-expanded` keeping Escape).
- Recommendation, not scheduled: repeated evidence chips in progress reports should show the outcome and remaining gate first, with a "Verification details" disclosure and an optional raw audit record. Identical targets in one report are deduplicated by scoped identity. See `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1049-files-and-report-polish-with-claude-code-artifact-proof/reports/evidence-chips-recommendation-2026-10-24.md`.
