(() => {
  const $ = (id) => document.getElementById(id);
  const token = decodeURIComponent(location.pathname.split('/').filter(Boolean).pop() || '');
  let proposal = null;

  function escapeHtml(value='') {
    return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  function setRecoveryLink(label) {
    const actions = $('hero').querySelector('.hero-actions');
    let link = $('proposalRecoveryLink');
    if (!link) {
      link = document.createElement('a');
      link.id = 'proposalRecoveryLink';
      link.className = 'btn primary';
      link.href = '/carbon/partner';
      actions.appendChild(link);
    }
    link.textContent = label;
  }

  function showUnavailable() {
    // Never disclose quote details for invalid, withdrawn, or unissued links.
    document.querySelectorAll('main.shell > section:not(#hero)').forEach(section => { section.hidden = true; });
    $('businessName').textContent = 'This proposal link is unavailable';
    $('headline').textContent = '';
    $('subhead').textContent = 'The link may be invalid, withdrawn, or no longer available. No quote or customer details are shown here. Visit CARBON° Business to discuss a current offer.';
    $('proposalRef').textContent = '';
    $('countdown').textContent = '';
    $('statusPill').textContent = 'UNAVAILABLE';
    $('statusPill').className = 'pill';
    $('jumpOffer').hidden = true;
    $('fullProposalLink').classList.add('hidden');
    $('hero').querySelector('.eyebrow').textContent = 'CARBON° BUSINESS';
    setRecoveryLink('Visit CARBON° Business');
    document.title = 'CARBON° Business';
  }

  function showExpiredRecovery(p) {
    // Retain history, but do not let an expired quote be mistaken for an operative offer.
    $('jumpOffer').hidden = true;
    $('fullProposalLink').classList.add('hidden');
    const formPanel = $('changeForm').closest('.panel');
    if (formPanel) formPanel.hidden = true;
    $('subhead').textContent = [
      p.subhead || '',
      'This quote has expired and is shown for reference only. It cannot be accepted or changed as a current offer. Request a refreshed quote for current scope, pricing, and validity.'
    ].filter(Boolean).join(' ');
    document.querySelector('.pricebox .label').textContent = 'EXPIRED QUOTE · REFERENCE ONLY';
    const note = $('priceNote').textContent.trim();
    $('priceNote').textContent = [note, 'Not an active offer. Request a refreshed quote.'].filter(Boolean).join(' ');
    setRecoveryLink('Request refreshed quote');
  }

  function statusLabel(p) {
    if (p.quote_status === 'DRAFT_NOT_ISSUED') return ['DRAFT · NOT ISSUED',''];
    if (p.quote_status === 'EXPIRED') return ['QUOTE EXPIRED','warn'];
    if (p.quote_status === 'ACTIVE') return ['QUOTE ACTIVE','good'];
    return [p.quote_status || 'UNKNOWN',''];
  }

  function render(p) {
    if (['DRAFT_NOT_ISSUED', 'REVOKED', 'CANCELLED', 'UNKNOWN'].includes(p.quote_status)) {
      showUnavailable();
      return;
    }
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
    if (p.quote_status === 'EXPIRED') showExpiredRecovery(p);
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
      if (!res.ok) throw new Error('Request could not be completed');
      $('formState').textContent = 'Received by CARBON°. Request reference: ' + body.request_id + '. This does not alter or accept the quote automatically.';
      $('changeMessage').value = '';
    } catch (err) {
      $('formState').textContent = 'Could not submit right now. Visit CARBON° Business to request help or a current offer.';
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
    .catch(showUnavailable);
})();