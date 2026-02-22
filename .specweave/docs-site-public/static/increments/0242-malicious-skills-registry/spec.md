# 0242: Malicious Skills Registry & Security Audits Dashboard

## Problem

Skills.sh has a public Security Audits dashboard (skills.sh/audits) showing combined results from Gen Agent Trust Hub, Socket, and Snyk. Our verified-skill.com platform lacks:

1. A public-facing security audits dashboard showing scan results
2. A malicious skills registry (blocklist) of known-dangerous skills
3. Prevention enforcement — blocking installation of known-malicious skills
4. External security provider integration (Gen, Socket, Snyk or similar)

The ClawHub incident proved that labeling alone is insufficient — 5 of the top 7 most-downloaded skills were malware despite being on a public platform. We need both transparency AND prevention.

## User Stories

### US-001: Public Security Audits Dashboard
As a developer evaluating skills, I want to see a public dashboard of all scanned skills with their security ratings, so I can make informed decisions before installing.

**Acceptance Criteria:**
- [x] AC-US1-01: Dashboard page at `/audits` shows all scanned skills with Tier 1 + Tier 2 results
- [x] AC-US1-02: Each skill shows scan score, severity breakdown (critical/high/medium/low), and verification tier reached
- [x] AC-US1-03: Table is sortable by name, score, date scanned, and status
- [x] AC-US1-04: Filterable by status (PASS, CONCERNS, FAIL, BLOCKED)
- [x] AC-US1-05: Blocked/malicious skills are visually distinct (red badge, strikethrough, or similar)

### US-002: Malicious Skills Registry (Blocklist)
As a platform operator, I want to maintain a public blocklist of known-malicious skills, so developers and other platforms can reference it.

**Acceptance Criteria:**
- [x] AC-US2-01: Public page at `/blocklist` listing all known-malicious skills with name, source, threat type, and discovery date
- [x] AC-US2-02: Admin API endpoint to add skills to blocklist with reason, evidence URL, and threat category
- [x] AC-US2-03: Blocklist is queryable via API: `GET /api/v1/blocklist?name=skill-name` returns blocked status
- [x] AC-US2-04: Blocklist entries include: skill name, source repo/registry, threat type (prompt injection, credential theft, etc.), discovery date, evidence links
- [x] AC-US2-05: Blocklist is continuously updated as new malicious skills are discovered across platforms

### US-003: Installation Prevention
As a developer using vskill CLI, I want to be blocked from installing known-malicious skills, so I'm protected even if I attempt to install directly.

**Acceptance Criteria:**
- [x] AC-US3-01: `vskill add` checks blocklist before installation
- [x] AC-US3-02: If skill matches blocklist entry, installation is refused with clear error message showing why it's blocked
- [x] AC-US3-03: Blocklist check runs against skill name AND content hash (to catch renamed copies)
- [x] AC-US3-04: Force-install flag (`--force`) available but shows prominent warning and requires explicit confirmation

### US-004: Cross-Platform Scanning
As a security researcher, I want to scan skills from other platforms (skills.sh, SkillsMP, etc.) and add results to our registry, so we build the most comprehensive blocklist.

**Acceptance Criteria:**
- [x] AC-US4-01: Admin can submit external skill URLs for scanning (GitHub repos, skills.sh URLs)
- [x] AC-US4-02: Scan results for external skills are stored and displayed on the audits dashboard
- [x] AC-US4-03: External skills that fail scanning are auto-added to the blocklist
- [x] AC-US4-04: Scan history preserves the original source URL for attribution

## Technical Notes

- Dashboard and blocklist are public pages (no auth required to view)
- Admin operations (adding to blocklist, triggering scans) require REVIEWER+ role
- Blocklist API should be lightweight and cacheable for CLI integration
- Consider seeding the blocklist with known malicious skills from ClawHub research (hightower6eu, Aslaep123, zaycv, aztr0nutzs actors)
- Future: integrate with external providers (Gen Agent Trust Hub, Socket, Snyk) as additional data sources

## Priority

HIGH — This is a key differentiator for verified-skill.com and directly supports the public narrative (YouTube video, blog posts) about why our platform exists.
