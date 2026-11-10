Claude's assistant data is account-level and lives on Anthropic's servers: chat memory, Projects and project knowledge, chat history and project memory. A second device gets the assistant just by signing in to the same account and org. Claude Code and Cowork memory are local Markdown files by default, protected only by Unix file permissions. Server sync for them exists in the shipped code but is gated by flags and account type. OAuth tokens are the only data encrypted at rest on disk, through macOS Keychain.

Versions examined: Claude Desktop 4.23118.0 and Claude Code CLI 2.1.302 (Mach-O arm64 at `/Users/antonabyzov/.local/share/claude/versions/2.1.302`). REA MCP was not loaded, so I inspected the shipped files directly. The app.asar is extracted to `/tmp/rea-claude-desktop-1794232862/app/.vite/build` (cited below as `build/`), and the CLI strings dump is in `/tmp/rea-cc/strings.txt`. Both bundles are minified onto one line, so citations use byte offsets (`@N`). I read file names, schemas and key names only, never conversation or memory content. Nothing was modified, and no statev2 or specwithcode-dev file was touched.

**A. claude.ai, Desktop chat and Mobile (account-level, server-side)**

1. VERIFIED (doc): Memory is saved as individual topics in real time ("Claude saves memory as a set of individual topics as you chat"). The legacy version used a 24-hour synthesis. It is on by default for Free, Pro, Max and Ultra on web, Desktop and Mobile. [support.claude.com/en/articles/11817273](https://support.claude.com/en/articles/11817273)
2. VERIFIED (doc), same page: Project scoping.
   - "Each project has its own memory." Inside a project, Claude uses that project's memory plus your non-project memory, never other projects'.
   - Turning off "Use account memory" on the project page isolates it fully.
   - Deleting a project deletes its memory.
3. VERIFIED (doc), same page: Controls.
   - **Incognito:** not saved to memory or chat history, and excluded from chat search. On Team and Enterprise, incognito chats are still in org exports and under retention policy.
   - **Pause:** keeps memory but stops using or making it.
   - **Reset:** permanently deletes all memory, including project memory.
   - **Per-chat memory off:** the chat stays in history and stays searchable.
   - **Other:** "Search and reference chats" is a separate toggle. Memory import/export is experimental. All memory is included in data exports.
   - **Retention:** deleting a conversation does not remove memories derived from it. Under custom retention, a memory entry not updated within the period is deleted.
4. VERIFIED (doc), same page: Enterprise and Team.
   - Owners turn memory on or off org-wide and cannot enable it per user.
   - "Owners can't view or edit a user's individual memories."
   - Turning memory off at org level permanently deletes all members' memory.
5. VERIFIED (artifact): Server-side memory settings and a reset timestamp exist. `GET /api/organizations/{org}/memory/settings` returns `last_claude_ai_memory_reset_at` (`build/index.chunk-D_UN03H-.js` @~6400, function `U`).
6. VERIFIED (artifact): Incognito is not enforced in the desktop main process. The IPC `WindowControl.setIncognitoMode` exists, but its main-process implementation is the empty body `setIncognitoMode(e){}` (`build/index.chunk-BBUaTQ8d.js` @2041999 and @5643378).
   - INFERRED: incognito is implemented in the claude.ai web layer and on the server. The desktop app is a wrapper around claude.ai (IPC channel prefix `claude.web`, same file @2041999).

**B. Cowork / Dispatch memory (Desktop agent mode)**

6. VERIFIED (artifact): Local layout is `~/Library/Application Support/Claude/local-agent-mode-sessions/<uuid>/<uuid>/`. It contains:
   - `agent/memory/` holding `MEMORY.md` plus topic `.md` files. These are plaintext UTF-8 at mode `-rw-r--r--`.
   - Per-session `local_<uuid>/.claude/projects/<slug>/memory/`.
   - `cowork_settings.json`, `audit.jsonl` with `.audit-key`, `scheduled-tasks.json` and `remote-session-spaces.json`.
   - INFERRED: the two uuids are account and org, because `cowork-memory-resets.json` keys entries as `account:org` (`L=(e,t)=>`${e}:${t}``, same file @3548).
7. VERIFIED (artifact): Remote sync client `CoworkMemorySync` uses `GET` and `PUT /api/claude_code/memory?scope=user&repo=<orgUuid>/<repo>` (`build/index.chunk-D_UN03H-.js` @717).
   - Headers: `X-Client-Platform: cowork-desktop` and `x-organization-uuid`.
   - Body: `{entries, soft_delete_keys}`. The response carries `checksum`, `content.entries` and `content.entryChecksums`.
   - Concurrency: optimistic, using ETag `If-Match` / `If-None-Match`. 412 or 409 maps to conflict, 413 to rejected, 404 to empty.
   - Sync is gated: it runs only if `canSyncCoworkMemoryRemotely()`, `!oit()` and flag `975112542` all hold. Otherwise a no-op class returns `{checksum:"local"}`, meaning device-local only.
8. VERIFIED (artifact): Third-party inference mode never syncs. The 3P profile hard-codes `canSyncCoworkMemoryRemotely(){return!1}` and `hasClaudeAiProductFeatures(){return!1}`; first-party returns `!0` (`build/index.chunk-BBUaTQ8d.js` @3078843 vs @3133092).
9. VERIFIED (artifact): A claude.ai memory reset propagates to the device. The `[cowork-memory-reset]` module polls the settings endpoint. When the reset time is newer than its locally recorded `actedOn`, it deletes this computer's Cowork memory for that account and org:
   - `memory/memory` and `<agent>/memory`
   - `spaces/*/memory`
   - `*/memory.md`
   - Until the server answers, Cowork memory is withheld ("stays off").
   - State lives in `cowork-memory-resets.json` (same file, functions `K`, `q`, `te`, `Z`). The reset check is skipped for 3P accounts.
10. VERIFIED (artifact): Dispatch memory is migrated to the account. `[dispatch-memory-migration]` (`build/index.chunk-Izwnk72J.js` @9499, @12215, @33700) does the following:
    - Creates a private claude.ai project through `POST /v1/code/channels` with `memory_enabled:true` and `creation_source:"dispatch_migration"`. The project is named "Claude Dispatch".
    - Writes notes as project knowledge under `knowledge/dispatch/...` (the model sees `/mnt/project-files/knowledge/dispatch/memory/`).
    - Writes server memories through `/v1/code/memory/channel/{id}/memories`.
    - Headers: `anthropic-beta: ccr-byoc-2025-07-29` and `x-organization-uuid`.
    - Has an opt-out (`dispatch_memory_migration_declined`) and local state in `memory-migration-state.json`.
11. VERIFIED (doc) vs artifact: The help article says "Cowork sessions that run locally on your computer don't use memory" and that memory is shared between Chat and Cowork only when Cowork runs in the cloud. The artifact shows populated local `agent/memory` dirs, so the local path exists, possibly as legacy or flag-gated.

**C. Claude Code CLI**

12. VERIFIED (doc): The four `CLAUDE.md` layers are managed, user, project and local. [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)
    - **Managed:** on macOS at `/Library/Application Support/ClaudeCode/CLAUDE.md` (Linux `/etc/claude-code/`, Windows `C:\Program Files\ClaudeCode\`). It cannot be excluded.
    - **User:** `~/.claude/CLAUDE.md`.
    - **Project:** `./CLAUDE.md` or `.claude/CLAUDE.md` plus `.claude/rules/`.
    - **Local:** `./CLAUDE.local.md`, gitignored and present only in that worktree.
    - Loading: ancestor files are concatenated root-first and subdirectory files load on demand. `@path` imports are supported; imports from outside the project need one approval. `claudeMdExcludes` applies at any settings layer.
    - Precedence with `AGENTS.md`: `AGENTS.md` is read only when no `CLAUDE.md` or `CLAUDE.local.md` exists.
13. VERIFIED (doc and artifact): Auto memory lives in `~/.claude/projects/<project>/memory/`.
    - The `<project>` key comes from the git repo, so it is shared across worktrees and subdirectories.
    - The first 200 lines or 25KB of `MEMORY.md` load at startup.
    - Docs: "Auto memory is machine-local… Files are not shared across machines or cloud environments."
    - Settings: `autoMemoryEnabled`, `autoMemoryDirectory`, `autoDreamEnabled` (background consolidation) and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. The binary's settings schema is at CLI binary @212826237.
    - Security rule: `autoMemoryDirectory` is ignored in checked-in project settings and is on the launch-folder key strip list `cqs` (@212982795). The trust dialog warns "This folder changes where automatic memory is written".
14. VERIFIED (artifact): Server-backed memory exists in 2.1.302, beyond what the docs describe.
    - **Org/team memory mounts:** discovered through `/v1/code/local/memory/mounts` with a credential from `/v1/code/local/memory/credential`, cached in `org-memory-discovery.json` for 24 hours (@217405412).
    - **Store paths:** `/v1/code/memory/{grouping/<id>|grouping-root|cagt_<silo>}` (@217373975). Kinds include `team-shared`, `space-shared`, `project_*`, `silo_*` and `slack_*`, and each store has `public` or `private` visibility.
    - **Sync markers:** each mount dir holds a `.memory-sync` marker, and a mount belonging to a different partition suppresses sync (`team_memory_multistore_conflict`).
    - **Secret scanning blocks writes:** "cannot be written to team memory. Team memory is shared with all repository collaborators" and "cannot be written to memory. Memory is synced to your account" (@102474410). Error codes include `team_memory_group_acl_denied` and `content_secret` (@102673261).
    - INFERRED: account-synced personal memory and team memory are flag-gated. Docs and local evidence (`team_memory_enabled`, GrowthBook gating) say machine-local is the default.
15. VERIFIED (artifact): Credentials are stored in the macOS Keychain.
    - Service name: `Claude Code${OAUTH_FILE_SUFFIX}` plus `-credentials`, with an 8-hex sha256 suffix when `CLAUDE_CONFIG_DIR` is set, and account `$USER` (@214659105). Keychain confirms service "Claude Code-credentials", acct "antonabyzov".
    - `CLAUDE_SECURESTORAGE_CONFIG_DIR` overrides the location.
    - `.credentials.json` strings are also present. INFERRED: that is the Linux/no-Keychain fallback.

**D. Desktop encryption at rest**

16. VERIFIED (artifact): Electron `safeStorage` is backed by the Keychain item "Claude Safe Storage" / "Claude Key". It encrypts:
    - `config.json` keys `oauth:tokenCache` and `oauth:tokenCacheV2`. Their values start with `djEw`, which is base64 for `v10`, the Chromium safeStorage prefix.
    - `msal-cache.enc` and `broker-session-accounts.enc`.
    - `__encrypted__:` prefixed values and pairing tokens.
    - At startup a self-test encrypts and decrypts a random value (`build/index.chunk-BBUaTQ8d.js` @1534021, @1548745, @3181347).
17. VERIFIED (artifact): These are not encrypted:
    - Cowork memory `.md` files and Claude Code `~/.claude/projects/*/memory`, which are plain files.
    - `claude_desktop_config.json`, which holds MCP server definitions and their env. It is `0600` plaintext.
    - INFERRED: protection is file mode plus FileVault only.

**E. How a second device gets the assistant**

18. VERIFIED (doc and artifact): Sign-in to the same account and org is the identity. Server-side memory, projects and knowledge, and chat history follow it. Requests carry `x-organization-uuid` and per-account auth.
19. Device-local unless the gated sync is on: Claude Code `CLAUDE.md`, auto memory, `settings.json` and MCP config. Cowork local memory, plugins and scheduled tasks under `local-agent-mode-sessions/<account>/<org>` are also device-local. These are copied by hand, through a git repo (checked-in project `CLAUDE.md`), or by the flag-gated `/api/claude_code/memory` and `/v1/code/memory/*` sync.
20. Enterprise:
    - Managed `CLAUDE.md` and managed-settings for Claude Code are VERIFIED (doc).
    - The org memory toggle is VERIFIED (doc).
    - The 3P/Bedrock-style desktop mode disables all remote memory sync and claude.ai features, VERIFIED (artifact, item 8).

Bounded gap: I did not trace project-knowledge upload endpoints or the incognito server flag. Those rest on docs only.