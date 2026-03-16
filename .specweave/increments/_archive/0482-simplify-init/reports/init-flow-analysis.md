# specweave init — Complete Flow Analysis

## Executive Summary

The simplified `specweave init` (v1.0.415) reduces the command from 1,242 lines to ~538 lines. It focuses exclusively on local scaffolding: detect adapter, detect git provider silently, create `.specweave/` structure, generate config with sensible defaults, and show guided next steps. All external tool integration (GitHub/JIRA/ADO connections, repo cloning, multi-project folders) has been moved to dedicated commands.

---

## Mermaid Activity Flow Diagram

```mermaid
flowchart TD
    START([specweave init projectName options]) --> QUICK{--quick flag?}
    QUICK -->|Yes| QUICK_MSG[Print quick mode message]
    QUICK -->|No| LANG_CHECK
    QUICK_MSG --> LANG_CHECK

    %% STEP 1: Language
    LANG_CHECK{CLI --language<br/>provided?}
    LANG_CHECK -->|Yes, valid| LANG_SET[Use CLI language]
    LANG_CHECK -->|Yes, invalid| LANG_ERR[Print error + exit 1]
    LANG_CHECK -->|No| IS_CI_LANG{Is CI/non-interactive?}
    IS_CI_LANG -->|Yes| LANG_DEFAULT[Default to 'en']
    IS_CI_LANG -->|No| LANG_PROMPT[Prompt language selection]
    LANG_SET --> WELCOME
    LANG_DEFAULT --> WELCOME
    LANG_PROMPT --> WELCOME

    WELCOME[Print welcome message] --> PATH_CHECK

    %% STEP 2: Path Resolution
    PATH_CHECK{projectName<br/>argument?}
    PATH_CHECK -->|"."| DOT_PATH
    PATH_CHECK -->|name provided| NAME_PATH
    PATH_CHECK -->|none| NO_NAME_PATH

    subgraph DOT["Path: dot notation (specweave init .)"]
        DOT_PATH[targetDir = cwd] --> HOME_CHECK{Is home<br/>directory?}
        HOME_CHECK -->|Yes| HOME_ERR[Print danger + exit 1]
        HOME_CHECK -->|No| DOT_NAME{Dir name<br/>matches pattern?}
        DOT_NAME -->|Yes| DOT_USE_NAME[Use dir name as project name]
        DOT_NAME -->|No| DOT_NAME_CI{Is CI?}
        DOT_NAME_CI -->|Yes| DOT_SUGGEST[Auto-sanitize name]
        DOT_NAME_CI -->|No| DOT_PROMPT_NAME[Prompt for project name]
        DOT_USE_NAME --> DOT_REINIT
        DOT_SUGGEST --> DOT_REINIT
        DOT_PROMPT_NAME --> DOT_REINIT
        DOT_REINIT{.specweave/<br/>exists?}
        DOT_REINIT -->|Yes| SMART_REINIT
        DOT_REINIT -->|No| DOT_INFO{Non-empty<br/>directory?}
        DOT_INFO -->|Yes| DOT_INFO_MSG[Show info: non-destructive]
        DOT_INFO -->|No| GUARDS
        DOT_INFO_MSG --> GUARDS
    end

    subgraph NAME["Path: explicit name (specweave init my-app)"]
        NAME_PATH[targetDir = cwd/name] --> NAME_EXISTS{Directory<br/>exists?}
        NAME_EXISTS -->|Yes| NAME_SW{.specweave/<br/>exists?}
        NAME_SW -->|Yes| SMART_REINIT
        NAME_SW -->|No| NAME_FILES{Has files?}
        NAME_FILES -->|Yes, CI| GUARDS
        NAME_FILES -->|Yes, interactive| NAME_CONFIRM{Confirm init<br/>in existing dir?}
        NAME_FILES -->|No (empty)| GUARDS
        NAME_CONFIRM -->|Yes| GUARDS
        NAME_CONFIRM -->|No| CANCEL_EXIT[Exit 0]
        NAME_EXISTS -->|No| NAME_MKDIR[Create directory] --> GUARDS
    end

    subgraph NONAME["Path: no name provided"]
        NO_NAME_PATH --> NONAME_CI{Is CI?}
        NONAME_CI -->|Yes| NONAME_CWD[Use cwd, sanitize name]
        NONAME_CI -->|No| NONAME_PROMPT[Prompt for project name]
        NONAME_CWD --> NONAME_REINIT{.specweave/<br/>exists?}
        NONAME_REINIT -->|Yes| SMART_REINIT
        NONAME_REINIT -->|No| GUARDS
        NONAME_PROMPT --> NAME_PATH
    end

    %% Smart Re-init
    subgraph REINIT["Smart Re-init Flow"]
        SMART_REINIT[Detect existing .specweave/] --> REINIT_FORCE{--force?}
        REINIT_FORCE -->|Yes| REINIT_FORCE_CI{Is CI?}
        REINIT_FORCE_CI -->|Yes| REINIT_FRESH[Action: fresh]
        REINIT_FORCE_CI -->|No| REINIT_CONFIRM_DEL{Confirm deletion?}
        REINIT_CONFIRM_DEL -->|Yes| REINIT_FRESH
        REINIT_CONFIRM_DEL -->|No| CANCEL_EXIT
        REINIT_FORCE -->|No| REINIT_NO_FORCE_CI{Is CI?}
        REINIT_NO_FORCE_CI -->|Yes| REINIT_CONTINUE[Action: continue]
        REINIT_NO_FORCE_CI -->|No| REINIT_CHOICE{User choice}
        REINIT_CHOICE -->|Continue| REINIT_CONTINUE
        REINIT_CHOICE -->|Fresh start| REINIT_FRESH_HANDLE
        REINIT_CHOICE -->|Cancel| CANCEL_EXIT

        REINIT_FRESH --> FRESH_HANDLE
        REINIT_FRESH_HANDLE --> FRESH_HANDLE

        FRESH_HANDLE[Backup .specweave/ → delete] --> GUARDS
        REINIT_CONTINUE[Set continueExisting=true] --> GUARDS
    end

    %% STEP 3: Guard Clauses
    GUARDS[Guard Clauses] --> UMBRELLA{Inside umbrella<br/>project?}
    UMBRELLA -->|Yes, no --force| UMB_ERR[Print error + exit 1]
    UMBRELLA -->|Yes, --force| UMB_WARN[Print warning, continue]
    UMBRELLA -->|No| SUSPICIOUS
    UMB_WARN --> SUSPICIOUS

    SUSPICIOUS{Suspicious path<br/>segment?}
    SUSPICIOUS -->|Yes, no --force| SUS_ERR[Print error + exit 1]
    SUSPICIOUS -->|Yes, --force| SUS_WARN[Print warning, continue]
    SUSPICIOUS -->|No| NESTED
    SUS_WARN --> NESTED

    NESTED{Nested .specweave/<br/>in parent dirs?}
    NESTED -->|Stale folders found| STALE_PROMPT{Clean up<br/>stale folders?}
    STALE_PROMPT -->|Yes| STALE_CLEAN[Remove stale folders]
    STALE_PROMPT -->|No| NESTED_PROBLEM
    STALE_CLEAN --> NESTED_PROBLEM
    NESTED -->|No stale| NESTED_PROBLEM
    NESTED_PROBLEM{Problematic<br/>nested folders?}
    NESTED_PROBLEM -->|Yes| NESTED_ERR[Print error + exit 1]
    NESTED_PROBLEM -->|No| CREATE

    %% STEP 4: Create Project
    CREATE[Start spinner] --> ADAPTER

    subgraph PROJECT["Project Creation"]
        ADAPTER{--adapter<br/>provided?}
        ADAPTER -->|Yes| ADAPTER_SET[Use provided adapter]
        ADAPTER -->|No| ADAPTER_DETECT

        ADAPTER_DETECT[Auto-detect tool] --> ADAPTER_CI{Is CI?}
        ADAPTER_CI -->|Yes| ADAPTER_USE_DETECTED[Use detected tool]
        ADAPTER_CI -->|No| ADAPTER_SHOW[Show detected tool]
        ADAPTER_SHOW --> ADAPTER_CONFIRM{Confirm<br/>detected tool?}
        ADAPTER_CONFIRM -->|Yes| ADAPTER_USE_DETECTED
        ADAPTER_CONFIRM -->|No| ADAPTER_GENERIC[Use 'generic']

        ADAPTER_SET --> PROVIDER
        ADAPTER_USE_DETECTED --> PROVIDER
        ADAPTER_GENERIC --> PROVIDER

        PROVIDER[detectProvider from .git/config<br/>silent, no prompts] --> IS_CONTINUE{continueExisting?}

        IS_CONTINUE -->|No| DIR_STRUCT[Create directory structure<br/>+ living docs scaffold]
        IS_CONTINUE -->|Yes| IS_CONTINUE2{continueExisting?}
        DIR_STRUCT --> IS_CONTINUE2

        IS_CONTINUE2 -->|No| COPY_TPL[Copy templates<br/>CLAUDE.md, AGENTS.md, .gitignore]
        IS_CONTINUE2 -->|Yes| IS_CLAUDE

        COPY_TPL --> IS_CLAUDE{Adapter is<br/>Claude?}
        IS_CLAUDE -->|Yes| CLAUDE_MSG[Configure for Claude Code]
        IS_CLAUDE -->|No| NON_CLAUDE[Install non-Claude adapter<br/>+ copy plugins + core plugin]
        CLAUDE_MSG --> GIT_INIT
        NON_CLAUDE --> GIT_INIT

        GIT_INIT{.git/<br/>exists?}
        GIT_INIT -->|No| GIT_DO[git init + git add + commit]
        GIT_INIT -->|Yes| POST_INSTALL
        GIT_DO --> POST_INSTALL

        POST_INSTALL{Non-Claude<br/>adapter?}
        POST_INSTALL -->|Yes| POST_INSTALL_RUN[adapter.postInstall]
        POST_INSTALL -->|No| CONFIG_CREATE
        POST_INSTALL_RUN --> CONFIG_CREATE
    end

    %% Config + Defaults
    CONFIG_CREATE[createConfigFile<br/>simplified, no maturity/structureDeferred] --> CONFIG_BATCH

    subgraph BATCH["Batched Config Update (single read-modify-write)"]
        CONFIG_BATCH{config.json<br/>exists?}
        CONFIG_BATCH -->|Yes| BATCH_READ[Read config]
        CONFIG_BATCH -->|No| PLUGINS

        BATCH_READ --> BATCH_PROVIDER{Provider<br/>detected?}
        BATCH_PROVIDER -->|Yes| BATCH_SET_PROV[Set repository.provider/org/repo]
        BATCH_PROVIDER -->|No| BATCH_SMART
        BATCH_SET_PROV --> BATCH_SMART

        BATCH_SMART[applySmartDefaults<br/>testing, quality gates, planning,<br/>LSP, sync, translation] --> BATCH_LANG{keepEnglish<br/>Originals?}
        BATCH_LANG -->|Yes| BATCH_SET_LANG[Set translation.keepEnglishOriginals]
        BATCH_LANG -->|No| BATCH_LSP
        BATCH_SET_LANG --> BATCH_LSP

        BATCH_LSP{Claude<br/>adapter?}
        BATCH_LSP -->|Yes| BATCH_SET_LSP[Set LSP config]
        BATCH_LSP -->|No| BATCH_WRITE
        BATCH_SET_LSP --> BATCH_WRITE

        BATCH_WRITE[writeJsonSync config] --> PLUGINS
    end

    %% Plugins
    PLUGINS{Claude<br/>adapter?}
    PLUGINS -->|Yes| PLUGIN_CONTINUE{continueExisting?}
    PLUGINS -->|No| GIT_HOOKS

    PLUGIN_CONTINUE -->|Yes| PLUGIN_KEEP[Keep existing plugins]
    PLUGIN_CONTINUE -->|No| PLUGIN_INSTALL[installAllPlugins]
    PLUGIN_KEEP --> AGENT_TEAMS
    PLUGIN_INSTALL --> AGENT_TEAMS

    AGENT_TEAMS[Enable agent teams env var] --> LSP_ENV[Setup LSP env var]
    LSP_ENV --> GIT_HOOKS

    %% Git Hooks
    GIT_HOOKS{Git repo AND<br/>not continueExisting?}
    GIT_HOOKS -->|Yes| HOOKS_INSTALL[Install git pre-commit hooks]
    GIT_HOOKS -->|No| BANNER

    HOOKS_INSTALL --> BANNER

    %% Output
    BANNER[Display summary banner<br/>project, provider, adapter,<br/>language, defaults] --> NEXT_STEPS

    NEXT_STEPS[Show next steps<br/>1. cd project-name<br/>2. Plugin status<br/>3. specweave sync-setup<br/>4. specweave increment<br/>5. specweave migrate-to-umbrella]

    NEXT_STEPS --> DONE([Done])

    %% Styling
    style LANG_ERR fill:#f44,color:#fff
    style HOME_ERR fill:#f44,color:#fff
    style UMB_ERR fill:#f44,color:#fff
    style SUS_ERR fill:#f44,color:#fff
    style NESTED_ERR fill:#f44,color:#fff
    style CANCEL_EXIT fill:#ff9,color:#333
    style DONE fill:#4f4,color:#fff
```

---

## Scenarios Matrix

### Scenario 1: Fresh Init — Quick Mode (zero prompts)

```
specweave init my-app --quick
```

| Step | What happens |
|------|-------------|
| Language | Defaults to `en` (no prompt) |
| Path | Creates `./my-app/` directory |
| Guards | Checks umbrella, suspicious path, nested .specweave |
| Adapter | Auto-detects (Claude/Cursor/Generic), no confirmation prompt |
| Provider | Reads `.git/config` silently, returns null (new dir, no git) |
| Structure | Creates `.specweave/`, living docs scaffold, reflect config |
| Templates | Copies CLAUDE.md, AGENTS.md, .gitignore, .gitattributes, README.md |
| Git | Runs `git init` + initial commit (no existing `.git/`) |
| Config | Creates `config.json` with TDD defaults, standard quality gates |
| Smart defaults | Testing=TDD, Quality=standard, LSP=on (Claude), Deep interview=off |
| Plugins | Installs all plugins (Claude) or copies plugin folder (non-Claude) |
| Hooks | Installs git pre-commit hooks |
| Output | Summary banner + guided next steps |

**Prompts shown: 0**

---

### Scenario 2: Fresh Init — Interactive Mode

```
specweave init .
```

| Step | What happens |
|------|-------------|
| Language | Detects system locale, prompts if non-English detected |
| Path | Uses current directory, checks name validity |
| Project name | If dir name has invalid chars (uppercase, spaces), prompts for sanitized name |
| Guards | Full guard chain |
| Adapter | Auto-detects, shows result, asks `Use Claude Code? (Y/n)` |
| Provider | Silent `.git/config` read |
| Rest | Same as quick mode |

**Prompts shown: 0-2** (language if non-English locale, adapter confirmation)

---

### Scenario 3: Re-init — Continue Existing (safe update)

```
specweave init .    # .specweave/ already exists
→ User selects "Continue working"
```

| Step | What happens |
|------|-------------|
| Re-init detection | Finds `.specweave/`, shows "Existing project detected" |
| User choice | Continue / Fresh start / Cancel |
| `continueExisting=true` | Skips: directory creation, template copy, plugin install, git hooks |
| Config | Reads existing `config.json`, applies smart defaults (preserves existing values via spread) |
| Adapter | Reads existing adapter from config, still shows detection for comparison |
| Output | Summary banner shows updated config |

**Key behavior**: Non-destructive. Existing increments, docs, history all preserved. Config updated in-place.

---

### Scenario 4: Re-init — Fresh Start (destructive)

```
specweave init . --force
→ Confirms deletion
```

| Step | What happens |
|------|-------------|
| Force detection | Shows DANGER warning with itemized deletion list |
| Confirmation | Interactive: requires explicit `y`. CI: auto-proceeds |
| Backup | Creates `.specweave.backup-YYYY-MM-DD/` before deletion |
| Deletion | Removes `.specweave/` entirely, logs file count |
| Continues | Runs full fresh init flow (directory structure, templates, config, plugins) |

**Safety layers**:
1. Explicit `--force` flag required
2. Interactive confirmation prompt (CI bypasses)
3. Automatic backup before deletion
4. CI mode without `--force` blocks fresh start entirely

---

### Scenario 5: Re-init — CI Mode (no force)

```
CI=true specweave init .    # .specweave/ exists
```

| Step | What happens |
|------|-------------|
| Detection | Non-interactive detected via `CI=true` |
| Re-init | Auto-continues with existing project (no prompt) |
| Fresh start | BLOCKED — CI cannot do fresh start without `--force` |

---

### Scenario 6: Named Project — Existing Directory with Files

```
specweave init my-existing-app    # directory exists with code
```

| Step | What happens |
|------|-------------|
| Directory check | Finds `my-existing-app/` exists |
| .specweave check | Not found → not a re-init |
| Files check | Directory has files → prompts "Initialize in existing directory?" |
| CI behavior | Skips confirmation, proceeds |
| Init | Non-destructive — only adds `.specweave/` and instruction files |

---

### Scenario 7: Guard — Inside Umbrella Project

```
cd /projects/my-umbrella/repositories/org/my-repo
specweave init .
```

| Step | What happens |
|------|-------------|
| `detectUmbrellaParent()` | Walks up directories, finds parent `.specweave/config.json` with `umbrella.enabled: true` |
| Without `--force` | Prints error: "Cannot initialize here: inside an umbrella project" + exit 1 |
| With `--force` | Prints warning, continues with init |

---

### Scenario 8: Guard — Suspicious Path

```
cd /tmp
specweave init .
```

| Step | What happens |
|------|-------------|
| `detectSuspiciousPath()` | Checks for segments like `tmp`, `temp`, `node_modules`, `dist`, `.cache` |
| Without `--force` | Prints error with suggested project root + exit 1 |
| With `--force` | Prints warning, continues |

---

### Scenario 9: Guard — Nested .specweave/ in Parent

```
cd /projects/parent-project/sub-dir
specweave init .
# where /projects/parent-project/.specweave/ exists
```

| Step | What happens |
|------|-------------|
| `detectNestedSpecweave()` | Scans parent directories for `.specweave/` folders |
| Stale folders | If found (no `config.json`), offers cleanup |
| Active folders | If found (has `config.json`, not user-level), blocks init + exit 1 |

---

### Scenario 10: Guard — Home Directory

```
cd ~
specweave init .
```

| Step | What happens |
|------|-------------|
| Home check | Detects `targetDir === os.homedir()` |
| Action | Prints DANGEROUS warning + suggested alternative + exit 1 |

**This is a hard block — no `--force` bypass.**

---

### Scenario 11: Provider Detection Variants

| Remote URL | Provider | Owner | Repo |
|-----------|----------|-------|------|
| `https://github.com/acme/app.git` | `github` | `acme` | `app` |
| `git@github.com:acme/app.git` | `github` | `acme` | `app` |
| `https://dev.azure.com/acme/proj/_git/repo` | `ado` | — | — (org: `acme`) |
| `git@ssh.dev.azure.com:v3/acme/proj/repo` | `ado` | — | — (org: `acme`) |
| `https://acme.visualstudio.com/proj/_git/repo` | `ado` | — | — (org: `acme`) |
| `https://bitbucket.org/ws/app.git` | `bitbucket` | `ws` | `app` |
| `git@bitbucket.org:ws/app.git` | `bitbucket` | `ws` | `app` |
| No `.git/config` or no remote | `null` | — | — (defaults to `local`) |

---

### Scenario 12: Non-Claude Adapter (Cursor/Generic)

```
specweave init . --adapter cursor
```

| Step | What happens |
|------|-------------|
| Adapter | Uses `cursor` directly (no detection) |
| Install | `adapter.install()` + `adapter.checkRequirements()` |
| Plugins | Copies `plugins/` folder from specweave package to project |
| Core plugin | Loads and compiles core plugin via `adapter.compilePlugin()` |
| Post-install | `adapter.postInstall()` runs after config creation |
| LSP | NOT auto-enabled (Claude-only feature) |
| Plugin install | Skipped (Claude-only) |
| Output | AGENTS.md used instead of CLAUDE.md as primary instruction file |

---

### Scenario 13: Language — Non-English

```
specweave init . --language ru
```

| Step | What happens |
|------|-------------|
| Language validation | Checks `isLanguageSupported('ru')` |
| Config | Adds `translation` block: method=in-session, keepFrameworkTerms=true |
| Smart defaults | Sets translation.enabled=true, languages=['en', 'ru'], primary='ru' |
| keepEnglishOriginals | If true, sets `config.translation.keepEnglishOriginals = true` |
| i18n strings | All UI messages use locale manager for the selected language |
| Next steps | Displayed in the selected language |

---

## Config Generation — What Gets Written

### Initial `createConfigFile()` output:

```json
{
  "version": "2.0",
  "project": { "name": "my-app", "version": "0.1.0" },
  "adapters": { "default": "claude" },
  "repository": { "provider": "local" },
  "hooks": {
    "post_task_completion": { "sync_tasks_md": true, "external_tracker_sync": true },
    "post_increment_planning": { "auto_create_github_issue": true },
    "post_increment_done": { "sync_living_docs": true, "sync_to_github_project": true, "close_github_issue": true }
  },
  "auto": { "enabled": true, "maxRetries": 20, "requireTests": false, "requireValidation": true },
  "lsp": { "enabled": true, "autoInstallPlugins": true, "marketplace": "boostvolt/claude-code-lsps" },
  "language": "en"
}
```

### After batched config update (provider + smart defaults + LSP):

```json
{
  "version": "2.0",
  "project": { "name": "my-app", "version": "0.1.0" },
  "adapters": { "default": "claude" },
  "repository": { "provider": "github", "organization": "acme", "repo": "my-app" },
  "hooks": {
    "post_task_completion": { "sync_tasks_md": true, "external_tracker_sync": true },
    "post_increment_planning": { "auto_create_github_issue": true },
    "post_increment_done": { "sync_living_docs": true, "sync_to_github_project": true, "close_github_issue": true }
  },
  "auto": { "enabled": true, "maxRetries": 20, "requireTests": false, "requireValidation": true },
  "lsp": { "enabled": true, "autoInstallPlugins": true, "marketplace": "boostvolt/claude-code-lsps" },
  "testing": { "defaultTestMode": "TDD", "defaultCoverageTarget": 80, "coverageTargets": { "unit": 80, "integration": 60, "e2e": 40 } },
  "qualityGates": { "preset": "standard", "enforcement": { "testsRequired": true, "llmValidation": true, "specCompliance": true } },
  "planning": { "deepInterview": { "enabled": false }, "incrementInterview": { "enabled": true, "minQuestions": 3 } },
  "sync": { "enabled": true, "autoSync": true, "settings": { "canUpsertInternalItems": true, "canUpdateExternalItems": true, "canUpdateStatus": true, "autoSyncOnCompletion": true } },
  "translation": { "enabled": false },
  "language": "en"
}
```

---

## Hooks Architecture — Lifecycle Timing

| Hook | When Fires | Actions |
|------|-----------|---------|
| `post_task_completion` | After each task marked `[x]` | `sync_tasks_md`: updates tasks.md checkboxes; `external_tracker_sync`: pushes to GitHub/JIRA/ADO |
| `post_increment_planning` | After PM/Architect/Planner agents complete spec/plan/tasks | `auto_create_github_issue`: creates GitHub issue for the increment. **No** `sync_living_docs` here — spec.md is still being written by agents at this point |
| `post_increment_done` | After `/sw:done` closes increment | `sync_living_docs` runs FIRST (generates FEATURE.md + chains to external tools), THEN `sync_to_github_project` + `close_github_issue` run in parallel. 30s sync lock prevents race conditions |

---

## What Was Removed vs. What Remains

### Removed from init (handled by other commands):

| Capability | Now handled by |
|-----------|---------------|
| Brownfield/greenfield detection | Removed entirely |
| Repository hosting setup (GitHub/ADO/Bitbucket credentials) | `specweave sync-setup` |
| Repo cloning (ADO/GitHub/Bitbucket) | `specweave migrate-to-umbrella` |
| Multi-project folder creation | `specweave migrate-to-umbrella` |
| Issue tracker setup (JIRA/ADO/GitHub) | `specweave sync-setup` |
| Testing config prompts | Smart defaults (auto TDD) |
| Translation config prompts | Smart defaults (auto from language) |
| Quality gates config prompts | Smart defaults (auto standard) |
| Deep interview config prompts | Smart defaults (auto off) |
| `structureDeferred` | `resolve-structure` deprecated |
| `projectMaturity` | Removed entirely |

### Kept in init:

| Capability | Why |
|-----------|-----|
| Language selection | Must be first (affects all UI strings) |
| Adapter detection | Core to init — determines instruction file format |
| Provider detection | Silent, no prompts — just reads `.git/config` |
| Smart re-init | Essential for `specweave init .` in existing projects |
| Guard clauses | Safety — prevents destructive mis-initialization |
| Directory structure | Core purpose of init |
| Template copy (CLAUDE.md/AGENTS.md) | Core purpose of init |
| Config generation | Core purpose of init |
| Smart defaults | Non-interactive, replaces all config prompts |
| Plugin installation | Claude-specific, still needed |
| Git hooks | Non-interactive, auto-installed |
| Summary banner | User feedback |
| Guided next steps | Replaces verbose adapter-specific instructions |

---

## Error Paths Summary

| Error | Trigger | Exit code |
|-------|---------|-----------|
| Invalid language | `--language xx` where xx not supported | 1 |
| Home directory | `specweave init .` in `~` | 1 |
| Inside umbrella | Parent dir has umbrella config (no `--force`) | 1 |
| Suspicious path | Path contains `tmp`, `node_modules`, etc. (no `--force`) | 1 |
| Nested .specweave | Active `.specweave/` in parent dir | 1 |
| Re-init cancelled | User selects "Cancel" in re-init prompt | 0 |
| Existing dir declined | User declines init in non-empty dir | 0 |
| CI fresh without force | CI mode tries fresh start without `--force` | 0 (returns false) |
| Template dir missing | Cannot locate templates directory | 1 (thrown) |
| Adapter not found | Invalid `--adapter` value | 1 (thrown) |
| Generic failure | Any unhandled error in try/catch | 1 |

---

## Backward Compatibility

- **Existing config.json files** with `sync`, `umbrella`, `issueTracker`, `multiProject`, `projectMaturity`, `structureDeferred` sections continue to work — all config readers use optional chaining
- **New config.json files** are simpler — no sync profiles, no issue tracker, no maturity fields
- **`resolve-structure` command** still works but has deprecation notice — init no longer sets `structureDeferred`
- **Helper modules** (`repository-setup.ts`, `greenfield-detection.ts`, `brownfield-analysis.ts`, cloning helpers) are NOT deleted — still used by other commands
