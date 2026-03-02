---
sidebar_position: 2
title: Plugin Ecosystem
description: Complete guide to SpecWeave's 20 plugins covering integrations, tech stacks, ML, infrastructure, and more
keywords: [plugins, skills, agents, commands, github, jira, kubernetes, react, ml, integration]
---

# 🧩 Plugin Ecosystem

SpecWeave's power comes from its **modular plugin architecture**. With **20 specialized plugins** (8 core SpecWeave + 12 tech-stack via vskill), you get enterprise-grade capabilities that activate automatically based on your project needs.

:::tip Key Insight
**Progressive Disclosure**: Only relevant plugins activate based on context. Working on React? Frontend plugin loads. Mention Kubernetes? Infrastructure plugin activates. This keeps your AI context lean and efficient.
:::

## 🎯 Quick Start

All plugins are **automatically installed** during `specweave init`:

```bash
npx specweave init .
# ✅ Installs all 20 plugins (GitHub, JIRA, React, ML, infra, etc.)
# ✅ Registers marketplace globally
# ✅ Ready to use immediately!
```

## 📊 Plugin Categories

### 🔧 Core Framework (Always Active)

#### **specweave** - Essential Framework
The foundation of SpecWeave, always loaded in every project.

**Key Capabilities:**
- 🎯 **24 Skills**: increment, pm, architect, spec-generator, tdd-cycle, grill, validate, judge-llm, team-lead, and more
- 🤖 **Role-Based Agents**: PM, Architect, Tech Lead, QA Lead spawn as subagents from skills
- ⚡ **28 Commands**: Full increment lifecycle management (do, done, progress, sync-docs, etc.)

**Example: Planning a New Feature**
```bash
# The PM agent (from core plugin) helps you create a spec
/sw:increment "User authentication with OAuth"

# Output: Creates spec.md, plan.md, tasks.md with:
# - User stories with acceptance criteria
# - Technical design with architecture
# - Task breakdown with embedded test plans
# - BDD format (Given/When/Then)
```

**Skills Highlight:**
- **increment**: Automatically activates when you say "plan feature", "new increment", "build X"
- **tdd-workflow**: Activates on "TDD", "test-driven", "red-green-refactor"
- **brownfield-analyzer**: Detects existing projects and maps documentation to SpecWeave structure

---

### 🔗 External Integrations

#### **specweave-github** - GitHub Issues Integration
Bidirectional sync between SpecWeave increments and GitHub Issues.

**Key Features:**
- ✅ Auto-creates issues on increment planning
- ✅ Task-level progress tracking (checkboxes)
- ✅ Universal Hierarchy: Epic → Milestone, Increment → Issue
- ✅ Smart conflict resolution

**Example: Auto-Sync Workflow**
```bash
# 1. Create increment (issue auto-created!)
/sw:increment "Add dark mode"
# 🔗 GitHub Issue #42 created automatically

# 2. Start work
/sw:do

# 3. Complete a task
# ✅ GitHub issue checkbox updates automatically!

# 4. Manual sync (if needed)
/sw-github:sync 0023 --time-range 1M
```

**Commands:**
- `/sw-github:sync` - Bidirectional sync with time range filtering
- `/sw-github:create-issue` - Manual issue creation
- `/sw-github:sync-epic` - Sync Epic folder to GitHub Milestone
- `/sw-github:status` - Check sync status

**Configuration:**
```json
{
  "sync": {
    "settings": {
      "autoCreateIssue": true,
      "syncDirection": "bidirectional"
    },
    "profiles": {
      "frontend": {
        "provider": "github",
        "config": {
          "owner": "myorg",
          "repo": "frontend"
        }
      }
    }
  }
}
```

---

#### **specweave-jira** - JIRA Integration
Enterprise JIRA integration with Epic/Story sync.

**Key Features:**
- ✅ Bidirectional Epic ↔ JIRA Epic sync
- ✅ User Stories ↔ JIRA Stories
- ✅ Status mapping (Planning → To Do, Active → In Progress)
- ✅ Multi-project support

**Example: JIRA Sync**
```bash
# Sync increment to JIRA
/sw-jira:sync 0042

# Sync Epic folder (20+ user stories)
/sw-jira:sync-epic FS-031-authentication

# Check status
/sw-jira:status 0042
```

**Status Mapping:**
```
SpecWeave          → JIRA
─────────────────────────────
planning           → To Do
active             → In Progress
paused             → On Hold
completed          → Done
abandoned          → Cancelled
```

---

#### **specweave-ado** - Azure DevOps Integration
Enterprise Azure DevOps sync with Work Items.

**Key Features:**
- ✅ Epic → Azure DevOps Epic
- ✅ Increment → User Story
- ✅ Tasks → Tasks with Area Paths
- ✅ Multi-project organization strategies

**Example:**
```bash
# Sync to Azure DevOps
/sw-ado:sync 0031

# Create work item manually
/sw-ado:create-workitem 0031

# Check sync status
/sw-ado:status 0031
```

---

#### **specweave-figma** - Figma Design Integration
Connect designs to implementation.

**Skills:**
- **figma-integration**: Extract design tokens, components, screens
- Converts Figma → React components
- Auto-generates prop types from Figma properties

---

### 💻 Tech Stack Plugins

#### **frontend** (`frontend@vskill`) - Frontend Development
React, Vue, Angular, Next.js expertise.

**Agents:**
- **frontend-architect**: Component architecture, state management patterns
- **react-expert**: Hooks, performance, modern patterns
- **nextjs-specialist**: SSR, ISR, routing, API routes

**Example: React Component Planning**
```bash
# Frontend architect activates automatically
"I need to build a reusable data table component with sorting and filtering"

# Generates:
# - Component architecture (container/presentational)
# - State management approach (useState, useReducer, Zustand)
# - Performance optimizations (React.memo, useMemo)
# - Accessibility (ARIA labels, keyboard navigation)
# - Test strategy (Jest, React Testing Library)
```

**Tech Stack Coverage:**
- React, Vue 3, Angular, Svelte
- Next.js, Nuxt, SvelteKit
- State Management: Redux, Zustand, Jotai, Pinia
- Styling: Tailwind CSS, Styled Components, Emotion

---

#### **backend** (`backend@vskill`) - Backend Development
Node.js, Python, .NET expertise.

**Agents:**
- **backend-architect**: API design, microservices, authentication
- **nodejs-expert**: Express, Fastify, NestJS patterns
- **python-expert**: Django, FastAPI, async patterns

**Example: API Design**
```bash
"Design RESTful API for user management with authentication"

# Backend architect generates:
# - OpenAPI/Swagger spec
# - Authentication strategy (JWT, OAuth2)
# - Database schema (PostgreSQL)
# - Rate limiting and caching
# - Error handling patterns
# - API versioning strategy
```

---

#### **mobile** (`mobile@vskill`) - Mobile Development
React Native and Expo expertise.

**Skills:**
- **react-native-expert**: Architecture, navigation, state, offline-first patterns, native modules, performance optimization

**Example:**
```bash
"Build offline-first mobile app with background sync"

# React Native expert provides:
# - React Native architecture
# - Offline data strategy (SQLite, Realm, WatermelonDB)
# - Background sync with NetInfo
# - Push notifications setup
# - Platform-specific considerations (iOS/Android)
```

---

### ☁️ Infrastructure & DevOps

#### **infra** (`infra@vskill`) - Infrastructure Engineering
Cloud infrastructure, DevOps, SRE, monitoring, K8s.

**Agents:**
- **devops**: CI/CD pipelines, cloud deployments
- **sre**: Incident response, troubleshooting, root cause analysis
- **observability-engineer**: Monitoring, logging, distributed tracing
- **network-engineer**: VPC, firewalls, load balancers

**Example: Production Incident**
```bash
"API response time increased to 5 seconds, CPU at 90%"

# SRE agent activates with:
# - Incident severity classification (SEV2)
# - Immediate mitigation steps
# - Root cause analysis checklist
# - Performance profiling strategy
# - Post-mortem template
```

**Playbooks:**
- High CPU Usage
- Database Deadlock
- Memory Leak Detection
- Slow API Response
- DDoS Attack Mitigation
- Disk Full Recovery
- Service Down Recovery
- Data Corruption
- Cascade Failure Prevention
- Rate Limit Exceeded

---

#### Kubernetes (part of `infra@vskill`)
Cloud-native K8s architecture, GitOps, service mesh. Bundled within the infra plugin.

**Agent:**
- **kubernetes-architect**: EKS/AKS/GKE, Helm, ArgoCD/Flux, Istio

**Example: K8s Setup**
```bash
"Deploy microservices to Kubernetes with GitOps"

# K8s architect provides:
# - Helm chart structure
# - ArgoCD/Flux configuration
# - Service mesh setup (Istio)
# - Multi-tenancy strategy
# - Monitoring with Prometheus/Grafana
# - Security policies (Network Policies, PSP)
```

---

### 🤖 Machine Learning & Data Science

#### **ml** (`ml@vskill`) - ML Engineering
Complete ML lifecycle from data to deployment.

**Agents:**
- **ml-engineer**: Model training, deployment, MLOps
- **data-scientist**: Statistical analysis, predictive modeling, EDA
- **mlops-engineer**: MLflow, Kubeflow, experiment tracking

**Commands:**
- `/sw-ml:pipeline` - Design complete ML pipeline
- `/sw-ml:evaluate` - Evaluate model with metrics
- `/sw-ml:deploy` - Generate deployment artifacts
- `/sw-ml:explain` - Model explainability (SHAP, LIME)

**Example: ML Pipeline**
```bash
# Design complete ML workflow
/sw-ml:pipeline "Customer churn prediction"

# Generates:
# 1. Data preprocessing (feature engineering, scaling)
# 2. Model training (XGBoost, Random Forest, Neural Network)
# 3. Hyperparameter tuning (Optuna)
# 4. Model evaluation (precision, recall, F1, ROC-AUC)
# 5. MLflow experiment tracking
# 6. Model registry and versioning
# 7. Deployment (FastAPI, Docker, Kubernetes)
# 8. Monitoring (data drift, model performance)
```

**Tech Stack:**
- Frameworks: TensorFlow, PyTorch, scikit-learn, XGBoost
- MLOps: MLflow, Kubeflow, Weights & Biases
- Deployment: FastAPI, TorchServe, TFServing
- Monitoring: Evidently AI, WhyLabs

---

### 💳 Specialized Domains

#### **payments** (`payments@vskill`) - Payment Integration
Stripe, PayPal, payment processor expertise.

**Agent:**
- **payment-integration**: Checkout flows, webhooks, PCI compliance

**Example:**
```bash
"Implement Stripe subscription billing"

# Payment integration agent provides:
# - Stripe Checkout setup
# - Subscription lifecycle management
# - Webhook handling (payment_intent.succeeded)
# - Invoice generation
# - Failed payment retry logic
# - PCI compliance checklist
```

---

### 📚 Documentation & Diagrams

#### **specweave-docs** - Documentation & Preview
Documentation generation, organization, and live Docusaurus preview with hot reload.

**Commands:**
- `/sw-docs:view` - Launch interactive docs server (internal or public)
- `/sw-docs:build` - Build static site for deployment
- `/sw-docs:generate` - Generate documentation
- `/sw-docs:organize` - Organize large doc folders
- `/sw-docs:health` - Documentation health report
- `/sw-docs:validate` - Validate documentation (MDX, YAML, links)

**Example:**
```bash
# View internal docs (default) - port 3015
/sw-docs:view

# View public docs - port 3016
/sw-docs:view --public

# Output:
# 🚀 Server running at http://localhost:3015 (or 3016 for public)
# 📁 Auto-generated sidebar from .specweave/docs/
# 🔄 Hot reload enabled
# 📊 Mermaid diagrams rendered
```

---

#### **specweave-diagrams** - Diagram Generation
Mermaid diagrams following C4 Model conventions.

**Agent:**
- **diagrams-architect**: C4 Context/Container/Component, sequence, ER diagrams

**Example:**
```bash
"Create C4 Container diagram for microservices architecture"

# Generates:
```mermaid
graph TB
    User[User]
    WebApp[Web Application]
    API[API Gateway]
    AuthService[Auth Service]
    UserService[User Service]
    DB[(Database)]

    User -->|HTTPS| WebApp
    WebApp -->|REST| API
    API -->|gRPC| AuthService
    API -->|gRPC| UserService
    UserService -->|SQL| DB
```
```

---

### 🚀 Release Management

#### **specweave-release** - Release Orchestration
Multi-repo releases, semantic versioning, RC workflows.

**Agents:**
- **release-manager**: Coordinates releases across monorepo/polyrepo

**Commands:**
- `/sw-release:init` - Initialize release strategy
- `/sw-release:align` - Align versions across repos
- `/sw-release:rc` - Manage Release Candidate lifecycle
- `/sw-release:platform` - Multi-repo platform releases

**Example:**
```bash
# Initialize release strategy
/sw-release:init
# Analyzes git history, CI/CD configs, recommends strategy

# Create Release Candidate
/sw-release:rc create v1.5.0-rc.1

# Promote to production
/sw-release:rc promote v1.5.0-rc.3
```

---

### 🎨 UI Testing & Automation

#### Browser Automation (part of `testing@vskill`)
Playwright integration with MCP protocol. Bundled within the testing plugin.

**Features:**
- Browser automation for E2E testing
- Visual regression testing
- Accessibility testing
- Performance monitoring

---

### 🔧 Utilities

#### Cost Optimization (built into core)
Tracks AI costs, suggests optimizations. Available via core plugin context management.

**Features:**
- Cost tracking per increment
- Model selection recommendations (Sonnet vs Haiku)
- Context optimization suggestions

---

## The Skills Ecosystem Fragmentation Problem

Before diving into how SpecWeave's plugins work together, it's worth understanding a real problem in the broader skills ecosystem: **duplication and fragmentation**.

Skills can be defined in different repositories, published through different channels (standalone skills vs plugins), and there's no single source of truth. This is already happening — even at Anthropic.

Take the `frontend-design` skill. It exists in two different Anthropic repos:

| Location | How You Get It |
|----------|----------------|
| [`anthropics/skills`](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) | Install as a standalone skill |
| [`anthropics/claude-code`](https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/skills/frontend-design/SKILL.md) | Comes bundled in a plugin |

Same skill, two repos. If you install the standalone skill AND the plugin, you get duplicates loaded into context. If the two copies diverge over time, you get inconsistent behavior depending on which one Claude picks up.

This fragmentation compounds across the ecosystem — community skills, marketplace plugins, vendor-published skills, GitHub repos — all with no coordination. It's the early days of npm and pip all over again, but with the added complexity that skills are natural language instructions rather than versioned code packages.

SpecWeave addresses this through its plugin marketplace architecture: skills are namespaced (`plugin:skill`), deduplicated on install, and version-pinned in lockfiles. The [vskill](https://github.com/anton-abyzov/vskill) installer handles the messy reality so you don't have to.

---

## 🎯 How Plugins Work Together

### Example: Full-Stack Feature Implementation

```bash
# 1. PM Agent (Core) creates spec
/sw:increment "Real-time chat feature"

# 2. Architect Agent (Core) designs system
# - WebSocket architecture
# - Database schema (PostgreSQL)
# - Caching strategy (Redis)

# 3. Frontend Agent (Frontend Plugin) designs UI
# - React components
# - State management (Zustand)
# - WebSocket client

# 4. Backend Agent (Backend Plugin) designs API
# - WebSocket server (Socket.io)
# - Authentication (JWT)
# - Message persistence

# 5. K8s Agent (Infrastructure Plugin) plans deployment
# - Helm charts
# - Horizontal Pod Autoscaler
# - Ingress configuration

# 6. GitHub Agent (GitHub Plugin) creates issue
# - Auto-creates GitHub Issue #84
# - Links to increment

# 7. Start implementation
/sw:do

# 8. All agents collaborate during implementation!
```

---

## 📈 Token Efficiency

**Context Optimization in Action:**

| Scenario | Active Plugins | Token Usage |
|----------|----------------|-------------|
| **Planning Only** | Core | ~12K tokens |
| **React Feature** | Core + Frontend | ~18K tokens |
| **Full-Stack API** | Core + Frontend + Backend | ~24K tokens |
| **ML Pipeline** | Core + ML + Infrastructure | ~28K tokens |
| **Enterprise (All)** | All 20 plugins | ~30K tokens |

**Result**: 75% smaller than monolithic architecture!

---

## 🔍 Finding the Right Plugin

| I want to... | Use Plugin | Key Command |
|-------------|-----------|-------------|
| Plan increment | **specweave** | `/sw:increment` |
| Execute tasks | **specweave** | `/sw:do` |
| Quality review | **specweave** | `/sw:grill` |
| Sync to GitHub | **specweave-github** | `/sw-github:push` |
| Build React app | **frontend** | Auto-activates on keywords |
| Build API | **backend** | Auto-activates on keywords |
| Deploy infra / K8s | **infra** | Auto-activates on keywords |
| Create ML pipeline | **ml** | Auto-activates on keywords |
| Integrate Stripe | **payments** | Auto-activates on keywords |
| Manage releases | **specweave-release** | `/sw-release:init` |
| Find skills | **skills** | `/skills:scout` |

---

## 🚀 Quick Reference: All 20 Plugins

### SpecWeave Core Plugins (8)

| Plugin | Install Name | Purpose |
|--------|-------------|---------|
| **specweave** | `sw@specweave` | Core framework: 24 skills, 28 commands, increment lifecycle |
| **specweave-github** | `sw-github@specweave` | GitHub sync: bidirectional issues, auto-creation |
| **specweave-jira** | `sw-jira@specweave` | JIRA sync: Epic/Story mapping, status sync |
| **specweave-ado** | `sw-ado@specweave` | Azure DevOps: work items, multi-project |
| **specweave-docs** | `sw-docs@specweave` | Documentation: Docusaurus preview, hot reload |
| **specweave-diagrams** | `sw-diagrams@specweave` | Diagrams: Mermaid, C4 Model |
| **specweave-release** | `sw-release@specweave` | Release mgmt: semantic versioning, RC workflow |
| **specweave-media** | `sw-media@specweave` | Media: AI image generation, assets |

### Tech Stack Plugins (12, via vskill)

| Plugin | Install Name | Purpose |
|--------|-------------|---------|
| **frontend** | `frontend@vskill` | React, Vue, Angular, Next.js |
| **backend** | `backend@vskill` | Node.js, Python, .NET, APIs |
| **mobile** | `mobile@vskill` | React Native, Expo, offline-first |
| **infra** | `infra@vskill` | DevOps, SRE, K8s, monitoring, CI/CD |
| **testing** | `testing@vskill` | Playwright, Vitest, TDD |
| **ml** | `ml@vskill` | MLOps, pipelines, deployment |
| **payments** | `payments@vskill` | Stripe, PayPal, PCI compliance |
| **kafka** | `kafka@vskill` | Kafka, event streaming |
| **skills** | `skills@vskill` | Skill discovery (scout) via verified-skill.com |
| **blockchain** | `blockchain@vskill` | Web3, smart contracts, DApps |
| **confluent** | `confluent@vskill` | Confluent platform, Schema Registry |
| **security** | `security@vskill` | Security analysis, OWASP, vulnerability scanning |

---

## 💡 Tips for Maximum Efficiency

### 1. Trust Progressive Disclosure
Don't manually load plugins. Let skills activate based on context:
- Say "React" → Frontend plugin activates
- Say "Kubernetes" → Infrastructure plugin activates
- Say "ML pipeline" → ML plugin activates

### 2. Use Context Optimizer
For large projects with 100+ files:
```bash
"Optimize context for authentication feature"
# Context optimizer removes 80% irrelevant specs/modules
```

### 3. Leverage Command Shortcuts
```bash
# Planning
/sw:increment → /sw:do → /sw:done

# Quality
/sw:validate → /sw:qa → /sw:check-tests

# Sync
/sw-github:sync → /sw:sync-docs
```

### 4. Multi-Project Setup
```json
{
  "sync": {
    "profiles": {
      "frontend": {"provider": "github", "config": {"repo": "frontend"}},
      "backend": {"provider": "github", "config": {"repo": "backend"}},
      "mobile": {"provider": "github", "config": {"repo": "mobile"}}
    }
  }
}
```

---

## 🎓 Learning Resources

- **[Getting Started Guide](/docs/intro)** - Installation and first increment
- **[Workflows](/docs/workflows/overview)** - Complete development journey
- **[Commands Reference](/docs/commands/overview)** - All essential commands
- **[Multi-Project Sync](/docs/integrations/multi-project-sync)** - GitHub/JIRA/ADO setup
- **[FAQ](/docs/faq)** - Common questions answered

---

## 🔧 Extensibility via CLAUDE.md

SpecWeave is a **framework, not a locked product**. Beyond plugins, you can customize behavior through your project's `CLAUDE.md` file:

### Custom Sync Rules
```markdown
## Sync Customization
When syncing to JIRA, always:
- Add custom field "Team: Backend" for backend increments
- Map "paused" status to "Blocked" instead of "On Hold"
- Include sprint field using our sprint naming convention (SPRINT-YYYY-WW)
```

### Custom Quality Gates
```markdown
## Quality Gates
Before closing any increment:
- Run `npm run lint:strict` in addition to tests
- Verify CHANGELOG.md entry exists for the feature
- Check that OpenAPI spec is regenerated if API changed
- Ensure Sentry release is tagged
```

### Custom Workflow Hooks
```markdown
## Workflow Automation
After completing a task:
- Post notification to #dev-updates Slack channel
- Update team capacity spreadsheet via webhook
- Trigger downstream pipeline if it's an API change
```

### Agent Behavior Overrides
```markdown
## Agent Customization
When the PM agent creates specs:
- Always include compliance section for HIPAA requirements
- Add "Data Classification" field to every user story
- Reference our design system component library

When the Architect agent designs:
- Prefer PostgreSQL over MySQL for new services
- Always include rate limiting in API designs
- Use our standard error response format
```

**What you can customize:**
| Area | Examples |
|------|----------|
| **External Sync** | Add fields, transform statuses, integrate with internal tools |
| **Quality Gates** | Custom validation, linting rules, security scans, compliance checks |
| **Lifecycle Hooks** | Trigger actions on events (created, done, paused, archived) |
| **Agent Behavior** | Override default prompts, add domain-specific requirements |
| **Naming Conventions** | Enforce team-specific ID formats, branch names, commit messages |
| **Integration Logic** | Custom webhook payloads, API transformations, field mappings |

---

## 🤝 Contributing

Want to add a new plugin? See [CLAUDE.md](https://github.com/anton-abyzov/specweave/blob/develop/CLAUDE.md) for plugin development guide.

**Plugin Ideas Welcome:**
- Cloud providers (AWS, GCP, Azure)
- Languages (Go, Rust, Java)
- Frameworks (Spring Boot, Django, Rails)
- Databases (MongoDB, Redis, Cassandra)
- Testing tools (Cypress, Playwright)

---

:::tip Next Steps
1. ✅ Install: `npx specweave init .`
2. 🎯 Plan: `/sw:increment "Your feature"`
3. ⚡ Implement: `/sw:do`
4. 🔗 Sync: `/sw-github:sync`
5. ✅ Complete: `/sw:done`

**All 20 plugins are ready to help you build faster!**
:::
