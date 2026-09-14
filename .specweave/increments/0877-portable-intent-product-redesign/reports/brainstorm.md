# Product direction decision

Decision: earn a place between user intent and verified delivery without duplicating the coding harness or the team's tracker.

Criteria fixed before selection: cross-tool continuity value, recurring user benefit, correctness without extra model calls, maintenance cost, and ability to validate with real users.

| Option | Continuity | Recurring benefit | Deterministic state | Maintenance | Kills it if |
|---|---|---|---|---|---|
| Keep the existing workflow | Medium | Unproven | Ledger already works | High accumulated surface | Existing false completion and stale guidance persist |
| Build a universal agent operating system | High ambition | Unproven | Depends on many adapters | Very high | Providers absorb the same control plane |
| Use Linear/Jira agent features only | Good inside supported products | Established planning value | Native events available | Low local maintenance | Users still lose intent when switching unsupported tools |
| Keep Markdown and a tiny CLI | High portability | Useful for disciplined teams | Strong | Low | Manual state management costs more than it saves |
| Intent and evidence workspace | High across tools | Plausible repeated value | Strong with ledger/watchers | Moderate | Board adds no value beyond checked-in handoff Markdown |
| Skills provenance and evaluation tooling | Complementary | Plausible for recurring expertise | Deterministic checks plus explicit eval runs | Moderate | Skills fail to beat unassisted model baselines |
| Shut down both products | None | Frees maintainer time | Not applicable | Minimal | Existing users demonstrably rely on reliable continuation |

## Pick

Ship an intent-and-evidence workspace with a tiny-CLI foundation; pair it with focused skills maintenance and evaluation. The dashboard is a projection of durable local state. The core remains usable without a dashboard, hosted account, tracker, or language-model inference. Skills are optional expertise, not a large mandatory prompt library.

The runner-up is a small Markdown/ledger CLI with no expanded product surface. The fact that would flip the decision is a timed pilot showing that the new board and execution history do not reduce re-explaining, missing requirements, or status-audit time compared with a short handoff document.

## Rejected directions

A generic agent board duplicates emerging Linear, Jira, and Azure Boards features. Universal orchestration and model-specific coaching create a costly race with harness providers. Blanket skill removal discards operational knowledge; reversible removal based on scope, duplication, and current usefulness is better. Killing Jira/ADO solely because their previous implementation was buggy would remove a plausible enterprise use without testing it; keep explicit optional connectors and show failures honestly.

## Pilot and stop conditions

Run the same multi-session work through two harnesses and measure repeated explanation, forgotten criteria, handoff time, reopened tasks, and correctness of board state. Compare with checked-in Markdown. For skills, repeat representative with/without trials using the same harness, model, effort, and fixtures. Use successful task outcomes first, tokens and estimated cost second. Collect paid pilot commitments before investing in enterprise administration. If neither continuity nor skills maintenance delivers recurring value, stop expanding and retain only useful open-source primitives.

These are proposed validation criteria, not measured customer outcomes. Current engineering checks establish software behavior, not market demand.
