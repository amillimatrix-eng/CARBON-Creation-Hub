(() => {
  'use strict';
  const API = String(window.AMX_API_BASE || '').replace(/\/$/, '');
  const $ = (id) => document.getElementById(id);
  const esc = (v) => String(v ?? '');
  const fmt = (v) => v ? new Date(v).toLocaleString() : 'UNKNOWN';
  const T10_FIELDS = ['T10_JOB','T10_ACTUAL','T10_EVIDENCE','T10_CHANGE','T10_REMAINING_GAP','T10_PASS'];

  async function request(path, options = {}, timeout = 35000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);
    try {
      const response = await fetch(API + path, {...options, signal: controller.signal});
      if (!response.ok) throw new Error('HTTP ' + String(response.status));
      return await response.json();
    } finally {
      clearTimeout(timer);
    }
  }

  function setBackend(state, meta) {
    const pill = $('backendPill');
    pill.dataset.state = state;
    pill.querySelector('b').textContent = state;
    $('backendMeta').textContent = meta || 'backend';
  }

  function appendRows(dl, rows) {
    rows.forEach(([k,v]) => {
      if (!v) return;
      const dt=document.createElement('dt'); dt.textContent=k;
      const dd=document.createElement('dd'); dd.textContent=esc(v);
      dl.append(dt,dd);
    });
  }

  function t10Rows(r) {
    return T10_FIELDS.map(k => [k.replaceAll('_',' '), r?.[k] || 'MISSING / UNKNOWN-HOLD']);
  }

  function t10Node(title, packet) {
    const e=document.createElement('article'); e.className='record';
    const top=document.createElement('div'); top.className='record-top';
    const h=document.createElement('h3'); h.textContent=esc(title);
    const status=document.createElement('small'); status.textContent=esc(packet?.T10_PASS || 'UNKNOWN');
    top.append(h,status); e.append(top);
    const dl=document.createElement('dl'); appendRows(dl,t10Rows(packet || {})); e.append(dl);
    return e;
  }

  function recordNode(r) {
    const el = document.createElement('article');
    el.className = 'record';
    const top = document.createElement('div'); top.className = 'record-top';
    const h = document.createElement('h3'); h.textContent = esc(r.evidence_id) + ' — ' + esc(r.capability);
    const status = document.createElement('small'); status.textContent = esc(r.status_freshness || 'UNKNOWN') + ' · T10 ' + esc(r.T10_PASS || 'UNKNOWN');
    top.append(h, status); el.append(top);
    const p = document.createElement('p'); p.textContent = esc(r.interview_safe_explanation || 'No explanation recorded.'); el.append(p);
    const dl = document.createElement('dl');
    appendRows(dl, [
      ['Artifact', r.artifact], ['Role', r.role_contribution], ['Acceptance', r.acceptance_test],
      ['Source', r.authoritative_source], ['Receipts', (r.durable_receipts || []).join(' · ') || r.durable_receipt],
      ['Inspect', r.inspect_route], ['Version', r.date_version],
      ...t10Rows(r)
    ]);
    el.append(dl); return el;
  }

  function renderEvidence(records) {
    const box = $('recordsList'); box.innerHTML = '';
    $('evidenceCount').textContent = String(records.length) + ' governed record' + (records.length === 1 ? '' : 's') + ' loaded.';
    if (!records.length) { box.innerHTML = '<div class="empty">No governed evidence is available.</div>'; return; }
    records.forEach(r => box.append(recordNode(r)));
  }

  function renderGallery(records) {
    const box = $('galleryCards'); box.innerHTML='';
    if (!records.length) { box.innerHTML='<div class="empty">No gallery-ready evidence is currently projected.</div>'; return; }
    records.forEach(r => {
      const a=document.createElement('article');a.className='card';
      const label=document.createElement('p');label.className='eyebrow';label.textContent=esc(r.evidence_id);
      const h=document.createElement('h3');h.textContent=esc(r.artifact || r.capability);
      const p=document.createElement('p');p.textContent=esc(r.interview_safe_explanation);
      const meta=document.createElement('div');meta.className='meta';
      [r.status_freshness,r.date_version,r.visibility,'T10 ' + (r.T10_PASS || 'UNKNOWN')].filter(Boolean).forEach(x=>{const s=document.createElement('span');s.textContent=esc(x);meta.append(s)});
      a.append(label,h,p,meta); box.append(a);
    });
  }

  function renderT10(meta, op) {
    const coverage=meta?.coverage || {};
    const total=coverage.total_records ?? 0;
    const complete=coverage.complete_records ?? 0;
    const ok=Boolean(coverage.coverage_complete);
    $('t10Coverage').textContent = ok ? 'COMPLETE' : 'HOLD';
    $('t10CoverageMeta').textContent = complete + '/' + total + ' evidence record(s) carry all six T10 fields.';
    const box=$('t10System'); box.innerHTML='';
    box.append(t10Node('Evidence House operator projection', op?.t10 || {}));
    box.append(t10Node('Matrix truth-screen propagation', op?.system_truth_t10 || {}));
    if (!ok) {
      const e=document.createElement('article'); e.className='record';
      const h=document.createElement('h3'); h.textContent='T10 evidence coverage · HOLD';
      const p=document.createElement('p'); p.textContent='Missing native T10 fields: ' + esc(JSON.stringify(coverage.missing_records || {}));
      e.append(h,p); box.append(e);
    }
  }

  function renderTruth(op) {
    const truth = op.system_truth || {};
    const workers = $('workerProofList'); workers.innerHTML = '';
    const workerItems = truth.workers || [];
    if (!workerItems.length) {
      workers.innerHTML='<div class="empty">No current worker-proof snapshot recovered.</div>';
    } else {
      workerItems.forEach(w => {
        const e=document.createElement('article');e.className='record';
        const h=document.createElement('h3');h.textContent=esc(w.name) + ' · ' + esc(w.state || 'UNKNOWN');
        const p=document.createElement('p');
        p.textContent=w.useful_work_proven_this_wake ? 'Useful consequential work is evidenced for the source proof window.' : 'Current useful work is NOT proven by a consequential receipt.';
        const s=document.createElement('small');s.textContent=w.last_scheduler_wake ? 'Last scheduler wake: ' + fmt(w.last_scheduler_wake) : 'No scheduler wake proven.';
        e.append(h,p,s);workers.append(e);
      });
    }
    const tools = $('toolProofList'); tools.innerHTML = '';
    const surfaces = truth.surfaces || [];
    if (!surfaces.length) {
      tools.innerHTML='<div class="empty">No current tool-surface snapshot recovered.</div>';
    } else {
      surfaces.forEach(t => {
        const e=document.createElement('article');e.className='record';
        const h=document.createElement('h3');h.textContent=esc(t.name) + ' · ' + esc(t.state || 'UNKNOWN');
        const p=document.createElement('p');p.textContent=esc(t.evidence || 'No evidence note recorded.');
        e.append(h,p);tools.append(e);
      });
    }
    const alerts = $('truthAlerts'); alerts.innerHTML = '';
    const alertItems = truth.alerts || [];
    if (!alertItems.length) {
      alerts.innerHTML='<div class="empty">No active truth-screen alerts.</div>';
    } else {
      alertItems.forEach(a => {
        const e=document.createElement('article');e.className='record';
        const h=document.createElement('h3');h.textContent=esc(a.severity) + ' · ' + esc(a.id) + ' · ' + esc(a.state);
        const p=document.createElement('p');p.textContent=esc(a.next || 'No next action recorded.');
        e.append(h,p);alerts.append(e);
      });
    }
    $('truthGeneratedAt').textContent = truth.generated_at ? 'Truth snapshot: ' + fmt(truth.generated_at) : 'Truth snapshot timestamp unavailable.';
  }

  function renderOperator(op) {
    renderTruth(op);
    const worker = op.worker || {};
    $('engineState').textContent = esc(worker.display_state || 'UNKNOWN');
    $('engineAcceptance').textContent = esc(worker.acceptance_state || worker.execution_truth || 'UNKNOWN');
    const opportunities = op.opportunities || {};
    $('ledgerCount').textContent = esc(opportunities.total_records ?? '—');
    $('ledgerMeta').textContent = Object.entries(opportunities.state_counts || {}).map(([k,v])=>k + ' ' + v).join(' · ') || 'opportunities';
    $('claimCount').textContent = esc((op.routing || {}).claim_count ?? '—');
    const rails = op.payment_rails || {};
    $('railState').textContent = esc(rails.inventory_completeness || 'UNKNOWN');
    $('railMeta').textContent = String((rails.rails || []).length) + ' recovered rail record(s)';
    $('revenueState').textContent = opportunities.realized_revenue_evidence?.present ? 'EVIDENCED PAID' : 'UNPROVEN / $0 CLAIMED';
    const due = $('dueList'); due.innerHTML='';
    const items = opportunities.due_or_actionable || [];
    if (!items.length) { due.innerHTML='<div class="empty">No due/actionable records projected from current durable state.</div>'; return; }
    items.forEach(x=>{const e=document.createElement('article');e.className='record';const h=document.createElement('h3');h.textContent=esc(x.organization) + ' · ' + esc(x.state);const p=document.createElement('p');p.textContent=esc(x.next_action || 'No next action recorded.');const s=document.createElement('small');s.textContent=x.due_at?'Due ' + fmt(x.due_at):'No due time';e.append(h,p,s);due.append(e)});
  }

  async function loadBootstrap() {
    setBackend('VERIFYING','backend');
    try {
      const d = await request('/api/house/bootstrap', {cache:'no-store'}, 70000);
      setBackend(d.backend?.status || 'CONNECTED', d.backend?.state_source || 'backend');
      $('stateSource').textContent = esc(d.backend?.state_source || 'UNKNOWN');
      $('freshness').textContent = 'Last successful read: ' + fmt(d.backend?.refreshed_at);
      renderEvidence(d.evidence?.records || []);
      renderGallery(d.gallery || []);
      renderOperator(d.operator || {});
      renderT10(d.t10 || {}, d.operator || {});
    } catch (err) {
      setBackend('DISCONNECTED','no false fallback');
      $('stateSource').textContent='UNAVAILABLE';
      $('freshness').textContent='Backend unavailable. No cached operational claims are being presented as live.';
      $('recordsList').innerHTML='<div class="empty error">Governed evidence unavailable from this backend. UNKNOWN/HOLD.</div>';
      $('galleryCards').innerHTML='<div class="empty error">Gallery evidence unavailable; protected assets and claims were not guessed.</div>';
      $('engineState').textContent='UNKNOWN'; $('engineAcceptance').textContent='Backend unavailable';
      $('ledgerCount').textContent='—'; $('claimCount').textContent='—'; $('railState').textContent='UNKNOWN'; $('revenueState').textContent='UNPROVEN';
      $('t10Coverage').textContent='UNKNOWN'; $('t10CoverageMeta').textContent='Backend unavailable; T10 coverage not inferred.';
      $('t10System').innerHTML='<div class="empty error">T10 projection unavailable. UNKNOWN/HOLD.</div>';
      $('dueList').innerHTML='<div class="empty error">Operator state unavailable.</div>';
      $('workerProofList').innerHTML='<div class="empty error">Worker proof unavailable.</div>';
      $('toolProofList').innerHTML='<div class="empty error">Tool proof unavailable.</div>';
      $('truthAlerts').innerHTML='<div class="empty error">Truth alerts unavailable.</div>';
      $('truthGeneratedAt').textContent='Truth snapshot unavailable.';
    }
  }

  $('evidenceSearch').addEventListener('submit', async (event) => {
    event.preventDefault();
    const query = $('evidenceQuery').value.trim(); if (!query) return;
    const button = event.currentTarget.querySelector('button');
    if (button.disabled) return;
    button.disabled = true;
    $('evidenceSearch').setAttribute('aria-busy', 'true');
    const state=$('searchState'), box=$('searchResults'); state.textContent='SEARCHING LOCAL GOVERNED EVIDENCE…'; box.innerHTML='';
    try {
      const d=await request('/api/evidence/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query,limit:8})});
      state.textContent=d.supported?String(d.count) + ' evidence match(es) · ' + esc(d.retrieval):esc(d.gap||'No governed evidence matched.');
      if(!d.results?.length){box.innerHTML='<div class="empty">No evidence supports this query. The House will not fabricate an answer.</div>';return;}
      d.results.forEach(x=>box.append(recordNode(x)));
    } catch(err) { state.textContent='SEARCH DEGRADED'; box.innerHTML='<div class="empty error">Evidence search backend unavailable. No answer inferred.</div>'; }
    finally { button.disabled = false; $('evidenceSearch').removeAttribute('aria-busy'); }
  });

  loadBootstrap();
})();
