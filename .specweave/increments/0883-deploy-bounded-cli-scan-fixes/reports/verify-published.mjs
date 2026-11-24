import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const [version, harness] = process.argv.slice(2);
assert.match(version || '', /^\d+\.\d+\.\d+$/);
assert.ok(harness && fs.existsSync(harness), 'Provide the bounded-scans.mjs path');
const workspace = fs.mkdtempSync(path.join(os.tmpdir(), '0883-registry-'));
const run = (command, args, options = {}) => execFileSync(command, args, {
  cwd: workspace, encoding: 'utf8', timeout: 120000,
  env: { ...process.env, PWDEBUG: '0', PLAYWRIGHT_HTML_OPEN: 'never' }, ...options,
});
const latest = run('npm', ['view', 'specweave', 'version']).trim();
assert.equal(latest, version, 'Expected release must be npm latest');
const dist = JSON.parse(run('npm', ['view', `specweave@${version}`, 'dist', '--json']));
const packed = JSON.parse(run('npm', ['pack', `specweave@${version}`, '--ignore-scripts', '--json']));
assert.equal(packed.length, 1);
const tarball = path.join(workspace, packed[0].filename);
const [algorithm, digest] = dist.integrity.split('-');
assert.equal(createHash(algorithm).update(fs.readFileSync(tarball)).digest('base64'), digest);
assert.equal(packed[0].integrity, dist.integrity);
const install = path.join(workspace, 'install');
run('npm', ['install', '--prefix', install, '--ignore-scripts', '--no-audit', '--no-fund', '--no-package-lock', tarball]);
const repo = path.join(install, 'node_modules/specweave');
const bin = path.join(repo, 'bin/specweave.js');
assert.equal(run(process.execPath, [bin, '--version']).trim(), version);
const proof = run(process.execPath, [path.resolve(harness)], {
  env: { ...process.env, SW_TEST_REPO: repo, PWDEBUG: '0', PLAYWRIGHT_HTML_OPEN: 'never' },
});
process.stdout.write(proof);
const bare = path.join(workspace, 'bare');
fs.mkdirSync(path.join(bare, '.specweave'), { recursive: true });
const refresh = [];
for (const args of [['refresh-plugins'], ['refresh-plugins', '--quiet']]) {
  const start = Date.now();
  const result = spawnSync(process.execPath, [bin, ...args], {
    cwd: bare, encoding: 'utf8', timeout: 5000,
    env: { ...process.env, PWDEBUG: '0', PLAYWRIGHT_HTML_OPEN: 'never' },
  });
  assert.ifError(result.error);
  assert.equal(result.status, 1, result.stdout + result.stderr);
  if (args.includes('--quiet')) assert.equal(result.stdout + result.stderr, '');
  else assert.match(result.stdout + result.stderr, /No SpecWeave project found/);
  refresh.push({ args, exit: result.status, elapsedMs: Date.now() - start });
}
const receipt = { version, latest, dist, installed: repo, refresh, boundedScans: 'PASS', checkedAt: new Date().toISOString() };
fs.writeFileSync(path.join(workspace, 'receipt.json'), JSON.stringify(receipt, null, 2) + '\n');
console.log(JSON.stringify(receipt, null, 2));
console.log(`REGISTRY VERIFICATION PASS: ${workspace}`);
