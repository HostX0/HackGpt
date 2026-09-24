'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const vm = require('node:vm');

const reviewerScript = readFileSync(join(__dirname, '..', 'static', 'reviewer.js'), 'utf8');

function node(tagName = 'div') {
  return {
    tagName: tagName.toUpperCase(),
    className: '',
    textContent: '',
    children: [],
    append(...items) { this.children.push(...items); },
    insertBefore(item, before) {
      const index = before ? this.children.indexOf(before) : -1;
      if (index < 0) this.children.push(item);
      else this.children.splice(index, 0, item);
    },
    querySelector(selector) {
      if (selector === 'pre') return this.children.find((child) => child.tagName === 'PRE') || null;
      if (selector.startsWith('.')) {
        const className = selector.slice(1);
        return this.children.find((child) => String(child.className).split(/\s+/).includes(className)) || null;
      }
      return null;
    },
  };
}

function harness() {
  const coverage = node('pre');
  let cards = [];
  const document = {
    createElement(tag) { return node(tag); },
    getElementById(id) { return id === 'coverage-content' ? coverage : null; },
    querySelectorAll(selector) { return selector === '#findings .finding' ? cards : []; },
  };
  const context = vm.createContext({document, console});
  context.render = (report) => {
    cards = (report.findings || []).map((finding) => {
      const card = node('details');
      card.className = 'finding';
      const raw = node('pre');
      raw.textContent = JSON.stringify(finding.evidence, null, 2);
      card.append(raw);
      return card;
    });
    coverage.textContent = JSON.stringify({checks: report.checks || [], limitations: report.limitations || []}, null, 2);
  };
  vm.runInContext(reviewerScript, context);
  return {context, coverage};
}

function sampleReport() {
  return {
    findings: [],
    checks: [
      {tool: 'http_baseline', status: 'completed', result: 'observed_only'},
      {tool: 'native-web-headers', status: 'inconclusive', reason: 'Synthetic response was not comparable', coverage: {objects_tested: 2, objects_total: 3, notes: ['one route excluded']}},
      {tool: 'controlled_verification', status: 'skipped', reason: 'No approved external verification adapter'},
      {tool: 'scanner-x', status: 'error', reason: 'Synthetic parser failure'},
    ],
    limitations: ['Authentication coverage was not executed.', 'No findings is not a security guarantee.'],
  };
}

test('coverage review keeps every non-success state visible', () => {
  const h = harness();
  h.context.render(sampleReport());
  const text = h.coverage.textContent;
  assert.match(text, /4 checks · 1 completed · 1 inconclusive · 1 skipped · 1 error · 0 unknown/);
  assert.match(text, /http_baseline — COMPLETED · result observed only/);
  assert.match(text, /native-web-headers — INCONCLUSIVE/);
  assert.match(text, /coverage 2\/3/);
  assert.match(text, /notes one route excluded/);
  assert.match(text, /controlled_verification — SKIPPED/);
  assert.match(text, /scanner-x — ERROR/);
  assert.match(text, /completed means the check executed; it does not mean the target is safe/);
});

test('coverage review fails closed for missing or unknown status', () => {
  const h = harness();
  const text = h.context.reviewerCoverageText({checks: [{tool: 'alpha'}, {tool: 'beta', status: 'mystery'}], limitations: []});
  assert.match(text, /2 checks · 0 completed · 0 inconclusive · 0 skipped · 0 error · 2 unknown/);
  assert.match(text, /alpha — UNKNOWN/);
  assert.match(text, /beta — UNKNOWN/);
  assert.doesNotMatch(text, /alpha — COMPLETED/);
});

test('coverage review preserves the raw coverage record verbatim at the end', () => {
  const h = harness();
  const report = sampleReport();
  const expected = JSON.stringify({checks: report.checks, limitations: report.limitations}, null, 2);
  const text = h.context.reviewerCoverageText(report);
  assert.ok(text.endsWith(expected));
  assert.match(text, /Recorded limitations:/);
  assert.match(text, /Authentication coverage was not executed\./);
});

test('coverage review renders recorded strings as text and never uses innerHTML', () => {
  const h = harness();
  const malicious = '<img src=x onerror=alert(1)>';
  h.context.render({findings: [], checks: [{tool: malicious, status: 'skipped', reason: malicious}], limitations: [malicious]});
  assert.match(h.coverage.textContent, /<img src=x onerror=alert\(1\)>/);
  assert.doesNotMatch(reviewerScript, /\.innerHTML\s*=/);
});
