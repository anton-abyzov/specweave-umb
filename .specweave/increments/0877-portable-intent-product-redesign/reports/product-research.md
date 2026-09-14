# Product research and website audit

## Decision

Keep both products, but narrow their promises. SpecWeave should preserve intent, execution history, and verifiable progress across tools. Verified Skills should help people select, inspect, evaluate, update, and retire focused expertise. Neither product earns its place merely by coaching a capable model, counting instructions, or duplicating an issue board.

This is a product hypothesis supported by current technical capabilities and observed product gaps, not evidence of paid demand. No customer interviews, conversion analysis, or controlled user productivity study was performed in this work.

## Requested OpenAI sources

Both requested articles were read in full, including the usage article's allowance, effort, reset, availability, and troubleshooting sections.

Eric Provencher's September 11 article recommends precise skill triggers, progressive disclosure, context-specific repository instructions, and explicit completion boundaries. Broad descriptions, unnecessary prerequisites, and fixed recipes can consume context and obstruct more capable models. It also notes that shared instructions may serve different models; useful constraints cannot be removed solely because one model needs less guidance. Product implication: reduce generic scaffolding, preserve domain constraints, and evaluate upgrades against a baseline. [OpenAI, Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra).

The usage article separates model, reasoning effort, task size, speed mode, and plan allowances. Work and Codex share allowance; lower reasoning can be a sensible starting point, and higher effort does not guarantee better outcomes. Resets restore eligible usage windows rather than money or API credit. Missing information or access cannot be repaired by extra reasoning. Product implication: record configuration and measured usage, label unavailable data, and never convert subscription usage percentages into invented per-task dollar costs. [OpenAI Help Center, Managing usage with GPT-6 Astra in Work and Codex](https://help.openai.com/en/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex).

Neither article establishes that all hooks, skills, verification, or project tracking should disappear. That would be an unsupported generalization.

## Harness, model, and execution identity

Anthropic explicitly defines an agent evaluation as measurement of a harness and model together. It distinguishes the transcript from the actual final state, recommends repeated isolated trials, and favors deterministic graders where suitable. Checking the path too rigidly can reject valid solutions. This supports outcome-based evidence and controlled comparisons, rather than scoring agents by how closely they follow a predetermined sequence. [Anthropic, Demystifying evals for AI agents, January 9, 2026](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).

Anthropic's managed-agent architecture separately models a session as an append-only record, a harness as the model/tool loop, and a sandbox as the execution environment. It explicitly separates recoverable state from model-specific context management. That makes the continuity idea technically sound, although it also shows that providers are building competing primitives. [Anthropic, Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents).

Recommended execution identity:

| Dimension | Example | Meaning |
|---|---|---|
| Intent | Improve release reliability | User's desired outcome |
| Session | Provider-specific conversation ID | Conversation container; not necessarily one intent |
| Run | One bounded execution segment | A model or harness change starts a new segment |
| Harness | Codex, Claude Code, Cursor, DeepSeek harness | Agent loop, tools, and instruction environment |
| Model | Exact observed model ID | Model used for the run |
| Effort | Observed provider setting | Separate from model |
| Provider/router | OpenAI, Anthropic, OpenRouter, local endpoint | Where inference is served or routed |
| Surface | Desktop, terminal, VS Code | Where the operator works |
| Host/environment | Local checkout, worktree, remote runner | Where tools execute |

OpenRouter is normally a provider/router dimension, not automatically a harness. Do not classify every product into the same flat agent list. Preserve unknown values; never infer model names from a task title.

An intent may span multiple sessions, and one session may contain several intents. Board cards should represent the user's desired outcome. Linked increments supply specification and evidence, while sessions and runs show how work occurred. Small changes can have an intent without a full increment. A stop event is not proof of completion.

## Competition and enterprise integrations

Linear already exposes agent sessions with active, waiting, error, complete, and stale states; semantic activity updates drive session status. Sessions can link to external applications and pull requests, and a preview API supports session plans. Its existence reduces differentiation for a generic agent Kanban board. [Linear, Developing the Agent Interaction](https://linear.app/developers/agent-interaction).

Atlassian's September 9 documentation describes a preview remote-agent connector supporting Jira assignment, mentions, and chat. New integrations should use A2A 1.0, with synchronous and streaming modes. This is a useful future integration boundary rather than a reason to reproduce Jira inside SpecWeave. [Atlassian, Rovo Agent Connector](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-agent-connector/).

Azure Boards already supports starting GitHub Copilot from a work item, tracking progress, and linking branches and draft pull requests. The documented integration requires GitHub repositories and GitHub App authentication; it does not support Azure Repos. [Microsoft, Use GitHub Copilot with Azure Boards](https://learn.microsoft.com/en-us/azure/devops/boards/github/work-item-integration-github-copilot?view=azure-devops).

Recommendation: retain tracker integrations as opt-in adapters under a dedicated Integrations area. Their business purpose is traceability in a team's existing system, not broad autonomous synchronization. Each adapter needs explicit supported entities, direction, field ownership, conflict handling, retry state, and a last-success timestamp. Unsupported capabilities must be marked clearly. Local intent/evidence should remain usable if a remote tracker is unavailable.

Use stable external IDs and idempotency keys. Keep a delivery journal and reconciliation cursor. Separate polling or webhooks that observe remote changes from commands that write them. Present conflicts as a reviewable state; do not silently resolve concurrent edits by whichever system happened to write last. Broad claims of real-time bidirectional sync are premature without transport and conflict guarantees demonstrated end to end.

## Skill value and verification

The Agent Skills specification supports a common packaging format and progressive disclosure. A format does not prove usefulness or equal execution behavior across harnesses. [Agent Skills, Specification](https://agentskills.io/specification).

GitHub documents attestations as claims linking artifacts to their provenance. Attestations provide evidence that consumers must verify; they do not establish that software is secure. The same distinction applies to skills: provenance, content security, and task quality are separate dimensions. [GitHub, Artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations).

Retain skills with hard-won domain knowledge, project-specific operational constraints, reusable scripts, or meaningful tool integration. Candidate removals include unconditional greeting rules, duplicate routers, generic testing sermons, legacy model workarounds without current evidence, and overbroad triggers. Removal should be reversible and recorded; specialist knowledge should not be discarded merely because it is infrequently used.

Verified Skills needs to make a smaller installed set attractive. The product should answer: Which skill is relevant? Who wrote it? Which version was checked? What can it do? Does it help my task in my setup? What changed since installation? Remove or archive a skill when its context and maintenance costs exceed demonstrated value.

## Captured website audit

Public flows were captured with Playwright using explicit `headless: true`, `PWDEBUG=0`, and `PLAYWRIGHT_HTML_OPEN=never`. Desktop viewport: 1440×1000. Mobile viewport: 390×844. Screenshots are in `/tmp/specweave-product-audit-20260914/`. Files were opened and inspected. Full-page screenshots captured before scrolling can omit scroll-triggered content; reduced-motion and section captures were added for SpecWeave. Screenshots establish visual observations, not full accessibility compliance.

1. SpecWeave home → understanding the product. Working page and navigation, but the headline prioritizes specification ceremony and overnight autonomy. The hero contains no visible cross-tool handoff or authoritative progress example. Current title: “Stop Prompting. Start Specifying.”
2. SpecWeave proof and integrations → evaluating credibility. The page contains absolute claims such as “Living docs, always current, never drifts,” automatic ADR capture, one-day onboarding, and real-time bidirectional enterprise sync. These require evidence or narrower wording. The volume of skill and increment counts does not explain user benefit.
3. Verified Skills home → deciding what to install. Search works and the live catalog is useful, but authoring, installation, trust tiers, catalog totals, and a long video compete above the first substantive explanation. Nine desktop destinations have nearly equal emphasis.
4. `/skill-studio` → understanding the authoring product. This route says “Claude skills,” while `/studio` describes a broader product. It repeats an older landing page, includes different platform counts, and creates inconsistent search metadata.
5. `/studio` → evaluation workflow. Download and terminal paths exist. “Everything runs on your machine. No data leaves your environment” is too broad when selected cloud providers process model calls. Preserve local-workspace benefits with a clear boundary.
6. Mobile homes → scanning and navigating. Both captured pages fit the 390px viewport without horizontal overflow. That does not establish keyboard behavior, contrast compliance, or usability of every nested page.

Evidence files: `specweave-desktop.png`, `specweave-desktop-reduced-motion.png`, `specweave-step-1.png` through `specweave-step-3.png`, `specweave-mobile.png`, `verified-skills-desktop.png`, `verified-skills-mobile.png`, `skill-studio-desktop.png`, and `studio-main.png`.

## Information architecture and visual decisions

SpecWeave should offer a layered path: understand portability → see an intent board → inspect specification and evidence → see execution history → connect an optional tracker. Lead with continuing work across tools, not a prescribed agent ceremony. Active work, blocked work, completed evidence, and unfinished increment status should be immediately distinguishable.

Verified Skills should offer: discover focused expertise → inspect three evidence dimensions → evaluate in Studio → install and maintain. Keep the catalog and APIs intact, but move raw volume statistics beneath the product explanation. Give Studio one canonical product page. Move operational destinations such as Queue and Insights into Resources. Link the trust center to an explanation of what checks do and do not establish.

The chosen design direction is a restrained editorial layout: warm neutral surfaces, ink typography, a deliberate green accent, ample space around short statements, and dense data where it is useful. Generated Kie artwork illustrates inspection and continuity; it does not imitate measured UI or manufacture benchmark results. Interactive evidence tabs expose distinctions without another long page of introductory copy.

## Deterministic state and cost

Project state should be a deterministic projection of files, ledger events, explicit intent transitions, supported session telemetry, and completed checks. Watch file changes, read incremental logs, deduplicate events, and update the browser through server-sent events. This requires no recurring model calls.

An optional summarizer can propose a short intent title from a new request when the user chooses. Cache by input hash and identify the proposal's source. It must not silently decide completion or fabricate evidence. Inactivity is not failure, an agent's final message is not a passed test, and unchecked acceptance criteria cannot become completed merely because a session stopped.

Cost displays need source labels. Separate observed tokens, observed API charges, calculated estimates, and unavailable metrics. Subscription allowance is not directly attributable dollar spend. Provider caching, discounts, retries, and billing units make naive conversions misleading.

Completion forecasting should initially show throughput and cycle-time distributions from comparable completed work, with sample size and uncertainty. A confident release date without stable backlog scope and enough observed history would be decoration, not business value.

## Business case and kill criteria

Best initial audience: developers and small teams who frequently switch coding tools, or maintain reusable operational skills across those tools. Their plausible benefit is less re-explaining, fewer abandoned tasks, and faster assessment of what is really complete. Enterprise features are an extension for teams that already need governed tracker workflows.

Do not invest in a universal autonomous agent operating system. Do not compete mainly on catalog size, generic model advice, or cosmetic agent leaderboards. Defensible value must be portable state, reliable evidence, useful maintenance, and compatibility that people can verify.

Proposed validation targets below are decisions for a pilot, not measured results:

| Hypothesis | Pilot measurement | Stop or narrow when |
|---|---|---|
| Portable state removes handoff friction | Timed same-intent transfers between two harnesses; number of repeated explanations and missed requirements | Transfers are no better than a short checked-in handoff file |
| Board state is trustworthy | Random audit of cards against actual files, evidence, and agent activity | Incorrect completion or stale active state persists after fixes |
| Skills improve outcomes | Representative with/without trials on users' recurring tasks | Generic skills do not beat baseline; remove them from recommended sets |
| Maintenance has recurring value | Four-week repeated usage after initial cleanup | People use it once and never return; keep a small CLI rather than grow a service |
| Teams value enterprise sync | Successful pilot with actual Jira/ADO workflows and explicit willingness to pay | Connector maintenance exceeds usage or native workflows already solve the need |
| Commercial product is viable | Paid pilot commitments and demonstrated retention, not downloads or stars | No recurring demand after focused interviews and working pilots |

If continuity does not outperform checked-in Markdown, SpecWeave should become a small interoperable state/CLI tool. If skills do not produce repeatable improvement, Verified Skills should focus on provenance and safe maintenance rather than sell a claim of intelligence. If neither shows recurring user value, stop expanding the products.

## Exact implementation and release surfaces

SpecWeave repository: `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave`.

- Homepage: `docs-site/src/pages/index.tsx`.
- Sections: `docs-site/src/components/sections/{HeroSection,WhySpecFirstSection,HowItWorksSection,IntegrationsSection,TopSkillsSection}.tsx` and neighboring CSS modules.
- Shared style/config: `docs-site/src/css/`, `docs-site/docusaurus.config.ts`.
- Tests/build: `cd docs-site && npm test`; `npm run typecheck`; `npm run build`.
- Production deployment: `.github/workflows/deploy-docs.yml`, GitHub Pages artifact from `docs-site/build`; push trigger on `develop`, twice-daily schedule, or manual dispatch. Public URL: `https://spec-weave.com`.

Verified Skills implementation worktree: `/tmp/vskill-platform-0877-product`, based on fetched `origin/main` at `54535ca` before this task.

- Homepage: `src/app/page.tsx`; dynamic data from `src/lib/cron/stats-refresh.ts` and `src/lib/queue/queue-stats-cache.ts`.
- Search/catalog: `src/app/components/home/{HeroSearch,TrendingSkills,CategoryNav}.tsx`.
- Product/Studio: `src/app/studio/page.tsx`; older duplicate `src/app/skill-studio/page.tsx`.
- Navigation and theme: `src/app/layout.tsx`, `src/app/components/MobileNav.tsx`, `src/app/globals.css`.
- Trust: `src/app/trust/page.tsx` and its tab components.
- Tests/build: `npm test` (Vitest), `npm run build` (Next.js), `playwright.config.ts` and `tests/e2e/`.
- Build caveat: `next.config.ts` currently skips type and lint errors during build. A green build alone is not proof of TypeScript or lint correctness.
- Deployment: `npm run deploy` builds an OpenNext Worker, runs queue-health checks before/after `wrangler deploy`; configuration in `wrangler.jsonc`, worker/custom domains `verified-skill.com` and `www.verified-skill.com`.

## Sources

All web sources accessed September 14, 2026. Exact primary URLs are cited alongside the claims above. Product implementation findings come from local source files and the contemporaneous public-page captures. Product hypotheses and proposed validation targets are labeled separately from facts.
