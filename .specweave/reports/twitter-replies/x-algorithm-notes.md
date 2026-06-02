# X (Twitter) Algorithm — Practical Notes for @aabyzov

**Source**: github.com/twitter/the-algorithm (the public source dump) + 12 months of behavioural observation on this account.

**Goal**: increase followers on @aabyzov and drive profile visits to verified-skill.com, SpecWeave, and Skill Studio.

---

## The For You ranker — what actually moves the needle

| Signal | Weight (relative) | Notes |
|---|---|---|
| Reply received on YOUR post | **27x** | Largest single multiplier in the public source. Every closer should bait a reply. |
| Retweet on your post | 1x | Nice signal but not load-bearing. |
| Like on your post | 0.5x | Vanity. Stop optimising for it. |
| Profile visit after seeing your post | mid-strong | This is the real follower-conversion signal. Posts that pull profile visits compound. |
| External link in post body | ~-50% reach | Always self-reply with the link, never put it in the parent. |
| Hashtags > 2 | negative | Skip. One niche hashtag is fine, more is spam-classifier bait. |
| Post under 280 chars | mild positive | Threads are fine, but the PARENT post should fit. |
| First 30 minutes engagement | very strong | The "hot window" — replies inside this window get the most inherited reach. |
| Reply on a 1M+ follower account | inherits visibility | Even a 20-like reply on @sama reaches ~40-60k people via reply-tree promotion. |
| Same template across multiple big accounts in 24h | spam-classifier hit | Vary tone and structure across reply targets. |
| Reply-guy deboost (4+ replies to big accounts in one window) | strong negative | **Stop at 4 per window.** This is the most-violated rule. |
| "Not interested" / Block | very strong negative | One vocal critic in your niche can shadow-deboost an entire week. |

---

## What this means for @aabyzov specifically

### The four-post Saturday sweep (proven format)
1. One reply to the highest-velocity post from a top-10 account inside its first 30 minutes.
2. One quote-tweet of a hot news item, landing on your own profile.
3. One reply on a friendly-niche account (Boris Cherny, Steipete, swyx).
4. One standalone evergreen post with a question closer.

Stop at 4. Do not do reply-rounds. Reply-guy deboost is the #1 reason your previous accounts hit a follower ceiling.

### Voice rules (locked)
- Short, sharp, plain English.
- Zero em-dashes.
- No emoji at the start of a post.
- No link in the body of any standalone post. Link goes in a self-reply.
- 1-3 sentences for replies. 3-5 lines for standalone posts.
- Mention Skill Studio / SpecWeave / verified-skill.com only when the parallel is real. Cold product drops underperform 5-10x vs. organic mentions.
- Avoid "essentially," "basically," "in order to," "it's worth noting," "as you can see," "feel free to" (per Anton's communication style — same rules apply to public posts).

### Targets (rotating set)
**Tier 1 — always check, daily:**
- @sama — Sam Altman
- @elonmusk — Elon Musk
- @karpathy — Andrej Karpathy
- @gdb — Greg Brockman
- @bcherny — Boris Cherny (Claude Code lead)

**Tier 2 — check 3x per week:**
- @trq212 — Thariq (Anthropic)
- @theo — Theo (t3.gg, AI-coding-adjacent)
- @steipete — Peter Steinberger (Mac dev + AI tooling)

**Tier 3 — opportunistic:**
- @swyx — Shawn Wang (AI Engineer)
- @simonw — Simon Willison
- @hwchase17 — Harrison Chase
- Anthropic and OpenAI official accounts

### Quote-tweet vs. reply — when to pick which
- **Reply** when the parent post has < 50k views and you want inherited reach.
- **Quote-tweet** when the parent post has > 500k views and you want to land on your own profile.
- Sweet spot for replies: post is 5-30 minutes old, 5-50 replies in already.

---

## High-leverage content pillars for @aabyzov

1. **Cross-vendor skill portability** — the Skill Studio thesis. Most reusable angle.
2. **Tool calls and the agentic loop** — pairs with anything Anthropic or OpenAI ships.
3. **Indie / one-person shops shipping production AI** — Peter Steinberger, Theo, swyx audience overlap.
4. **Practical Claude Code patterns** — high-engagement with @bcherny's audience.
5. **Founder economics in the AI era** — for Threads / LinkedIn cross-posts.

Avoid: model-religion takes, hot-take politics, hot-take crypto. Reach is good, follower quality is terrible.

---

## What does NOT work (observed)

- Posting the same draft to X + LinkedIn + Threads without re-tailoring the voice. LinkedIn especially needs softer openers and longer setup.
- Posting after 11 PM EST. Reach for tech content drops ~70% after 10 PM EST.
- Posting on Sunday afternoon. Saturday 9-11 AM EST is the proven sweet spot (already in feedback memory).
- "Hot take" posts without a question closer. They get likes, not follows.
- Cold links to verified-skill.com in any post body. Always self-reply.

---

## Refresh policy

This file is the working knowledge base. The scheduled twitter-replies task should overwrite this file whenever:
- A new high-leverage target is identified.
- An algorithm signal changes (X publishes new ranker changes, or observed behaviour shifts).
- A reply pattern stops working (track follower-conversion rate per reply, see if any pillar is dead).

Mirror copy lives at `~/.claude/scheduled-tasks/twitter-replies-to-top-people/x-algorithm-notes.md`.

---

## Hop-chain sub-patterns (added run 18, 2026-05-21)

- **Concession openers match counter-party intent.** "fair." for attacks (Matt-style — concede the critique, then split). "yes." for generalisations (Virgil-style — full agreement on the frame). Wrong opener costs trust.
- **Paused branches stay reversible until 24h silent.** Run-17 declared the Virgil wiki-content branch paused after 6h silence. Virgil reactivated it 9h later with a sharper frame. Don't declare a branch dead until a full 24h has passed without counter-reply.
- **Name the counter-party's killer phrase in the opener.** Matt's "endogenous confound" (hop #12) → Anton's "fair. endogenous confound." (hop #13). Mirroring the exact attack term is the highest-trust conversation signal. Seven consecutive hops have landed this pattern (runs 12-18).
- **"One primitive, N UIs" is the right architecture-debate frame.** When the counter-party names one collapse (X reduces to UI on top of Y), extend it to N>1 collapses. Shows the primitive carries more weight without adding complexity. Universal frame for "protocol vs. policy" debates.

## Original-post patterns (added run 19, 2026-05-21)

- **Universal trope reframe.** Take a senior-engineer trope ("works on my machine", "race condition", "off-by-one", "shared mutable state", "no SBOM = no ship") and apply it to a domain that doesn't yet have its own trope (agents, skills, AI installs). Surprise + universality lands across audience segments. Run-19's "the most expensive 'works on my machine' I shipped this year wasn't code" used this pattern.
- **Gate hard-block = original-post window.** When the gate is tripped (4+ cold tier-1 replies in 24h) AND own-thread replies are stale enough that post-saturation isn't active (30-60 min since last own-thread reply), use the time for ONE original standalone on a content pillar. Don't sit idle.
- **3-stanza hook-setup-imperative.** Optimal shape for a standalone pillar post under 280 chars: hook (universal trope), setup (the specific reframe / failure mode), imperative closer (aphoristic rule). Each stanza 1-2 sentences, blank line between. Run-19's "install-side hash or it doesn't ship" landed this shape.
- **Mention-light pillar posts beat mention-heavy ones.** A post that names the THESIS (e.g., "install-side hash") without naming the PRODUCT (Skill Studio, verified-skill.com, SpecWeave) lands organically; the product earns the mention only in a self-reply if engagement materialises. Cold product drops in the parent post underperform 5-10x per existing notes.
- **One-word affirms from credentialed counter-parties are propagation signals, not reply triggers.** OpenClaw's "100% truth" on Anton's parent post is a strong-signal affirm. Replying with substance pressures a positive moment into a longer thread the counter-party may not want. Let it propagate; cash the goodwill on the next genuine engagement.
