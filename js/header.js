/* =====================================================================
   Main Navigation Header / Top Bar
   ---------------------------------------------------------------------
   Centred brand logo, utility icons on the right (search, account,
   currency, cart), centred category nav beneath, and the mobile drawer
   that replaces all of it below 860px.

   Progressive enhancement: the header is fully navigable and the links
   all work before this file loads. What JS adds is the search sheet,
   the currency popover, the drawer animation, and marking the current
   page. The cart lives in cart.js.
   ===================================================================== */

(function () {
  'use strict';

  const $  = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.prototype.slice.call((r || document).querySelectorAll(s));
  const on = (el, ev, fn, o) => el && el.addEventListener(ev, fn, o);

  /* ------------------------------------------------------------ icons */
  const ICON = {
    search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    user:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4.5 20.5a7.5 7.5 0 0 1 15 0"/></svg>',
    bag:    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 8h14l-1 12H6L5 8Z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>',
    phone:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3h3l2 5-2.5 1.5a12 12 0 0 0 6 6L16 13l5 2v3a2 2 0 0 1-2.2 2A17 17 0 0 1 4 6.2 2 2 0 0 1 6 3Z"/></svg>',
    pin:    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s7-5.5 7-11a7 7 0 1 0-14 0c0 5.5 7 11 7 11Z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    clock:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5.5l3.5 2"/></svg>',
    mail:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6.5 8.5 6 8.5-6"/></svg>',
    check:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" class="tick" aria-hidden="true"><path d="m4 12.5 5.5 5.5L20 6.5"/></svg>',
    x:      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" aria-hidden="true"><path d="M5 5l14 14M19 5 5 19"/></svg>'
  };

  /* ------------------------------------------------------- utilities */
  /* One open overlay at a time. Each returns a closer. */
  const FOCUSABLE = 'a[href],button:not([disabled]),input,textarea,select,[tabindex]:not([tabindex="-1"])';
  let closer = null;

  function closeAll() { if (closer) { const c = closer; closer = null; c(); } }

  /* Traps Tab inside a panel and returns the function that tears it down.
     The returned closer MUST also close the panel: closeAll() invokes it,
     so if it only restored focus, Escape would leave the sheet open and
     detach its own keydown handler so Escape could never close it again. */
  function trap(panel, closeFn, trigger) {
    function key(e) {
      if (e.key === 'Escape') { e.preventDefault(); closeAll(); return; }
      if (e.key !== 'Tab') return;
      const f = $$(FOCUSABLE, panel).filter(el => el.offsetParent !== null);
      if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
    panel.addEventListener('keydown', key);
    return function close() {
      panel.removeEventListener('keydown', key);
      closeFn();
      if (trigger) trigger.focus();
    };
  }

  function lockScroll(on) {
    // Compensate for the disappearing scrollbar so the page doesn't jump.
    const w = window.innerWidth - document.documentElement.clientWidth;
    if (on && w > 0) document.body.style.paddingRight = w + 'px';
    else document.body.style.paddingRight = '';
    document.body.style.overflow = on ? 'hidden' : '';
  }

  /* -------------------------------------------------- current section */
  /* With one page there is no "current page", so instead the section you
     are reading is marked. The nav is duplicated across the topbar and the
     mobile drawer, so both copies of the matching link are marked. */
  function markCurrent() {
    // Measure the header so scroll-margin-top can clear it exactly.
    const hdr = document.querySelector('.site-hdr');
    const measure = () => {
      if (hdr) document.documentElement.style
        .setProperty('--hdr-h', Math.round(hdr.getBoundingClientRect().height) + 'px');
    };
    measure();
    addEventListener('resize', measure, { passive: true });

    const links = $$('[data-nav="section"]');
    if (!links.length) return;
    links.forEach(a => a.removeAttribute('aria-current'));

    const byId = {};
    links.forEach(a => {
      const id = a.getAttribute('href').slice(1);
      (byId[id] = byId[id] || []).push(a);
    });

    const mark = id => {
      // clear every copy first, then mark all of them: the nav is rendered
      // twice, and marking only one copy leaves the visible one unhighlighted
      links.forEach(a => a.removeAttribute('aria-current'));
      if (id && byId[id]) byId[id].forEach(a => a.setAttribute('aria-current', 'true'));
    };

    // The current section is the last one whose top has passed a line a
    // little below the sticky header. This is derived from scroll position
    // rather than from an IntersectionObserver because a section shorter
    // than the viewport can never be "intersecting" in any useful sense:
    // #about is 85px tall, so a band-based observer skipped straight over
    // it and highlighted Contact while About was the thing on screen.
    const line = () => window.innerHeight * 0.3 + window.scrollY;

    const pick = () => {
      const y = line();
      let id = null;
      for (const k of Object.keys(byId)) {
        const el = document.getElementById(k);
        if (!el) continue;
        if (el.getBoundingClientRect().top + window.scrollY <= y) id = k;
      }
      mark(id);
    };

    addEventListener('scroll', pick, { passive: true });
    addEventListener('hashchange', pick);
    addEventListener('resize', pick, { passive: true });
    pick();
  }

  /* ---------------------------------------------------- search sheet */
  function initSearch() {
    const sheet = $('#searchSheet');
    if (!sheet) return;
    const input = $('#searchInput');
    const results = $('#searchResults');
    const hint = $('#searchHint');
    const trg = $('[data-open="search"]');

    function index() {
      return $$('[data-item]').map(el => ({
        name: el.dataset.item,
        price: parseInt(el.dataset.price, 10) || 0,
        cat: el.dataset.cat || '',
        href: '#' + (el.id || '')
      }));
    }

    function chips() {
      const hot = index().slice(0, 6);
      if (!hot.length) return;
      hint.hidden = false;
      hint.innerHTML = 'Popular right now';
      results.innerHTML = '<div class="chips">' + hot.map(it =>
        '<a class="chip" href="' + it.href + '">' + it.name + '</a>'
      ).join('') + '</div>';
    }

    function esc(s) {
      return s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    }

    function mark(text, q) {
      const i = text.toLowerCase().indexOf(q);
      if (i < 0) return esc(text);
      return esc(text.slice(0, i)) + '<mark>' + esc(text.slice(i, i + q.length)) + '</mark>' + esc(text.slice(i + q.length));
    }

    function run() {
      const q = input.value.trim().toLowerCase();
      if (!q) { chips(); return; }
      const hits = index().filter(it =>
        it.name.toLowerCase().includes(q) || it.cat.toLowerCase().includes(q)
      );
      if (!hits.length) {
        hint.hidden = true;
        results.innerHTML = '<p class="result-empty">Nothing matches &ldquo;' + esc(input.value.trim()) +
          '&rdquo;.<br>The menu is still placeholder text, so try a broad word like <em>chicken</em>.</p>';
        return;
      }
      hint.hidden = true;
      results.innerHTML = hits.map(it =>
        '<a class="result" href="' + it.href + '">' +
          '<span class="result-txt">' +
            '<span class="result-name">' + mark(it.name, q) + '</span>' +
            '<span class="result-meta">' + esc(it.cat) + '</span>' +
          '</span>' +
          '<span class="result-price">' + window.MONEY.format(it.price) + '</span>' +
        '</a>'
      ).join('');
    }

    function open() {
      closeAll();
      sheet.classList.add('open');
      sheet.removeAttribute('inert');
      $$('.scrim').forEach(s => { if (s.id !== 'mobScrim') s.classList.add('open'); });
      lockScroll(true);
      chips();
      closer = trap(sheet, close, trg);
      setTimeout(() => input && input.focus(), 260);
    }

    function close() {
      sheet.classList.add('closing');
      sheet.classList.remove('open');
      sheet.setAttribute('inert', '');
      $$('.scrim').forEach(s => { if (s.id !== 'mobScrim') s.classList.remove('open'); });
      lockScroll(false);
      sheet.classList.remove('closing');
    }

    on(trg, 'click', open);
    // Scoped to this sheet: a global [data-close] selector would also bind
    // the account sheet's close button and fire two handlers for one click.
    $$('[data-close]', sheet).forEach(b => on(b, 'click', close));
    on(input, 'input', run);
    on(input, 'keydown', e => { if (e.key === 'Enter' && $('.result', results)) $('.result', results).click(); });
    on($('#searchClose'), 'click', close);
    on($('#sheetScrim'), 'click', close);
    // Clear the field when the sheet is dismissed, so it reopens fresh.
    sheet.addEventListener('transitionend', e => {
      if (e.propertyName === 'transform' && !sheet.classList.contains('open')) input.value = '';
    });
  }

  /* ------------------------------------------------ currency popover */
  function initCurrency() {
    const pop = $('#curPop');
    if (!pop) return;
    const trg = $('[data-open="currency"]');
    const lbl = $('#curLabel');
    const list = $('#curList');
    const drw = $('#drawerSeg');

    function paint() {
      const cur = window.MONEY.current();
      if (lbl) lbl.textContent = cur;
      if (trg) trg.setAttribute('aria-label', 'Currency: ' + cur + '. Change currency');
      $$('[data-cur]').forEach(b => b.setAttribute('aria-checked', String(b.dataset.cur === cur)));
    }

    function open() {
      closeAll();
      pop.classList.add('open');
      trg.setAttribute('aria-expanded', 'true');
      closer = () => { pop.classList.remove('open'); trg.setAttribute('aria-expanded', 'false'); };
    }

    function toggle() {
      if (pop.classList.contains('open')) closeAll(); else open();
    }

    function choose(cur) {
      window.MONEY.set(cur);
      paint();
      // Anything showing a price needs re-rendering.
      document.dispatchEvent(new CustomEvent('money:change', { detail: { currency: cur } }));
      if (pop.classList.contains('open')) closeAll();
      toast('Prices now in ' + cur);
    }

    // Build the option list from config so adding a currency is one edit.
    list.innerHTML = window.MONEY.options().map(c =>
      '<button type="button" role="menuitemradio" data-cur="' + c + '" aria-checked="false">' +
        '<span>' + c + '</span>' + ICON.check +
      '</button>'
    ).join('');
    if (drw) {
      drw.innerHTML = window.MONEY.options().map(c =>
        '<button type="button" role="radio" data-cur="' + c + '" aria-checked="false">' + c + '</button>'
      ).join('');
    }

    $$('[data-cur]').forEach(b => on(b, 'click', () => choose(b.dataset.cur)));
    on(trg, 'click', toggle);
    on(document, 'click', e => {
      if (pop.classList.contains('open') && !pop.contains(e.target) && !trg.contains(e.target)) closeAll();
    });
    on(trg, 'keydown', e => { if (e.key === 'ArrowDown') { e.preventDefault(); open(); const f = $('[data-cur]', list); f && f.focus(); } });
    on(pop, 'keydown', e => {
      if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;
      e.preventDefault();
      const items = $$('[data-cur]', list);
      const i = items.indexOf(document.activeElement);
      items[(i + (e.key === 'ArrowDown' ? 1 : items.length - 1)) % items.length].focus();
    });

    paint();
  }

  /* ------------------------------------------------- account sheet */
  function initAccount() {
    const sheet = $('#acctSheet');
    if (!sheet) return;
    const trg = $('[data-open="account"]');
    const nameEl = $('#acctName');

    function open() {
      closeAll();
      sheet.classList.add('open');
      sheet.removeAttribute('inert');
      $$('.scrim').forEach(s => { if (s.id !== 'mobScrim') s.classList.add('open'); });
      lockScroll(true);
      closer = trap(sheet, close, trg);
      setTimeout(() => { const i = $('#acctEmail'); i && i.focus(); }, 260);
    }

    function close() {
      sheet.classList.remove('open');
      sheet.setAttribute('inert', '');
      $$('.scrim').forEach(s => { if (s.id !== 'mobScrim') s.classList.remove('open'); });
      lockScroll(false);
    }

    on(trg, 'click', open);
    on($('#acctClose'), 'click', close);
    on($('#acctSubmit'), 'click', e => {
      e.preventDefault();
      const email = $('#acctEmail').value.trim();
      if (!email) { toast('Enter an email address first', true); return; }
      window.ACCOUNT.save(email);
      close();
      toast('Saved on this device only');
    });
    on($('#acctSignOut'), 'click', () => {
      window.ACCOUNT.clear();
      close();
      toast('Cleared');
    });

    function paint() {
      const a = window.ACCOUNT.get();
      if (nameEl) nameEl.textContent = a ? a.email : '';
      if (a) {
        $('#acctForm').hidden = true;
        $('#acctSignedIn').hidden = false;
        $('#acctOrders').innerHTML = window.ACCOUNT.orders().map(o =>
          '<div class="order-row"><span class="order-ref">' + o.ref + '</span>' +
          '<span class="order-when">' + new Date(o.at).toLocaleString() + '</span>' +
          '<span class="line-meta">' + o.items + ' item' + (o.items === 1 ? '' : 's') + '</span></div>'
        ).join('');
      } else {
        $('#acctForm').hidden = false;
        $('#acctSignedIn').hidden = true;
      }
    }

    document.addEventListener('account:change', paint);
    paint();
  }

  /* --------------------------------------------------- mobile drawer */
  function initDrawer() {
    const drawer = $('#drawer');
    const scrim = $('#mobScrim');
    const ham = $('#hamburger');
    if (!drawer || !ham) return;

    function open() {
      closeAll();
      drawer.classList.add('open');
      drawer.removeAttribute('inert');
      scrim.classList.add('open');
      ham.setAttribute('aria-expanded', 'true');
      // Keep the header above the scrim so the toggle stays clickable.
      const r = $('.site-hdr').getBoundingClientRect();
      drawer.style.setProperty('--drawer-top', r.bottom + 'px');
      document.body.style.overflow = 'hidden';
      closer = () => {
        drawer.classList.remove('open');
        drawer.setAttribute('inert', '');
        scrim.classList.remove('open');
        ham.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      };
    }

    function close() { closeAll(); }

    on(ham, 'click', () => drawer.classList.contains('open') ? close() : open());
    on(scrim, 'click', close);
    on($('#drawerClose'), 'click', close);
    $$('a', drawer).forEach(a => on(a, 'click', close));
    on(document, 'keydown', e => { if (e.key === 'Escape' && drawer.classList.contains('open')) close(); });
  }

  /* ------------------------------------------------------------ toast */
  let toastBox;
  window.toast = function (msg, isErr) {
    if (!toastBox) {
      toastBox = document.createElement('div');
      toastBox.className = 'toasts';
      toastBox.setAttribute('role', 'status');
      toastBox.setAttribute('aria-live', 'polite');
      document.body.appendChild(toastBox);
    }
    const t = document.createElement('div');
    t.className = 'toast' + (isErr ? '' : ' toast--ok');
    t.textContent = msg;
    toastBox.appendChild(t);
    setTimeout(() => t.remove(), 2800);
  };

  /* ------------------------------------------------------------- boot */
  function init() {
    markCurrent();
    initSearch();
    initCurrency();
    initAccount();
    initDrawer();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  /* Re-run on view transitions / bfcache restores. */
  on(window, 'pageshow', markCurrent);
})();
