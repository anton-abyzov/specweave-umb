// Read-only source probes. Transpile actual TypeScript in memory; no requests or shell mutations.
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const ts = require('/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/node_modules/typescript');
const base = process.argv[2] || '/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0880-graphics';
const cache = new Map();
function load(rel) {
  const file = path.resolve(base, rel);
  if (cache.has(file)) return cache.get(file);
  let source = fs.readFileSync(file,'utf8');
  if (file.endsWith('/client.ts')) source += '\nexport { parseAnswers };\n';
  const output = ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
  const mod = {exports:{}};
  cache.set(file,mod.exports);
  const localRequire = (id) => {
    if (id.endsWith('/find-project-root.js')) return {resolveEffectiveRoot:()=>base};
    if (id === './usage.js') return {appendUsage:()=>{}};
    if (id.startsWith('.')) return load(path.relative(base,path.resolve(path.dirname(file),id.replace(/\.js$/,'.ts'))));
    return require(id);
  };
  vm.runInThisContext('(function(require,module,exports){'+output+'\n})',{filename:file})(localRequire,mod,mod.exports);
  return mod.exports;
}
(async()=>{
  const {prefilterCommand,guardCommand} = load('src/core/jev/decide.ts');
  const {JevClient,parseAnswers} = load('src/core/jev/client.ts');
  const {JEV_DEFAULTS} = load('src/core/jev/config.ts');
  const {redactSecrets} = load('src/core/jev/redact.ts');
  const findings = {};
  findings.prefilter = ['sort -o /tmp/important-file /tmp/input','uniq /tmp/input /tmp/important-file','git diff --output=/tmp/important-file','rg --pre /tmp/helper pattern /tmp/input'].map(command=>({command,result:prefilterCommand(command)}));
  const questions = {COMMAND_SCOPE:{type:'choice',instructions:'scope',criteria:{read_only:'Read',destructive_remote:'Destructive'}},COMMAND_DESTRUCTIVE:{type:'noul',instructions:'destructive?'}};
  const malformed = {answers:{COMMAND_SCOPE:{type:'choice',choice:'unexpected',confidence:5,probabilities:{}},COMMAND_DESTRUCTIVE:{type:'choice',choice:'no',confidence:1,probabilities:{no:1}}}};
  const answers = parseAnswers(malformed,questions);
  findings.malformedAccepted = answers;
  findings.malformedGuard = await guardCommand({config:JEV_DEFAULTS,ask:async()=>({answers,latencyMs:1,usage:{}})},{command:'rm -rf /tmp/fictional-audit-target'});
  const fakeToken = 'ghp_'+'A'.repeat(24);
  let sent;
  const client = new JevClient({...JEV_DEFAULTS,enabled:true},{apiKey:'not-a-real-key',usageLog:false,fetch:async(url,options)=>{sent=JSON.parse(options.body); return new Response(JSON.stringify({answers:{CHECK:{type:'noul',noul:1}},usage:{}}),{status:200});}});
  await client.ask({note:fakeToken},{CHECK:{type:'noul',instructions:'Check '+fakeToken}});
  findings.questionRedaction = {stateMasked:!JSON.stringify(sent.state).includes(fakeToken),questionMasked:!JSON.stringify(sent.questions).includes(fakeToken)};
  const fakePem = '-----BEGIN PRIVATE KEY-----\n'+'FAKE-KEY-MATERIAL-FOR-AUDIT'+'\n-----END PRIVATE KEY-----';
  findings.pemRedaction = redactSecrets(fakePem);
  console.log(JSON.stringify(findings,null,2));
})();
