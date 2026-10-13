#!/usr/bin/env node
// Fixed local replay; input files supply data, never executable validators.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {sha256} from './product_native_evidence.mjs';
import {verifySourceCheckpointAdvance} from './product_source_checkpoint.mjs';
assert.equal(Number(process.versions.node.split('.')[0]),22,'Node 22 required');
assert.ok([5,6].includes(process.argv.length),'usage: replay_source_checkpoint.mjs plan native advance [source-record]');
const bytes=process.argv.slice(2).map(p=>readFileSync(p));
const [plan,native,advance,record]=bytes.map(b=>JSON.parse(b));
const result=verifySourceCheckpointAdvance(plan,native,advance,{planSha256:sha256(bytes[0]),nativeSha256:sha256(bytes[1])},record?.bundle??null);
console.log(JSON.stringify({verified:true,projectId:plan.projectId,...result}));
