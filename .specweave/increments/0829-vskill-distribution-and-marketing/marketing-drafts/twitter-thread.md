# Twitter / X launch thread

**Status:** DRAFT — post day-of launch, 9-11 AM EST (per feedback memory).
**Length:** 8 tweets.
**Hashtags (last tweet only):** #AI #Tauri #Claude #OpenSource

---

## Tweet 1 (hook)

Just shipped vSkill Desktop — the package manager for AI agent skills.

Browse, install, and run skills locally on Mac, Windows, Linux.
Works with Claude, GPT, Llama, Gemini, Ollama.

Open source. No telemetry.

[ATTACH: hero screenshot or 5-second app launch GIF]

verified-skill.com/desktop

## Tweet 2 (the why)

Why I built it:

36.82% of AI agent skills have security flaws (Snyk).
And the rest? You can't tell if they actually improve the model — or just feel like they should.

vSkill fixes both: 3-tier security scan + built-in A/B evals.

[ATTACH: scan results UI screenshot]

## Tweet 3 (the architecture flex)

The interesting bit:

Tauri 2 shell (Rust, ~3 MB) + Node SEA sidecar (114 MB, contains the eval runtime).
Same Node code runs in `npx vskill studio` AND in the desktop app.
Cold launch: 1.5 s on Apple Silicon.

[ATTACH: architecture diagram]

## Tweet 4 (the cross-platform breadth)

53 agent platforms supported.

Claude Code, Cursor, Copilot, Codex, Windsurf, Zed, Gemini CLI, Ollama, LM Studio, llama.cpp,
Continue, Aider, Cody, plus 40 more.

One install command. Every agent.

[ATTACH: agent grid screenshot]

## Tweet 5 (the eval flex)

A/B evals you can actually trust:

— Stream pass/fail token-by-token via SSE
— Run against any model with an API key
— Run against local Ollama / LM Studio with zero config
— Show variance, not just averages

[ATTACH: eval results streaming GIF]

## Tweet 6 (the trust angle)

3-tier security scan before every install:

1. 52 static patterns (known exfil, RCE, prompt-injection vectors)
2. Author blocklist (cross-checked against known-bad GitHub orgs)
3. LLM-intent classifier on the SKILL.md text itself

No `--skip-scan` flag. By design.

## Tweet 7 (founder voice)

I'm the sole maintainer.

Built this because every team I worked with was hand-managing skills like it was 2003 and
shell scripts.

If you've ever copy-pasted a SKILL.md folder into a new project and prayed — this is for you.

## Tweet 8 (CTA + hashtags)

Get vSkill Desktop:
🟦 Mac, Windows, Linux: verified-skill.com/desktop
📦 npm: npx vskill@latest studio
⭐ Source (MIT): github.com/anton-abyzov/vskill

#AI #Tauri #Claude #OpenSource

[ATTACH: small product logo]

---

## Quote-tweet seeds (DO NOT post these as your own — share with launch supporters)

- "Finally, a real package manager for Claude skills. The A/B eval bit is the killer feature."
- "Tauri + Node SEA in one binary is wild. 1.5 s cold launch, native menu bar tray, MIT."
- "The 3-tier security scan alone is worth installing this. 36% of skills have flaws — yikes."

## Posting checklist

- [ ] Schedule for 9-11 AM EST (Saturday slot if launching same week, weekday otherwise)
- [ ] Pin tweet 1 to profile for 48 hours
- [ ] Reply to first 20 quote-tweets / replies within 30 min
- [ ] DO NOT use auto-engagement bots — Twitter shadowbans aggressively in 2026
