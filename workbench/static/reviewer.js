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

  function checkStatus(value) {
    const status = recordedText(value);
    return ['completed', 'inconclusive', 'skipped', 'error'].includes(status) ? status : 'unknown';
  }

  function coverageDetail(check) {
    const item = check && typeof check === 'object' && !Array.isArray(check) ? check : {};
    const details = [];
    const result = recordedText(item.result);
    const reason = recordedText(item.reason);
    if (result) details.push('result ' + humanLabel(result));
    if (reason) details.push('reason ' + reason);
    const coverage = item.coverage && typeof item.coverage === 'object' && !Array.isArray(item.coverage) ? item.coverage : null;
    if (coverage) {
      const tested = coverage.objects_tested;
      const total = coverage.objects_total;
      const validTested = Number.isInteger(tested) && tested >= 0;
      const validTotal = Number.isInteger(total) && total >= 0;
      if (validTested && validTotal) details.push('coverage ' + tested + '/' + total);
      else if (validTested) details.push('objects tested ' + tested);
      else if (validTotal) details.push('objects total ' + total);
      if (Array.isArray(coverage.notes)) {
        const notes = coverage.notes.map(recordedText).filter(Boolean);
        if (notes.length) details.push('notes ' + notes.join(' | '));
      }
    }
    return details;
  }

  function coverageReviewText(report) {
    const checks = report && Array.isArray(report.checks) ? report.checks : [];
    const limitations = report && Array.isArray(report.limitations) ? report.limitations : [];
    const counts = {completed: 0, inconclusive: 0, skipped: 0, error: 0, unknown: 0};
    checks.forEach((check) => { counts[checkStatus(check && check.status)] += 1; });
    const lines = [
      'Coverage review',
      checks.length + ' checks · ' + counts.completed + ' completed · ' + counts.inconclusive + ' inconclusive · ' + counts.skipped + ' skipped · ' + counts.error + ' error · ' + counts.unknown + ' unknown',
      'Reviewer boundary: completed means the check executed; it does not mean the target is safe. Skipped, inconclusive, error and unknown states remain visible coverage gaps.',
    ];
    if (checks.length) {
      lines.push('', 'Checks:');
      checks.forEach((check, index) => {
        const item = check && typeof check === 'object' && !Array.isArray(check) ? check : {};
        const tool = recordedText(item.tool) || 'not recorded';
        const status = checkStatus(item.status);
        const details = coverageDetail(item);
        lines.push((index + 1) + '. ' + tool + ' — ' + status.toUpperCase() + (details.length ? ' · ' + details.join(' · ') : ''));
      });
    } else {
      lines.push('', 'No checks are recorded for this report.');
    }
    if (limitations.length) {
      lines.push('', 'Recorded limitations:');
      limitations.forEach((limitation) => {
        const text = recordedText(limitation);
        if (text) lines.push('- ' + text);
      });
    }
    lines.push('', 'Raw coverage record (authoritative):', JSON.stringify({checks, limitations}, null, 2));
    return lines.join('\n');
  }

  function enhanceCoverageReview(report) {
    if (typeof document.getElementById !== 'function') return;
    const output = document.getElementById('coverage-content');
    if (output) output.textContent = coverageReviewText(report);
  }

  function aiStatus(value) {
    const status = recordedText(value);
    return ['not_requested', 'running', 'completed', 'unavailable', 'cancelled'].includes(status) ? status : 'unknown';
  }

  function processingPolicy(value) {
    const policy = recordedText(value);
    return ['local_only', 'cloud_allowed'].includes(policy) ? policy : 'unknown';
  }

  function executionLocation(value) {
    const location = recordedText(value);
    return ['local_reported', 'cloud_reported'].includes(location) ? location : 'unknown';
  }

  function recordedCount(value) {
    return Number.isInteger(value) && value >= 0 ? String(value) : 'not reported';
  }

  function aiReviewText(report) {
    const ai = report && report.ai && typeof report.ai === 'object' && !Array.isArray(report.ai) ? report.ai : {};
    const usage = ai.usage && typeof ai.usage === 'object' && !Array.isArray(ai.usage) ? ai.usage : {};
    const status = aiStatus(ai.status);
    const requested = status !== 'not_requested';
    const provider = recordedText(ai.provider) || recordedText(usage.provider) || (requested ? 'not recorded' : 'not used');
    const model = recordedText(ai.model) || recordedText(usage.model) || (requested ? 'not recorded' : 'not used');
    const policy = processingPolicy(recordedText(ai.processing_policy) || usage.processing_policy);
    const approvalValue = typeof ai.cloud_processing_approved === 'boolean' ? ai.cloud_processing_approved : usage.cloud_processing_approved;
    const cloudApproval = typeof approvalValue === 'boolean' ? (approvalValue ? 'yes' : 'no') : 'not recorded';
    const location = executionLocation(usage.execution_location);
    const lines = [
      'AI/model review',
      'Status: ' + humanLabel(status).toUpperCase(),
      'Provider: ' + provider,
      'Model: ' + model,
      'Processing policy: ' + humanLabel(policy),
      'Cloud processing approved: ' + cloudApproval,
      'Reported execution location: ' + humanLabel(location),
      'Reviewer boundary: AI interpretation is not evidence and never changes verification, scope, tool authority or approval. Processing approval does not prove where inference actually ran; reported location is daemon metadata, not an egress attestation.',
    ];
    if (status === 'not_requested') {
      lines.push('Inference: not requested; native checks remain deterministic and no alternate provider is substituted.');
    } else {
      lines.push(
        'Inference attempts: ' + recordedCount(usage.inference_attempts),
        'Responses received: ' + recordedCount(usage.responses_received),
        'Prompt tokens reported: ' + recordedCount(usage.prompt_tokens_reported),
        'Output tokens reported: ' + recordedCount(usage.output_tokens_reported),
        'Billing cost: not estimated by the workbench.'
      );
    }
    const errorType = recordedText(ai.error_type);
    if (errorType) lines.push('Recorded error type: ' + errorType);
    const disclosure = recordedText(ai.data_disclosure);
    if (disclosure) lines.push('Recorded data disclosure: ' + disclosure);
    lines.push('', 'Raw AI record (authoritative):', JSON.stringify(ai, null, 2));
    return lines.join('\n');
  }

  function enhanceAiReview(report) {
    if (typeof document.getElementById !== 'function') return;
    const output = document.getElementById('ai-content');
    if (output) output.textContent = aiReviewText(report);
  }

  globalThis.reviewerEvidenceFacts = reviewerEvidenceFacts;
  globalThis.reviewerCoverageText = coverageReviewText;
  globalThis.reviewerAiText = aiReviewText;
  globalThis.render = function renderWithReviewerEvidence(report) {
    baseRender(report);
    enhanceReviewerEvidence(report);
    enhanceCoverageReview(report);
    enhanceAiReview(report);
  };
})();
