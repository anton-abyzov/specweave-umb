# r/ClaudeAI draft

**Status:** DRAFT — post day-of launch or day-after.
**Best window:** Tuesday-Thursday afternoon ET.

---

## Title

I built a local skill manager for Claude Code (and 52 other agent platforms). Open source.

## Body

Hi r/ClaudeAI,

If you've been hand-managing your `~/.claude/skills/` folder and wishing it worked more
like a real package manager — that's exactly what I built.

**vSkill Desktop** gives you:

- A native Mac/Windows/Linux app to browse, install, and version skills
- Live SKILL.md editor with linting and autocomplete
- A/B evals so you can actually prove a skill makes Claude better — not just feel like it does
- A three-tier security scan before any install (52 patterns → blocklist → LLM intent)
- One install command works across Claude Code, Cursor, Copilot, Codex, Windsurf, plus 48 more

It's open source, MIT-licensed, and built local-first — no telemetry, no cloud sync unless you
opt in. The desktop app is Tauri + Node SEA so it's a real native binary, not an Electron
wrapper.

What it solves for Claude users specifically:

- **Discovery.** 1000+ skills in the registry, all scanned for malicious patterns. No more
  "is this random GitHub gist safe?"
- **Workflow.** Cmd-K palette opens skill search from anywhere, just like Linear/Raycast
- **Reproducibility.** Skills are versioned. A teammate can install the exact same set with
  one command (`vskill install -f vskill.lock`)
- **Multi-agent.** If you also use Cursor or Copilot for some workflows, the same skill
  ships to all of them — no copy-paste

Downloads at verified-skill.com/desktop. Source at github.com/anton-abyzov/vskill.

I'm the sole maintainer (Anton), happy to answer anything in the thread. Issues + PRs welcome.

## Posting rules check

- [ ] Confirm sub allows tool posts in the current rules
- [ ] No "buy now" framing — it's free + open source, so be explicit about that
- [ ] Pin a comment to the top with quick FAQ
