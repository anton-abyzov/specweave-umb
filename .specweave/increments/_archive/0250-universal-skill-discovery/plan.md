# Plan — 0250: Universal Skill Discovery Pipeline

## Architecture

```
SourceRegistry
├── GitHubProvider (broad search: SKILL.md, .claude/commands, descriptions)
├── SkillsShProvider (scrape skills.sh listing)
└── NpmProvider (npm registry keyword search)
        ↓
  SubmissionQueue (existing)
        ↓
  ContentFetcher (new: raw.githubusercontent.com)
        ↓
  SecurityScanner (existing scanSkillContent — just needs wiring)
        ↓
  Dashboard UI (existing — trust scores now populated)
```

## New Files

1. `src/core/fabric/discovery/provider.ts` — `DiscoveryProvider` interface + `SourceRegistry` class
2. `src/core/fabric/discovery/github-provider.ts` — Broad GitHub search
3. `src/core/fabric/discovery/skillssh-provider.ts` — skills.sh scraper
4. `src/core/fabric/discovery/npm-provider.ts` — npm registry search
5. `src/core/fabric/content-fetcher.ts` — Fetch SKILL.md raw content

## Modified Files

1. `src/cli/workers/marketplace-scanner-worker.ts` — Use SourceRegistry instead of inline GitHub search
2. `src/core/fabric/submission-queue-types.ts` — Add `skillContent?: string` to SkillSubmission
3. `src/core/fabric/submission-queue.ts` — Add `updateContent()` method

## Implementation Order

Phase 1 (T-001 → T-005): Provider framework + all 3 providers + config
Phase 2 (T-006 → T-007): Content fetching
Phase 3 (T-008 → T-009): Security scoring wiring
Phase 4 (T-010): Integration into scanner worker
