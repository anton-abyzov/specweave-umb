<!-- SW:META template="claude" version="3.0.0" sections="header,jev" -->

<!-- SW:SECTION:header version="3.0.0" -->
@AGENTS.md

# specweave: Claude Code notes

Everything shared by every tool is in AGENTS.md, imported above. Only Claude-specific notes belong here.

- Skills: `/sw-increment "title"`, `/sw-do`, `/sw-auto`, `/sw-review`, `/sw-done`, `/sw-handoff`, from `.claude/skills/`, so they load in cloud sessions too. With the `sw` plugin they are also `/sw:do` and so on.
- With the plugin, the SessionStart hook prints a short pickup; run `specweave pickup` for the next task's acceptance criteria.
- Use plan mode before writing a spec for anything bigger than a small fix.
<!-- SW:END:header -->

<!-- SW:SECTION:jev version="3.0.0" -->
Jev is enabled here; its rules are in the Jev section of AGENTS.md.
<!-- SW:END:jev -->

## Commands

| Action | Command |
|---|---|
| Build | TODO: not detected — fill in the build command |
| Test | TODO: not detected — fill in the test command |
| Lint | TODO: not detected — fill in the lint command |

If a cell still says TODO, fill it in from `package.json`/`Makefile` and commit; `specweave verify` runs these rows.

## Project notes

(architecture map, things agents get wrong here, recurring mistakes — keep it short)

## Skill Memories

<!-- Auto-captured by SpecWeave reflect. Edit or delete as needed. -->

### Team Lead
- **2026-03-03**: Agents in team contexts should NOT run /sw:done or /sw:grill themselves — team-lead handles centralized closure to prevent context overflow and enable parallel work
- **2026-03-03**: Team-lead MUST activate master increment (set metadata.json status to "active") BEFORE spawning agents. `specweave complete` silently exits on "planned" status — agents don't manage lifecycle transitions. Closure must retry on failure (max 2) rather than skip.

## Project Structure

- **Umbrella repo**: specweave-umb with repos under `repositories/anton-abyzov/`

## Manual Verification Gates

Ask user to manually verify: new UI flows, auth changes, payment flows, data migrations.
