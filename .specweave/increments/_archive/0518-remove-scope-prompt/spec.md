# Spec: Remove scope selection prompt — always install to local project

## Problem

`vskill install` still shows an interactive "Installation scope: Project vs Global" prompt.
The user expects skills to always install to the **local project** by default. No prompt.
Additionally, the previous 0516 changes were never published to npm, so the old version
(with native plugin install prompts) is still served via `npx vskill`.

## Goal

Remove the scope selection prompt entirely. Skills always install to the local project
unless the `--global` flag is explicitly passed by the user.

---

## US-001: Skills always install to local project by default
**Project**: vskill

**As a** developer running `vskill i owner/repo`,
**I want** skills to install into my current project's skill directories automatically,
**so that** I don't need to answer an unnecessary scope question every time.

### ACs

- [x] AC-US1-01: Running `vskill i owner/repo` without flags installs to local project (no scope prompt shown)
- [x] AC-US1-02: Running `vskill i owner/repo --global` still installs globally (explicit override respected)
- [x] AC-US1-03: The "Installation scope:" prompt is completely removed from the interactive flow

## US-002: Publish updated package so npx picks up all fixes
**Project**: vskill

**As a** developer using `npx vskill i`,
**I want** the published npm package to reflect all recent changes (0516 + 0518),
**so that** native plugin install prompts and scope prompts are gone.

### ACs

- [x] AC-US2-01: `package.json` version bumped to 0.4.16
- [x] AC-US2-02: Package published to npm registry
