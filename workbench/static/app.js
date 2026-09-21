'use strict';
const $ = (id) => document.getElementById(id);
let token = sessionStorage.getItem('hackgpt-token') || '';
let selectedRun = null;
let polling = null;
let running = false;
const fragment = new URLSearchParams(location.hash.slice(1));
if (fragment.has('token')) {
  token = fragment.get('token');
  sessionStorage.setItem('hackgpt-token', token);
  history.replaceState(null, '', location.pathname);
}
function notice(text, error = false) {
  $('notice').textContent = text;
  $('notice').className = text ? (error ? 'notice error' : 'notice') : '';
}
async function api(path, body, raw = false) {
  const response = await fetch(path, {method: body === undefined ? 'GET' : 'POST', headers: {'Authorization': 'Bearer ' + token, ...(body === undefined ? {} : {'Content-Type': 'application/json'})}, ...(body === undefined ? {} : {body: JSON.stringify(body)})});
  if (!response.ok) {
    const error = await response.json().catch(() => ({error: 'Local service unavailable'}));
    throw new Error(error.error || 'Request failed');
  }
  return raw ? response : response.json();
}
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = String(text);
  if (className) node.className = className;
  return node;
}
function human(text) { return String(text || '').replaceAll('_', ' '); }
function syncForm() {
  const lab = $('target-type').value === 'lab';
  $('target').disabled = lab;
  $('target').required = !lab;
  $('target-help').textContent = lab ? 'A disposable local fixture with a real HTTP proof. No external target is contacted.' : 'One HEAD request to this exact public URL. Ports 80/443 only. No redirects, private IPs or response bodies.';
  const verify = document.querySelector('input[name="mode"]:checked').value === 'verify';
  $('approval-row').hidden = !verify;
  $('approve').required = verify;
  $('model').disabled = !$('use-ai').checked;
  $('model').required = $('use-ai').checked;
}
async function unlock() {
  try {
    const health = await api('/api/health');
    $('unlock').hidden = true;
    $('connection').textContent = 'Local session connected';
    $('connection').className = 'status connected';
    $('controls').disabled = false;
    $('refresh').disabled = false;
    syncForm();
    await loadHistory();
    notice('');
    if (health.active_run) await selectRun(health.active_run);
  } catch (error) {
    $('unlock').hidden = false;
    $('controls').disabled = true;
    $('refresh').disabled = true;
    $('connection').textContent = 'Session locked';
    $('connection').className = 'status';
    if (token) notice(error.message, true);
  }
}
$('unlock-form').addEventListener('submit', async (event) => {
  event.preventDefault(); token = $('token').value.trim(); $('token').value = '';
  sessionStorage.setItem('hackgpt-token', token); await unlock();
});
$('target-type').addEventListener('change', syncForm);
$('use-ai').addEventListener('change', syncForm);
document.querySelectorAll('input[name="mode"]').forEach((node) => node.addEventListener('change', syncForm));
$('detect').addEventListener('click', async () => {
  $('detect').disabled = true;
  try {
    const result = await api('/api/models');
    $('model-list').replaceChildren();
    result.models.forEach((name) => { const option = element('option'); option.value = name; $('model-list').append(option); });
    if (result.models.length && !$('model').value) $('model').value = result.models[0];
    $('model-help').textContent = result.note + (result.models.length ? ' ' + result.models.length + ' local model(s) detected.' : '');
  } catch (error) { notice(error.message, true); }
  finally { $('detect').disabled = false; }
});
$('scan-form').addEventListener('submit', async (event) => {
  event.preventDefault(); if (running) return;
  const body = {target: $('target-type').value === 'lab' ? 'lab' : $('target').value.trim(), mode: document.querySelector('input[name="mode"]:checked').value, authorized: $('authorized').checked, authorization: $('authorization').value.trim(), approve_verification: $('approve').checked, use_ai: $('use-ai').checked, model: $('model').value.trim()};
  $('start').disabled = true;
  try {
    const result = await api('/api/runs', body);
    notice('Run started. Only recorded evidence determines the verification state.');
    await selectRun(result.id);
  } catch (error) { notice(error.message, true); $('start').disabled = false; }
});
async function selectRun(id) {
  if (polling) clearTimeout(polling);
  selectedRun = id;
  await poll(id);
}
async function poll(id) {
  try {
    const report = await api('/api/runs/' + id);
    if (id !== selectedRun) return;
    render(report);
    if (report.status === 'running') polling = setTimeout(() => poll(id), 900);
    else await loadHistory();
  } catch (error) {
    running = false; $('start').disabled = false; $('cancel').disabled = true;
    notice(error.message + ' Reconnect before assuming the run has stopped.', true);
  }
}
function render(report) {
  running = report.status === 'running';
  $('start').disabled = running; $('cancel').disabled = !running;
  $('export-json').disabled = running || !report.integrity; $('export-md').disabled = running || !report.integrity;
  $('count-findings').textContent = report.findings.length;
  $('count-verified').textContent = report.findings.filter((f) => f.verification === 'verified_in_lab').length;
  $('count-checks').textContent = report.checks.filter((c) => c.status === 'completed').length;
  $('run-status').textContent = human(report.status).toUpperCase() + ' / ' + report.target;
  $('verdict').textContent = human(report.verdict);
  $('timeline').replaceChildren();
  report.events.forEach((event) => {
    const row = element('div', undefined, 'event');
    const time = new Date(event.at).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'});
    row.append(element('time', time), element('span', event.message)); $('timeline').append(row);
  });
  $('timeline').scrollTop = $('timeline').scrollHeight;
  $('findings').replaceChildren();
  if (!report.findings.length) $('findings').append(element('p', 'No findings recorded in the executed checks. Review coverage before drawing conclusions.', 'muted'));
  report.findings.forEach((finding) => {
    const details = element('details', undefined, 'finding');
    const summary = element('summary');
    summary.append(element('span', finding.severity.toUpperCase(), 'severity ' + finding.severity), element('strong', finding.title));
    details.append(summary, element('div', human(finding.verification), 'verification'), element('p', finding.remediation));
    details.append(element('pre', JSON.stringify(finding.evidence, null, 2)), element('p', 'Evidence SHA-256: ' + finding.evidence_sha256, 'hash'));
    $('findings').append(details);
  });
  $('coverage-content').textContent = JSON.stringify({checks: report.checks, limitations: report.limitations}, null, 2);
  $('ai-content').textContent = JSON.stringify(report.ai, null, 2);
  $('integrity').textContent = report.integrity ? 'Finalized report SHA-256 (unsigned): ' + report.integrity.report_sha256 : 'Report in progress. Integrity digest will be calculated at completion.';
  if (report.persistence_error) notice(report.persistence_error, true);
}
async function loadHistory() {
  const result = await api('/api/runs');
  $('history-list').replaceChildren();
  if (!result.runs.length) return $('history-list').append(element('p', 'No saved assessments yet. Completed, partial and failed runs will appear here.', 'muted'));
  result.runs.forEach((run) => {
    const button = element('button', undefined, 'history-item'); button.type = 'button';
    button.append(element('strong', run.target), element('span', human(run.verdict)), element('time', new Date(run.started_at).toLocaleString()));
    button.disabled = running;
    button.addEventListener('click', () => selectRun(run.id)); $('history-list').append(button);
  });
}
$('refresh').addEventListener('click', () => loadHistory().catch((error) => notice(error.message, true)));
$('cancel').addEventListener('click', async () => {
  try { const result = await api('/api/runs/' + selectedRun + '/cancel', {}); notice(result.note); $('cancel').disabled = true; }
  catch (error) { notice(error.message, true); }
});
async function download(extension) {
  try {
    const response = await api('/api/runs/' + selectedRun + '/export.' + extension, undefined, true);
    const url = URL.createObjectURL(await response.blob()); const link = document.createElement('a');
    link.href = url; link.download = 'hackgpt-' + selectedRun + '.' + extension; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (error) { notice(error.message, true); }
}
$('export-json').addEventListener('click', () => download('json'));
$('export-md').addEventListener('click', () => download('md'));
if (token) unlock();
