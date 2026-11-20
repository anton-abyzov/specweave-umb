import { selectHistory, historyCost } from "/srv/specwithcode/minisforum/worktrees/env-worktree-setting/apps/server/src/orchestration-v2/ContextHandoffBudget.ts";
const base = { threadId: "coord", runId: "r1", providerThreadId: "p1", status: "completed" } as any;
const w = (i:number, kind:string, status:string, origin="app_owned") => ({ ...base, role:"assistant", kind, itemId:`${kind}-${i}`, text:`Worker w${i} ...`, worker:{key:`child-${i}`, origin, status}});
const msgs:any[] = [{...base, role:"user", kind:"user_message", itemId:"first-user", text:"Constraint: never push to main."}];
for (let i=0;i<12;i++){ msgs.push(w(i,"thread_created","created")); msgs.push(w(i,"subagent","running")); }
msgs.push({...base, role:"user", kind:"user_message", itemId:"mid-user", text:"Also: use Postgres not SQLite."});
for (let i=0;i<30;i++) msgs.push({...base, role:"assistant", kind:"dynamic_tool", itemId:`tool-${i}`, text:"Historical tool x"});
msgs.push({...base, role:"assistant", kind:"assistant_message", itemId:"latest-answer", text:"Answer."});
msgs.push({...base, role:"user", kind:"user_message", itemId:"latest-user", text:"Continue."});
for (const budget of [2048, 4096, 16000, 64000]) {
  const s = selectHistory({ messages: msgs, coverage:"cov", budget });
  const ids = s.messages.map((m:any)=>m.itemId);
  console.log(budget, "cost", historyCost(s.messages, s.context), "workers", ids.filter(x=>x.startsWith("subagent")).length, "launches", ids.filter(x=>x.startsWith("thread_created")).length, "tools", ids.filter(x=>x.startsWith("tool")).length, "mid-user", ids.includes("mid-user"), "anchors", ["first-user","latest-user","latest-answer"].every(x=>ids.includes(x)), "omitted", s.omittedItems);
}
const s = selectHistory({ messages: msgs, coverage:"cov", budget: 64000 }); console.log(s.context.split("\n").at(-1));
