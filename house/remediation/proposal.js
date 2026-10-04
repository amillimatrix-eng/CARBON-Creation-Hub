(() => {
  const $ = (id) => document.getElementById(id);
  const token = decodeURIComponent(location.pathname.split('/').filter(Boolean).pop() || '');
  let proposal = null;

  function escapeHtml(value='') {
    return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  function statusLabel(p) {
    if (p.quote_status === 'DRAFT_NOT_ISSUED') return ['DRAFT · NOT ISSUED',''];
    if (p.quote_status === 'EXPIRED') return ['QUOTE EXPIRED','warn'];
    if (p.quote_status === 'ACTIVE') return ['QUOTE ACTIVE','good'];
    return [p.quote_status || 'UNKNOWN',''];
  }

  function render(p) {
    proposal = p;
    document.title = p.business_name + ' × CARBON°';
    $('businessName').textContent = p.business_name + ' × CARBON°';
    $('headline').textContent = p.headline || '';
    $('subhead').textContent = p.subhead || '';
    $('proposalRef').textContent = p.proposal_ref || '';

    const [label, cls] = statusLabel(p);
    $('statusPill').textContent = label;
    $('statusPill').className = 'pill ' + cls;

    if (p.full_proposal_url) {
      $('fullProposalLink').href = p.full_proposal_url;
      $('fullProposalLink').classList.remove('hidden');
    }

    $('visualNote').textContent = p.visual_note || '';
    $('visualStrip').innerHTML = (p.visuals || []).map(v => `
      <article class="visual-card">
        <strong>${escapeHtml(v.title)}</strong>
        <small>${escapeHtml(v.note || '')}</small>
      </article>`).join('');

    $('marketCards').innerHTML = (p.market_context || []).map(m => `
      <article class="market-card">
        <div class="metric">${escapeHtml(m.metric)}</div>
        <p>${escapeHtml(m.context)}</p>
        <a href="${escapeHtml(m.url)}" target="_blank" rel="noopener">View source ↗</a>
      </article>`).join('');

    $('offerTitle').textContent = p.offer?.title || '';
    $('offerSummary').textContent = p.offer?.summary || '';
    $('price').textContent = p.offer?.price_display || 'To confirm';
    $('priceNote').textContent = p.offer?.price_note || '';

    $('included').innerHTML = (p.offer?.included || []).map(i => `
      <div class="include"><strong>${escapeHtml(i.name)}</strong><span>${escapeHtml(i.detail)}</span></div>`).join('');

    $('modules').innerHTML = (p.modules || []).map(m => `
      <label class="module">
        <input type="checkbox" value="${escapeHtml(m.id)}" ${m.selected ? 'checked' : ''}>
        <span><strong>${escapeHtml(m.name)}</strong><small>${escapeHtml(m.description)}</small></span>
      </label>`).join('');

    $('sources').innerHTML = (p.sources || []).map(s => `
      <div class="source">
        <div><strong>${escapeHtml(s.label)}</strong><p>${escapeHtml(s.used_for)}</p></div>
        <a href="${escapeHtml(s.url)}" target="_blank" rel="noopener">Open source ↗</a>
      </div>`).join('');

    startCountdown(p);
  }

  function startCountdown(p) {
    const el = $('countdown');
    if (!p.valid_until || p.quote_status === 'DRAFT_NOT_ISSUED') {
      el.textContent = p.quote_status === 'DRAFT_NOT_ISSUED'
        ? '24h validity begins when issued'
        : '';
      return;
    }
    const expiry = Date.parse(p.valid_until);
    const tick = () => {
      const ms = expiry - Date.now();
      if (ms <= 0) { el.textContent = 'Expired'; return; }
      const h = Math.floor(ms / 3600000);
      const m = Math.floor((ms % 3600000) / 60000);
      el.textContent = `${h}h ${m}m remaining`;
      setTimeout(tick, 30000);
    };
    tick();
  }

  $('jumpOffer').addEventListener('click', () => $('offer').scrollIntoView({behavior:'smooth'}));

  $('changeForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const selected = [...document.querySelectorAll('#modules input:checked')].map(i => i.value);
    const payload = {
      selected_modules: selected,
      message: $('changeMessage').value.trim(),
      contact: $('contact').value.trim(),
      action: 'REQUEST_CHANGE'
    };
    $('submitChange').disabled = true;
    $('formState').textContent = 'Sending…';
    try {
      const res = await fetch('/api/proposals/' + encodeURIComponent(token) + '/request-change', {
        method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)
      });
      const body = await res.json();
      if (!res.ok) throw new Error(body.detail || 'Request failed');
      $('formState').textContent = 'Received by CARBON°. Request reference: ' + body.request_id + '. This does not alter or accept the quote automatically.';
      $('changeMessage').value = '';
    } catch (err) {
      $('formState').textContent = 'Could not submit right now: ' + err.message;
    } finally {
      $('submitChange').disabled = false;
    }
  });

  fetch('/api/proposals/' + encodeURIComponent(token))
    .then(async r => {
      if (!r.ok) throw new Error((await r.json()).detail || 'Proposal unavailable');
      return r.json();
    })
    .then(render)
    .catch(err => {
      $('businessName').textContent = 'Proposal unavailable';
      $('subhead').textContent = err.message;
      $('statusPill').textContent = 'UNAVAILABLE';
    });
})();