#!/usr/bin/env node
// Offline validation only: validator module is fixed, never chosen by evidence.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {verifyReceipt} from './product_native_evidence.mjs';

assert.equal(Number(process.versions.node.split('.')[0]), 22, 'Node 22 required');
assert.equal(process.argv.length, 4, 'usage: replay_product_native.mjs plan.json receipt.json');
const plan = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const receipt = JSON.parse(readFileSync(process.argv[3], 'utf8'));
verifyReceipt(plan, receipt);
console.log(JSON.stringify({verified:true, mode:plan.mode, projectId:plan.projectId,
                           operationId:plan.operationId ?? null}));
