# Artifact shelf shows deliverables, not task logs

## Problem

The project "Artifacts" shelf in hack26-crypto (November 8, 2026) showed 11 cards, led by `task-T-04.txt`, `task-T-03.txt` and `task-T-02.txt`. Each card is a raw command log.

Those files come from `specweave task done --run`. `writeRunLog` (`specweave/src/cli/commands/task.ts:407`) writes `.specweave/increments/<id>/reports/task-<T-NN>.txt` as task evidence, and the ledger cites them. The server scans every increment `reports/` folder (`apps/server/src/project/ProjectLibrary.ts:228`). `collectProjectArtifacts` (`apps/web/src/studio/projectArtifacts.ts:300`) adds each scanned output with no kind filter, and `libraryFileType` types `.txt` and every unknown extension as a document. Thread lists add any file a reply names, so a quoted `full log: …/task-T-04.txt` lands there too.

ChatGPT and Claude both keep logs out of their artifact views:

- ChatGPT's Library holds generated files and images, and code-interpreter stdout stays in a collapsed block.
- Codex shows the diff and cites terminal logs as evidence in its summary.
- Claude makes artifacts only from substantial, self-contained content people reuse, and its files feature offers documents for download.
- Claude Code collapses tool output in the transcript.

## Scope

In:

- One shared rule that decides which artifacts are deliverables.
- The project shelf shows only deliverables.
- The thread artifacts list folds logs into a collapsed "Logs" section.
- The Library keeps listing everything.
- Unit tests.
- Headless before and after screenshots of the shelf fixture.

Out:

- SpecWeave's evidence file name and format.
- A project-level hide store.
- Server scan changes.

## Acceptance Criteria

- [ ] AC-01: The project shelf counts and shows deliverables only. Deliverables are designs, decks, pages, Markdown/PDF/Word documents, images, video, published links, and anything registered in the hub. Plain-text logs (`.txt`, `.log`, `.out`, extensionless), code, and data such as JSON are left off unless registered or pinned.
- [ ] AC-02: A pinned artifact always shows on the shelf, whatever its type. The existing project pin is the override, with no new store.
- [ ] AC-03: The Library's Artifacts view still lists the logs, under their increment, so they stay reachable.
- [ ] AC-04: A thread's artifacts list folds plain-text logs into a collapsed "Logs" section that the chip count leaves out. Pinning a log brings it back to Pinned.
- [ ] AC-05: Headless before and after screenshots of the shelf fixture show `task-T-NN.txt` gone and the deliverables still there.

## Approach

- `apps/web/src/artifactShelf.ts`:
  - Add `isPlainTextLog(path)`.
  - Add a `logs` section. It is collapsible, sits before Older, and holds unpinned, non-hidden logs, which are left out of `visibleCount`.
- `apps/web/src/studio/projectArtifacts.ts`:
  - Add `isShelfDeliverable(artifact)`. Pinned or registered artifacts always show. Otherwise the kind decides: design, slides, page, image, video and link show; a document shows unless `isPlainTextLog` matches; data and code never show.
  - Add `shelfArtifacts(artifacts)`.
- `ProjectArtifactShelf.tsx`: the shelf and its count use `shelfArtifacts`. The Library uses the full list.
- Tests go in `apps/web/src/studio/projectArtifacts.test.ts` and `apps/web/src/artifactShelf.test.ts`. The fixture `apps/web/tests/project-artifacts/` gains `task-T-NN.txt` outputs.
- Rejected:
  - Filtering in the server scan, which would also hide the logs from the Library.
  - A denylist on `task-T-*` names only, because other logs would leak.
  - A parallel hide store.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: JSON counts as a deliverable only when it is registered in the hub or pinned. Rationale: the user said "JSON only when it's the deliverable", and registering is the explicit signal.
- D-02: A thread list folds logs instead of dropping them, so the evidence stays one click from the thread.

### Open
- none

## Tasks

### T-01 Shelf deliverable rule and project shelf filter
- AC: AC-01, AC-02, AC-03 | Files: apps/web/src/studio/projectArtifacts.ts, apps/web/src/studio/projectArtifacts.test.ts, apps/web/src/components/studio/shell/ProjectArtifactShelf.tsx | Test: npx vitest run apps/web/src/studio/projectArtifacts.test.ts

### T-02 Thread list folds logs
- AC: AC-04 | Files: apps/web/src/artifactShelf.ts, apps/web/src/artifactShelf.test.ts, apps/web/src/components/chat/ArtifactShelfList.tsx | Test: npx vitest run apps/web/src/artifactShelf.test.ts

### T-03 Headless before/after screenshots
- AC: AC-05 | Files: apps/web/tests/project-artifacts/main.tsx, apps/web/tests/project-artifacts/verify.mjs | Test: node apps/web/tests/project-artifacts/verify.mjs
