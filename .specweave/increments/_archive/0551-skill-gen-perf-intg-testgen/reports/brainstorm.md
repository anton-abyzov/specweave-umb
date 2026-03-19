# Brainstorm: Skill Generation, Test Case Gen, Docs & Competitive Research
**Date**: 2026-03-16 | **Depth**: deep | **Agents**: 3 parallel research | **Status**: complete

## Key Findings

### 1. Skill Generation Performance
- Current: single monolithic LLM call (12-30s CLI, 4-12s API)
- Batch generation (`generate-all.ts`) is sequential with 2s delays
- **Top optimization**: Split SKILL.md body + eval generation into parallel LLM calls (30-40% speedup)
- **Top optimization**: Parallelize batch generation with semaphore (3-5x for 10+ skills)
- **Top optimization**: Default to Anthropic API over CLI for batch ops (3x faster)
- Batch API is unused everywhere in the codebase — biggest single opportunity

### 2. Integration Test Generation (Missing Piece)
- Runner infrastructure exists (5-phase, Chrome profiles, credentials, cleanup)
- But NO auto-generation of integration test cases
- Proposal: Extend `buildEvalInitPrompt()` with integration test schema
- Auto-detect MCP dependencies → generate requiredCredentials, chromeProfile, cleanup blocks
- Generate outcome-based assertions (API status codes, resource existence) not text-judged
- Generate unit + integration in parallel LLM calls (Haiku for unit, Sonnet for integration)

### 3. Competitive Landscape
- Market is HOT: PromptFoo acquired by OpenAI ($86M), Braintrust at $800M, Humanloop by Anthropic
- **vSkill is genuinely unique**: skill-as-code + A/B baseline comparison + multi-model leaderboard
- Nobody else compares "with skill" vs "without skill" to prove skill adds value
- Browser integration tests would be truly novel — no competitor tests in real browser contexts
- Positioning: "The eval tool for the AI skill economy"

### 4. Documentation & Design
- Verified Skill platform (Next.js 15) already has `/docs` hub
- Extend with `/docs/eval/*` (8 sub-pages) + `/why-eval` marketing page
- Design system: Geist Sans/Mono, CSS variables (no Tailwind), dark/light
- Add Shiki syntax highlighting, callout components, sidebar TOC with scroll-spy
- Article concept: "Test AI Skills Like Software, Not Guesswork"

## Recommended Next Steps
1. `/sw:increment` for skill-gen performance + integration test generation
2. `/sw:increment` for `/docs/eval/*` pages on verified-skill.com
3. `/sw:increment` for `/why-eval` marketing landing page
4. Social media campaign based on competitive hooks
