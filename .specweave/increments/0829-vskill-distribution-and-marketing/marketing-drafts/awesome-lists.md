# Awesome-list PR queue

**Status:** DRAFT — submit PRs the week of launch.
**Pattern:** one PR per list, plain entry, no astroturfing.

---

## Target lists

### Tier 1 (must-do)

| List | Repo | Section | PR title |
|------|------|---------|----------|
| awesome-claude | langgptai/awesome-claude-prompts (or current canonical) | Tools | Add vSkill — local skill marketplace for Claude agents |
| awesome-ai-tools | mahseema/awesome-ai-tools | Developer Tools / Skills | Add vSkill — open-source skill manager (MIT, 53 agent platforms) |
| awesome-tauri | tauri-apps/awesome-tauri | Apps | Add vSkill — native skill marketplace for AI agents (Tauri 2 + Node SEA) |
| awesome-llm | Hannibal046/Awesome-LLM | Tools | Add vSkill — package manager for LLM agent skills |

### Tier 2 (high-leverage but lower fit)

| List | Repo | Section | Notes |
|------|------|---------|-------|
| awesome-developer-tools | jondot/awesome-developer-tools | AI/ML | Mention skills + evals angle |
| awesome-rust | rust-unofficial/awesome-rust | Applications | Tauri shell qualifies, mention sidecar architecture |
| awesome-electron-alternatives | (search github) | — | If exists, lead with the size + speed numbers |

### Tier 3 (nice to have)

- awesome-ollama — relevant because of local Ollama integration
- awesome-lmstudio — same
- awesome-self-hosted — local registry self-hosting angle

---

## Standard PR description template

```markdown
### Adding vSkill

**Repo:** https://github.com/anton-abyzov/vskill
**Description:** Local-first skill marketplace for AI agents. Native Mac/Windows/Linux app with three-tier security scan and built-in A/B evals. Works with 53 agent platforms (Claude Code, Cursor, Copilot, etc.). MIT-licensed.

**Why this fits the list:** [customize per list — emphasize the angle that matches the list's focus]

**Maintenance:** Sole maintainer (anton-abyzov), actively shipping releases since [LAUNCH_DATE].
**Stars at submission:** [fill in]
**License:** MIT
```

## Anti-patterns to avoid

- DO NOT submit PRs to multiple lists in the same hour from the same account — looks like spam
- DO NOT add vSkill to your own awesome lists and then PR those into other lists
- DO NOT pad descriptions with marketing speak; awesome-list maintainers reject those fast
- DO NOT submit if vSkill has fewer than 100 stars — wait for organic traction first

## Tracking

After PR submission, log here:

| Date | List | PR # | Status | Merged? |
|------|------|------|--------|---------|
| | | | | |
