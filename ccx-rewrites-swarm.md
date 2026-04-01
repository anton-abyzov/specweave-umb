# CCX Rewrites -- Parallel Agent Swarm Instructions

Run these three in parallel via cowork or agent swarm. Each agent gets one repo.

## Agent 1: Go (PRIORITY 1 -- start first)

**Repo**: https://github.com/anton-abyzov/ccx-go
**Local**: /Users/antonabyzov/Projects/github/ccx-go
**Spec**: SPEC.md in repo root

**Instruction for agent:**
```
You are building ccx-go -- a Go implementation of an AI coding assistant CLI.

Read SPEC.md for the full implementation plan.
Read README.md for architecture overview.

Start with Phase 1: Foundation (P1-01 through P1-04).

Key constraints:
- TDD: Write tests first (go test), then implement
- Use Cobra for CLI, Bubbletea for TUI, stdlib net/http for API
- No CGO -- pure Go for cross-compilation
- All API types need proper struct tags for JSON
- Start with the Claude API streaming client (P1-02) -- everything depends on it

Reference: Use publicly documented API specifications and the architecture analysis at https://verified-skill.com/insights/claude-code for understanding API formats, tool schemas, and protocol details.

After Phase 1, proceed to Phase 2 (core tools), then Phase 3 (TUI).
```

## Agent 2: Rust (PRIORITY 2)

**Repo**: https://github.com/anton-abyzov/ccx-rs
**Local**: /Users/antonabyzov/Projects/github/ccx-rs
**Spec**: SPEC.md in repo root

**Instruction for agent:**
```
You are building ccx-rs -- a Rust implementation of an AI coding assistant CLI built on OpenAI Codex's Apache-2.0 infrastructure crates.

Read SPEC.md for the full implementation plan.
Read README.md for architecture overview.

IMPORTANT: Before writing any code, clone openai/codex and identify the exact crates to extract:
  git clone --depth 1 https://github.com/openai/codex.git /tmp/codex-ref
  ls /tmp/codex-ref/codex-rs/crates/

Start with Phase 1: Fork and Adapt (P1-01 through P1-04).

Key strategy:
- Extract reusable crates from Codex (sandboxing, tui, exec, file-search, git-utils, etc.)
- Build new Claude-specific crates (claude-api, claude-core, claude-auth, claude-tools)
- TDD: cargo test for every module
- Start with claude-api crate (P1-02) -- the streaming client is the foundation

Codex reference: https://github.com/openai/codex (Apache-2.0)
Architecture analysis: https://verified-skill.com/insights/claude-code
```

## Agent 3: .NET (PRIORITY 3)

**Repo**: https://github.com/anton-abyzov/ccx-dotnet
**Local**: /Users/antonabyzov/Projects/github/ccx-dotnet
**Spec**: SPEC.md in repo root

**Instruction for agent:**
```
You are building ccx-dotnet -- a .NET 10 implementation of an AI coding assistant CLI.

Read SPEC.md for the full implementation plan.
Read README.md for architecture overview.

Start with Phase 1: Foundation (P1-01 through P1-04).

Key constraints:
- AOT-compatible from day one: PublishAot=true, no reflection
- Source-generated JSON serialization (JsonSerializerContext)
- Spectre.Console for ALL terminal output (testable via IAnsiConsole)
- TDD: xUnit + FluentAssertions
- Start with solution scaffold (P1-01) then API client (P1-02)

Architecture analysis: https://verified-skill.com/insights/claude-code
```

## Swarm Execution

### Via Claude Code Cowork
Run each agent in a separate terminal/session:
```sh
# Terminal 1 -- Go (priority)
cd /Users/antonabyzov/Projects/github/ccx-go
claude "Read SPEC.md and implement Phase 1. Start with P1-02 (API client). TDD required."

# Terminal 2 -- Rust
cd /Users/antonabyzov/Projects/github/ccx-rs
claude "Read SPEC.md and implement Phase 1. Clone Codex crates first (P1-01), then build claude-api (P1-02). TDD required."

# Terminal 3 -- .NET
cd /Users/antonabyzov/Projects/github/ccx-dotnet
claude "Read SPEC.md and implement Phase 1. Scaffold solution (P1-01) then build API client (P1-02). TDD required. AOT-compatible."
```

### Via SpecWeave Team Lead
```
/sw:team-lead "Implement Phase 1 of all three Claude Code rewrites in parallel.
Agent 1 (Go): /Users/antonabyzov/Projects/github/ccx-go -- SPEC.md Phase 1
Agent 2 (Rust): /Users/antonabyzov/Projects/github/ccx-rs -- SPEC.md Phase 1
Agent 3 (.NET): /Users/antonabyzov/Projects/github/ccx-dotnet -- SPEC.md Phase 1
Each agent should read SPEC.md, implement P1-01 through P1-04 with TDD.
Reference source at /Users/antonabyzov/Projects/claude-code-src/"
```

## Progress Tracking

| Phase | Go | Rust | .NET |
|-------|-----|------|------|
| P1-01: Scaffold | [ ] | [ ] | [ ] |
| P1-02: API Client | [ ] | [ ] | [ ] |
| P1-03: Tool Interface | [ ] | [ ] | [ ] |
| P1-04: Query Loop | [ ] | [ ] | [ ] |
| P2-01: Bash Tool | [ ] | [ ] | [ ] |
| P2-02: File Tools | [ ] | [ ] | [ ] |
| P2-03: Search Tools | [ ] | [ ] | [ ] |
| P2-04: Web Tools | [ ] | [ ] | [ ] |

## Cross-Reference

- OpenAI Codex (Apache-2.0): https://github.com/openai/codex
- oh-my-codex (MIT, orchestration patterns): https://github.com/Yeachan-Heo/oh-my-codex
- Architecture analysis: https://verified-skill.com/insights/claude-code
