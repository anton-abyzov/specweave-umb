# SpecWithCode: plan to grow GitHub stars

Prepared November 24, 2026. Read-only research. Nothing was posted and no repository was changed.

## 1. Current numbers

| Metric | Value |
|---|---|
| Stars | 10 (29 days since the repo was created on October 26, 2026, about 0.34 per day) |
| Stars per day | Oct 26: 2, Oct 27: 1, Nov 6: 1, Nov 19: 1, Nov 22: 1, Nov 24: 4 |
| Forks / watchers | 4 / 0 |
| Releases | 314 (latest `v1.0.416`, November 24, 2026), about 11 per day |
| Pull requests | 850 |
| Discussions | 0 (enabled) |
| Open "good first issue" | 8 |
| Views, Nov 10 to 23 | 263 views, 54 unique visitors (about 4 unique per day) |
| Repo home page, same window | 72 views, 44 unique |
| Referrers, same window | Google 21 views / 18 unique, github.com 13 / 9, spec-weave.com 2 / 2, t.co 1 / 1 |
| Clones, same window | 231,094 clones, 3,066 unique (assumed to be CI and automation; not measured) |
| Release downloads, last 30 releases | 14,576 in total, mostly updater metadata |
| Installer downloads, one release | `v1.0.407`: 316 `SpecWithCode-arm64.dmg`, 30 Windows `.exe`; update-check files fetched 2,827 (`latest-mac.yml`), 1,462 (`latest.yml`), 528 (`latest-linux.yml`) times. `v1.0.412`: 68 DMG, 18 `.exe` |
| Hacker News mentions | 0 (Algolia search for `specwithcode`) |
| Sister repo `anton-abyzov/specweave` | 173 stars; its README has a SpecWithCode section linking to specwithcode.com, not to the GitHub repo |
| License, topics, social image | MIT, 20 topics (the maximum), custom Open Graph image set |

How the numbers were read: the active `gh` login has pull access only, so `stargazers` returned 404 and `traffic/*` returned 403. Star history and traffic were read with the owner login for those calls only (`GH_TOKEN=$(gh auth token --user <owner>)`), GET requests only. Measurement commands below need the same.

**Reading.** There are two gaps. First, people already run the app (hundreds of DMG downloads per popular release, thousands of update checks) and almost none of them have starred: the app never sends them to the repo. Second, the repo page itself gets almost no traffic. 44 people saw the repo home page in 14 days and 2 starred in that window. No README change can produce stars from 4 visitors a day. The 4 stars on November 24 fall outside the traffic window, so their source is not yet visible; check referrers again on November 25.

## 2. What a first-time visitor sees

Present near the top (read from the markup, not from a rendered page): app icon, a one-line value statement, "Free and open source under MIT", a real app screenshot, a 15 s real-run GIF (Claude Code hits its limit, thread continues on Codex), then download text, a `curl | bash` server install, a star ask, download badges and a social star badge. A second star ask sits at the end of "Why". A comparison table follows.

Missing or weak:

- Social proof. 10 stars and no user quotes. The strongest real proof sits at line 96, far below: the "Built with itself" table (1,393 pull requests merged between October 9 and November 7, 2026, at least 418 linked to worker threads).
- Two 800 px images stack before any install step, so the install command is probably below the fold on a laptop.
- Windows and Linux installers are unsigned (stated at line 110, not near the download badges). Hacker News and Reddit readers will raise this first.
- 314 releases in 29 days floods anyone who clicks Watch > Releases. Watchers: 0.

Wording that conflicts with the owner's constraints (proposals in section 4):

- Repo description: "Free desktop app, MIT."
- README line 54, GIF alt text: "hands its thread to Codex on a free ChatGPT account".
- README "Why": "**Never stuck on a limit.**" reads as an absolute, close to "unlimited".
- `specweave` README line 31: "a desktop app built on SpecWeave", under the heading "the free workspace on top". This is "built on another project" wording.

## 3. Evidence on what moves stars

- **Hacker News is the largest single lever, and most posts get nothing.** An analysis of 188,085 Show HN posts (2012 to April 2026) found a median score of 2; a score of 50 is the top 6%, 250 the top 1%. Median conversion is about 1.4 stars per upvote within 48 hours, and 92% of the star effect is over after 48 hours. The widely quoted "509 stars on day one" comes only from the top 500 posts (score 258 or more), so it is not an expectation. About 200 Show HN posts are submitted per day now.
- An arXiv study of 138 AI repos with HN posts in 2024 to 2025 reports average gains of 121 stars in 24 h, 189 in 48 h and 289 in a week, and no advantage from the "Show HN" tag after controls. Those repos averaged 1,247 stars beforehand, so the figures do not transfer to a 10-star repo.
- **Timing evidence conflicts.** The 188k-post analysis found the best odds of 50+ points at Monday 00:00 UTC (10.8%) and weekend slots, the worst at Thursday 06:00 UTC (2.6%). Blog guides say Tuesday to Thursday, 9 to 11 AM ET. One practitioner guide says there is no best time. Low-competition slots have the data behind them.
- **Show HN rules** (official page): the thing must be runnable, made by the poster, who stays to discuss; no sign-up barrier; "Please don't ask friends to upvote or comment"; no "quickly-generated one-offs"; new versions generally do not qualify.
- **GitHub Trending** is undocumented. Third-party observation says it ranks by star velocity over roughly 24 to 48 hours, 25 repos per page, filterable by language. No reliable threshold exists. The practical consequence is to concentrate launches in one 48-hour window, not spread them.
- **Awesome lists** give a slow, permanent trickle and count as "seen elsewhere" proof. Rules read from each repo are in section 5.
- **README.** No controlled study exists. One unsourced-method blog claims 89% of repos over 10k stars show a screenshot or GIF in the first screen against 45% of 100 to 1k repos. SpecWithCode already does this.
- **Product Hunt.** Results are anecdotal and variable (one open source tool: 0 to 168 stars in three weeks). The guidelines forbid asking for upvotes.
- **Reddit.** Rules could not be fetched (Reddit blocks automated reads). A third-party mirror of the r/LocalLLaMA wiki lists rule 4 "Limit Self Promotion": about 10% of your content, affiliation disclosed, no "I found this" posts, minimum karma to post. r/ChatGPTCoding has run numbered self-promotion threads. r/opensource bans AI projects outright. All Reddit rules here are unverified; the owner reads each sidebar before posting.

## 4. README and metadata proposals (not applied)

1. Repo description: "Run Claude Code, Codex, Copilot and other coding agents side by side on the machines you own. When a plan hits its limit, the thread continues on another signed-in provider. Open source, MIT."
2. Add under the title: "Get more out of the plans you already pay for."
3. Replace "Never stuck on a limit." with "Keep working when a plan hits its limit."
4. GIF alt text: replace "on a free ChatGPT account" with "on another signed-in account".
5. Put the 15 s real-run GIF first and move the static screenshot below "Try it", so the install step is in the first screen.
6. Add one proof line near the top that reuses the README's own figures and links to the table: "Developed in SpecWithCode: 1,393 pull requests merged between October 9 and November 7, 2026."
7. State next to the download badges that Windows and Linux builds are unsigned and link the checksum file. Saying it first costs less than being told.
8. Keep one star ask (the one after "Try it") plus the social badge. Drop the second.
9. In the `specweave` README, replace "a desktop app built on SpecWeave" with "a desktop app that keeps its specs in SpecWeave format" and link the GitHub repo as well as the site.
10. Add a "Watch releases? We ship many builds a day; a weekly summary is in Discussions" note, and post that weekly summary. This also gives Discussions its first content.

## 5. Ranked actions

Approval key: **Owner** means the owner's explicit approval is needed (anything as him personally, Hacker News, Reddit, Product Hunt). **Brand** means brand account, pre-approved.

| # | Action | Effort | Why it should move stars | Venue and rule | Approval |
|---|---|---|---|---|---|
| 1 | Show HN, once | 1 h to post, 4 to 6 h answering | Only venue with measured star conversion (about 1.4 per upvote, measured on high-scoring posts); the largest upside of any single action | news.ycombinator.com. Runnable product, poster present, no upvote or comment requests, plain title | Owner |
| 2 | Apply README and description proposals before any launch | 2 h | Every later visitor lands here; fixes the wording conflicts and puts install in the first screen | Own repo | Owner reviews the proposals |
| 3 | One in-app star prompt plus a "Star on GitHub" item in the Help menu and About screen | Half a day | The installed base is the largest audience available today (316 DMG downloads on one release against 10 stars in total) and has already seen the value | Acceptable: shown once, after a first completed handoff or task, one click to dismiss for good, no reward. Spammy: at launch, repeated, blocking, or tied to an incentive. Sourcebot ships a one-time delayed toast; a stars-for-drinks scheme drew a backlash in 2019. No conversion data found | Owner (product change) |
| 3b | Cross-links from owned properties: star button on specwithcode.com, a GitHub link in the `specweave` README (173 stars) and on spec-weave.com | 1 h | Free traffic; spec-weave.com already refers visitors | Own sites | Brand |
| 4 | Wait on the two submissions already open. `hesreallyhim/awesome-claude-code` issue #3523 (filed November 7, labels `validation-passed`, `resource-submission`, 1 comment): nothing to fix, review is best-effort with no promised reply. `RoggeOhta/awesome-codex-cli` PR #565 (filed November 6, no comments): the list has 30 open PRs and was last pushed September 6, so expect little | 15 min | awesome-claude-code has 58,700 stars and an "Agent Orchestration" section | awesome-claude-code: web issue form only, filed by a human, one resource at a time, 14 days old or 100 stars (met). Do not file again or open a PR. awesome-codex-cli: must have Codex integration, one-sentence description, star badge | Owner (posts as him) |
| 5 | New list submissions with no star gate: `jamesmurdza/awesome-ai-devtools` (4,000 stars, "Multi-Agent Orchestration" and "Desktop & Mobile Applications" sections), `e2b-dev/awesome-ai-agents` (31,051 stars, Google form or PR, alphabetical order; last pushed August 21, 2026, may be stale), `jqueryscript/awesome-claude-code` (557 stars, "Clients & GUIs", guidelines "under construction", so open an issue) | 1 h | Permanent referral links from pages developers browse when choosing a tool | ai-devtools: PR template checklist, developer tools only, description in the list's style | Owner (PRs from his account) |
| 6 | Reddit, one subreddit per day: r/ClaudeAI, then r/ChatGPTCoding or r/codex | 1 h each plus replies | Audience is exactly people hitting plan limits | Rules unverified; read each sidebar, disclose authorship, use the project or showcase flair or the self-promotion thread where one exists. Skip r/LocalLLaMA (my judgement, not a rule I read: the product runs hosted subscriptions) and r/opensource (bans AI projects) | Owner |
| 7 | Comparison pages on specwithcode.com ("running Claude Code and Codex together", "what to do when Claude Code hits its limit") with a star button | 1 day | Google is already the top referrer (18 of 30 referred unique visitors). Effect of comparison pages on stars was not researched | Own site. Factual rows only; never "the only" | Brand |
| 8 | Short clips from the 15 s real-run GIF on brand X, YouTube Shorts and Telegram, linking to the repo | 2 h | Motion shows the handoff in seconds; t.co already appears as a referrer | Brand accounts | Brand |
| 9 | One technical post on dev.to and Hashnode: how a thread continues on another provider with its history | 3 h | Search traffic and a link target for newsletters. dev.to and Hashnode rules and results were not researched | Tags such as `#showdev`, `#opensource`; canonical URL to the site | Brand, or Owner if under his name |
| 10 | Newsletters: email Console.dev (`hello@console.dev`), submit to Changelog News (sign-in form, self-submissions welcome, say why it is newsworthy) | 1 h | Console features 2 to 3 tools a week and takes no payment for reviews | Console wants cross-platform, easy install, good docs, no security or privacy downside; unsigned installers weaken the case. Hacker Newsletter (60,000+ subscribers) is hand-picked from HN, with no submission. tldr.tech shows no editorial submission path, only "Advertise" | Brand email; Owner if signed by him |
| 11 | Star-gated lists once the threshold is reached: `kyrolabs/awesome-ade` ("Orchestrators — Desktop", needs roughly 50 stars), `kyrolabs/awesome-agents` (3,014 stars, needs traction, PR at the bottom of the list) | 30 min | Exact-fit category | Both auto-close new repos without traction; submitting early burns the attempt | Owner |
| 12 | Product Hunt | 1 day prep, 1 day present | Variable, audience less developer-heavy than HN | Guidelines: no asking for upvotes, no incentives; ask people to try it and comment | Owner |
| 13 | Do not chase GitHub Trending directly | 0 | It follows velocity; actions 1, 6 and 8 inside one 48-hour window are the only way to qualify | None | None |

Suggested Show HN title: "Show HN: SpecWithCode – one coordinator for Claude Code and Codex threads on your own machines". First comment: what it is, what runs locally, that it uses the reader's own subscriptions, that Windows and Linux builds are unsigned, and what is not done yet.

Wording kept out of every draft: fork or "built on" language, "saves money", "free AI", "unlimited", "the only". Money line: "Get more out of the plans you already pay for."

## 6. 14-day sequence

US Thanksgiving is Thursday, November 26, 2026, so the launch waits until the weekend after.

| Day | Date | Step |
|---|---|---|
| 1 | Nov 25 | Start the daily snapshot (section 7). Check referrers for the 4 stars of November 24. Apply README and description proposals after owner review. |
| 2 | Nov 26 | Cross-links and star button on owned sites and the `specweave` README. |
| 3 | Nov 27 | File awesome-ai-devtools PR, e2b form, jqueryscript issue. Check #3523 and #565. |
| 4 | Nov 28 | Ship the in-app star prompt if approved, so launch visitors who install also see it. Publish comparison page. Cut brand clips. Draft the Show HN text and first comment for owner approval. |
| 5 | Nov 29 | Show HN at about 7 PM ET (Monday 00:00 UTC, the best-odds slot in the data). Owner answers for the evening. Brand clips go out the same hour. |
| 6 | Nov 30 | r/ClaudeAI post. Keep answering HN. |
| 7 | Dec 1 | r/ChatGPTCoding or r/codex post. |
| 8 | Dec 2 | Console.dev email and Changelog News submission, citing the HN thread if it did well. |
| 9 | Dec 3 | Publish the dev.to and Hashnode post. |
| 10 | Dec 4 | First weekly release summary in Discussions. |
| 11 | Dec 5 | If stars are at 50 or more, file awesome-ade. Otherwise hold. |
| 12 | Dec 6 | Review the in-app prompt's first week if it shipped. |
| 13 | Dec 7 | Decide on Product Hunt from the numbers. If the Show HN got no traction, check the HN FAQ on reposts before trying again (not verified here). |
| 14 | Dec 8 | Review: stars per day, referrers, which venue converted. Keep the top two, drop the rest. |

## 7. How to measure

GitHub keeps traffic for 14 days only, so save a snapshot every day (owner login required):

```sh
R=anton-abyzov/specwithcode
gh api repos/$R --jq '.stargazers_count'
gh api "repos/$R/stargazers?per_page=100" -H "Accept: application/vnd.github.star+json" --paginate --jq '.[].starred_at[0:10]' | sort | uniq -c
gh api repos/$R/traffic/popular/referrers
gh api repos/$R/traffic/views
gh api repos/$R/traffic/popular/paths
```

Track three numbers: stars per day (baseline 0.34), unique visitors per day (baseline about 4), and stars per unique visitor to the repo home page (baseline 2 of 44, too small to trust). Per venue, read the referrer row: `news.ycombinator.com`, `reddit.com`, `t.co`, `dev.to`, `console.dev`, `Google`. GitHub drops UTM parameters, so the referrer host is the attribution.

Planning ranges, not promises: a Show HN at the median (2 points) adds nothing; at 50 points (top 6%) about 70 stars if the 1.4 ratio holds at low scores (it was measured only on posts scoring 258 or more, so this is an extrapolation); at 250 points (top 1%) several hundred. Lists and search add single digits per week each.

## 8. Sources

- Show HN rules: https://news.ycombinator.com/showhn.html
- Show HN by the numbers, 188,085 posts: https://danfking.github.io/blog/2026/04/23/show-hn-by-the-numbers/
- Launch-Day Diffusion, HN impact on GitHub stars for AI tools: https://arxiv.org/abs/2511.04453v1
- HN launch guide (no best time): https://www.lucasfcosta.com/hn-launch
- HN timing guides: https://dev.to/iris1031/how-to-launch-on-hacker-news-the-show-hn-guide-real-data-461e and https://business.daily.dev/resources/hacker-news-marketing-developer-tools-show-hn-launch-day-sustained-coverage/
- GitHub Trending observations: https://dev.to/iris1031/how-to-get-on-github-trending-the-algorithm-the-tactics-and-the-real-data-o5b and https://gingiris.github.io/growth-tools/blog/2026/05/01/affine-github-trending-playbook/
- awesome-claude-code rules: https://github.com/hesreallyhim/awesome-claude-code/blob/main/CONTRIBUTING.md
- awesome-claude-code open submission: https://github.com/hesreallyhim/awesome-claude-code/issues/3523
- awesome-codex-cli rules and open PR: https://github.com/RoggeOhta/awesome-codex-cli/blob/main/CONTRIBUTING.md and https://github.com/RoggeOhta/awesome-codex-cli/pull/565
- awesome-ai-devtools: https://github.com/jamesmurdza/awesome-ai-devtools
- awesome-ai-agents (e2b): https://github.com/e2b-dev/awesome-ai-agents
- awesome-ade and awesome-agents: https://github.com/kyrolabs/awesome-ade and https://github.com/kyrolabs/awesome-agents
- jqueryscript awesome-claude-code: https://github.com/jqueryscript/awesome-claude-code
- Product Hunt community guidelines: https://help.producthunt.com/en/articles/3615694-community-guidelines
- Product Hunt open source launch account: https://dev.to/rahil_pirani_c48446facc8c/i-launched-an-open-source-tool-on-product-hunt-with-no-budget-no-team-and-no-audience-heres-57c3
- Console.dev selection criteria: https://console.dev/selection-criteria
- Changelog News submit: https://changelog.com/news/submit
- Hacker Newsletter: https://www.hackernewsletter.com/
- r/LocalLLaMA rules (third-party mirror, unverified): https://r.datuan.dev/r/LocalLLaMA/wiki/index
- r/ChatGPTCoding self-promotion thread (mirror): https://redlib.hbubli.cc/r/ChatGPTCoding/comments/1fjhnw1/selfpromotion_thread_8
- r/opensource AI ban: https://www.linux-magazine.com/Online/News/r-opensource-Bans-AI-Assisted-and-AI-Related-Projects/(tagID)/152
- In-app star prompts: https://github.com/sourcebot-dev/sourcebot/pull/409 and https://www.theregister.com/2019/07/30/would_you_star_a_github_project_for_a_free_drink/
- TLDR: https://tldr.tech/
- README practice (weak evidence): https://dev.to/0012303/i-analyzed-10000-github-readmes-the-top-repos-all-do-this-596n and https://dev.to/m4xshen/how-i-grew-my-open-source-project-to-1k-stars-3mk2
