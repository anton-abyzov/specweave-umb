# Sidebar chat row machine gap (PR 462)

Created November 15, 2026 by the cross-family reviewer as the record home for the review of pull request 462 in `repositories/anton-abyzov/specwithcode`, because `specweave review --record` needs an increment and none owned that PR. The code was written before this increment existed (Grok, branch `fix/sidebar-row-machine-gap`, reviewed head `456fac4f7`); this file does not claim the work was planned here.

## Problem

In the sidebar Chats list, a wide gap sat between a chat's name and its machine mark, worse at narrow sidebar widths, because every row reserved a shared machine column sized to the longest name in its group. The plan count (`5/6`) also took room from the name, and at the default 256 px sidebar showing the row's actions button made the count vanish.

## Scope

In: track PR 462 (`Chat rows: machine hugs the edge, count yields to the name`, plus `Chat rows: keep the plan count when the menu shows`) and its cross-family review record. Out: code changes in this increment; the owner of PR 462 answers the review findings there.

## Acceptance Criteria

- [ ] AC-01: The machine mark is as wide as its own name and ends at the row's right edge with a small gap; at narrow widths it shrinks to the colored square before the title loses more characters.
- [ ] AC-02: A plan count that does not fit beside the name's floor drops before the title is cut shorter, and a count visible at the default 256 px sidebar stays visible on hover, keyboard focus, an open menu and touch screens.
- [ ] AC-03: Project thread rows with the same gap problem get the same treatment.
- [ ] AC-04: A cross-family review of head `456fac4f7` is recorded under `reports/reviews/` with its verdict.

## Approach

PR 462 carries the implementation in `apps/web/src/components/studio/shell/` and related tests. This increment only holds the review record produced from a read-only adversarial pass over `git diff 77fe12407..456fac4f7`.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Record the review under this new increment instead of guessing an existing one, because no increment's spec, ledger or card names PR 462 (reversible: move the record if the coordinator names another home).
### Open
- none

## Review
- Reviewer: meta (muse-wonder-full-1.0)

## Tasks

### T-01 Record the cross-family review of PR 462 at 456fac4f7
- AC: AC-04 | Files: .specweave/increments/1357-sidebar-chat-row-machine-gap-pr-462/reports | Test: specweave review 1357-sidebar-chat-row-machine-gap-pr-462 --record <report.md> --model muse-wonder-full-1.0 --head 456fac4f7

### T-02 Owner answers the review findings on PR 462
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/shell.css, repositories/anton-abyzov/specwithcode/apps/web/tests/sidebar-stable-order/row-room.mjs | Test: node apps/web/tests/sidebar-stable-order/row-room.mjs on a fixture build
