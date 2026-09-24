'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const vm = require('node:vm');

const reviewerScript = readFileSync(join(__dirname, '..', 'static', 'reviewer.js'), 'utf8');

function harness() {
  const document = {
    getElementById() { return null; },
    querySelectorAll() { return []; },
    createElement() {
      return {
        className: '', textContent: '', children: [],
        append(...items) { this.children.push(...items); },
        insertBefore(item) { this.children.push(item); },
        querySelector() { return null; },
      };
    },
  };
  const context = vm.createContext({document, console, Date});
  context.render = () => {};
  context.loadHistory = async () => {};
  vm.runInContext(reviewerScript, context);
  return context;
}

test('retest history rejects malformed recorded timestamps instead of showing Invalid Date', () => {
  const context = harness();
  const text = context.reviewerRetestOptionText({
    started_at: 'definitely-not-a-date',
    target: 'lab://fixture',
    status: 'interrupted',
    verdict: 'inconclusive',
  });
  assert.match(text, /^time invalid · lab:\/\/fixture · INTERRUPTED · inconclusive$/);
  assert.doesNotMatch(text, /Invalid Date/);
});

test('retest history distinguishes missing time and missing target', () => {
  const context = harness();
  const text = context.reviewerRetestOptionText({
    status: 'cancelled',
    verdict: 'inconclusive',
  });
  assert.equal(text, 'time not recorded · target not recorded · CANCELLED · inconclusive');
});

test('retest history preserves recorded terminal state for a valid timestamp', () => {
  const context = harness();
  const text = context.reviewerRetestOptionText({
    started_at: '2026-09-24T12:30:00Z',
    target: 'lab://fixture',
    status: 'completed',
    verdict: 'observations_need_context',
  });
  assert.match(text, /lab:\/\/fixture · COMPLETED · observations need context$/);
  assert.doesNotMatch(text, /^time (?:invalid|not recorded)/);
});

test('durability classification stays conservative across modern and legacy reports', () => {
  const context = harness();
  assert.equal(context.reviewerDurabilityState({status: 'running'}), 'pending');
  assert.equal(context.reviewerDurabilityState({status: 'completed', durability: {status: 'durable'}}), 'durable');
  assert.equal(context.reviewerDurabilityState({status: 'completed', durability: {status: 'not_durable'}}), 'memory_only');
  assert.equal(context.reviewerDurabilityState({status: 'completed', durability: {status: 'mystery'}}), 'unknown');
  assert.equal(context.reviewerDurabilityState({status: 'completed'}), 'legacy');
});
