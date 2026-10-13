# SpecWithCode traffic plan

12 October 2026. Goal: grab a lot of traffic first, then promote. Research sources are in the "Sources" section; claims marked (est.) come from vendor or secondary sources.

## Where we start

| Signal | Today |
|---|---|
| `specweave` on npm | 26,123 downloads in the last 30 days |
| SpecWeave on GitHub | 165 stars, 21 forks |
| SpecWithCode .dmg downloads | single digits per release (v1.0.0–v1.0.3, all published 12 Oct) |
| spec-weave.com/studio | download page live, still says version 1.0.0 |
| Gatekeeper | `spctl` rejects the app: it is signed with an Apple Development certificate, not notarized |

The npm audience is the asset. SpecWithCode has almost no installs yet, so the first job is to make the install path friction-free and then point the existing SpecWeave audience at it.

## Decision: new business account or email?

Do not buy a business account. Make three cheap moves:

1. **Brand email: yes, for $0.** Forward `hello@` and `support@` on the product domain to Gmail with Cloudflare Email Routing (free), and send through Resend's free tier. Product Hunt, directories, press and support need a contact address that is not a personal Gmail. Take Google Workspace ($7–8.40 per user per month, est.) only if you want a separate mailbox and calendar.
2. **Domain: buy `specwithcode.dev` (about $12 a year, est.) if it is still free.** It is pending in project memory. Until then, spec-weave.com/studio is the canonical URL, and every video uses it.
3. **Brand handles: reserve, do not post from them.** Claim @specwithcode on X, YouTube, Threads/Instagram and LinkedIn (company page), all free. Post from your own accounts:
   - Product Hunt prohibits company accounts; the maker must be you.
   - Hacker News discourages creating accounts for promotion; founder posts are the norm.
   - LinkedIn company pages get a fraction of a personal profile's reach (est. 1.6% of followers).
   - The X gold check (Premium Business, $200 a month) is not worth it before traction.

Nothing here was bought or created. Each of the three needs your go-ahead.

## Fix the path before sending traffic

These matter more than any channel. A Show HN that hits "macOS says this app is damaged" loses most of its clicks.

1. **Notarize the app.** EasyChamp, Inc. already has a paid Apple developer team (`NMCB2JZ7QG`). Create a "Developer ID Application" certificate under it and notarize in the release workflow. No new purchase. The account holder has to create the certificate; it is free.
2. **Update the download page** to the current release (the production-readiness thread owns the site).
3. **Answer "is it open source?" before HN asks.** The README says MIT, and the release repo `anton-abyzov/specwithcode` is public, but the app source (`specweave-studio`) is private. Either publish the source or say plainly: "free, closed-source app on top of the open-source SpecWeave CLI". The August 2026 thread "Devtools must be open source" scored 733 points.
4. **One-line install** on the page and in every description: download link plus the Gatekeeper step until notarization ships.

## What to show (ranked)

Lead with what competitors cannot claim together:

1. **One coordinator, many agents.** Describe the work once; the coordinator starts worker threads and their reports come back on their own (filmed for real in the new explainer).
2. **Mix vendors per role.** Coordinator on Claude Opus 5.5, a worker on Codex, another on Grok or Antigravity. Cursor, Codex and Claude Code each lock you to one vendor.
3. **Your own Macs, your own subscriptions.** No inference resold, no vendor cloud.
4. **Usage limits handled.** Per-subscription rings, fallback to another signed-in provider.
5. **Honest "done".** A worker can report done; only a person makes it Verified.
6. **Free.** Conductor Pro is $50 a month, crystl Guild $170 a year (est.).
7. **Survives.** Vibe Kanban, Crystal and Terragon stopped in 2026; SpecWeave's CLI is open source and active.

Hook for every channel: "Stop being the router between Claude Code and Codex."

## Channel plan

Four weeks, founder accounts, one launch day per big channel.

| Week | Channel | What ships |
|---|---|---|
| 0 | Site, YouTube | Notarized build; download page updated; explainer "How SpecWithCode works" (1:59) on /tutorials and on Anton Abyzov: AI Power; the 35-second vertical cut as the first Short |
| 1 | LinkedIn, Threads, X | Native-video posts from your profiles (your data: Threads and LinkedIn beat your flat X account); link in the first comment on LinkedIn; reply-riding on your own live posts |
| 1 | npm audience | A short "SpecWithCode is out" section at the top of the SpecWeave README and docs, and in the `specweave` CLI release notes |
| 2 | Hacker News | Show HN Tuesday or Wednesday, 7–9 am PT: "Show HN: SpecWithCode – one coordinator for Claude Code, Codex and Grok threads on your Macs". Link the .dmg (no sign-up), post a maker comment (why, how, limits), answer for two hours |
| 2 | Reddit | r/ClaudeAI "Built with Claude" showcase megathread (feed posts need 50+ karma); r/ChatGPTCoding self-promo thread |
| 3 | Product Hunt | Tuesday 12:01 am PT, you as maker; the 35-second Short as the gallery video; ask people to visit and comment, never to upvote |
| 3 | GitHub | Submit to awesome-claude-code through its "Recommend a new resource" issue form; aim one day of HN, Reddit and PH traffic at the repo for Trending |
| Ongoing | YouTube | 5 Shorts a month (est. +46% long-form views), one tutorial a week; each Short ends on spec-weave.com/studio |
| Ongoing | SEO | Comparison pages: "SpecWithCode vs Conductor", "vs Claude Code agent teams", "vs the Codex app", "a Spec Kit alternative with orchestration" |

Skip for now: paid directories ($49–497 each, low intent), TLDR ads ($2,700+), X Premium Business. Revisit after the HN and PH launches.

## Where AI assistants carry the load

Use SpecWithCode itself, so the promotion is also the demo:

- A **SpecWithCode personal assistant** project with routines: a daily draft of one LinkedIn and one Threads post from that day's merged PRs, waiting for your approval in its thread.
- The existing social routine (Postiz/Blotato, per-post approval) schedules what you approve. AI content routes to Anton Abyzov: AI Power only.
- A weekly routine that collects the numbers below into one short report.
- Kie.ai (Seedance 2.0, GPT Image 2) for b-roll, thumbnails and Short covers. Kie credits are down to about 1,700; a top-up needs your go-ahead.

## Numbers to watch weekly

.dmg downloads per release (GitHub API), spec-weave.com/studio visits and download clicks, YouTube views and average view duration, HN points and comments, PH rank, GitHub stars, `specweave` npm downloads.

## Your decisions

1. Buy `specwithcode.dev`: yes or no.
2. Brand email: free Cloudflare forwarding (recommended) or Google Workspace.
3. Reserve the @specwithcode handles: yes or no.
4. App source: publish it, or say "closed source on an open-source CLI".
5. Create the Developer ID certificate under EasyChamp, Inc. for notarization.

## Sources

- Show HN rules: https://news.ycombinator.com/showhn.html ; guidelines: https://news.ycombinator.com/newsguidelines.html
- Product Hunt launch guide (no company accounts): https://www.producthunt.com/launch
- HN results in this niche (Algolia): https://hn.algolia.com/api/v1/search?query=Show%20HN%20claude%20code%20parallel&tags=show_hn
- "Devtools must be open source": https://hn.algolia.com/api/v1/search?query=devtools%20must%20be%20open%20source&tags=story
- LinkedIn page vs profile reach: https://metricool.com/linkedin-trends/
- YouTube Shorts study: https://metricool.com/how-to-grow-on-youtube/
- X Premium Business pricing: https://techcrunch.com/2025/10/07/x-splits-verified-organizations-into-premium-business-and-premium-organizations
- Cloudflare Email Routing: https://mecanik.dev/en/posts/cloudflare-email-routing-free-custom-domain-email/
- Competitors: https://crystl.dev/blog/best-ai-agent-orchestration-tools/ , https://cursor.com/changelog/3-0 , https://9to5mac.com/2026/02/02/openai-launches-codex-app-for-macos-here-are-the-details
- awesome-claude-code submissions: https://www.mintlify.com/hesreallyhim/awesome-claude-code/contributing
