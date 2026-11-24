#!/usr/bin/env python3
"""Claude Code token usage scan. Read-only. Python 3.8+ stdlib only.

Usage: python3 usage_scan.py <machine-label> <out.json> [since YYYY-MM-DD]
Reads ~/.claude*/projects/**/*.jsonl and (through the bundled CLI only) the app's
projection tables. Never opens statev2.sqlite itself.
"""
import json, os, sys, glob, subprocess, collections, statistics, datetime, re

LABEL = sys.argv[1]
OUT = sys.argv[2]
SINCE = sys.argv[3] if len(sys.argv) > 3 else "2026-10-24"
HOME = os.path.expanduser("~")
W = dict(inp=1.0, read=0.1, w5=1.25, w1h=2.0, out=5.0)
SPIKE = 50000

def weighted(u):
    return u["inp"] * W["inp"] + u["read"] * W["read"] + u["w5"] * W["w5"] + u["w1h"] * W["w1h"] + u["out"] * W["out"]

def ts_parse(s):
    try:
        return datetime.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp()
    except Exception:
        return None

def local_day(t):
    # US Eastern standard time (UTC-5) in late November; fixed offset keeps machines comparable
    return datetime.datetime.utcfromtimestamp(t - 5 * 3600).strftime("%Y-%m-%d")

roots = []
for h in sorted(glob.glob(os.path.join(HOME, ".claude*"))):
    p = os.path.join(h, "projects")
    if os.path.isdir(p):
        roots.append(p)
for extra in glob.glob(os.path.join(HOME, ".specwithcode", "**", "claude*", "projects"), recursive=False):
    if os.path.isdir(extra):
        roots.append(extra)
files = []
for r in roots:
    for dp, dn, fn in os.walk(r):
        for f in fn:
            if f.endswith(".jsonl"):
                files.append(os.path.join(dp, f))

since_ts = ts_parse(SINCE + "T00:00:00") + 5 * 3600
seen_msg = {}
calls = []          # one per API response
events = []         # (ts, sid, kind, extra)
prompts = collections.Counter()
owners = {}
file_count = 0
for path in files:
    try:
        if os.path.getmtime(path) < since_ts:
            continue
    except OSError:
        continue
    file_count += 1
    sub = "/subagents/" in path or "/workflows/" in path
    fsid = os.path.basename(path)[:-6]
    cur_shape = None
    cur_owner = None
    pending = []    # flags to attach to next call in this file
    try:
        fh = open(path, "r", errors="replace")
    except OSError:
        continue
    with fh:
        for line in fh:
            if len(line) < 20:
                continue
            # cheap prefilter
            if '"type":"api-request-blob"' in line[:200]:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            t = d.get("type")
            if t == "attachment":
                a = d.get("attachment") or {}
                if a.get("type") == "deferred_tools_delta" and a.get("surfacedDefinitions"):
                    n = len(json.dumps(a.get("surfacedDefinitions")))
                    if n > 50000:
                        pending.append("surfaced")
                        events.append((ts_parse(d.get("timestamp", "")) or 0, d.get("sessionId") or fsid, "surfaced",
                                       {"chars": n, "names": len(a.get("surfacedNames") or []), "sub": bool(sub or d.get("isSidechain")),
                                        "noToolSearch": bool(a.get("toolSearchAbsent"))}))
            elif t == "session-owner":
                owners.setdefault(d.get("sessionId"), []).append((d.get("accountUuid") or "")[:8])
                pending.append("owner:" + (d.get("accountUuid") or "")[:8])
                cur_owner = (d.get("accountUuid") or "")[:8]
            elif t == "api-request":
                sh = d.get("shapeHash")
                if cur_shape is not None and sh != cur_shape:
                    pending.append("shape")
                cur_shape = sh
            elif t == "system":
                st = d.get("subtype")
                if st == "compact_boundary":
                    pending.append("compact")
                    cm = d.get("compactMetadata") or {}
                    events.append((ts_parse(d.get("timestamp", "")) or 0, d.get("sessionId"), "compact",
                                   {"trigger": cm.get("trigger"), "pre": cm.get("preTokens")}))
            elif t == "user":
                m = d.get("message") or {}
                c = m.get("content")
                txt = None
                if isinstance(c, str):
                    txt = c
                elif isinstance(c, list) and c and isinstance(c[0], dict) and c[0].get("type") == "text":
                    txt = c[0].get("text")
                if txt and not d.get("isMeta"):
                    tt = ts_parse(d.get("timestamp", "")) or 0
                    if tt >= since_ts:
                        head = re.sub(r"[0-9a-f]{8}-[0-9a-f-]{20,}", "<id>", txt.strip()[:60])
                        head = re.sub(r"\d+", "N", head)[:40]
                        prompts[(local_day(tt), "sub" if (sub or d.get("isSidechain")) else "main", head)] += 1
                        pending.append("prompt")
            elif t == "assistant":
                m = d.get("message") or {}
                u = m.get("usage")
                mid = m.get("id")
                if m.get("model") == "<synthetic>":
                    txt0 = json.dumps(m.get("content"))[:300]
                    if "thrashing" in txt0:
                        events.append((ts_parse(d.get("timestamp", "")) or 0, d.get("sessionId") or fsid, "thrash", {}))
                    continue
                if not u or not mid:
                    continue
                tt = ts_parse(d.get("timestamp", ""))
                if tt is None:
                    continue
                cc = u.get("cache_creation") or {}
                w1h = cc.get("ephemeral_1h_input_tokens") or 0
                w5 = cc.get("ephemeral_5m_input_tokens") or 0
                tot_cc = u.get("cache_creation_input_tokens") or 0
                if w1h + w5 == 0 and tot_cc:
                    w5 = tot_cc
                a_in = a_out = a_n = 0
                a_model = None
                for it in (u.get("iterations") or []):
                    if it.get("type") == "advisor_message":
                        a_n += 1
                        a_model = it.get("model")
                        a_in += (it.get("input_tokens") or 0) + (it.get("cache_creation_input_tokens") or 0) + 0.1 * (it.get("cache_read_input_tokens") or 0)
                        a_out += it.get("output_tokens") or 0
                rec = dict(acct=cur_owner, a_model=a_model, a_n=a_n, a_in=a_in, a_out=a_out, ts=tt, sid=d.get("sessionId") or fsid, file=fsid, sub=bool(sub or d.get("isSidechain")),
                           agent=d.get("agentId"), model=m.get("model"), req=d.get("requestedModel"),
                           effort=d.get("effort"), ttl=d.get("promptCacheRequested"), ver=d.get("version"),
                           ep=d.get("entrypoint"), cwd=d.get("cwd") or "", adv=d.get("advisorModel"),
                           inp=u.get("input_tokens") or 0, read=u.get("cache_read_input_tokens") or 0,
                           w5=w5, w1h=w1h, out=u.get("output_tokens") or 0,
                           iters=len(u.get("iterations") or []), flags=pending, path=path)
                pending = []
                key = mid
                old = seen_msg.get(key)
                if old is None:
                    seen_msg[key] = len(calls)
                    calls.append(rec)
                else:
                    o = calls[old]
                    if rec["out"] > o["out"]:
                        o["out"] = rec["out"]
                    if rec["a_n"] > o["a_n"]:
                        o["a_n"], o["a_in"], o["a_out"] = rec["a_n"], rec["a_in"], rec["a_out"]
                    o["flags"] = o["flags"] + rec["flags"]

calls = [c for c in calls if c["ts"] >= since_ts]
calls.sort(key=lambda c: c["ts"])

def proj(cwd):
    if "/.specwithcode/" in cwd:
        return "scratch/" + cwd.rstrip("/").split("/")[-1][:40]
    return "/".join(cwd.rstrip("/").split("/")[-2:])[:60]

def blank():
    return dict(calls=0, inp=0, read=0, w5=0, w1h=0, out=0, wt=0.0, adv_n=0, adv_in=0.0, adv_out=0, adv_wt=0.0)

def add(a, c):
    a["calls"] += 1
    for k in ("inp", "read", "w5", "w1h", "out"):
        a[k] += c[k]
    a["wt"] += weighted(c)
    a["adv_n"] += c["a_n"]; a["adv_in"] += c["a_in"]; a["adv_out"] += c["a_out"]
    a["adv_wt"] += c["a_in"] + 5.0 * c["a_out"]

# ---- per-stream (session + agent) sequencing for spike classification
streams = collections.defaultdict(list)
for c in calls:
    streams[(c["sid"], c["agent"] or ("sub:" + c["file"] if c["sub"] else ""))].append(c)

spikes = collections.defaultdict(lambda: dict(n=0, tok=0, wt=0.0))
spike_examples = []
first_ctx = collections.defaultdict(list)
for key, seq in streams.items():
    prev = None
    for i, c in enumerate(seq):
        ctx = c["inp"] + c["read"] + c["w5"] + c["w1h"]
        c["ctx"] = ctx
        write = c["w5"] + c["w1h"]
        cause = None
        gap = (c["ts"] - prev["ts"]) if prev else None
        c["gap"] = gap
        if i == 0:
            first_ctx[(local_day(c["ts"]), "sub" if c["sub"] else "main")].append(ctx)
        if write >= SPIKE:
            fl = c["flags"]
            ttl = 3600 if (prev and prev["ttl"] == "1h") else 300
            if "surfaced" in fl:
                cause = "tool_definitions_surfaced"
            elif prev is None:
                cause = "session_start_or_resume"
            elif any(f.startswith("owner:") for f in fl) and len(set(owners.get(c["sid"], []))) > 1:
                cause = "account_change"
            elif c["model"] != prev["model"]:
                cause = "model_change"
            elif "compact" in fl:
                cause = "post_compaction"
            elif gap is not None and gap > 3600:
                cause = "idle_over_1h"
            elif gap is not None and gap > ttl:
                cause = "idle_over_ttl_5m"
            elif c["ver"] != prev["ver"]:
                cause = "cli_version_change"
            elif "shape" in fl:
                cause = "request_shape_change"
            elif c["read"] > write:
                cause = "large_new_content"
            else:
                cause = "unexplained_miss"
            k = (local_day(c["ts"]), "sub" if c["sub"] else "main", cause)
            s = spikes[k]
            s["n"] += 1
            s["tok"] += write
            s["wt"] += c["w5"] * W["w5"] + c["w1h"] * W["w1h"]
            c["cause"] = cause
            if len(spike_examples) < 4000:
                spike_examples.append(dict(day=local_day(c["ts"]), sid=c["sid"][:8], sub=c["sub"], cause=cause,
                                           write=write, read=c["read"], gap=None if gap is None else int(gap),
                                           model=c["model"], prev=prev["model"] if prev else None, ttl=c["ttl"]))
        prev = c

# ---- aggregates
by_day_model = collections.defaultdict(blank)
by_day_effort = collections.defaultdict(blank)
by_day_proj = collections.defaultdict(blank)
by_day_ttl = collections.defaultdict(blank)
by_day_ep = collections.defaultdict(blank)
by_day_ver = collections.defaultdict(blank)
by_day_ctx = collections.defaultdict(blank)
by_day = collections.defaultdict(blank)
by_hour = collections.defaultdict(lambda: dict(wt=0.0, calls=0, sids=set()))
by_hour_acct = collections.defaultdict(lambda: dict(calls=0, wt=0.0, adv_wt=0.0, inp=0, read=0, w5=0, w1h=0, out=0, adv_in=0.0, adv_out=0))
adv_models = collections.Counter()
sess = {}
for c in calls:
    d = local_day(c["ts"])
    kind = "sub" if c["sub"] else "main"
    add(by_day[d], c)
    add(by_day_model[(d, c["model"], kind)], c)
    add(by_day_effort[(d, c["model"], str(c["effort"]), kind)], c)
    add(by_day_proj[(d, proj(c["cwd"]))], c)
    add(by_day_ttl[(d, kind, str(c["ttl"]))], c)
    add(by_day_ep[(d, str(c["ep"]))], c)
    add(by_day_ver[(d, str(c["ver"]))], c)
    ctx = c["ctx"]
    b = "<100K" if ctx < 100000 else "100-200K" if ctx < 200000 else "200-400K" if ctx < 400000 else "400K+"
    add(by_day_ctx[(d, kind, b)], c)
    fam = "fable" if "fable" in (c["model"] or "") else "opus" if "opus" in (c["model"] or "") else "other"
    hu = by_hour_acct[(datetime.datetime.utcfromtimestamp(c["ts"]).strftime("%Y-%m-%dT%H"), str(c["acct"]), fam)]
    hu["calls"] += 1; hu["wt"] += weighted(c)
    for k_ in ("inp", "read", "w5", "w1h", "out"):
        hu[k_] += c[k_]
    if c["a_n"]:
        afam = "fable" if "fable" in (c["a_model"] or "") else "opus" if "opus" in (c["a_model"] or "") else "other"
        ha = by_hour_acct[(datetime.datetime.utcfromtimestamp(c["ts"]).strftime("%Y-%m-%dT%H"), str(c["acct"]), "advisor:" + afam)]
        ha["calls"] += c["a_n"]; ha["adv_wt"] += c["a_in"] + 5.0 * c["a_out"]; ha["adv_in"] += c["a_in"]; ha["adv_out"] += c["a_out"]
        adv_models[(d, str(c["a_model"]), str(c["model"]))] += c["a_n"]
    h = datetime.datetime.utcfromtimestamp(c["ts"] - 5 * 3600).strftime("%Y-%m-%d %H")
    by_hour[h]["wt"] += weighted(c); by_hour[h]["calls"] += 1; by_hour[h]["sids"].add(c["sid"])
    s = sess.get(c["sid"])
    if s is None:
        s = sess[c["sid"]] = dict(sid=c["sid"], cwd=proj(c["cwd"]), first=c["ts"], last=c["ts"], models=collections.Counter(),
                                  efforts=collections.Counter(), main=blank(), sub=blank(), maxctx=0, days=collections.Counter(),
                                  model_changes=0, compactions=0, spikes=collections.Counter(), spike_tok=0, ep=c["ep"],
                                  subagents=set(), prompts=0, lastmodel=None, small_fat=0, adv=0)
    s["last"] = c["ts"]
    add(s[kind], c)
    s["models"][c["model"]] += 1
    s["efforts"][str(c["effort"])] += 1
    s["days"][d] += weighted(c)
    if not c["sub"]:
        s["maxctx"] = max(s["maxctx"], ctx)
        if s["lastmodel"] and s["lastmodel"] != c["model"]:
            s["model_changes"] += 1
        s["lastmodel"] = c["model"]
        if "compact" in c["flags"]:
            s["compactions"] += 1
        if "prompt" in c["flags"]:
            s["prompts"] += 1
            if ctx >= 200000:
                s["small_fat"] += 1
    else:
        s["subagents"].add(c["agent"] or c["file"])
    if c.get("cause"):
        s["spikes"][c["cause"]] += 1
        s["spike_tok"] += c["w5"] + c["w1h"]
    if c["iters"] > 1:
        s["adv"] += 1

# ---- app DB (through the CLI only)
CLI = None
for cand in ("/Applications/SpecWithCode.app/Contents/Resources/cli/specwithcode",
             os.path.join(HOME, "Applications/SpecWithCode.app/Contents/Resources/cli/specwithcode")):
    if os.path.exists(cand):
        CLI = cand
        break

def q(sql):
    if not CLI:
        return None
    try:
        r = subprocess.run([CLI, "db", "query", sql], capture_output=True, text=True, timeout=300)
        rows = []
        for l in r.stdout.splitlines():
            l = l.strip()
            if l.startswith("{"):
                try:
                    rows.append(json.loads(l))
                except Exception:
                    pass
        if r.returncode != 0 and not rows:
            return {"error": (r.stderr or r.stdout)[-400:]}
        return rows
    except Exception as e:
        return {"error": str(e)}

db = {}
db["cli_version"] = subprocess.run([CLI, "--version"], capture_output=True, text=True).stdout.strip() if CLI else None
native = q("SELECT json_extract(a.payload_json,'$.nativeThreadId') nid, a.thread_id tid, count(*) n "
           "FROM orchestration_v2_projection_run_attempts a WHERE a.provider_instance_id LIKE 'claude%' GROUP BY 1,2")
threads = q("SELECT thread_id tid, title, project_id pid, created_at, "
            "json_extract(payload_json,'$.creationSource') src, json_extract(payload_json,'$.createdBy') by, "
            "json_extract(payload_json,'$.lineage.parentThreadId') parent, "
            "json_extract(payload_json,'$.modelSelection.model') model FROM orchestration_v2_projection_threads")
tmap = {}
if isinstance(threads, list):
    tmap = {t["tid"]: t for t in threads}
nmap = {}
if isinstance(native, list):
    for r in native:
        if r.get("nid"):
            nmap[r["nid"]] = r["tid"]
db["threads_total"] = len(tmap)
db["runs_by_day"] = q("SELECT substr(requested_at,1,10) day, provider_instance_id pi, json_extract(payload_json,'$.modelSelection.model') model, "
                      "count(*) runs, count(distinct thread_id) threads FROM orchestration_v2_projection_runs "
                      "WHERE requested_at >= '%s' GROUP BY 1,2,3 ORDER BY 1,4 DESC" % SINCE)
db["threads_created_by_day"] = q("SELECT substr(created_at,1,10) day, default_provider prov, json_extract(payload_json,'$.creationSource') src, "
                                 "count(*) n FROM orchestration_v2_projection_threads WHERE created_at >= '%s' GROUP BY 1,2,3 ORDER BY 1" % SINCE)
db["model_switches_in_thread"] = q(
    "WITH r AS (SELECT thread_id, ordinal, requested_at, provider_instance_id pi, json_extract(payload_json,'$.modelSelection.model') model, "
    "LAG(json_extract(payload_json,'$.modelSelection.model')) OVER (PARTITION BY thread_id ORDER BY ordinal) pm, "
    "LAG(provider_instance_id) OVER (PARTITION BY thread_id ORDER BY ordinal) ppi FROM orchestration_v2_projection_runs) "
    "SELECT substr(requested_at,1,10) day, ppi || ':' || pm frm, pi || ':' || model too, count(*) n, count(distinct thread_id) threads "
    "FROM r WHERE pm IS NOT NULL AND (pm != model OR ppi != pi) AND requested_at >= '%s' GROUP BY 1,2,3 ORDER BY 1, 4 DESC" % SINCE)
db["handoffs_by_day"] = q("SELECT substr(updated_at,1,10) day, strategy, count(*) n FROM orchestration_v2_projection_context_handoffs "
                          "WHERE updated_at >= '%s' GROUP BY 1,2 ORDER BY 1" % SINCE)
db["transfers_by_day"] = q("SELECT substr(updated_at,1,10) day, type, source_provider sp, target_provider tp, count(*) n "
                           "FROM orchestration_v2_projection_context_transfers WHERE updated_at >= '%s' GROUP BY 1,2,3,4 ORDER BY 1" % SINCE)
db["provider_threads_per_thread"] = q("SELECT n, count(*) threads FROM (SELECT thread_id, count(*) n FROM orchestration_v2_projection_provider_threads "
                                      "WHERE driver='claudeAgent' GROUP BY 1) GROUP BY 1 ORDER BY 1")
db["subagents_by_day"] = q("SELECT substr(started_at,1,10) day, provider, origin, count(*) n FROM orchestration_v2_projection_subagents "
                           "WHERE started_at >= '%s' GROUP BY 1,2,3 ORDER BY 1" % SINCE)
db["compactions_by_day"] = q("SELECT substr(compacted_at,1,10) day, kind, count(*) n FROM orchestration_v2_thread_history_compactions GROUP BY 1,2 ORDER BY 1")
db["scheduled_tasks"] = q("SELECT count(*) n FROM scheduled_tasks")
db["scheduled_runs_by_day"] = q("SELECT substr(started_at,1,10) day, count(*) n FROM scheduled_task_run_receipts WHERE started_at >= '%s' GROUP BY 1 ORDER BY 1" % SINCE)
db["scheduled_runner_by_day"] = q("SELECT count(*) n FROM scheduled_task_runner_receipts")
db["turn_usage_by_day"] = q(
    "SELECT substr(started_at,1,10) day, count(*) turns, "
    "sum(json_extract(payload_json,'$.turnTokenUsage.cachedInputTokens')) cached, "
    "sum(json_extract(payload_json,'$.turnTokenUsage.cacheCreationTokens')) created, "
    "sum(json_extract(payload_json,'$.turnTokenUsage.inputTokens')) input, "
    "sum(json_extract(payload_json,'$.turnTokenUsage.outputTokens')) output, "
    "sum(CASE WHEN json_extract(payload_json,'$.tokenUsage.maxTokens') >= 1000000 THEN 1 ELSE 0 END) turns_1m "
    "FROM orchestration_v2_projection_provider_turns WHERE provider_turn_id LIKE 'provider-turn:provider:claude%%' AND started_at >= '%s' GROUP BY 1 ORDER BY 1" % SINCE)
db["limit_fallback_messages"] = q(
    "SELECT substr(created_at,1,10) day, substr(message_id,1,24) kind, count(*) n FROM orchestration_v2_projection_messages "
    "WHERE (message_id LIKE 'limit-%%' OR message_id LIKE '%%:limit-%%') AND created_at >= '%s' GROUP BY 1,2 ORDER BY 1" % SINCE)

# ---- session table
def dump_sess(s):
    tid = nmap.get(s["sid"])
    t = tmap.get(tid) if tid else None
    tot = blank()
    for k in tot:
        tot[k] = s["main"][k] + s["sub"][k]
    title = (t or {}).get("title") or ""
    cls = ("native" if not tid else "advisor" if title.startswith("Advisor") else "coordinator" if (tid or "").startswith("project-coordinator")
           else "review" if ("review" in title.lower()) else "worker_" + str((t or {}).get("src")))
    s["cls"] = cls
    denom = tot["read"] + tot["w5"] + tot["w1h"] + tot["inp"]
    return dict(sid=s["sid"][:8], cwd=s["cwd"], thread=(t or {}).get("title"), tid=(tid or "")[:60],
                src=(t or {}).get("src"), origin="app" if tid else "native", ep=s["ep"],
                first=local_day(s["first"]), last=local_day(s["last"]), hours=round((s["last"] - s["first"]) / 3600, 1),
                models=dict(s["models"]), efforts=dict(s["efforts"]),
                cls=cls, adv_n=tot["adv_n"], adv_wt=round(tot["adv_wt"]),
                wt=round(tot["wt"]), wt_sub=round(s["sub"]["wt"]), calls=tot["calls"], inp=tot["inp"], read=tot["read"],
                w5=tot["w5"], w1h=tot["w1h"], out=tot["out"], hit=round(tot["read"] / denom, 4) if denom else None,
                maxctx=s["maxctx"], model_changes=s["model_changes"], compactions=s["compactions"],
                spikes=dict(s["spikes"]), spike_tok=s["spike_tok"], subagents=len(s["subagents"]), prompts=s["prompts"],
                prompts_over_200k=s["small_fat"], multi_iter_calls=s["adv"],
                days={k: round(v) for k, v in s["days"].items()})

sessions = sorted((dump_sess(s) for s in sess.values()), key=lambda x: -x["wt"])

def rows(dd, names):
    out = []
    for k, v in sorted(dd.items()):
        r = dict(zip(names, k if isinstance(k, tuple) else (k,)))
        r.update({a: (round(b) if isinstance(b, float) else b) for a, b in v.items()})
        out.append(r)
    return out

def med(xs):
    return int(statistics.median(xs)) if xs else None

origin_day = collections.defaultdict(lambda: dict(wt=0, sessions=0))
class_day = collections.defaultdict(lambda: dict(wt=0, sessions=0))
for s in sessions:
    for d, w in s["days"].items():
        origin_day[(d, s["origin"])]["wt"] += w
        origin_day[(d, s["origin"])]["sessions"] += 1
        class_day[(d, s["cls"])]["wt"] += w
        class_day[(d, s["cls"])]["sessions"] += 1
sid_cls = {s_["sid"]: s_.get("cls") for s_ in sess.values()}
ev_day = collections.defaultdict(lambda: dict(n=0, chars=0, pre=0))
for (et, esid, ek, ex) in events:
    if et < since_ts:
        continue
    k2 = (local_day(et), ek, sid_cls.get(esid) or "?", str(ex.get("trigger") or ("sub" if ex.get("sub") else "")))
    ev_day[k2]["n"] += 1
    ev_day[k2]["chars"] += ex.get("chars") or 0
    ev_day[k2]["pre"] += ex.get("pre") or 0

hours = sorted(by_hour.items())
limit_history = None
for base in (os.environ.get("STUDIO_HOME"), os.path.join(HOME, ".specwithcode")):
    if not base:
        continue
    fp = os.path.join(base, "userdata", "usage-limit-history.json")
    if os.path.exists(fp):
        try:
            lh = json.load(open(fp))
            limit_history = [x for x in lh.get("series", []) if x.get("driver") == "claudeAgent"]
        except Exception as e:
            limit_history = {"error": str(e)}
        break
result = dict(
    machine=LABEL, generated=datetime.datetime.utcnow().isoformat() + "Z", since=SINCE, weights=W, roots=roots,
    files_scanned=file_count, calls=len(calls), sessions_n=len(sessions),
    accounts=sorted({a for v in owners.values() for a in v}),
    by_day=rows(by_day, ["day"]),
    by_day_model=rows(by_day_model, ["day", "model", "kind"]),
    by_day_effort=rows(by_day_effort, ["day", "model", "effort", "kind"]),
    by_day_project=rows(by_day_proj, ["day", "project"]),
    by_day_ttl=rows(by_day_ttl, ["day", "kind", "ttl"]),
    by_day_entrypoint=rows(by_day_ep, ["day", "entrypoint"]),
    by_day_version=rows(by_day_ver, ["day", "version"]),
    by_day_ctx_bucket=rows(by_day_ctx, ["day", "kind", "bucket"]),
    by_day_class=[dict(day=k[0], cls=k[1], **v) for k, v in sorted(class_day.items())],
    events_by_day=[dict(day=k[0], event=k[1], cls=k[2], detail=k[3], **v) for k, v in sorted(ev_day.items())],
    hourly_utc_account=[dict(hour=k[0], acct=k[1], fam=k[2], **{a: (round(b) if isinstance(b, float) else b) for a, b in v.items()})
                        for k, v in sorted(by_hour_acct.items())],
    advisor_models=[dict(day=k[0], advisor=k[1], caller=k[2], n=n) for k, n in sorted(adv_models.items())],
    limit_history=limit_history,
    by_day_origin=[dict(day=k[0], origin=k[1], **v) for k, v in sorted(origin_day.items())],
    spikes=[dict(day=k[0], kind=k[1], cause=k[2], n=v["n"], tok=v["tok"], wt=round(v["wt"])) for k, v in sorted(spikes.items())],
    spike_examples=sorted(spike_examples, key=lambda x: -x["write"])[:150],
    first_call_ctx=[dict(day=k[0], kind=k[1], n=len(v), median=med(v), p90=int(sorted(v)[int(len(v) * 0.9) - 1]) if len(v) >= 10 else None)
                    for k, v in sorted(first_ctx.items())],
    hourly=[dict(hour=h, wt=round(v["wt"]), calls=v["calls"], sessions=len(v["sids"])) for h, v in hours],
    prompts_top=[dict(day=k[0], kind=k[1], head=k[2], n=n) for k, n in prompts.most_common(400)],
    sessions=sessions[:1500],
    sessions_tail_wt=sum(s["wt"] for s in sessions[1500:]),
    db=db,
)
with open(OUT, "w") as f:
    json.dump(result, f)
tot = blank()
for r in result["by_day"]:
    for k in tot:
        tot[k] += r[k]
print(json.dumps(dict(machine=LABEL, files=file_count, calls=len(calls), sessions=len(sessions), total=tot,
                      out=OUT, bytes=os.path.getsize(OUT))))
