#!/usr/bin/env node
// Tiny static server for the /verify dashboard.
// Serves index.html, /api/verify-current.json (live file), and POST /api/run-all (spawns runner).

import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { spawn } from "node:child_process";
import { join, dirname, resolve, extname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const INCREMENT_DIR = resolve(__dirname, "..");
const REPO_ROOT = resolve(__dirname, "../../../..");

const RUN_VERIFY = join(INCREMENT_DIR, "scripts", "run-verify.mjs");
const AGENT_HANDLE = join(REPO_ROOT, ".specweave", "state", "verify-current.json");
const PORT = Number(process.env.PORT) || 5853;

const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json",
  ".css": "text/css; charset=utf-8",
};

function send(res, status, body, type = "text/plain") {
  res.writeHead(status, { "content-type": type, "cache-control": "no-store" });
  res.end(body);
}

const server = createServer(async (req, res) => {
  try {
    if (req.method === "GET" && (req.url === "/" || req.url === "/verify")) {
      const html = await readFile(join(__dirname, "index.html"));
      return send(res, 200, html, TYPES[".html"]);
    }

    if (req.method === "GET" && req.url === "/api/verify-current.json") {
      try {
        const body = await readFile(AGENT_HANDLE);
        return send(res, 200, body, TYPES[".json"]);
      } catch {
        return send(res, 200, JSON.stringify({ current: null }), TYPES[".json"]);
      }
    }

    if (req.method === "POST" && req.url === "/api/run-all") {
      const child = spawn(process.execPath, [RUN_VERIFY], {
        cwd: REPO_ROOT,
        env: { ...process.env, NO_COLOR: "1" },
      });
      let stderr = "";
      child.stderr.on("data", (b) => (stderr += b.toString()));
      child.stdout.on("data", () => {}); // drain
      child.on("close", async (code) => {
        try {
          const body = await readFile(AGENT_HANDLE, "utf8");
          const parsed = JSON.parse(body);
          send(res, 200, JSON.stringify(parsed.current ?? parsed), TYPES[".json"]);
        } catch (e) {
          send(res, 500, JSON.stringify({ error: e.message, exitCode: code, stderr }), TYPES[".json"]);
        }
      });
      return;
    }

    send(res, 404, `not found: ${req.url}`);
  } catch (err) {
    send(res, 500, `server error: ${err.message}`);
  }
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`verify dashboard → http://127.0.0.1:${PORT}/`);
  console.log(`  GET  /verify                  — dashboard UI`);
  console.log(`  GET  /api/verify-current.json — agent handle file`);
  console.log(`  POST /api/run-all             — trigger run-verify.mjs`);
});
