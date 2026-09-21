'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const vm = require('node:vm');
const root = join(__dirname, '..', 'static');
const html = readFileSync(join(root, 'index.html'), 'utf8');
const script = readFileSync(join(root, 'app.js'), 'utf8');

function node() {
  return {value: '', checked: false, disabled: false, hidden: true, textContent: '', className: '', children: [], listeners: {},
    addEventListener(name, callback) { this.listeners[name] = callback; },
    append(...items) { this.children.push(...items); }, replaceChildren(...items) { this.children = [...items]; }};
}
function harness(responder = async () => ({})) {
  const nodes = Object.fromEntries([...html.matchAll(/\bid="([^"]+)"/g)].map((match) => [match[1], node()]));
  const mode = {value: 'analyst'};
  nodes['target-type'].value = 'lab'; nodes.authorization.value = 'Reviewer UI fixture'; nodes.authorized.checked = true;
  const requests = [];
  const document = {getElementById(id) { assert.ok(nodes[id], `HTML must define #${id}`); return nodes[id]; },
    querySelector() { return mode; }, querySelectorAll() { return []; }, createElement() { return node(); }};
  const context = vm.createContext({document, location: {hash: '', pathname: '/'}, history: {replaceState() {}},
    sessionStorage: {getItem() { return ''; }, setItem() {}}, URLSearchParams, console, setTimeout, clearTimeout,
    fetch: async (path, options) => { const body = options.body ? JSON.parse(options.body) : undefined; requests.push({path, body}); const value = await responder(path, body); return {ok: !value.__error, json: async () => value.__error || value}; }});
  vm.runInContext(script, context);
  return {nodes, requests, run: (code) => vm.runInContext(code, context),
    trigger: (id, event = 'click') => nodes[id].listeners[event]({preventDefault() {}})};
}
function report(id) {
  return {id, status: 'completed', target: 'lab://fixture', environment: 'synthetic_lab', verdict: 'observations_need_context', findings: [], checks: [], events: [], limitations: [], ai: {}, integrity: {report_sha256: 'fixture'}};
}

test('finalized report enables evidence bundle export control', () => {
  const h = harness(); h.run(`selectedRun = '${'b'.repeat(32)}'; render(${JSON.stringify(report('b'.repeat(32)))})`);
  assert.equal(h.nodes['export-bundle'].disabled, false);
  assert.match(html, /Evidence bundle/);
});

test('running report keeps evidence bundle disabled', () => {
  const h = harness(); const running = {...report('b'.repeat(32)), status: 'running', integrity: null};
  h.run(`selectedRun = '${'b'.repeat(32)}'; render(${JSON.stringify(running)})`);
  assert.equal(h.nodes['export-bundle'].disabled, true);
});

test('retest selector compares an earlier finalized run to the selected run', async () => {
  const oldId = 'a'.repeat(32), currentId = 'b'.repeat(32);
  const h = harness(async (path) => path.includes('/compare/') ? {schema: 'hackgpt.retest-diff/v1', counts: {not_reproduced: 1}, items: [], note: 'comparison only'} : {});
  h.run(`historyRuns = [{id:'${oldId}', started_at:'2026-09-20T00:00:00Z', target:'lab://fixture', verdict:'observations_need_context'}]; selectedRun='${currentId}'; render(${JSON.stringify(report(currentId))})`);
  h.nodes['compare-run'].value = oldId; await h.trigger('compare-run', 'change'); await h.trigger('compare');
  assert.equal(h.requests[0].path, `/api/runs/${oldId}/compare/${currentId}`);
  assert.match(h.nodes['compare-content'].textContent, /not_reproduced/);
});
