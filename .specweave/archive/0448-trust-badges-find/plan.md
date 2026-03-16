# Implementation Plan: Trust badges in vskill find output

## Overview

Add visual trust tier badges to `vskill find` CLI output so users can assess skill trustworthiness at a glance. The platform already computes trust tiers (T0-T4) via a composite scoring engine and stores them in the Skill table and KV search index. The CLI needs a rendering function that maps tiers to colored ANSI badges, integrated into both TTY and non-TTY output paths.

## Architecture

### Components
- **`getTrustBadge()` in `find.ts`**: Maps trustTier string to colored ANSI output (green/cyan/yellow/dim)
- **`SkillSearchResult` type in `client.ts`**: Already includes `trustTier?: string` field
- **`searchSkills()` in `client.ts`**: Already maps `trustTier` from raw API response
- **Search API (`/api/v1/skills/search`)**: Returns trustTier from Postgres + KV edge index
- **`SearchIndexEntry` in `search-index.ts`**: Stores trustTier in KV shards

### Data Flow
```
Skill table (trustTier column)
  → search-index.ts (KV shard entry with trustTier)
  → /api/v1/skills/search (returns trustTier in JSON)
  → client.ts searchSkills() (maps to SkillSearchResult.trustTier)
  → find.ts getTrustBadge() (renders colored ANSI badge)
  → console output (TTY: colored badge, non-TTY: raw tier string)
```

### Trust Tier Definitions (from platform)
| Tier | Label | CLI Color | Meaning |
|------|-------|-----------|---------|
| T4 | CERTIFIED | green | High trust: all scans pass, provenance verified, human reviewed |
| T3 | VERIFIED | cyan | Verified: tier2 LLM scan passed, score >= 60 |
| T2 | BASIC | yellow | Basic: tier1 static scan passed, score >= 30 |
| T1 | UNSCANNED | dim | No scan results or low score |
| T0 | BLOCKED | red | On the blocklist (known malicious) |

## Technology Stack

- **Language**: TypeScript (ESM, Node.js)
- **Output**: ANSI escape codes via `src/utils/output.ts` helpers (green, cyan, yellow, dim, red)
- **Testing**: Vitest with mocked API client

**Architecture Decisions**:
- **Badge in TTY only**: Non-TTY outputs the raw tier string (e.g., "T3") for machine parsing; TTY outputs the human-readable colored badge
- **No additional API call**: trustTier piggybacks on the existing search response -- zero latency cost
- **Blocked skills skip badge**: They use the existing BLOCKED rendering path with threat info, not the trust badge
- **KV shard compaction**: trustTier "T1" (default) is omitted from compact entries to save space; reader defaults missing tier to "T1"

## Implementation Phases

### Phase 1: Platform - Trust tier in search API response
- Ensure `trustTier` is stored in Prisma Skill model
- Include `trustTier` in `SEARCH_ENTRY_SELECT` for Postgres queries
- Include `trustTier` in `SearchIndexEntry` for KV shards
- Enrich blocked skills with `trustTier: "T0"` in search route

### Phase 2: CLI - Parse and render trust badges
- Add `trustTier` to `SkillSearchResult` interface in `client.ts`
- Map `trustTier` from raw API response in `searchSkills()`
- Implement `getTrustBadge(trustTier)` function in `find.ts`
- Integrate badge into TTY output line (after star count)
- Include trustTier in non-TTY tab-separated output

### Phase 3: Testing
- Unit tests for all 5 tiers in TTY mode (green certified, cyan verified, yellow maybe, dim maybe, no badge for blocked)
- Unit tests for non-TTY output with trustTier column
- Unit tests for JSON output preserving trustTier

## Testing Strategy

- **Unit tests**: `find.test.ts` with mocked `searchSkills()` verifying ANSI badge presence in console output
- **Coverage**: All 5 trust tiers + undefined/missing tier edge case
- **TTY simulation**: `Object.defineProperty(process.stdout, "isTTY", ...)` to toggle TTY/non-TTY modes

## Technical Challenges

### Challenge 1: ANSI color in test assertions
**Solution**: Tests check for the badge text content (e.g., "certified", "verified", "? maybe") rather than raw ANSI codes, since the output helpers wrap text transparently.

### Challenge 2: KV shard size with additional field
**Solution**: `compactEntry()` omits trustTier when value is "T1" (the default/most common tier), keeping shard sizes minimal.
