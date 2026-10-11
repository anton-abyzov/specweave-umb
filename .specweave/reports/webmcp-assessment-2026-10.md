# WebMCP: what it is and whether to care (2026-10-11, deep pass)

## Bottom line

**Don't build WebMCP into SpecWeave, Studio, the docs site or EasyChamp yet.** Four small things are worth doing, and one time-boxed opportunity needs a yes/no:

| # | Do | Effort | When |
|---|---|---|---|
| 1 | Record two EasyChamp rules: (a) the `ec-chat-api` assistant registry is the single agent contract and WebMCP/CLI/MCP are generated from it; (b) no agent write tools for payments, registrations or minors' data, ever | minutes | now |
| 2 | Send `Permissions-Policy: tools=()` on console.easychamp.com (stops third-party scripts like PostHog from registering tools under EasyChamp's origin) | < 1 h | now, low priority |
| 3 | Deprecate the stale `ec-mcp-server` / npm `easychamp-mcp` 0.1.0 (wrong base URL `sc-standings-api`, raw API key, ~239 generated tools incl. Stripe/PayPal) | ~0.5 day | next EasyChamp MCP touch |
| 4 | Fix verified-skill.com trust scores: canonical WebMCP skills (browserbase add-webmcp, webmcp-gen, GoogleChromeLabs) score 40 while mirror copies score 67-69 | ~0.5 day | now (registry bug, not WebMCP-specific) |
| **?** | **"State of WebMCP security" report + `vskill audit-webmcp <url>` CLI on verified-skill.com, published before TPAC (26-30 Oct)** | 2-3 days | **by ~24 Oct or drop** |

Everything else is trigger-gated (see "Triggers").

## What WebMCP is

A web page registers **tools** (name, description, JSON Schema input, a JS `execute` callback) that an AI agent inside the browser can call instead of reading the DOM and clicking. The tool runs in the page with the user's live session, so there is no server and no auth to build. It is the inverse of a normal MCP server.

- Spec: W3C Web Machine Learning **Community Group** draft, 9 Oct 2026; editors from Microsoft and Google. Not standards track.
- API (imperative only): `document.modelContext.registerTool(tool, { signal, exposedTo })`, `getTools()`, `executeTool()`; events `toolchange`, `toolactivated`, `toolcancel`. Unregister by aborting the signal.
- Annotations: `readOnlyHint`, `consequentialHint`, `untrustedContentHint` (all advisory).
- **Removed along the way**: `navigator.modelContext` (gone in Chrome 152), `provideContext`, `requestUserInteraction` (June), and the **declarative `<form toolname>` API, dropped from the spec on 8 Oct 2026** (Chromium keeps it behind a separate flag).
- No user-confirmation API exists in the spec. Issue #288 shows ChatGPT's browser calling a proposal tool and then clicking the page's own Approve button.
- Security: secure contexts only; `tools` Permissions Policy (default `self`); same-origin unless `exposedTo`. Threats the spec lists: tool poisoning via descriptions, injection via outputs, misrepresented intent, over-parameterization (PII harvesting). A June arXiv paper (2606.06387) shows third-party scripts hijacking or reframing a page's tools. Four Chrome CVEs in WebMCP code so far.

## Who actually uses it (verified Oct 2026)

**Correction to the first pass**, which said nothing calls WebMCP tools. Consumers that exist:

- **ChatGPT desktop app's built-in browser** ("site tools"), but only for ChatGPT Work and Codex with GPT-5.6/6 Sol; consumer ChatGPT is not included.
- **Playwright 1.64** (7 Oct 2026): `page.webmcp`, and Playwright MCP exposes page tools as `webmcp_<tool>` by default.
- **chrome-devtools-mcp** 1.10: `list_webmcp_tools` / `execute_webmcp_tool` behind `--categoryExperimentalWebmcp`.
- Brave Leo (flag), Stagehand, Puppeteer, Cloudflare Browser Run, Google's test extensions.
- **Not shipped**: Gemini in Chrome (still "will soon support" since I/O in May), Claude in Chrome (#30645 was a stale-bot close; #76809 open), Edge Copilot.

Supply side: **Shopify** gives every Liquid storefront tools automatically since August (allbirds.com registers 12, including `proceed_to_checkout` and `manage_orders`, none marked `consequentialHint`). Cloudflare (opt-in edge bridge) and Vercel `mcp-handler` 2.2 have bridges. A community crawl found 580 of 14,351 indexed sites registering tools, mostly search/read plugins.

Browsers: Chrome origin trial M149-156 (M156 stable 20 Oct); an extension to M162 (~Feb 2027) is pending with one LGTM, and the team hopes to send an Intent to Ship in that window. Edge OT to 30 Mar 2027. **WebKit formally opposes; Mozilla is neutral** and is pushing a redesign (generic function calling, `Tool` handle). TAG review is stalled on "missing multi-stakeholder support". TPAC (26-30 Oct, Dublin) is the next decision point, so expect API churn.

Discovery/SEO: none. No search or answer engine uses WebMCP. Lighthouse's experimental "Agentic browsing" category has three WebMCP audits but reports a pass fraction and does not affect Performance or SEO.

## Fit per surface

### EasyChamp

The real asset is not a web page. `ec-chat-api/services/assistant/registry.py` already holds **84 typed operations (33 read, 51 write)** with JSON Schema, risk level and scopes; writes become proposals that a person confirms in console, and Claude Code reaches it via the `ec-assistant` CLI (device-code pairing). `Operation.tool()` already emits nearly the WebMCP tool shape.

Ideas tested and **rejected by the skeptic pass**:
- *Read tools on watch.easychamp.com / league sites* (standings, fixtures, open play): standings and fixtures are server-owned data, so a plain MCP tool scores the same as WebMCP, with no browser needed. Parents and players can't reach WebMCP today (consumer ChatGPT doesn't have it). And EasyChamp's analytics `human-gate.ts` filters out exactly the agent traffic you'd want to count.
- *Project the registry onto console as WebMCP tools*: it weakens the safety model. An agent sitting in the signed-in tab can open the approval URL and press Confirm itself (#288). It would need step-up confirmation (passkey/re-auth). The headline flow "RSVP my kid" is also not supported: `club.attendance.rsvp` changes the signed-in user only (registry.py:308). Realistic cost is 2-3 weeks.
- *Free scheduling tools / sim as tools*: a deterministic schedule generator belongs in the registry/remote MCP (`competition.schedule.generate` exists), not WebMCP.

**The actual EasyChamp gap is a remote MCP server over the assistant gateway** (OAuth per the 2026-07-28 MCP auth spec), so claude.ai and ChatGPT connectors can reach the 84 operations, not just shell agents. That's 1-2 weeks: Keycloak has only experimental CIMD and no RFC 8707, so it needs a workaround. Start it when an organizer or partner asks for connector access.

### SpecWeave Studio

Consuming WebMCP is now cheap: bump `playwright-core` 1.60 → 1.64 and wrap `page.webmcp` as `preview_list_page_tools` / `preview_call_page_tool` in `apps/server/src/mcp/toolkits/preview/tools.ts`, mapping `readOnlyHint` to the read-only tier and `consequentialHint` to Studio's approval flow. 1-2 days. **But it's parity, not a differentiator** (Playwright MCP already does it), so don't market "Studio supports WebMCP".

Gotcha (verified headless): Playwright always passes `--enable-features=CDPScreenshotNewSurface`, and a later `--enable-features=WebMCP` silently replaces it (last wins). Use `--enable-features=CDPScreenshotNewSurface,WebMCP`. Playwright 1.64 refuses `page.webmcp` unless that literal flag is present; an origin-trial token isn't enough. For desktop `<webview>` tabs, prefer per-webview `enableblinkfeatures` over an app-wide switch.

### verified-skill.com / vskill

- No WebMCP tools on the site: agents already use `npx vskill` and the JSON API.
- The one genuinely ownable angle: **nobody scores whether a site's WebMCP surface is safe.** Known Good only lists tools; Lighthouse only checks that they exist and their schemas are valid; every MCP scanner targets server-side MCP. Headless enumeration already works (Chrome headless shell 153 + `--enable-features=WebMCP` + CDP `WebMCP.enable` / `getTools()`, no token, verified on allbirds.com). A `vskill audit-webmcp <url>` CLI that reuses the existing PI-001..004 prompt-injection patterns plus the tier-2 LLM pass can flag: write-shaped tools without `consequentialHint`, PII-shaped inputs, oversized descriptions, and missing `Permissions-Policy`. Attributing third-party scripts needs an init-script wrapper around `registerTool`; frameId/origin don't reveal it.
- Paired with a data-backed "State of WebMCP security" post before TPAC, this earns links and authority for the "trust layer for agent-facing surfaces" story. It won't bring skill installs; the audience is standards and site-owner people. Ask Shopify for comment and frame findings as a hint gap, not "Shopify is unsafe". Report counts, not ecosystem percentages, because the Known Good sample isn't random. **Worth it only inside the TPAC window; otherwise drop it.**
- Rejected: an API-drift rule pack (stale APIs fail loudly; regex on prose gives false positives), a curated WebMCP-skills page (it would surface the trust-40 anomaly), a paid monitoring tier (pricing tiers are still "planned"; Shopify merchants can't change their tools anyway), our own "add WebMCP" skill (Browserbase, Google, BuilderIO, webmcpify, TanStack and Playwright already ship them).

### spec-weave.com docs

No. Static Docusaurus with local search (`@easyops-cn/docusaurus-search-local`) and `llms.txt` already live. Server-owned content belongs to fetch, `llms.txt` or remote MCP.

### SpecWeave (CLI)

No code needed. `specweave verify --cmd` can already run a Lighthouse agentic-browsing check if a project wants one.

## How we can use WebMCP today with zero code

Claude Code can call WebMCP tools headlessly now through Playwright MCP (`webmcp_<tool>`) or `chrome-devtools-mcp --categoryExperimentalWebmcp`, launching Chromium with `--enable-features=CDPScreenshotNewSurface,WebMCP`. Add it per project only when a site we own registers tools, not globally, because it adds tool noise.

## Triggers to revisit

- **Gemini in Chrome ships WebMCP tool calls** (or Claude in Chrome via #76809), or **Chrome sends an Intent to Ship**: re-run the EasyChamp read-tool pilot, measured with a server-side beacon instead of PostHog. Add a third test arm (same functions as a plain MCP server) and kill WebMCP if that arm is within ~10%.
- **TPAC outcome (late Oct)**: if the API is reshaped into generic function calling, wait for the new shape.
- **First site we own that registers tools**: same PR adds Playwright `page.webmcp` contract tests (description ≤ 500 chars, output ≤ 1.5K, valid schema, tool output matches the UI) and Studio's page-tool wrapper.

## Sources

- [WebMCP draft spec (9 Oct 2026)](https://webmachinelearning.github.io/webmcp/) · [repo + issues #288, #322, #236, #338](https://github.com/webmachinelearning/webmcp)
- [Chrome WebMCP docs](https://developer.chrome.com/docs/ai/webmcp) · [Chrome at I/O 2026](https://developer.chrome.com/blog/chrome-at-io26) · [chromestatus 5117755740913664](https://chromestatus.com/feature/5117755740913664)
- [ChatGPT site tools](https://learn.chatgpt.com/docs/webmcp) · [Playwright 1.64 release](https://github.com/microsoft/playwright/releases/tag/v1.64.0) · [chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [WebKit position #670 (oppose)](https://github.com/WebKit/standards-positions/issues/670) · [Mozilla position #1412 (neutral)](https://github.com/mozilla/standards-positions/issues/1412)
- [Mid-Session Tool Injection, arXiv 2606.06387](https://arxiv.org/abs/2606.06387) · [State of WebMCP, July 2026](https://www.spronta.com/blog/state-of-webmcp-july-2026/)
- [Claude in Chrome requests #30645](https://github.com/anthropics/claude-code/issues/30645), [#76809](https://github.com/anthropics/claude-code/issues/76809)
- Local code: `ec-chat-api/services/assistant/registry.py`, `ec-arena-ui/src/lib/analytics/human-gate.ts`, `ec-mcp-server/src/client.ts`, `specweave-studio/apps/server/src/preview/ServerBrowserContexts.ts`, `vskill-platform/src/app/pricing/page.tsx`
