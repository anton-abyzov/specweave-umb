# 0245: External SAST Scanner Integration

## Problem

The vskill-platform scans skills with Tier 1 (37 regex patterns) and Tier 2 (LLM semantic analysis). These catch prompt injection, credential theft, and obfuscation but miss cross-function data flow vulnerabilities: command injection via `execSync(env_var)`, SSRF, and deep secret patterns (700+ types). External SAST tools (Semgrep, njsscan, Trufflehog) catch these but require filesystem + child_process, which Cloudflare Workers cannot provide.

## Solution

Add a Tier 1.5 external scanning layer using GitHub Actions as the compute backend. External scans run async after skill publication (non-blocking). Results are displayed per-provider on a security detail page. The CLI blocks install on CRITICAL findings with a link to the full report.

## User Stories

### US-001: External SAST Scanning Pipeline
As a platform operator, I want submitted skills to be automatically scanned by external SAST tools (Semgrep, njsscan, Trufflehog) so that cross-function vulnerabilities and deep secrets are detected.

**ACs:**
- [x] AC-US1-01: After a skill is published via Tier 1+2, external scans are dispatched via GitHub Actions repository_dispatch
- [x] AC-US1-02: GitHub Actions workflow clones the target repo and runs Semgrep, njsscan, and Trufflehog
- [x] AC-US1-03: Results are normalized to a common finding format and POSTed back to the platform via authenticated webhook
- [x] AC-US1-04: Results are stored in both Prisma (ExternalScanResult) and KV (fast reads)
- [x] AC-US1-05: If any provider finds CRITICAL issues, the skill is auto-blocked via BlocklistEntry

### US-002: Security Detail Pages
As a user, I want to see per-provider security scan results on a dedicated page so that I can assess a skill's safety before installing.

**ACs:**
- [x] AC-US2-01: `/skills/{name}/security` shows all provider results with verdict badges, scores, and finding counts
- [x] AC-US2-02: `/skills/{name}/security/{provider}` shows detailed findings (severity, rule, message, file:line)
- [x] AC-US2-03: Skill detail page (`/skills/{name}`) shows external scan summary with link to full report
- [x] AC-US2-04: Audits page (`/audits`) includes external scan columns per provider
- [x] AC-US2-05: Per-provider SVG badges at `/api/v1/skills/{name}/badge/{provider}`

### US-003: CLI Install Security Gate
As a developer, I want `vskill add` to check external scan results and block installation of skills with CRITICAL findings so that I don't install vulnerable skills.

**ACs:**
- [x] AC-US3-01: `vskill add` fetches `/api/v1/skills/{name}/security` before installing
- [x] AC-US3-02: If any provider has CRITICAL findings: print error, show report URL, exit code 1
- [x] AC-US3-03: If scans are PENDING: show informational message, proceed with install
- [x] AC-US3-04: `--force` flag overrides security blocks with warning
- [x] AC-US3-05: Network errors are non-fatal (best-effort check, don't block on API failure)

### US-004: Webhook Security and Hardening
As a platform operator, I want scan result webhooks to be authenticated and the system to handle failures gracefully.

**ACs:**
- [x] AC-US4-01: Webhook endpoint verifies HMAC-SHA256 signature on every request
- [x] AC-US4-02: Dispatches are deduplicated (skip if scan already PENDING/RUNNING for this skill)
- [x] AC-US4-03: Dispatches are rate-limited (max 100/hour)
- [x] AC-US4-04: PENDING scans older than 20 minutes are lazily timed out on read
- [x] AC-US4-05: Admin can re-trigger external scans for any published skill

## Out of Scope

- Socket.dev API integration (no public API for skill scanning)
- Snyk Code integration (requires org enablement, add later)
- CodeQL integration (complex setup, add later)
- Pre-publish blocking (external scans are post-publish async)

## Extended References

<!-- These files extend this spec. Load with: cat docs/architecture.md docs/providers.md docs/evidence.md -->
<!-- In Claude Code, use: @.specweave/increments/0245-external-sast-scanner-integration/docs/architecture.md -->

@docs/architecture.md
@docs/providers.md
@docs/evidence.md
