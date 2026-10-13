# Git preservation

2026-10-13: reviewed the umbrella root and canonical product checkouts before changing anything. The root held 4 modified tracked text records and 14 untracked text files (3,409,799 bytes); the largest set is the complete linked WebMCP research evidence bundle. No images or binaries. Heuristic credential review found an all-zero schema example, no actual credentials. The repository pre-commit malware and secret scan passed.

Committed all 18 files unchanged as f86d8b82fad24df7055b373d5edc6b9da74d426f, preserving author decisions and existing task statuses. This commit includes the preexisting root-only commits 54099076d and 2bcdd3314 in its ancestry. Pushed to private anton-abyzov/specweave-umb, branch codex/0908-pending-records. `git ls-remote` returned the identical full SHA; root `git status --short` was empty afterward.

SSH authentication was unavailable. Used GitHub CLI's existing credential helper with the HTTPS remote for this operation; no shared remote/auth configuration changed.

Merged this preserved branch into the isolated umbrella branch codex/project-names-release at 5bbd9b282, retaining latest origin/main and both sides of history. AGENTS.md merged cleanly, retaining the new fleet test command and the standing visible-browser authorization.

Canonical specweave-studio, specweave, vskill and vskill-platform source checkouts were clean and matched their configured upstreams. Older feature checkouts are intentionally not reset to main. Other owners have active worktrees with changes and generated artifacts; these are outside the cleanup scope and remain untouched. This report makes no claim that every worktree on the machine is clean.
