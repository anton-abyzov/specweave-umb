import { selectHistory } from "/srv/specwithcode/minisforum/worktrees/env-worktree-setting/apps/server/src/orchestration-v2/ContextHandoffBudget.ts";
const base = { threadId: "coord", runId: "r1", providerThreadId: "p1", status: "completed" } as any;
const msgs: any[] = [
  { ...base, role: "user", kind: "user_message", itemId: "first-user", text: "Original constraint: never push to main. " },
];
for (let i = 0; i < Number(process.env.N ?? 12); i++) msgs.push({ ...base, role: "assistant", kind: "subagent", itemId: `sub-${i}`,
  text: `Worker child:explore-${i}; origin provider_native; child thread unavailable; recorded status completed. Use studio_thread_read for current status and results; use studio_thread_list for its threadLink. Do not restart work from this historical record.` });
msgs.push({ ...base, role: "assistant", kind: "assistant_message", itemId: "latest-answer", text: "Partial answer: migration is half done, next step is T-04." });
msgs.push({ ...base, role: "user", kind: "user_message", itemId: "latest-user", text: "Continue." });
for (const budget of [4096, 16000, 32000]) {
  const s = selectHistory({ messages: msgs, coverage: "cov", budget });
  const ids = s.messages.map((m: any) => m.itemId);
  console.log(budget, "latest-answer:", ids.includes("latest-answer"), "first-user:", ids.includes("first-user"), "selected", ids.length);
}
