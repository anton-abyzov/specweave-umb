# Increment 0226: ToxicSkills Security Content (Marketing + YouTube)

## Overview

Create public marketing content referencing Snyk's ToxicSkills research (February 2026) to motivate adoption of SpecWeave's verified skill ecosystem. Two deliverables: a blog post for the docs-site and a YouTube video script.

**Existing deep technical docs** (NOT in scope — already exist):
- `docs/skills/skills-ecosystem-security.md` — full security landscape
- `docs/skills/verified-skills.md` — 3-tier standard
- `docs/guides/why-verified-skill-matters.md` — ClawHub case study
- `docs/skills/secure-skill-factory-standard.md` — full RFC

**This increment creates** approachable, marketing-oriented content that drives traffic to those technical pages.

---

## User Stories

### US-001: Blog Post — "36% of AI Agent Skills Have Security Flaws"

**As a** developer discovering SpecWeave through search or social media,
**I want** an accessible blog post explaining the ToxicSkills threat and how SpecWeave addresses it,
**So that** I understand the risk and am motivated to use verified skills.

**Acceptance Criteria**:
- [x] AC-US1-01: Blog post exists at `blog/2026-02-21-toxicskills-why-your-ai-agent-skills-need-verification.md`
- [x] AC-US1-02: Post references Snyk ToxicSkills study with specific data (3,984 skills, 36.82% flaw rate, 76 malicious)
- [x] AC-US1-03: Post includes SpecWeave's scan results from PoC (75% Tier 1, 100% combined)
- [x] AC-US1-04: Post links to existing deep-dive docs (ecosystem security, verified skills standard)
- [x] AC-US1-05: Post follows existing blog format (frontmatter with slug, authors, tags, truncate marker)
- [x] AC-US1-06: Post uses professional tone without excessive emoji (matches existing blog style)

### US-002: YouTube Script — "Your AI Agent Skills Might Be Malware"

**As a** content creator preparing a YouTube video about AI agent security,
**I want** a structured script with clear sections, talking points, and visual cues,
**So that** I can produce a compelling 6-8 minute video.

**Acceptance Criteria**:
- [x] AC-US2-01: Script exists at `docs-site/drafts/youtube-toxicskills-script.md`
- [x] AC-US2-02: Script includes intro hook, problem statement, data, solution, and CTA sections
- [x] AC-US2-03: Script references specific numbers from ToxicSkills study and SpecWeave PoC
- [x] AC-US2-04: Script includes visual/screen cues (e.g., "[SHOW: table of scan results]")
- [x] AC-US2-05: Script targets 6-8 minute runtime (~1000-1200 words spoken)
