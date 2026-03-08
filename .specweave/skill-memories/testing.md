# Testing Memory

<!-- Project-specific learnings for this skill -->

## Learnings

- **2026-03-08**: Playwright CLI-First Rule: always use Playwright CLI via Bash for test execution, setup, and automation. MCP Playwright tools are prohibited except for ui-inspect (interactive DOM introspection). Config: `testing.playwright.preferCli` in `.specweave/config.json`.
- **2026-03-08**: Skill evals must include negative/error scenarios (auth failures, missing dependencies, timeouts, permission denied)—missing error case coverage indicates insufficient quality assurance and hides real-world failure modes
