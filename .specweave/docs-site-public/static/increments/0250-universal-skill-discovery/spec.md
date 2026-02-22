# 0250: Universal Skill Discovery Pipeline

## Problem

The marketplace scanner only searches GitHub by two narrow topics (`claude-code-skill`, `specweave-plugin`) which yields almost no results. The pipeline is also hollow: discovered repos never have their SKILL.md content fetched or security-scanned, so trust scores are always 0.

Real skills exist across multiple sources:
- GitHub repos containing `SKILL.md` files (thousands, not tagged with specific topics)
- skills.sh curated directory
- npm packages with agent-skill keywords
- Known skill authors/organizations

## Solution

Build a **Source Registry** — a pluggable system of discovery providers that feed into the existing submission queue. Each provider knows how to search one source and normalize results into `GitHubRepoInfo` shape. Then wire up the content fetching and security scanning stages that are currently stubbed.

## User Stories

### US-001: Multi-Source Discovery
As a marketplace admin, I want the scanner to discover skills from GitHub (broad search), skills.sh, and npm, so that the marketplace has comprehensive coverage.

**ACs:**
- [x] AC-US1-01: Source registry accepts pluggable provider implementations
- [x] AC-US1-02: GitHub provider searches by `filename:SKILL.md` AND `path:.claude/commands` AND `claude code skill` in description/readme
- [x] AC-US1-03: skills.sh provider fetches their public listing and extracts GitHub repo URLs
- [x] AC-US1-04: npm provider searches for packages with `claude-code-skill` or `agent-skill` keywords
- [x] AC-US1-05: All providers normalize results into the existing `GitHubRepoInfo` shape
- [x] AC-US1-06: Scanner config in `.specweave/config.json` lists enabled sources

### US-002: SKILL.md Content Fetching
As the scanner pipeline, I need to fetch actual SKILL.md content from discovered repos so that security scanning can analyze it.

**ACs:**
- [x] AC-US2-01: After discovery, fetch SKILL.md via GitHub raw content API (`raw.githubusercontent.com`)
- [x] AC-US2-02: Store fetched content on the submission record
- [x] AC-US2-03: Handle missing/moved SKILL.md gracefully (mark as `tier1_failed`)
- [x] AC-US2-04: Respect rate limits when fetching content

### US-003: Security Scoring Integration
As a marketplace admin, I want discovered skills to be automatically security-scored so the trust score in the dashboard reflects real analysis.

**ACs:**
- [x] AC-US3-01: Pass fetched SKILL.md content to `scanSkillContent()` for Tier 1 analysis
- [x] AC-US3-02: Populate `tier1Result` with actual findings, score, and pass/fail
- [x] AC-US3-03: Skills scoring >= 70 auto-advance to `tier1_passed`
- [x] AC-US3-04: Skills scoring < 70 marked `tier1_failed` with findings detail

## Technical Notes

- Providers implement a `DiscoveryProvider` interface: `{ name: string; discover(): AsyncGenerator<GitHubRepoInfo> }`
- The scanner worker already has the loop — we add a provider orchestrator that feeds it
- Content fetching uses `raw.githubusercontent.com/{owner}/{repo}/{branch}/SKILL.md` (no API token needed for public repos)
- npm search via `https://registry.npmjs.org/-/v1/search?text=keywords:claude-code-skill`

## Out of Scope
- Tier 2 (manual/AI review) — handled by increment 0245
- Publishing to external registries
- Private repo scanning
