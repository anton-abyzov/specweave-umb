---
title: "New Mac from scratch: setup and provisioning in 1.0.297"
thread: "thread:delegated-task:command%3Amcp%3A3eaecc6b-6634-40a1-8cc1-59151412463f%3Adelegate-task%3A710cbb37-040e-48ee-8676-de111ae43e7e"
threadTitle: "Verify specweave copy M4 to M5"
savedAt: "2026-11-14T18:01:02.731Z"
date: November 14, 2026
release: SpecWithCode 1.0.297
---

# New Mac from scratch: setup and provisioning in 1.0.297

Short answer: almost all of it ships in 1.0.297. The first-run wizard on the M5 already installs Git, Node.js and the agent CLIs, Codex included. A **Provision** button on the M4 then brings everything up to the pinned versions without you touching the M5. Only three steps are yours alone: sign-ins, one Allow, and the macOS developer-tools window. The Codex desktop app is not part of it. Agents only need the `codex` command line tool.

## Your steps on the M5, in order

1. **Install SpecWithCode** from the download page and open it.
2. **Sign in to SpecWithCode Connect** in the wizard. The machine links itself to your account; there are no IDs to paste.
3. **Agents step.**
   - *Machine basics* checks Git, Node.js, GitHub CLI and the SpecWeave CLI. It installs what is missing with one click each and shows a visible log, with no admin password. Git on a Mac opens Apple's developer-tools window, which you confirm.
   - The Claude Code and Codex rows install the CLI with its official installer (`curl -fsSL https://chatgpt.com/codex/install.sh | sh`). Then **Sign in** runs `codex login` and `claude auth login`.
4. **Let the M4 work here.** On the M5, choose the M4 under **Let another of your machines run work here** and press **Allow**. Nothing needs accepting on the M4; it shows a notice that the M5 joined.
5. **Copy the project.** From the **M4's own window**, run Copy to another machine and send it to the M5 with secrets on. Until PR 380 ships, a copy approved from the M5's window is refused (`This connection requires access:write`).

## What the M4 can do for you

- **Provision** (Settings > Machines > the M5's row) runs on the M5 through the M5's own server and streams every step. It installs or updates only what is missing or older, at pinned versions:
  - Git and GitHub CLI;
  - Node.js 22;
  - the Claude Code and Codex CLIs;
  - the SpecWithCode server and its launch agent;
  - the agents' PATH.

  It never signs anything in, never turns on Allow, and never restarts the connection. At the end it lists what is left for you. Running it on the M5 itself (`specwithcode provision`) does the same.
- The button appears only when the M4 holds the key to maintain the M5. Press **Add m5** on its card first if it is not there.
- **Check readiness** on the same row shows each tool's state. Since 1.0.297 that check also runs quietly after each app update.

## Is it confirmed and working?

| Step | In 1.0.297 | Confirmation you see |
|---|---|---|
| Machine basics install (1318) and readiness sweep (1322) | Yes | Green rows in the Agents step; Check readiness on the M4 |
| Codex and Claude CLI install and sign-in in the wizard | Yes | Each row turns to Ready |
| Provision from the M4 | Yes | A readback in the sheet: every item Installed, Updated or Not needed, plus your remaining steps |
| Allow the M4 on the M5 | Yes | A "joined" notice on the M4; the M5's card on the M4 shows "Agents on m4 can start work on m5" |
| New devices need one approval per machine (1327) | **No**, PRs 361/362 still in review | Ships in the next release |
| Copy approved from the M5's window | **No**, PR 380 still in review | Start the copy from the M4's window |

## Recommendation

Keep the CLI as the only Codex install. It is what the agents and provisioning manage, it updates from Settings, and the desktop app adds nothing for workers. Open the Codex desktop app yourself only if you want to use it by hand.

One gap worth a small fix: provisioning installs the CLIs but cannot sign them in. A Codex sign-in that expires later, as it did on the M5 tonight (`token_expired`), only shows up when a run fails. The readiness sweep could flag "Codex signed out" on the M4 the same way it flags a missing tool.
