'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const vm = require('node:vm');

const root = join(__dirname, '..', 'static');
const reviewerScript = readFileSync(join(root, 'reviewer.js'), 'utf8');
const html = readFileSync(join(root, 'index.html'), 'utf8');

function domNode(tagName = 'div') {
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
  let cards = [];
  const document = {
    createElement(tag) { return domNode(tag); },
    querySelectorAll(selector) { return selector === '#findings .finding' ? cards : []; },
  };
  const context = vm.createContext({document, console});
  context.render = (report) => {
    cards = report.findings.map((finding) => {
      const card = domNode('details');
      card.className = 'finding';
      const raw = domNode('pre');
      raw.textContent = JSON.stringify(finding.evidence, null, 2);
      const hash = domNode('p');
      hash.textContent = 'Evidence SHA-256: ' + finding.evidence_sha256;
      card.append(raw, hash);
      return card;
    });
  };
  vm.runInContext(reviewerScript, context);
  return {context, cards: () => cards};
}

function factMap(context, finding) {
  return Object.fromEntries(JSON.parse(JSON.stringify(context.reviewerEvidenceFacts(finding))));
}

test('page loads reviewer evidence assets after the core application', () => {
  assert.match(html, /href="\/reviewer\.css"/);
  assert.match(html, /<script src="\/app\.js" defer><\/script><script src="\/reviewer\.js" defer><\/script>/);
});

test('reviewer facts expose recorded provenance without inventing missing fields', () => {
  const {context} = harness();
  const facts = factMap(context, {
    source: 'adapter/native-web-headers/1',
    rule: 'header/content-security-policy',
    verification: 'candidate',
    confidence: 0.875,
    external_id: 'finding-7',
    observed_at: '2026-09-24T07:30:00+00:00',
    evidence_sha256: 'a'.repeat(64),
    evidence: {method: 'HEAD', http_status: 200, scope: 'this response only', absent_header: 'content-security-policy'},
  });
  assert.equal(facts.Source, 'adapter/native-web-headers/1');
  assert.equal(facts.Rule, 'header/content-security-policy');
  assert.equal(facts.Verification, 'candidate');
  assert.equal(facts.Confidence, '87.5%');
  assert.equal(facts['External ID'], 'finding-7');
  assert.equal(facts.Method, 'HEAD');
  assert.equal(facts['HTTP status'], '200');
  assert.equal(facts['Scope note'], 'this response only');
  assert.equal(facts['Absent header'], 'content-security-policy');
  assert.equal(facts['Evidence SHA-256'], 'a'.repeat(64));
});

test('synthetic proof safety context is visible while raw evidence stays unchanged', () => {
  const h = harness();
  const evidence = {
    environment: 'ephemeral synthetic loopback lab',
    demonstrated_impact: 'unauthenticated read of designated synthetic records',
    control_status: 401,
    record_status: 200,
    credentials_sent: false,
    customer_data_sampled: false,
    body_sha256: 'b'.repeat(64),
  };
  const finding = {
    source: 'native/0.1.0',
    rule: 'lab/missing-authorization',
    verification: 'verified_in_lab',
    evidence,
    evidence_sha256: 'c'.repeat(64),
  };
  h.context.render({findings: [finding]});
  const card = h.cards()[0];
  const panel = card.querySelector('.reviewer-evidence');
  const raw = card.querySelector('pre');
  assert.ok(panel, 'structured reviewer panel missing');
  assert.ok(card.children.indexOf(panel) < card.children.indexOf(raw), 'structured review should precede raw JSON');
  assert.equal(raw.textContent, JSON.stringify(evidence, null, 2));
  const text = JSON.stringify(panel);
  assert.match(text, /ephemeral synthetic loopback lab/);
  assert.match(text, /Credentials sent/);
  assert.match(text, /Customer data sampled/);
  assert.match(text, /unauthenticated read of designated synthetic records/);
});

test('reviewer rendering treats recorded text as text rather than markup', () => {
  const h = harness();
  const malicious = '<img src=x onerror=alert(1)>';
  h.context.render({findings: [{source: malicious, rule: 'safe/rule', verification: 'candidate', evidence: {}, evidence_sha256: 'd'.repeat(64)}]});
  const panel = h.cards()[0].querySelector('.reviewer-evidence');
  assert.match(JSON.stringify(panel), /<img src=x onerror=alert\(1\)>/);
  assert.doesNotMatch(reviewerScript, /\.innerHTML\s*=/);
});
