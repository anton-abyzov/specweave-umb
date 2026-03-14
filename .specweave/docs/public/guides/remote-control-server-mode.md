---
sidebar_position: 42
title: Remote Control Server Mode & Spawn Options
---

# Remote Control Server Mode & Spawn Options

Use Claude Code's Remote Control server mode to run multiple concurrent sessions from a single process, with configurable spawn strategies for team and parallel workflows.

## Overview

Remote Control connects [claude.ai/code](https://claude.ai/code) or the Claude mobile app to a Claude Code session running on your machine. **Server mode** (`claude remote-control`) extends this by acting as a dedicated session host that can spawn multiple concurrent sessions on demand.

This is particularly useful for SpecWeave workflows where you want to:

- Run `/sw:auto` from your phone while away from your desk
- Spawn parallel sessions for multi-increment work
- Keep a persistent session server running on a dev machine or VM

## Requirements

- Claude Code **v2.1.51+** (`claude --version`)
- **Pro, Max, Team, or Enterprise** plan (Team/Enterprise admins must enable Claude Code in [admin settings](https://claude.ai/admin-settings/claude-code))
- Authenticated via `claude` → `/login`
- Workspace trust accepted (run `claude` in your project directory at least once)

---

## Starting Server Mode

Navigate to your project directory and run:

```bash
claude remote-control
```

The process stays running in your terminal, waiting for remote connections. It displays a session URL and you can press **spacebar** to show a QR code for quick mobile access.

### Server Mode Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--name "My Project"` | Custom session title visible in the session list at claude.ai/code | Auto-generated |
| `--spawn <mode>` | How concurrent sessions are created (see [Spawn Modes](#spawn-modes)) | `same-dir` |
| `--capacity <N>` | Maximum number of concurrent sessions | `32` |
| `--verbose` | Show detailed connection and session logs | Off |
| `--sandbox` | Enable sandboxing for filesystem and network isolation | Off |
| `--no-sandbox` | Explicitly disable sandboxing | (default) |

### Examples

```bash
# Basic server with a custom name
claude remote-control --name "SpecWeave Dev"

# Server with git worktree isolation and max 8 sessions
claude remote-control --spawn worktree --capacity 8

# Verbose logging for debugging
claude remote-control --spawn worktree --verbose

# Named server with sandboxing enabled
claude remote-control --name "Isolated Env" --sandbox
```

---

## Spawn Modes

The `--spawn` flag controls how new concurrent sessions are created when additional connections arrive. Press **`w`** at runtime to toggle between modes.

### `same-dir` (Default)

All sessions share the current working directory.

```bash
claude remote-control --spawn same-dir
```

**When to use**: Solo work, sequential tasks, or when sessions operate on different files.

**Caution**: Multiple sessions editing the same files can cause conflicts. Coordinate carefully or use `worktree` mode instead.

### `worktree`

Each on-demand session gets its own [git worktree](https://git-scm.com/docs/git-worktree), providing full filesystem isolation.

```bash
claude remote-control --spawn worktree
```

**When to use**: Parallel increment work, team collaboration, or any scenario where sessions might edit overlapping files.

**Requirements**: The working directory must be a git repository.

**How it works**:
1. When a new session connects, Claude Code creates a temporary git worktree branching from the current HEAD
2. Each session operates in its own isolated copy of the repository
3. Changes are committed to the worktree's branch and can be merged back

---

## Alternative Ways to Start Remote Control

### Interactive Session with Remote Control

Start a normal interactive session that's also available remotely:

```bash
# With --remote-control (or --rc shorthand)
claude --remote-control

# With a custom name
claude --remote-control "My Project"
```

Unlike server mode, you can type messages locally while the session is also available remotely. However, this only supports **one remote session** — use server mode with `--spawn` for concurrency.

### From an Existing Session

Already in a Claude Code session? Enable Remote Control on the fly:

```
/remote-control
/remote-control My Project
/rc
```

This starts a remote session with your current conversation history intact. The `--verbose`, `--sandbox`, and `--no-sandbox` flags are not available with this command.

---

## Connecting from Another Device

Once a Remote Control session is active:

1. **Open the session URL** displayed in the terminal in any browser
2. **Scan the QR code** (press spacebar to toggle in server mode) with the Claude iOS/Android app
3. **Browse [claude.ai/code](https://claude.ai/code)** — remote sessions show a computer icon with a green status dot

### Enable Remote Control for All Sessions

To skip the explicit activation step:

1. Run `/config` inside Claude Code
2. Set **"Enable Remote Control for all sessions"** to `true`

Each interactive Claude Code process then registers one remote session automatically.

---

## SpecWeave Integration Patterns

### Pattern 1: Autonomous Execution from Mobile

Start `/sw:auto` from your phone after setting up a server:

```bash
# On your dev machine
claude remote-control --name "Auto Worker" --spawn worktree
```

Then from claude.ai/code on your phone:
```
/sw:auto 0001-user-auth --max-hours 8
```

### Pattern 2: Parallel Increments with Worktree Isolation

Run multiple increments simultaneously with full isolation:

```bash
# Start server with worktree isolation
claude remote-control --spawn worktree --capacity 4 --name "Parallel Work"
```

Connect multiple browser tabs at claude.ai/code, each working on a different increment:
- Tab 1: `/sw:do` on increment 0001
- Tab 2: `/sw:do` on increment 0002
- Tab 3: `/sw:grill 0001` (review while still implementing 0002)

### Pattern 3: Team Dev Server

Set up a shared development server for a team:

```bash
# On a shared dev machine or VM
claude remote-control \
  --name "Team Server" \
  --spawn worktree \
  --capacity 16 \
  --verbose
```

Each team member connects from their own device and gets an isolated worktree.

---

## Connection & Security

- **Outbound-only**: your machine makes outbound HTTPS requests only — no inbound ports are opened
- **TLS transport**: all traffic routes through the Anthropic API over TLS
- **Short-lived credentials**: multiple credentials scoped to individual purposes, each expiring independently
- **Local execution**: code never leaves your machine — the web/mobile interface is just a window into the local session

---

## Limitations

| Limitation | Details |
|------------|---------|
| **One remote session per interactive process** | Outside of server mode, each Claude Code instance supports one remote session. Use server mode with `--spawn` for concurrency. |
| **Terminal must stay open** | Closing the terminal or stopping the `claude` process ends the session. |
| **Network timeout** | If your machine can't reach the network for ~10 minutes, the session times out and the process exits. Restart with `claude remote-control`. |
| **Worktree requires git** | The `--spawn worktree` option only works in git repositories. |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Session not appearing in claude.ai/code | Verify authentication with `/login`. Check that your plan supports Remote Control. |
| Worktree spawn fails | Ensure you're in a git repository (`git status`). Check for uncommitted changes that might block worktree creation. |
| Session disconnects frequently | Check network stability. The 10-minute timeout is for sustained outages — brief drops reconnect automatically. |
| Can't toggle spawn mode at runtime | Press `w` (lowercase) while the server is running. Only available in server mode (`claude remote-control`). |
| Multiple sessions conflict on same files | Switch to `--spawn worktree` mode or press `w` to toggle at runtime. |

---

## Related Documentation

- [Autonomous Execution Guide](./autonomous-execution) — `/sw:auto` mode
- [Claude CLI Automation Patterns](../development/claude-cli-automation) — scripting and CI/CD integration
- [Claude Code Remote Control (Official)](https://code.claude.com/docs/en/remote-control) — full upstream reference
