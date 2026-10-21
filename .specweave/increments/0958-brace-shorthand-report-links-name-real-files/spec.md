# Brace shorthand report links name real files

## Problem

On October 20, 2026 the user opened a report chip in "Finish every authorized project thread" and got only "Failed to read workspace file '/Users/antonabyzov/.specwithcode/audits/2026-10-20/findings-{B,C,D,E}.md' in '<specweave checkout>'". The worker wrote `~/.specwithcode/audits/2026-10-20/findings-{B,C,D,E}.md` in inline code. Four real files exist (`findings-B.md` … `findings-E.md`), and the server reads them fine (no scope or authorization problem). Causes, all in specwithcode-dev:

1. `apps/web/src/markdown-links.ts` treats the brace span as one literal path, while `threadArtifacts.ts` has its own `expandBraceList`. The Artifacts strip showed the real files; the chat chip opened a file that does not exist.
2. An absolute file link is never checked on the host (`useExistingFileLinks` only checks candidates, searches and extensionless paths), so a missing file looks like a normal chip.
3. The viewer shows the server's raw message, which names the workspace even for an absolute path and never says the file is missing or what is beside it.
4. The worker instructions ask for absolute paths but not for one path per file, so shell shorthand reaches reports.

## Scope

In: brace (`{a,b}`, `{A..E}`, `{1..3}`) and basename glob (`*`, `?`) spans in inline code and fenced path lists; chat chips, viewer links and artifacts; the not-found pane in the report viewer; the server's not-found message; the worker report rule. Out: brace syntax inside explicit markdown link destinations (`[x](a{b,c}.md)`, rare, stays literal); recording each run's cwd (report-file-links.md option B).

## Acceptance Criteria

- [ ] AC-01: A span naming several files in brace shorthand shows one chip per real file (`findings-B.md`, `findings-C.md`, `findings-D.md`, `findings-E.md`), each opening that file; the shorthand itself is never a clickable file.
- [ ] AC-02: A file whose name really contains braces (it exists on the host) still opens as one file.
- [ ] AC-03: A basename glob (`findings-*.md`) shows the host's matching files as chips, and never a literal chip for the pattern.
- [ ] AC-04: An expansion the host lacks is marked not found, and the Artifacts strip and the chat chips agree (one shared expansion).
- [ ] AC-05: Opening a missing file in the viewer says it was not found, gives its full path and folder, and offers similarly named files in that folder to open; a missing folder is named as such. The server's message for a missing absolute path says "not found" without naming the workspace.
- [ ] AC-06: A real file outside the checkout under an app home (`~/.specwithcode/audits/...`) reads; protected state stays refused (no access broadened).
- [ ] AC-07: The worker report rule asks for one full path per file, never brace or glob shorthand.
- [ ] AC-08: Headless check of the original report text in the built app: four chips, each opening its file, and the missing-file pane, light and dark, saved as files.

## Approach

`apps/web/src/markdown-links.ts` gains `expandShellShorthand` (braces, ranges, nesting, `$`-prefixed groups left alone, capped) and `MarkdownFileLinkMeta.expansions` / `glob`; `resolveInlineCodeFileLinks` settles each expansion with the same base folders; `threadArtifacts.ts` drops its own expander. `useExistingFileLinks` checks the literal path first (a real brace name wins), then each expansion, and lists the folder for a glob. `ChatMarkdown` renders a group of chips keeping the authored copy text. `ViewerLinkedPane` lists the parent folder after a failed read to show the not-found pane. `packages/contracts/src/project.ts` words the missing-file message; `ProjectWorkspaceService.ts` and `StudioOrchestrationInstructions.ts` carry the report rule.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Until the host answers, a brace span shows its expansions (the likely meaning); a literal brace file replaces them once the host confirms it (reversible).
- D-02 More than 32 expansions or a glob in a folder segment stays plain code (reversible).
### Open
- none

## Tasks

### T-01 Shared shorthand expansion and settled chips
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/web/src/markdown-links.ts, apps/web/src/threadArtifacts.ts, apps/web/src/components/chat/useExistingFileLinks.ts, apps/web/src/components/ChatMarkdown.tsx | Test: vp test run apps/web/src/markdown-links.shorthand.test.ts apps/web/src/threadArtifacts.test.ts

### T-02 Missing-file pane and server message
- AC: AC-05, AC-06 | Files: apps/web/src/components/chat/ViewerLinkedPane.tsx, packages/contracts/src/project.ts, apps/server/src/workspace/WorkspaceFileSystem.test.ts | Test: vp test run packages/contracts/src/project.test.ts apps/server/src/workspace/WorkspaceFileSystem.test.ts

### T-03 Report rule for workers
- AC: AC-07 | Files: apps/server/src/project/ProjectWorkspaceService.ts, apps/server/src/provider/StudioOrchestrationInstructions.ts | Test: vp test run apps/server/src/provider

### T-04 Headless check, PR and merge
- AC: AC-08 | Files: apps/web/tests/viewer-links/ | Test: node apps/web/tests/viewer-links/verify.mjs ~/.specwithcode/m4/scratch/brace-links-evidence

### T-05 Verify and close 0958
