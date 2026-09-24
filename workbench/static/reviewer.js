'use strict';
(function installReviewerEvidenceDrilldown() {
  const baseRender = globalThis.render;
  if (typeof baseRender !== 'function') throw new Error('Evidence Workbench renderer unavailable');

  function recordedText(value) {
    return typeof value === 'string' && value.trim() ? value.trim() : null;
  }

  function humanLabel(value) {
    const text = recordedText(value);
    return text ? text.replaceAll('_', ' ') : 'not recorded';
  }

  function confidenceLabel(value) {
    if (typeof value !== 'number' || !Number.isFinite(value) || value < 0 || value > 1) return null;
    return (Math.round(value * 1000) / 10).toFixed(value * 1000 % 10 === 0 ? 0 : 1) + '%';
  }

  function reviewerEvidenceFacts(finding) {
    const item = finding && typeof finding === 'object' ? finding : {};
    const evidence = item.evidence && typeof item.evidence === 'object' && !Array.isArray(item.evidence) ? item.evidence : {};
    const facts = [
      ['Source', recordedText(item.source) || 'not recorded'],
      ['Rule', recordedText(item.rule) || 'not recorded'],
      ['Verification', humanLabel(item.verification)],
    ];
    const confidence = confidenceLabel(item.confidence);
    if (confidence) facts.push(['Confidence', confidence]);
    const externalId = recordedText(item.external_id);
    if (externalId) facts.push(['External ID', externalId]);
    const observedAt = recordedText(item.observed_at);
    if (observedAt) facts.push(['Observed at', observedAt]);

    const evidenceFields = [
      ['Method', 'method'],
      ['HTTP status', 'http_status'],
      ['Scope note', 'scope'],
      ['Environment', 'environment'],
      ['Absent header', 'absent_header'],
      ['Demonstrated impact', 'demonstrated_impact'],
      ['Control status', 'control_status'],
      ['Record status', 'record_status'],
    ];
    evidenceFields.forEach(([label, key]) => {
      const value = evidence[key];
      if ((typeof value === 'string' && value.trim()) || (typeof value === 'number' && Number.isFinite(value))) {
        facts.push([label, String(value).trim()]);
      }
    });
    if (typeof evidence.credentials_sent === 'boolean') facts.push(['Credentials sent', evidence.credentials_sent ? 'yes' : 'no']);
    if (typeof evidence.customer_data_sampled === 'boolean') facts.push(['Customer data sampled', evidence.customer_data_sampled ? 'yes' : 'no']);
    facts.push(['Evidence SHA-256', recordedText(item.evidence_sha256) || 'not recorded']);
    return facts;
  }

  function evidencePanel(finding) {
    const panel = document.createElement('section');
    panel.className = 'reviewer-evidence';
    const heading = document.createElement('h4');
    heading.textContent = 'Reviewer evidence';
    panel.append(heading);
    const list = document.createElement('dl');
    list.className = 'reviewer-facts';
    reviewerEvidenceFacts(finding).forEach(([label, value]) => {
      const term = document.createElement('dt');
      term.textContent = label;
      const description = document.createElement('dd');
      description.textContent = value;
      list.append(term, description);
    });
    panel.append(list);
    const boundary = document.createElement('p');
    boundary.className = 'reviewer-boundary';
    boundary.textContent = 'Structured fields summarize recorded report evidence only. Raw evidence below remains authoritative for review.';
    panel.append(boundary);
    return panel;
  }

  function enhanceReviewerEvidence(report) {
    if (!report || !Array.isArray(report.findings)) return;
    const cards = Array.from(document.querySelectorAll('#findings .finding'));
    cards.forEach((card, index) => {
      const finding = report.findings[index];
      if (!finding || card.querySelector('.reviewer-evidence')) return;
      const panel = evidencePanel(finding);
      const rawEvidence = card.querySelector('pre');
      card.insertBefore(panel, rawEvidence || null);
    });
  }

  globalThis.reviewerEvidenceFacts = reviewerEvidenceFacts;
  globalThis.render = function renderWithReviewerEvidence(report) {
    baseRender(report);
    enhanceReviewerEvidence(report);
  };
})();
