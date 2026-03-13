# Video 004: Why Skills Matter

## Video

**YouTube**: [Link pending - will be added after upload]

**Duration**: ~9 minutes

---

## Summary

For developers getting generic AI output who want to understand how skills produce production-grade results. This video uses 4 before/after visual comparisons to explain what skills are, how they work, how to create them, and how to test them — no prior Claude Code or SpecWeave knowledge required.

---

## What You'll Learn

1. What a skill is and why the same prompt produces dramatically different quality with vs without one
2. How skills inject domain knowledge (patterns, rules, examples) into an LLM
3. How to formalize scattered instructions into a structured SKILL.md file
4. Why skills should be evaluated and iterated on, not blindly deployed

---

## Public Repos

All demos in this video use public repositories:
- **SpecWeave**: https://github.com/anton-abyzov/specweave

> EasyChamp repos shown are proprietary - techniques work identically on any project.

---

## Key Concepts

### Skills = Formalized Domain Knowledge

A skill is a structured set of instructions (a `SKILL.md` file) that tells the AI how to work in your specific domain. It contains frontmatter (metadata), an instructions body (the expertise), and supporting files (examples, templates, references).

### Same Prompt, Different Quality

The core insight: the exact same prompt produces generic, cookie-cutter output without a skill, but unique, polished, production-grade output with one. The difference isn't the prompt — it's the domain context.

### Eval-Driven Quality

Skills aren't "set and forget." The best teams measure skill output quality, identify gaps, improve the skill, and repeat — creating a compounding quality loop.

---

## Code & Configs Shown

```markdown
# Example SKILL.md structure (shown in "Creating Skills" segment)
---
name: frontend-design
description: Production-grade frontend interfaces
triggers: [build, create, design]
---

## Instructions

When building frontend interfaces:
- Use semantic HTML5 elements
- Follow the project's design system tokens
- Ensure WCAG 2.1 AA accessibility
...
```

---

## Step-by-Step

### (0:00) Intro — The Problem with Generic AI Output (~1 min)

**Visual**: Show the "What is a Skill?" diagram (left side only — red, generic)

"You've been using AI to write code. And the output is... fine. It compiles. It runs. But it doesn't feel like your code. It's generic. Cookie-cutter. It has that unmistakable AI vibe. Every time, you end up rewriting half of it. What if I told you there's a way to fix this — without writing a better prompt?"

**Visual**: Reveal the right side (green, production-grade). Pan to show the full before/after.

"Same prompt. Dramatically different quality. The difference? A skill."

### (1:00) What is a Skill? (~2 min)

**Visual**: Full `what-is-a-skill` diagram

"A skill is a structured set of instructions that tells the AI how to work in your specific domain. Think of it like onboarding a new developer — you wouldn't just say 'write code.' You'd give them your coding standards, your design system, your testing expectations. A skill does the same thing for AI."

Key points to cover:
- Not just a better prompt — it's formalized expertise
- Domain-specific: frontend, backend, testing, security — each has its own skill
- Reusable across projects and team members
- The same prompt input produces fundamentally different output quality

### (3:00) How Skills Work (~2 min)

**Visual**: `how-skills-work` diagram

"So what's actually happening under the hood? On the left, you have a raw LLM. You give it a prompt, it does its best — but it's guessing. It doesn't know your conventions, your patterns, your preferences."

"On the right, the same LLM gets augmented with a skill. The skill injects three things: patterns — how you structure code. Rules — what you always do and never do. And examples — what good output actually looks like in your domain."

Key points:
- Skill knowledge panel: Patterns, Rules, Examples
- The LLM isn't smarter — it has more context
- Domain knowledge injection = consistent, predictable output
- Question marks (guessing) vs checkmarks (confident)

### (5:00) Creating Skills — From Scattered to Structured (~1.5 min)

**Visual**: `creating-skills` diagram

"Here's the thing — you already have this knowledge. It's just scattered. 'Use TypeScript.' 'Handle errors this way.' 'Always add tests.' 'Be consistent.' Sound familiar? These are instructions you repeat in code reviews, Slack messages, onboarding docs. The problem isn't the knowledge — it's that it's never formalized."

"A SKILL.md file changes that. Three sections: frontmatter for metadata, an instructions body for the actual expertise, and supporting files for examples and templates. Once it's formalized, the knowledge is repeatable, shareable, and testable."

### (6:30) Testing & Evaluating Skills (~1.5 min)

**Visual**: `skill-eval-testing` diagram

"The worst thing you can do with a skill is deploy it and hope it works. That's the left side — write it, ship it, cross your fingers. Dead end."

"The right side is what separates good skills from great ones: an eval loop. Run the skill. Measure the quality of the output. Improve the skill based on what you find. Repeat. Every cycle makes the skill better. Over time, you get compounding quality improvements."

Key points:
- Skills are like code — they need tests
- Eval metrics: consistency, correctness, adherence to standards
- Feedback loops create compounding improvements
- Tool-agnostic concept — works with any eval framework

### (8:00) Call to Action (~1 min)

"So to recap: skills formalize your domain knowledge, inject it into the AI, and produce consistent, production-grade output — from the same prompts that used to give you generic results. And when you add evaluation, quality compounds over time."

"Links to everything shown in this video are in the description. Start with the 'Why Skills Matter' docs page for the full writeup with all four diagrams. Then check out the Skills Fundamentals page to understand skills, plugins, and marketplaces."

Links to show:
- Why Skills Matter docs page: https://verified-skill.com/docs/skills/why-skills-matter
- Skills Fundamentals: https://verified-skill.com/docs/skills/fundamentals
- SpecWeave GitHub: https://github.com/anton-abyzov/specweave

---

## Quick Reference

| Term | Definition |
|------|------------|
| Skill | A structured set of instructions (SKILL.md) that injects domain knowledge into an AI |
| SKILL.md | The file format for defining skills — frontmatter + instructions + supporting files |
| Domain Knowledge | Patterns, rules, and examples specific to your project or team |
| Skill Eval | The process of measuring skill output quality and iterating to improve |

---

## Transcript

[Will be added after video recording]

---

## Related Videos

- **Previous**: [003 - ClaWHub Postmortem](./003-clawhub-postmortem.md)
- **Next**: [005 - TBD](./005-tbd.md)
- **See also**: [001 - SpecWeave Complete Masterclass](./001-specweave-complete-masterclass.md), [002 - ToxicSkills Security](./002-toxicskills-security.md)

---

## Questions?

- Check the [SpecWeave docs](https://verified-skill.com)
- Open an issue on GitHub: https://github.com/anton-abyzov/specweave/issues
- Join the community discussions
