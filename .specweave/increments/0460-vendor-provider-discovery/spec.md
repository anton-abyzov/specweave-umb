---
increment: 0460-vendor-provider-discovery
title: "Vendor & Provider Skill Discovery Enhancement"
type: feature
priority: P0
status: active
created: 2026-03-09
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Vendor & Provider Skill Discovery Enhancement

## Problem Statement

`npx vskill find frontend-design` returns 15 community results but zero from Anthropic's official repos, despite both `anthropics/skills` and `anthropics/claude-code` containing the skill. The root cause is that `vendor-org-discovery` was never deployed to any VM -- a deployment gap. Beyond the fix, when the same skill exists in multiple repos from the same vendor org, search results show duplicates instead of a single canonical entry. There is also no abstraction for representing skill providers beyond the flat `VENDOR_ORGS` set, blocking future integration with external providers like Smithery or Codex.

## Goals

- Deploy vendor-org-discovery to VM-2 so vendor skills are indexed
- Deduplicate search results when the same skill appears in multiple repos from the same org
- Surface alternate source repos in CLI output
- Establish a provider registry type system as foundation for multi-provider support

## User Stories

### US-001: Deploy vendor-org-discovery (P0)
**Project**: vskill-platform

**As a** platform operator
**I want** vendor-org-discovery deployed to VM-2
**So that** vendor skills from Anthropic, OpenAI, and other trusted orgs are discovered and indexed in the registry

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given VM-2 env file at `crawl-worker/.env.vm2`, when deployment runs via `deploy.sh`, then `vendor-org-discovery` is present in `ASSIGNED_SOURCES` and the crawl-worker starts without errors
- [x] **AC-US1-02**: Given the crawl-worker is running on VM-2, when the health endpoint is queried, then the response includes `vendor-org-discovery` as an active source
- [x] **AC-US1-03**: Given vendor-org-discovery has run at least once, when a user searches `vskill find frontend-design`, then Anthropic skills appear in results with `certTier: CERTIFIED` and `trustTier: T4`
- [x] **AC-US1-04**: Given the admin vendor-orgs endpoint exists, when an on-demand discovery is triggered via `POST /api/v1/admin/discovery/vendor-orgs`, then the response includes `orgBreakdown` with skill counts per vendor org

---

### US-002: Search dedup for same-org skills (P1)
**Project**: vskill-platform

**As a** user searching for skills
**I want** search results to show one canonical entry when the same skill exists in multiple repos from the same vendor org
**So that** I see clean, non-redundant results with the best version highlighted

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given skills with identical `ownerSlug` and `skillSlug` exist across multiple repos (e.g., `anthropics/skills/frontend-design` and `anthropics/claude-code/frontend-design`), when edge search returns results, then duplicates are collapsed into a single canonical entry (the one with highest `githubStars`)
- [x] **AC-US2-02**: Given a collapsed search result, when the API response is returned, then the canonical entry includes an `alternateRepos` array containing `{ ownerSlug, repoSlug, repoUrl }` for each collapsed duplicate
- [x] **AC-US2-03**: Given the Postgres fallback search path, when results are returned, then the same dedup logic applies (group by `ownerSlug`+`skillSlug`, keep highest stars, attach alternates)
- [x] **AC-US2-04**: Given the `SearchResult` type in `search.ts`, when `alternateRepos` is added, then the field is typed as `Array<{ ownerSlug: string; repoSlug: string; repoUrl: string }>` and is optional (undefined when no duplicates exist)
- [x] **AC-US2-05**: Given the dedup logic, when unit tests run, then at least 3 test cases cover: no duplicates (passthrough), two repos same skill (collapse), mixed vendors (only same-org collapses)

---

### US-003: CLI display of alternate sources (P1)
**Project**: vskill

**As a** CLI user running `vskill find`
**I want** to see alternate source repos when a result has them
**So that** I know the skill is available from multiple repos and can choose

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the `SkillSearchResult` interface in `client.ts`, when updated, then it includes `alternateRepos?: Array<{ ownerSlug: string; repoSlug: string; repoUrl: string }>`
- [x] **AC-US3-02**: Given a search result with `alternateRepos` and TTY output, when displayed, then a line reading `also: owner/other-repo` appears in dim text below the main entry
- [x] **AC-US3-03**: Given a search result with `alternateRepos` and `--json` flag, when output is rendered, then the `alternateRepos` array is included in the JSON object
- [x] **AC-US3-04**: Given a search result with `alternateRepos` and piped (non-TTY) output, when displayed, then alternate repos are appended as a tab-separated field after existing columns

---

### US-004: Provider registry foundation (P2)
**Project**: vskill-platform

**As a** platform architect
**I want** a provider registry that can represent GitHub orgs and future external providers
**So that** the system is ready for diverse skill sources beyond GitHub org scanning

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given a new file `src/lib/trust/provider-registry.ts`, when imported, then it exports a `ProviderDefinition` type with fields: `id: string`, `type: "github-org" | "external-api"`, `name: string`, `trustLevel: "vendor" | "trusted" | "community"`, and `config: Record<string, unknown>`
- [x] **AC-US4-02**: Given the provider registry, when `PROVIDER_REGISTRY` constant is exported, then it contains entries for all current vendor orgs (anthropics, openai, google-gemini, google, microsoft, vercel, cloudflare) with `type: "github-org"` and `trustLevel: "vendor"`
- [x] **AC-US4-03**: Given the provider registry, when `VENDOR_ORGS` is derived from it, then `VENDOR_ORGS` equals the set of provider IDs where `trustLevel === "vendor"` and `type === "github-org"`
- [x] **AC-US4-04**: Given `trusted-orgs.ts` is migrated to use the registry, when existing callers import `VENDOR_ORGS`, `TRUSTED_ORGS`, `isVendorOrg`, `isTrustedOrg`, or `checkVendorRepo`, then all exports remain backward-compatible with identical behavior
- [x] **AC-US4-05**: Given the migration, when unit tests run, then equivalence tests verify that `VENDOR_ORGS` and `TRUSTED_ORGS` from the migrated module produce identical sets to the current hardcoded values

## Out of Scope

- Smithery or Codex provider implementation (US-004 is foundation only)
- UI changes on verified-skill.com web frontend for alternate repos display
- Changing the dedup strategy for cross-org duplicates (only same-org dedup)
- Modifying the crawl scheduler or adding new VM assignments beyond VM-2
- Changing trust tier logic or certification pipeline

## Technical Notes

### Dependencies
- `crawl-worker/sources/vendor-org-discovery.js` (JS crawl-worker source) -- already implemented
- `src/lib/crawler/vendor-org-discovery.ts` (platform-side TS) -- already implemented
- `src/lib/trust/trusted-orgs.ts` -- will be migrated to use registry
- `src/lib/search.ts` -- dedup logic added post-fetch
- `src/commands/find.ts` (vskill CLI) -- display changes

### Architecture Decisions
- Dedup is applied post-fetch in `searchSkillsEdge` and `searchSkills` rather than at index time, keeping the KV index simple and dedup logic centralized
- Canonical selection uses highest `githubStars` within the same `ownerSlug`+`skillSlug` group
- Provider registry is a static TypeScript module (not database-backed) to maintain the current zero-DB-dependency pattern for trust checks

## Success Metrics

- Anthropic skills appear in `vskill find` results within 24h of deployment
- Zero duplicate entries for same-org skills in search results
- Provider registry passes backward-compatibility tests with zero behavioral changes to existing trust checks
