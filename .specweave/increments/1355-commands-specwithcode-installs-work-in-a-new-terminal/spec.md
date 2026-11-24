# Commands SpecWithCode installs work in a new Terminal

## Problem

On a fresh M5 (November 15, 2026), threads ran Claude and the picker said "Runtime ready, signed in", but `claude` in Terminal said `zsh: command not found: claude`. The server finds commands in folders a new Terminal does not search: `~/.local/bin` (the official Claude installer the setup terminal runs, and the app's own CLI launchers), `~/.local/share/specweave/providers/bin`, and the app's tools folder (Node.js, gh, SpecWeave, Codex). Nothing adds those folders to the login shell's PATH, so a project that runs `specweave` in Terminal cannot, and nothing says why.

## Scope

In: a server job that keeps one marked block in the login shell's startup file appending those folders to PATH (zsh and bash on macOS and Linux), at start and every two minutes, respecting a deleted block and linked dotfiles. Out: Windows user PATH, fish and other shells, non-login zsh on macOS (reads `~/.zshrc`), Linux bash login shells (read `~/.profile`), cleanup on uninstall (the block only appends folders, so missing ones are harmless), a UI notice, the update banner naming another machine.

## Acceptance Criteria

- [ ] AC-01: With `claude` in `~/.local/bin`, Node.js, SpecWeave or Codex installed by the app, `~/.zprofile` (macOS zsh), `~/.zshrc` (Linux zsh), `~/.bash_profile` (macOS bash) or `~/.bashrc` (Linux bash) gains one marked block that appends only the folders holding one of those commands; the person's own installs stay first and sourcing it twice adds each folder once.
- [ ] AC-02: The block is replaced when installs change, removed when nothing is left, and never added back after the person deletes it, even with a corrupt record; a failed write retries instead of opting out; two app homes on one account settle on one merged block; a changed login shell moves the block.
- [ ] AC-03: The person's file is changed only inside the block: bytes and mode kept, replaced atomically, skipped when it changed since it was read; half-paired markers, linked, non-regular, foreign-owned or over-1 MB files, unknown shells, Windows, tests and `SPECWITHCODE_TERMINAL_PATH=off` are left alone.

## Approach

`apps/server/src/machineTools/terminalPath.ts` holds the pure parts (startup file per shell, folder list, block text, apply) over a small file interface; `terminalPathRuntime.ts` runs it at start and every two minutes; `serverRuntimeStartup.ts` forks it in desktop mode or a managed service. The folder list is fixed, not derived from the login shell PATH, because reading that PATH after the block exists would undo the block. A state file `~/.local/share/specweave/terminal-path.json`, shared by every app home on the account, records the startup files written, so a deleted block stays deleted; it is written after the startup file, and an unreadable one counts as written. Each writer merges its folders with the listed ones in a fixed order and prunes only its own versioned folders. The file is handled as latin1 bytes and replaced by temp file and rename after a stamp check. Rejected: symlinks into `~/.local/bin` (versioned folders go stale, and `~/.local/bin` itself is not on a fresh Mac's PATH).

## Decisions

### Asked
- D-01 Fix the Terminal gap → yes, fix it and ship (user, November 15, 2026)
### Defaulted (change any before sw-do)
- D-02 Edit the startup file automatically, append (not prepend), with an opt-out by deleting the block → default
### Open
- none

## Tasks

### T-01 Terminal block for the installed commands
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/machineTools/terminalPath.ts, repositories/anton-abyzov/specwithcode/apps/server/src/machineTools/terminalPath.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/machineTools/terminalPath.test.ts

### T-02 Run it at server start
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/machineTools/terminalPathRuntime.ts, repositories/anton-abyzov/specwithcode/apps/server/src/serverRuntimeStartup.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/serverRuntimeStartup.test.ts
