---
title: "1320 review: reports stay in SpecWithCode"
increment: "1320-reports-stay-in-specwithcode-no-provider-artifact-links-in-replies"
reviewer: "Fresh-context subagent, Claude Sonnet 5.5, read-only"
pr: "https://github.com/anton-abyzov/specwithcode/pull/332"
verdict: "SHIP after round 2 fixes"
---

# 1320 review: reports stay in SpecWithCode

Two adversarial review rounds ran in fresh contexts on Claude Sonnet 5.5. Both were read-only and had no access to the implementing thread. The merged head `bd93aa7b1a` (squashed into main as `8d8563c120`) fixes everything either round confirmed.

## Round 1 (head `7db5ba3677`)

| # | Finding | Resolution |
|---|---|---|
| 1 | `studio_report_save` wrote with no access-mode check and used the project root, not the thread worktree | Refuses plan mode and approval-required. The project root is kept by design, because the shelf, Library and viewer read reports there (comment in `ThreadReportService.ts`). |
| 2 | The 24-bit dedupe key could call a different text "already saved" and drop provenance | A key hit compares the stored body, returns the stored title, and adds the import's provenance to the earlier save |
| 3 | The text's own `Source:`/quoted keys could spoof provenance; a leading `---` rule was mangled | Saved keys match case-insensitively and quoted. A block counts as front matter only when it has properties. |
| 4 | U+2028/2029 in a title broke the saved-thread lookup | `frontMatterValue` replaces every line break. The source refuses them, and `original` is stored as the normalized `URL.href`. |
| 5 | Concurrent saves could both succeed with different files | EEXIST re-reads and returns the same report. A true collision gets `-N-<key>.md`. |
| 6 | Loose Gemini/claude.ai patterns, unescaped Copy link label, missing tests | UUID and hex id patterns; `providerHostedDocumentMarkdown` escapes; tests added for each |

CI then showed that recorded Claude replays lacked the new `disallowedTools`. `ClaudeAdapterV2.testkit.ts` tolerates exactly that set in old recordings. A dropped `Workflow`, a partial set or an extra entry still fails.

## Round 2 (delta `7db5ba3677..01940accc6`)

The round found no blocking findings. Three low-severity items were fixed in `bd93aa7b1a`:

- `readSavedReport` reads only regular files (`lstat`), so a symlink planted under a report's name is never read or written through.
- A leading block of list items or links stays prose. It must name a property, and `key:` needs whitespace after the colon. Quoted kept keys are written bare.
- Plan mode and approval-required get separate refusals that name the project folder's reports path.

## Checks on the merged head

- PR gate green on `bd93aa7b1a`: 17 pass, 10 skipped. A `ProjectionStore.slowQueries` timing flake (50.3 ms against 50) passed on rerun.
- Focused tests: ThreadReports, handlers and ThreadReportService pass (41). RuntimeInstructions, CodexDeveloperInstructions and ClaudeWorkflowPolicy pass. Web providerHostedDocument, OutsideDocumentLink, ChatMarkdown and the designTokens guard pass (129).
- Headless chip check `scripts/studio-verify/outside-document.mjs`: 3 cases (light, dark, 390 px). Screenshots are in `reports/outside-document/`.
