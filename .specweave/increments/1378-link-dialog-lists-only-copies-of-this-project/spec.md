# 1378 Link dialog lists only copies of this project

## Problem

Anton, November 17, 2026, EasyChamp on m4: "Link with a project on another machine" lists every project on every machine under "Other copy" (ai-comparison, firstproject, fortnite-3js, ol, sketchmate_project, specos, specweave…). Only "EasyChamp on m1" and "EasyChamp on m3" are copies ("Same root repository; 34 of 38 repositories match"). Screenshot: `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-5ecbdca7-2c9d-47fe-b3e5-8326aab9c5a2.png`.

The subtitle still says "One coordinator stays; the other copy runs workers.", the model increment 1372 replaced ("One main, switch any time", project memory `decision_copy_to_another_machine_flow.md`). Nothing is pre-selected unless a caller names a copy, so the person hunts for the right row.

Facts checked on origin/main `b74f6e8e34` (`repositories/anton-abyzov/specwithcode`):

- The list is `linkCandidates` ranked by `rankCandidates` (`apps/web/src/studio/projectLink.ts`), rendered in `apps/web/src/components/studio/ProjectLinkDialog.tsx`. Every code project on another machine is a candidate.
- "Same root repository" is `rootMatches` from `fingerprintSummary`. It is `true`, `false` or `null`. It stays `null` for a machine that is not ready, for a project the cheap first pass (`looksLikeSameProject`) never fingerprints, while folders are read, and for everything when this project's own fingerprint fails.
- `LinkCandidate` carries `score`, not the matching repository count (`compareFingerprints(...).shared`).
- The copy dialog names Main through `copyRoles` (`apps/web/src/studio/projectDomain.ts`) with the retired machine records (`useRetiredMachineRecords`). For a project that is not linked, the link review picks the side that keeps the coordinator ("Coordinator stays on", `defaultKeptSide`), so no Main is known on the first step.

## Scope

In:

- The dialog's first step: which rows show, the "Other projects" disclosure, the empty message, pre-selection and the subtitle.
- Translations of the first step's own strings in all 8 catalogs.
- Unit tests and a headless capture, light and dark.

Out:

- The review step and its wording ("Coordinator stays on", "becomes read-only history").
- "Link {machine} to this project" (the `joining` flow), which keeps its title, subtitle and review.
- Translating generated lines (`fingerprintSummary`, `linkMachineProblem`).
- Which side keeps the coordinator by default.
- Splitting the phrase catalogs (about 5,400 lines each before this change, no gate on them; this adds 12 lines to each, as 1372 did).

## Acceptance Criteria

- [x] AC-01: The first step lists only copies of this project: a compared copy whose root repository matches, a copy that tracks the same repository at the same place and has not been compared (its machine is not connected, or its folder could not be read), and the copy a caller names. Every other project is under "Other projects", a disclosure that is closed by default and shows how many it holds. A row there can still be picked and reviewed.
- [x] AC-02: When the folders have been read and no copy is listed, the dialog says "No copy of {project} was found on another machine." and "Other projects" is open. While folders are still being read it says "Reading folders…" and shows neither.
- [x] AC-03: With no copy named by the caller, once the folders have been read the dialog pre-selects the copy with the most matching repositories among compared same-root copies on machines that can link now. A tie goes to the first in the existing order. A copy on a machine that cannot link ("Connect X first") or without a root match is never pre-selected. A copy the caller names and a row the person picked are never replaced.
- [x] AC-04: The subtitle no longer says "One coordinator stays; the other copy runs workers." For a project already linked with another copy it reads "Pick the copy of {project} on another machine. Each copy keeps its own coordinator; Main stays on {main} and you can switch it any time.", {main} being the machine `copyRoles` names. Otherwise it reads "Pick the copy of {project} on another machine. Each copy keeps its own coordinator, and you can switch Main any time."
- [x] AC-05: A selected row is never hidden: closing "Other projects" with a row picked inside it clears that pick.
- [x] AC-06: The first step's title, subtitle, legend, disclosure, messages and button are translated in ru, es, zh, ja, pt, ko, de and fr.
- [x] AC-07: Headless captures of the first step in light and dark are saved in `reports/screens/`: copies with the best one pre-selected, "Other projects" open, and no copy found.

## Approach

- `apps/web/src/studio/linkCandidateGroups.ts` (new, pure): `linkCandidateGroups` splits ranked candidates into copies and others; `bestLinkCopy` picks the pre-selection; `linkedMainEnvironmentId` names Main for a linked project. `sameRepositoryPlaceKey` moves out of `sameRepositoryLinkOffers` in `projectLink.ts` so both use one rule. `LinkCandidate` gains `shared`.
- `apps/web/src/components/studio/ProjectLinkCandidates.tsx` (new): the row list, the disclosure and the messages, inside the one `RadioGroup`. `ProjectLinkDialog.tsx` keeps the state and gains a "folders read" flag, set on the failure path too, that gates the empty message and the pre-selection.
- The pre-selection is set once, when the read finishes. It does not follow later changes, so a row never changes under the pointer.
- Rejected: hiding non-copies with no way to reach them (a renamed or re-cloned copy could not be linked); pre-selecting by `score` (a copy with fewer nested repositories outranks one with the same matches).
- Risks: two existing dialog tests assert the old order and a disabled "Review link" on opening; they are rewritten for the new behaviour, not loosened.

## Reviews

- muse-wonder-1.0 xhigh: PR #538 SHIP at `521de8439069b74efc99ed7ea13908a5195ada17`, merged as `039667b4333eb5b594aa085316ebadfc9bd90801`; closure review SHIP on main `039667b4` (`reports/review.md`). Released in v1.0.338.

Follow-ups left open (minor):
- The review step still says the joining coordinator "becomes read-only history", next to the first step's "Each copy keeps its own coordinator" (D-03).
- Generated match lines ("Same root repository; …") and machine lines ("Connect X first.") stay English (D-04).
- A machine that connects while the dialog is open is not read again until the dialog reopens.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 A same-repository copy on a machine that is not connected stays in the main list with "Connect X first." → default; folded away, the dialog would claim no copy exists.
- D-02 A project that is not linked yet names no Main in the subtitle → default; the review step decides which side keeps the coordinator and may default to the other machine.
- D-03 Subtitle wording is Anton's suggestion, unchanged. The review step still says the joining coordinator "becomes read-only history"; left for a later change.
- D-04 The first step's fixed strings are translated; generated match and machine lines stay English → default.

### Open
- none

## Tasks

### T-01 Group candidates, pick the best copy, name Main
- AC: AC-01, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/linkCandidateGroups.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/linkCandidateGroups.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectLink.ts | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/web && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/studio/linkCandidateGroups.test.ts src/studio/projectLink.test.ts

### T-02 Dialog lists copies, folds the rest, pre-selects and names Main
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectLinkDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectLinkCandidates.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectLinkDialog.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectLinkDialog.choose.test.tsx | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/web && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/components/studio/ProjectLinkDialog.test.tsx src/components/studio/ProjectLinkDialog.choose.test.tsx

### T-03 Translations and headless captures
- AC: AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/es.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/fr.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ja.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ko.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/pt.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ru.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/zh.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/link-dialog/index.html, repositories/anton-abyzov/specwithcode/apps/web/tests/link-dialog/fixture.css, repositories/anton-abyzov/specwithcode/apps/web/tests/link-dialog/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/link-dialog/stubs.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/link-dialog/vite.config.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/link-dialog/verify.mjs | Test: cd ~/.specwithcode/m4/verify/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/link-dialog/vite.config.ts && node apps/web/tests/link-dialog/verify.mjs /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1378-link-dialog-lists-only-copies-of-this-project/reports/screens

### T-04 Review, merge, release, verify and close 1378
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: .specweave/increments/1378-link-dialog-lists-only-copies-of-this-project/spec.md | Test: specweave verify 1378-link-dialog-lists-only-copies-of-this-project
