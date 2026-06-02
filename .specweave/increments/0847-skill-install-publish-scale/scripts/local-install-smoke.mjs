#!/usr/bin/env node
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const INCREMENT_DIR = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const ROOT = resolve(INCREMENT_DIR, "../../..");
const VSKILL_REPO = resolve(ROOT, "repositories/anton-abyzov/vskill");
const REPORT_PATH = resolve(INCREMENT_DIR, "reports/local-install-smoke.json");

const envFiles = [
  ".env",
  ".env.cloudflare",
  "repositories/anton-abyzov/vskill-platform/.env",
  "repositories/anton-abyzov/vskill-platform/.env.local",
  "repositories/anton-abyzov/vskill-platform/crawl-worker/.env",
  "repositories/anton-abyzov/vskill-platform/scanner-worker/.env",
].map((p) => resolve(ROOT, p));

const report = {
  generatedAt: new Date().toISOString(),
  ok: true,
  tempRoot: null,
  loadedEnvNames: [],
  package: {},
  steps: [],
  checks: [],
};

function unquote(value) {
  const trimmed = value.trim();
  if (
    (trimmed.startsWith("\"") && trimmed.endsWith("\"")) ||
    (trimmed.startsWith("'") && trimmed.endsWith("'"))
  ) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

function loadEnv() {
  const env = { ...process.env };
  const loaded = new Set();
  for (const file of envFiles) {
    if (!existsSync(file)) continue;
    for (const line of readFileSync(file, "utf8").split(/\r?\n/)) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const match = /^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/.exec(trimmed);
      if (!match) continue;
      const [, key, raw] = match;
      if (env[key] == null || env[key] === "") {
        env[key] = unquote(raw);
        loaded.add(key);
      }
    }
  }
  report.loadedEnvNames = [...loaded].sort();
  return env;
}

function redactionValues(env) {
  return Object.entries(env)
    .filter(([key, value]) =>
      value &&
      String(value).length >= 8 &&
      /(TOKEN|SECRET|PASSWORD|DATABASE|PRIVATE|PAT|KEY)/i.test(key)
    )
    .map(([key, value]) => [key, String(value)]);
}

function sanitize(text, redactors) {
  let out = String(text ?? "");
  for (const [key, value] of redactors) {
    out = out.split(value).join(`<redacted:${key}>`);
  }
  return out;
}

function tail(text, max = 4000) {
  const s = String(text ?? "");
  return s.length > max ? s.slice(s.length - max) : s;
}

function recordCheck(name, ok, details = {}) {
  report.checks.push({ name, ok, ...details });
  if (!ok) report.ok = false;
}

function runStep(name, command, args, opts) {
  const redactors = redactionValues(opts.env ?? process.env);
  const result = spawnSync(command, args, {
    cwd: opts.cwd,
    env: opts.env,
    encoding: "utf8",
    timeout: opts.timeoutMs ?? 120000,
    maxBuffer: 1024 * 1024 * 10,
  });
  const step = {
    name,
    command: sanitize([command, ...args].join(" "), redactors),
    cwd: opts.cwd,
    status: result.status,
    signal: result.signal,
    ok: result.status === (opts.expectedStatus ?? 0),
    stdoutTail: tail(sanitize(result.stdout, redactors)),
    stderrTail: tail(sanitize(result.stderr, redactors)),
  };
  report.steps.push(step);
  if (!step.ok) {
    report.ok = false;
    throw new Error(`${name} failed with status ${result.status}`);
  }
  return step;
}

function parseSkillMd(content, fallbackName) {
  const match = /^---\n([\s\S]*?)\n---\n?([\s\S]*)$/m.exec(content);
  const frontmatter = match?.[1] ?? "";
  const body = match?.[2] ?? content;
  const nameMatch = /^name:\s*["']?([^"'\n]+)["']?\s*$/m.exec(frontmatter);
  const descMatch = /^description:\s*["']?([^"'\n]+)["']?\s*$/m.exec(frontmatter);
  return {
    name: nameMatch?.[1]?.trim() || fallbackName,
    description: descMatch?.[1]?.trim() || body.trim().split(/\r?\n/).find(Boolean) || fallbackName,
    body,
    originalFrontmatter: frontmatter,
    files: {
      "agents/openai.yaml": "name: greet-anton\nsummary: Greeting skill smoke metadata\n",
      "references/smoke.md": "# Smoke reference\nThis verifies bundled resource export.\n",
    },
  };
}

async function main() {
  const baseEnv = loadEnv();
  const tempRoot = mkdtempSync(join(tmpdir(), "vskill-local-smoke-"));
  report.tempRoot = tempRoot;
  const packDir = join(tempRoot, "pack");
  const prefix = join(tempRoot, "npm-prefix");
  const home = join(tempRoot, "home");
  const publicProject = join(tempRoot, "public-project");
  const pluginProject = join(tempRoot, "plugin-project");
  const privateProject = join(tempRoot, "private-project");
  for (const dir of [packDir, prefix, home, publicProject, pluginProject, privateProject]) {
    mkdirSync(dir, { recursive: true });
  }

  runStep("npm-pack", "npm", ["pack", "--pack-destination", packDir], {
    cwd: VSKILL_REPO,
    env: baseEnv,
  });
  const tgz = readdirSync(packDir).find((name) => /^vskill-.*\.tgz$/.test(name));
  if (!tgz) throw new Error("npm pack did not produce a vskill tarball");
  const tarball = join(packDir, tgz);
  report.package.tarball = tgz;

  runStep("npm-install-local-prefix", "npm", ["install", "-g", "--prefix", prefix, tarball], {
    cwd: tempRoot,
    env: baseEnv,
  });
  const vskillBin = join(prefix, "bin", "vskill");
  const installedPackageRoot = join(prefix, "lib/node_modules/vskill");
  recordCheck("vskill-bin-exists", existsSync(vskillBin), { path: vskillBin });
  recordCheck("installed-package-exists", existsSync(installedPackageRoot), { path: installedPackageRoot });

  const smokeEnv = {
    ...baseEnv,
    HOME: home,
    PATH: `${join(prefix, "bin")}:${baseEnv.PATH ?? ""}`,
    CI: "1",
    NO_COLOR: "1",
  };

  runStep("vskill-version", vskillBin, ["--version"], {
    cwd: tempRoot,
    env: smokeEnv,
  });

  runStep(
    "public-github-install",
    vskillBin,
    [
      "install",
      "anthropics/skills/skill-creator",
      "--agent",
      "codex",
      "--cwd",
      "--copy",
      "--yes",
      "--force",
    ],
    { cwd: publicProject, env: smokeEnv, timeoutMs: 180000 },
  );
  recordCheck(
    "public-github-codex-skill-written",
    existsSync(join(publicProject, ".codex/skills/skill-creator/SKILL.md")),
  );

  const privateRepo = smokeEnv.VSKILL_TEST_PRIVATE_REPO;
  const privateSkill = smokeEnv.VSKILL_TEST_PRIVATE_SKILL || "greet-anton";
  if (privateRepo) {
    runStep(
      "private-github-install",
      vskillBin,
      [
        "install",
        `${privateRepo.replace(/^https:\/\/github\.com\//, "").replace(/\.git$/, "")}/${privateSkill}`,
        "--agent",
        "codex",
        "--cwd",
        "--copy",
        "--yes",
        "--force",
      ],
      { cwd: privateProject, env: smokeEnv, timeoutMs: 180000 },
    );
    recordCheck(
      "private-github-codex-skill-written",
      existsSync(join(privateProject, `.codex/skills/${privateSkill}/SKILL.md`)),
    );
  } else {
    report.checks.push({
      name: "private-github-install",
      ok: true,
      status: "skipped",
      reason: "VSKILL_TEST_PRIVATE_REPO not configured",
    });
  }

  runStep(
    "local-plugin-install",
    vskillBin,
    [
      "install",
      "--plugin-dir",
      VSKILL_REPO,
      "--plugin",
      "personal",
      "--only-skills",
      "obsidian-brain",
      "--agent",
      "codex",
      "--cwd",
      "--copy",
      "--yes",
      "--force",
      "--no-enable",
    ],
    { cwd: pluginProject, env: smokeEnv, timeoutMs: 180000 },
  );
  recordCheck(
    "local-plugin-codex-skill-written",
    existsSync(join(pluginProject, ".codex/skills/personal/obsidian-brain/SKILL.md")),
  );

  const { buildClipboardBlob } = await import(
    pathToFileURL(join(installedPackageRoot, "dist/installer/clipboard-export.js")).href
  );
  const sourceSkill = readFileSync(join(VSKILL_REPO, "skills/greet-anton/SKILL.md"), "utf8");
  const parsed = parseSkillMd(sourceSkill, "greet-anton");
  const blob = buildClipboardBlob(parsed, "chatgpt");
  recordCheck("chatgpt-export-includes-openai-metadata", blob.blob.includes("agents/openai.yaml"));
  recordCheck("chatgpt-export-includes-bundled-resource", blob.blob.includes("references/smoke.md"));
  recordCheck("chatgpt-export-has-paste-url", Boolean(blob.pasteInstructionsUrl));

  mkdirSync(dirname(REPORT_PATH), { recursive: true });
  writeFileSync(REPORT_PATH, JSON.stringify(report, null, 2) + "\n", { mode: 0o600 });
  if (!report.ok) process.exitCode = 1;
  console.log(`local install smoke ${report.ok ? "passed" : "failed"}`);
  console.log(`report: ${REPORT_PATH}`);
}

main().catch((err) => {
  report.ok = false;
  report.error = err instanceof Error ? err.message : String(err);
  mkdirSync(dirname(REPORT_PATH), { recursive: true });
  writeFileSync(REPORT_PATH, JSON.stringify(report, null, 2) + "\n", { mode: 0o600 });
  console.error(`local install smoke failed: ${report.error}`);
  console.error(`report: ${REPORT_PATH}`);
  process.exit(1);
});
