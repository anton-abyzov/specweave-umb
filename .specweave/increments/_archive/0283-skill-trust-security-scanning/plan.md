# Implementation Plan: Skill Trust and Security Scanning

## Overview

This increment spans three repositories: vskill (CLI scanner patterns), vskill-platform (trust model, blocklist propagation, provenance, platform scanner), and specweave (core security-scanner DCI patterns). The implementation follows a bottom-up approach: scanner patterns first, then trust model and data layer, then integration points (CLI display, UI, auto-propagation).

## Architecture

### Components

1. **DCI Pattern Scanner** (vskill, vskill-platform, specweave): New regex patterns specifically targeting malicious DCI shell blocks. Shared pattern definitions with repo-specific wrappers.
2. **Trust Score Engine** (vskill-platform): Computes and persists trust tier (T0-T4) and trust score (0-100) per skill based on weighted inputs.
3. **Blocklist Auto-Propagation** (vskill-platform): Event handler that creates BlocklistEntry records when SecurityReports are resolved as confirmed malware.
4. **Provenance Verifier** (vskill-platform): GitHub API integration that checks submitter identity against repository ownership/collaborator list.
5. **Content Hash Verifier** (vskill-platform): Pre-publish hash comparison to detect post-scan content tampering.
6. **Trust Display** (vskill CLI, vskill-platform UI): Trust tier and score surfaced in CLI output and web UI.

### Data Model Changes

**Skill model (Prisma) -- new fields:**
```prisma
model Skill {
  // ... existing fields ...
  trustTier           String    @default("T1")  // T0-T4
  trustScore          Int       @default(0)      // 0-100
  provenanceVerified  Boolean   @default(false)
  provenanceCheckedAt DateTime?
}
```

**Submission model -- new fields:**
```prisma
model Submission {
  // ... existing fields ...
  provenanceVerified  Boolean   @default(false)
  provenanceStatus    String?   // "verified" | "mismatch" | "unchecked"
  contentHashAtScan   String?   // SHA-256 of SKILL.md at scan time
}
```

**ScanResult model -- new field:**
```prisma
model ScanResult {
  // ... existing fields ...
  contentHash String?  // SHA-256 of content that was scanned
}
```

### API Contracts

- `GET /api/v1/skills/:name` -- adds `trustTier`, `trustScore`, `provenanceVerified` to response
- `GET /api/v1/stats` -- adds `trust: { t0: N, t1: N, t2: N, t3: N, t4: N }` to response
- `PATCH /api/v1/admin/reports/:id` -- when resolving as confirmed_malware, auto-creates blocklist entry

### Trust Score Flow

```
Scan Results ──┐
               ├──> Trust Score Engine ──> trustTier + trustScore
Provenance ────┤                              │
               │                              ▼
Community ─────┤                     Skill.trustTier (T0-T4)
               │                     Skill.trustScore (0-100)
Blocklist ─────┘                              │
                                              ▼
                                     API Response / CLI / UI
```

## Technology Stack

- **Language/Framework**: TypeScript (all three repos)
- **Scanner**: Regex-based pattern matching (existing approach, extended)
- **Database**: PostgreSQL via Prisma (vskill-platform)
- **External API**: GitHub REST API (provenance verification)
- **Testing**: Vitest (TDD mode)

**Architecture Decisions**:

- **ADR-1: Separate trust from extensibility**: Trust tiers (T0-T4) are orthogonal to extensibility tiers (E0-E4). A skill can be maximally extensible (E4) but minimally trusted (T1) or vice versa. This avoids conflating customizability with safety.
- **ADR-2: Computed + persisted trust score**: The trust score is computed when inputs change and persisted in the database, rather than computed on every request. This avoids N+1 query patterns and enables efficient filtering/sorting by trust level.
- **ADR-3: DCI patterns in all three repos**: DCI patterns are defined independently in each repo rather than shared via a package, because each repo has slightly different scanner interfaces (vskill uses `ScanPattern`, specweave uses `PatternCheck`, platform uses its own format). The patterns themselves are documented in the spec to ensure consistency.
- **ADR-4: Provenance via GitHub Collaborators API**: The `/repos/{owner}/{repo}/collaborators/{username}` endpoint provides the most reliable check. It handles both user-owned repos (owner match) and org repos (collaborator membership). This requires a GitHub access token with `repo` scope, which the platform already has via OAuth.

## Implementation Phases

### Phase 1: DCI Scanner Patterns (P1)
All three repos. Define and test 12+ DCI-specific patterns. This is the foundation -- everything else depends on being able to detect DCI abuse.

- vskill: `src/scanner/patterns.ts` -- add DCI patterns
- vskill-platform: `src/lib/scanner/patterns.ts` -- add DCI patterns
- specweave: `src/core/fabric/security-scanner.ts` -- add DCI patterns

### Phase 2: Trust Model + Data Layer (P1)
Platform only. Prisma schema migration, trust score computation logic, trust tier derivation.

- Schema migration for Skill, Submission, ScanResult
- Trust score engine: `src/lib/trust/trust-score.ts`
- Trust tier derivation: `src/lib/trust/trust-tier.ts`
- API updates to include trust data in responses

### Phase 3: Blocklist Auto-Propagation (P1)
Platform only. Wire up the SecurityReport resolution flow to create BlocklistEntry records.

- Event handler in report resolution endpoint
- Idempotency guard (skip if entry already exists)
- Admin UI confirmation

### Phase 4: Provenance & Hash Verification (P2)
Platform only. GitHub API integration for submitter identity verification and content hash tamper detection.

- Provenance verifier service
- Content hash recording at scan time
- Pre-publish hash comparison
- Trust score recomputation on provenance result

### Phase 5: CLI + UI Integration (P2)
Display trust tier and score in vskill CLI and platform web UI.

- CLI: `vskill install` and `vskill info` trust display
- Platform: Trust Center page updates, skill detail page badges
- Stats endpoint trust breakdown

## Testing Strategy

TDD mode (RED-GREEN-REFACTOR) for all new code:

- **Unit tests**: Each DCI pattern has positive (should match) and negative (should not match) test cases. Trust score computation has tests for each weight component and edge cases (blocked skills, missing data).
- **Integration tests**: Blocklist auto-propagation from report resolution. Provenance verification with mocked GitHub API responses.
- **Vitest mocking**: `vi.hoisted()` + `vi.mock()` for ESM. GitHub API mocked with `vi.fn()`.

## Technical Challenges

### Challenge 1: False positives on legitimate DCI blocks
**Solution**: The standard skill-memories DCI pattern (`for d in .specweave/skill-memories .claude/skill-memories "$HOME/.claude/skill-memories"; do p="$d/$s.md"; [ -f "$p" ] && awk ...`) is well-known. Add it as a safe-context pattern that suppresses DCI-abuse findings when the block matches the canonical lookup format.
**Risk**: Attackers could append malicious commands after the safe pattern. Mitigation: safe-context matching is per-command, not per-line -- if additional commands follow the safe pattern on the same line, findings are still raised.

### Challenge 2: GitHub API rate limits for provenance verification
**Solution**: Cache provenance results per submission (stored in `Submission.provenanceStatus`). Only re-verify when the submission is re-scanned. Use conditional requests (If-None-Match) where possible.
**Risk**: Rate limit exhaustion during bulk imports. Mitigation: Queue provenance checks with backoff, do not block the scan pipeline on provenance results.

### Challenge 3: Trust score migration for existing skills
**Solution**: Write a migration script that computes trust tier and score for all existing skills based on their current scan results and blocklist status. Skills with no scan results get T1, skills with passing tier1 get T2, etc.
**Risk**: Migration timeout on large datasets. Mitigation: Batch processing in chunks of 100 skills.
