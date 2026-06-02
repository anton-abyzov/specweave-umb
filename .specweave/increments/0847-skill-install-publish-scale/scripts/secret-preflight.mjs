#!/usr/bin/env node
import { existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";

const ROOT = resolve(new URL("../../../../", import.meta.url).pathname);
const DEFAULT_REPORT = resolve(
  ROOT,
  ".specweave/increments/0847-skill-install-publish-scale/reports/secret-preflight.json",
);

const args = new Set(process.argv.slice(2));
const offline = args.has("--offline");
const json = args.has("--json");
const strict = args.has("--strict");
const writeReport = !args.has("--no-report");

const envFiles = [
  ".env",
  ".env.cloudflare",
  "repositories/anton-abyzov/vskill-platform/.env",
  "repositories/anton-abyzov/vskill-platform/.env.local",
  "repositories/anton-abyzov/vskill-platform/crawl-worker/.env",
  "repositories/anton-abyzov/vskill-platform/scanner-worker/.env",
].map((p) => resolve(ROOT, p));

const credentialNotes = [
  "/Users/antonabyzov/Projects/Obsidian/personal-docs/003 Resources/Technical Knowledge/Credentials-Secrets-Passwords/Projects/vskill github gh new tokens March 1 2026.md",
  "/Users/antonabyzov/Projects/Obsidian/personal-docs/003 Resources/Technical Knowledge/Credentials-Secrets-Passwords/Projects/Github OAuth Auth token vskill verified skill.md",
  "/Users/antonabyzov/Projects/Obsidian/personal-docs/003 Resources/Technical Knowledge/Credentials-Secrets-Passwords/EasyChamp/Skill Studio Desktop release credentials.md",
  "/Users/antonabyzov/Projects/Obsidian/personal-docs/003 Resources/Technical Knowledge/Credentials-Secrets-Passwords/NPM token npmjs npmjs.org password creds.md",
];

const requiredEnvNames = [
  "GITHUB_TOKEN",
  "GH_TOKEN",
  "VSKILL_TEST_GITHUB_PAT",
  "VSKILL_TEST_PRIVATE_GITHUB_PAT",
  "NPM_TOKEN",
  "CF_API_TOKEN_FULL_ACCESS",
];

function parseEnvFile(file) {
  if (!existsSync(file)) return {};
  const out = {};
  const raw = readFileSync(file, "utf8");
  for (const line of raw.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const match = /^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/.exec(trimmed);
    if (!match) continue;
    const [, key, value] = match;
    if (process.env[key] == null) {
      out[key] = unquote(value);
    }
  }
  return out;
}

function unquote(value) {
  const trimmed = value.trim();
  if (
    (trimmed.startsWith('"') && trimmed.endsWith('"')) ||
    (trimmed.startsWith("'") && trimmed.endsWith("'"))
  ) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

function loadLocalEnv() {
  const loaded = {};
  for (const file of envFiles) {
    const parsed = parseEnvFile(file);
    for (const [key, value] of Object.entries(parsed)) {
      if (process.env[key] == null) {
        process.env[key] = value;
        loaded[key] = file;
      }
    }
  }
  return loaded;
}

function tokenCandidate() {
  return (
    process.env.VSKILL_TEST_GITHUB_PAT ||
    process.env.VSKILL_TEST_PRIVATE_GITHUB_PAT ||
    process.env.GITHUB_TOKEN ||
    process.env.GH_TOKEN ||
    ""
  );
}

function repoFromEnv(name, fallback) {
  const value = process.env[name] || fallback;
  const cleaned = value
    .replace(/^https:\/\/github\.com\//, "")
    .replace(/\.git$/, "")
    .replace(/^\/+|\/+$/g, "");
  const [owner, repo] = cleaned.split("/");
  return owner && repo ? { owner, repo, full: `${owner}/${repo}` } : null;
}

async function githubJson(path, token) {
  const headers = {
    Accept: "application/vnd.github+json",
    "User-Agent": "vskill-secret-preflight",
    "X-GitHub-Api-Version": "2022-11-28",
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`https://api.github.com${path}`, {
    headers,
    signal: AbortSignal.timeout(10000),
  });
  let body = null;
  try {
    body = await res.json();
  } catch {
    body = null;
  }
  return {
    ok: res.ok,
    status: res.status,
    scopes: res.headers.get("x-oauth-scopes") || "",
    rateRemaining: res.headers.get("x-ratelimit-remaining") || "",
    body,
  };
}

function classifyRepoResponse(result) {
  if (result.ok) return "ok";
  if (result.status === 401 || result.status === 403) return "unauthorized";
  if (result.status === 404) return "missing-or-inaccessible";
  if (result.status === 429) return "rate-limited";
  return "transient-or-unknown";
}

async function checkRepo(label, repo, token) {
  if (!repo) {
    return { label, status: "skipped", reason: "repo-not-configured" };
  }
  const result = await githubJson(`/repos/${repo.owner}/${repo.repo}`, token);
  const permissions = result.body?.permissions && typeof result.body.permissions === "object"
    ? {
        admin: Boolean(result.body.permissions.admin),
        maintain: Boolean(result.body.permissions.maintain),
        push: Boolean(result.body.permissions.push),
        triage: Boolean(result.body.permissions.triage),
        pull: Boolean(result.body.permissions.pull),
      }
    : null;
  return {
    label,
    repo: repo.full,
    status: classifyRepoResponse(result),
    httpStatus: result.status,
    rateRemaining: result.rateRemaining || undefined,
    permissions,
  };
}

function classifyScopes(scopes) {
  if (!scopes) return { status: "unknown", scopes: [] };
  const parts = scopes
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)
    .sort();
  const risky = parts.filter((s) => /^(repo|workflow|admin:|write:|delete:)/.test(s));
  return {
    status: risky.length > 0 ? "review-required" : "least-privilege-looking",
    scopes: parts,
    riskyScopes: risky,
  };
}

async function main() {
  const loaded = loadLocalEnv();
  const presentEnv = requiredEnvNames
    .filter((name) => Boolean(process.env[name]))
    .sort();
  const missingEnv = requiredEnvNames
    .filter((name) => !process.env[name])
    .sort();

  const publicRepo = repoFromEnv("VSKILL_TEST_PUBLIC_REPO", "anton-abyzov/vskill-test-sandbox");
  const privateRepo = repoFromEnv("VSKILL_TEST_PRIVATE_REPO", "");
  const forbiddenRepo = repoFromEnv("VSKILL_TEST_FORBIDDEN_REPO", "octocat/Hello-World");
  const token = tokenCandidate();

  const summary = {
    ok: true,
    mode: offline ? "offline" : "online",
    generatedAt: new Date().toISOString(),
    envFiles: envFiles.map((file) => ({
      path: file,
      exists: existsSync(file),
      loadedKeys: Object.entries(loaded)
        .filter(([, source]) => source === file)
        .map(([key]) => key)
        .sort(),
    })),
    env: {
      present: presentEnv,
      missing: missingEnv,
      tokenCandidatePresent: Boolean(token),
    },
    obsidianCredentialNotes: credentialNotes.map((path) => ({
      path,
      exists: existsSync(path),
    })),
    github: {
      publicRepo: publicRepo?.full ?? null,
      privateRepo: privateRepo?.full ?? null,
      forbiddenRepo: forbiddenRepo?.full ?? null,
      checks: [],
      tokenScopes: { status: "skipped", scopes: [] },
    },
  };

  if (!offline && token) {
    const user = await githubJson("/user", token);
    summary.github.user = {
      status: classifyRepoResponse(user),
      httpStatus: user.status,
      loginPresent: Boolean(user.body?.login),
    };
    summary.github.tokenScopes = classifyScopes(user.scopes);
    summary.github.strict = strict;
    summary.github.checks.push(await checkRepo("public", publicRepo, token));
    summary.github.checks.push(await checkRepo("private", privateRepo, token));
    summary.github.checks.push(await checkRepo("forbidden", forbiddenRepo, token));

    const forbidden = summary.github.checks.find((c) => c.label === "forbidden");
    if (forbidden?.permissions?.push || forbidden?.permissions?.admin || forbidden?.permissions?.maintain) {
      summary.ok = false;
      summary.github.forbiddenAccessFailure =
        "Token has write-like permissions on the forbidden repo; use a narrower sandbox-scoped token.";
    }
    if (strict && summary.github.tokenScopes.status === "review-required") {
      summary.ok = false;
    }
  } else if (!offline && !token) {
    summary.github.checks.push({
      label: "github",
      status: "skipped",
      reason: "no-token-candidate-present",
    });
  }

  if (writeReport) {
    mkdirSync(dirname(DEFAULT_REPORT), { recursive: true });
    writeFileSync(DEFAULT_REPORT, JSON.stringify(summary, null, 2) + "\n", { mode: 0o600 });
  }

  if (json) {
    process.stdout.write(JSON.stringify(summary, null, 2) + "\n");
  } else {
    process.stdout.write(`Secret preflight ${summary.ok ? "passed" : "needs attention"} (${summary.mode})\n`);
    process.stdout.write(`Present env names: ${presentEnv.join(", ") || "none"}\n`);
    process.stdout.write(`Missing env names: ${missingEnv.join(", ") || "none"}\n`);
    process.stdout.write(`Report: ${DEFAULT_REPORT}\n`);
  }

  process.exit(summary.ok ? 0 : 2);
}

main().catch((err) => {
  const message = err instanceof Error ? err.message : String(err);
  process.stderr.write(`secret preflight failed: ${message.replace(/[A-Za-z0-9_=-]{24,}/g, "[redacted]")}\n`);
  process.exit(1);
});
