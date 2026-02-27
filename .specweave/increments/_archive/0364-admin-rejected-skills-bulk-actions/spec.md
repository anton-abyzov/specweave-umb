# 0364: Admin-Only Rejected Skills with Bulk Actions

## Problem
The Trust Center's "Rejected Skills" tab has a display bug (API returns `rejections` key but frontend reads `entries` — shows count but empty table). The tab is publicly visible when it should be admin-only. There's no way to act on rejected skills in bulk (reprocess or block). Many rejections are platform errors (missing SKILL.md, timeouts) not real security issues.

## Solution
- Fix API response bug
- Make rejected tab admin-only (GitHub username allowlist)
- Add server-side pagination (20/page) with category filtering (security issues vs platform errors)
- Add bulk actions: reprocess (re-enqueue) and block (add to blocklist)

## User Stories

### US-001: Admin views rejected skills
As an admin, I want to see rejected skills categorized as "Security Issues" vs "Processing Errors" so I can focus on real threats.
- [x] AC-US1-01: Rejected tab only visible when user is admin
- [x] AC-US1-02: Default category filter is "Security Issues"
- [x] AC-US1-03: Paginated with 20 items per page
- [x] AC-US1-04: Search by skill name with debounce

### US-002: Admin bulk reprocesses rejected skills
As an admin, I want to select multiple rejected skills and reprocess them so that platform errors get a fresh scan.
- [x] AC-US2-01: Checkbox selection per row + select-all
- [x] AC-US2-02: Bulk action bar appears when items selected
- [x] AC-US2-03: Reprocess resets state to RECEIVED and re-enqueues

### US-003: Admin bulk blocks rejected skills
As an admin, I want to select multiple rejected skills and block them with threat metadata so confirmed threats are added to the blocklist.
- [x] AC-US3-01: Block dialog with threatType, severity, reason fields
- [x] AC-US3-02: Creates BlocklistEntry for each selected skill
