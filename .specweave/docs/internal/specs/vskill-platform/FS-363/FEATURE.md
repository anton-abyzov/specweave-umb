---
id: FS-363
title: "Search: match by repository name, supplement partial edge results"
type: feature
status: active
priority: P1
created: 2026-02-24
lastUpdated: 2026-02-24
complexity: medium
stakeholder_relevant: true
project: vskill-platform
external_tools:
  github:
    type: milestone
    id: 5
    url: https://github.com/anton-abyzov/specweave-umb/milestone/5
---

# Search: match by repository name, supplement partial edge results

## TL;DR

**What**: Fix search to match by repository name and supplement partial edge results with Postgres fallback.
**Status**: active | **Priority**: P1
**User Stories**: 2

## Overview

Searching "spec" in SearchPalette returns only 2 skills instead of all skills from the specweave repository. Root cause: edge search shards by first letter of skill name, so skills in other shards are invisible; route returns partial edge results immediately without consulting Postgres.

## User Stories

- [US-001: Search by repository name](./us-001-search-by-repository-name.md)
- [US-002: Supplement partial edge results with Postgres](./us-002-supplement-partial-edge-results-with-postgres.md)
