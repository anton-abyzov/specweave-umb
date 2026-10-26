# 1011 Activity diffs and compact output

## Problem

Citations are `path:line` in `repositories/anton-abyzov/specweave-studio` at `252be2eb4`. origin/main has since moved to `05fa77b27` (re-checked October 23, 2026, 3:20 AM EDT). Of the cited files only `packages/contracts/src/orchestrationV2.ts` (2 lines added after line 3236), `apps/server/src/orchestration-v2/Orchestrator.ts` (changes after line 2288) and `AGENTS.md` (lines added after line 81) changed, so every cited line still matches except the get-turn-item contract, now at orchestrationV2.ts:3717-3729. The installed app is 1.0.74: `CFBundleShortVersionString` in `/Applications/SpecWithCode.app/Contents/Info.plist` read 1.0.74 on October 23, 2026 at 2:14 AM EDT, the same version as the source (apps/web/package.json:3).

- **Code changes are hard to see from the timeline.**
  - The wire and detail projections strip `diffStr`, `oldStr` and `newStr` from `file_change` items (apps/server/src/orchestration-v2/WireProjection.ts:97-105,195-197). Expanded edit rows list only the `changes[]` paths (apps/web/src/components/chat/V2ItemInspector.tsx:327-338).
  - `changes[].diffStr` does reach the client. The pending file-approval panel shows it as "Supplied patch" (packages/client-runtime/src/state/threadRequests.ts:105-118; apps/web/src/components/chat/ComposerPendingApprovalPanel.tsx:102-108). Stripping it would blank Codex approval previews.
  - Claude stores the tool's output text as `diffStr` (apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts:4262-4268).
  - Codex stores each change's `diff` verbatim (apps/server/src/orchestration-v2/Adapters/codexFileChanges.ts:24-29). Our own fixture models an update hunk as a bare `@@` with no file headers (codexFileChanges.test.ts:13); that is an assumption, not observed Codex output (`reports/rea/clean-room-spec.md` 1.7). The renderer falls back to raw text when it parses no files (apps/web/src/lib/diffRendering.ts:184-192).
  - A diff is reachable only from "Open diff" inside an expanded edit row or from the changed-files card (V2ItemInspector.tsx:314-322; apps/web/src/components/chat/ChangedFilesTree.tsx:101-132).
- **Diff links are not exact.**
  - Open diff passes the raw, often absolute `fileName` (V2ItemInspector.tsx:318). DiffPanel reveals a file only on an exact repo-relative match (apps/web/src/components/DiffPanel.tsx:551-553). The existing `resolveDiffPathForWorkspace` maps repo-relative paths to workspace-relative ones and returns null for absolute paths (apps/web/src/diffFileActions.ts:15-17,50-78).
  - A revealed file that the collapse setting collapsed stays collapsed (DiffPanel.tsx:569-610).
  - An unknown or uncheckpointed run silently shows the latest turn (DiffPanel.tsx:272-276; apps/web/src/diffPanelStore.ts:89-106).
  - Every link targets the active thread, inherited rows included (apps/web/src/components/ChatView.tsx:13977-13986; packages/contracts/src/orchestrationV2.ts:1717-1723).
  - `getTurnDiff` accepts only checkpoints of `completed` runs, on both the from side and the to side (apps/server/src/checkpointing/CheckpointDiffQuery.ts:115-124,166-183). Capture writes ready checkpoints for interrupted and cancelled runs too (apps/server/src/orchestration-v2/CheckpointCaptureService.ts:70-92), and the client lists every checkpoint (packages/client-runtime/src/state/threadCheckpoints.ts:29-51). A stopped turn, and the turn after it, show a card whose diff then fails.
  - The turn patch still contains HEAD-move files that the card drops. The excluded set is computed only at capture, by six git calls that include a live reflog read, and only the filtered `files` list is persisted (apps/server/src/orchestration-v2/CheckpointService.ts:471-490; apps/server/src/vcs/GitVcsDriver.ts:1098-1167).
  - The diff runs in the cwd of the thread's shared root scope (CheckpointDiffQuery.ts:150-158,185-188). Each run replaces that scope's payload, cwd included (apps/server/src/orchestration-v2/Orchestrator.ts:1884-1897; apps/server/src/orchestration-v2/ProjectionStore.ts:2685-2696).
  - The card counts files with whitespace changes included (CheckpointService.ts:443-452). The panel defaults to Ignore whitespace (CheckpointDiffQuery.ts:86; DiffPanel.tsx:315).
  - The patch is silently cut at 10 MB (GitVcsDriver.ts:444,1284-1313; packages/contracts/src/checkpointDiff.ts:21-27).
  - Opening a file opens the current working-tree copy, not the turn's version (diffFileActions.ts:94-95; apps/web/src/rightPanelStore.ts:146).
- **Shell edits and attribution are missing.**
  - Edits made with `sed -i`, heredocs or formatters create no edit item. They exist only in the checkpoint, which stages the whole cwd (GitVcsDriver.ts:981-997; CheckpointService.ts:443-490).
  - Locks are held per cwd (CheckpointService.ts:258-260), so other agents' edits in a shared checkout land in the turn as well (apps/server/src/checkpointing/headMoveAttribution.ts:1-9).
  - An umbrella-rooted thread never captures the child repositories that the umbrella ignores (`/Users/antonabyzov/Projects/github/specweave-umb/.gitignore:53`).
  - Items carry no cwd or machine (orchestrationV2.ts:1419-1438). Checkpoints carry no cwd, HEAD or machine (orchestrationV2.ts:1289-1302).
- **Rows are hard to read.**
  - A lone Read row shows the absolute path because `workspaceRoot` is not passed (apps/web/src/components/chat/MessagesTimeline.logic.ts:90-100).
  - A lone edit row reads "Changed 1 file" and names no path (MessagesTimeline.logic.ts:1711-1727).
  - Command titles are cut in code at 95 characters plus "…" (apps/web/src/components/chat/toolOutputPresentation.tsx:98).
  - Labels end in a CSS ellipsis inside a `select-none` line, with no tooltip and no copy (apps/web/src/components/chat/WorkLog.tsx:57-73).
  - Whether the reference rows really overflow the right edge or only end in an ellipsis is unverified.
- **Full details cannot be retrieved.**
  - Detail reads are capped at 256 KiB, append "… output truncated for transport" and take no offset (WireProjection.ts:16,34,173-186; orchestrationV2.ts:3715-3727).
  - Failed-edit error text is cut at 32 KiB (WireProjection.ts:14,102-103), and dynamic tool input is also bounded (WireProjection.ts:184). Copy therefore copies only the capped text (toolOutputPresentation.tsx:184-190).
  - SpecWithCode's own ACP and Antigravity ingestion keeps only the last 8,000 characters, and only a text marker says so (apps/server/src/provider/acp/AcpRuntimeModel.ts:623-661,861-863; apps/server/src/provider/acp/AntigravityProtocol.ts:16-17,179-183,316).
  - An open running row fetches its output once while running and once at completion (packages/client-runtime/src/work-log/itemDetail.ts:131-137). A comment says the opposite (packages/client-runtime/src/state/orchestration.ts:47).
  - Claude does not stream tool output (ClaudeAdapterV2.ts:275). Codex declares streaming (apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.ts:266), but the only code that names `outputDelta` is the logger (apps/server/src/provider/EventNdjsonLogger.ts:57-58).
  - ESC bytes render as control pictures (packages/client-runtime/src/work-log/commandLabel.ts:1386-1390). Code panels default to no wrapping (toolOutputPresentation.tsx:174).
- **Failures fade from view.**
  - Failed icons are drawn at 40% opacity (apps/web/src/components/chat/MessagesTimeline.tsx:3907).
  - The work-group header checks only its latest entry (MessagesTimeline.logic.ts:1781-1783) and puts `failed` only in its aria-label (MessagesTimeline.tsx:4620-4672).
  - "Worked for X" folds hide failed tools that come before the final message (MessagesTimeline.logic.ts:1102-1121; MessagesTimeline.tsx:2796-2824). Only the "Used N tools" row shows "N failed" (MessagesTimeline.tsx:4599-4603).
  - On the wire, `outputIndicatesFailure` means a nonzero exit or a match by the text heuristic (WireProjection.ts:86-95; packages/shared/src/toolOutput.ts:177-189). No adapter sets it.
  - Claude command items carry no `exitCode` (ClaudeAdapterV2.ts:4254-4261).
- **Installed 1.0.74 confirms it.** The headless before set (`reports/installed-before/receipt.json`, 38 PNGs, 44 of 56 checks passing) shows a 3-file edit labelled "Changed 1 file", Open diff leaving every file collapsed, group headers running past the row at 390 px, and a 340 KiB output stopping at 262,177 characters with "output truncated for transport".
- **There is little proof.**
  - Every timeline test passes a no-op `onOpenTurnDiff` (apps/web/src/components/chat/MessagesTimeline.test.tsx:406).
  - The DiffPanel test mocks file reveal and the code view (apps/web/src/components/DiffPanel.test.tsx:106,122).
  - The timeline-detail fixture uses no-op callbacks (apps/web/tests/timeline-detail/README.md:3).
  - The code-review capture recipe is fixed at 1600x1000 (`/Users/antonabyzov/Projects/github/studio-audit-evidence/code-review/capture.mjs:87`).
  - No installed-app capture covers a thread timeline.

## Scope

**In:**
- Compact row labels that always expand back to the full text, with a full-text tooltip and a Copy action on each row.
- Visible failure counts on tool groups and turn folds. Failed commands get an "exit N" chip, or "failed" when there is no exit code.
- Exact Open diff links into the existing DiffPanel:
  - each link uses the source thread, the run and an exactly relativized path;
  - the revealed file is expanded;
  - the panel never falls back to another turn;
  - each state gets its own notice;
  - interrupted and cancelled turns are diffable;
  - clicking the file title opens the existing editor.
- Inline per-edit patches in expanded edit rows, using the existing Pierre renderer. They come from provider data that is already persisted, are fetched only on expand, and are paged.
- Codex approval previews keep their supplied patch.
- Turn-level listing of files that changed without an edit item, in the existing changed-files card, labelled honestly.
- The turn patch is filtered to the persisted card files and flagged when truncated. Checkpoints are stamped with cwd, HEAD and the capturing environment, and both the diff and the editor use the stamped cwd.
- Paged detail reads for outputs, inputs and edit bodies, with Copy full and Load more. Display strips ANSI, with a Raw toggle. Ingestion truncation gets a visible notice. Open running rows refresh while they run, for providers that stream tool output.
- Unit tests and a headless fixture (1280/720/390 px, light and dark) that mounts the real DiffPanel. Installed-app before and after captures, a frontend-design pass, and an independent adversarial review before merge.

**Out:**
- A new diff viewer, route or per-command diff RPC.
- Per-command git snapshots.
- Output on live stream events.
- Rendering ANSI colors.
- Isolated worktrees for delegated workers.
- Codex `outputDelta` streaming.
- Per-repository capture scopes (O-08).
- Detection of concurrent writers (O-09).
- The mobile app.
- Deleting the unused `ShellCommandBlock.tsx`.
- Any "bug-free" claim.

**Gates:**
- **App edits wait for approval.** No app code is edited until the user adds `repositories/anton-abyzov/specweave-studio` to Project settings > approved folders. The app-bound worktree must come from `studio_thread_launch` with `workspaceStrategy: "worktree"`. No worktree is created from a shell, and the stale detached checkout stays untouched.
- **The before capture is not app code and is not gated by approval.** S-0 below runs outside the app repo and must finish before 1015 replaces 1.0.74.
- **No release from this lane.** This lane never releases, publishes, merges into a release, or restarts the app or its service. The sole release owner, increment 1015, dispatches rollout and owns CI and merge inclusion.
- **Installed proof stays separate.** Installed-app screenshots live in `reports/installed-before/` and `reports/installed-after/` of this increment, apart from the fixture PNGs in `reports/fixture/`. Each receipt records the `app` path, `bundleVersion` and `headless: true`. Source-build captures count as neither kind.
- **Safe browser runs.** Every browser run is headless with `PWDEBUG=0` and `PLAYWRIGHT_HTML_OPEN=never`, uses private scratch state, and never touches `statev2.sqlite*`.

## Acceptance Criteria

- [ ] AC-01: A lone Read or edit row shows the workspace-relative path, or the absolute path only when the file is outside the workspace. The path is middle-truncated so the file name stays visible. Hover shows the full path, and the row's Copy action copies the exact full path.
- [ ] AC-02: A command row label is not cut in code. The whole first line renders with CSS truncation, the tooltip shows it in full, and the collapsed row's Copy action copies the exact full command. Expanding the row still shows the full Command panel.
- [ ] AC-03: A lone edit row shows the changed path, "+N more" for extra files and +/- counts, instead of "Changed 1 file". While collapsed it shows Open diff, enabled or disabled by the rules in AC-05.
  - Counts come from the provider when it sends them (only Cursor today); otherwise the server computes them per file from the full patch before any wire size limit, counting `+`/`-` lines and excluding file headers. With no patch the counts are omitted, never shown as 0.
  - A test covers a Codex change over 32 KiB whose counts match the full patch.
- [ ] AC-04: Open diff behaves the same from an edit row, the inspector, the card header, each card row and each "not reported by an edit tool" row.
  - It carries that row's source thread, run and path. An inherited row navigates to its source thread with the diff open.
  - The path is relativized exactly against the checkpoint's stamped repository root (checkpoint patch paths are repository-relative, not cwd-relative), falling back to today's workspace root for old checkpoints. A test covers a thread whose cwd is a subfolder of the repository. A suffix match is used only when it is unique, and it is labelled "Matched by file name".
  - DiffPanel opens that run's turn, scrolls to the file and expands it, even when the setting collapses files.
  - Clicking the file title opens the existing editor. When the turn is the thread's latest checkpointed turn and no run is active, it opens at the first changed new-side line. Otherwise it opens the current file at the top and shows "Showing the current file; it may differ from this turn".
- [ ] AC-05: Open diff never shows another turn's diff. Each state gets its own text:
  - A running turn: the action is disabled and reads "Diff available when the turn ends".
  - A checkpoint whose status is `error`, `missing` or `stale`: "No diff: this turn's snapshot failed", "… is missing" or "… is out of date".
  - A folder that is not a Git repository: "No diff: this folder is not a Git repository". Capture stamps `notGitRepository`, and the stamp takes precedence over "… is missing", which then means an absent ref. Old checkpoints without the stamp show "… is missing".
  - An unknown run: "No diff recorded for this turn".
  - Refs that are absent on the serving machine: "This turn's snapshot was taken on <machine>".
  - Interrupted and cancelled turns that have a ready checkpoint open their diff. So does the turn after them or after a failed turn: its base is the scope snapshot one ordinal earlier, the same ref its card's file list was computed from (CheckpointService.ts:376-379). A test covers the turn after a failed run.
  - A failed turn has no snapshot (capture runs only for waiting and stopped runs, RunExecutionService.ts:520-545): "No diff: this turn ended with an error before a snapshot was taken". Its edit rows keep their provider patches. Its file changes become part of the next turn's starting snapshot (RunExecutionService.ts:697-700), so no turn diff shows them until O-11 is answered.
  - When a requested path is missing from the patch, a notice names the path and gives one reason: outside the checkpoint folder `<cwd>`; hidden by Ignore whitespace, with a one-click toggle; beyond the diff size limit; or "not in this turn's snapshot (ignored path, nested repository or reverted)". The row's inline provider patch stays available.
- [ ] AC-06: Expanding an edit row that has provider patch data fetches the patch on demand and renders it inline in the existing Pierre renderer, in light and dark.
  - Sources: Codex, ACP (every patch entry, not only the first), Cursor, OpenCode and Pi patches; Claude edits from the structured result's hunks first, then its git patch, then the tool input. Only the input fallback is labelled "Edit snippet", and the git patch fallback is labelled "Git diff of the file; may include changes this edit did not make". Every inline patch carries a "From <provider>" caption (D-04). Old Claude items whose `diffStr` holds the structured result as JSON render through the same converter; anything that still does not parse shows its stored text in the existing raw view with the reason.
  - Claude Edit inputs with an internal edits list are treated as a multi-edit; MultiEdit stays supported for old sessions. A Write update without hunks shows "No diff from the provider for this overwrite" and keeps Open diff.
  - Codex add, delete, update and move changes each render as a headed patch, with one test per kind. Update and move hunks get synthesized file headers and counted ranges, labelled "Line numbers not reported by the provider".
  - ACP keeps every patch it receives. Each v2 diff block keeps its own patch text with its own changes (today only the first block's patch, AcpAdapterV2.ts:1044-1047). A v1 diff becomes an edit row whatever its tool kind (today other kinds lose the patch, :3607-3631). A v1 patch skipped past the 1,000-edit search cap (:1027-1030) shows "Provider diff too large to compute" and keeps Open diff.
  - Above 256 KiB the patch shows "Showing X of Y" with Load more. Above 5,000 lines or 1 MiB it shows "Too large to show here" with Open diff and Copy full. Copy copies the full patch across all pages.
  - A failed edit shows the provider's full error text, paged, and it is never parsed as a patch.
- [ ] AC-07: When a turn's checkpoint lists files that no successful edit item names, the card shows them under "Changed in this folder during the turn, not reported by an edit tool (commands, other tools or other agents in this checkout)".
  - Matching uses the exact relativizer from AC-04, and failed edit items are not subtracted.
  - Each listed file opens the turn diff at that file.
  - A turn whose checkpoint lists no files shows no card and no diff action.
  - A test covers a read-only turn with a concurrent writer: the section appears with this label, and nothing claims the turn edited the file.
- [ ] AC-08: With Ignore whitespace off, the DiffPanel file list equals the card's file list, with HEAD-move-only files excluded from both. This includes interrupted turns and the turn after a failed turn. A patch cut by the server size cap shows "Diff truncated at 10 MB", and each card file missing from the patch is listed as "beyond the diff size limit". Such files have no exact per-file diff in this increment; that is an accepted limit, because this increment adds no diff RPC.
- [ ] AC-09: The DiffPanel turn header shows the turn number, repository, checkpoint folder, branch@short HEAD (no branch when HEAD is detached) and the label of the machine that captured it, when the checkpoint records them.
  - Capture stamps `cwd`, `repoRoot`, `branch`, `headOid` and the capturing environment. The diff uses the stamped checkpoint folder. The editor opens files in the thread's current workspace (rightPanelStore.ts:769-800 keeps only a relative path), so when the stamped folder differs it shows AC-04's "Showing the current file" notice naming both folders. A test covers a thread whose worktree changed between turns.
  - When the capturing machine differs from the serving machine, the header says so.
  - Checkpoints without these fields render as they do today.
- [ ] AC-10: No failure signal disappears into a fold. A tool-group header and a "Worked for X" fold show three separate counts over every contained entry, not only the latest:
  - A full-strength "N failed" for entries that failed by status, by a nonzero `exitCode` or by a provider error.
  - A faint "N possible failures" for entries flagged only by the text heuristic. They keep today's faint mark and are never added to "N failed". Today the group header counts them as failures (presentation.ts:369-397 feeding MessagesTimeline.logic.ts:2180), and a fold hides failures before the final message (MessagesTimeline.logic.ts:1102-1121).
  - A faint "N declined" for Codex items the user declined. They carry a "declined" chip. The item keeps status `cancelled` for older clients and adds the optional `declined` flag (D-28); today the adapter maps declined to cancelled (CodexAdapterV2.ts:406-411), which shows "stopped".
  - A collapsed failed command shows "exit N" when it has an exit code and "failed" when it has none.
  - Claude: Claude Code 2.1.302 returns a Bash exit its command table treats as an error as `is_error: true` with "Exit code N" on the first line (`reports/rea/claude-code.md` section 3, "Bash failure flag"). Studio already maps `is_error` to failed status (ClaudeAdapterV2.ts:2329-2332), and T-05 takes `exitCode` from that exact first line (D-29). A nonzero exit the table treats as normal (`git diff` with differences) arrives as a plain result and can only count as a possible failure. A recorded SDK result fixture pins both cases. If a CLI version omits `is_error`, the entry still gets a possible-failure count, never nothing.
  - An interrupted command shows "stopped" and is counted nowhere. Signals: the Claude Bash interrupted flag (dropped today) and a Codex stop.
  - One test per signal: each provider's failure, possible failure (including a heuristic-only "no files found"), Codex declined, and each stop signal.
- [ ] AC-11: Output, input and edit text longer than one 256 KiB page is paged. Command output opens on its last page, scrolled to the bottom ("Showing last X of Y", Load earlier); inputs, edit bodies and tool output open on the first page ("Showing X of Y", Load more). This covers command output, string and structured tool output, tool input, and edit bodies; structured values page over their compact JSON text, and image bytes stay separate assets.
  - Copy full copies the entire stored text, without the transport marker. Its SHA-256 equals the source's, including emoji and multibyte characters that sit on page boundaries.
  - Copy full on a running item restarts if the item's revision changes mid-copy.
  - The display strips ANSI sequences and offers a Raw toggle. Copy always keeps the exact bytes.
- [ ] AC-12: When SpecWithCode's ingestion cut a tool's output (ACP, Antigravity), the expanded row says "SpecWithCode kept only the last 8,000 characters of this output", or applies the O-04 outcome.
- [ ] AC-13: An open row of a running command from a provider whose `streamsToolOutput` capability is true refetches at most once every 2 seconds and at least once every 3 seconds. Refetching stops when the row closes, and the row fetches once more on completion. Codex is excluded: it declares the capability (CodexAdapterV2.ts:266) but handles no output deltas. Today this means ACP, Cursor, OpenCode and Pi. Running Claude, Codex and OpenCode2 rows (OpenCode2AdapterV2.ts:137 declares false) say "Output appears when the command ends". A fake-timer test covers this.
- [ ] AC-14: At 1280, 720 and 390 px, in light and dark:
  - no page or row scrolls sideways (code and diff panels scroll inside themselves and are exempt);
  - every row label fits its row;
  - trailing actions stay visible and keyboard-reachable;
  - each reference row renders on one line, placed at the end of its own fixture thread so that the 390 px list renders it: `sed -n 240,500p packages/core/src/chat/streaming.ts`, `Read …/SKILL.md`, `/tmp/sk-cost-arch/brief.md`, "Ran 24 commands, changed 3 files, and performed 5 other actions", and a thinking row.
- [ ] AC-15: `TimelineDetail` (Concise, Normal, Verbose) changes only density and default expansion, following the activity-by-level matrix in `reports/rea/clean-room-spec.md` section 2. In every level:
  - every edit row (in Concise, after unfolding its turn) and the turn card keep Open diff into the existing DiffPanel at the exact run and path, and the provider patch stays reachable by expanding or Copy full;
  - "N failed" appears at full strength on every fold and group header, with the faint "N possible failures" and "N declined" counts beside it (AC-10), and failed, declined and stopped rows keep their chip;
  - links carry thread, run and path, and the DiffPanel header shows the AC-09 provenance;
  - main-thread and subagent edits keep their attribution and open the existing DiffPanel, routed as AC-19 describes.
  - Concise keeps its current contract (thinking hidden, one-line card) plus the AC-10 counts and "+N not from edit tools". Normal folds as today. Verbose opens every row; multi-file rows open their first 3 file sections, and a 200-edit thread requests detail only for mounted rows.
  - A parametrized test (T-09) renders one fixture thread at each level, with the subagent's thread both loaded and not loaded, and asserts the four invariants; the DiffPanel header part is asserted in the fixture (T-12) after a click at each level, and the fixture captures each level.
- [ ] AC-16: Installed before and after sets cover the same scenario: a read-only turn, a multi-file edit, a shell edit, a failed command, large output, long paths, and Open diff clicked from an edit row and from a card row.
  - In Normal, both sets capture every scenario at 1280, 720 and 390 px in light and dark. Concise, Verbose, expanded rows and the Open diff clicks are captured at dark 1280, as the before set was (38 PNGs). T-15's receipt checker enforces this rule.
  - Before captures come from installed 1.0.74 (taken October 23, 2026, 2:48 AM EDT: `reports/installed-before/receipt.json`). The harness refuses `--phase before` unless `bundleVersion` is 1.0.74, and refuses to overwrite an existing receipt.
  - After captures come from the build that 1015 releases. The receipt names the release tag and source commit, and asserts that 1011's merge commit is an ancestor.
  - Each receipt names the app path, `bundleVersion` and `headless: true`, and is stored apart from fixture PNGs.
  - If installed output cannot exceed one page, the receipt says paging is proven by the fixture only.
- [x] AC-17: The frontend-design pass is recorded in `reports/frontend-design.md` and the pre-merge adversarial review in `reports/review-<reviewer>.md` of this increment. The review runs in a fresh context with another model family, on the branch diff. Each file lists every finding as fixed or open, and no report claims a "bug-free" result. The plan review `reports/plan-review-claude.md` is not the pre-merge review.
- [ ] AC-18: A pending Codex file-change approval still shows every supplied patch, with no "Preview unavailable" regression. A patch over 32 KiB shows the transport marker, and the full patch is available from the edit row.
- [ ] AC-19: Edit rows in a provider-native subagent's thread show Open diff. It opens the parent thread's DiffPanel at the run that launched the subagent, with the file revealed and expanded and the notice "Edited by subagent <title> in turn N"; if the subagent was still running when that checkpoint was taken, the notice says the change may appear in a later turn. An app-owned delegate's edit rows open their own thread's DiffPanel. On the parent's card, files named by a loaded subagent's edit items are listed under "Edited by subagent <title>", not under "not reported by an edit tool". When a subagent of that run is not loaded, its files stay in the not-reported section, whose label then names that run's subagents, so a file is never attributed to the turn's own edit tools. No new viewer.
- [ ] AC-20: Codex `commandActions` (read, listFiles, search, unknown) are kept on `command_execution` and checked before an item is treated as a generic command, so Codex reads, listings and searches count as such in group chips. Unknown actions stay commands, and shell text is never parsed. Tests cover the mapping only. This AC does not block the others.

## Approach

**Reference designs (REA, clean-room).** Static REA of Codex desktop 26.928.20755 (`app.asar` sha256 `2301fba4…`), Claude Code 2.1.302 and Agent SDK 0.3.276 types, plus the app's own protocol sources, is in `reports/rea/` (`codex-desktop.md`, `claude-code.md`, `protocols.md`, `clean-room-spec.md`). It informs behavior only; no code, prompts, assets or UI copy are reused. Adopted ideas, each with its evidence key in `reports/rea/clean-room-spec.md`: per-edit rows with verb, path link and +/- counts (CX-SER, CC-NF) and a collapsed inline patch of capped height (CX-SER); a per-change preview size gate with a placeholder that still opens the full diff (CX-SER, CX-CORE); turn cards that open the diff panel scoped to that turn and scrolled to the file (CX-CORE); file references shown short with the full path on hover (CX-SER, CC-JT, CC-85); exploration grouping from typed command actions (CX-CORE, CX-IFM); a condensed default with a verbose toggle that only changes expansion (CC-R2, CC-8W). Claude edit-result facts used by AC-06 (structured hunks, the internal edits list) come from SDK and CC-HQ. Not adopted: a second diff surface, hover diff previews (CX-FOCUS), and Codex's two-density setting (CX-CORE; SpecWithCode keeps its three `TimelineDetail` levels). A clean-room HTML mockup of all three levels with light/dark and 1280/420 px captures is in `reports/rea/mockup/` (design reference only, not app code and not acceptance evidence).

**Pre-step S-0 (no app edits, done October 23, 2:48 AM EDT):** take the before capture before 1015's 6:26 AM EDT trigger on October 23, 2026 (`/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/release-readiness.md:7`).
- Copy the code-review recipe into `/Users/antonabyzov/Projects/github/studio-audit-evidence/activity-diffs/` and add viewport, theme and thread-route options. The recipe is `/Users/antonabyzov/Projects/github/studio-audit-evidence/code-review/capture.mjs`; its `THEME` option is at line 86 and its fixed viewport at line 87.
- Add a standalone mock ACP `.mjs` next to the copy. Inside a scratch git repo it makes a 3-file edit, a `sed -i` edit and one failing command, and returns large output as a plain-string `rawOutput`. A string `rawOutput` is not bounded by `boundToolCallRawOutput` (AcpRuntimeModel.ts:647-650); whether it reaches storage whole is unverified.
- Point a provider at the mock through `SETTINGS_FILE` (capture.mjs:27-35).
- Write the PNGs and the receipt to this increment's `reports/installed-before/`.
- If S-0 cannot finish before the trigger, ask 1015 to hold dispatch until `reports/installed-before/receipt.json` exists.

**Files in order** (paths relative to the app repo):

1. **T-01 Contracts.** Only optional fields, so old and new clients and servers interoperate across machines.
   - `file_change.diffOmitted`, and optional `changes[].additions`/`deletions` for per-file counts (AC-03).
   - `outputKeptTailChars` on `command_execution` and `dynamic_tool`.
   - An optional typed `commandActions` on `command_execution` (AC-20; T-14 fills and reads it).
   - An optional `declined` flag on `command_execution` and `file_change` (AC-10, D-28; T-14 sets it).
   - Get-turn-item input gets `field` (output, input or body), an optional `changeIndex` that selects one `changes[]` entry's patch for `body`, `offset` and `limit`. The result gets `page {field, changeIndex?, offset, nextOffset|null, totalLength, revision}`.
   - Checkpoint gets `cwd`, `repoRoot`, `branch`, `headOid`, `capturedOnEnvironmentId` and `notGitRepository` (AC-05, AC-09, D-27).
   - `ThreadTurnDiff.truncated`.
   - A pure `sliceTextPage` in `packages/shared/src/toolOutput.ts`: UTF-16 offsets, a 256 KiB UTF-8 budget, no split surrogate pairs, and an `anchor` of start or end for tail-first command output (AC-11, D-24). The server uses it, and client tests use it as a fake server.
2. **T-02 Harness.** `scripts/studio-verify/activity-diffs-capture.mjs` for the after set and for reproducibility. It has a phase guard and a merge-ancestry check. The mock-agent mode lives in `apps/server/scripts/acp-mock-agent.ts`, wired like `scripts/studio-verify/lifecycle-controls.mjs:383-396`.
3. **T-03 Server detail.**
   - `projectTurnItemForDetail` pages every bounded field with `sliceTextPage`. For `file_change` it returns the edit bodies (`diffStr`, `oldStr`, `newStr`, `changes[].diffStr`) instead of delegating to the wire projection, which strips them today (WireProjection.ts:195-197).
   - The timeline wire keeps `changes[].diffStr`, each bounded with `truncateDetail`, and sets `diffOmitted` when it bounds or strips one. Before bounding, it computes per-file +/- counts from the full patch when the provider sent none (AC-03, D-23).
   - `ThreadManagementService.getTurnItem` forwards `field`, `offset` and `limit`; ws.ts already passes the whole input (apps/server/src/ws.ts:1980-1990).
4. **T-04 Turn diff.**
   - `getTurnDiff` accepts ready checkpoints of completed, interrupted and cancelled runs.
   - When no ready run checkpoint has `appRunOrdinal` N-1, it takes the from ref by scope ordinal (`checkpointRefForScopeOrdinal` for the to checkpoint's scope at `ordinalWithinScope - 1`), as the `fromTurnCount === 0` path already does (CheckpointDiffQuery.ts:163-172), after checking the ref exists. That is the ref the card's files were computed from (CheckpointService.ts:376-379), so the turn after a failed run is diffable and AC-08 equality holds (AC-05).
   - It diffs in `checkpoint.cwd` when stamped, falling back to the scope cwd.
   - It keeps only the `diff --git` blocks whose paths are in the persisted `checkpoint.files`, and never recomputes `headMovePaths` at read time.
   - It reports truncation through an optional `diffCheckpointsReport` on VcsDriver and CheckpointStore, following the optional `headMovePaths` (apps/server/src/checkpointing/CheckpointStore.ts:95-99), so existing fakes keep compiling (CheckpointScopeOwnership.test.ts:221-227).
   - Capture stamps `notGitRepository` on the non-Git branch (CheckpointService.ts:381-393), and `scope.cwd`, `repoRoot`, `branch` (D-27), the HEAD from the `head=` trailer (headMoveAttribution.ts:11-23) and `ServerEnvironmentIdentity` (apps/server/src/environment/ServerEnvironment.ts:56-61). Checkpoints persist as `payload_json` (ProjectionStore.ts:2700-2728), so no migration is needed.
5. **T-05 Claude.** A pure converter `packages/shared/src/structuredPatch.ts` turns the structured result's hunks into a headed patch; the adapter renders from hunks, then the git patch, then tool input (`old_string`/`new_string` to `oldStr`/`newStr`, an internal edits list or old MultiEdit `edits[]` to one snippet patch, Write `content` to `newStr`). Failure text stays in `diffStr`. The Bash interrupted flag maps to a stopped status. An `is_error` Bash result whose first line is exactly `Exit code N` sets `exitCode` N (D-29); a recorded SDK result fixture covers an error exit, a non-error nonzero exit and an interrupt.
6. **T-06 Other providers.**
   - Codex add, delete, update and move become headed patches with counted ranges.
   - ACP keeps each v2 diff block's patch with that block's changes, not only the first block's patch; turns a v1 diff into `file_change` whatever its tool kind; and marks a v1 patch skipped past the 1,000-edit cap so the row can say so (AC-06).
   - ACP and Antigravity set `outputKeptTailChars` when they bound output.
7. **T-07 client-runtime.**
   - `repoRelativePath` (exact relativization, unique-suffix fallback) in `presentation.ts`.
   - `filesChangedOutsideEditItems` built on it, taking loaded subagent edit sets so their files list under the subagent (AC-19).
   - A resolver from a provider-native subagent's thread to its parent thread and launching run (`OrchestrationV2Subagent.runId`, AC-19).
   - Three counts in `summarizeToolGroup` (AC-10): failed (failed status, nonzero `exitCode` or a provider error), possible failures (`outputIndicatesFailure` or the text heuristic with neither of the first two) and declined (the `declined` flag). Possible failures need no new contract field.
   - A detail fetch for `diffOmitted`.
   - A 2-second refetch for streaming providers.
   - A page loop for Copy full that restarts when the revision changes.
   - The new checkpoint fields in `threadCheckpoints`.
   - The stale comment fixed.
8. **T-08 Diff links.**
   - ChatView's `onOpenTurnDiff` accepts an optional third argument `{ sourceThreadId, attributedTo }`; `attributedTo` carries the subagent title for the AC-19 notice. The wider function stays assignable to the old type, so T-09 to T-11 adopt it separately.
   - `selectTurn` from a link records `origin: "link"`, so the panel never falls back to another turn; the persisted store defaults the field.
   - The panel expands the revealed file, shows the notices from AC-05, AC-08 and AC-09, and opens the editor through `rightPanelStore.openFile(ref, path, line)` (rightPanelStore.ts:146) under the AC-04 line rule, with the two-folder notice when the stamped folder differs from the current workspace (AC-09).
9. **T-09 Rows.**
   - Pass `workspaceRoot` to lone-row labels, and show the path on lone edit rows.
   - Use `MiddleTruncate` (apps/web/src/components/ui/middle-truncate.tsx), a `title` tooltip, and trailing Copy and Open diff buttons that use `stopRowToggle`.
   - Add the three AC-10 counts to group headers and folds, and the exit, failed, declined and stopped chips.
   - Update `isRowUnchanged` for every new row field.
   - Pass the source thread, the shell-edit set and, on a provider-native subagent's rows, the parent thread and launching run (AC-19).
   - Add `MessagesTimeline.activityDiffs.test.tsx`, the AC-15 test that renders one thread at each level.
10. **T-10 Expanded body.**
    - Remove the 95-character slice.
    - `ToolCodePanel` gets paging, Copy full and a Raw toggle backed by `terminalOutputPlainText` (apps/web/src/components/chat/shellCodeBlocks.ts:152-174).
    - `V2ItemInspector` renders inline patches through `getRenderablePatch` inside `DiffWorkerPoolProvider` with `StyledDiffCodeView`, following MessagesTimeline.tsx:5350-5405. The lint rule bans importing `CodeView` directly (vite.config.ts:17-20).
    - `V2ItemInspector` shows Open diff on a subagent row whose `runId` is null (V2ItemInspector.tsx:314), routed to the parent run (AC-19).
    - Add regression tests for the approval preview.
11. **T-11 Card.** The not-reported-by-an-edit-tool section with per-file links, the AC-19 "Edited by subagent" section, and the count in Concise.
12. **T-12 Fixture.**
    - Clone `apps/web/tests/timeline-detail`.
    - Add a page that mounts the real DiffPanel with a canned turn patch through `resolveId` mocks (apps/web/tests/run-on-machines/vite.config.ts:6-28).
    - Clicks record their exact arguments in `window.__diffOpens`. The DiffPanel page asserts that the target file is expanded, scrolled into view, and opened at line N.
    - A subagent thread (AC-19) and a `?detail=concise|normal|verbose` switch, so each level is captured and its DiffPanel header checked after a click (AC-15).
    - Copy is checked against the source SHA-256.
    - The frontend-design pass writes `reports/frontend-design.md`; its findings reopen T-09 or T-10.
13. **T-13 Pre-merge gate.**
    - `scripts/studio-verify/activity-diffs-verify.sh` runs every focused test from T-01 to T-14, the web build (`apps/web`: `node ../../node_modules/vite-plus/bin/vp build`), the server build (`node apps/server/scripts/cli.ts build`) and `typecheck-gate.sh --package` for apps/server, apps/web, packages/contracts, packages/client-runtime and packages/shared. These are the app's required checks (AGENTS.md:26,74-77).
    - Run the cross-family `specweave review 1011 --base origin/main` from the app worktree before handoff to 1015, and record the resolved base commit as `BRANCH_BASE` for T-15.
    - Write `docs/studio/activity-diffs.md` (AGENTS.md:47).
14. **T-14 Codex exploration actions and declined flag (AC-10, AC-20).** `CodexAdapterV2` copies `commandActions` into the item, and keeps status `cancelled` for a declined item while setting `declined` (CodexAdapterV2.ts:406-411); `classifyToolActivity` checks the actions first. The declined flag ships with the rest because AC-10 needs it. If the `commandActions` part slips, it is left out and AC-20 stays open.
15. **T-15 Verify and close.** Starts after 1015 has released a build containing the merge and the user has accepted it in the installed app (AGENTS.md:47).
    - Run the after capture.
    - Run the receipt checker.
    - Run `specweave verify 1011 --cmd` with the T-13 script. The umbrella's default commands do not touch the app (`/Users/antonabyzov/Projects/github/specweave-umb/.specweave/config.json:32-39`; `--cmd` is at `repositories/anton-abyzov/specweave/bin/specweave.js:184`).
    - Run a fresh-context `specweave review` with an explicit `--base` (bin/specweave.js:198), then `specweave complete`.

**Key decisions:** D-04 to D-29 below.

**Rejected alternatives:**
- A new per-edit viewer. The user requires reuse of the existing viewer.
- Per-command git snapshots. They cost a git call per command and still mix in concurrent agents.
- Output on live events. It would hit the 8 MiB/1,000-item stream budget (apps/server/src/orchestration-v2/LiveStreamBudget.ts:17-18).
- Recomputing `headMovePaths` at read time. Reflog drift breaks the card/panel equality.
- A longest-suffix path match. It reveals the wrong `package.json` or `index.ts` in monorepos.
- Stripping `changes[].diffStr` from the wire. It breaks approval previews.
- A new `failureSource` contract field. The signal can be derived from status, `exitCode` and `outputIndicatesFailure`, which are already on the wire.
- Changing the `diffCheckpoints` return type. It breaks every CheckpointStore fake.
- Falling back to the Uncommitted view for running turns. It mixes in unrelated changes.
- Cutting labels in code. That truncation cannot be undone.

**Risks:**
- **MessagesTimeline.tsx has a render-cost test.** Row fields that `isRowUnchanged` does not compare drop streaming updates (MessagesTimeline.logic.ts:2385+). Verbose inverts disclosure, so new disclosures must use `isDisclosed` (MessagesTimeline.logic.ts:749-760).
- **WorkLogRow forbids `className` and `style`** (WorkLog.tsx:88), so new actions go in `trailing`.
- **The pagePopups registry from PR #598 is not on main**; `git grep pagePopups` finds nothing. This increment adds no controlled popup and never closes and unmounts a controlled Base UI popup in one commit.
- **Old Claude items keep JSON in `diffStr`.** They render inline only when `getRenderablePatch` yields files; otherwise they get the link only.
- **Each detail page re-reads and decodes the whole `payload_json`** (ProjectionStore.ts:4927-4937).
- **Shared checkouts still pull other agents' edits into a turn.** The AC-07 label says so, but nothing detects it.
- **The head-move filter keeps every file when a git listing truncates** (GitVcsDriver.ts:1157-1159).
- **Very large turns still parse the whole patch on the client** (DiffPanel.tsx:426-446).
- **The `ServerEnvironmentIdentity` provision at apps/server/src/orchestration-v2/runtimeLayer.ts:147-149 is unverified.**

## Decisions

### Asked
- D-01: Reuse the existing diff viewer and editor, with no new viewer → yes (user).
- D-02: Rollout goes only through the sole release owner, increment 1015 → yes (user).
- D-03: Installed-app proof stays distinct from fixtures; a frontend-design pass and an adversarial review are required; no "bug-free" claim → yes (user).

### Defaulted (change any before sw-do)
- D-04: The whole-turn checkpoint diff is the source of truth. Provider patches appear inline, labelled as reported by the provider.
- D-06: Diffs are available for ready checkpoints of completed, interrupted and cancelled runs, and for the turn after a failed run through the scope snapshot one ordinal earlier. Every other state shows its own notice (AC-05).
- D-07: Paths are relativized exactly against the repository root of the checkpoint folder. A suffix match is used only when unique, and it is labelled. Failed edits are never subtracted.
- D-08: Inherited rows navigate to their source thread with its diff open.
- D-09: Concise keeps hiding thinking. Failure counts, Open diff and the shell-edit count stay visible at every level.
- D-10: "N failed" comes from failed status, a nonzero `exitCode` or a provider error, derived on the client. Heuristic-only matches stay faint and get their own faint "N possible failures" count; declined items get "N declined".
- D-11: Pages use UTF-16 offsets with a 256 KiB UTF-8 budget. The panel shows one page: command output its last page with Load earlier (D-24), other text its first page with Load more. Copy full fetches every page at a single revision.
- D-13: Live refresh is a 2-second refetch of open rows, only for providers that stream tool output.
- D-14: Displayed output is ANSI-stripped, with a Raw toggle. Copy keeps the exact bytes.
- D-15: Claude inline patches follow D-22's order, and only the input fallback is labelled "Edit snippet". Codex hunks get synthesized headers and counted ranges.
- D-16: The turn patch is filtered to the persisted `checkpoint.files`. Ignore whitespace stays a client setting, and a notice appears when it hides a requested file.
- D-17: The before capture is S-0, taken outside the app repo now. The in-repo harness produces the after set. Both use a mock ACP agent in a private scratch repo, with no provider spend.
- D-18: The approval preview keeps `changes[].diffStr` on the wire, bounded to 32 KiB per change, and the full patch is available from the row.
- D-19: The diff uses the stamped `checkpoint.cwd`, falling back to the scope cwd. The editor uses the current workspace and says so when the folders differ, because file surfaces keep only a relative path.
- D-20: The editor jumps to a line only for the thread's latest checkpointed turn while no run is active.
- D-21: Diff truncation is reported through an optional `diffCheckpointsReport` method.
- D-22: Claude patch source order: structured hunks, then the result's git patch (labelled fallback, it may include changes the edit did not make), then the input snippet.
- D-23: The server computes +/- counts from the full patch before the wire size limit.
- D-24: Command output opens at its end; other text opens at its start.
- D-25: Subagent edits open the parent run's diff; app-owned delegates open their own thread's diff.
- D-26: Inline patches stop at 5,000 lines or 1 MiB with a placeholder that keeps Open diff and Copy full; Verbose opens the first 3 file sections.
- D-27: Capture stamps `repoRoot` and `branch` (one extra `git symbolic-ref --quiet --short HEAD`, plus `rev-parse --show-toplevel` if capture does not already resolve it).
- D-28: Codex declined is an optional `declined` flag on an item whose status stays `cancelled`, not a new status literal, because older clients decode statuses with a closed literal list (orchestrationV2.ts:1325-1334) and would reject one.
- D-29: A Claude command's exit code is read only from an `is_error` Bash result whose first line is exactly `Exit code N`, the format Claude Code 2.1.302 writes. Anything else leaves `exitCode` unset and the chip says "failed".

### Open
- O-01 (user action): Add the app folder in Project settings > approved folders. Then the bound worktree is created through `studio_thread_launch` with `workspaceStrategy: "worktree"`. Every app edit waits for this, and no shell-created worktree is used.
- O-02 (coordination, resolved): S-0 finished at 2:48 AM EDT on October 23, 2026, before 1015's 6:26 AM EDT trigger; `reports/installed-before/receipt.json` records bundleVersion 1.0.74. Had 1.0.74 been replaced first, AC-16's before set would have been reported as missing, never substituted with source-build captures.
- O-03 (was D-05): How are shell edits attributed? (a) Turn-level only, as the AC-07 label says. (b) Also per command, from Codex `commandActions`. Recommendation: (a). REA showed (b) cannot use Codex `commandActions`: its kinds are read, listFiles, search and unknown, and none describes a write (`reports/rea/protocols.md`, schema.gen.ts:21026-21066). The only per-command edit source found is an internal Claude Bash edit diff the public SDK type omits (`reports/rea/clean-room-spec.md`, CC-HQ fo 225611182); a follow-up may read it if it appears at runtime.
- O-04 (was D-12): How should the 8,000-character ingestion cap work? (a) Keep it and flag it (AC-12). (b) Keep bounding intermediate `tool_call_update`s, but store the completed update's full text up to a stated budget. Recommendation: (b), because the user asked that nothing be truncated irreversibly. Until answered, T-06 implements (a).
- O-05: May one paid Claude turn in a scratch repo be used for installed proof of Claude edit rows? Default: no. Claude behaviour is then proven by unit tests and the fixture.
- O-06 (partly answered): Can the installed server spawn the mock agent? Yes: S-0 ran `activity-mock-agent.mjs` through the grok driver from installed 1.0.74, and the expanded 340 KiB plain-string `rawOutput` showed 262,177 characters before the transport marker, so more than one 256 KiB page reached storage (`reports/installed-before/receipt.json`). Whether all 340 KiB is stored is still unverified.
- O-07: Do checkpoint refs travel when a thread moves between machines? Unverified. The default is the AC-05 "taken on <machine>" notice.
- O-08: Should umbrella-rooted threads get per-repository capture scopes? The scope kinds already exist (orchestrationV2.ts:797). Default: notice only in this increment.
- O-09: Should a concurrent writer in a shared checkout be detected? Default: the honest label only, because nothing records other runs per cwd (CheckpointService.ts:258-260 is an in-memory lock).
- O-10: Rollout timing belongs to 1015. This lane never releases, publishes or restarts, and T-15 waits for 1015's release and the user's installed acceptance.
- O-11: Should failed runs get a checkpoint too? Today capture runs only for waiting and stopped runs (RunExecutionService.ts:520-545, CheckpointCaptureService.ts:71-104), so a failed turn's file changes appear in no turn diff. Recommendation: capture them like stopped runs. That touches `RunExecutionService.ts`, which no task owns, and the rollback and recovery paths, which were not traced. Default: AC-05's failed-turn notice only.

### Implementation notes (October 24, 2026)
- N-01 (T-01): file-change items and `OrchestrationV2FileChangeDetail` carry an optional `diffNote` string, so a patch's label ("Edit snippet", git patch fallback, synthesized line numbers, too large, overwrite without diff) survives the wire. Known values are in `FILE_CHANGE_DIFF_NOTES`. Unknown values decode and are ignored, following D-28.
- N-02 (T-01, T-03): the `getTurnItem` input also takes `before` (it wins over `offset`) and `anchor: "start" | "end"`, so D-24's open-at-end and Load earlier need no length probe. A read with no field returns `truncated[]`, which lists every field cut to its first page, all at one revision.
- N-03 (T-03): a cut `oldStr` or `newStr` (an OpenCode, Pi or Cursor body over 256 KiB) keeps the transport marker but cannot be paged, because the field enum has no name for it. This is an accepted limit; the turn diff stays the source of truth (D-04).
- N-04 (T-05): the `./structuredPatch` subpath export in `packages/shared/package.json` belongs to T-05. The Claude input snippet is turned into a headed patch on the server and stored as `diffStr` with `diffNote: "input_snippet"`.
- N-05 (T-05): a cancelled Claude edit shows the snippet it proposed (input fallback, labelled "Edit snippet"); only a failed edit keeps the provider's text. A Bash result arrives with `is_error: true` as well as `interrupted: true` when interrupted, so the interrupt check runs first.
- N-06 (T-04, T-16): the stamp comes from an optional `captureCheckpointReport` on VcsDriver and CheckpointStore (one `symbolic-ref` and one `rev-parse --show-toplevel --show-prefix`, on run captures only). The checkpoint context that `getTurnDiff` reads did not carry `files`, `cwd` or `ordinalWithinScope`, so T-16 adds them in `ProjectionStore.ts`, a file no task owned. A file list in an unexpected shape is left out, never read as empty. Only single-turn diffs are filtered; multi-turn and full-thread ranges keep the whole patch, because `files` describes one turn.
- N-08 (T-09): the T-09 Test runs from `apps/web`, as CI does. The root vitest config does not apply the React Compiler, so `MessagesTimeline.renderCost.test.tsx` fails from the root even on unchanged files ("expected 60 to be +0").
- N-09 (T-09, T-08): ChatView reads the parent projection only for a provider-native subagent thread (`isProviderNativeSubagentThread`), so app-owned delegates never load their coordinator. It passes no `loadedSubagentEditItems`: subscribing to every child thread's projection to fill the parent card would add a stream per subagent. On the live parent card, subagent files therefore stay in the not-reported section, whose label names the run's subagents (AC-19's not-loaded rule); the "Edited by subagent" section appears when a caller supplies loaded items (tests and the fixture). Open follow-up: read already-loaded child projections without subscribing.
- N-10 (review fix 4): row Copy of commands and paths keeps the exact bytes through a new optional `preserveBytes` option on `apps/web/src/hooks/useCopyToClipboard.ts`. That file is outside every task's Files. The option is off by default, so other callers keep the message-copy cleanup. Main added the identical option in #661, and the merge of origin/main (`ba567f62c1`) keeps main's copy of the file.
- N-11 (T-13): `specweave review 1011` builds its diff from the umbrella checkout `repositories/anton-abyzov/specweave-studio`, not from this worktree, so it cannot review `feat/activity-diffs-1011`. The cross-family review ran through `delegate_task` against the worktree and is recorded in `reports/review-codex.md`. T-13 is recorded with the gate run, and the review record is its evidence. `specweave task done --run` stops a command at 20 minutes, and the gate takes about 22, so T-13 is recorded with `--evidence` from a full passing gate run on the merged head. Its logs are in `reports/gate-<sha>/`.
- N-12 (T-12 design pass O-01): `apps/web/src/session-logic.ts` (outside every task's Files) maps a declined `cancelled` item to the existing `declined` lifecycle status, so its row says "Declined" beside its chip instead of "Stopped". The failure counts were already keyed on the flag, so they do not change.
- N-07 (T-06, T-14, T-16): ACP v1 diffs each become their own `changes[]` entry. Codex `listFiles` actions classify as search, like an `ls` tool. Headed Codex patches changed the expectations in `CodexAdapterV2.fileChanges.test.ts`, and the client grouped every command as "command" before the search check, so T-16 fixes both.

## Tasks

### T-01 Contract fields and shared text paging
- AC: AC-03, AC-04, AC-06, AC-09, AC-11, AC-12, AC-20 | Files: repositories/anton-abyzov/specweave-studio/packages/contracts/src/orchestrationV2.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/orchestrationV2.test.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/checkpointDiff.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/checkpointDiff.test.ts, repositories/anton-abyzov/specweave-studio/packages/shared/src/toolOutput.ts, repositories/anton-abyzov/specweave-studio/packages/shared/src/toolOutput.test.ts | Test: (cd packages/contracts && node ../../node_modules/vite-plus/bin/vp test run --config ../../vite.config.ts --dir . src/orchestrationV2.test.ts src/checkpointDiff.test.ts) && (cd packages/shared && node ../../node_modules/vite-plus/bin/vp test run --config ../../vite.config.ts --dir . src/toolOutput.test.ts)

### T-02 Installed-app capture harness with phase and ancestry guards
- AC: AC-16 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-verify/activity-diffs-capture.mjs, repositories/anton-abyzov/specweave-studio/scripts/studio-verify/activity-diffs-capture.test.mjs, repositories/anton-abyzov/specweave-studio/apps/server/scripts/acp-mock-agent.ts | Test: node --test scripts/studio-verify/activity-diffs-capture.test.mjs

### T-03 Paged detail reads, bounded wire patches, approval previews kept
- AC: AC-03, AC-06, AC-11, AC-18 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/WireProjection.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/WireProjection.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/ThreadManagementService.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/ThreadManagementService.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/WireProjection.test.ts apps/server/src/orchestration-v2/ThreadManagementService.test.ts

### T-04 Turn diff for stopped runs, filtered to card files, truncation flag, cwd/HEAD/machine stamp
- AC: AC-04, AC-05, AC-08, AC-09 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/checkpointing/CheckpointDiffQuery.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/checkpointing/CheckpointDiffQuery.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/checkpointing/CheckpointStore.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/checkpointing/CheckpointStore.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/vcs/GitVcsDriver.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/vcs/GitVcsDriver.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/vcs/VcsDriver.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/CheckpointService.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/CheckpointService.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/CheckpointCaptureService.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/CheckpointCaptureService.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/runtimeLayer.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/checkpointing/CheckpointDiffQuery.test.ts apps/server/src/checkpointing/CheckpointStore.test.ts apps/server/src/vcs/GitVcsDriver.test.ts apps/server/src/orchestration-v2/CheckpointService.test.ts apps/server/src/orchestration-v2/CheckpointCaptureService.test.ts apps/server/src/orchestration-v2/CheckpointScopeOwnership.test.ts apps/server/src/checkpointing/headMoveAttribution.test.ts

### T-05 Claude edit bodies from structured results, stopped flag
- AC: AC-06, AC-10 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts, repositories/anton-abyzov/specweave-studio/packages/shared/src/structuredPatch.ts, repositories/anton-abyzov/specweave-studio/packages/shared/src/structuredPatch.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts && (cd packages/shared && node ../../node_modules/vite-plus/bin/vp test run --config ../../vite.config.ts --dir . src/structuredPatch.test.ts)

### T-06 Headed Codex patches, all ACP patch entries, ingestion-cut flags
- AC: AC-06, AC-12 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/Adapters/codexFileChanges.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/Adapters/codexFileChanges.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/provider/acp/AcpRuntimeModel.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/provider/acp/AcpRuntimeModel.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/provider/acp/AntigravityProtocol.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/provider/acp/AntigravityProtocol.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/Adapters/codexFileChanges.test.ts apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.test.ts apps/server/src/provider/acp/AcpRuntimeModel.test.ts apps/server/src/provider/acp/AntigravityProtocol.test.ts

### T-07 Client runtime: exact relativizer, failure counts, shell-edit set, paging loop, live refresh, checkpoint fields
- AC: AC-03, AC-04, AC-07, AC-09, AC-10, AC-11, AC-13, AC-18, AC-19 | Files: repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/work-log/presentation.ts, repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/work-log/presentation.test.ts, repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/work-log/itemDetail.ts, repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/work-log/itemDetail.test.ts, repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/state/threadCheckpoints.ts, repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/state/threadCheckpoints.test.ts, repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/state/orchestration.ts, repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/state/threadRequests.test.ts | Test: (cd packages/client-runtime && node ../../node_modules/vite-plus/bin/vp test run src/work-log/presentation.test.ts src/work-log/itemDetail.test.ts src/state/threadCheckpoints.test.ts src/state/threadRequests.test.ts)

### T-08 Exact diff links, state notices and attribution header in the existing DiffPanel
- AC: AC-04, AC-05, AC-08, AC-09, AC-19 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/ChatView.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/diffPanelStore.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/diffPanelStore.test.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/diffFileActions.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/diffFileActions.test.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/DiffPanel.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/DiffPanel.test.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/diffPanelStore.test.ts apps/web/src/diffFileActions.test.ts apps/web/src/components/DiffPanel.test.tsx

### T-09 Compact timeline rows, source-thread links and visible failures
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-10, AC-15, AC-19 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/MessagesTimeline.logic.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/MessagesTimeline.logic.test.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/MessagesTimeline.toolActivity.test.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/MessagesTimeline.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/MessagesTimeline.renderCost.test.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/MessagesTimeline.test.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/MessagesTimeline.activityDiffs.test.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/WorkLog.tsx | Test: cd apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/chat/MessagesTimeline.logic.test.ts src/components/chat/MessagesTimeline.toolActivity.test.ts src/components/chat/MessagesTimeline.renderCost.test.tsx src/components/chat/MessagesTimeline.activityDiffs.test.tsx src/components/chat/MessagesTimeline.test.tsx

### T-10 Expanded output, full copy, inline edit patches and approval-preview regression
- AC: AC-02, AC-04, AC-06, AC-11, AC-12, AC-13, AC-18, AC-19 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/toolOutputPresentation.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/toolOutputPresentation.test.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/V2ItemInspector.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/V2ItemInspector.test.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/state/queries.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/ComposerPendingApprovalPanel.test.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/toolOutputPresentation.test.tsx apps/web/src/components/chat/V2ItemInspector.test.tsx apps/web/src/components/chat/ComposerPendingApprovalPanel.test.tsx

### T-11 Changed-files card: not-reported-by-an-edit-tool section and per-file links
- AC: AC-04, AC-07, AC-15, AC-19 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/ChangedFilesTree.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/ChangedFilesTree.test.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/ChangedFilesTree.test.tsx

### T-12 Activity fixture with real DiffPanel, layout checks and frontend-design pass
- AC: AC-04, AC-14, AC-15, AC-17, AC-19 | Files: repositories/anton-abyzov/specweave-studio/apps/web/tests/activity-diffs/index.html, repositories/anton-abyzov/specweave-studio/apps/web/tests/activity-diffs/fixture.css, repositories/anton-abyzov/specweave-studio/apps/web/tests/activity-diffs/main.tsx, repositories/anton-abyzov/specweave-studio/apps/web/tests/activity-diffs/mocks.tsx, repositories/anton-abyzov/specweave-studio/apps/web/tests/activity-diffs/vite.config.ts, repositories/anton-abyzov/specweave-studio/apps/web/tests/activity-diffs/verify.mjs, repositories/anton-abyzov/specweave-studio/apps/web/tests/activity-diffs/README.md, repositories/anton-abyzov/specweave-studio/AGENTS.md | Test: node node_modules/vite-plus/bin/vp build --config apps/web/tests/activity-diffs/vite.config.ts && PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never STUDIO_PLAYWRIGHT_MODULE="$PWD/apps/server/node_modules/playwright-core/index.mjs" node apps/web/tests/activity-diffs/verify.mjs "$HOME/Projects/github/specweave-umb/.specweave/increments/1011-activity-diffs-and-compact-output/reports/fixture"

### T-13 Pre-merge gate: focused tests, builds, typecheck, cross-family review, docs
- AC: AC-17 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-verify/activity-diffs-verify.sh, repositories/anton-abyzov/specweave-studio/docs/studio/activity-diffs.md | Test: bash scripts/studio-verify/activity-diffs-verify.sh && specweave --workspace ~/Projects/github/specweave-umb review 1011 --base origin/main

### T-14 Codex exploration actions and declined flag
- AC: AC-10, AC-20 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.test.ts, repositories/anton-abyzov/specweave-studio/packages/shared/src/toolActivity.ts, repositories/anton-abyzov/specweave-studio/packages/shared/src/toolActivity.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.test.ts && (cd packages/shared && node ../../node_modules/vite-plus/bin/vp test run --config ../../vite.config.ts --dir . src/toolActivity.test.ts)

### T-16 Ripple fixes: checkpoint context fields, Codex file-change test, command-action grouping
- AC: AC-04, AC-08, AC-09, AC-20 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/ProjectionStore.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/ProjectionStore.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.fileChanges.test.ts, repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/work-log/presentation.ts, repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/work-log/presentation.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/ProjectionStore.test.ts apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.fileChanges.test.ts apps/server/src/checkpointing/CheckpointDiffQuery.test.ts && (cd packages/client-runtime && node ../../node_modules/vite-plus/bin/vp test run src/work-log/presentation.test.ts)

### T-15 Verify and close 1011
- AC: AC-16, AC-17 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-verify/activity-diffs-acceptance.mjs, repositories/anton-abyzov/specweave-studio/scripts/studio-verify/activity-diffs-acceptance.test.mjs | Test: node --test scripts/studio-verify/activity-diffs-acceptance.test.mjs && PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never node scripts/studio-verify/activity-diffs-capture.mjs --phase after --expect-commit "$MERGE_SHA" "$HOME/Projects/github/specweave-umb/.specweave/increments/1011-activity-diffs-and-compact-output/reports/installed-after" && node scripts/studio-verify/activity-diffs-acceptance.mjs "$HOME/Projects/github/specweave-umb/.specweave/increments/1011-activity-diffs-and-compact-output/reports" && specweave --workspace ~/Projects/github/specweave-umb verify 1011 --cmd "bash $PWD/scripts/studio-verify/activity-diffs-verify.sh" && specweave --workspace ~/Projects/github/specweave-umb review 1011 --base "$BRANCH_BASE" && specweave --workspace ~/Projects/github/specweave-umb complete 1011 (runs only after 1015 has released a build containing MERGE_SHA and the user has accepted it in the installed app; BRANCH_BASE is the base commit recorded in T-13; T-13 runs T-14's tests too)
