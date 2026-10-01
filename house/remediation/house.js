(() => {
  'use strict';
  const API = String(window.AMX_API_BASE || '').replace(/\/$/, '');
  const $ = (id) => document.getElementById(id);
  const esc = (v) => String(v ?? '');
  const fmt = (v) => v ? new Date(v).toLocaleString() : 'UNKNOWN';

  function setBackend(state, meta) {
    const pill = $('backendPill');
    pill.dataset.state = state;
    pill.querySelector('b').textContent = state;
    $('backendMeta').textContent = meta || 'backend';
  }

  function recordNode(r) {
    const el = document.createElement('article');
    el.className = 'record';
    const top = document.createElement('div'); top.className = 'record-top';
    const h = document.createElement('h3'); h.textContent = esc(r.evidence_id) + ' — ' + esc(r.capability);
    const status = document.createElement('small'); status.textContent = esc(r.status_freshness || 'UNKNOWN');
    top.append(h, status); el.append(top);
    const p = document.createElement('p'); p.textContent = esc(r.interview_safe_explanation || 'No explanation recorded.'); el.append(p);
    const dl = document.createElement('dl');
    const rows = [
      ['Artifact', r.artifact], ['Role', r.role_contribution], ['Acceptance', r.acceptance_test],
      ['Source', r.authoritative_source], ['Receipts', (r.durable_receipts || []).join(' · ') || r.durable_receipt],
      ['Inspect', r.inspect_route], ['Version', r.date_version]
    ];
    rows.forEach(([k,v]) => { if (!v) return; const dt=document.createElement('dt');dt.textContent=k;const dd=document.createElement('dd');dd.textContent=esc(v);dl.append(dt,dd); });
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
      [r.status_freshness,r.date_version,r.visibility].filter(Boolean).forEach(x=>{const s=document.createElement('span');s.textContent=esc(x);meta.append(s)});
      a.append(label,h,p,meta); box.append(a);
    });
  }

  function renderOperator(op) {
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
      const r = await fetch(API + '/api/house/bootstrap', {cache:'no-store'});
      if (!r.ok) throw new Error('HTTP ' + String(r.status));
      const d = await r.json();
      setBackend('CONNECTED', d.backend?.state_source || 'backend');
      $('stateSource').textContent = esc(d.backend?.state_source || 'UNKNOWN');
      $('freshness').textContent = 'Last successful read: ' + fmt(d.backend?.refreshed_at);
      renderEvidence(d.evidence?.records || []);
      renderGallery(d.gallery || []);
      renderOperator(d.operator || {});
    } catch (err) {
      setBackend('DISCONNECTED','no false fallback');
      $('stateSource').textContent='UNAVAILABLE';
      $('freshness').textContent='Backend unavailable. No cached operational claims are being presented as live.';
      $('recordsList').innerHTML='<div class="empty error">Governed evidence unavailable from this backend. UNKNOWN/HOLD.</div>';
      $('galleryCards').innerHTML='<div class="empty error">Gallery evidence unavailable; protected assets and claims were not guessed.</div>';
      $('engineState').textContent='UNKNOWN'; $('engineAcceptance').textContent='Backend unavailable';
      $('ledgerCount').textContent='—'; $('claimCount').textContent='—'; $('railState').textContent='UNKNOWN'; $('revenueState').textContent='UNPROVEN';
      $('dueList').innerHTML='<div class="empty error">Operator state unavailable.</div>';
    }
  }

  $('evidenceSearch').addEventListener('submit', async (event) => {
    event.preventDefault();
    const query = $('evidenceQuery').value.trim(); if (!query) return;
    const state=$('searchState'), box=$('searchResults'); state.textContent='SEARCHING LOCAL GOVERNED EVIDENCE…'; box.innerHTML='';
    try {
      const r=await fetch(API + '/api/evidence/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query,limit:8})});
      if(!r.ok) throw new Error('HTTP ' + String(r.status)); const d=await r.json();
      state.textContent=d.supported?String(d.count) + ' evidence match(es) · ' + esc(d.retrieval):esc(d.gap||'No governed evidence matched.');
      if(!d.results?.length){box.innerHTML='<div class="empty">No evidence supports this query. The House will not fabricate an answer.</div>';return;}
      d.results.forEach(x=>box.append(recordNode(x)));
    } catch(err) { state.textContent='SEARCH DEGRADED'; box.innerHTML='<div class="empty error">Evidence search backend unavailable. No answer inferred.</div>'; }
  });

  loadBootstrap();
})();
