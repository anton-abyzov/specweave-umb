# SpecWeave Installation

Comprehensive installation guide for all scenarios.

## Prerequisites

Before installing SpecWeave, ensure you have:

**Required:**
- [Node.js](/docs/glossary/terms/nodejs) 20.12.0+ - Check with `node --version`
- npm 10+ - Check with `npm --version`

**Recommended:**
- Claude Code (best experience)
- [Git](/docs/glossary/terms/git) for version control

## Installation Methods

### Method 1: Global Install (Recommended)

Install once, use everywhere:

```bash
# Install globally
npm install -g specweave

# Verify installation
specweave --version

# Create new project
specweave init my-project
cd my-project
```

**Pros:**
- ✅ Command always available (`specweave` command)
- ✅ Faster subsequent runs (no download)
- ✅ Works offline after first install
- ✅ Consistent version across projects

**Cons:**
- ❌ Requires admin/root on some systems
- ❌ Manual updates needed: `specweave update`

**Best for:** Regular SpecWeave users, developers working on multiple projects

### Method 2: npx (No Install)

Run without installing:

```bash
# New project (always uses latest version)
npx specweave init my-project
cd my-project

# Existing project
cd my-existing-project
npx specweave init .
```

**Pros:**
- ✅ No global installation needed
- ✅ Always uses latest version
- ✅ No permission issues
- ✅ Perfect for CI/CD

**Cons:**
- ❌ Slower (downloads each time)
- ❌ Requires internet connection

**Best for:** First-time users, [CI/CD](/docs/glossary/terms/ci-cd) pipelines, testing latest version

### Method 3: From Source (Contributors)

For contributors or testing unreleased features:

```bash
# Clone repository
git clone https://github.com/anton-abyzov/specweave.git
cd specweave

# Install dependencies
npm install

# Build TypeScript
npm run build

# Link globally
npm link

# Verify
specweave --version

# Create project
specweave init my-project
```

**Best for:** Contributors, debugging, custom modifications

## What Gets Installed

### Directory Structure

After running `specweave init`, you get:

```
your-project/
├── .claude/                  # Claude Code integration (if detected)
│   ├── settings.json         # Plugin marketplace reference (GitHub remote)
│   ├── agents/               # 10 specialized agents (installed from plugins)
│   │   ├── pm/               # Product Manager AI
│   │   ├── architect/        # System Architect
│   │   ├── tech-lead/        # Tech Lead
│   │   ├── qa-engineer/      # QA Engineer (testing plugin)
│   │   ├── security/         # Security Engineer
│   │   ├── performance/      # Performance Engineer
│   │   ├── docs-writer/      # Technical Documentation
│   │   ├── tdd-cycle/        # TDD Workflow
│   │   ├── translator/       # Multilingual Support
│   │   └── code-reviewer.md  # Code Review (standalone file)
│   ├── skills/               # 14 development skills (installed from plugins)
│   │   ├── increment/
│   │   ├── context-loader/
│   │   ├── tdd-workflow/
│   │   ├── brownfield-analyzer/
│   │   ├── brownfield-onboarder/
│   │   ├── increment-quality-judge/
│   │   ├── increment-quality-judge-v2/
│   │   ├── context-optimizer/
│   │   ├── plugin-detector/
│   │   ├── role-orchestrator/
│   │   ├── specweave-detector/
│   │   ├── specweave-framework/
│   │   ├── task-builder/
│   │   └── translator/
│   ├── commands/             # 22 slash commands (installed from plugins)
│   │   ├── increment.md
│   │   ├── do.md
│   │   ├── progress.md
│   │   ├── done.md
│   │   ├── validate.md
│   │   ├── qa.md
│   │   ├── status.md
│   │   ├── pause.md
│   │   ├── resume.md
│   │   ├── abandon.md
│   │   ├── sync-docs.md
│   │   ├── sync-tasks.md
│   │   ├── check-tests.md
│   │   ├── costs.md
│   │   ├── translate.md
│   │   ├── update-scope.md
│   │   ├── next.md
│   │   └── ... (5 more)
│   └── hooks/                # 8 automation hooks (installed from plugins)
│       ├── post-task-completion.sh
│       ├── pre-implementation.sh
│       ├── post-implementation.sh
│       ├── pre-increment-planning.sh
│       ├── post-increment-planning.sh
│       └── ... (3 more)
│
├── .specweave/               # SpecWeave framework
│   ├── increments/           # Auto-numbered features
│   │   ├── README.md
│   │   ├── roadmap.md
│   │   └── 0001-feature/     # Created by workflow
│   ├── docs/                 # Living documentation
│   │   ├── internal/
│   │   │   ├── strategy/     # PRDs, market research
│   │   │   ├── architecture/ # HLDs, ADRs, C4 diagrams
│   │   │   ├── delivery/     # Roadmap, CI/CD
│   │   │   ├── operations/   # Runbooks, SLOs
│   │   │   └── governance/   # Security, compliance
│   │   └── public/           # Published docs
│   ├── tests/                # Centralized test repository
│   ├── config.json            # Configuration
│   └── logs/                 # Execution logs
│
├── CLAUDE.md                 # Complete development guide
├── AGENTS.md                 # Universal adapter (for non-Claude tools)
└── .gitignore                # Standard ignores
```

### For Claude Code (Native)

Gets **full native integration**:
- ✅ 11 agents in `.claude/agents/`
- ✅ 17 skills in `.claude/skills/`
- ✅ 22 slash commands in `.claude/commands/`
- ✅ 8 automation hooks in `.claude/hooks/`

### For Other AI Tools (Cursor, Copilot, Gemini, ChatGPT)

Gets **universal adapter**:
- ✅ `AGENTS.md` - Works with ANY AI tool
- ✅ `.cursorrules` - For Cursor (if detected)
- ✅ `.github/copilot/` - For Copilot (if detected)
- ✅ Same `.specweave/` structure
- ✅ Same `CLAUDE.md` guide

**Note:** Only Claude Code gets native agents/skills. Other tools use the universal AGENTS.md adapter with manual workflow.

## Scenario-Specific Installation

### New Project (Greenfield)

```bash
# Method 1: Create new directory
npx specweave init my-project
cd my-project

# Method 2: Create directory first
mkdir my-project && cd my-project
npx specweave init .
```

**What happens:**
1. Creates project directory (if needed)
2. Detects your AI tool (Claude, Cursor, Copilot, etc.)
3. Installs appropriate components
4. Creates `.specweave/` structure
5. Generates `CLAUDE.md` and `AGENTS.md`
6. Sets up `.gitignore`
7. Initializes git repository (if git is available)

### Existing Project (Brownfield)

```bash
cd my-existing-project
npx specweave init .
```

**What happens:**
1. Detects existing files
2. Prompts for confirmation if directory is not empty
3. ✅ Preserves your existing code and git history
4. Adds SpecWeave structure without touching your code
5. Uses directory name as project name (or prompts if invalid)

**Safe Operations:**
- ✅ Never modifies existing source code
- ✅ Never overwrites existing files (asks first)
- ✅ Keeps your git history intact
- ✅ All SpecWeave work isolated in `.specweave/`

### Multiple Projects (Umbrella Workspace)

When working with multiple repositories, use the **umbrella workspace** pattern — initialize once, then clone repos with `specweave get`:

```bash
# 1. Create the umbrella workspace
specweave init my-workspace
cd my-workspace

# 2. Clone repositories into the workspace
specweave get my-org/user-service
specweave get my-org/order-service
specweave get my-org/notification-service

# Bulk clone an entire GitHub org
specweave get "my-org/*"

# Filter by pattern
specweave get "my-org/service-*"
```

> **Using npx?** Replace `specweave get` with `npx specweave get` if you haven't installed globally.

**Directory structure:**

```
my-workspace/
├── .specweave/                          ← Single SpecWeave root
│   ├── increments/                      ← All increments managed here
│   │   ├── 0001-user-auth/
│   │   └── 0002-order-api/
│   ├── docs/
│   └── config.json
├── repositories/
│   └── my-org/
│       ├── user-service/                ← Cloned repo
│       ├── order-service/               ← Cloned repo
│       └── notification-service/        ← Cloned repo
├── CLAUDE.md
└── AGENTS.md
```

**Why umbrella?** Centralizing specs prevents fragmentation across repos. A single increment can span multiple repositories, and all planning, tracking, and living docs stay in one place.

**Key principles:**

- ✅ One `specweave init` — the umbrella workspace owns all configuration
- ✅ Increments centralized at umbrella root, tagged by project
- ✅ Child repos do NOT get their own `.specweave/increments/`
- ✅ Cross-repo coordination via `/sw:team-lead` for parallel work across repos

## Verification

After installation, verify everything is set up correctly:

```bash
cd your-project

# Verify SpecWeave structure
ls -la .specweave/          # Should have increments/, docs/, config.json
cat .specweave/config.json  # Should show configuration
cat CLAUDE.md               # Should exist
cat .gitignore              # Should exist

# For Claude Code users
ls -la .claude/agents/      # Should have 11 agents
ls -la .claude/skills/      # Should have 17 skills
ls -la .claude/commands/    # Should have 22 commands
ls -la .claude/hooks/       # Should have 8 hooks

# For other AI tool users
cat AGENTS.md               # Should exist

# Test a command (Claude Code only)
# Open Claude Code and type: /sw:progress
```

### Verification Checklist

- [ ] `.specweave/` directory exists
- [ ] `.specweave/config.json` is present
- [ ] `CLAUDE.md` exists
- [ ] `.gitignore` includes SpecWeave ignores
- [ ] Git repository initialized (if git available)
- [ ] For Claude Code: `.claude/agents/` has 11 agent folders
- [ ] For Claude Code: `.claude/skills/` has 17 skill folders
- [ ] For Claude Code: `.claude/commands/` has 22 command files
- [ ] For other tools: `AGENTS.md` exists

### Test the Interactive Flow

**Try the quick build workflow:**

```bash
# Open Claude Code in your project and type:
"build a very simple web calculator app"

# SpecWeave will guide you through:
# 1. Approach selection (Quick build vs plan first)
# 2. Feature selection (multi-select checkboxes)
# 3. Tech stack choice (Vanilla, React, etc.)
# 4. Review and submit

# Your app will be built in ~2 minutes!
```

**Or use slash commands for full control:**

```bash
# In Claude Code:
/sw:increment "my first feature"

# This creates:
# ✅ .specweave/increments/0001-my-first-feature/
#    ├── spec.md (requirements)
#    ├── plan.md (architecture)
#    └── tasks.md (implementation steps with embedded tests)
```

## Configuration

After installation, optionally customize `.specweave/config.json`:

```json
{
  "project": {
    "name": "your-project",
    "type": "greenfield"
  },
  "hooks": {
    "enabled": true,
    "post_task_completion": {
      "enabled": true,
      "notification_sound": true
    }
  },
  "testing": {
    "e2e_playwright_mandatory_for_ui": true,
    "min_coverage": 80
  },
  "integrations": {
    "jira": { "enabled": false, "url": "", "project_key": "" },
    "github": { "enabled": false, "repository": "" },
    "azure_devops": { "enabled": false, "organization": "", "project": "" }
  }
}
```

**Configuration options:**

- `project.type` - "greenfield" or "brownfield"
- `hooks.enabled` - Enable automation hooks
- `testing.e2e_playwright_mandatory_for_ui` - Enforce E2E tests
- `testing.min_coverage` - Minimum test coverage (default: 80%)
- `integrations.*` - Enable JIRA, GitHub, Azure DevOps sync

## Upgrading

### Recommended: `specweave update`

The best way to upgrade is to run `specweave update` inside your project:

```bash
cd your-project
specweave update
```

This single command handles the **full upgrade lifecycle**:

1. **Updates the CLI binary** — checks npm for the latest version and self-updates
2. **Migrates project configuration** — updates `CLAUDE.md`, `AGENTS.md`, and `config.json` to match the new version
3. **Cleans up stale state** — removes old lock files, orphaned folders, and expired auto-session state
4. **Prunes skill memories** — removes learnings older than 90 days to keep AI context fresh
5. **Refreshes marketplace plugins** — installs latest agents, skills, commands, and hooks
6. **Validates project health** — detects and fixes installation issues automatically

```bash
# Common flags
specweave update              # Full update (recommended)
specweave update --check      # Dry run — shows what would change without modifying anything
specweave update --no-plugins # Update CLI and config only, skip plugin refresh
specweave update --all        # Refresh ALL marketplace plugins (not just core)
specweave update --no-self    # Skip CLI binary update, only update project files
specweave update --verbose    # Show detailed output for each step
```

### Why not just `npm update -g specweave`?

Running `npm update -g specweave` (or `pnpm update -g specweave`) **only updates the CLI binary**. It does NOT touch your projects. This means:

- Your `CLAUDE.md` and `AGENTS.md` still contain old framework instructions
- Your `config.json` may be missing fields required by the new version
- Stale state files and orphaned folders accumulate over time
- Marketplace plugins (agents, skills, commands, hooks) remain outdated
- Legacy formats are never migrated to current conventions

In short: you're running a new CLI against old project scaffolding, which can cause subtle issues — missing skills, broken hooks, or stale guidance in AI prompts.

**Use `npm update -g specweave` only when** you need to update the binary on a machine where no SpecWeave project is open (e.g., a fresh CI runner). For all other cases, prefer `specweave update`.

### npx (Always Latest)

npx automatically uses the latest version of the CLI binary, but the same caveat applies — it does not update your project files. Run `npx specweave update` inside your project to get the full upgrade.

### Reinstall Project

If you need a clean reinstall (e.g., corrupted state or major version jump):

```bash
cd your-project

# Backup your .specweave/ if needed
cp -r .specweave .specweave.backup

# Reinstall (will prompt for confirmation)
specweave init . --force

# Or with npm
npx specweave init . --force
```

## Uninstallation

### Remove from Project

```bash
cd your-project

# Remove SpecWeave files
rm -rf .claude .specweave CLAUDE.md AGENTS.md

# Your application code remains untouched!
```

**Note:** Your source code is never modified by SpecWeave, so uninstallation is safe and clean.

### Uninstall Global Package

```bash
npm uninstall -g specweave
```

## Troubleshooting

### npx not found

```bash
# Update npm
npm install -g npm@latest

# Verify npx
npx --version
```

### Permission denied (global install)

**Option 1: Use npx instead (recommended)**
```bash
npx specweave init my-app
```

**Option 2: Fix npm permissions**
```bash
# See: https://docs.npmjs.com/resolving-eacces-permissions-errors

# Quick fix (macOS/Linux):
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Skills not activating (Claude Code)

```bash
# Verify installation
ls -la .claude/skills/
# Should see 17 skills with SKILL.md files

# Check a specific skill
cat .claude/skills/increment/SKILL.md

# If missing, reinstall
npx specweave init . --force
```

### Commands not found (Claude Code)

```bash
# Verify commands
ls -la .claude/commands/
# Should see: increment.md, do.md, etc. (22 total)

# Check a specific command
cat .claude/commands/increment.md

# If missing, reinstall
npx specweave init . --force
```

### Hooks not running

```bash
# Make hooks executable
chmod +x .claude/hooks/*.sh

# Verify permissions
ls -la .claude/hooks/
# Should show -rwxr-xr-x permissions

# Test hook manually
./.claude/hooks/post-task-completion.sh
```

### Node.js version too old

```bash
# Check version
node --version

# If < 18, upgrade using nvm (recommended)
# Install nvm: https://github.com/nvm-sh/nvm
nvm install 18
nvm use 18

# Or upgrade Node.js directly
# See: https://nodejs.org/
```

### ⚠️ CRITICAL: Global packages lost after Node upgrade (nvm)

**If you use nvm and upgrade Node versions, all global packages are LOST!**

This is the most common issue users face. When you switch from Node 18 to Node 22, your `specweave` and `claude` commands will disappear.

**Symptoms:**
```bash
$ nvm use 22
# Now using node v22.0.0

$ specweave --version
bash: specweave: command not found

$ claude --version
bash: claude: command not found
```

**Solution 1: Reinstall packages (Quick Fix)**
```bash
# After switching to new Node version
nvm use 22

# Reinstall global packages
npm install -g specweave
npm install -g @anthropic-ai/claude-code

# Verify
specweave --version
claude --version
```

**Solution 2: Auto-copy during upgrade (Recommended)**
```bash
# Copy all global packages from Node 18 to Node 22
nvm install 22 --reinstall-packages-from=18

# Or after install:
nvm use 22
nvm reinstall-packages 18
```

**Solution 3: Backup/restore script (Best Practice)**
```bash
# BEFORE switching (save current globals)
npm list -g --depth=0 --parseable | sed '1d' | awk '{gsub(/.*\//,"",$1); print}' > ~/.nvm-global-packages.txt

# AFTER switching (restore globals)
nvm use 22
cat ~/.nvm-global-packages.txt | xargs npm install -g
```

**Why this happens:**

Each Node version managed by nvm has its own separate `node_modules` directory:
```
~/.nvm/versions/node/
├── v18.20.0/lib/node_modules/  ← Node 18 globals
├── v20.11.0/lib/node_modules/  ← Node 20 globals (empty!)
└── v22.0.0/lib/node_modules/   ← Node 22 globals (empty!)
```

**See detailed guide:** [Node Version Management Runbook](../../internal/operations/runbook-node-version-management.md)

### npm version too old

```bash
# Check version
npm --version

# Upgrade npm
npm install -g npm@latest

# Verify
npm --version
```

### Installation hangs or times out

```bash
# Clear npm cache
npm cache clean --force

# Try again with verbose logging
npm install -g specweave --verbose

# Or use npx instead
npx specweave init my-project
```

### .gitignore not created

```bash
# Manually create .gitignore
cat > .gitignore << 'EOF'
# Node
node_modules/
npm-debug.log
yarn-error.log
.pnpm-debug.log

# SpecWeave logs
.specweave/logs/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
EOF
```

## Platform-Specific Notes

### macOS

- ✅ Full support, all features work
- ✅ Hooks include notification sounds (Glass.aiff)
- ✅ Recommended platform for development

### Linux

- ✅ Full support, all features work
- ⚠️ Notification sounds may not work (requires audio system)
- ✅ Perfect for CI/CD and servers

### Windows

- ✅ Full support
- ✅ UNC paths supported (e.g., `\\Mac\Home\...`)
- ✅ Network drives supported
- ⚠️ Hooks may require WSL or Git Bash
- ⚠️ Notification sounds not supported

### WSL (Windows Subsystem for Linux)

- ✅ Full support, recommended for Windows users
- ✅ All Linux features available
- ✅ Better compatibility than native Windows

## Next Steps

After successful installation:

1. ✅ Watch the [4-min OpenCode Demo](../../academy/videos/005-opencode-web-calculator.mdx) — see the full workflow in action
2. ✅ Read the [Quick Start Guide](quickstart)
3. ✅ Review `CLAUDE.md` in your project
4. ✅ Explore [Core Concepts](../../overview/introduction)
5. ✅ Start your first increment

## Support

Need help? We've got you covered:

- **Quick Start:** [Quickstart Guide](quickstart)
- **Issues:** [GitHub Issues](https://github.com/anton-abyzov/specweave/issues)
- **Discussions:** [GitHub Discussions](https://github.com/anton-abyzov/specweave/discussions)
- **Documentation:** [verified-skill.com](https://verified-skill.com)
- **npm Package:** [npmjs.com/package/specweave](https://www.npmjs.com/package/specweave)

---

**SpecWeave** - Spec-Driven Development Framework

🚀 **Install now:** `npm install -g specweave`
