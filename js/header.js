/* =====================================================================
   Page chrome: header state, scroll spy, search, drawer, hours,
   scroll reveal and toasts.
   ---------------------------------------------------------------------
   Progressive enhancement. The header, the nav and every section link
   work before this file loads, and the page is navigable with
   JavaScript disabled. What this adds is the search sheet, the drawer
   animation, the current-section marking, the live opening-hours status
   and the reveal transitions. If it never loads, none of that is
   missed: nothing on the page depends on it being visible.
   ===================================================================== */

(function () {
  'use strict';

  const $  = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.prototype.slice.call((r || document).querySelectorAll(s));
  const on = (el, ev, fn, o) => el && el.addEventListener(ev, fn, o);

  const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  /* ------------------------------------------------------------ toast */
  let toastBox;
  window.toast = function (msg) {
    if (!toastBox) {
      toastBox = document.createElement('div');
      toastBox.className = 'toasts';
      toastBox.setAttribute('role', 'status');
      toastBox.setAttribute('aria-live', 'polite');
      document.body.appendChild(toastBox);
    }
    const t = document.createElement('div');
    t.className = 'toast';
    t.textContent = msg;
    toastBox.appendChild(t);
    setTimeout(() => t.remove(), 3000);
  };

  /* --------------------------------------------------------- overlays */
  /* One overlay at a time. Each trap() returns the closer. */
  const FOCUSABLE = 'a[href],button:not([disabled]),input,textarea,select,[tabindex]:not([tabindex="-1"])';
  let closer = null;
  function closeAll() { if (closer) { const c = closer; closer = null; c(); } }

  function lockScroll(on_) {
    // Compensate for the disappearing scrollbar so the page does not jump.
    const w = window.innerWidth - document.documentElement.clientWidth;
    if (on_ && w > 0) document.body.style.paddingRight = w + 'px';
    else document.body.style.paddingRight = '';
    document.body.style.overflow = on_ ? 'hidden' : '';
  }

  /* Traps Tab inside a panel and returns the function that tears it down.
     The returned closer MUST also close the panel: closeAll() invokes it,
     so if it only restored focus, Escape would leave the sheet open with
     its keydown handler detached and no way to close it again. */
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
      if (trigger && document.contains(trigger)) trigger.focus();
    };
  }

  /* ------------------------------------------------------------ header */
  function initHeader() {
    const hdr = $('.site-hdr');
    if (!hdr) return;

    /* --hdr-h drives scroll-padding-top, so a jump to #contact clears
       the bar. Measured rather than guessed, because the header is
       ~118px on a laptop and ~104px on a phone. */
    const measure = () => {
      const h = Math.round(hdr.getBoundingClientRect().height);
      document.documentElement.style.setProperty('--hdr-h', h + 'px');
      hdr.classList.toggle('is-stuck', window.scrollY > 8);
    };
    measure();
    on(window, 'resize', measure, { passive: true });
    on(window, 'scroll', measure, { passive: true });
  }

  /* ---------------------------------------------------- search sheet */
  function initSearch() {
    const sheet = $('#searchSheet');
    if (!sheet) return;
    const input = $('#searchInput');
    const results = $('#searchResults');
    const hint = $('#searchHint');
    const trg = $('[data-open="search"]');

    /* The dish list comes from the JSON island the build inlines into
       every page, not from scraping the DOM. The menu lives on its own
       page now, so scraping would find nothing on the other five and
       search would claim the dish does not exist.

       A result links to the dish on the menu page. Already being on the
       menu page, that is a bare fragment so it jumps instead of
       reloading; anywhere else it is a real navigation. */
    const MENU = '/menu';
    const onMenu = location.pathname.replace(/\.html$/, '') === MENU;

    /* Categories are stored by id, because the id is what the filter
       buttons match on. A guest reading a search result wants the name
       they would see on the menu, not the id behind it. */
    const catLabel = (function () {
      const map = {};
      const cats = window.SITE && window.SITE.categories;
      if (cats) cats.forEach(c => { map[c.id] = c.label; });
      return id => map[id] || id;
    }());

    function index() {
      const el = document.getElementById('menuIndex');
      if (!el) return [];
      let rows;
      try { rows = JSON.parse(el.textContent); } catch (e) { return []; }
      if (!Array.isArray(rows)) return [];
      return rows.map(d => ({
        name: d.name,
        price: d.price,
        cat: d.cat || '',
        href: (onMenu ? '' : MENU) + '#dish-' + d.id
      }));
    }

    function esc(s) {
      return String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    }

    function mark(text, q) {
      const i = text.toLowerCase().indexOf(q);
      if (i < 0) return esc(text);
      return esc(text.slice(0, i)) + '<mark>' + esc(text.slice(i, i + q.length)) + '</mark>' + esc(text.slice(i + q.length));
    }

    function chips() {
      const hot = index().slice(0, 6);
      if (!hot.length) return;
      hint.hidden = false;
      results.innerHTML = '<div class="chips">' + hot.map(it =>
        '<a class="chip" href="' + esc(it.href) + '">' + esc(it.name) + '</a>'
      ).join('') + '</div>';
    }

    function run() {
      const q = input.value.trim().toLowerCase();
      if (!q) { chips(); return; }
      const hits = index().filter(it =>
        it.name.toLowerCase().includes(q) || it.cat.toLowerCase().includes(q)
      );
      if (!hits.length) {
        hint.hidden = true;
        results.innerHTML = '<p class="result-empty">Nothing on the menu matches ' +
          '&ldquo;' + esc(input.value.trim()) + '&rdquo;.</p>';
        return;
      }
      hint.hidden = true;
      results.innerHTML = hits.map(it =>
        '<a class="result" href="' + esc(it.href) + '">' +
          '<span class="result-txt">' +
            '<span class="result-name">' + mark(it.name, q) + '</span>' +
            '<span class="result-meta">' + esc(catLabel(it.cat)) + '</span>' +
          '</span>' +
          '<span class="result-price">' + esc(window.SITE.currency.symbol) + ' ' +
            it.price.toLocaleString('en-US') + '</span>' +
        '</a>'
      ).join('');
    }

    function open() {
      closeAll();
      sheet.classList.add('open');
      sheet.removeAttribute('inert');
      $('#sheetScrim').classList.add('open');
      lockScroll(true);
      chips();
      closer = trap(sheet, close, trg);
      setTimeout(() => input && input.focus(), 280);
    }

    function close() {
      sheet.classList.remove('open');
      sheet.setAttribute('inert', '');
      $('#sheetScrim').classList.remove('open');
      lockScroll(false);
    }

    on(trg, 'click', open);
    // Scoped to this sheet: a global [data-close] selector would also
    // bind the drawer's close button and fire two handlers per click.
    $$('[data-close]', sheet).forEach(b => on(b, 'click', close));
    on(input, 'input', run);
    on(input, 'keydown', e => {
      if (e.key === 'Enter') { const r = $('.result', results); if (r) r.click(); }
    });
    on($('#sheetScrim'), 'click', close);
    // Clear the field when dismissed, so it reopens fresh.
    sheet.addEventListener('transitionend', e => {
      if (e.propertyName === 'transform' && !sheet.classList.contains('open')) input.value = '';
    });
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
      // Keep the header above the scrim so the toggle stays clickable,
      // and hang the drawer off the bottom of it rather than the top of
      // the window, so the bar does not float over the open panel.
      const r = $('.site-hdr').getBoundingClientRect();
      drawer.style.setProperty('--drawer-top', r.bottom + 'px');
      document.body.style.overflow = 'hidden';
      closer = function () {
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
    on(document, 'keydown', e => {
      if (e.key === 'Escape' && drawer.classList.contains('open')) close();
    });
  }

  /* ------------------------------------------------------------ hours */
  /* The rows are rendered at build time, so the hours are there with
     JavaScript off. All this adds is which row is today, and the live
     open/closed state in the hero strip. */
  function toMin(t) {
    const p = String(t).split(':');
    return (+p[0]) * 60 + (+(p[1] || 0));
  }

  function initHours() {
    const hours = (window.SITE && window.SITE.hours) || [];
    if (!hours.length) return;

    const now = new Date();
    const today = now.getDay();
    const mins = now.getHours() * 60 + now.getMinutes();

    /* Rows carry the days they cover in data-days, because the table
       groups consecutive days that share the same hours: "Sunday -
       Friday" is one row, not five. */
    $$('.hours > div[data-days]').forEach(el => {
      const days = (el.dataset.days || '').split(/\s+/).filter(Boolean).map(Number);
      if (days.indexOf(today) !== -1) el.classList.add('is-today');
    });

    const label = $('[data-open-label]');
    const box = label && label.closest('.strip-open');
    if (!label || !box) return;

    const todayHours = hours.filter(h => h.day === today)[0];
    const t = todayHours ? toMin(todayHours.open) : null;
    const c = todayHours ? toMin(todayHours.close) : null;
    const openNow = t != null && c != null &&
      (t <= c ? (mins >= t && mins < c) : (mins >= t || mins < c));

    box.classList.add(openNow ? 'is-open' : 'is-closed');

    if (openNow) {
      label.textContent = 'Open now · closes ' + todayHours.close;
      return;
    }

    /* Closed. Say when it next opens, which is either later today, or
       tomorrow at the earliest hour on any day. */
    const hh = t => String(Math.floor(t / 60)).padStart(2, '0') + ':' + String(t % 60).padStart(2, '0');
    if (todayHours && mins < t) {
      label.textContent = 'Closed · opens today at ' + todayHours.open;
    } else {
      const soonest = hours.reduce(function (a, h) {
        return !a || toMin(h.open) < toMin(a.open) ? h : a;
      }, null);
      label.textContent = 'Closed · opens ' +
        (soonest && soonest.day === (today + 1) % 7 ? 'tomorrow' : DAYS[soonest ? soonest.day : 0]) +
        ' at ' + (soonest ? soonest.open : '11:00');
    }
  }

  /* ----------------------------------------------------------- reveal */
  /* Content starts hidden only when the inline head script has said
     JavaScript is running, so a failed script leaves it visible. */
  function initReveal() {
    const items = $$('[data-reveal]');
    if (!items.length) return;
    if (!('IntersectionObserver' in window) ||
        matchMedia('(prefers-reduced-motion: reduce)').matches) {
      items.forEach(el => el.classList.add('in'));
      return;
    }
    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('in');
        io.unobserve(en.target);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.04 });
    items.forEach(el => io.observe(el));
  }

  /* ------------------------------------------------------------- boot */
  function init() {
    initHeader();
    initSearch();
    initDrawer();
    initHours();
    initReveal();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  /* Re-run the measurement on a bfcache restore, where scrollY is
     already back at its old value before this fires. */
  on(window, 'pageshow', initHeader);
})();
