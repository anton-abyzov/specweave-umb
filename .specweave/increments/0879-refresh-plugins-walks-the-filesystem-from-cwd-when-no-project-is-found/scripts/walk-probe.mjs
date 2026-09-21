// Emulates walkForFile from src/utils/cleanup-stale-plugins.ts (statSync follows symlinks)
import * as fs from 'fs';
import path from 'path';
const SKIP = new Set(['node_modules', '.git', '.specweave']);
const root = process.argv[2];
const limitMs = Number(process.argv[3] || 10000);
const t0 = Date.now();
let dirs = 0, escaped = 0, maxDepth = 0;
const realRoot = fs.realpathSync(root);
function walk(dir, depth) {
  if (Date.now() - t0 > limitMs) throw new Error('TIMEOUT');
  let names; try { names = fs.readdirSync(dir); } catch { return; }
  for (const name of names) {
    if (SKIP.has(name)) continue;
    const full = path.join(dir, name);
    let st; try { st = fs.statSync(full); } catch { continue; }
    if (st.isDirectory()) {
      dirs++; if (depth > maxDepth) maxDepth = depth;
      try { const rp = fs.realpathSync(full); if (!rp.startsWith(realRoot + path.sep)) escaped++; } catch {}
      walk(full, depth + 1);
    }
  }
}
try { walk(root, 1); console.log(JSON.stringify({ finished: true, ms: Date.now() - t0, dirs, escaped, maxDepth })); }
catch (e) { console.log(JSON.stringify({ finished: false, reason: e.message, ms: Date.now() - t0, dirs, escaped, maxDepth })); }
