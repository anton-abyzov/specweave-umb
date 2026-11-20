import { selectHistory } from "/srv/specwithcode/minisforum/worktrees/env-worktree-setting/apps/server/src/orchestration-v2/ContextHandoffBudget.ts";
const base = { threadId: "coord", runId: "r1", providerThreadId: "p1", status: "completed" } as any;
const msgs: any[] = [
  { ...base, role: "user", kind: "user_message", itemId: "first-user", text: "Original constraint." },
  { ...base, role: "user", kind: "user_message", itemId: "latest-user", text: "Ship the migration." },
  { ...base, role: "assistant", kind: "assistant_message", itemId: "answer", text: "Plan: T-01 done, T-02 next. " + "x".repeat(400) },
];
for (let i = 0; i < 10; i++) msgs.push({ ...base, role: "assistant", kind: "dynamic_tool", itemId: `tool-${i}`,
  text: `Historical tool studio_thread_read; recorded status completed. Input and output are not replayed. Read this item with studio_thread_read and itemId to recover its receipt before claiming an action or repeating it.` });
const s = selectHistory({ messages: msgs, coverage: "cov", budget: 4096 });
console.log("answer kept:", s.messages.some((m: any) => m.itemId === "answer"), "selected", s.messages.map((m: any) => m.itemId).join(","));
