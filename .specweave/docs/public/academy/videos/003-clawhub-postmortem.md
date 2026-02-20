# Video 003: ClawHub Is Dead. The Problem Isn't.

## Video

**YouTube**: [Link pending - will be added after upload]

**Duration**: ~15-18 minutes

---

## Summary

ClawHub — the largest community skill marketplace for Claude Code — was shut down after security researchers discovered hundreds of malicious skills. This video walks through what happened, what the attacks looked like, why it matters even now that ClawHub is gone, and why we built verified-skill.com.

---

## Visual Evidence (Screenshots)

This video references three key screenshots. All are from public sources and security research.

### Screenshot A: Headlines

News headlines from February 2026:
- "Researchers Find 341 Malicious ClawHub Skills Stealing Data from OpenClaw Users"
- The Verge: "OpenClaw's AI 'skill' extensions are a security nightmare" (Emma Roth, Feb 4, 2026)
- "Hundreds of Malicious Skills Found in OpenClaw's ClawHub"

Source: Aikido Security / The Verge

### Screenshot B: Single Threat Actor Profile

ClawHub user profile `@hightower6eu` showing 9 published skills — ALL malicious:
- Autoupdater Skills (131 downloads)
- Polymarket Tranding [sic] (115 downloads)
- Clawhub (109 downloads)
- Skills Update (640 downloads)
- Polymarket Automatic Trading Bot (911 downloads)
- Clawhub (1,364 downloads)
- Skills Auto-Updater (951 downloads)
- Polymarket Trading Bot (1,293 downloads)
- Clawhub (1,393 downloads)

Orange annotation: "All of these are malicious"

### Screenshot C: Top Downloads Were Malicious

ClawHub Skills library sorted by downloads. The most-downloaded skills on the entire platform are flagged "Malicious!":
- Clawhub `/clawhubcli` — 1,399 downloads — **Malicious!**
- Clawhub `/clawhub` — 1,368 downloads — **Malicious!**
- Polymarket Trading Bot `/poly` — 1,297 downloads — **Malicious!**
- moltbook-interact `/moltbook-interact` — 1,141 downloads (unmarked)
- Skills Auto-Updater `/updater` — 956 downloads — **Malicious!**
- Polymarket Automatic Trading Bot `/polym` — 921 downloads — **Malicious!**
- Capability Evolver `/capability-evolver` — 695 downloads (unmarked)

5 of the top 7 most-downloaded skills on ClawHub were malicious.

### Screenshot D: Live Malicious Skill on skills.sh (Post-ClawHub)

skills.sh skill detail page for `capability-evolver` by `autogame-17`:
- URL: skills.sh/autogame-17/capability-evolver/capability-evolver
- Described as a "meta-skill" that lets agents "inspect their own runtime history, identify failures, and autonomously write new code or update their own memory"
- Tagline: "Evolution is not optional. Adapt or die."
- 55 weekly installs — still actively being downloaded
- First seen: Feb 1, 2026
- Security Audits sidebar:
  - Gen Agent Trust Hub: **FAIL**
  - Socket: **FAIL**
  - Snyk: **WARN**

This proves the problem persists beyond ClawHub. A skill that FAILS two independent security audits and gets a WARN from a third is still live, still installable, and still getting 55 downloads per week on skills.sh — the largest active skill marketplace.

### Screenshot E: skills.sh Security Audits Dashboard

The skills.sh/audits page — a combined security audit results table showing all skills with ratings from three providers (Gen Agent Trust Hub, Socket, Snyk):

| # | Skill | Org | Gen | Socket | Snyk |
|---|-------|-----|-----|--------|------|
| 1 | find-skills | vercel-labs/skills | SAFE | 0 ALERTS | MED RISK |
| 2 | vercel-react-best-practices | vercel-labs/agent-skills | SAFE | 0 ALERTS | LOW RISK |
| 3 | web-design-guidelines | vercel-labs/agent-skills | SAFE | 0 ALERTS | MED RISK |
| 4 | remotion-best-practices | remotion-dev/skills | SAFE | 0 ALERTS | MED RISK |
| 5 | frontend-design | anthropics/skills | SAFE | 0 ALERTS | LOW RISK |
| 6 | vercel-composition-patterns | vercel-labs/agent-skills | SAFE | 0 ALERTS | LOW RISK |
| 7 | agent-browser | vercel-labs/agent-browser | SAFE | 0 ALERTS | HIGH RISK |
| 8 | skill-creator | anthropics/skills | SAFE | 0 ALERTS | LOW RISK |
| 9 | browser-use | browser-use/browser-use | **CRITICAL** | **1 ALERTS** | **CRITICAL** |

Key observation: Even official skills from Vercel and Anthropic get MED/HIGH RISK from Snyk — showing the detection-vs-prevention gap. And `browser-use` (#9) is CRITICAL across all three providers yet still appears in the list.

This is the model we should match and improve upon: multi-provider audit transparency, but with the addition of a **blocklist** that prevents installation of known-malicious skills entirely.

---

## Script

### SCENE 1: Hook — ClawHub Is Gone (0:00 - 1:30)

[Screen: Black. White text fades in: "February 2026"]

**NARRATOR:**

"ClawHub is dead."

[Pause. Beat.]

"The largest community-run skill marketplace for Claude Code — shut down. But before it went dark, security researchers found something that should concern every developer using AI agents."

[SCREEN: Show Screenshot A — the headlines]

"Researchers Find 341 Malicious ClawHub Skills Stealing Data from OpenClaw Users. The Verge called it 'a security nightmare.' And Aikido Security confirmed: hundreds of malicious skills were found in OpenClaw's ClawHub."

"These aren't hypothetical vulnerabilities. These are real attacks, with real download counts, targeting real developers. And here's the thing — ClawHub being shut down doesn't make the problem go away. It makes it harder to track."

[SCREEN: Transition to SpecWeave logo + video title]

---

### SCENE 2: What Was ClawHub? (1:30 - 3:00)

[Screen: ClawHub homepage screenshot, then browser showing the skill library]

**NARRATOR:**

"For context — ClawHub was a community marketplace where anyone could publish skills for Claude Code. Skills are markdown files that tell AI agents how to behave. They can execute shell commands, make network requests, read your files — whatever the agent has permission to do."

"Think of it like npm for AI agents. Anyone could publish. Anyone could install. Minimal review. No automated security scanning."

"And just like early npm — it got exploited."

[SCREEN: Show the transcript quote from security researcher Paul]

"Here's what security researcher Paul described in a recent interview:"

[On-screen text, clean typography:]

> "They basically ask the user — it's kind of like ClickFix. The skills say, 'Hey, if you want to talk to Polymarket, you have to download this Polymarket authentication tool.' You download it. It's actually malware. It's just a string in the first couple of lines that says curl this or download from GitHub."

"Simple social engineering. A skill tells your AI agent: download this tool. The agent downloads it. The tool is malware. No sandboxing. No verification. No warning."

---

### SCENE 3: The Evidence — One Threat Actor (3:00 - 5:00)

[SCREEN: Show Screenshot B — @hightower6eu profile]

**NARRATOR:**

"Let me show you what this looked like in practice."

"This is the ClawHub profile of a user called hightower6eu. Nine published skills. Every single one of them — malicious."

[Highlight each skill card as they're named]

"Autoupdater Skills. Polymarket Tranding — yes, with a typo. Clawhub. Skills Update. Polymarket Automatic Trading Bot. Another Clawhub clone. Skills Auto-Updater. Polymarket Trading Bot. And yet another Clawhub copy."

"Look at the pattern. Three strategies in one profile:"

[SCREEN: Animated list]

"**One: Platform impersonation.** Multiple skills named 'Clawhub' — mimicking the platform itself. A developer looking for ClawHub's own tooling installs the attacker's version instead."

"**Two: Financial bait.** Polymarket trading bots. Crypto developers are prime targets — they're likely to have high-value API keys and wallet credentials on their machines."

"**Three: Auto-updater trojans.** Skills called 'Autoupdater' and 'Skills Update' that promise to keep your tools current. Instead, they run malicious code with your full shell permissions."

"And this was just ONE account. One threat actor. Publishing openly. With no review process stopping them."

---

### SCENE 4: The Download Numbers (5:00 - 7:00)

[SCREEN: Show Screenshot C — Skills library sorted by downloads]

**NARRATOR:**

"Now here's the part that should really concern you."

"This is the ClawHub skill library, sorted by downloads. The most popular skills on the entire platform."

[Pan slowly down the list]

"Clawhub CLI — 1,399 downloads — Malicious."

"Clawhub — 1,368 downloads — Malicious."

"Polymarket Trading Bot — 1,297 downloads — Malicious."

"moltbook-interact — 1,141 downloads — the one that's NOT marked malicious."

"Skills Auto-Updater — 956 downloads — Malicious."

"Polymarket Automatic Trading Bot — 921 downloads — Malicious."

[SCREEN: Red highlight overlay on the stats]

"Five of the top seven most-downloaded skills on ClawHub were malicious. The platform's most popular content was malware."

"These aren't skills nobody installed. These had hundreds, over a thousand downloads each. Real developers, running real AI agents, executing malicious instructions on their machines."

[Beat]

"And the platform had no mechanism to flag them. As the security researcher described:"

[On-screen quote:]

> "Before, when you authenticated into ClawHub, there was no way to label a skill as malicious. Literally no way. I made a PR to delete 400 malicious packages. Their AI closed it and said, 'This is a copy of our database, this isn't being used.'"

"An AI rejected the security fix. You can't make this up."

---

### SCENE 5: Why This Still Matters (7:00 - 9:00)

[SCREEN: "ClawHub is closed." crossed out. Then: "The problem isn't."]

**NARRATOR:**

"ClawHub shut down. Problem solved, right?"

[Beat]

"No. And here's why."

"**First** — the malicious skills didn't disappear. They were copied. Forked. Republished. The same threat actors operate across multiple platforms. As Paul put it:"

[On-screen quote:]

> "There's a room in North Korea right now that all they're doing is figuring out how to drop the same payloads they're using in npm and GitHub into these skills."

"ClawHub was just one marketplace. Skills.sh has over 59,000 skills. SkillsMP has over 96,000. There are at least ten competing registries. None of them share a security standard."

"**Second** — the attack surface hasn't changed. Skills still run with your full shell permissions. There is still no universal sandboxing. The agent still can't distinguish between a legitimate instruction and a malicious one."

"**Third** — and this is the critical insight — skills are MORE dangerous than npm packages. Let me explain why."

[SCREEN: Comparison diagram]

"When you install a malicious npm package, it can run commands through pre-install and post-install scripts. That's the attack surface. It's scoped."

"A malicious skill? It sits inside your AI agent. The agent already has access to your shell, your files, your environment variables, your SSH keys. There's a pre-existing trust relationship. The skill inherits ALL of those permissions."

[On-screen quote from Paul:]

> "You're inside Claude, right? You've probably already given it access to things. So now you drop this malicious skill that can do all kinds of stuff. Because of that pre-existing set of permissions and trust that you've built with that agent — it's ultimately going to have more impact than npm."

"This is why it's worse than npm. Not in scale — the npm ecosystem is huge and decades old. But in impact per attack. One malicious skill, inside an agent with your full permissions, can do more damage than a hundred malicious npm packages."

---

### SCENE 6: What We Found — The Attack Taxonomy (9:00 - 10:30)

[SCREEN: Attack type cards appearing one by one]

**NARRATOR:**

"Based on the ClawHub evidence and our own analysis, here are the attack types we've documented:"

"**Prompt injection** — 91% of malicious skills use it. Hidden instructions buried in markdown that hijack the agent's behavior. The developer sees a normal response. The attacker gets your source code."

"**Credential exfiltration** — base64-encoded commands disguised as setup scripts. One HTTP request sends your AWS keys, API tokens, or wallet credentials to the attacker."

"**Social engineering via skills** — what Paul calls 'ClickFix.' The skill says 'download this authentication tool.' The tool is malware. The agent follows the instruction because that's what skills tell it to do."

"**Platform impersonation** — skills named 'Clawhub' that mimic the platform itself. Typosquatting at the skill level."

"**Auto-updater trojans** — skills that promise to keep your tools current but instead run malicious code on a schedule. The cron job from hell."

"**Reverse shells** — SSH backdoors that give attackers persistent remote access to your machine."

"**Overlay attacks** — malicious JavaScript that pops open a login screen to harvest your credentials."

"Every single one of these was found in the wild. On a platform that developers were actively using."

---

### SCENE 6.5: The Industry Response — And Its Limits (10:30 - 12:00)

[SCREEN: Show Screenshot D — capability-evolver on skills.sh with security audit badges]

**NARRATOR:**

"Now, to be fair — the industry is starting to respond. This is skills.sh, the largest active skill marketplace. And look at the right sidebar."

[Highlight the Security Audits section]

"Security Audits. Gen Agent Trust Hub: FAIL. Socket: FAIL. Snyk: WARN. Three independent security providers are now scanning skills on this platform."

"This is good. This is progress. After the ClawHub disaster, Vercel — which runs skills.sh — partnered with Gen Digital, Socket, and Snyk to add automated security audits. Every skill now gets scanned by all three providers."

[SCREEN: Brief explainer cards for each provider]

"Gen Agent Trust Hub does content analysis, URL verification, antivirus scanning, and AI-powered threat detection. Socket evaluates supply chain risk and vulnerability scoring. Snyk checks for prompt injection, data exfiltration patterns, and dangerous dependencies."

"But here's what I want you to notice about this screenshot."

[SCREEN: Zoom to the skill title and weekly installs]

"This skill — Capability Evolver — FAILS two security audits and gets a WARNING from the third. And it still has 55 weekly installs. It's still live. Still downloadable. Still being installed by developers every week."

[Beat]

"The audits are there. The information is there. But the skill is still available. The platform shows you a warning — it doesn't stop you from installing. It's like a nutrition label on poison: informative, but not protective."

"And it's not just this one skill."

[SCREEN: Show Screenshot E — skills.sh/audits dashboard]

"This is skills.sh's new Security Audits page. A combined view of all skills with ratings from Gen Agent Trust Hub, Socket, and Snyk. This is transparency — and it's a real step forward."

"But look at the data. Even official skills from Vercel and Anthropic show MED RISK or HIGH RISK from Snyk. And skill number nine — browser-use — is CRITICAL across ALL THREE providers. Yet it's still listed. Still installable."

"This is the gap between DETECTION and PREVENTION. Skills.sh detects the risk and labels it. Our platform — verified-skill.com — prevents it. A skill that fails verification never reaches the registry. You can't install what doesn't pass."

"And we're going further. We're building a public malicious skills registry — a blocklist of every known-malicious skill we discover through scanning. Not just our own submissions, but skills we find across other platforms. If it's known-malicious, it's blocked. Period. You can't install it even if you try."

"Detection is step one. Prevention is the goal. A public blocklist is the safety net."

---

### SCENE 7: Why We Built Verified Skill (12:00 - 14:30)

[SCREEN: verified-skill.com landing page]

**NARRATOR:**

"This is why we built verified-skill.com."

"Not because ClawHub was broken. Because the PATTERN is broken. Every skill marketplace will face this same problem. The question is whether they face it before or after developers get compromised."

[SCREEN: Three-tier pipeline animation]

"Our platform runs every submitted skill through a three-tier verification pipeline."

"**Tier 1: Automated Pattern Scanning.** 37 deterministic security checks across 8 categories — command injection, data exfiltration, privilege escalation, credential theft, prompt injection, filesystem access, network access, and code execution. Each pattern has a severity level: critical, high, or medium. A score below 50 fails immediately."

"**Tier 2: LLM Intent Analysis.** An AI judge — Llama 3.1 70B — analyzes the skill's INTENT, not just its patterns. This catches what regex can't: social engineering, indirect prompt injection, subtle data flows that look benign individually but are malicious in combination."

"**Tier 3: Human Review.** A security expert with admin credentials reviews the skill manually. Confirms it does what it claims. Nothing more, nothing less. The reviewer's decision is recorded in an immutable audit trail — reviewer ID, timestamp, reason."

[SCREEN: State machine diagram]

"Every submission follows a strict state machine: RECEIVED, scanning, results, approval or rejection, publication. Every state transition is logged. Every decision is auditable. There is no way to skip a step."

"And here's what ClawHub didn't have: a way to mark things as malicious. On our platform, skills can be rejected at any tier. Admins can pull published skills. The audit trail is permanent."

[SCREEN: vskill.lock example]

"On the client side, every installed skill gets a lockfile entry — SHA hash of the content, scan date, verification tier, installation scope. If a skill's content changes, the diff is scanned before the update is applied."

"This is what responsible skill infrastructure looks like."

---

### SCENE 8: The Bigger Picture (14:30 - 15:30)

[SCREEN: Timeline — npm (2010), PyPI (2003), Docker Hub (2013), Skills (2025)]

**NARRATOR:**

"We've seen this movie before. npm launched in 2010. It took eight years and the event-stream incident before npm audit existed. PyPI has been around since 2003 — malicious packages are STILL uploaded daily. Docker Hub had cryptominer images for five years before scanning was added."

"Every ecosystem follows the same arc: explosive growth, no security, major incident, retroactive tooling. By the time the tooling arrives, the ecosystem is too large to fully secure."

"ClawHub was the skills ecosystem's event-stream moment. The question is whether we learn from it — or wait for the next one."

"ClawHub is gone. Other marketplaces are still growing. The threat actors haven't stopped. The attack techniques are documented and public. And the stakes — inside an AI agent with your shell permissions — are higher than npm ever was."

---

### SCENE 9: What You Should Do (15:30 - 17:00)

[SCREEN: Numbered list]

**NARRATOR:**

"Three things you can do today."

"**One**: Audit your installed skills. If you installed anything from ClawHub before it shut down, remove it. Run `npx vskill verify` on any skill files in your project."

"**Two**: Don't install skills from unverified sources. If a marketplace doesn't show you exactly what security checks a skill has passed, treat every skill as potentially malicious."

"**Three**: Use verified-skill.com. Every skill on our platform has been through automated scanning, AI-powered intent analysis, and — for certified skills — human review. The methodology is public. The audit trail is permanent. Trust is provable."

[SCREEN: Final card]

"ClawHub showed us what happens when you build a skill marketplace without security. We built verified-skill.com so the next marketplace doesn't have to learn that lesson the hard way."

"Because the next ClawHub is already being built. And the attackers are already waiting."

[End card: verified-skill.com + SpecWeave logo]

---

## Key Concepts

### ClawHub Postmortem
ClawHub was the largest community skill marketplace for Claude Code. It was shut down after security researchers discovered 341+ malicious skills. At its peak, 5 of the top 7 most-downloaded skills were malicious.

### Skills vs npm — Why Skills Are Worse
npm packages execute in a sandboxed JavaScript runtime. Skills execute inside an AI agent that already has shell permissions, file access, and network capabilities. The pre-existing trust relationship amplifies the impact of each attack.

### Three-Tier Verification
Verified-skill.com's defense model: automated pattern scanning (37 checks) + LLM intent analysis (Llama 3.1 70B) + human expert review. Every state transition is audited.

### The Persistence Problem
ClawHub's closure didn't eliminate the threat. The same threat actors operate across multiple registries. The attack techniques are public. The skills ecosystem needs platform-level security, not platform-specific patches.

---

## Quick Reference

| Term | Definition |
|------|------------|
| ClawHub | Shut-down community skill marketplace for Claude Code |
| ClawHavoc | Campaign distributing 335+ trojan packages via ClawHub |
| hightower6eu | Threat actor with 9 malicious skills on ClawHub (all impersonation/crypto bait) |
| ToxicSkills | Snyk's Feb 2026 security audit — 36.82% of skills had flaws |
| verified-skill.com | SpecWeave's verified skill platform with 3-tier pipeline |
| vskill.lock | Client-side lockfile tracking SHA, scan date, and verification tier |

---

## Related Videos

- **Previous**: [002 - ToxicSkills Security](./002-toxicskills-security.md)
- **Next**: [004 - TBD]
- **See also**: [Why Verified Skill Matters](../../guides/why-verified-skill-matters.md)

---

## Questions?

- Visit [verified-skill.com](https://verified-skill.com)
- Read the [security landscape analysis](https://spec-weave.com/docs/guides/skills-ecosystem-security)
- Open an issue on [GitHub](https://github.com/anton-abyzov/specweave)
