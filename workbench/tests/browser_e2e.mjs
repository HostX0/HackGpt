// Real Chromium-to-loopback Workbench journey using only owned synthetic fixtures.
// This test intentionally avoids browser automation packages: it talks to Chrome's
// DevTools protocol directly so fresh-source validation has no npm dependency.
import assert from 'node:assert/strict';
import {mkdir, mkdtemp, readFile, rm, writeFile} from 'node:fs/promises';
import {createConnection} from 'node:net';
import {tmpdir} from 'node:os';
import {basename, dirname, join, resolve} from 'node:path';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, '..', '..');
const chromeBin = process.env.CHROME_BIN;
if (!chromeBin) throw new Error('CHROME_BIN is required');

const sleep = (ms) => new Promise((resolveSleep) => setTimeout(resolveSleep, ms));

async function freePort() {
  return new Promise((resolvePort, reject) => {
    const server = createConnection();
    server.on('error', () => {});
    const listener = import('node:net').then(({createServer}) => {
      const socketServer = createServer();
      socketServer.on('error', reject);
      socketServer.listen(0, '127.0.0.1', () => {
        const {port} = socketServer.address();
        socketServer.close(() => resolvePort(port));
      });
    });
    void listener;
  });
}

async function waitFor(fn, label, timeoutMs = 15000, intervalMs = 100) {
  const deadline = Date.now() + timeoutMs;
  let lastError;
  while (Date.now() < deadline) {
    try {
      const value = await fn();
      if (value) return value;
    } catch (error) {
      lastError = error;
    }
    await sleep(intervalMs);
  }
  if (lastError) throw new Error(`Timed out waiting for ${label}: ${lastError.message}`);
  throw new Error(`Timed out waiting for ${label}`);
}

function childProcess(command, args, options = {}) {
  const child = spawn(command, args, {cwd: repoRoot, stdio: ['ignore', 'pipe', 'pipe'], ...options});
  let stdout = '';
  let stderr = '';
  child.stdout?.on('data', (chunk) => { stdout += chunk.toString(); });
  child.stderr?.on('data', (chunk) => { stderr += chunk.toString(); });
  return {child, stdout: () => stdout, stderr: () => stderr};
}

async function terminate(child) {
  if (!child || child.exitCode !== null) return;
  child.kill('SIGTERM');
  await Promise.race([
    new Promise((resolveExit) => child.once('exit', resolveExit)),
    sleep(3000).then(() => { if (child.exitCode === null) child.kill('SIGKILL'); }),
  ]);
}

class DevTools {
  constructor(wsUrl) {
    const url = new URL(wsUrl);
    this.host = url.hostname;
    this.port = Number(url.port);
    this.path = url.pathname + url.search;
    this.socket = null;
    this.buffer = Buffer.alloc(0);
    this.pending = new Map();
    this.events = [];
    this.nextId = 1;
  }

  async connect() {
    const key = Buffer.from('hackgpt-browser-e2e').toString('base64');
    this.socket = await new Promise((resolveSocket, reject) => {
      const socket = createConnection({host: this.host, port: this.port}, () => resolveSocket(socket));
      socket.once('error', reject);
    });
    this.socket.write([
      `GET ${this.path} HTTP/1.1`,
      `Host: ${this.host}:${this.port}`,
      'Upgrade: websocket',
      'Connection: Upgrade',
      `Sec-WebSocket-Key: ${key}`,
      'Sec-WebSocket-Version: 13',
      '\r\n',
    ].join('\r\n'));
    let header = '';
    while (!header.includes('\r\n\r\n')) {
      header += await new Promise((resolveChunk, reject) => {
        const onData = (chunk) => { cleanup(); resolveChunk(chunk.toString('binary')); };
        const onError = (error) => { cleanup(); reject(error); };
        const cleanup = () => { this.socket.off('data', onData); this.socket.off('error', onError); };
        this.socket.once('data', onData);
        this.socket.once('error', onError);
      });
    }
    assert.match(header, /^HTTP\/1\.1 101 /, 'DevTools WebSocket upgrade failed');
    this.socket.on('data', (chunk) => this._onData(chunk));
  }

  _onData(chunk) {
    this.buffer = Buffer.concat([this.buffer, chunk]);
    while (this.buffer.length >= 2) {
      const first = this.buffer[0];
      const second = this.buffer[1];
      let length = second & 0x7f;
      let offset = 2;
      if (length === 126) {
        if (this.buffer.length < 4) return;
        length = this.buffer.readUInt16BE(2); offset = 4;
      } else if (length === 127) {
        if (this.buffer.length < 10) return;
        const longLength = this.buffer.readBigUInt64BE(2);
        if (longLength > BigInt(Number.MAX_SAFE_INTEGER)) throw new Error('oversized WebSocket frame');
        length = Number(longLength); offset = 10;
      }
      const masked = Boolean(second & 0x80);
      const maskOffset = offset;
      if (masked) offset += 4;
      if (this.buffer.length < offset + length) return;
      let payload = Buffer.from(this.buffer.subarray(offset, offset + length));
      if (masked) {
        const mask = this.buffer.subarray(maskOffset, maskOffset + 4);
        payload = Buffer.from(payload.map((byte, index) => byte ^ mask[index % 4]));
      }
      this.buffer = this.buffer.subarray(offset + length);
      const opcode = first & 0x0f;
      if (opcode === 8) return;
      if (opcode !== 1) continue;
      const message = JSON.parse(payload.toString('utf8'));
      if (message.id && this.pending.has(message.id)) {
        const {resolve: resolvePending, reject} = this.pending.get(message.id);
        this.pending.delete(message.id);
        if (message.error) reject(new Error(message.error.message || JSON.stringify(message.error)));
        else resolvePending(message.result || {});
      } else if (message.method) {
        this.events.push(message);
      }
    }
  }

  command(method, params = {}) {
    const id = this.nextId++;
    const payload = Buffer.from(JSON.stringify({id, method, params}));
    const mask = Buffer.from([0x11, 0x22, 0x33, 0x44]);
    let header;
    if (payload.length < 126) header = Buffer.from([0x81, 0x80 | payload.length]);
    else {
      header = Buffer.alloc(4); header[0] = 0x81; header[1] = 0x80 | 126; header.writeUInt16BE(payload.length, 2);
    }
    const masked = Buffer.from(payload.map((byte, index) => byte ^ mask[index % 4]));
    this.socket.write(Buffer.concat([header, mask, masked]));
    return new Promise((resolveCommand, reject) => {
      this.pending.set(id, {resolve: resolveCommand, reject});
      setTimeout(() => {
        if (this.pending.delete(id)) reject(new Error(`DevTools command timed out: ${method}`));
      }, 15000).unref();
    });
  }

  close() { this.socket?.end(); }
}

const port = await freePort();
const debugPort = await freePort();
const workRoot = await mkdtemp(join(tmpdir(), 'hackgpt-browser-e2e-'));
const dataDir = join(workRoot, 'data');
const profileDir = join(workRoot, 'chrome');
await mkdir(dataDir);
await mkdir(profileDir);

const server = childProcess(process.env.PYTHON || 'python', ['-m', 'workbench', '--port', String(port), '--data-dir', dataDir]);
const launchLine = await waitFor(() => {
  const all = `${server.stdout()}\n${server.stderr()}`;
  return all.split(/\r?\n/).find((line) => line.includes('#token='));
}, 'private workbench launch URL');
const launchUrl = launchLine.match(/https?:\/\/\S+/)?.[0];
assert(launchUrl, 'launch URL was not printed');
const launchToken = new URL(launchUrl).hash.replace(/^#token=/, '');
assert(launchToken.length >= 16, 'launch token missing');

const chrome = childProcess(chromeBin, [
  '--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage',
  `--remote-debugging-port=${debugPort}`, `--user-data-dir=${profileDir}`, 'about:blank',
]);

let devtools;
try {
  const version = await waitFor(async () => {
    const response = await fetch(`http://127.0.0.1:${debugPort}/json/version`);
    return response.ok ? response.json() : null;
  }, 'Chrome DevTools endpoint');
  const targets = await fetch(`http://127.0.0.1:${debugPort}/json`).then((response) => response.json());
  const page = targets.find((item) => item.type === 'page');
  assert(page?.webSocketDebuggerUrl, 'no Chrome page target found');
  devtools = new DevTools(page.webSocketDebuggerUrl);
  await devtools.connect();
  await devtools.command('Page.enable');
  await devtools.command('Runtime.enable');
  const runtimeExceptions = [];
  const originalOnData = devtools._onData.bind(devtools);
  devtools._onData = (chunk) => {
    originalOnData(chunk);
    for (const event of devtools.events.splice(0)) {
      if (event.method === 'Runtime.exceptionThrown') runtimeExceptions.push(event.params);
    }
  };
  await devtools.command('Page.navigate', {url: launchUrl});
  await waitFor(async () => {
    const result = await devtools.command('Runtime.evaluate', {expression: 'document.readyState', returnByValue: true});
    return result.result?.value === 'complete';
  }, 'workbench page load');

  async function evaluate(expression) {
    const result = await devtools.command('Runtime.evaluate', {expression, awaitPromise: true, returnByValue: true});
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || 'Runtime evaluation failed');
    return result.result?.value;
  }

  await waitFor(() => evaluate("document.getElementById('connection').textContent === 'Local session'"), 'session unlock');
  assert(await evaluate("location.hash === ''"), 'session token fragment was not removed');
  assert(await evaluate("sessionStorage.getItem('hackgpt-token').length >= 16"), 'session token was not held in session storage');
  assert(await evaluate("!document.body.innerText.includes(sessionStorage.getItem('hackgpt-token'))"), 'session token rendered into page text');
  assert(await evaluate("document.getElementById('controls').disabled === false"), 'assessment form not unlocked');
  assert(await evaluate("document.getElementById('adapter-workspace') !== null"), 'reviewed adapter UI missing');
  assert(await evaluate("document.getElementById('adapter-execute').disabled"), 'adapter execute enabled before plan/approval');

  await evaluate(`(() => {
    document.getElementById('target-type').value = 'lab';
    document.getElementById('target-type').dispatchEvent(new Event('change', {bubbles:true}));
    document.querySelector('input[name="mode"][value="verify"]').checked = true;
    document.querySelector('input[name="mode"][value="verify"]').dispatchEvent(new Event('change', {bubbles:true}));
    document.getElementById('authorization').value = 'browser-e2e-owned-lab';
    document.getElementById('authorized').checked = true;
    document.getElementById('approve').checked = true;
    document.getElementById('scan-form').requestSubmit();
    return true;
  })()`);

  await waitFor(async () => (await evaluate("document.getElementById('integrity').textContent.startsWith('Finalized report SHA-256')")) === true, 'finalized synthetic assessment', 20000, 120);
  assert(Number(await evaluate("document.getElementById('count-verified').textContent")) >= 1, 'owned synthetic verification did not render a verified lab finding');
  assert((await evaluate("document.getElementById('verdict').textContent")).includes('verified in synthetic lab only'), 'UI did not preserve synthetic-only verdict wording');
  assert(await evaluate("document.getElementById('history-list').textContent.includes('lab')"), 'finalized run did not appear in browser history UI');
  // Exercise the existing approved metadata adapter -> report path on an owned directory.
  const projectDir = join(workRoot, 'owned-project');
  await mkdir(projectDir);
  await writeFile(join(projectDir, 'README.md'), 'Owned browser integration fixture. No secrets.\n');
  await evaluate(`(() => {
    document.getElementById('adapter-kind').value = 'project';
    document.getElementById('adapter-kind').dispatchEvent(new Event('change', {bubbles:true}));
    document.getElementById('adapter-asset').value = 'browser-owned-project';
    document.getElementById('adapter-target').value = ${JSON.stringify(projectDir)};
    document.getElementById('adapter-plan').click();
    return true;
  })()`);
  await waitFor(() => evaluate("!document.getElementById('adapter-approve').disabled"), 'adapter authority preview');
  assert(await evaluate("document.getElementById('adapter-execute').disabled"), 'planning alone enabled execution');
  assert(await evaluate("document.getElementById('adapter-target').disabled"), 'planned scope was editable');
  await evaluate("document.getElementById('adapter-approve').click()");
  await waitFor(() => evaluate("!document.getElementById('adapter-execute').disabled"), 'exact plan approval');
  await evaluate("document.getElementById('adapter-execute').click()");
  await waitFor(() => evaluate("!document.getElementById('adapter-report').disabled"), 'owned adapter receipt');
  assert(await evaluate("document.getElementById('adapter-preview').textContent.includes('Lifecycle state: COMPLETED')"), 'adapter did not render completed lifecycle state');
  assert(await evaluate("document.getElementById('adapter-preview').textContent.includes('Durable receipt: present')"), 'adapter did not render its durable receipt boundary');
  assert(await evaluate("document.getElementById('adapter-preview').textContent.includes('Candidate findings recorded:')"), 'adapter did not render candidate finding count');
  await evaluate("document.getElementById('adapter-report').click()");
  await waitFor(() => evaluate("!document.getElementById('adapter-open-report').disabled"), 'linked candidate report');
  await evaluate("document.getElementById('adapter-open-report').click()");
  await waitFor(() => evaluate("document.getElementById('run-status').textContent.includes('project://') && !document.getElementById('export-json').disabled"), 'linked report review');
  await waitFor(() => evaluate("document.activeElement.id === 'verdict'"), 'linked report conclusion focus');
  assert(await evaluate("Number(document.getElementById('count-verified').textContent) === 0"), 'adapter observations were promoted to verified');
  assert(await evaluate("!document.getElementById('use-ai').checked"), 'report review enabled AI');
  assert(await evaluate(`!document.body.innerText.includes(${JSON.stringify(launchToken)})`), 'token leaked during adapter review');
  assert(runtimeExceptions.length === 0, `browser runtime exceptions observed: ${runtimeExceptions.length}`);

  const summary = {
    schema: 'hackgpt.browser-e2e/v1',
    browser: version.Browser || 'unknown',
    protocol: version['Protocol-Version'] || 'unknown',
    loopback_server: true,
    token_fragment_removed: true,
    session_unlocked: true,
    owned_synthetic_assessment: true,
    owned_adapter_lifecycle_review: true,
    adapter_report_review: true,
    accessibility: {
      main_navigation_named: await evaluate("Boolean(document.querySelector('nav[aria-label]'))"),
      live_status: await evaluate("document.getElementById('notice').getAttribute('aria-live') === 'polite' && document.getElementById('model-state').getAttribute('aria-live') === 'polite' && document.getElementById('adapter-status').getAttribute('aria-live') === 'polite'"),
      native_disclosures: await evaluate("document.querySelectorAll('details > summary').length >= 3"),
      verdict_focusable: await evaluate("document.getElementById('verdict').getAttribute('tabindex') === '-1'"),
    },
  };
  console.log(JSON.stringify(summary));
} finally {
  devtools?.close();
  await terminate(chrome.child);
  await terminate(server.child);
  await rm(workRoot, {recursive: true, force: true});
}
