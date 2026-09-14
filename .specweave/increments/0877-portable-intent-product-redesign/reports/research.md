# Research decision — SpecWeave and Verified Skills

Date:2026-09-14. This report records the product decision; detailed source analysis, competitor evidence, before-state audit, and pilot criteria are in [product-research.md](product-research.md). Compared alternatives are in [brainstorm.md](brainstorm.md).

## Decision

Keep the products, with a narrower claim: portable intent and inspectable delivery evidence for SpecWeave; focused expertise, provenance, and measured usefulness for Verified Skills. A generic Kanban board and a large prompt catalog are weak businesses. Neither paid demand nor productivity improvement has been established by this engineering exercise.

The strongest potential user is someone who changes coding tools during substantial work. The durable record should answer what was requested, what passed, what remains, and which configuration did the work. Harness, model, effort, provider, and surface remain separate facts. OpenRouter normally belongs under provider/router. One conversation may contain several intents; one intent may span several conversations. A card represents an outcome, not automatically a transcript.

## Both requested articles, applied

OpenAI’s [skills and prompts article](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) supports narrower triggers, progressive disclosure, concise repository context, and removal of generic procedural scaffolding. It does not establish that every operational constraint or hook is obsolete. We removed unconditional greeting/test fixtures, duplicate and malformed installations, default per-tool interception, and automatic compaction capture; retained domain expertise and explicit continuation.

OpenAI’s [usage article](https://help.openai.com/en/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex) explains shared Work/Codex allowances and configuration-sensitive usage. A higher effort setting is not a universal quality guarantee. Subscription allowance cannot be converted into invented per-task spend. The board reads local files without invoking a model; unknown execution and pricing facts remain unknown.

## Architecture and product layers

1. Intent: short title, desired outcome, workflow state, optional increment reference. Small work can remain lightweight.
2. Specification and evidence: acceptance criteria, task ledger, verification status, evidence references, handoff. A card moved to Done must not fabricate a passed check or rewrite increment completion.
3. Execution history: declared configuration, ledger actors, and observed native session metadata, visibly distinguished. Explicit association prevents assigning an unrelated session to an intent merely because both share a directory.
4. Connections: optional GitHub/Jira/Azure DevOps mappings and health. The local workflow remains useful without an account or tracker.

The new board uses a local append-only intent file, authoritative task/spec reads, filesystem events, and a reconciliation poll. No cheap-model summarizer is required. Observed session adapters cache parsed metadata and read bounded log windows. Large logs are marked partial. Universal automatic transcript interpretation, controlled harness rankings, remote telemetry, and calibrated completion prediction are not implied.

## Integration decision

Keep integrations optional and visible in a dedicated product/docs area. Existing pull is a report of external changes; it is not a conflict-resolving bidirectional merge. The release fixes silent provider failures, preserves successful partial results, honors explicit GitHub targets, and exits unsuccessfully when the pull is incomplete. See [integration-failures.md](integration-failures.md).

Future reconciliation should use stable external IDs, a saved last-synced field snapshot, ownership rules per field, idempotent operations, per-provider cursors, and explicit conflicts when both sides change. Advance a provider cursor only after its batch is acknowledged. Retry failed providers without dropping successful batches. This algorithm is a design recommendation, not a shipped claim.

Linear, Jira, and Azure Boards already expose agent-oriented work primitives; competing as another generic tracker adds little value. SpecWeave should preserve evidence across those boundaries rather than recreate their enterprise planning UI. Primary references and platform-specific limits are in the detailed research.

## Cap, metrics, and prediction

SpecWeave2 already has advisory WIP limits, not a hard active-increment cap. `limits.activeIncrements:0` disables the advisory note. The new board does not impose a card cap. It emphasizes in-progress work, blocked/stale claims, completed tasks, and current verification.

A token count from unrelated tasks does not identify a superior harness. Use matched tasks, starting state, permissions, repeated trials, and outcome checks. Report cost coverage and source separately. Forecasting should wait for sufficient comparable completed work; a range with sample size and uncertainty is preferable to an invented completion date.

## Business validation and stop conditions

Run a four-week pilot with developers who actually switch tools. Compare against a short checked-in handoff document. Measure re-explaining time, forgotten acceptance criteria, reopened tasks, handoff time, and confidence in completion evidence. These are proposed measures, not observed improvements.

For skills, compare representative tasks with and without each skill using the same model/harness/effort and executable outcome checks. Retire instructions that add context and maintenance without repeatable benefit. Security/provenance evidence remains separate from usefulness.

Seek paid pilot commitments before building enterprise administration. If the board fails to outperform checked-in Markdown, retain a small interoperable CLI/state format and stop growing the UI. If skill evaluation yields no recurring benefit, narrow the registry to provenance and maintenance. If neither creates recurring user value, stop product expansion. Do not market unsupported productivity multipliers, universal model rankings, or guaranteed safety.
