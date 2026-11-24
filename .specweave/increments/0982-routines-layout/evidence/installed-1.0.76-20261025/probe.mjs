// Read-only probe of the live M4 service with an orchestration:read + diagnostics:read token.
import { readFileSync } from "node:fs";
const { token, origin } = JSON.parse(readFileSync("/tmp/rl-pair.json", "utf8"));
const res = await fetch(`${origin}/api/auth/browser-session`, { method: "POST", headers: { Origin: origin, "Content-Type": "application/json" }, body: JSON.stringify({ credential: token }) });
console.log("session", res.status);
const cookie = (res.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
const t = await fetch(`${origin}/api/auth/websocket-ticket`, { method: "POST", headers: { Origin: origin, Cookie: cookie } });
console.log("ticket", t.status);
const ticket = (await t.json()).ticket;
const url = new URL(origin); url.protocol = "ws:"; url.pathname = "/ws"; url.searchParams.set("wsTicket", ticket); url.searchParams.set("orchestrationProtocol", "2");
const value = await new Promise((done, reject) => {
  const ws = new WebSocket(url); const timer = setTimeout(() => (ws.close(), reject(new Error("timeout"))), 20000);
  ws.addEventListener("open", () => ws.send(JSON.stringify({ _tag: "Request", id: "1", tag: "scheduledTasks.list", payload: {}, headers: [] })));
  ws.addEventListener("message", (e) => { for (const item of [JSON.parse(e.data)].flat()) if (item._tag === "Exit" && String(item.requestId) === "1") { clearTimeout(timer); ws.close(); item.exit?._tag === "Success" ? done(item.exit.value) : reject(new Error(JSON.stringify(item.exit).slice(0, 500))); } });
});
const tasks = Array.isArray(value) ? value : value.tasks ?? value.items ?? [];
console.log("keys", Array.isArray(value) ? "array" : Object.keys(value));
const byProject = {};
for (const t of tasks) { const k = t.projectId ?? "none"; (byProject[k] ??= []).push({ type: t.schedule?.type, enabled: t.enabled, last: t.lastRunStatus }); }
console.log("count", tasks.length, JSON.stringify(Object.fromEntries(Object.entries(byProject).map(([k, v]) => [k, { n: v.length, types: [...new Set(v.map((x) => x.type))], enabled: v.filter((x) => x.enabled).length }]))));
