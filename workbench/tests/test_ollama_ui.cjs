// Dependency-free JavaScript contract tests with an explicit DOM/fetch double.
// These exercise app logic, not browser layout, accessibility auditing or E2E.
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
  return {
    value: '', checked: false, disabled: false, hidden: true, textContent: '', className: '', children: [], listeners: {},
    addEventListener(name, callback) { this.listeners[name] = callback; },
    append(...items) { this.children.push(...items); },
    replaceChildren(...items) { this.children = [...items]; },
  };
}
function harness(responder = async () => ({})) {
  const nodes = Object.fromEntries([...html.matchAll(/\bid="([^"]+)"/g)].map((match) => [match[1], node()]));
  const mode = {value: 'analyst'};
  nodes['target-type'].value = 'lab';
  nodes.authorization.value = 'Synthetic UI test';
  nodes.authorized.checked = true;
  nodes.approve.checked = true;
  const requests = [];
  const document = {
    getElementById(id) { assert.ok(nodes[id], `HTML must define #${id}`); return nodes[id]; },
    querySelector() { return mode; }, querySelectorAll() { return []; }, createElement() { return node(); },
  };
  const context = vm.createContext({document, location: {hash: '', pathname: '/'}, history: {replaceState() {}},
    sessionStorage: {getItem() { return ''; }, setItem() {}}, URLSearchParams, console, setTimeout, clearTimeout,
    fetch: async (path, options) => {
      const body = options.body ? JSON.parse(options.body) : undefined;
      requests.push({path, body});
      const value = await responder(path, body);
      return {ok: !value.__error, json: async () => value.__error || value};
    },
  });
  vm.runInContext(script, context);
  return {nodes, mode, requests, run: (code) => vm.runInContext(code, context),
    trigger: (id, event = 'click') => nodes[id].listeners[event]({preventDefault() {}})};
}
const checked = {model: 'local:test', tool_calling: true, parameter_size: '3B', quantization: 'Q4_K_M', note: 'Metadata only; inference not tested.'};
const finalReport = {id: 'fixture', status: 'completed', target: 'lab', verdict: 'observed_only', findings: [], checks: [], events: [], limitations: [], ai: {}, integrity: {report_sha256: 'fixture'}};

test('initial page does not connect to any AI provider automatically', () => {
  const h = harness(); assert.equal(h.requests.length, 0);
  assert.match(html, /CURRENT AI ADAPTER:\s*OLLAMA/);
  assert.doesNotMatch(html, /AI PROVIDER:\s*OLLAMA ONLY/);
});

test('native-only form clearly disables model checks', () => {
  const h = harness(); h.run('syncForm()');
  assert.equal(h.nodes['check-model'].disabled, true);
  assert.match(h.nodes['model-state'].textContent, /AI disabled/);
});

test('detect fills candidates without replacing an existing selected model', async () => {
  const h = harness(async () => ({models: ['different:test'], note: 'Metadata candidates', state: 'models_detected', blocked_models: 1}));
  h.nodes.model.value = 'chosen:test'; await h.trigger('detect');
  assert.equal(h.nodes.model.value, 'chosen:test');
  assert.equal(h.nodes['model-list'].children[0].value, 'different:test');
  assert.match(h.nodes['model-state'].textContent, /1 remote model/);
});

test('controlled local verification checks tool capability without starting a run', async () => {
  const h = harness(async () => checked);
  h.nodes['use-ai'].checked = true; h.nodes.model.value = 'local:test'; h.mode.value = 'verify';
  await h.run('checkModel()');
  assert.deepEqual(h.requests, [{path: '/api/models/check', body: {model: 'local:test', require_tools: true}}]);
  assert.match(h.nodes['model-state'].textContent, /analysis \+ tool calling/);
  assert.match(h.nodes['model-details'].textContent, /inference not tested/);
});

test('analysis-only models are labeled rather than upgraded to agents', async () => {
  const h = harness(async () => ({...checked, tool_calling: false}));
  h.nodes['use-ai'].checked = true; h.nodes.model.value = 'local:test';
  await h.run('checkModel()');
  assert.equal(h.requests[0].body.require_tools, false);
  assert.match(h.nodes['model-state'].textContent, /analysis only/);
});

test('failed preflight prevents a run and displays recovery without fallback', async () => {
  const h = harness(async () => ({__error: {error: 'Tool calling unsupported.', next_step: 'Choose Analyst mode.'}}));
  h.nodes['use-ai'].checked = true; h.nodes.model.value = 'local:test'; h.mode.value = 'verify';
  await h.trigger('scan-form', 'submit');
  assert.equal(h.requests.length, 1);
  assert.equal(h.requests[0].path, '/api/models/check');
  assert.match(h.nodes.notice.textContent, /Choose Analyst mode/);
  assert.equal(h.nodes.start.disabled, false);
});

test('native-only run does not probe or use Ollama', async () => {
  const h = harness(async (path) => path === '/api/runs/fixture' ? finalReport : path === '/api/runs' ? {id: 'fixture', runs: []} : {});
  await h.trigger('scan-form', 'submit');
  assert.equal(h.requests.filter((request) => request.path.startsWith('/api/models')).length, 0);
  assert.equal(h.requests[0].body.use_ai, false);
});

test('duplicate submits during preflight do not start duplicate assessments', async () => {
  let resolve;
  const h = harness(async (path) => path === '/api/models/check' ? new Promise((done) => { resolve = done; }) : path === '/api/runs/fixture' ? finalReport : {id: 'fixture', runs: []});
  h.nodes['use-ai'].checked = true; h.nodes.model.value = 'local:test';
  const first = h.trigger('scan-form', 'submit');
  await h.trigger('scan-form', 'submit');
  assert.equal(h.requests.length, 1);
  resolve(checked); await first;
  assert.equal(h.requests.filter((request) => request.path === '/api/runs' && request.body).length, 1);
});

test('stale model-check replies do not certify a new selection', async () => {
  let resolve;
  const h = harness(async () => new Promise((done) => { resolve = done; }));
  h.nodes['use-ai'].checked = true; h.nodes.model.value = 'local:test';
  const old = h.run('checkModel()');
  h.nodes.model.value = 'other:test'; await h.trigger('model', 'input');
  resolve(checked); await old;
  assert.equal(h.nodes['model-details'].hidden, true);
  assert.match(h.nodes['model-state'].textContent, /not checked/);
});

test('active runs disable model diagnostics controls', () => {
  const h = harness(); h.nodes['use-ai'].checked = true;
  h.run(`render(${JSON.stringify({...finalReport, status: 'running'})})`);
  assert.equal(h.nodes.detect.disabled, true);
  assert.equal(h.nodes['check-model'].disabled, true);
});

test('cloud approval defaults off and is disabled with AI off', () => {
  const h = harness(); h.run('syncForm()');
  assert.equal(h.nodes['allow-cloud'].checked, false);
  assert.equal(h.nodes['allow-cloud'].disabled, true);
  assert.match(html, /Provider usage limits may apply/);
});

test('cloud-approved metadata preflight keeps exact model and capability contract', async () => {
  const h = harness(async () => ({...checked, execution_location: 'cloud_reported'}));
  h.nodes['use-ai'].checked = true; h.nodes.model.value = 'fixture:cloud'; h.nodes['allow-cloud'].checked = true;
  await h.run('checkModel()');
  assert.deepEqual(h.requests[0].body, {model: 'fixture:cloud', require_tools: false, allow_cloud: true});
  assert.match(h.nodes['model-details'].textContent, /cloud reported/);
});

test('cloud discovery is explicit and does not automatically select a cloud model', async () => {
  const h = harness(async () => ({models: ['fixture:cloud'], note: 'Cloud allowed', state: 'models_detected', blocked_models: 0}));
  h.nodes['use-ai'].checked = true; h.nodes['allow-cloud'].checked = true;
  await h.trigger('detect');
  assert.deepEqual(h.requests[0], {path: '/api/models/discover', body: {allow_cloud: true}});
  assert.equal(h.nodes.model.value, '');
});

test('changing model, target or authorization revokes prior cloud approval', async () => {
  const h = harness(); h.nodes['use-ai'].checked = true;
  for (const id of ['model', 'target', 'authorization']) {
    h.nodes['allow-cloud'].checked = true;
    await h.trigger(id, 'input');
    assert.equal(h.nodes['allow-cloud'].checked, false);
  }
});

test('withdrawing cloud approval during preflight cancels stale submission', async () => {
  let resolve;
  const h = harness(async () => new Promise((done) => { resolve = done; }));
  h.nodes['use-ai'].checked = true; h.nodes.model.value = 'fixture:cloud'; h.nodes['allow-cloud'].checked = true;
  const pending = h.trigger('scan-form', 'submit');
  h.nodes['allow-cloud'].checked = false; await h.trigger('allow-cloud', 'change');
  resolve(checked); await pending;
  assert.equal(h.requests.length, 1);
  assert.match(h.nodes.notice.textContent, /approval changed/);
});

test('successful run forwards approval once and resets it for the next assessment', async () => {
  const h = harness(async (path) => path === '/api/models/check' ? checked : path === '/api/runs/fixture' ? finalReport : {id: 'fixture', runs: []});
  h.nodes['use-ai'].checked = true; h.nodes.model.value = 'fixture:cloud'; h.nodes['allow-cloud'].checked = true;
  await h.trigger('scan-form', 'submit');
  const post = h.requests.find((request) => request.path === '/api/runs' && request.body);
  assert.equal(post.body.allow_cloud, true);
  assert.equal(h.nodes['allow-cloud'].checked, false);
});

test('stale cloud catalog cannot overwrite candidates after consent withdrawal', async () => {
  let resolve;
  const h = harness(async () => new Promise((done) => { resolve = done; }));
  h.nodes['use-ai'].checked = true; h.nodes['allow-cloud'].checked = true;
  const pending = h.trigger('detect');
  h.nodes['allow-cloud'].checked = false; await h.trigger('allow-cloud', 'change');
  resolve({models: ['fixture:cloud'], note: 'old', state: 'models_detected'}); await pending;
  assert.equal(h.nodes['model-list'].children.length, 0);
});

test('Test response is explicit and forwards no target, authorization or evidence', async () => {
  const h = harness(async () => ({model: 'fixture:cloud', note: 'Fixed synthetic prompts only'}));
  h.nodes['use-ai'].checked = true; h.nodes.model.value = 'fixture:cloud'; h.nodes['allow-cloud'].checked = true;
  await h.run('testModel()');
  assert.deepEqual(h.requests, [{path: '/api/models/self-test', body: {model: 'fixture:cloud', require_tools: false, allow_cloud: true}}]);
  assert.match(h.nodes['model-state'].textContent, /not a security finding/);
  assert.equal(h.nodes.start.disabled, false);
});

test('a pending self-test blocks duplicate probes and assessment submissions', async () => {
  let resolve;
  const h = harness(async () => new Promise((done) => { resolve = done; }));
  h.nodes['use-ai'].checked = true; h.nodes.model.value = 'local:test';
  const pending = h.run('testModel()');
  await h.run('testModel()'); await h.trigger('scan-form', 'submit');
  assert.equal(h.requests.length, 1);
  resolve({model: 'local:test', note: 'Fixed probe'}); await pending;
});

test('stale self-test response does not validate a newly selected model', async () => {
  let resolve;
  const h = harness(async () => new Promise((done) => { resolve = done; }));
  h.nodes['use-ai'].checked = true; h.nodes.model.value = 'old:test';
  const pending = h.run('testModel()');
  h.nodes.model.value = 'new:test'; await h.trigger('model', 'input');
  resolve({model: 'old:test', note: 'Stale'}); await pending;
  assert.equal(h.nodes['model-details'].hidden, true);
  assert.match(h.nodes['model-state'].textContent, /not checked/);
});
