# OpenClaw: Optimal Agent Workflow

> Internal guide — how we get the most out of OpenClaw for multi-project development.

## Two Modes of Operation

OpenClaw supports identity-based agents ("soul" files, personality, detailed persona). That works well for **non-project roles** — marketing, social media, promotion — where the agent's identity matters more than the codebase it touches.

For **project work** (development, implementation, code review), we use a different, more efficient pattern.

## The Project Agent Pattern

Instead of configuring per-person identity files, we use a thread-based setup where each conversation thread binds to an agent with a specific working folder and shared skills.

```
Slack thread  →  agent instance
                   ├── working folder: /path/to/project
                   ├── skills[]: global + project-specific
                   └── tools[]: Chrome profile, credentials, service accounts
```

### Why This Works Better

1. **No per-person training** — You don't configure Bob's agent differently from Alice's. They both use the same skills, pointed at the same project.
2. **Skills are capabilities, not identities** — A "marketing" skill lives globally. A "vskill-platform" skill lives at project level. No duplication.
3. **Environment is separate from config** — Chrome profiles with saved passwords, service accounts, browser state — these are tool-level concerns, not agent-level.
4. **Multi-project friendly** — Same person can work on vskill, vskill-platform, and specweave by starting threads pointed at different working folders. Same skills, different context.

### Setup

1. **Create a connection** (e.g., Slack integration) where each thread maps to an agent session
2. **Specify the working folder** — the agent starts in that project directory
3. **Skills load automatically** — global skills (marketing, analytics) + project-level skills (from `.specweave/` config)
4. **Drop a task** — paste a Jira ticket, ADO work item, GitHub issue link, or just describe the work
5. **Agent executes** — using all available SpecWeave skills (`/sw:increment`, `/sw:do`, `/sw:done`, etc.)

### What the Agent Gets

| Layer | Source | Example |
|-------|--------|---------|
| Working folder | Thread config | `/repos/anton-abyzov/vskill-platform/` |
| Global skills | Shared across all projects | marketing, analytics, social-media |
| Project skills | `.specweave/` in the working folder | project-specific workflows, domain skills |
| Tools | Per-environment config | Chrome profile with saved passwords, API keys |

### Task Input

The agent accepts tasks in any form:

- **Plain text**: "Implement the skill discovery API endpoint"
- **GitHub issue link**: Agent reads the issue and works from it
- **Jira/ADO link**: Agent extracts requirements and creates an increment
- **SpecWeave increment**: Agent picks up from `/sw:do`

## When to Use Identity-Based Agents Instead

For roles where **personality and voice matter more than codebase context**:

- **Marketing** — writing copy, managing campaigns, consistent brand voice
- **Social media** — posting schedules, engagement, tone consistency
- **Content creation** — blog posts, documentation with a specific style
- **Customer support** — response templates, escalation patterns

These roles benefit from OpenClaw's built-in identity system (soul files, personality config, detailed persona). The agent's identity IS the value — it maintains consistency across interactions.

## Key Principle

```
Project agents  = working_folder + skills[] + tools[]     (no identity needed)
Role agents     = identity + soul + skills[] + tools[]     (identity IS the product)
```

Don't mix them. Project agents should be lightweight and interchangeable. Role agents should be carefully crafted personas.

## Multi-Project Flow

Real workflow for a team working on multiple projects simultaneously:

```
Thread 1 → vskill CLI agent        → /repos/vskill/        → SpecWeave skills
Thread 2 → vskill-platform agent   → /repos/vskill-platform/ → SpecWeave skills
Thread 3 → marketing agent         → (no fixed folder)      → marketing identity + skills
Thread 4 → social media agent      → (no fixed folder)      → social identity + skills
```

Threads 1-2: Same developer, different projects, same skills, no identity config.
Threads 3-4: Different roles, identity matters, use soul files.

## Environment Isolation

Each agent session uses its own tool environment:

- **Chrome profile** — pre-configured with saved passwords for the relevant services
- **Service accounts** — API keys, tokens stored in the tools layer
- **Browser state** — logged-in sessions, cookies, bookmarks

The agent just invokes the tool. It doesn't need to know passwords — the Chrome profile already has them.
