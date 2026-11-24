# New page: "How Private Skills Work" — `/private-skills` (was /paid-skills)
*CORRECTED 2026-07-01 per Anton: there is NO paid-skills marketplace. The paid model = enterprises pay for storing their skills in vskill infrastructure, secured and scanned. No selling, no revenue share, no platform fees.*

*Full copy draft, ready to implement in vskill-platform. Everything below describes SHIPPED functionality (0874/0826).*

---

## Hero

**H1:** Your team's skills. Stored, secured, scanned.

**Sub:** Private skill hosting for the SKILL.md standard. Your internal runbooks, standards, and workflows live in an isolated tenant, pass a 3-tier security scan on every version, and install into Claude Code, Cursor, Copilot, and 50+ agents with one command.

**CTA row:** [Become a founding design partner →](calendar link) · [See pricing](/pricing)

---

## The problem strip

"Your engineers already share CLAUDE.md files, Cursor rules, and skills — over Slack, gists, and git repos. Nobody scans them. Nobody versions them. Nobody knows what's installed where." (Snyk: prompt injection in 36% of public skills.)

## How it works (4 steps, one screenshot each)

1. **Create & test in Skill Studio** — author in plain English, benchmark against any LLM, prove the skill works with A/B evals.
   *Screenshot: Studio authoring view with eval results.*
2. **Publish privately** — pick 🔒 Private in the publish drawer. Every version passes the 3-tier scan: 52 security patterns → malware blocklist → LLM intent analysis.
   *Screenshot: Publish drawer with PUBLIC/PRIVATE chooser.*
3. **We store and secure it** — your skills live in your org's isolated tenant on our infrastructure: default-deny from the public registry, member roster, exportable audit log (1-year retention).
   *Screenshot: sidebar with "🔒 Private (N) / 🌐 Public (N)" grouping + org audit log.*
4. **Your engineers install with one command** — `vskill install org/skill` delivers the scanned artifact and auto-updates on each newly scanned version, across 53 agents.
   *Screenshot: CLI install with "Verified ✓" output.*

## Why not just a git repo? (comparison table)

| | Git-repo skill sharing | verified-skill.com private hosting |
|---|---|---|
| Security scan per version | ❌ trust on read | ✅ 52 patterns + blocklist + LLM intent |
| Storage | your repo, your problem | ✅ isolated tenant on our infrastructure |
| Versioning | ❌ SHA-pinning hacks | ✅ semver + update notifications |
| Visibility | ❌ | ✅ what's installed, where, by whom + audit log |
| Reach | Claude-only patterns | ✅ 53 agents from one artifact |

## What the scan covers (trust strip)

52 static security patterns · known-malware blocklist · LLM intent analysis · re-scanned on every new version → link to `/verification` methodology page with a full sample scan report.

## Pricing (link /pricing)

Free — unlimited public skills · **Pro $20/mo — private skill storage from your private GitHub repos** · **Team $30/seat/mo (min 3) — org-wide: shared tenant, member roster, audit log** · Enterprise — SSO, dedicated support, custom contract.

## FAQ (accordions)

- Where exactly are private skills stored? (isolated org tenant; never appears in the public registry — default-deny at the data layer)
- Who can see our skills? (only your org members; enforced at every API route; audit log records access)
- What happens when a scan fails? (version stays unpublished; you get the findings report)
- Can we self-host instead? (MIT-licensed; desktop app + studio runtime self-hostable — the hosted tier is for teams that want us to run, secure, and scan it)
- Which agents are supported? (53-agent list)
- SSO / SOC 2? (Enterprise tier; SOC 2 evidence collection in progress — wording stays "reduces risk", never "guarantees safe")

## Final CTA

"Become a founding design partner — white-glove migration of your existing skill repo, flat founder pricing for year one, direct line to the founder." → calendar link, not a form.

---

# Supporting assets (unchanged)

**Captured (live site, 1440px, scratchpad/screenshots/):** home.png · pricing.png · desktop.png · docs-studio.png
**Still to capture (local Studio run):** publish drawer w/ PrivacyChooser · PaywallModal · private/public sidebar · CLI verified-install output · My Queue statuses

# Explainer video (60–90s) — storyboard from real screenshots
1. (0–8s) Hook: "Your engineers' AI agents run skills nobody has scanned."
2. (8–25s) Studio authoring + eval run (reuse 0862 lifecycle footage).
3. (25–40s) Publish drawer → 🔒 Private → scan pass with findings report.
4. (40–55s) `vskill install` → Verified ✓ → same skill in Claude Code AND Cursor.
5. (55–75s) Org tenant view (audit log) + pricing card. CTA: "founding design partners — verified-skill.com/private-skills".
Production: HyperFrames over real captures; Kokoro TTS or own VO; reuse yEg46Ybh4Yk's format.
