# X promotion: viral research, trend method, reply drafts

## Problem

SpecWithCode needs reach on X. The owner wants to know what makes competitor AI-coding videos and posts go viral, a repeatable way to find trending threads worth joining, video ideas built from his own footage, and a reply-drafting workflow that stays human-paced. @aabyzov was suspended on X on 2026-06-12 after an hourly reply bot ran (restored by 2026-09-22), so nothing may post automatically.

## Scope

In: competitor viral research (X posts, launch videos), a trend-finding method, video scenarios from footage on Kingston, a reply-drafting skill and a first batch of drafts. Out: posting anything, automated replies, the fuel-tank promo video (its own thread).

## Acceptance Criteria

- [x] AC-01: reports/viral-research.md lists competitor viral posts and videos with links, metrics and the hook, format and length of each, plus patterns.
- [x] AC-02: reports/trend-method.md gives a daily method to find relevant trending threads, with sources, queries and a scoring rule.
- [x] AC-03: reports/video-scenarios.md proposes scenarios built from named files of the owner's footage, none duplicating the fuel-tank promo.
- [x] AC-04: A reply-drafting skill drafts truthful, humanized replies with a per-day cap and owner review before any post.
- [x] AC-05: reports/reply-drafts-batch-01.md holds a first batch of drafts against live threads, each with the thread link and a fact check.

## Approach

Research fans out over competitors and sources in a workflow, with fact-check verifiers on a cheaper model. Live X threads are read in the owner's signed-in Chrome, read-only. Product claims come from spec-weave.com/code and the launch kit truth rules.

## Decisions

### Defaulted
- D-01 Reply cap: at most 5 replies a day, posted by the owner by hand, never two within 20 minutes.

## Tasks

### T-01 Competitor viral research
- AC: AC-01 | Files: reports/viral-research.md | Test: test -s reports/viral-research.md

### T-02 Trend-finding method
- AC: AC-02 | Files: reports/trend-method.md | Test: test -s reports/trend-method.md

### T-03 Video scenarios from owner footage
- AC: AC-03 | Files: reports/video-scenarios.md | Test: test -s reports/video-scenarios.md

### T-04 Reply-drafting skill
- AC: AC-04 | Files: skill x-reply-drafts | Test: test -s SKILL.md

### T-05 First batch of reply drafts
- AC: AC-05 | Files: reports/reply-drafts-batch-01.md | Test: test -s reports/reply-drafts-batch-01.md

### T-06 Verify and close 1212
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: .specweave/increments/1212-x-promotion-viral-research-trend-method-reply-drafts/* | Test: specweave verify 1212
