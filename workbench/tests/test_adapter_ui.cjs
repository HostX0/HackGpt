'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const vm = require('node:vm');
const root = join(__dirname, '..', 'static');
const html = readFileSync(join(root, 'index.html'), 'utf8');
const script = readFileSync(join(root, 'adapter.js'), 'utf8');

function node() {
  return {value: '', checked: false, disabled: false, hidden: false, textContent: '', className: '', listeners: {},
    addEventListener(name, callback) { this.listeners[name] = callback; }};
}

function harness(responder) {
  const nodes = Object.fromEntries([...html.matchAll(/\bid="([^"]+)"/g)].map((m) => [m[1], node()]));
  nodes['adapter-kind'].value = 'project';
  nodes['adapter-asset'].value = 'asset-1';
  nodes['adapter-target'].value = '/tmp/project';
  const requests = [];
  const document = {getElementById(id) { assert.ok(nodes[id], `missing #${id}`); return nodes[id]; }};
  const context = vm.createContext({
    document,
    sessionStorage: {getItem() { return 'session-token'; }},
    fetch: async (path, options) => {
      const body = options.body ? JSON.parse(options.body) : undefined;
      requests.push({path, body, options});
      const value = await responder(path, body);
      return {ok: !value.__error, json: async () => value.__error || value};
    },
    console,
  });
  vm.runInContext(script, context);
  return {nodes, requests, trigger: async (id, event='click') => nodes[id].listeners[event]({preventDefault() {}})};
}

const id = 'a'.repeat(32);
const sha = 'b'.repeat(64);
const declaration = {adapter: {id: 'native-project-metadata', version: '1'}, limits: {max_objects: 1000, max_requests: 0, timeout_seconds: 30}};

function planned(status='planned') {
  return {id, status, adapter_id: 'native-project-metadata', plan_sha256: sha, declaration,
    request_summary: {adapter_id: 'native-project-metadata', asset_key: 'asset-1', project_label: 'project', full_path_included: false}, outcome: null};
}

test('adapter UI performs no automatic execution or discovery', () => {
  const h = harness(async () => ({}));
  assert.equal(h.requests.length, 0);
  assert.equal(h.nodes['adapter-approve'].disabled, true);
  assert.equal(h.nodes['adapter-execute'].disabled, true);
  assert.match(h.nodes['adapter-status'].textContent, /Plan first/);
});

test('plan preview freezes exact inputs before approval', async () => {
  const h = harness(async (path) => {
    assert.equal(path, '/api/adapters/plan');
    return planned();
  });
  await h.trigger('adapter-plan');
  assert.equal(h.requests.length, 1);
  assert.deepEqual(h.requests[0].body, {adapter_id: 'native-project-metadata', request: {
    root: '/tmp/project', asset_key: 'asset-1', max_files: 1000, max_depth: 12, timeout_seconds: 30,
  }});
  assert.equal(h.nodes['adapter-kind'].disabled, true);
  assert.equal(h.nodes['adapter-target'].disabled, true);
  assert.equal(h.nodes['adapter-approve'].disabled, false);
  assert.match(h.nodes['adapter-preview'].textContent, /full_path_included/);
});

test('approve binds digest then execute resends the planned typed request', async () => {
  const h = harness(async (path, body) => {
    if (path === '/api/adapters/plan') return planned();
    if (path.endsWith('/approve')) return {...planned('approved'), outcome: {code: 'approved_exact_plan'}};
    if (path.endsWith('/execute')) return {...planned('completed'), outcome: {code: 'completed_with_candidate_result'}, receipt: {
      usage: {objects_tested: 2, network_requests: 0, elapsed_ms: 3},
      result: {findings: [{verification: 'candidate'}], coverage: {objects_tested: 2}},
    }};
    throw new Error('unexpected path ' + path + JSON.stringify(body));
  });
  await h.trigger('adapter-plan');
  await h.trigger('adapter-approve');
  assert.equal(h.requests[1].body.plan_sha256, sha);
  assert.equal(h.nodes['adapter-execute'].disabled, false);
  await h.trigger('adapter-execute');
  assert.equal(h.requests[2].body.adapter_id, 'native-project-metadata');
  assert.equal(h.requests[2].body.request.root, '/tmp/project');
  assert.match(h.nodes['adapter-preview'].textContent, /candidate_findings/);
  assert.match(h.nodes['adapter-status'].textContent, /durable receipt/);
});

test('Semgrep adapter uses only reviewed bounded fields and explains offline container policy', async () => {
  const h = harness(async () => planned());
  h.nodes['adapter-kind'].value = 'semgrep';
  h.nodes['adapter-asset'].value = 'project-src';
  h.nodes['adapter-target'].value = '/tmp/source';
  await h.trigger('adapter-kind', 'change');
  await h.trigger('adapter-plan');
  assert.deepEqual(h.requests[0].body, {adapter_id: 'semgrep-project-local', request: {
    root: '/tmp/source', asset_key: 'project-src', max_files: 250, max_depth: 12,
    timeout_seconds: 90, max_target_bytes: 500000,
  }});
  assert.match(h.nodes['adapter-target-help'].textContent, /network-disabled container/);
  assert.match(h.nodes['adapter-target-help'].textContent, /never auto-pulls/);
});

test('web adapter request uses only exact target asset key and timeout', async () => {
  const h = harness(async () => planned());
  h.nodes['adapter-kind'].value = 'web';
  h.nodes['adapter-asset'].value = 'web-1';
  h.nodes['adapter-target'].value = 'https://example.test';
  await h.trigger('adapter-kind', 'change');
  await h.trigger('adapter-plan');
  assert.deepEqual(h.requests[0].body, {adapter_id: 'native-web-headers', request: {
    target: 'https://example.test', asset_key: 'web-1', timeout_seconds: 15,
  }});
  assert.match(h.nodes['adapter-target-help'].textContent, /one HEAD request/);
});
