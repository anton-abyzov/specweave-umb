# Marketing drafts — 0829 launch pack

**STATUS: DRAFTS ONLY. Nothing has been posted. The user picks the launch date.**

This directory holds launch-day announcement drafts for Skill Studio (US-024 in spec.md).
Each file is self-contained, with a posting window, a body, and a checklist.

## Files

| File | Channel | When to post |
|------|---------|--------------|
| `hacker-news.md` | HN Show HN | Tue/Wed 8:30-10:00 AM ET |
| `product-hunt.md` | Product Hunt | 12:01 AM PT on a Tuesday |
| `reddit-localllama.md` | r/LocalLLaMA | Sat/Sun afternoon ET, 24-48h after HN |
| `reddit-claude.md` | r/ClaudeAI | Tue-Thu afternoon ET, day-of or +1 |
| `dev-to-article.md` | dev.to deep-dive | Day-of or +1 after HN |
| `twitter-thread.md` | X / Twitter | 9-11 AM EST (per user pref) |
| `awesome-lists.md` | GitHub awesome-* PRs | Week of launch |

## Constraints (per architect's brief)

- NO posting from this agent — drafts only
- NO astroturfing, vote rings, or paid hunters on Product Hunt
- NO keyword-stuffing in any draft
- All drafts use natural founder voice; no AI-mention clichés

## Open questions for the user

1. **Launch date.** All windows above are relative — pick the actual launch day.
2. **press@verified-skill.com.** Email alias not yet configured. Flagged in spec OQ-A5;
   ci-pipeline-agent should provision before press kit goes live.
3. **Real founder bio + headshot.** The press page (`src/app/press/page.tsx`) uses a
   2-line generic placeholder — update before press kit is shared with media.
4. **Real screenshots.** All `*@2x.png` placeholders on /press should be replaced with
   actual desktop captures from 0828's testing reports.

## Sequencing recommendation

```
Day 0 (launch day):
  09:00 ET  HN Show HN post
  09:00 PT  Product Hunt launches (timed for 12:01 AM PT, but maker is awake)
  10:00 ET  Twitter thread
  14:00 ET  dev.to deep-dive
  17:00 ET  r/ClaudeAI

Day +1:
  Reply backlog in HN, PH, dev.to
  Tier 1 awesome-list PRs

Day +2 (Sat or Sun):
  r/LocalLLaMA

Day +3:
  Tier 2 awesome-list PRs
  Quote-tweet community posts that already mention vSkill
```
