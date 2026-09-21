#!/usr/bin/env node
// 0878 AC-10 — Jev (TypeSafe System One) bench.
//
// Zero dependencies. Node >= 20 (global fetch).
//   node jev-bench.mjs --dry-run      list the suites, no network, exit 0
//   node jev-bench.mjs                run everything live, write reports/jev-bench.{json,md}
//   node jev-bench.mjs --suite intent --suite triage
//   node jev-bench.mjs --from-json    re-render the markdown from an existing JSON report
//   node jev-bench.mjs --allow-local-files
//                                     opt in to ALSO sending local files from
//                                     ~/.agents/skills to the provider (off by default)
//
// Requires OPENROUTER_API_KEY in the environment for a live run. The key is read
// once, used only as an Authorization header, and never printed or written out.
//
// Data sent to the provider: every suite input is either synthetic (written in this
// file) or a file tracked in the public `specweave` repository. Nothing outside the
// repository is read unless `--allow-local-files` is passed, and when it is, the
// report names every local file whose excerpt was sent.

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const INCREMENT_ROOT = path.resolve(HERE, '..');
const REPO_ROOT = path.resolve(INCREMENT_ROOT, '..', '..', '..');
const SPECWEAVE_REPO = path.join(REPO_ROOT, 'repositories', 'anton-abyzov', 'specweave');
const SKILLS_DIR = path.join(os.homedir(), '.agents', 'skills');

const ENDPOINT = 'https://openrouter.ai/api/v1/systemone';
const MODEL = 'jev-1.13';
const CONCURRENCY = 6;
const TIMEOUT_MS = 20000;

// ---------------------------------------------------------------- args ----
const argv = process.argv.slice(2);
const DRY_RUN = argv.includes('--dry-run');
// Opt-in: also send local (non-repository) skill files to the provider. Default off —
// ~/.agents/skills holds the operator's private skills; uploading them silently would
// disclose personal data and make the report's privacy statement false.
const ALLOW_LOCAL_FILES = argv.includes('--allow-local-files');
const onlySuites = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--suite' && argv[i + 1]) onlySuites.push(argv[++i]);
  else if (argv[i].startsWith('--suite=')) onlySuites.push(argv[i].slice(8));
}
const outDirArg = (() => {
  const i = argv.indexOf('--out');
  return i >= 0 && argv[i + 1] ? argv[i + 1] : path.join(INCREMENT_ROOT, 'reports');
})();

// ---------------------------------------------------------------- http ----
let apiKey = '';
async function ask(state, questions, meta) {
  const body = JSON.stringify({ model: MODEL, state, questions });
  let lastErr;
  for (let attempt = 0; attempt < 3; attempt++) {
    const ac = new AbortController();
    const timer = setTimeout(() => ac.abort(), TIMEOUT_MS);
    const t0 = Date.now();
    try {
      const res = await fetch(ENDPOINT, {
        method: 'POST',
        headers: { Authorization: `Bearer ${apiKey}`, 'content-type': 'application/json' },
        body,
        signal: ac.signal,
      });
      const latencyMs = Date.now() - t0;
      if (res.status === 429 || res.status === 529) {
        lastErr = new Error(`retryable ${res.status}`);
        await sleep(400 * Math.pow(2, attempt));
        continue;
      }
      const text = await res.text();
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${text.slice(0, 300)}`);
      const json = JSON.parse(text);
      return { ...json, latencyMs, meta };
    } catch (err) {
      lastErr = err;
      if (err?.name === 'AbortError') lastErr = new Error(`timeout after ${TIMEOUT_MS}ms`);
      if (attempt < 2) await sleep(400 * Math.pow(2, attempt));
    } finally {
      clearTimeout(timer);
    }
  }
  throw lastErr ?? new Error('unknown failure');
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function pool(items, limit, worker) {
  const out = new Array(items.length);
  let next = 0;
  const runners = Array.from({ length: Math.min(limit, items.length) }, async () => {
    for (;;) {
      const i = next++;
      if (i >= items.length) return;
      out[i] = await worker(items[i], i);
    }
  });
  await Promise.all(runners);
  return out;
}

// --------------------------------------------------------------- stats ----
function pct(sorted, p) {
  if (!sorted.length) return 0;
  const idx = Math.min(sorted.length - 1, Math.max(0, Math.ceil((p / 100) * sorted.length) - 1));
  return sorted[idx];
}
const round = (n, d = 4) => Number.isFinite(n) ? Number(n.toFixed(d)) : 0;
const topProbs = (probabilities, n = 3) =>
  Object.entries(probabilities ?? {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, n)
    .map(([k, v]) => `${k}=${round(v, 2)}`)
    .join(', ');

// ================================================================
// Ported regex baselines (from the live EasyChamp services)
// ec-chat-api/services/intent_router.py  — INTENT_PATTERNS, detect_intent
// ec-chat-api/services/chat_approval.py  — requires_write_approval
// Ported to JS verbatim. Only known divergence: JS \w is ASCII-only, which
// affects CREATE_LEAGUE's (\w+) group; those patterns require the literal
// English "create" anyway, so no bench item is affected.
// ================================================================
const UUID = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}';
const INTENT_PATTERNS = [
  ['disambiguation', [
    /^(?:it'?s?\s+)?(?:match\s*day|matchday|md)\s+(\d+)\s*$/i,
    /^(\d+)\s*$/i,
    /^(?:the\s+)?(?:option\s+)?(\d+)(?:st|nd|rd|th)?\s*(?:one|match|game)?\s*$/i,
    /^(?:the\s+)?(first|second|third|fourth)\s*(?:one|match|game)?\s*$/i,
  ]],
  ['get_leagues', [
    /(?:get|show|list|display|what are)\s+(?:me\s+)?(?:all\s+)?(?:my\s+)?leagues?/i,
    /(?:my\s+)?leagues?\s+(?:list|please)/i,
    /show\s+(?:me\s+)?(?:all\s+)?(?:my\s+)?leagues?/i,
  ]],
  ['get_competitions', [
    /(?:get|show|list|display|what are)\s+(?:me\s+)?(?:all\s+)?(?:my\s+)?(?:competitions?|championships?|tournaments?|cups?)/i,
    /(?:my\s+)?(?:competitions?|championships?)\s+(?:list|please)/i,
    /show\s+(?:me\s+)?(?:all\s+)?(?:my\s+)?(?:competitions?|championships?|tournaments?|cups?)/i,
  ]],
  ['get_teams', [
    /(?:get|show|list|display|what are)\s+(?:me\s+)?(?:all\s+)?(?:my\s+)?teams?/i,
    /(?:my\s+)?teams?\s+(?:list|please)/i,
    /show\s+(?:me\s+)?(?:all\s+)?(?:my\s+)?teams?/i,
  ]],
  ['get_standings', [
    /(?:get|show|display)\s+(?:the\s+)?standings?\s+(?:for\s+)?(.+)?/i,
    /(?:what\s+(?:are|is)\s+(?:the\s+)?)?standings?\s+(?:for\s+)?(.+)?/i,
    /(.+?)\s+standings?/i,
  ]],
  ['create_league', [
    /create\s+(?:a\s+)?(\w+)\s+league\s+['"]?([^\s'"]+)['"]?\s+(?:and|with)\s+(?:a\s+)?cup/i,
    /create\s+(?:a\s+)?(\w+)\s+league\s+['"]?([^'"]+)['"]?/i,
    /create\s+(?:a\s+)?league\s+['"]?([^'"]+)['"]?\s+(?:for\s+)?(\w+)?/i,
  ]],
  ['simulate_match', [
    /sim(?:ulate)?\s+(?:the\s+)?(?:match|game|fixture)\s+(?:of\s+|between\s+)?(.+?)\s+(?:vs\.?|versus|v|against)\s+(.+)/i,
    /sim(?:ulate)?\s+(.+?)\s+(?:vs\.?|versus|against)\s+(.+)/i,
  ]],
  ['simulate_games', [
    new RegExp(`simulate\\s+(?:all\\s+)?(?:games?|matches?|fixtures?)\\s+.*?(?:competition|comp)(?:\\s+(?:id[:\\s]*)?)?(${UUID})`, 'i'),
    new RegExp(`simulate\\s+.*?(${UUID})`, 'i'),
    /simulate\s+(?:all\s+)?(?:games?|matches?|fixtures?)/i,
  ]],
  ['enter_result', [
    /(?:change|update|set|enter|record)\s+(?:the\s+)?(?:game|match|result|score)\s+(?:of\s+|for\s+)?(.+?)\s+(?:vs\.?|versus)\s+(.+?)[,\s]+(?:the\s+)?(?:score\s+)?(?:is\s+)?(\d+)\s*[-–:]\s*(\d+)/i,
    /(.+?)\s+(?:vs\.?|versus)\s+(.+?)[,\s]+(?:the\s+)?(?:score\s+)?(?:is\s+)?(\d+)\s*[-–:]\s*(\d+)/i,
    /(.+?)\s+(?:vs\.?|versus)\s+(.+?)\s+(\d+)\s*[-–:]\s*(\d+)/i,
    /^(.+?)\s*-\s*(.+?),\s*(\d+)\s*[-–:]\s*(\d+)\s*$/i,
    new RegExp(`(?:set|enter|record|save)\\s+(?:the\\s+)?result.*?(${UUID})\\s*:\\s*(.+?)\\s+(\\d+)\\s*[-\\u2013:]\\s*(.+?)\\s+(\\d+)`, 'i'),
    /(.+?)\s+(?:at\s+home\s+)?(?:won|beat|defeated)\s+(.+?)\s+(\d+)\s*[-–:]\s*(\d+)/i,
    /^(.+?)\s+(\d+)\s*[-–:]\s*(\d+)\s+(.+?)$/i,
  ]],
];
const EVENT_LINEUP_HINT =
  /\b(scored|scorer|scoring|goal\s+event|own[\s-]?goal|penalty\s+goal|yellow[\s-]?card|red[\s-]?card|booking|assist|substitut|line[\s-]?up|lineup|starting\s+(?:xi|eleven|line)|at\s+minute|\bminute\b)\b/i;

function regexDetectIntent(query) {
  const q = (query ?? '').toLowerCase().trim();
  const hasEventCue = EVENT_LINEUP_HINT.test(q);
  for (const [intent, patterns] of INTENT_PATTERNS) {
    if (intent === 'enter_result' && hasEventCue) continue;
    for (const re of patterns) if (re.test(q)) return intent;
  }
  return 'complex_query';
}

const WRITE_INTENT =
  /\b(?:create|generate|add|assign|update|change|rename|delete|remove|import|advance|simulate|record|enter|set|schedule|reschedule|publish|unpublish|save|apply)\b/i;
const SPORTS_WRITE_INTENT =
  /(?:\b\d+\s*[-–:]\s*\d+\b|\b(?:beat|defeated|won|drew|scored|assisted|saved|intercepted|booked)\b|\b(?:goal|assist|yellow card|red card|substitution)\s+by\b|\bmatch\s*day\s+\d+\b)/i;

function regexRequiresWriteApproval(message) {
  const m = message ?? '';
  return WRITE_INTENT.test(m) || SPORTS_WRITE_INTENT.test(m);
}

// ================================================================
// Suite 1 — easychamp-intent (26 synthetic chat messages)
// Labels use the IntentType enum from intent_router.py.
// ================================================================
const INTENT_CRITERIA = {
  get_leagues: 'The user wants to see the leagues they own or belong to.',
  get_competitions: 'The user wants to see competitions, championships, tournaments or cups.',
  get_teams: 'The user wants to see teams.',
  get_standings: 'The user wants the current table, standings or ranking of a competition.',
  create_league: 'The user asks to create a new league (optionally with a cup).',
  simulate_games: 'The user asks to simulate many fixtures at once: all games, the rest of the season, a whole competition.',
  simulate_match: 'The user asks to simulate exactly one named fixture between two teams, with no score given.',
  enter_result: 'The user is reporting a final score for a fixture so it gets recorded, e.g. "Team A 3-1 Team B".',
  disambiguation: 'The user is picking one option from a list the assistant just offered: a bare number, an ordinal, or a matchday number.',
  complex_query: 'Anything else that needs the full LLM tool path: questions about data or about how the product works, analysis, negations, goal/card/lineup events, or requests none of the other options covers.',
};
const INTENT_ITEMS = [
  { id: 'i01', message: 'show me all my leagues', label: 'get_leagues' },
  { id: 'i02', message: 'what leagues do i have?', label: 'get_leagues' },
  { id: 'i03', message: 'leagues pls', label: 'get_leagues' },
  { id: 'i04', message: 'покажи мои лиги', label: 'get_leagues' },
  { id: 'i05', message: 'list my competitions', label: 'get_competitions' },
  { id: 'i06', message: 'which tournaments am i running?', label: 'get_competitions' },
  { id: 'i07', message: 'muéstrame mis competiciones', label: 'get_competitions' },
  { id: 'i08', message: 'show teams', label: 'get_teams' },
  { id: 'i09', message: 'shwo me my teams', label: 'get_teams' },
  { id: 'i10', message: 'standings for the Miami Cup', label: 'get_standings' },
  { id: 'i11', message: 'how is my table looking in the winter league?', label: 'get_standings' },
  { id: 'i12', message: 'tabla de posiciones de la liga de invierno', label: 'get_standings' },
  { id: 'i13', message: 'create a soccer league "Sunny Isles Winter"', label: 'create_league' },
  { id: 'i14', message: 'start a new basketball league called Ocean Drive', label: 'create_league' },
  { id: 'i15', message: 'simulate all games', label: 'simulate_games' },
  { id: 'i16', message: 'simulate every remaining fixture in the cup', label: 'simulate_games' },
  { id: 'i17', message: 'sim the match Inter Miami vs Orlando City', label: 'simulate_match' },
  { id: 'i18', message: 'симулируй матч Интер Майами против Орландо', label: 'simulate_match' },
  { id: 'i19', message: 'simula el partido Barcelona vs Madrid', label: 'simulate_match' },
  { id: 'i20', message: 'Inter Miami 3-2 Orlando City', label: 'enter_result' },
  { id: 'i21', message: 'record that Barcelona beat Madrid 2-1', label: 'enter_result' },
  { id: 'i22', message: 'Реал 2:1 Барселона', label: 'enter_result' },
  { id: 'i23', message: 'Messi scored at minute 67, final score 1-1', label: 'complex_query' },
  { id: 'i24', message: 'the second one', label: 'disambiguation' },
  { id: 'i25', message: "don't show me my teams, show me the fixtures instead", label: 'complex_query' },
  { id: 'i26', message: 'explain what simulate all games does before I run it', label: 'complex_query' },
];

// ================================================================
// Suite 2 — easychamp-write-approval (24 synthetic messages)
// Label = would executing this message change durable data?
// ================================================================
const APPROVAL_ITEMS = [
  { id: 'w01', message: 'create a league called Miami Winter', label: true },
  { id: 'w02', message: 'delete the fixture between Inter and Orlando', label: true },
  { id: 'w03', message: 'Barcelona 3-1 Madrid', label: true },
  { id: 'w04', message: 'Реал обыграл Барсу 2:1, запиши результат', label: true },
  { id: 'w05', message: 'move the Saturday game to Sunday', label: true },
  { id: 'w06', message: 'swap the home and away teams for matchday 2', label: true },
  { id: 'w07', message: 'push the roster I pasted earlier into the U16 team', label: true },
  { id: 'w08', message: 'cancel the friendly against Ocean FC', label: true },
  { id: 'w09', message: 'make Diego the captain of the U16 squad', label: true },
  { id: 'w10', message: 'simulate the rest of the season', label: true },
  { id: 'w11', message: 'publish the winter competition', label: true },
  { id: 'w12', message: 'añade a Diego al equipo sub-16', label: true },
  { id: 'w13', message: "don't delete anything, just show me the fixtures", label: false },
  { id: 'w14', message: 'what does simulate mean?', label: false },
  { id: 'w15', message: 'can you explain how creating a league works?', label: false },
  { id: 'w16', message: 'show me the standings', label: false },
  { id: 'w17', message: 'who scored in the last match?', label: false },
  { id: 'w18', message: 'did Inter beat Orlando last week?', label: false },
  { id: 'w19', message: 'the final score was 3-2, right?', label: false },
  { id: 'w20', message: 'what is the record for most goals scored by a single player?', label: false },
  { id: 'w21', message: 'how do I update a result?', label: false },
  { id: 'w22', message: 'list all teams in the league', label: false },
  { id: 'w23', message: "remove me from this chat's notification list — actually never mind, forget it", label: false },
  { id: 'w24', message: 'is it safe to delete a competition that already has results?', label: false },
];

// ================================================================
// Suite 3 — easychamp-moderation (15 synthetic club-chat reports)
// ================================================================
const MODERATION_CATEGORY = {
  harassment: 'A member is insulting, threatening, demeaning or persistently targeting another person.',
  spam: 'Unsolicited promotion, repeated advertising, referral or scam links, mass unrelated posting.',
  off_topic: 'Harmless but wrong place: chatter unrelated to the club, team or match at hand.',
  safety_concern: 'Someone may be in danger: self-harm, a threat of violence, an unsafe situation involving a minor, a medical emergency.',
  false_report: 'The report itself is baseless or retaliatory: the quoted message shows nothing that breaks the rules.',
};
const MODERATION_ACTION = {
  dismiss: 'Close the report, take no action against the message or the author.',
  hide_message: 'Hide or remove the message, but do not sanction the author.',
  warn_user: 'Hide the message if needed and send the author a formal warning.',
  escalate_admin: 'Send this to a human administrator immediately for review.',
};
const MODERATION_ITEMS = [
  { id: 'm01', reason: 'harassment', note: 'He keeps going after my son after every game.', message: "you're garbage, quit the team before you embarrass your dad again", label: 'harassment', action: 'warn_user', sev: [2, 3] },
  { id: 'm02', reason: 'harassment', note: 'Called our keeper names in front of the U12 group.', message: 'the keeper is a clown, no wonder we lose every week', label: 'harassment', action: 'warn_user', sev: [1, 2] },
  { id: 'm03', reason: 'bullying', note: 'Third time this week, same kid targeted.', message: 'nobody wants you here. everyone in this chat agrees. just leave.', label: 'harassment', action: 'escalate_admin', sev: [2, 3] },
  { id: 'm04', reason: 'harassment', note: 'Threatened the referee.', message: "ref if you show up saturday i'll be waiting for you in the parking lot", label: 'safety_concern', action: 'escalate_admin', sev: [3, 3] },
  { id: 'm05', reason: 'spam', note: 'Posted the same link in six club channels.', message: 'FREE BOOTS!!! click bit.ly/xyz-deal and use my referral code DIEGO10', label: 'spam', action: 'hide_message', sev: [1, 2] },
  { id: 'm06', reason: 'advertising', note: 'Local business owner, posts every day.', message: 'Reminder: 20% off at my restaurant for all club parents this month, DM me', label: 'spam', action: 'hide_message', sev: [0, 1] },
  { id: 'm07', reason: 'spam', note: 'Looks like a crypto scam.', message: 'guaranteed 40% weekly returns, send USDT to this wallet, first 10 parents only', label: 'spam', action: 'escalate_admin', sev: [2, 3] },
  { id: 'm08', reason: 'off topic', note: 'Politics in the match-day thread.', message: 'anyway can we all agree the mayor is ruining this city', label: 'off_topic', action: 'dismiss', sev: [0, 1] },
  { id: 'm09', reason: 'off topic', note: 'Wrong channel.', message: 'does anyone have a good plumber in Sunny Isles?', label: 'off_topic', action: 'dismiss', sev: [0, 1] },
  { id: 'm10', reason: 'off topic', note: 'Flooded the squad chat with memes during the game.', message: '(17 consecutive meme images posted during the live match thread)', label: 'off_topic', action: 'hide_message', sev: [0, 2] },
  { id: 'm11', reason: 'other', note: 'This worries me, he is 15.', message: "honestly after today i don't see the point of any of this anymore, nobody would notice if i stopped showing up at all", label: 'safety_concern', action: 'escalate_admin', sev: [3, 3] },
  { id: 'm12', reason: 'safety', note: 'Sent during the away trip.', message: 'a stranger is following our U14 group around the parking lot, we are two coaches short', label: 'safety_concern', action: 'escalate_admin', sev: [3, 3] },
  { id: 'm13', reason: 'harassment', note: 'He reported me right after I benched him.', message: 'lineup for saturday is posted, please confirm by friday', label: 'false_report', action: 'dismiss', sev: [0, 0] },
  { id: 'm14', reason: 'spam', note: 'They report every message I post.', message: 'training moved to pitch 3, same time', label: 'false_report', action: 'dismiss', sev: [0, 0] },
  { id: 'm15', reason: 'harassment', note: 'Says the emoji was aimed at her.', message: 'good game everyone 👏', label: 'false_report', action: 'dismiss', sev: [0, 0] },
];

// ================================================================
// Suite 4 — vskill-crawl (real SKILL.md files + non-skill controls)
// Every file in the default corpus is tracked in the public
// github.com/anton-abyzov/specweave repository, so nothing private leaves the
// machine. Files under the operator's home directory are sent only when the run
// is started with --allow-local-files, and the report then names them.
// First CRAWL_EXCERPT_CHARS characters of each file.
// ================================================================
const CRAWL_EXCERPT_CHARS = 2500;
const SKILL_CATEGORY = {
  coding: 'Writing, reviewing, testing or debugging application code.',
  devops: 'Builds, releases, CI/CD, packaging, signing, deployment, infrastructure.',
  marketing: 'Content, copy, social media, outreach, campaigns, growth.',
  design: 'Visual design, UI, imagery, video, brand.',
  data: 'Data analysis, pipelines, ETL, reporting, dashboards, SQL.',
  productivity: 'Personal or office workflow: notes, documents, email, scheduling, admin, finance.',
  other: 'None of the above.',
};
const QUALITY_LEVELS = [
  'Not usable: no instructions, a stub, or content that would not help an agent do anything.',
  'Thin: a short description and a couple of generic bullets; an agent would still have to guess.',
  'Solid: clear scope, concrete steps or commands, enough detail to follow without guessing.',
  'Excellent: concrete commands and examples, failure modes and gotchas, decision rules, hard-won specifics.',
];
// `category: null` means "no ground-truth label" — the question is still asked (the
// answer is reported) but the item is excluded from category accuracy. Used where the
// correct bucket is genuinely arguable, so a label dispute cannot masquerade as a miss.
const repoItem = (id, rel, isSkill, category = null) => ({
  id, rel, isSkill, category,
  file: path.join(SPECWEAVE_REPO, ...rel.split('/')),
  local: false,
});
const CRAWL_FILES = [
  // real agent skills shipped in the repo (public)
  repoItem('c01', 'plugins/specweave/skills/increment/SKILL.md', true, 'coding'),
  repoItem('c02', 'plugins/specweave/skills/do/SKILL.md', true, 'coding'),
  repoItem('c03', 'plugins/specweave/skills/review/SKILL.md', true, 'coding'),
  repoItem('c04', 'plugins/specweave/skills/team/SKILL.md', true, 'coding'),
  repoItem('c05', 'skills/sw-task/SKILL.md', true, 'coding'),
  repoItem('c06', 'skills/sw-handoff/SKILL.md', true, 'coding'),
  repoItem('c07', 'skills-optional/tdd-cycle/SKILL.md', true, 'coding'),
  repoItem('c08', 'skills-optional/e2e/SKILL.md', true, 'coding'),
  repoItem('c09', 'skills-optional/debug/SKILL.md', true, 'coding'),
  repoItem('c10', 'skills-optional/release-expert/SKILL.md', true, 'devops'),
  repoItem('c11', 'skills-optional/diagrams/SKILL.md', true, null),
  repoItem('c12', 'plugins/specweave/skills/sync/SKILL.md', true, null),
  // non-skill controls (public): prose an agent-skill crawler must reject
  repoItem('c13', 'README.md', false, null),
  repoItem('c14', 'CODE_OF_CONDUCT.md', false, null),
  repoItem('c15', 'LICENSE', false, null),
  repoItem('c16', 'docs-site/DEPLOYMENT.md', false, 'devops'),
  repoItem('c17', 'docs-site/docs/academy/fundamentals/iac-fundamentals.md', false, 'devops'),
  repoItem('c18', 'docs-site/blog/2026-01-04-seo-best-practices.md', false, 'marketing'),
  repoItem('c19', 'docs-site/drafts/social-media-programmable-skills-v2.md', false, 'marketing'),
];

// Opt-in corpus (--allow-local-files). These live under the operator's home directory
// and are NOT public: their excerpts would be uploaded to the provider. Off by default;
// every file actually sent is listed in the JSON and markdown report. The list is kept
// to skills with no personal content — never credentials, finances, vault layout or
// client names — because the first 2500 characters of a skill often carry exactly that.
const LOCAL_CRAWL_FILES = [
  { id: 'l01', rel: '~/.agents/skills/webapp-testing/SKILL.md', file: path.join(SKILLS_DIR, 'webapp-testing', 'SKILL.md'), isSkill: true, category: 'coding', local: true },
  { id: 'l02', rel: '~/.agents/skills/frontend-design/SKILL.md', file: path.join(SKILLS_DIR, 'frontend-design', 'SKILL.md'), isSkill: true, category: 'design', local: true },
  { id: 'l03', rel: '~/.agents/skills/nanobanana/SKILL.md', file: path.join(SKILLS_DIR, 'nanobanana', 'SKILL.md'), isSkill: true, category: 'design', local: true },
  { id: 'l04', rel: '~/.agents/skills/cold-email/SKILL.md', file: path.join(SKILLS_DIR, 'cold-email', 'SKILL.md'), isSkill: true, category: 'marketing', local: true },
  { id: 'l05', rel: '~/.agents/skills/copywriting/SKILL.md', file: path.join(SKILLS_DIR, 'copywriting', 'SKILL.md'), isSkill: true, category: 'marketing', local: true },
];

function crawlCorpusSpec() {
  return ALLOW_LOCAL_FILES ? [...CRAWL_FILES, ...LOCAL_CRAWL_FILES] : CRAWL_FILES;
}

// ================================================================
// Suite 5 — inbox-triage (14 synthetic marketing@ emails)
// Entirely invented; no mailbox is read.
// ================================================================
const INBOX_CATEGORY = {
  customer_support: 'An existing user reporting a problem, asking how to do something, or asking for help with their account.',
  sales_lead: 'Someone interested in buying, upgrading, pricing or a demo.',
  partnership: 'A proposal to work together: integration, reseller, co-marketing, sponsorship, press.',
  spam_or_cold_outreach: 'Unsolicited vendor pitch, SEO/dev agency, bulk mail, phishing.',
  billing: 'Invoices, payments, receipts, refunds, cards, subscription charges.',
  newsletter: 'A subscribed bulletin, product update, digest or notification blast.',
  personal: 'A person writing to the human behind the address about something not about the product.',
};
const URGENCY_LEVELS = [
  'No urgency: nothing happens if this is never answered.',
  'Low: answer within the week.',
  'Medium: answer today; someone is waiting or money is involved.',
  'High: answer now; production is broken, money is at risk, or a deadline is hours away.',
];
const INBOX_ITEMS = [
  { id: 'e01', subject: 'Cannot log in since yesterday', snippet: 'Hi, our whole club has been locked out since the update. We have a tournament on Saturday and nobody can enter results. Please help.', label: 'customer_support', reply: true, urg: [2, 3] },
  { id: 'e02', subject: 'Question about exporting fixtures', snippet: 'Is there a way to export the fixture list to CSV? I could not find it in settings.', label: 'customer_support', reply: true, urg: [1, 2] },
  { id: 'e03', subject: 'Pricing for 40 teams', snippet: 'We run a regional youth league with about 40 teams. What would the annual cost be, and do you offer a nonprofit rate?', label: 'sales_lead', reply: true, urg: [1, 2] },
  { id: 'e04', subject: 'Demo request — Barcelona futsal association', snippet: 'We are evaluating three platforms this month. Could we get a 30 minute demo next week?', label: 'sales_lead', reply: true, urg: [1, 2] },
  { id: 'e05', subject: 'Integration proposal — scoreboard hardware', snippet: 'We make LED scoreboards used in 200 venues and would like to integrate with your live match API. Open to a call?', label: 'partnership', reply: true, urg: [0, 1] },
  { id: 'e06', subject: 'Sponsorship of your league product', snippet: 'Our sports drink brand is looking for co-marketing partners for the 2026 season. Who handles partnerships?', label: 'partnership', reply: true, urg: [0, 1] },
  { id: 'e07', subject: 'Boost your rankings — guaranteed page 1', snippet: 'Dear sir/madam, I reviewed your website and found 27 critical SEO errors. Our agency can fix them for $499/month.', label: 'spam_or_cold_outreach', reply: false, urg: [0, 0] },
  { id: 'e08', subject: 'Hire pre-vetted offshore developers', snippet: 'We provide senior React and .NET engineers at $18/hour. Reply STOP to unsubscribe.', label: 'spam_or_cold_outreach', reply: false, urg: [0, 0] },
  { id: 'e09', subject: 'Your invoice INV-2291 is 14 days overdue', snippet: 'This is a reminder that invoice INV-2291 for $840 remains unpaid. Service may be suspended after 30 days.', label: 'billing', reply: true, urg: [2, 3] },
  { id: 'e10', subject: 'Receipt for your Cloudflare payment', snippet: 'Thanks for your payment of $62.40. No action is required. View your invoice in the dashboard.', label: 'billing', reply: false, urg: [0, 1] },
  { id: 'e11', subject: 'Card declined — subscription at risk', snippet: 'We could not charge the card ending 4417 for the September renewal. Update your payment method within 3 days to avoid interruption.', label: 'billing', reply: false, urg: [2, 3] },
  { id: 'e12', subject: 'This week in sports tech', snippet: 'Issue #144: what the new streaming rights mean for grassroots clubs, plus five tools we tried this week.', label: 'newsletter', reply: false, urg: [0, 0] },
  { id: 'e13', subject: 'Your weekly usage summary', snippet: '1,204 fixtures created, 88 clubs active, 3 failed syncs. View the full report in your dashboard.', label: 'newsletter', reply: false, urg: [0, 1] },
  { id: 'e14', subject: 'Coffee next week?', snippet: 'Hey — saw you are back in Miami. Free for coffee Tuesday or Wednesday? Would be good to catch up properly.', label: 'personal', reply: true, urg: [0, 1] },
];

// ================================================================
// Runner
// ================================================================
async function runItems(items, build) {
  const calls = [];
  const results = await pool(items, CONCURRENCY, async (item) => {
    const { state, questions } = build(item);
    try {
      const res = await ask(state, questions, { id: item.id });
      calls.push({
        id: item.id,
        latencyMs: res.latencyMs,
        input_tokens: res.usage?.input_tokens ?? 0,
        output_tokens: res.usage?.output_tokens ?? 0,
        cost: res.usage?.cost ?? 0,
      });
      return { item, answers: res.answers, latencyMs: res.latencyMs, usage: res.usage, ok: true };
    } catch (err) {
      calls.push({ id: item.id, latencyMs: 0, input_tokens: 0, output_tokens: 0, cost: 0, error: String(err?.message ?? err) });
      return { item, error: String(err?.message ?? err), ok: false };
    }
  });
  const lat = calls.filter((c) => !c.error).map((c) => c.latencyMs).sort((a, b) => a - b);
  const stats = {
    calls: calls.length,
    failures: calls.filter((c) => c.error).length,
    latency: {
      p50: pct(lat, 50),
      p95: pct(lat, 95),
      mean: lat.length ? Math.round(lat.reduce((a, b) => a + b, 0) / lat.length) : 0,
      min: lat[0] ?? 0,
      max: lat[lat.length - 1] ?? 0,
    },
    input_tokens: calls.reduce((a, c) => a + c.input_tokens, 0),
    output_tokens: calls.reduce((a, c) => a + c.output_tokens, 0),
    cost: round(calls.reduce((a, c) => a + c.cost, 0), 8),
  };
  stats.costPer1kItems = round((stats.cost / Math.max(1, items.length)) * 1000, 4);
  return { results, stats };
}

const acc = (correct, total) => ({ correct, total, accuracy: total ? round(correct / total, 4) : 0 });

// ---------------------------------------------------- suite: intent ----
async function suiteIntent() {
  const { results, stats } = await runItems(INTENT_ITEMS, (item) => ({
    state: { message: item.message, product: 'EasyChamp — a sports league management chat assistant' },
    questions: {
      intent: {
        type: 'choice',
        instructions:
          'A user typed this message into the EasyChamp assistant. Which handler should it be routed to? Messages may be in English, Russian or Spanish, and may contain typos.',
        criteria: INTENT_CRITERIA,
      },
    },
  }));
  let jevOk = 0;
  let reOk = 0;
  const rows = [];
  const misses = [];
  for (const r of results) {
    const expected = r.item.label;
    const regexPred = regexDetectIntent(r.item.message);
    const a = r.ok ? r.answers.intent : null;
    const jevPred = a?.choice ?? null;
    if (jevPred === expected) jevOk++;
    if (regexPred === expected) reOk++;
    rows.push({
      id: r.item.id, message: r.item.message, expected, jev: jevPred,
      jevConfidence: a ? round(a.confidence, 3) : null,
      jevTop: a ? topProbs(a.probabilities) : null,
      regex: regexPred, jevCorrect: jevPred === expected, regexCorrect: regexPred === expected,
      latencyMs: r.latencyMs ?? null, error: r.error ?? null,
    });
    if (jevPred !== expected) {
      misses.push({ id: r.item.id, input: r.item.message, expected, got: jevPred, probabilities: a ? topProbs(a.probabilities, 4) : null, regexSaid: regexPred, error: r.error ?? null });
    }
  }
  return {
    name: 'easychamp-intent',
    title: 'EasyChamp chat intent routing (26 messages)',
    baselineName: 'INTENT_PATTERNS regex router (intent_router.py, ported)',
    items: INTENT_ITEMS.length,
    stats,
    metrics: { jev: acc(jevOk, INTENT_ITEMS.length), baseline: acc(reOk, INTENT_ITEMS.length) },
    rows, misses,
  };
}

// -------------------------------------------------- suite: approval ----
async function suiteApproval() {
  const { results, stats } = await runItems(APPROVAL_ITEMS, (item) => ({
    state: { message: item.message, product: 'EasyChamp — a sports league management chat assistant' },
    questions: {
      write: {
        type: 'noul',
        instructions:
          'Does this message ask the assistant to create, change or delete durable data (leagues, competitions, teams, players, fixtures, results, schedules, publication state)? Judge the request the user is actually making, not the words in isolation: a question about a feature, a retracted request, or an explicit instruction not to change anything is not a write.',
        criteria: {
          true: 'The user is instructing the assistant to perform a write: create, update, delete, schedule, publish, simulate, or record a result.',
          false: 'The user is asking a question, reading data, discussing how something works, negating or retracting a request, or chatting.',
        },
      },
    },
  }));
  const rows = [];
  let jevTP = 0, jevFP = 0, jevTN = 0, jevFN = 0;
  let reTP = 0, reFP = 0, reTN = 0, reFN = 0;
  const misses = [];
  for (const r of results) {
    const expected = r.item.label;
    const noul = r.ok ? r.answers.write.noul : null;
    const jevPred = noul === null ? null : noul >= 0.5;
    const rePred = regexRequiresWriteApproval(r.item.message);
    if (jevPred !== null) {
      if (expected && jevPred) jevTP++; else if (!expected && jevPred) jevFP++;
      else if (!expected && !jevPred) jevTN++; else jevFN++;
    }
    if (expected && rePred) reTP++; else if (!expected && rePred) reFP++;
    else if (!expected && !rePred) reTN++; else reFN++;
    rows.push({ id: r.item.id, message: r.item.message, expected, jevNoul: noul === null ? null : round(noul, 3), jev: jevPred, regex: rePred, jevCorrect: jevPred === expected, regexCorrect: rePred === expected, latencyMs: r.latencyMs ?? null, error: r.error ?? null });
    if (jevPred !== expected) misses.push({ id: r.item.id, input: r.item.message, expected, got: jevPred, noul: noul === null ? null : round(noul, 3), regexSaid: rePred, kind: expected ? 'false negative' : 'false positive', error: r.error ?? null });
  }
  const n = APPROVAL_ITEMS.length;
  return {
    name: 'easychamp-write-approval',
    title: 'EasyChamp write-approval gate (24 messages)',
    baselineName: 'requires_write_approval regex (chat_approval.py, ported)',
    items: n,
    stats,
    metrics: {
      jev: { ...acc(jevTP + jevTN, n), falsePositives: jevFP, falseNegatives: jevFN },
      baseline: { ...acc(reTP + reTN, n), falsePositives: reFP, falseNegatives: reFN },
    },
    rows, misses,
  };
}

// ------------------------------------------------ suite: moderation ----
async function suiteModeration() {
  const { results, stats } = await runItems(MODERATION_ITEMS, (item) => ({
    state: { report_reason: item.reason, reporter_note: item.note, reported_message: item.message },
    questions: {
      category: { type: 'choice', instructions: 'A club member reported a chat message. What is this report really about? Judge the reported message itself, not only the reason the reporter picked.', criteria: MODERATION_CATEGORY },
      severity: { type: 'score', instructions: 'How severe is the reported message?', criteria: ['Nothing wrong with it at all.', 'Mildly inappropriate; a nudge would be enough.', 'Clearly breaks club rules; the author should be sanctioned.', 'Severe: a threat, a danger to a person, or something that needs a human right now.'] },
      action: { type: 'choice', instructions: 'What should the moderation system do automatically with this report?', criteria: MODERATION_ACTION },
    },
  }));
  const rows = [];
  let catOk = 0, actOk = 0, sevOk = 0;
  const misses = [];
  for (const r of results) {
    const a = r.ok ? r.answers : null;
    const cat = a?.category?.choice ?? null;
    const act = a?.action?.choice ?? null;
    const sev = a?.severity?.score ?? null;
    const inBand = sev !== null && sev >= r.item.sev[0] - 0.5 && sev <= r.item.sev[1] + 0.5;
    if (cat === r.item.label) catOk++;
    if (act === r.item.action) actOk++;
    if (inBand) sevOk++;
    rows.push({ id: r.item.id, reason: r.item.reason, message: r.item.message.slice(0, 70), expectedCategory: r.item.label, jevCategory: cat, categoryConfidence: a ? round(a.category.confidence, 3) : null, expectedAction: r.item.action, jevAction: act, expectedSeverity: r.item.sev, jevSeverity: sev === null ? null : round(sev, 2), severityInBand: inBand, latencyMs: r.latencyMs ?? null, error: r.error ?? null });
    if (cat !== r.item.label || act !== r.item.action || !inBand) {
      misses.push({ id: r.item.id, input: r.item.message.slice(0, 90), expected: `${r.item.label} / ${r.item.action} / sev ${r.item.sev.join('-')}`, got: `${cat} / ${act} / sev ${sev === null ? 'n/a' : round(sev, 2)}`, probabilities: a ? topProbs(a.category.probabilities, 3) : null, error: r.error ?? null });
    }
  }
  const n = MODERATION_ITEMS.length;
  return {
    name: 'easychamp-moderation',
    title: 'EasyChamp club-chat moderation triage (15 reports)',
    baselineName: null,
    items: n, stats,
    metrics: { category: acc(catOk, n), action: acc(actOk, n), severityInBand: acc(sevOk, n) },
    rows, misses,
  };
}

// ----------------------------------------------------- suite: crawl ----
async function suiteCrawl() {
  const spec = crawlCorpusSpec();
  const present = [];
  for (const f of spec) {
    if (!existsSync(f.file)) continue;
    const text = await readFile(f.file, 'utf8');
    present.push({ ...f, chars: text.length, text: text.slice(0, CRAWL_EXCERPT_CHARS) });
  }
  const { results, stats } = await runItems(present, (item) => ({
    state: { file_name: path.basename(item.file), content: item.text },
    questions: {
      is_skill: { type: 'noul', instructions: 'Is this file an agent skill definition — a document written to instruct an AI coding agent how to perform a specific task?', criteria: { true: 'A skill, playbook or agent instruction file: it tells an agent when to act and what to do.', false: 'Any other document: a readme, licence, changelog, code of conduct, article, or configuration.' } },
      category: { type: 'choice', instructions: 'Which single category best describes what this document is about?', criteria: SKILL_CATEGORY },
      quality: { type: 'score', instructions: 'How useful would this document be to an agent that had to do the job it describes, with nothing else to go on?', criteria: QUALITY_LEVELS },
    },
  }));
  const rows = [];
  let skillOk = 0, catOk = 0, catTotal = 0;
  const misses = [];
  const qualities = [];
  for (const r of results) {
    const a = r.ok ? r.answers : null;
    const noul = a?.is_skill?.noul ?? null;
    const pred = noul === null ? null : noul >= 0.5;
    const cat = a?.category?.choice ?? null;
    const q = a?.quality?.score ?? null;
    if (pred === r.item.isSkill) skillOk++;
    if (r.item.category) {
      catTotal++;
      if (cat === r.item.category) catOk++;
    }
    if (q !== null) qualities.push({ id: r.item.id, name: r.item.rel + (r.item.isSkill ? '' : ' (control)'), chars: r.item.chars, truncated: r.item.chars > CRAWL_EXCERPT_CHARS, quality: round(q, 2) });
    rows.push({ id: r.item.id, file: r.item.rel, local: r.item.local === true, chars: r.item.chars, truncated: r.item.chars > CRAWL_EXCERPT_CHARS, expectedIsSkill: r.item.isSkill, jevIsSkill: pred, noul: noul === null ? null : round(noul, 3), expectedCategory: r.item.category, jevCategory: cat, categoryConfidence: a ? round(a.category.confidence, 3) : null, quality: q === null ? null : round(q, 2), latencyMs: r.latencyMs ?? null, error: r.error ?? null });
    if (pred !== r.item.isSkill || (r.item.category && cat !== r.item.category)) {
      misses.push({ id: r.item.id, input: r.item.rel, expected: `is_skill=${r.item.isSkill} / ${r.item.category ?? 'n/a'}`, got: `is_skill=${pred} (noul ${noul === null ? 'n/a' : round(noul, 2)}) / ${cat}`, probabilities: a ? topProbs(a.category.probabilities, 3) : null, error: r.error ?? null });
    }
  }
  const sentLocal = present.filter((p) => p.local).map((p) => p.rel);
  return {
    name: 'vskill-crawl',
    title: `vskill crawl classification (${present.filter((p) => p.isSkill).length} real SKILL.md + ${present.filter((p) => !p.isSkill).length} non-skill controls)`,
    baselineName: null,
    items: present.length, stats,
    metrics: { isAgentSkill: acc(skillOk, present.length), category: acc(catOk, catTotal) },
    rows, misses,
    extras: {
      qualityScores: qualities.sort((a, b) => b.quality - a.quality),
      note: 'quality has no ground-truth label; the distribution is reported for calibration only',
      excerptChars: CRAWL_EXCERPT_CHARS,
      corpus: sentLocal.length ? 'public specweave repository + local files (--allow-local-files)' : 'files tracked in the public specweave repository',
    },
    localFilesSent: sentLocal,
    skipped: spec.filter((f) => !existsSync(f.file)).map((f) => f.rel),
  };
}

// ----------------------------------------------------- suite: inbox ----
async function suiteInbox() {
  const { results, stats } = await runItems(INBOX_ITEMS, (item) => ({
    state: { mailbox: 'marketing@ (shared product inbox)', subject: item.subject, snippet: item.snippet },
    questions: {
      category: { type: 'choice', instructions: 'Which single bucket does this email belong in?', criteria: INBOX_CATEGORY },
      urgency: { type: 'score', instructions: 'How soon does this email need a human?', criteria: URGENCY_LEVELS },
      needs_reply: { type: 'noul', instructions: 'Does this email need a written reply from a human?', criteria: { true: 'A person is waiting for an answer, or ignoring it costs the business something.', false: 'Automated, informational, bulk or unsolicited; no reply is expected or warranted.' } },
    },
  }));
  const rows = [];
  let catOk = 0, replyOk = 0, urgOk = 0;
  const misses = [];
  for (const r of results) {
    const a = r.ok ? r.answers : null;
    const cat = a?.category?.choice ?? null;
    const urg = a?.urgency?.score ?? null;
    const noul = a?.needs_reply?.noul ?? null;
    const reply = noul === null ? null : noul >= 0.5;
    const inBand = urg !== null && urg >= r.item.urg[0] - 0.5 && urg <= r.item.urg[1] + 0.5;
    if (cat === r.item.label) catOk++;
    if (reply === r.item.reply) replyOk++;
    if (inBand) urgOk++;
    rows.push({ id: r.item.id, subject: r.item.subject, expectedCategory: r.item.label, jevCategory: cat, categoryConfidence: a ? round(a.category.confidence, 3) : null, expectedReply: r.item.reply, jevReply: reply, noul: noul === null ? null : round(noul, 3), expectedUrgency: r.item.urg, jevUrgency: urg === null ? null : round(urg, 2), urgencyInBand: inBand, latencyMs: r.latencyMs ?? null, error: r.error ?? null });
    if (cat !== r.item.label || reply !== r.item.reply || !inBand) {
      misses.push({ id: r.item.id, input: r.item.subject, expected: `${r.item.label} / reply=${r.item.reply} / urg ${r.item.urg.join('-')}`, got: `${cat} / reply=${reply} (noul ${noul === null ? 'n/a' : round(noul, 2)}) / urg ${urg === null ? 'n/a' : round(urg, 2)}`, probabilities: a ? topProbs(a.category.probabilities, 3) : null, error: r.error ?? null });
    }
  }
  const n = INBOX_ITEMS.length;
  return {
    name: 'inbox-triage',
    title: 'Shared-inbox triage (14 synthetic emails)',
    baselineName: null,
    items: n, stats,
    metrics: { category: acc(catOk, n), needsReply: acc(replyOk, n), urgencyInBand: acc(urgOk, n) },
    rows, misses,
  };
}

const SUITES = [
  { key: 'intent', name: 'easychamp-intent', run: suiteIntent, items: INTENT_ITEMS.length, questionsPerItem: 1, desc: 'EasyChamp chat intent routing vs the INTENT_PATTERNS regex router' },
  { key: 'approval', name: 'easychamp-write-approval', run: suiteApproval, items: APPROVAL_ITEMS.length, questionsPerItem: 1, desc: 'EasyChamp write-approval gate vs the requires_write_approval regex' },
  { key: 'moderation', name: 'easychamp-moderation', run: suiteModeration, items: MODERATION_ITEMS.length, questionsPerItem: 3, desc: 'Club-chat moderation: category + severity + auto action' },
  { key: 'crawl', name: 'vskill-crawl', run: suiteCrawl, items: crawlCorpusSpec().length, questionsPerItem: 3, desc: 'vskill crawl: is-a-skill + category + quality over public repository files' },
  { key: 'inbox', name: 'inbox-triage', run: suiteInbox, items: INBOX_ITEMS.length, questionsPerItem: 3, desc: 'Shared-inbox triage: category + urgency + needs-reply' },
];

// ================================================================
// Reporting
// ================================================================
// Hand-written commentary. Every entry records the run it was written for: a
// signature of that suite's metrics, plus (for the headline) the suite set, item
// count and failure count of the whole run. `attachProse` stamps a piece of prose
// into the report only when its signature still matches the run being rendered, so
// a partial run (`--suite intent`) or a re-run where Jev answers differently gets
// freshly computed tables with no stale claims sitting next to them. Numbers that
// move between runs — accuracies, latency, cost, individual probabilities — are
// interpolated from the report instead of being typed into the prose.
function suiteSignature(s) {
  return Object.entries(s.metrics)
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([k, v]) => `${k}:${v.correct}/${v.total}${v.falsePositives === undefined ? '' : `(fp${v.falsePositives},fn${v.falseNegatives})`}`)
    .join(' ');
}

const rowOf = (s, id) => s.rows.find((r) => r.id === id) ?? {};
const nOf = (s, k) => `${s.metrics[k]?.correct ?? '?'}/${s.metrics[k]?.total ?? '?'}`;
const per1k = (s) => `$${s.stats.costPer1kItems.toFixed(4)}`;
const questionsIn = (report) =>
  report.suites.reduce((a, s) => a + s.items * (SUITES.find((x) => x.name === s.name)?.questionsPerItem ?? 0), 0);

const RECORDED_SUITES = {
  'easychamp-intent': {
    signature: 'baseline:12/26 jev:25/26',
    reading: (s) => {
      const miss = s.misses[0] ?? {};
      const missRow = rowOf(s, miss.id);
      return [
        `Jev ${nOf(s, 'jev')} against the shipped regex router's ${nOf(s, 'baseline')} on the same messages. The port is exact: both implementations were run over all ${s.items} inputs and the outputs diffed byte-for-byte against \`intent_router.py\`.`,
        '',
        'The regex misses everything it was not written for — Russian (`покажи мои лиги`), Spanish (`muéstrame mis competiciones`), a typo (`shwo me my teams`), and ordinary paraphrases (`what leagues do i have?`, `start a new basketball league called Ocean Drive`, `simulate every remaining fixture in the cup`). Worse than missing, it is confidently wrong twice: `don\'t show me my teams, show me the fixtures instead` → `get_teams`, and `explain what simulate all games does before I run it` → `simulate_games` — a question *about* a bulk write classified as the bulk write.',
        '',
        `Jev's single miss is the one case the regex gets right by construction: \`${miss.input}\` → \`${miss.got}\` at ${missRow.jevConfidence}, where the router has a hard-coded event-cue escape hatch (added in increment 0099) that sends goal/card/lineup messages to the LLM tool path. Jev cannot know that policy from the option wording. Note the confidence: ${missRow.jevConfidence} is under the 0.70 \`jev.thresholds.route\` default, so the integration would have deferred instead of acting. The shape that follows is regex-first for the cheap exact hits, Jev for everything that falls through, and the confidence threshold as the handoff back to the LLM.`,
        '',
        `At ${per1k(s)} per 1,000 messages, routing EasyChamp's entire chat volume through Jev costs less than the single LLM call it avoids on one message.`,
      ].join('\n');
    },
  },
  'easychamp-write-approval': {
    signature: 'baseline:10/24(fp9,fn5) jev:24/24(fp0,fn0)',
    reading: (s) => {
      const b = s.metrics.baseline;
      return [
        `${nOf(s, 'jev')} against the shipped \`requires_write_approval\` regex's ${nOf(s, 'baseline')} — ${b.falsePositives} false positives and ${b.falseNegatives} false negatives. This is the suite where the regex is not merely weaker but actively harmful in both directions.`,
        '',
        'It demands a write confirmation for `what does simulate mean?`, `who scored in the last match?`, `did Inter beat Orlando last week?`, `how do I update a result?` and `is it safe to delete a competition that already has results?` — all pure questions — because it keyword-matches `simulate`, `scored`, `beat`, `update`, `delete`. Users trained by that noise click Confirm without reading, which is exactly how an approval gate stops protecting anything. In the other direction it waves five real writes straight through: `move the Saturday game to Sunday`, `cancel the friendly against Ocean FC`, `make Diego the captain of the U16 squad`, `push the roster I pasted earlier into the U16 team`, and the Spanish `añade a Diego al equipo sub-16` — the verb list is closed and English-only.',
        '',
        `Jev got every one, including both negation shapes (\`don't delete anything, just show me the fixtures\`, \`remove me from this chat's notification list — actually never mind, forget it\`). ${per1k(s)} per 1,000 messages at ${s.stats.latency.p50} ms p50. This is the strongest result in the bench and the first integration I would ship: keep the regex as a fast pre-filter that can only ever escalate, and let Jev veto its false positives before the dialog is shown.`,
      ].join('\n');
    },
  },
  'easychamp-moderation': {
    signature: 'action:10/15 category:14/15 severityInBand:15/15',
    reading: (s) => {
      const actionMisses = s.rows.filter((r) => r.jevAction !== r.expectedAction);
      const catMiss = s.rows.find((r) => r.jevCategory !== r.expectedCategory);
      return [
        `Category ${nOf(s, 'category')} and severity ${nOf(s, 'severityInBand')} inside the expected band; the auto-action choice is the weak one at ${nOf(s, 'action')}.`,
        '',
        `Every action miss is a one-notch policy disagreement, not a misread: ${actionMisses.map((r) => `\`${r.id}\` (${r.jevCategory}) label \`${r.expectedAction}\` → Jev \`${r.jevAction}\``).join('; ')}. Jev read the messages correctly; it simply has no way to know this club's escalation policy.${catMiss ? ` The single category miss — \`${catMiss.id}\` ${catMiss.message} → \`${catMiss.jevCategory}\` over \`${catMiss.expectedCategory}\` — is arguably better than my label.` : ''}`,
        '',
        'The design conclusion: ask Jev what the message *is* (category and severity, both near-perfect), then map to an action deterministically in code from the category × severity grid. Do not ask a model to guess house policy that is three lines of config. The three cases the feature exists for — a parking-lot threat to a referee, a 15-year-old\'s self-harm signal, a stranger following a U14 group — all came back `safety_concern` / `escalate_admin` / severity 3.0, and the three retaliatory false reports all came back `false_report` / `dismiss` / severity 0.0.',
      ].join('\n');
    },
  },
  'vskill-crawl': {
    signature: 'category:13/14 isAgentSkill:19/19',
    reading: (s) => {
      const noul = (skill) => s.rows.filter((r) => r.expectedIsSkill === skill && r.noul !== null).map((r) => r.noul).sort((a, b) => a - b);
      const skills = noul(true);
      const controls = noul(false);
      const catMiss = s.rows.filter((r) => r.expectedCategory && r.jevCategory !== r.expectedCategory);
      const skillRows = s.rows.filter((r) => r.expectedIsSkill && typeof r.quality === 'number' && r.chars);
      const bySize = [...skillRows].sort((a, b) => b.chars - a.chars);
      const big = bySize.slice(0, 3);
      const small = bySize.slice(-3);
      const meanQ = (rs) => round(rs.reduce((a, r) => a + r.quality, 0) / Math.max(1, rs.length), 2);
      const kb = (n) => `${Math.max(1, Math.round(n / 1024))} KB`;
      const sizeEffect = big.length && small.length && meanQ(big) < meanQ(small);
      return [
        `\`is_agent_skill\` ${nOf(s, 'isAgentSkill')} on ${s.extras?.corpus ?? 'the repository corpus'}, with clean separation: the ${skills.length} real SKILL.md files sit at noul ${skills[0]}–${skills[skills.length - 1]}, the ${controls.length} non-skill controls (readme, code of conduct, licence, a deployment guide, an IaC course page, a SEO blog post and a social-media draft) at ${controls[0]}–${controls[controls.length - 1]}. Nothing sits near the 0.5 line, which is the property the crawler actually needs.`,
        '',
        `Category ${nOf(s, 'category')} over the items that carry an unambiguous label. Files whose bucket is genuinely arguable (\`diagrams\`, \`sync\`) are asked but not scored, so a label dispute cannot masquerade as a miss.${catMiss.length ? ` The miss is ${catMiss.map((r) => `\`${r.file}\` → ${r.jevCategory} (${r.categoryConfidence}) over ${r.expectedCategory}`).join('; ')} — a hand-off skill is about moving work between sessions, so the label is the weaker half of that disagreement.` : ''}`,
        '',
        `Quality is unlabelled and reported for calibration only; it is not a ranking. One artefact must be recorded before this goes near the crawler: the bench feeds the **first ${s.extras?.excerptChars ?? CRAWL_EXCERPT_CHARS} characters**, so long documents are judged on their preamble. ${sizeEffect ? `The three largest SKILL.md files (${kb(big[big.length - 1].chars)}–${kb(big[0].chars)}: ${big.map((r) => r.file.split('/').slice(-2)[0]).join(', ')}) average ${meanQ(big)}, while the three smallest (${kb(small[small.length - 1].chars)}–${kb(small[0].chars)}) average ${meanQ(small)} — truncation penalises exactly the files with the most content` : `In this corpus the largest SKILL.md files average ${meanQ(big)} against ${meanQ(small)} for the smallest, so no size effect is visible`}. Jev accepts 32k tokens per question; feed whole files, or head + tail, never a fixed prefix.`,
        '',
        'Corpus note: every file here is tracked in the public `specweave` repository, so running the bench discloses nothing. `--allow-local-files` exists for testing against a personal skill library; when it is used the report names each local file whose excerpt was sent. A bench that silently uploads the operator\'s `~/.agents/skills` is a data-exfiltration path, not evidence.',
      ].join('\n');
    },
  },
  'inbox-triage': {
    signature: 'category:14/14 needsReply:14/14 urgencyInBand:14/14',
    reading: (s) => [
      `${nOf(s, 'category')} on all three questions — category, urgency band and needs-reply — and worth stating plainly: I wrote both the emails and the labels, so this is a ceiling test on a small, clean, unambiguous set, not evidence that it survives a real inbox.`,
      '',
      `What it does establish is the economics and the shape of the traps. Three questions on one call cost ${per1k(s)} per 1,000 emails at ${s.stats.latency.p50} ms p50, and the distinctions that matter land correctly: an overdue-invoice reminder is \`billing\` / urgency 2–3 / needs a reply, a payment receipt is \`billing\` but needs none, a card-declined notice is urgent but automated, a cold SEO pitch scores urgency 0 and reply false, and a personal "coffee next week?" is separated from the sales leads. Real evidence would need a labelled sample of actual mail, which is deliberately out of scope here — this bench reads no private mail.`,
    ].join('\n'),
  },
};

const RECORDED_HEADLINE = {
  suites: ['easychamp-intent', 'easychamp-write-approval', 'easychamp-moderation', 'vskill-crawl', 'inbox-triage'],
  items: 98,
  failures: 0,
  text: (report) => {
    const t = report.totals;
    const by = Object.fromEntries(report.suites.map((s) => [s.name, s]));
    const intent = by['easychamp-intent'];
    const appr = by['easychamp-write-approval'];
    const mod = by['easychamp-moderation'];
    const missRow = rowOf(intent, intent.misses[0]?.id);
    return `${t.items} items, ${questionsIn(report)} questions, ${t.failures} failed calls, $${t.cost.toFixed(5)} in total. Jev beat the two shipped EasyChamp regex baselines by a wide margin on their own inputs — ${nOf(intent, 'jev')} vs ${nOf(intent, 'baseline')} on intent routing, ${nOf(appr, 'jev')} vs ${nOf(appr, 'baseline')} on the write-approval gate — at ${t.latency.p50} ms p50 and $${t.costPer1kItems.toFixed(4)} per 1,000 items. Its misses are informative rather than random: the one intent miss came back at ${missRow.jevConfidence} confidence, under the 0.70 route threshold, and the ${mod.rows.filter((r) => r.jevAction !== r.expectedAction).length} moderation auto-action misses are one-notch policy disagreements on decisions that belong in code, not in a model.`;
  },
};

// Stamp the prose that still describes this exact run, and record what was skipped.
function attachProse(report) {
  const readings = {};
  const stale = {};
  for (const s of report.suites) {
    const rec = RECORDED_SUITES[s.name];
    if (!rec) continue;
    const sig = suiteSignature(s);
    if (sig === rec.signature) {
      try {
        readings[s.name] = rec.reading(s, report);
      } catch (err) {
        stale[s.name] = { recorded: rec.signature, thisRun: sig, error: String(err?.message ?? err) };
      }
    } else {
      stale[s.name] = { recorded: rec.signature, thisRun: sig };
    }
  }
  const names = report.suites.map((s) => s.name);
  const headlineFits =
    names.length === RECORDED_HEADLINE.suites.length &&
    RECORDED_HEADLINE.suites.every((n) => names.includes(n)) &&
    names.every((n) => readings[n]) &&
    report.totals.items === RECORDED_HEADLINE.items &&
    report.totals.failures === RECORDED_HEADLINE.failures;
  report.readings = readings;
  report.staleReadings = stale;
  report.headline = headlineFits ? RECORDED_HEADLINE.text(report) : null;
  return report;
}

const md = (v) => String(v ?? '—').replace(/\|/g, '\\|').replace(/\n/g, ' ');
const pctS = (a) => `${(a.accuracy * 100).toFixed(1)}% (${a.correct}/${a.total})`;

function renderMarkdown(report) {
  const L = [];
  L.push('# Jev (TypeSafe System One) bench — increment 0878');
  L.push('');
  L.push(`Run ${report.generatedAt} · model \`${report.model}\` (\`${report.servedModel ?? 'n/a'}\`) · \`${report.endpoint}\` · concurrency ${report.concurrency}.`);
  L.push('');
  const localSent = report.localFilesSent ?? [];
  if (localSent.length) {
    L.push(
      `**Local files were sent to the provider.** This run used \`--allow-local-files\`, so besides the synthetic inputs and the public repository files, the first ${report.crawlExcerptChars ?? CRAWL_EXCERPT_CHARS} characters of ${localSent.length} file(s) outside the repository were POSTed to \`${report.endpoint}\`: ` +
        localSent.map((f) => `\`${f}\``).join(', ') +
        '. Treat those excerpts as disclosed to the provider. No mailbox, vault or customer data was read. The API key is read from `OPENROUTER_API_KEY` and never appears in this report.',
    );
  } else {
    L.push('All inputs are either synthetic (written into `jev-bench.mjs`) or files tracked in the public `specweave` repository. Nothing outside the repository was read or sent: no mailbox, vault, home-directory or customer data. The API key is read from `OPENROUTER_API_KEY` and never appears in this report.');
  }
  L.push('');
  L.push('## Totals');
  L.push('');
  L.push(`| items | calls | failures | p50 | p95 | input tok | output tok | cost | cost / 1k items |`);
  L.push(`|---|---|---|---|---|---|---|---|---|`);
  const t = report.totals;
  L.push(`| ${t.items} | ${t.calls} | ${t.failures} | ${t.latency.p50} ms | ${t.latency.p95} ms | ${t.input_tokens} | ${t.output_tokens} | $${t.cost.toFixed(6)} | $${t.costPer1kItems.toFixed(4)} |`);
  L.push('');
  if (report.headline) {
    L.push('## Headline');
    L.push('');
    L.push(report.headline);
    L.push('');
  } else {
    L.push('## Headline');
    L.push('');
    L.push('_No recorded headline matches this run — the suite set or the results differ from the run the commentary in `jev-bench.mjs` was written for. Every table in this report is computed from this run._');
    L.push('');
  }
  L.push('## Suite summary');
  L.push('');
  L.push('| suite | items | Jev (primary metric) | regex baseline | p50 | p95 | cost | cost / 1k items |');
  L.push('|---|---|---|---|---|---|---|---|');
  for (const s of report.suites) {
    const [hk, head] = Object.entries(s.metrics).find(([k]) => k !== 'baseline');
    const base = s.metrics.baseline ? pctS(s.metrics.baseline) : '—';
    L.push(`| ${s.name} | ${s.items} | ${hk} ${pctS(head)} | ${base} | ${s.stats.latency.p50} ms | ${s.stats.latency.p95} ms | $${s.stats.cost.toFixed(6)} | $${s.stats.costPer1kItems.toFixed(4)} |`);
  }
  L.push('');
  for (const s of report.suites) {
    L.push(`## ${s.title}`);
    L.push('');
    if (s.baselineName) { L.push(`Baseline: ${s.baselineName}.`); L.push(''); }
    L.push('| metric | result |');
    L.push('|---|---|');
    for (const [k, v] of Object.entries(s.metrics)) {
      const extra = v.falsePositives !== undefined ? ` — FP ${v.falsePositives}, FN ${v.falseNegatives}` : '';
      L.push(`| ${k} | ${pctS(v)}${extra} |`);
    }
    L.push(`| latency p50 / p95 | ${s.stats.latency.p50} ms / ${s.stats.latency.p95} ms |`);
    L.push(`| tokens in / out | ${s.stats.input_tokens} / ${s.stats.output_tokens} |`);
    L.push(`| cost | $${s.stats.cost.toFixed(6)} (${'$' + s.stats.costPer1kItems.toFixed(4)} per 1,000 items) |`);
    if (s.stats.failures) L.push(`| failed calls | ${s.stats.failures} |`);
    L.push('');
    if (s.misses.length) {
      L.push(`### Misses (${s.misses.length})`);
      L.push('');
      L.push('| id | input | expected | Jev said | probabilities | baseline |');
      L.push('|---|---|---|---|---|---|');
      for (const m of s.misses) {
        L.push(`| ${m.id} | ${md(m.input)} | ${md(m.expected)} | ${md(m.got ?? m.error)} | ${md(m.probabilities ?? m.noul)} | ${m.regexSaid === undefined ? '—' : md(String(m.regexSaid))} |`);
      }
      L.push('');
    } else {
      L.push('No misses.');
      L.push('');
    }
    if (s.name === 'easychamp-intent' || s.name === 'easychamp-write-approval') {
      const wrong = s.rows.filter((r) => !r.regexCorrect);
      L.push(`### Where the regex baseline is wrong (${wrong.length})`);
      L.push('');
      L.push('| id | input | expected | regex said | Jev said |');
      L.push('|---|---|---|---|---|');
      for (const r of wrong) {
        L.push(`| ${r.id} | ${md(r.message)} | ${md(String(r.expected))} | ${md(String(r.regex))} | ${md(String(r.jev))} |`);
      }
      L.push('');
    }
    if (s.extras?.qualityScores) {
      L.push('### Quality scores (0–3, unlabelled — calibration only)');
      L.push('');
      L.push('| skill | quality |');
      L.push('|---|---|');
      for (const q of s.extras.qualityScores) L.push(`| ${md(q.name)} | ${q.quality} |`);
      L.push('');
    }
    L.push('### Reading');
    L.push('');
    const reading = report.readings?.[s.name];
    if (reading) {
      L.push(reading);
    } else {
      const stale = report.staleReadings?.[s.name];
      L.push(
        stale
          ? `_The recorded commentary for this suite describes a different result (\`${stale.recorded}\`); this run scored \`${stale.thisRun}\`, so it is withheld rather than printed next to numbers it does not describe._`
          : '_(no reading recorded for this suite)_',
      );
    }
    L.push('');
  }
  L.push('---');
  L.push('');
  L.push('Raw per-item records, probabilities and latencies: `jev-bench.json`. Regenerate this markdown from that JSON with `node scripts/jev-bench.mjs --from-json` (no network).');
  L.push('');
  return L.join('\n');
}

function printDryRun() {
  console.log('jev-bench — dry run (no network)');
  console.log(`endpoint: ${ENDPOINT}`);
  console.log(`model:    ${MODEL}`);
  console.log(`key:      OPENROUTER_API_KEY ${process.env.OPENROUTER_API_KEY ? '(present)' : '(NOT SET — a live run would fail)'}`);
  console.log(`out:      ${outDirArg}`);
  console.log(`concurrency: ${CONCURRENCY}`);
  console.log('');
  let items = 0;
  let questions = 0;
  for (const s of SUITES) {
    const selected = !onlySuites.length || onlySuites.includes(s.key);
    items += selected ? s.items : 0;
    questions += selected ? s.items * s.questionsPerItem : 0;
    console.log(`  ${selected ? '[x]' : '[ ]'} ${s.key.padEnd(11)} ${String(s.items).padStart(2)} items × ${s.questionsPerItem} question(s)  — ${s.desc}`);
  }
  console.log('');
  const corpus = crawlCorpusSpec();
  const missing = corpus.filter((f) => !existsSync(f.file));
  const localInCorpus = corpus.filter((f) => f.local);
  console.log(`crawl corpus: ${corpus.length - missing.length}/${corpus.length} source files present${missing.length ? ` (missing: ${missing.map((m) => m.rel).join(', ')})` : ''}`);
  console.log(
    localInCorpus.length
      ? `local files: ${localInCorpus.length} file(s) OUTSIDE the repository would be sent (--allow-local-files): ${localInCorpus.map((f) => f.rel).join(', ')}`
      : 'local files: none — every input is synthetic or tracked in the public specweave repository (pass --allow-local-files to include ~/.agents/skills)',
  );
  console.log(`baselines: intent_router.INTENT_PATTERNS + chat_approval.requires_write_approval (ported to JS, run offline)`);
  console.log('');
  console.log(`total: ${items} items, ${items} API calls, ${questions} questions`);
  console.log('dry run OK');
}

async function main() {
  if (DRY_RUN) {
    printDryRun();
    return;
  }
  await mkdir(outDirArg, { recursive: true });
  const jsonPath = path.join(outDirArg, 'jev-bench.json');
  const mdPath = path.join(outDirArg, 'jev-bench.md');

  if (argv.includes('--from-json')) {
    const report = attachProse(JSON.parse(await readFile(jsonPath, 'utf8')));
    await writeFile(mdPath, renderMarkdown(report), 'utf8');
    console.log(`re-rendered ${mdPath} from ${jsonPath}`);
    return;
  }

  apiKey = process.env.OPENROUTER_API_KEY ?? '';
  if (!apiKey) {
    console.error('OPENROUTER_API_KEY is not set. Run `source ~/.zshrc` first, or use --dry-run.');
    process.exit(4);
  }

  const chosen = SUITES.filter((s) => !onlySuites.length || onlySuites.includes(s.key));
  const suites = [];
  let servedModel = null;
  for (const s of chosen) {
    process.stderr.write(`running ${s.key} ... `);
    const t0 = Date.now();
    const out = await s.run();
    suites.push(out);
    process.stderr.write(`${out.items} items in ${Date.now() - t0} ms, ${out.stats.failures} failures\n`);
  }
  try {
    const probe = await ask({ ok: true }, { q: { type: 'noul', instructions: 'Is this a probe?' } });
    servedModel = probe.model;
  } catch { /* non-fatal */ }

  const allLat = suites.flatMap((s) => s.rows.map((r) => r.latencyMs).filter((n) => typeof n === 'number' && n > 0)).sort((a, b) => a - b);
  const totals = {
    items: suites.reduce((a, s) => a + s.items, 0),
    calls: suites.reduce((a, s) => a + s.stats.calls, 0),
    failures: suites.reduce((a, s) => a + s.stats.failures, 0),
    input_tokens: suites.reduce((a, s) => a + s.stats.input_tokens, 0),
    output_tokens: suites.reduce((a, s) => a + s.stats.output_tokens, 0),
    cost: round(suites.reduce((a, s) => a + s.stats.cost, 0), 8),
    latency: { p50: pct(allLat, 50), p95: pct(allLat, 95), mean: allLat.length ? Math.round(allLat.reduce((a, b) => a + b, 0) / allLat.length) : 0, min: allLat[0] ?? 0, max: allLat[allLat.length - 1] ?? 0 },
  };
  totals.costPer1kItems = round((totals.cost / Math.max(1, totals.items)) * 1000, 4);

  const report = attachProse({
    generatedAt: new Date().toISOString(),
    endpoint: ENDPOINT,
    model: MODEL,
    servedModel,
    concurrency: CONCURRENCY,
    keySource: 'OPENROUTER_API_KEY',
    node: process.version,
    allowLocalFiles: ALLOW_LOCAL_FILES,
    crawlExcerptChars: CRAWL_EXCERPT_CHARS,
    localFilesSent: suites.flatMap((s) => s.localFilesSent ?? []),
    totals,
    suites,
  });
  await writeFile(jsonPath, JSON.stringify(report, null, 2) + '\n', 'utf8');
  await writeFile(mdPath, renderMarkdown(report), 'utf8');
  console.log(`\nwrote ${jsonPath}`);
  console.log(`wrote ${mdPath}`);
  console.log(`items ${totals.items} · p50 ${totals.latency.p50} ms · p95 ${totals.latency.p95} ms · cost $${totals.cost.toFixed(6)} · $${totals.costPer1kItems.toFixed(4)} per 1k items`);
  for (const s of suites) {
    const [, head] = Object.entries(s.metrics).find(([k]) => k !== 'baseline');
    console.log(`  ${s.name.padEnd(26)} ${pctS(head)}${s.metrics.baseline ? `   regex ${pctS(s.metrics.baseline)}` : ''}`);
  }
}

main().catch((err) => {
  console.error(String(err?.message ?? err));
  process.exit(1);
});
