import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
const receipt = JSON.parse(readFileSync(new URL('./installed-routing-recovered-20261025.json', import.meta.url)));
const source = receipt.sourceItems.find(item => item.type === 'user_message');
const calls = receipt.sourceItems.filter(item => item.type === 'dynamic_tool');
assert.equal(calls.length, 2);
const destinations = new Set();
for (const item of calls) {
  assert.equal(item.textTruncated, false);
  const call = JSON.parse(item.text);
  const result = call.output.structuredContent;
  assert.equal(call.toolName, 'mcp__studio-code__studio_project_route');
  assert.equal(result.projectId, call.input.projectId);
  assert.equal(result.coordinatorThreadId, `project-coordinator:${result.projectId}`);
  assert.equal(result.coordinatorCreated, false);
  assert.equal(result.attachments, 1);
  assert.ok(result.grantedBy.startsWith('/Users/antonabyzov/Projects/'));
  const key = createHash('sha256').update(JSON.stringify([source.sourceThreadId, source.messageId, result.projectId])).digest('hex').slice(0, 32);
  assert.ok(result.messageId.startsWith(`coordinator-send:${result.projectId}:route:${key}:`));
  destinations.add(result.projectId);
}
assert.equal(destinations.size, 2);
for (const recipient of receipt.recipientItems ?? []) {
  const call = calls.map(item => JSON.parse(item.text)).find(call => call.output.structuredContent.messageId === recipient.messageId);
  assert.ok(call);
  assert.equal(recipient.sourceThreadId, call.output.structuredContent.coordinatorThreadId);
  assert.ok(recipient.text.includes(source.sourceThreadId));
  assert.ok(recipient.text.includes(source.messageId));
  assert.ok(recipient.text.includes(call.input.note));
  assert.equal(recipient.text.split("The text after this line is the user's own request.\n\n")[1], source.text.trim());
}
console.log(`PASS: ${calls.length} historical dispatches, ${receipt.recipientItems?.length ?? 0} recipient readbacks; deterministic route identities verified (no retry replay).`);
