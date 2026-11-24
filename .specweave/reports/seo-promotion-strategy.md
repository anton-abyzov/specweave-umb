# SpecWeave / Verified Skill: SEO and promotion strategy (2026-09-25)

Based on measured data in `seo-measured-data.md` (same folder). Numbers are measured unless marked as a target.

## Diagnosis
1. **Search engines can barely see us.** Neither domain is in Search Console. Google sent about 40 visits to spec-weave.com in 11 days. spec-weave.com is not in the top 20 for "spec driven development tools". The homepage title ("Change agents. Keep the thread.") contains none of the phrases people search for. spec-weave.com has only 172 URLs and 3 blog posts. It isn't listed in Engineering4AI/awesome-spec-driven-development (274 stars), which ranks #4 for that query.
2. **Launch spike, then decay.** specweave npm went from 26.3k/month (Mar) to about 3.2k/month. vskill went from 19.5k (Mar) to about 1.8k. Stars fell from 50/month (Feb) to 5-9. The category also cooled: Google Trends interest roughly halved after Jun 2026. So we lost share of a shrinking market.
3. **No distribution loop.** In 11 days the site got zero referrals from GitHub, npm, Reddit or X. The repo got 107 views in 14 days.
4. **Measurement is broken.** verified-skill.com has almost no beacon data. The spec-weave.com beacon only started on 2026-09-14. There's no conversion event (for example, copying the install command).

## Where the demand is (Keyword Planner, US monthly)
| Cluster | Keywords (volume) | Fit | Competition on the results page |
|---|---|---|---|
| A. Limits and switching (our wedge) | claude code usage limit (1K-10K), claude code vs codex (1K-10K, +900% YoY), switch from claude code to codex (10-100); autocomplete: "limit reached", "limits vs codex", "switch to codex/opencode/cursor/pi", "handoff to codex / new session / handoff.md" | Exact product fit, and no competitor owns it | Weak: Reddit threads, small GitHub repos (cc2codex, claude-codex-handoff), one blog, plus OpenAI's own import doc. Winnable. |
| B. Skills | claude code skills (10K-100K), agent skills (1K-10K, +9,900%) | verified-skill.com (about 6k skill and publisher pages already in the sitemap) | Unknown until Search Console is live |
| C. Spec-driven development comparisons | openspec (10K-100K, +99,900%), github spec kit (1K-10K), bmad method (1K-10K), spec driven development (1K-10K), spec driven development tools (100-1K); rising: openspec, context engineering, sdd | Comparison intent | Hard head-on: spec-kit has 139k stars, OpenSpec 70k, GSD 64k; SpecWeave has 164. Listicles rank (augmentcode, codemyspec, InfoWorld, martinfowler). |
| D. Instruction files | agents md (1K-10K), claude md (1K-10K); autocomplete "agents.md vs claude.md", "vs skills.md", "vs copilot-instructions.md" | SpecWeave writes both files | Medium |

Ad competition is "Low" everywhere. Top-of-page bids are mostly $3-8.

## Positioning
Stop competing as "another spec-driven development framework" (we lose to spec-kit and OpenSpec on stars). Own the phrase **"switch AI coding agents without losing context"**. SpecWeave then becomes the layer on top of whichever agent or spec tool you use. Keep "Change agents. Keep the thread." as the subhead. Put the searched words in the title and H1, for example: `SpecWeave: Spec-driven development that survives switching between Claude Code, Codex and Cursor`.

## Content plan (one page per cluster)
1. `/switch-claude-code-to-codex` (cluster A): "Hit your Claude Code usage limit? Continue in Codex in 60 seconds." Include a 60-second demo, the exact commands, and what gets carried over. Sibling pages: to Cursor and to OpenCode.
2. `/compare/*` (cluster C): honest comparisons of SpecWeave with OpenSpec, Spec Kit, BMAD, Kiro and GSD, each saying "use both". Move the existing `/docs/guides/specweave-vs-speckit` to `/compare/` and redirect the old URL.
3. `/agents-md-vs-claude-md` plus a short "SDD with Claude Code / Codex / Copilot" tutorial series (cluster D and the autocomplete "spec driven development with ...").
4. verified-skill.com (cluster B): "best Claude Code skills for X" category pages. Check indexing of the roughly 6k programmatic pages in Search Console first.
5. Add `llms.txt` to both sites (both return 404 today). Drop the GPTBot/Claude-Web crawl-delay: AI answer engines already send referrals (Gemini to spec-weave.com, ChatGPT to vskill).

## Distribution (faster than SEO)
- **Get listed:** PR to awesome-spec-driven-development and the awesome-claude-code lists. Pitch the authors of the ranking listicles (augmentcode, codemyspec, InfoWorld).
- **Reddit r/ClaudeCode and r/ClaudeAI:** these threads rank on Google for the handoff queries. Answer usage-limit threads with the working command and the demo, not a link dump.
- **YouTube (AI Power channel):** "Claude Code limit hit, continue in Codex". YouTube results show up in both results pages I checked.
- **Event-driven:** autocomplete shows "limits reduced / increased / boosted", so demand spikes whenever Anthropic changes limits. Keep the page and posts ready to fire on the next change.
- One Show HN about the handoff (not the framework).

## Paid test (only after measurement is fixed)
Google Search, US, exact and phrase match: claude code usage limit, claude code limit reached, claude code vs codex, switch from claude code to codex, openspec alternative, spec kit alternative. Budget $10-15/day for 3 weeks (about $300). Land on the switch page. Kill a keyword if CPC is over $5 or fewer than 2% of visitors copy the install command. Skip broad terms like "claude code" (huge volume, wrong intent).

## Metrics
| Metric | Baseline (measured) | 90-day target |
|---|---|---|
| Google clicks to spec-weave.com | about 40 per 11 days | 500/month |
| Search Console impressions (both sites) | not tracked | 10k/month |
| Average position for the 15 target keywords | not ranking | top 10 for all of cluster A |
| npm downloads specweave / vskill | about 3.2k / 1.8k per month | 2x |
| GitHub stars | 5-9/month | 30+/month |
| Referral visits from Reddit, YouTube, lists | 0 | tracked weekly |
| Install-command copies (new event, PostHog or Cloudflare) | none | primary conversion |

## First two weeks
1. Anton: verify both domains in Search Console (DNS TXT in Cloudflare) and submit the sitemaps. Add the beacon to verified-skill.com. Add an install-copy event.
2. Rewrite the homepage title, meta description and H1.
3. Ship the switch page, 5 comparison pages and the agents.md vs claude.md page.
4. Open the awesome-list PR. Record the 60-second video.
5. Start the ads test after steps 1-3.
