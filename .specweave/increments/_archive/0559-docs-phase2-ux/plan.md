# Implementation Plan: Docs Phase 2: UX, Dual Activation, Plugin Accuracy, Team-Lead Section

## Overview

Documentation-only changes to the Docusaurus docs-site in the specweave repository. All modifications target existing markdown files and the sidebar configuration. No new pages are created; no application code is changed.

## Architecture

### Components Modified
- **docs-site/docs/reference/skills.md**: Fix plugin references, add dual activation, correct vskill commands
- **docs-site/docs/skills/fundamentals.md**: Correct plugin counts to match actual codebase
- **docs-site/docs/skills/installation.md**: Verify vskill install commands
- **docs-site/docs/workflows/overview.md**: Add dual activation tips, fix Mermaid emojis
- **docs-site/docs/guides/agent-teams-and-swarms.md**: Add dual activation for team-lead
- **docs-site/sidebars.ts**: Add team-lead entry to Agent Teams category
- **docs-site/docs/commands/overview.md**: Add natural language alternatives

### Data Sources (for verification)
- **specweave/.claude-plugin/marketplace.json**: 1 plugin (sw) with all skills unified
- **vskill/.claude-plugin/marketplace.json**: 5 plugins (mobile, skills, marketing, productivity, google-workspace)
- **specweave/plugins/specweave/skills/**: 44 actual skill directories

## Technology Stack

- **Framework**: Docusaurus v3 with Mermaid support
- **Language**: Markdown (MDX compatible)
- **Build**: `npm run build` in docs-site directory

**Architecture Decisions**:
- Keep all changes in existing files rather than creating new pages
- Use admonition blocks (:::tip) for dual activation examples for visual consistency
- Remove references to non-existent plugins rather than inventing placeholder descriptions

## Implementation Phases

### Phase 1: Plugin Accuracy (P1 - US-002, US-003)
Fix the most impactful inaccuracies first:
- Correct skills/fundamentals.md plugin counts
- Fix reference/skills.md plugin table and install commands
- Correct all vskill install command syntax

### Phase 2: Dual Activation (P1 - US-001)
Add dual invocation examples:
- Add to reference/skills.md core skill sections
- Add to workflows/overview.md phase commands
- Add to commands/overview.md quick reference

### Phase 3: Team-Lead & Navigation (P2 - US-004, US-005)
- Add sidebar entry for team-lead
- Add dual activation examples to agent-teams page

### Phase 4: Mermaid Fixes (P2 - US-006)
- Remove emoji from Mermaid node labels in workflows/overview.md

## Testing Strategy

- Verify Docusaurus build succeeds
- Visual inspection of modified pages
- Cross-reference plugin lists against actual marketplace.json files

## Technical Challenges

### Challenge 1: Plugin Table Accuracy
**Solution**: Cross-reference every plugin mentioned in docs against the actual marketplace.json files and plugin directories in both repos.
**Risk**: Some community plugins may have been removed. Mitigation: only list what exists in the codebase.
