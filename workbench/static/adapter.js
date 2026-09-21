'use strict';
(() => {
  const byId = (id) => document.getElementById(id);
  const panel = byId('adapter-workspace');
  if (!panel) return;

  let plan = null;
  let executing = false;

  async function request(path, body) {
    const token = sessionStorage.getItem('hackgpt-token') || '';
    const response = await fetch(path, {
      method: body === undefined ? 'GET' : 'POST',
      headers: {
        Authorization: 'Bearer ' + token,
        ...(body === undefined ? {} : {'Content-Type': 'application/json'}),
      },
      ...(body === undefined ? {} : {body: JSON.stringify(body)}),
    });
    const payload = await response.json().catch(() => ({error: 'Local adapter service unavailable'}));
    if (!response.ok) throw new Error(payload.error || 'Adapter request failed');
    return payload;
  }

  function setStatus(text, error = false) {
    const node = byId('adapter-status');
    node.textContent = text;
    node.className = error ? 'help adapter-error' : 'help';
  }

  function kind() { return byId('adapter-kind').value; }
  function adapterId() { return kind() === 'project' ? 'native-project-metadata' : 'native-web-headers'; }

  function buildRequest() {
    const assetKey = byId('adapter-asset').value.trim();
    const target = byId('adapter-target').value.trim();
    if (!assetKey || !target) throw new Error('Provide an engagement asset key and exact target.');
    if (kind() === 'project') {
      return {root: target, asset_key: assetKey, max_files: 1000, max_depth: 12, timeout_seconds: 30};
    }
    return {target, asset_key: assetKey, timeout_seconds: 15};
  }

  function freeze(value) {
    byId('adapter-kind').disabled = value;
    byId('adapter-asset').disabled = value;
    byId('adapter-target').disabled = value;
  }

  function resetPlan() {
    if (executing) return;
    plan = null;
    freeze(false);
    byId('adapter-plan').disabled = false;
    byId('adapter-approve').disabled = true;
    byId('adapter-execute').disabled = true;
    byId('adapter-cancel').disabled = true;
    byId('adapter-reset').disabled = true;
    byId('adapter-preview').textContent = 'No reviewed adapter plan yet.';
    setStatus('Plan first. Execution remains disabled until the exact minimized authority preview is approved.');
    syncTargetLabel();
  }

  function syncTargetLabel() {
    const project = kind() === 'project';
    byId('adapter-target-label').textContent = project ? 'Project directory on this machine' : 'Exact authorized URL';
    byId('adapter-target').placeholder = project ? '/path/to/authorized/project' : 'https://authorized.example';
    byId('adapter-target-help').textContent = project
      ? 'Metadata-only: filenames may be inspected within the displayed limits. File contents are not read and symlinks are not followed.'
      : 'Passive bounded web check: one HEAD request, no redirects and no response body.';
  }

  function show(record) {
    byId('adapter-preview').textContent = JSON.stringify({
      id: record.id,
      status: record.status,
      declaration: record.declaration,
      request_summary: record.request_summary,
      plan_sha256: record.plan_sha256,
      outcome: record.outcome || null,
      usage: record.receipt ? record.receipt.usage : null,
      candidate_findings: record.receipt ? record.receipt.result.findings.length : null,
      coverage: record.receipt ? record.receipt.result.coverage : null,
    }, null, 2);
  }

  byId('adapter-kind').addEventListener('change', syncTargetLabel);
  byId('adapter-reset').addEventListener('click', resetPlan);

  byId('adapter-plan').addEventListener('click', async () => {
    try {
      const body = {adapter_id: adapterId(), request: buildRequest()};
      byId('adapter-plan').disabled = true;
      setStatus('Validating typed scope and operator authority. No adapter I/O is performed while planning.');
      const record = await request('/api/adapters/plan', body);
      plan = {id: record.id, planSha256: record.plan_sha256, adapterId: body.adapter_id, request: body.request};
      freeze(true);
      byId('adapter-approve').disabled = false;
      byId('adapter-reset').disabled = false;
      show(record);
      setStatus('Plan ready. Review the minimized declaration and limits before approving the exact plan digest.');
    } catch (error) {
      byId('adapter-plan').disabled = false;
      setStatus(error.message, true);
    }
  });

  byId('adapter-approve').addEventListener('click', async () => {
    if (!plan || executing) return;
    try {
      byId('adapter-approve').disabled = true;
      const record = await request('/api/adapter-runs/' + plan.id + '/approve', {plan_sha256: plan.planSha256});
      show(record);
      byId('adapter-execute').disabled = false;
      setStatus('Exact plan approved. Execution will revalidate the same request before any I/O.');
    } catch (error) {
      byId('adapter-approve').disabled = false;
      setStatus(error.message, true);
    }
  });

  byId('adapter-execute').addEventListener('click', async () => {
    if (!plan || executing) return;
    executing = true;
    byId('adapter-execute').disabled = true;
    byId('adapter-reset').disabled = true;
    byId('adapter-cancel').disabled = false;
    setStatus('Executing the approved bounded adapter. Findings remain candidate observations until separately verified.');
    try {
      const record = await request('/api/adapter-runs/' + plan.id + '/execute', {adapter_id: plan.adapterId, request: plan.request});
      show(record);
      setStatus('Execution completed with a durable receipt. Receipt authority is review metadata, not independent verification.');
    } catch (error) {
      try {
        const record = await request('/api/adapter-runs/' + plan.id);
        show(record);
      } catch (_) {}
      setStatus(error.message, true);
    } finally {
      executing = false;
      byId('adapter-cancel').disabled = true;
      byId('adapter-reset').disabled = false;
    }
  });

  byId('adapter-cancel').addEventListener('click', async () => {
    if (!plan || !executing) return;
    byId('adapter-cancel').disabled = true;
    try {
      await request('/api/adapter-runs/' + plan.id + '/cancel', {});
      setStatus('Cancellation requested. The adapter stops at its next enforced cancellation boundary.');
    } catch (error) {
      setStatus(error.message, true);
    }
  });

  byId('adapter-refresh').addEventListener('click', async () => {
    try {
      const info = await request('/api/adapters');
      const ids = info.adapters.map((item) => item.adapter.id).join(', ');
      setStatus('Reviewed execution registry: ' + ids + '. External scanners are not bundled.');
    } catch (error) {
      setStatus(error.message, true);
    }
  });

  resetPlan();
})();
