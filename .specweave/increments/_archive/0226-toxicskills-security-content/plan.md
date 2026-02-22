# Plan: 0226-toxicskills-security-content

## Approach

Create two content pieces in the docs-site:

1. **Blog post** — SEO-optimized, developer-facing article about ToxicSkills. Structure: hook with stats → real attack examples → SpecWeave's response → CTA to try verified skills. Keep it under 1200 words for readability.

2. **YouTube script** — Structured for filming, with visual cues and a narrative arc. Structure: shocking opener → problem escalation → solution reveal → live demo concept → CTA.

## Key Decisions

- Blog goes in `blog/` (standard Docusaurus blog path)
- YouTube script goes in `drafts/` (not published to site, internal reference)
- Neither duplicates existing deep technical docs — they link to them
- Use data from `reports/scan-results.md` for SpecWeave's own PoC results
- Reference Snyk ToxicSkills study data already cited in existing docs

## File Locations

| Deliverable | Path |
|------------|------|
| Blog post | `repositories/anton-abyzov/specweave/docs-site/blog/2026-02-21-toxicskills-why-your-ai-agent-skills-need-verification.md` |
| YouTube script | `repositories/anton-abyzov/specweave/docs-site/drafts/youtube-toxicskills-script.md` |
