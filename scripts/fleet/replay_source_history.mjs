#!/usr/bin/env node
// Fixed offline validator. Evidence supplies data paths, never executable code.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {sourceHistoryBindings, verifySourceHistory} from './product_source_history.mjs';

assert.equal(Number(process.versions.node.split('.')[0]), 22, 'Node 22 required');
assert.equal(process.argv.length, 6, 'usage: replay_source_history.mjs plan native history source-record');
const [planBytes, nativeBytes, historyBytes, recordBytes] = process.argv.slice(2).map(p => readFileSync(p));
const plan = JSON.parse(planBytes), native = JSON.parse(nativeBytes);
const result = verifySourceHistory(plan, native, JSON.parse(historyBytes),
  sourceHistoryBindings(planBytes, nativeBytes), JSON.parse(recordBytes).bundle);
console.log(JSON.stringify({verified: true, projectId: plan.projectId,
  originalSuccessfulWorkerId: result.originalSuccessfulWorkerId,
  threadIds: result.threadIds, historicalOnlyThreadIds: result.historicalOnlyThreadIds}));
