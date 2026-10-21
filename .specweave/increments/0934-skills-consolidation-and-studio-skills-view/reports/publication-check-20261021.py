import subprocess,urllib.parse,json,pathlib,hashlib,yaml,datetime,re
url='https://verified-skill.com/api/v1/skills/anton-abyzov/social-media-posting-skill/social-media-posting-skill'
def get(url):
    return json.loads(subprocess.check_output(['curl','--fail','--silent','--show-error','--max-time','45','--header','Cache-Control: no-cache',url],text=True))
base=pathlib.Path('/Users/antonabyzov/.agents');raw=(base/'skills/social-media-posting/SKILL.md').read_bytes();text=raw.decode();normalized=text.removeprefix('\ufeff').replace('\r\n','\n');meta=yaml.safe_load(text.split('---',2)[1]);lock=json.loads((base/'vskill.lock').read_text())['skills']['social-media-posting']
flat_description=re.sub(r'\s+', ' ',meta['description']).strip()
expected_description=flat_description if len(flat_description)<=500 else flat_description[:499].rstrip()+'…'
skill=get(url)['skill'];assert skill['currentVersion'] and skill['description']==expected_description;assert skill['description'].startswith('One skill for')
version=get(url+'/versions/'+urllib.parse.quote(skill['currentVersion'],safe=''))['version']
assert version['version']==skill['currentVersion']
assert isinstance(version['content'],str) and version['content'].encode()==raw
sha=hashlib.sha256(raw).hexdigest();assert version['contentHash']==sha
assert lock['sha']==hashlib.sha256(normalized.encode()).hexdigest()
assert version['gitSha']==lock['sourceCommitSha']
assert len(version['manifest'])==1
entry=next(x for x in version['manifest'] if x['path']=='SKILL.md');assert entry['sha256']==sha and entry['size']==len(raw)
assert version['treeHash']==hashlib.sha256(('SKILL.md\0'+normalized+'\n').encode()).hexdigest()
source_url='https://raw.githubusercontent.com/anton-abyzov/social-media-posting-skill/'+version['gitSha']+'/SKILL.md'
source_raw=subprocess.check_output(['curl','--fail','--silent','--show-error','--max-time','45',source_url])
assert source_raw==raw
print(json.dumps({'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'registryVersion':skill['currentVersion'],'sourceDeclaredVersion':meta.get('version'),'contentHash':sha,'sourceCommitSha':version['gitSha'],'manifestEntries':len(version['manifest']),'treeHash':version['treeHash'],'lockMatchesDisk':True,'descriptionMatchesPublishedContract':True,'descriptionCharacters':len(skill['description']),'contentBytes':len(raw)},indent=2))
