---
increment: 0445-trending-diversity
title: "Trending Skills Diversity: Cap Per-Repo + Show 10"
---

# Architecture Plan: Trending Skills Diversity

## Overview

Add a `diversifyTrending()` pure function to `stats-compute.ts` that caps per-repo skill count and limits total trending list size. Integrate into both stats computation paths.

## Key Decisions

### ADR-001: Pure function approach
**Decision**: Implement diversity filtering as a standalone pure function rather than SQL-level filtering.
**Rationale**: Easier to test, more flexible (works with both full and minimal stats paths), and the DB query already fetches top 50 sorted by score — post-processing is simpler than complex SQL windowing.

### ADR-002: Repo URL as grouping key with author fallback
**Decision**: Group by `repoUrl`, falling back to `author` when repoUrl is empty.
**Rationale**: repoUrl is the most accurate grouping key, but some skills may not have one. Author provides a reasonable fallback.

## Components

### 1. `diversifyTrending()` function
- **File**: `src/lib/stats-compute.ts`
- **Input**: sorted skills array, maxPerRepo, limit
- **Output**: filtered array preserving input order
- **Logic**: Single-pass with repo counter map

### 2. Integration in `computeFullStats()`
- Call after momentum sort, before returning trending array

### 3. Integration in `computeMinimalStats()`
- Same pattern for consistency

### 4. Unit tests
- **File**: `src/lib/__tests__/stats-compute.test.ts`
- Test: capping, limit, order preservation, empty repoUrl fallback, empty input, momentum interaction
