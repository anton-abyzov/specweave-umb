---
status: completed
---
# Spec: Documentation Triple Invocation Pattern

## Overview

Update ALL public SpecWeave documentation to showcase three invocation methods for every skill/command, ordered by naturalness:

1. **Natural Language** (default, most prominent) - user just describes intent
2. **Claude Code** - slash command with `/sw:` prefix
3. **Other AI Tools** - command without prefix (Cursor, Copilot, Windsurf)

## User Stories

### US-001: CommandTabs Component
As a documentation reader, I want to see all three invocation methods in a clean tabbed interface so I can quickly find the method that matches my tooling.

**ACs:**
- [x] AC-US1-01: React component `CommandTabs` created at `src/components/CommandTabs/`
- [x] AC-US1-02: Uses Docusaurus design tokens (indigo-purple palette from tokens.css)
- [x] AC-US1-03: Three tabs: "Just say it", "Claude Code", "Other AI Tools"
- [x] AC-US1-04: "Just say it" tab is default/active
- [x] AC-US1-05: Dark mode support via `[data-theme='dark']`
- [x] AC-US1-06: CSS modules pattern matching existing components

### US-002: Getting Started & Overview Docs
As a new user, I want the first docs I read to show natural language as the primary invocation method.

**ACs:**
- [x] AC-US2-01: overview/introduction.md updated with triple invocation
- [x] AC-US2-02: getting-started/index.md uses CommandTabs for all examples
- [x] AC-US2-03: getting-started/first-increment.md uses CommandTabs
- [x] AC-US2-04: getting-started/installation.md mentions natural language capability

### US-003: Commands Documentation
As a developer, I want every command page to show all three invocation methods.

**ACs:**
- [x] AC-US3-01: commands/overview.md fully updated with CommandTabs
- [x] AC-US3-02: All individual command pages (do, auto, auto-status, cancel-auto, status, pause, resume, abandon, save, jobs) updated
- [x] AC-US3-03: Command tables include natural language column

### US-004: Guides Documentation
As a developer, I want guides to demonstrate the natural language-first approach.

**ACs:**
- [x] AC-US4-01: guides/brainstorming.md updated with CommandTabs
- [x] AC-US4-02: All guides with command examples use CommandTabs
- [x] AC-US4-03: Correct activation words used for each skill

### US-005: Academy, Workflows & Reference Docs
As a learner, I want academy tutorials to teach natural language invocation first.

**ACs:**
- [x] AC-US5-01: Academy essentials updated with CommandTabs
- [x] AC-US5-02: Workflow docs use triple invocation pattern
- [x] AC-US5-03: Reference/commands.md and reference/skills.md updated
- [x] AC-US5-04: Skills section index updated

### US-006: Enterprise & Integration Docs
As an enterprise user, I want enterprise docs to show all invocation methods.

**ACs:**
- [x] AC-US6-01: Enterprise release management docs updated
- [x] AC-US6-02: Skills fundamentals and installation docs updated

## Activation Words Reference

| Skill | Natural Language Triggers | Claude Code | Other AI |
|-------|--------------------------|-------------|----------|
| brainstorm | "brainstorm", "ideate", "explore ideas", "what are our options" | /sw:brainstorm | brainstorm |
| increment | "let's build", "I want to create", "add feature", [product descriptions] | /sw:increment | increment |
| do | "start implementing", "execute tasks", "continue working" | /sw:do | do |
| auto | "ship while I sleep", "autonomous mode", "run autonomously" | /sw:auto | auto |
| done | "we're done", "close it", "finish up" | /sw:done | done |
| progress | "what's the status?", "show progress", "how far along" | /sw:progress | progress |
| validate | "check quality", "validate it" | /sw:validate | validate |
| qa | "quality check", "assess quality" | /sw:qa | qa |
| grill | "review my work", "critique the code" | /sw:grill | grill |
| team-lead | "parallel agents", "team work" | /sw:team-lead | team-lead |
| architect | "design the system", "system architecture" | /sw:architect | architect |
| pm | "write specs", "define requirements" | /sw:pm | pm |
| sync-docs | "update the docs", "sync documentation" | /sw:sync-docs | sync-docs |
| tdd-cycle | "TDD", "test-driven development" | /sw:tdd-cycle | tdd-cycle |
| code-reviewer | "review code", "code review" | /sw:code-reviewer | code-reviewer |
| e2e | "e2e tests", "playwright tests" | /sw:e2e | e2e |
| pause | "pause this", "put on hold" | /sw:pause | pause |
| resume | "resume work", "continue where we left off" | /sw:resume | resume |
| abandon | "abandon this", "cancel increment" | /sw:abandon | abandon |
| jobs | "show background jobs", "check jobs" | /sw:jobs | jobs |
| next | "what's next", "next increment" | /sw:next | next |

## CommandTabs Component API

```tsx
import CommandTabs from '@site/src/components/CommandTabs';

<CommandTabs
  natural="Let's brainstorm how to handle authentication"
  claude='/sw:brainstorm "how to handle authentication"'
  other='brainstorm "how to handle authentication"'
/>
```

Props:
- `natural` (string, required): Natural language example
- `claude` (string, required): Claude Code slash command
- `other` (string, required): Non-Claude command (no sw: prefix)
