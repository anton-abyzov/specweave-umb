# Verify — 0934-skills-consolidation-and-studio-skills-view

PASS · 2026-10-21T17:55:11.152Z · commands from explicit

## Commands

### `cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/node_modules/vite-plus/bin/vp test run /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/server/src/project/projectSkillsInventory.test.ts /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/server/src/provider/Drivers/GrokSkills.test.ts /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/server/src/project/ProjectSkillsService.test.ts /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ProjectSkillsSettings.logic.test.ts /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ProjectSkillsSettings.test.tsx --maxWorkers=1 --no-file-parallelism` → exit 0 (59s)

```

 RUN  v5.0.1 /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio


 Test Files  5 passed (5)
      Tests  54 passed (54)
   Start at  13:53:57
   Duration  54.39s (transform 64%, import 24%, tests 6%, environment 5%, setup 1%)

  Transform  transforming modules took 34.00s · 64% of tracked time, re-done on every run
             persist transforms across runs with fsModuleCache: true
             learn more: https://vitest.dev/guide/improving-performance#caching-between-reruns
```

### `/usr/local/bin/python3 - <<'PY_CHECK'
import subprocess,re
p=subprocess.run(['/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node','/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/node_modules/tsx/dist/cli.mjs','/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/server/scripts/skills-attention-report.ts','/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave'],cwd='/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio',text=True,capture_output=True)
print(p.stdout);print(p.stderr)
assert p.returncode==0
assert '(error)' not in p.stdout and '(timeout)' not in p.stdout
assert re.search(r'^phantom 0$',p.stdout,re.M)
m=re.search(r'^attention (\d+)$',p.stdout,re.M);assert m and int(m.group(1))<=12
PY_CHECK` → exit 0 (11s)

```
   ok         memory-leak-debugging                 Grok                lock -        file -            
   ok         morning                               Grok                lock -        file -            
   ok         motion-graphics                       Claude,Codex,Grok   lock -        file -            
   ok         nanobanana                            Grok                lock -        file -            
   ok         obsidian-brain                        Claude,Codex,Grok   lock 1.1.0    file 1.1.0        
   ok         openai-docs                           Codex               lock -        file -            
   ok         paid-ads-experiments                  Codex               lock -        file -            
   ok         pdf                                   Grok                lock -        file -            
   ok         pdf:pdf                               Codex               lock -        file 26.1017.22135
   ok         postiz-marketing-pipeline             Claude,Codex,Grok   lock -        file 2.5.0        
   ok         postiz:postiz                         Codex               lock -        file 2.0.26       
   ok         pptx                                  Grok                lock -        file -            
   ok         pr-babysit                            Grok                lock -        file -            
   ok         precocity-invoicing                   Claude,Codex,Grok   lock -        file 1.2.0          aka anton-personal-skills:precocity-invoicing
   ok         presentations:Presentations           Codex               lock -        file 26.1017.22135
   ok         product-launch-video                  Claude,Codex,Grok   lock -        file -            
   ok         rea                                   Claude,Codex,Grok   lock 1.0.1    file 1.0.1        
   ok         remotion-best-practices               Claude,Codex,Grok   lock -        file 4.0.534      
   ok         resume-claude                         Grok                lock -        file -            
   ok         resume-codex                          Grok                lock -        file -            
   ok         resume-cursor                         Grok                lock -        file -            
   ok         resume-tuner                          Claude,Codex,Grok   lock -        file 1.1.0          aka anton-personal-skills:resume-tuner
   ok         reverse-engineer-anything             Claude,Codex,Grok   lock -        file 37           
   ok         review-agent                          Codex               lock -        file -            
   ok         scrollcraft-layout                    Claude,Codex,Grok   lock -        file -            
   ok         skill-creator                         Codex               lock -        file -            
   ok         skill-design-principles               Grok                lock -        file -            
   ok         skill-installer                       Codex               lock -        file -            
   ok         social-media-posting                  Claude,Codex,Grok   lock 1.3.1    file 1.3.1        
   ok         spreadsheets:excel-live-control       Codex               lock -        file 26.1017.22135
   ok         spreadsheets:Spreadsheets             Codex               lock -        file 26.1017.22135
   ok         statusline                            Grok                lock -        file -            
   ok         sw:auto                               Claude,Codex,Grok   lock -        file 3.1.2/3.1.4    aka auto
!  duplicate  sw:do                                 Claude,Codex,Grok   lock -        file 3.1.2/3.1.4    aka do  | Agents load 2 different versions of this skill: Claude, Grok 3.1.2; Codex 3.1.4.
   ok         sw:done                               Claude,Codex,Grok   lock -        file 3.1.2/3.1.4    aka done
!  duplicate  sw:handoff                            Claude,Codex,Grok   lock -        file 3.1.2/3.1.4    aka handoff  | Agents load 2 different versions of this skill: Claude, Grok 3.1.2; Codex 3.1.4.
   ok         sw:increment                          Claude,Codex,Grok   lock -        file 3.1.2/3.1.4    aka increment
   ok         sw:review                             Claude,Codex,Grok   lock -        file 3.1.2/3.1.4    aka review
   ok         tauri-desktop-release                 Claude,Codex,Grok   lock -        file 1.2.0        
   ok         tax-filing                            Claude,Codex,Grok   lock -        file 1.1.0        
   ok         template-creator:template-creator     Codex               lock -        file 26.1017.22135
   ok         threejs-frame-conventions             Grok                lock -        file -            
   ok         troubleshooting                       Grok                lock -        file -            
   ok         typesafe-ai                           Claude,Codex,Grok   lock -        file -            
   ok         unslop                                Claude,Codex,Grok   lock 1.0.0    file 1.0.0        
   ok         visualize:visualize                   Codex               lock -        file 1.0.50       
   ok         webapp-testing                        Claude,Codex,Grok   lock 1.0.0    file 1.0.0        
rows 116
phantom 0
attention 2
```

### `/usr/local/bin/python3 - <<'PY_CHECK'
import subprocess,json,pathlib
p=subprocess.run(['vskill','doctor','--json'],text=True,capture_output=True)
d=json.loads(p.stdout);print(json.dumps(d,indent=2));assert p.returncode in (0,1)
assert not [i for i in d['issues'] if i['kind'] in ('bad-name','bad-description','identical-copy')]
assert not pathlib.Path('/Users/antonabyzov/.claude/skills/.trash').exists()
h=pathlib.Path('/Users/antonabyzov'); root=h/'Projects/github/specweave-umb'
settings=json.loads((h/'.claude/settings.json').read_text())
for name in ('cowork-plugin-management:create-cowork-plugin','cowork-plugin-management:cowork-plugin-customizer','anthropic-skills:nanobanana','anthropic-skills:social-media-posting','anthropic-skills:remotion-best-practices'): assert settings['skillOverrides'][name]=='off'
for manifest in (h/'.claude/plugins/synced').glob('*/manifest.json'):
    d=json.loads(manifest.read_text()); plugins=d.get('plugins',{})
    names=list(plugins) if isinstance(plugins,dict) else [p['name'] for p in plugins]
    assert not ({'sw','marketing'} & set(names))
plugins=json.loads((h/'.claude/plugins/installed_plugins.json').read_text())['plugins']['sw@specweave']
relevant=[p for p in plugins if p['scope']=='user' or p.get('projectPath')==str(root)]
assert relevant
for p in relevant:
    assert tuple(map(int,p['version'].split('.'))) >= (3,0,23)
    assert pathlib.Path(p['installPath']).is_dir()
links=list((root/'.claude/skills').glob('sw-*')); assert links
for p in links: assert p.is_symlink() and p.resolve()==(root/'.agents/skills'/p.name).resolve()
for name in ('sw-brainstorm','sw-team'):
    for base in (root/'.agents/skills',root/'.claude/skills'): assert not (base/name).exists()
legacy=h/'vskill.lock'
if legacy.exists():
    skills=json.loads(legacy.read_text()).get('skills',{});assert 'resume-tailoring-skill' not in skills and 'social-media-posting-skill' not in skills
print('machine hygiene assertions passed')
PY_CHECK` → exit 0 (1s)

```
      "readers": [
        "kiro-cli"
      ]
    },
    {
      "scope": "project",
      "dir": "/Users/antonabyzov/Projects/github/specweave-umb/.pi/skills",
      "readers": [
        "pi"
      ]
    },
    {
      "scope": "project",
      "dir": "/Users/antonabyzov/Projects/github/specweave-umb/.trae/skills",
      "readers": [
        "trae"
      ]
    },
    {
      "scope": "project",
      "dir": "/Users/antonabyzov/Projects/github/specweave-umb/.windsurf/skills",
      "readers": [
        "windsurf"
      ]
    },
    {
      "scope": "project",
      "dir": "/Users/antonabyzov/Projects/github/specweave-umb/.aider/skills",
      "readers": [
        "aider"
      ]
    }
  ],
  "issues": [],
  "fixes": [],
  "summary": {
    "divergent": 0,
    "identical-copy": 0,
    "broken-link": 0,
    "redundant-link": 0,
    "migration-damage": 0,
    "name-mismatch": 0,
    "duplicate-name": 0,
    "bad-name": 0,
    "bad-description": 0,
    "lock-missing": 0
  },
  "remaining": 0
}
machine hygiene assertions passed
```

### `/usr/local/bin/python3 - <<'PY_CHECK'
import json,pathlib,hashlib
r=pathlib.Path('/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports');m=json.loads((r/'archive-scan-20261021-manifest.json').read_text());a=json.loads((r/'archive-scan-20261021-result.json').read_text());rest=json.loads((r/'archive-scan-20261021-restoration.json').read_text())
assert len(m['files'])==len(a['files'])==a['filesScanned']==158
assert len({x['path'] for x in m['files']})==len({x['realpath'] for x in m['files']})==158
assert sorted((x['path'],x['realpath'],x['bytes']) for x in m['files'])==sorted((x['path'],x['realpath'],x['bytes']) for x in a['files'])
assert not m['errors'] and not a['errors']
assert all(x['exitCode']==0 and not x['stderr'] and not x['parseErrors'] for x in a['files'])
assert sum(x['uncompressedBytes'] for x in a['files'])==a['uncompressedBytes']==6130100518
for name,c in a['candidates'].items():
    calls=[(x,y) for x in a['files'] for y in x['matches'] if name in y['candidates']]
    assert c['calls']==len(calls) and c['sessions']==len({x['realpath'] for x,y in calls})
used='hyperframes-creative hyperframes-studio asc-build-lifecycle asc-id-resolver asc-testflight-orchestration asc-screenshot-resize asc-whats-new-writer asc-apple-ads typesafe-ai reverse-engineer-anything jev-browser-use'.split()
removed='faceless-explainer music-to-video pr-to-video talking-head-recut embedded-captions slideshow figma remotion-to-hyperframes slack-messaging excalidraw-mcp competitors nanobanana'.split()
for name in used: assert (pathlib.Path('/Users/antonabyzov/.agents/skills')/name/'SKILL.md').is_file()
for name in removed:
    assert a['candidates'][name]['calls']==0
    for root in map(pathlib.Path,('/Users/antonabyzov/.agents/skills','/Users/antonabyzov/.claude/skills','/Users/antonabyzov/.codex/skills')): assert not (root/name).exists() and not (root/name).is_symlink()
for item in rest['files']:
    for base,field in ((rest['source'],'sourceSha256'),(rest['target'],'restoredSha256')):
        p=pathlib.Path(base)/item['relativePath'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item[field]
assert hashlib.sha256(pathlib.Path('/Users/antonabyzov/.agents/skills/asc-cli-usage/SKILL.md').read_bytes()).hexdigest()==rest['ascCliUsageUnchangedSha256']
acceptance=json.loads((r/'archive-scan-20261021-acceptance.json').read_text())
for name in acceptance['backupDirectoriesVerified']: assert (pathlib.Path(rest['source']).parent/name).is_dir()
print('158 archived receipts reconcile; 11 used skills present; 12 zero-use skills absent; all 13 backups preserved; restoration hash matches')
PY_CHECK` → exit 0 (0s)

```
158 archived receipts reconcile; 11 used skills present; 12 zero-use skills absent; all 13 backups preserved; restoration hash matches
```

### `/usr/local/bin/python3 - <<'PY_CHECK'
import subprocess,json
p=subprocess.run(['vskill','doctor','--json'],text=True,capture_output=True)
d=json.loads(p.stdout);print(json.dumps({'exitCode':p.returncode,'summary':d.get('summary'),'issues':d['issues']},indent=2))
assert p.returncode==0 and not d['issues']
PY_CHECK` → exit 0 (1s)

```
{
  "exitCode": 0,
  "summary": {
    "divergent": 0,
    "identical-copy": 0,
    "broken-link": 0,
    "redundant-link": 0,
    "migration-damage": 0,
    "name-mismatch": 0,
    "duplicate-name": 0,
    "bad-name": 0,
    "bad-description": 0,
    "lock-missing": 0
  },
  "issues": []
}
```

### `/usr/local/bin/python3 - <<'PY_CHECK'
import pathlib,json,hashlib,yaml
base=pathlib.Path('/Users/antonabyzov/.agents');lock=json.loads((base/'vskill.lock').read_text())['skills']
for name in ('social-media-posting','html-report','webapp-testing','unslop','obsidian-brain','rea','dcfc-inquiry-replies'):
    p=base/'skills'/name/'SKILL.md';raw=p.read_text(encoding='utf-8-sig').replace('\r\n','\n');sha=hashlib.sha256(raw.encode()).hexdigest()
    assert sha==lock[name]['sha'],name
    print(name,'lock hash matches disk')
for name in ('frontend-design','webapp-testing','unslop','jev-browser-use','motion-graphics','remotion-best-practices','asc-whats-new-writer'):
    text=(base/'skills'/name/'SKILL.md').read_text();meta=yaml.safe_load(text.split('---',2)[1]);assert 'use when' in meta['description'].lower(),name
html=yaml.safe_load((base/'skills/html-report/SKILL.md').read_text().split('---',2)[1]);assert 0<len(html['description'])<=1024
remotion=yaml.safe_load((base/'skills/remotion-best-practices/SKILL.md').read_text().split('---',2)[1]);assert len(remotion['description'])>30
assert lock['obsidian-brain']['pinnedVersion']=='1.1.0' and 'kie-gemini-omni' not in lock
print('seven retained trigger descriptions and D03 private-fork locks passed')
PY_CHECK` → exit 0 (0s)

```
social-media-posting lock hash matches disk
html-report lock hash matches disk
webapp-testing lock hash matches disk
unslop lock hash matches disk
obsidian-brain lock hash matches disk
rea lock hash matches disk
dcfc-inquiry-replies lock hash matches disk
seven retained trigger descriptions and D03 private-fork locks passed
```

### `/usr/local/bin/python3 - <<'PY_CHECK'
import subprocess,json
p=subprocess.run(['vskill','outdated','--json'],cwd='/Users/antonabyzov/.agents',text=True,capture_output=True)
data=json.loads(p.stdout);assert isinstance(data,list),data
updates=[r for r in data if r.get('updateAvailable')]
assert p.returncode==(1 if updates else 0),(p.returncode,p.stderr)
warnings=[r for r in data if r.get('warning')]
print(json.dumps({'entries':len(data),'exitCode':p.returncode,'updates':[r['name'] for r in updates],'warnings':warnings}));assert not warnings
PY_CHECK` → exit 0 (3s)

```
{"entries": 7, "exitCode": 1, "updates": ["cursor/plugins/unslop"], "warnings": []}
```

### `/usr/local/bin/python3 - <<'PY_CHECK'
import pathlib,re
p=pathlib.Path('/Users/antonabyzov/Projects/github/specweave-umb/AGENTS.md');text=p.read_text()
assert 'Available Subagent Types' not in text and p.stat().st_size<9000
block=text[:text.index('<!-- SW:END:jev -->')+len('<!-- SW:END:jev -->')]
assert len(block.encode())/4<=1200
jev=text.split('<!-- SW:SECTION:jev',1)[1].split('<!-- SW:END:jev -->',1)[0]
rows=[l for l in jev.splitlines() if l.startswith('|')][2:];assert len(rows)<=6
print('instruction bytes',p.stat().st_size,'procedure tokens by bytes/4',len(block.encode())/4,'Jev rows',len(rows))
PY_CHECK` → exit 0 (0s)

```
instruction bytes 8272 procedure tokens by bytes/4 1199.0 Jev rows 4
```

### `/usr/local/bin/python3 -B /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/hygiene-reconcile-20261021-check.py` → exit 0 (0s)

```
{"ok": true, "copiesPreserved": 3, "redundantLinksPreserved": 39, "canonicalSkillsUnchanged": 13, "installerLockUnchanged": true, "usedSkillsPresent": 11, "backupRoot": "/Users/antonabyzov/.specweave/recovery/0934-hygiene-20261021"}
```

### `/usr/local/bin/python3 /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/publication-check-20261021.py` → exit 0 (2s)

```
{
  "checkedAt": "2026-10-21T17:55:11.131505+00:00",
  "registryVersion": "1.2.3",
  "sourceDeclaredVersion": "1.3.1",
  "contentHash": "a3d5c75a015c5f12cee2037823dcf754b5e7c84bd6cb893508a23ab3b748bf97",
  "sourceCommitSha": "2b25fe6ebf3bcc6a477db02d2bb3f76fd1bab236",
  "manifestEntries": 1,
  "treeHash": "fca0012b4b0c3b9228b2b23d7f7007a7d3557647b77cb7dc301faa5e2c8270c5",
  "lockMatchesDisk": true,
  "descriptionMatchesPublishedContract": true,
  "descriptionCharacters": 499,
  "contentBytes": 21975
}
```

## Acceptance criteria

8/8 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | Studio joins presences by canonical file (realpath) before name, so apify-data-gathering, nanobanana and the 12 sw plugin skills each show as one row with the other providers' names as aliases; the phantom-row count on the specweave cwd is 0. |
| AC-02 | x (tasks) | Doctor findings count toward attention only when their agents or paths belong to a provider in the snapshot; Grok `userInvocable:false` keeps `enabled: true` with a `userInvocable` flag; entries under a dot-segment path (`/.trash/`, `/.root-owned-*`) and non-SKILL.md command files are dropped from provider catalogs; Studio's identical-copy rule and doctor's agree. |
| AC-03 | x (tasks) | The Skills table shows the SKILL.md version beside the lock version with a "lock out of date" hint when they differ, and for plugin presences the plugin manifest version per provider; "duplicate" with different versions reads "different versions"; Level is normalised by path (`*/plugins/cache/*` is Plugin) and Bundled and System have labels; legacy-lock entries with nothing on disk show as "stale lock entry" without attention. |
| AC-04 | x (tasks) | Running the repro script (`scratchpad/studio-skills-ui/repro.ts`, moved into the repo as a test fixture runner) on the specweave cwd reports at most 12 attention rows, all real. |
| AC-05 | x (tasks) | On this Mac the synced "sw", marketing and cowork-plugin-management org plugins and the three org skill copies are off, `~/.claude/skills/.trash` is outside the skills tree, the Claude sw plugin is 3.0.23, the umbrella `.claude/skills` entries are symlinks to `.agents/skills` with the retired sw-brainstorm and sw-team gone, the two legacy lock entries are removed, and `vskill doctor --json` reports no bad-name, bad-description or identical-copy finding. |
| AC-06 | x (tasks) | A 90-day Codex re-check (find -L over ~/.codex/sessions, including the external archive) is recorded per candidate; only candidates with zero Claude calls and zero Codex reads are removed; the removals, merges and deprecations from the merge map are applied, each merged skill's content is folded into its target with the target's trigger phrase extended, and `vskill doctor` is clean afterwards. |
| AC-07 | x (tasks) | The 14 user skills without a "Use when" trigger have one, remotion-best-practices has a real description, html-report's description is at most 1,024 characters; obsidian-brain, social-media-posting and every edited skill are republished through vSkill and relocked (lock sha equals disk); personal forks are relocked without republishing (D-03). |
| AC-08 | x (tasks) | Umbrella AGENTS.md has no "Available Subagent Types" section, the Jev table is at most 6 rows, and the SpecWeave procedure text is at most 1.2k tokens measured by `wc -c` divided by 4. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | https://github.com/anton-abyzov/specwithcode-dev/pull/431 a… |  |
| T-02 | done | claude@antons-macbook-m4max | https://github.com/anton-abyzov/specwithcode-dev/pull/431 a… |  |
| T-03 | done | claude@antons-macbook-m4max | https://github.com/anton-abyzov/specwithcode-dev/pull/431 a… |  |
| T-04 | done | claude@antons-macbook-m4max | vskill 1.2.10 doctor --json (umbrella root, October 20): is… |  |
| T-05 | done | cli@antons-macbook-m4max | reports/codex-90d.md + merge-map-applied.md: 13 zero-use ca… |  |
| T-06 | done | cli@antons-macbook-m4max | relock.md: personal forks obsidian-brain/kie-gemini-omni ke… |  |
| T-07 | done | claude@antons-macbook-m4max | AGENTS.md commit 596f2d788; test exit 0: no Subagent Types … |  |
| T-08 | done | codex-0934-archive | test -f /Users/antonabyzov/.agents/skills/asc-id-resolver/S… |  |
| T-09 | done | codex-0934-publication | Live resubmission sub_92092aad-2a4c-42d8-b186-8304f7c84397 … |  |
| T-10 | done | codex-0934-hygiene | vskill doctor --json \| jq -e '.issues \| length == 0' && /… |  |

10/10 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
