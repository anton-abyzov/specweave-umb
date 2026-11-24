# Artifact cards show real content for every file

## Problem

Artifact cards for reports written outside the project folder show only "Document MD" and the file name. The M4 runs 1.0.152, which includes the Markdown pages from #1189, so this is not an old install. `artifactPreviewFormat` returns null for any absolute non-image path, so the card never reads the file, although `projects.readFile` serves absolute host paths. Agents often write reports to evidence and temp folders, so most real cards are blank.

Two more defects sit beside it. Cards and the viewer read a worktree or absolute file with the project's machine, not the machine of the thread that wrote it. A deleted file fails `realpath`, which counts as a passing failure, so its card retries forever.

## Scope

In: card previews for absolute paths, short excerpt reads, the writing thread's machine, lasting failures, the fallback, the dark theme treatment. Out: moving files between machines, thread snapshots, the viewer's layout.

## Acceptance Criteria

- [ ] AC-01: A Markdown card for a file outside the project shows a miniature of its title, headings and first lines, with no "Document MD" label.
- [ ] AC-02: In the dark theme the Markdown miniature is light on dark and matches the theme; HTML pages and images keep their real colours.
- [ ] AC-03: A card reads at most 32 KB of Markdown or text and 256 KB of HTML, lazily and cached; a file larger than the old 512 KB limit still previews.
- [ ] AC-04: A worktree or absolute file written by a thread on another machine is read from that machine, on the card and in the viewer.
- [ ] AC-05: A missing, protected or unreadable file stops retrying and shows its name with a quiet note.
- [ ] AC-06: 495 cards still scroll within 2x of the 9.3 ms p99 frame baseline.
- [ ] AC-07: Headless screenshots against real artifacts show the before and after in both themes.

## Approach

`artifactPreviewFormat` drops the path and size checks. `ProjectReadFileInput` gains an optional `maxBytes`, clamped by the server; an older server ignores it and the client still slices. `artifactFileEnvironment` picks the thread's machine when `root` is set or the path is absolute. `isLastingReadFailure` also counts `realpath-target` failures and protected files; no contract change, so older servers benefit too. `{type:"none", gone:true}` carries the note. In `:root.dark`, a CSS `invert` plus `hue-rotate` on the Markdown sheet reuses one raster and one cache key.

Rejected: the asset route, since it refuses `.md` outside a project and would widen what it serves; a second dark raster, since it doubles cache and work.

## Decisions

- Read through `projects.readFile`: it already checks protected paths and reaches other machines over their connection.
- The "Document" head stays only for files with no preview format (a PDF), where the type adds information.

## Tasks

### T-01 Excerpt read
- AC: AC-03 | Files: packages/contracts/src/project.ts, apps/server/src/workspace/WorkspaceFileSystem.ts, apps/web/src/components/files/projectFilesQueryState.ts | Test: WorkspaceFileSystem.test.ts

### T-02 Cards read every file from the right machine
- AC: AC-01, AC-03, AC-04, AC-05 | Files: apps/web/src/studio/artifactPreview.ts, apps/web/src/components/studio/shell/ProjectArtifactShelf.tsx | Test: ProjectArtifactShelf.test.tsx, projectFilesQueryState.test.ts

### T-03 Dark miniature and fallback
- AC: AC-01, AC-02, AC-05 | Files: apps/web/src/components/studio/shell/panes.css | Test: apps/web/tests/project-artifacts/verify.mjs

### T-04 Reproduce and prove headless
- AC: AC-06, AC-07 | Files: ~/.specwithcode/m4/evidence/artifact-card-previews/ | Test: installed app, M1 over a tunnel, bench.mjs
