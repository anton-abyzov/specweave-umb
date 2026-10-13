// Offline persisted-envelope regressions. No Studio, Google, auth or provider calls.
import assert from "node:assert/strict";
import test from "node:test";
import { bindDispatchReceipt, nativeTurn, summarizeTool, toolName } from "./aide-google-live.mjs";

const config = { phase: "native", projectId: "project", commandId: "command", expectedVersion: "1.0.8", expectedSource: "a".repeat(40), origin: "http://127.0.0.1:8319", baseDir: "/synthetic" };
const threadId = "thread";
const workspace = { settings: { coordinatorThreadId: threadId } };
const time = (second) => `2026-10-13T06:00:${String(second).padStart(2, "0")}.000Z`;
const tools = ["studio_google_status", "studio_google_gmail_search", "studio_google_calendar_events", "studio_google_drive_search"];
const inputs = [{ checkConnection: true }, { query: "newer_than:30d", maxResults: 1 }, { timeMin: "2026-10-01T00:00:00-04:00", timeMax: "2026-11-01T00:00:00-04:00", maxResults: 1 }, { maxResults: 1 }];
const outputs = [{ connectionState: "verified", checkedAt: time(1), serviceChecks: ["gmail", "calendar", "drive"].map((service) => ({ service, status: "ok" })) }, { messages: [{ subject: "PRIVATE_SENTINEL" }] }, { events: [{ summary: "PRIVATE_SENTINEL" }] }, { files: [{ name: "PRIVATE_SENTINEL" }] }];
const items = () => tools.map((tool, index) => ({ id: `item-${index}`, type: "dynamic_tool", runId: "run", ordinal: index, status: "completed", startedAt: time(index * 2), completedAt: time(index * 2 + 1), toolName: `studio-code.${tool}`, input: inputs[index], output: index % 2 ? [{ type: "text", text: JSON.stringify(outputs[index]) }] : outputs[index] }));
const run = { id: "run", userMessageId: "coordinator-send:project:command", status: "completed", completedAt: time(9) };

async function execute({ rows = items(), existing = false, nextConfig = config } = {}) {
  let reads = 0, sends = 0;
  const rpc = { async call(tag) {
    if (tag === "projects.coordinatorSend") { sends++; return { threadId, created: false }; }
    assert.equal(tag, "orchestration.getThreadProjection");
    return { thread: { id: threadId, projectId: config.projectId }, runs: existing || reads++ > 0 ? [run] : [], turnItems: rows };
  } };
  const receipt = {};
  await nativeTurn(nextConfig, rpc, workspace, receipt, () => {});
  return { receipt, sends };
}

test("accepts exact Studio Codex/Claude names and rejects another MCP server", () => {
  for (const name of tools) {
    for (const qualified of [name, `studio-code.${name}`, `mcp__studio-code__${name}`]) assert.equal(toolName({ type: "dynamic_tool", toolName: qualified }), name);
    for (const foreign of [`other.${name}`, `mcp__other__${name}`, `fake__${name}`]) assert.equal(toolName({ type: "dynamic_tool", toolName: foreign }), null);
  }
});

test("actual Codex structured/text-array envelopes prove four bounded reads without content", async () => {
  const { receipt, sends } = await execute();
  assert.equal(sends, 1);
  assert.equal(receipt.native.success, true);
  assert.equal(receipt.native.healthBeforeReads, true);
  assert.equal(receipt.native.dispatchBoundToSource, true);
  assert.equal(receipt.native.additionalNativeTools, 0);
  assert.equal(JSON.stringify(receipt).includes("PRIVATE_SENTINEL"), false);
});

for (const type of ["command_execution", "file_change", "file_search", "web_search", "todo_list", "secret_request"]) {
  test(`rejects extra native ${type}`, async () => {
    const { receipt } = await execute({ rows: [...items(), { id: "extra", runId: "run", type }] });
    assert.equal(receipt.native.additionalNativeTools, 1);
    assert.equal(receipt.native.success, false);
  });
}

test("rejects health started after reads or unfinished when reads began", async () => {
  for (const change of [{ ordinal: 8 }, { output: { ...outputs[0], checkedAt: time(8) } }]) {
    const rows = items(); Object.assign(rows[0], change);
    const { receipt } = await execute({ rows });
    assert.equal(receipt.native.healthBeforeReads, false);
    assert.equal(receipt.native.success, false);
  }
});

test("delayed completion ingestion and same-thread context handoff are not extra operations", async () => {
  const rows = items(); rows[0].completedAt = time(8);
  rows.push({ id: "context", runId: "run", type: "handoff" });
  const { receipt } = await execute({ rows });
  assert.equal(receipt.native.healthBeforeReads, true);
  assert.equal(receipt.native.delegationItems, 0);
  assert.equal(receipt.native.success, true);
});

test("cannot relabel an existing older run with the current runtime source", async () => {
  await assert.rejects(execute({ existing: true }), /existing_run_requires_original_dispatch_receipt/);
});

function dispatch() {
  return { phase: "native", nativeTurnsRequested: 1, serverVersion: config.expectedVersion, serverSourceCommit: config.expectedSource, origin: config.origin, baseDir: config.baseDir, projectId: config.projectId, native: { commandId: config.commandId, threadId, dispatchAttemptedAt: time(0), runId: "run", resumedReceipt: false, dispatchBoundToSource: true }, cleanup: { ownedSessionRevoked: true, existingActiveSessionsPreserved: true } };
}

test("inspect recovers the same bound dispatch without sending another turn", async () => {
  const prior = dispatch();
  const binding = bindDispatchReceipt(config, prior, JSON.stringify(prior));
  const { receipt, sends } = await execute({ existing: true, nextConfig: { ...config, phase: "inspect", dispatchBinding: binding } });
  assert.equal(sends, 0);
  assert.equal(receipt.native.success, true);
  assert.equal(binding.sha256.length, 64);
});

test("rejects a dispatch from another source or command and missing cleanup", () => {
  for (const mutate of [p => p.serverSourceCommit = "b".repeat(40), p => p.native.commandId = "other", p => p.cleanup.ownedSessionRevoked = false]) {
    const prior = dispatch(); mutate(prior);
    assert.throws(() => bindDispatchReceipt(config, prior, JSON.stringify(prior)), /dispatch_receipt_binding_invalid/);
  }
});

test("bound resume cannot dispatch if the prior run is missing", async () => {
  const prior = dispatch();
  await assert.rejects(execute({ nextConfig: { ...config, dispatchBinding: bindDispatchReceipt(config, prior, JSON.stringify(prior)) } }), /dispatch_receipt_run_mismatch/);
});

test("provider error envelopes cannot hide a successful-looking collection", () => {
  const row = items()[1]; row.output = { error: "PRIVATE_SENTINEL", result: outputs[1] };
  assert.equal(summarizeTool(row, tools[1]).success, false);
});

test("provider failure receipt excludes free-text private diagnostics", async () => {
  const { receipt } = await execute({ rows: [...items(), { id: "error", runId: "run", type: "error", failure: { class: "provider_error", message: "PRIVATE_SENTINEL", code: "PRIVATE_SENTINEL" } }] });
  assert.equal(receipt.native.success, false);
  assert.equal(JSON.stringify(receipt).includes("PRIVATE_SENTINEL"), false);
});
