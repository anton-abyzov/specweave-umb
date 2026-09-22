import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';

const repo = fs.realpathSync(process.argv[2]);
const output = process.argv[3];
const candidate = process.argv.includes('--candidate');
const ts = createRequire(path.join(repo, 'package.json'))('typescript');
const relative = 'tests/unit/cli/slash-command-hints.test.ts';
const baseline = execFileSync('git', ['show', `59fd2c4d5:${relative}`], { cwd: repo, encoding: 'utf8' });
let current = fs.readFileSync(path.join(repo, relative), 'utf8');

if (candidate) {
  current = current.replace('function collectHits(): Hit[] {', 'const BARE_AT_START = bareRe(true);\nconst BARE_AFTER_INTERPOLATION = bareRe(false);\n\nfunction collectHits(): Hit[] {');
  const original = `      const line = source.getLineAndCharacterOfPosition(node.getStart(source)).line + 1;
      const rel = path.relative(REPO_ROOT, file);
      for (const m of text.matchAll(NAMESPACED)) hits.push({ token: \`/\${m[1]}\`, file: rel, line });
      for (const m of text.matchAll(bareRe(atStart))) hits.push({ token: \`/\${m[1] ?? m[2]}\`, file: rel, line });`;
  assert(current.includes(original));
  current = current.replace(original, `      if (!text.includes('/')) return;
      const matches = [
        ...text.matchAll(NAMESPACED),
        ...text.matchAll(atStart ? BARE_AT_START : BARE_AFTER_INTERPOLATION),
      ];
      if (matches.length === 0) return;
      const line = source.getLineAndCharacterOfPosition(node.getStart(source)).line + 1;
      const rel = path.relative(REPO_ROOT, file);
      for (const m of matches) hits.push({ token: \`/\${m[1] ?? m[2]}\`, file: rel, line });`);
}

const temporary = fs.mkdtempSync(path.join(os.tmpdir(), '0877-slash-equivalence-'));
fs.symlinkSync(fs.realpathSync(path.join(repo, 'node_modules')), path.join(temporary, 'node_modules'));
async function load(text, name) {
  text = text.slice(0, text.indexOf("describe('CLI output never names"));
  text = text.replace("import { describe, it, expect } from 'vitest';", '');
  text = text.replace(/const REPO_ROOT = [^\n]+;/, `const REPO_ROOT = ${JSON.stringify(repo)};`);
  text = text.replace('function collectHits(): Hit[] {', 'function collectHits(scanRoot: string = SRC): Hit[] {');
  text = text.replace('for (const file of walk(SRC))', 'for (const file of walk(scanRoot))');
  text = text.replace('const hits: Hit[] = [];', 'const hits: Hit[] = []; probeCounters.locationLookups = 0; probeCounters.literals = 0;');
  text = text.replace('const record = (node: ts.Node, text: string, atStart: boolean) => {', 'const record = (node: ts.Node, text: string, atStart: boolean) => { probeCounters.literals++;');
  text = text.replace('const line = source.getLineAndCharacterOfPosition', 'probeCounters.locationLookups++; const line = source.getLineAndCharacterOfPosition');
  text += '\nconst probeCounters = { literals: 0, locationLookups: 0 };\nexport { collectHits, walk, probeCounters };\n';
  const compiled = ts.transpileModule(text, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } }).outputText;
  const target = path.join(temporary, `${name}.mjs`);
  fs.writeFileSync(target, compiled);
  return import(pathToFileURL(target).href);
}

try {
  const old = await load(baseline, 'old');
  const next = await load(current, 'new');
  const fixtures = path.join(temporary, 'fixtures');
  fs.mkdirSync(fixtures);
  fs.writeFileSync(path.join(fixtures, 'escaped-and-nested.ts'), String.raw`
const ignored = ['/dead-input'];
console.log('\u002fsw:do', '\x2fsw:increment', '\u002fincrement');
console.log('prefix\n/do', '/increment /sw:do\n/sw:done\n /do');
console.log(logger.warn('/sw:done'), ['/sw:do'].map(x => x));
console.log('no command', 'https://example.test/path', '$5 /month');
function plain() { return '/dead-return'; }
function getInstructions() { return console.log('/sw:handoff'); }
const object = { customInstructions: () => console.warn('/sw:qa') };
console.log((() => { console.info('/sw:review'); return '/sw:sync'; })());
`);
  fs.writeFileSync(path.join(fixtures, 'templates.ts'), [
    'const variable = "x";',
    'console.log(`/sw:do ${variable}/resume\\n/increment ${variable}: /done`);',
    'console.warn(`\\u002fsw:increment ${variable}\\u002fsw:done`);',
    'function getInstructions() { return `plain ${logger.info("/sw:qa")} /sw:handoff`; }',
    'const instructions = () => "/sw:sync";',
    '',
  ].join('\n'));
  const oldFixture = old.collectHits(fixtures);
  const newFixture = next.collectHits(fixtures);
  assert.deepEqual(newFixture, oldFixture);
  assert(oldFixture.some(h => h.token === '/increment'));
  assert(oldFixture.some(h => h.token === '/sw:increment'));
  const escapedLine = oldFixture.filter(h => h.file.endsWith('escaped-and-nested.ts') && h.line === 3);
  assert.deepEqual(escapedLine.map(h => h.token), ['/sw:do', '/sw:increment', '/increment']);
  assert(oldFixture.filter(h => h.token === '/sw:qa').length >= 2);
  assert(!oldFixture.some(h => ['/dead-input', '/dead-return', '/resume'].includes(h.token)));

  const timings = { oldMs: [], newMs: [] };
  let reference;
  for (const order of [['old', old, 'new', next], ['new', next, 'old', old]]) {
    for (let i = 0; i < order.length; i += 2) {
      const name = order[i];
      const implementation = order[i + 1];
      global.gc?.();
      const start = performance.now();
      const hits = implementation.collectHits();
      timings[`${name}Ms`].push(performance.now() - start);
      if (!reference) reference = hits;
      else assert.deepEqual(hits, reference);
    }
  }
  const result = {
    baseline: '59fd2c4d5', candidate, node: process.version,
    sourceFiles: old.walk(path.join(repo, 'src')).length,
    orderedHits: reference.length,
    orderedHitsSha256: createHash('sha256').update(JSON.stringify(reference)).digest('hex'),
    fixtureHits: oldFixture.length, fixtureOrderedEquality: true,
    repositoryOrderedEquality: true, unchangedTraversal: true, timings,
    workCounters: { old: old.probeCounters, new: next.probeCounters },
  };
  if (output) fs.writeFileSync(output, JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result, null, 2));
} finally {
  fs.rmSync(temporary, { recursive: true, force: true });
}
