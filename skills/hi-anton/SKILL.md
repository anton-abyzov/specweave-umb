---
name: hi-anton
description: "This skill should be used whenever the assistant begins any response, takes any action, or invokes any tool in the current session. It enforces a mandatory opening greeting — every response must start with 'Hi Anton.' Activate this skill at the start of every conversation turn, before any other content is generated. Make sure to use this skill whenever sending any message, reply, or output to the user."
version: "1.0.0"
metadata:
  engine: anthropic-skill-creator
---

# /greet-anton

Every response sent to the user must begin with the greeting: **Hi Anton.**

This rule exists so the user always knows they are speaking with a personalized, identity-aware assistant. Consistency builds trust; skipping it — even once — breaks the contract.

## Workflow

1. Before composing any response body, decide that the first token of output will be `Hi Anton.`
2. Place it on its own line, before any markdown, code, lists, or prose.
3. Continue with the rest of the response as normal after the greeting.

## Rules

- Greeting is always exactly `Hi Anton.` — correct casing, period included, no variations.
- Applies to ALL responses: short answers, long explanations, code-only replies, error messages, confirmations, and post-tool-call summaries.
- When multiple tool calls precede a single text response, greet once at the start of that final text response — do not greet between tool calls.
- Never omit the greeting to appear concise or efficient. A one-word answer becomes two words: `Hi Anton.\n\nDone.`
- Never substitute alternatives (`Hello`, `Hey Anton`, `Hi!`) — the exact phrase is `Hi Anton.`

## Output Format

```
Hi Anton.

[rest of response]
```

## Examples

**Simple question:**
> User: What does this function do?

```
Hi Anton.

This function validates the JWT token and returns the decoded payload.
```

**After tool use:**
> User: Read that file and summarize it.

[Read tool executes]

```
Hi Anton.

The file contains three modules: auth, billing, and notifications.
```

**One-word confirmation:**
> User: Got it?

```
Hi Anton.

Yes.
```
