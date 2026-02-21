# Skills.sh Compatibility Gap Analysis

## 1. Agent Detection Comparison

### Detection Method
- **vskill**: Uses `which <binary>` (shell command detection)
- **skills.sh**: Uses `existsSync(~/.agent-dir/)` (directory presence detection)

**Recommendation**: Directory-based detection is more reliable for agents that don't install a binary (e.g., VS Code extensions like Cursor, Cline, Windsurf). Keep `which` as primary but add `existsSync` fallback for IDE-based agents.

### Agent Count
- **vskill**: 39 agents
- **skills.sh**: 50+ agents

### Missing Agents in vskill (11 agents from skills.sh)
| Agent | skills.sh ID | Note |
|-------|-------------|------|
| Cortex | cortex | New agent |
| Clawdbot | clawdbot | Claude Code fork |
| Aider | aider | Terminal AI assistant |
| Tabnine Chat | tabnine-chat | IDE plugin |
| Devin | devin | Cognition AI |
| Bolt.new | bolt-new | StackBlitz |
| v0 | v0 | Vercel |
| Kilo Code | kilo-code | ID mismatch (vskill: kilo) |
| GPT Pilot | gpt-pilot | Pythagora |
| Plandex | plandex | Terminal planner |
| Sweep | sweep | Sweep AI |

## 2. Folder Structure Comparison

Both tools use `.agents/skills/{name}/` as the canonical directory for universal agents. The symlink targets are identical.

**Gap**: No gap for universal agents.

## 3. Critical Path Discrepancy: Claude Code

| Tool | Claude Code Path |
|------|-----------------|
| vskill | `.claude/commands` |
| skills.sh | `.claude/skills` |

**This is the most critical discrepancy.** Skills installed by `npx skills` go to `.claude/skills/`, but vskill puts them in `.claude/commands/`. Claude Code itself reads from both directories, but cross-tool visibility breaks because:
- `vskill list` scans `.claude/commands/` only
- `npx skills list` scans `.claude/skills/` only

**Migration strategy**: Change vskill's Claude Code `localSkillsDir` from `.claude/commands` to `.claude/skills`. This is a one-line change. Existing users with skills in `.claude/commands` will still work since Claude Code reads both.

## 4. Lock File Interop

- **vskill**: Uses `vskill.lock` (JSON, at project root)
- **skills.sh**: Uses `.skill-lock.json` (JSON, at project root)

**Gap**: Neither tool reads the other's lock file. `vskill list` only reads `vskill.lock`.

**Recommendation**: In `vskill list`, also scan `.skill-lock.json` to show skills installed by `npx skills`. This is additive — no breaking changes.

## 5. Cross-Tool Visibility: npx skills -> vskill list

Skills installed by `npx skills add` go to `.claude/skills/`. Since vskill scans `.claude/commands/`, these are invisible.

**Fix**: Change Claude Code path to `.claude/skills/` (see section 3).

## 6. Cross-Tool Visibility: vskill add -> npx skills list

Skills installed by `vskill add` go to `.claude/commands/`. Since `npx skills list` scans `.claude/skills/`, these are invisible.

**Fix**: Same path change resolves this direction too.

## 7. Full Agent Diff

New agents to add to vskill (beyond the 11 missing):
- Consider adding `trae-cn` as a separate entry (already exists in vskill)
- Cortex and Clawdbot are the most notable new additions

## Draft Implementation Plan

### File: `src/agents/agents-registry.ts`
1. **Change Claude Code path**: `localSkillsDir: '.claude/commands'` -> `localSkillsDir: '.claude/skills'`
2. **Change globalSkillsDir**: `'~/.claude/commands'` -> `'~/.claude/skills'`
3. **Add 11 missing agents** from the diff table above
4. **Update TOTAL_AGENTS constant** and test expectations

### File: `src/commands/list.ts`
5. **Add `.skill-lock.json` reading** in `listSkills()` to show skills from both lock files
6. **Mark source** in output (show "skills.sh" vs "vskill" in the Source column)

### File: `src/agents/agents-registry.ts`
7. **Add directory-based detection fallback**: For agents without CLI binaries, check `existsSync(~/.agent-dir/)` as alternative detection method
