# r/LocalLLaMA draft

**Status:** DRAFT — post 24-48 hours after HN/PH launch to surf the wave.
**Best window:** Saturday or Sunday afternoon ET, when the sub is most active.

---

## Title

[Tool] vSkill Desktop — local-first skill marketplace for AI agents (works with Ollama, LM Studio, llama.cpp)

## Body

Hi r/LocalLLaMA,

I built vSkill because the AI-agent skill ecosystem has a real package-management problem
and I wanted a tool that doesn't ship my prompts off to a cloud just to manage them.

What it does:

- **Local-first.** The desktop app + the registry both run on your machine. Skills install
  to a local folder. Evals run against whatever model you point them at — Ollama, LM Studio,
  llama.cpp, vLLM, or a hosted Claude/GPT/Gemini key.
- **No telemetry.** Network access is on-demand and visible. The eval-server is a Node
  Single-Executable bundled inside the Tauri shell — same runtime as `npx vskill studio`,
  no extra daemon.
- **Three-tier security scan.** Every skill gets scanned for 52 known malicious patterns,
  cross-checked against a blocklist of known-bad authors, and the SKILL.md itself gets a
  small LLM-intent classification before install. You can run all three locally if your
  model can do classification.
- **Open source, MIT.** Source at github.com/anton-abyzov/vskill. Self-host the registry
  with a single CF Worker + D1.

What I'd love feedback on from this sub specifically:

1. The Ollama/LM Studio integration — currently auto-detects via known ports. Is that
   the right detection model, or should I require explicit config?
2. The eval harness uses streaming SSE for token-by-token output. Works well against
   Ollama's `/api/generate` stream, would love bug reports against vLLM or llama.cpp.
3. Local registry self-hosting — would you actually run your own, or is the public
   registry enough?

Downloads + screenshots at verified-skill.com/desktop. AppImage signed with GPG, works
on every distro I've tested (Ubuntu 22.04, Fedora 39, Arch, Pop!_OS).

Not affiliated with any of the LLM providers. Sole maintainer, would love issues + PRs.

## Posting rules check

- [ ] Flair: Tool / Resources (whichever the mods prefer that week)
- [ ] No "show HN cross-post" framing — sub hates that
- [ ] First comment ready with answers to the 3 likely first questions:
      "Why not just bash scripts?", "Is this another VSCode wrapper?", "Show me a benchmark"
- [ ] Be present in comments for the first 4 hours
