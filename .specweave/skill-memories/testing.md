# Testing Memory

<!-- Project-specific learnings for this skill -->

## Learnings

- **2026-03-19**: Playwright CLI-First Rule: see `sw:playwright` skill for full guidance (trade-off table, CLI commands, YAML page layouts, six-phase QA flow). Config: `testing.playwright.preferCli` in `.specweave/config.json`.
- **2026-03-19**: Skill evals must include negative/error scenarios (auth failures, missing dependencies, timeouts, permission denied)—missing error case coverage indicates insufficient quality assurance and hides real-world failure modes
- **2026-03-19**: Integration tests executing Claude CLI commands that modify settings (plugin install/enable, settings.json writes) must use isolated temporary configurations or mocks, never real ~/.claude/ directories. Prevents environment pollution of user's actual settings and plugins.
