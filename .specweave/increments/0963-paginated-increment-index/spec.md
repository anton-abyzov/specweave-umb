# Paginated, searchable increment index

## Problem

The Link increment picker lists at most 300 increments: the server reads every increment folder, sorts, keeps the newest 300 and reads metadata for each; the dialog filters only those. In a planning root with thousands of increments, older ones cannot be found, and every open of the picker reads up to 300 metadata files.

## Scope

In: `projects.incrementsList` input and result, `listProjectIncrements`, the Link increment dialog. Out: a background indexer, LLM summarisation, Kanban boards.

## Acceptance Criteria

- [ ] AC-01: The list accepts a search text, a status filter, an offset and a limit, and returns the page, the total match count and counts per status
- [ ] AC-02: A search for an id or a word in the title finds any increment in a root of 3,000 increments, not only the newest 300
- [ ] AC-03: A page reads metadata only for the folders it needs and reuses it while the folder is unchanged; no background job or model call
- [ ] AC-04: The dialog searches on the server, filters by status with counts, and loads more pages
- [ ] AC-05: Older clients that send only projectId and threadId still get the newest increments

## Approach

Folder names are read once per request (a directory listing). An id-only query filters names without opening files. Title search and status filters read `metadata.json` through a cache keyed by path and mtime. Default limit 50, maximum 200.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 No persistent index file: a directory listing plus an mtime cache is enough for thousands and cannot go stale
### Open
- none

## Tasks

### T-01 Paginated, filtered server list
- AC: AC-01, AC-02, AC-03, AC-05 | Files: packages/contracts/src/threadIncrementProgress.ts, apps/server/src/project/ThreadIncrementProgress.ts, apps/server/src/project/ThreadIncrementProgressService.ts, apps/server/src/project/IncrementIndex.test.ts | Test: vp test run apps/server/src/project/IncrementIndex.test.ts
### T-02 Dialog search, status filter and paging
- AC: AC-04 | Files: apps/web/src/components/chat/LinkIncrementDialog.tsx | Test: headless dialog screenshot
### T-03 Verify and close 0963
