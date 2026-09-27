/* =====================================================================
   Cart — browser-local, PKR-authoritative
   ---------------------------------------------------------------------
   !! NOT A REAL SHOP !!

   There is no Shopify backend, no server and no payment processor. The
   cart is an array in localStorage on the visitor's own device. That
   means:
     - it is not shared between devices or browsers
     - it is not shared between tabs reliably
     - it disappears if site data is cleared
     - the "checkout" button cannot take money
   It exists to demonstrate the header's cart badge, drawer and totals.
   Do not present it as a working storefront.
   ===================================================================== */

(function () {
  'use strict';

  const $  = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.prototype.slice.call((r || document).querySelectorAll(s));
  const on = (el, ev, fn) => el && el.addEventListener(ev, fn);
  const KEY = 'uhcp-cart-v1';

  let items = load();

  function load() {
    try {
      const raw = JSON.parse(localStorage.getItem(KEY) || '[]');
      // Defend against a hand-edited or corrupted value.
      return Array.isArray(raw) ? raw.filter(it =>
        it && typeof it.key === 'string' && Number.isFinite(+it.qty) && +it.qty > 0
      ).map(it => ({ key: it.key, name: String(it.name), pkr: +it.pkr || 0, qty: Math.min(+it.qty, 99) })) : [];
    } catch (e) { return []; }
  }

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(items)); }
    catch (e) { window.toast('Could not save the cart on this device', true); }
    render();
  }

  /* Cross-tab sync: the storage event fires in *other* tabs only. */
  on(window, 'storage', e => { if (e.key === KEY) { items = load(); render(); } });

  function add(key, name, pkr, qty) {
    qty = qty || 1;
    const found = items.find(it => it.key === key);
    if (found) found.qty = Math.min(found.qty + qty, 99);
    else items.push({ key, name, pkr, qty: Math.min(qty, 99) });
    save();
    window.toast('Added to cart');
  }

  function setQty(key, qty) {
    const it = items.find(i => i.key === key);
    if (!it) return;
    if (qty <= 0) items = items.filter(i => i.key !== key);
    else it.qty = Math.min(qty, 99);
    save();
  }

  function remove(key) { items = items.filter(i => i.key !== key); save(); }
  function clear() { items = []; save(); }

  const count = () => items.reduce((n, it) => n + it.qty, 0);
  const subtotal = () => items.reduce((n, it) => n + it.pkr * it.qty, 0);

  function totals() {
    const sub = subtotal();
    const D = window.SITE.delivery;
    const free = sub >= D.freeOver;
    return {
      subtotal: sub,
      delivery: items.length === 0 || free ? 0 : D.fee,
      free,
      total: sub + (items.length === 0 || free ? 0 : D.fee)
    };
  }

  /* --------------------------------------------------------- render */
  function render() {
    const n = count();

    $$('[data-cart-count]').forEach(el => {
      el.textContent = n;
      el.hidden = n === 0;
    });
    $$('[data-cart-fab]').forEach(el => { el.hidden = n === 0; });

    const box = $('#cartItems');
    if (!box) return;

    if (!items.length) {
      box.innerHTML =
        '<div class="cart-empty">' +
          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 8h14l-1 12H6L5 8Z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>' +
          '<p>Your cart is empty.<br><a href="/menu" style="color:var(--accent);font-weight:700">Browse the menu</a></p>' +
        '</div>';
    } else {
      box.innerHTML = items.map(it =>
        '<div class="line" data-key="' + it.key + '">' +
          '<div class="line-body">' +
            '<div class="line-name">' + it.name + '</div>' +
            '<div class="line-meta">' + window.MONEY.format(it.pkr) + ' each</div>' +
            '<div class="line-price" data-line-total="' + it.key + '">' + window.MONEY.format(it.pkr * it.qty) + '</div>' +
          '</div>' +
          '<div class="line-side">' +
            '<div class="stepper">' +
              '<button type="button" data-dec="' + it.key + '" aria-label="One fewer ' + it.name + '">&minus;</button>' +
              '<output aria-label="Quantity of ' + it.name + '">' + it.qty + '</output>' +
              '<button type="button" data-inc="' + it.key + '" aria-label="One more ' + it.name + '">+</button>' +
            '</div>' +
            '<button type="button" class="line-remove" data-rm="' + it.key + '">Remove</button>' +
          '</div>' +
        '</div>'
      ).join('');
    }

    // The stepper/remove listener is bound ONCE in initDrawer, not here.
    // Re-binding inside render() would stack a new listener on every
    // repaint, so a single click on "+" would fire N times.

    paintTotals();
  }

  function paintTotals() {
    const t = totals();
    const set = (sel, v) => { const el = $(sel); if (el) el.textContent = v; };

    set('#sumSub', window.MONEY.format(t.subtotal));
    set('#sumTotal', window.MONEY.format(t.total));
    set('#cartCount', count() + ' item' + (count() === 1 ? '' : 's'));

    const dRow = $('#sumDelivery');
    if (dRow) {
      dRow.hidden = false;
      set('#sumDeliveryVal', t.delivery === 0 ? 'Free' : window.MONEY.format(t.delivery));
    }

    const hint = $('#cartHint');
    if (hint) {
      const D = window.SITE.delivery;
      if (!items.length) hint.textContent = window.SITE.commerce.checkoutNote;
      else if (t.subtotal < D.minOrder) hint.textContent = 'Minimum order is ' + window.MONEY.format(D.minOrder) + '.';
      else if (!t.free) hint.textContent = 'Spend ' + window.MONEY.format(D.freeOver - t.subtotal) + ' more for free delivery.';
      else hint.textContent = window.SITE.commerce.checkoutNote;
    }

    const co = $('#checkoutBtn');
    if (co) {
      const belowMin = t.subtotal < window.SITE.delivery.minOrder;
      co.disabled = !items.length || belowMin;
      co.textContent = belowMin ? 'Below minimum order' : 'Checkout';
      co.title = window.SITE.commerce.checkoutNote;
    }

    // Line totals depend on currency, so repaint them on change.
    items.forEach(it => {
      const el = $('[data-line-total="' + it.key + '"]');
      if (el) el.textContent = window.MONEY.format(it.pkr * it.qty);
    });
  }

  /* ---------------------------------------------------------- drawer */
  function initDrawer() {
    const cart = $('#cart');
    const scrim = $('#cartScrim');
    if (!cart) return;
    let lastFocus = null;

    /* Delegated, bound once, so repainting the list cannot orphan or
       duplicate handlers. */
    const box = $('#cartItems');
    if (box) {
      on(box, 'click', e => {
        const dec = e.target.closest('[data-dec]');
        const inc = e.target.closest('[data-inc]');
        const rm  = e.target.closest('[data-rm]');
        if (!dec && !inc && !rm) return;
        const key = (dec || inc || rm).dataset.dec || (dec || inc || rm).dataset.inc || (dec || inc || rm).dataset.rm;
        const it = items.find(i => i.key === key);
        if (!it) return;
        if (dec) setQty(it.key, it.qty - 1);
        else if (inc) setQty(it.key, it.qty + 1);
        else remove(it.key);
      });
    }

    function open() {
      lastFocus = document.activeElement;
      cart.classList.add('open');
      cart.removeAttribute('inert');
      scrim.classList.add('open');
      document.body.style.overflow = 'hidden';
      const w = window.innerWidth - document.documentElement.clientWidth;
      if (w > 0) document.body.style.paddingRight = w + 'px';
      setTimeout(() => { const f = $('#cartClose'); f && f.focus(); }, 260);
    }
    function close() {
      cart.classList.remove('open');
      cart.setAttribute('inert', '');
      scrim.classList.remove('open');
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
      lastFocus && lastFocus.focus();
    }

    on(cart, 'keydown', e => {
      if (e.key === 'Escape') { close(); return; }
      if (e.key !== 'Tab') return;
      const f = $$('a[href],button:not([disabled]),input,select,textarea,[tabindex]:not([tabindex="-1"])', cart)
        .filter(el => el.offsetParent !== null);
      if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });

    $$('[data-open="cart"]').forEach(b => on(b, 'click', open));
    on(scrim, 'click', close);
    on($('#cartClose'), 'click', close);
    on($('#cartClear'), 'click', () => { if (items.length) { clear(); toast('Cart cleared'); } });
    on($('#checkoutBtn'), 'click', () => window.toast(window.SITE.commerce.checkoutNote, true));
  }

  /* ------------------------------------------------- add-to-cart UI */
  function initButtons() {
    // Any [data-add] inside a [data-item] card, with optional size choice.
    $$('[data-item]').forEach(card => {
      const btn = $('[data-add]', card);
      if (!btn) return;
      on(btn, 'click', () => {
        const sizeEl = $('[data-size].is-on', card);
        const size = sizeEl ? sizeEl.textContent.trim() : '';
        const key = card.id + '::' + size;
        add(key, card.dataset.item + (size ? ' (' + size + ')' : ''), +card.dataset.price, 1);
        btn.classList.add('is-added');
        btn.textContent = 'Added';
        setTimeout(() => { btn.classList.remove('is-added'); btn.textContent = 'Add to cart'; }, 1300);
      });
      $$('[data-size]', card).forEach(s => on(s, 'click', () => {
        $$('[data-size]', card).forEach(x => x.setAttribute('aria-pressed', 'false'));
        s.setAttribute('aria-pressed', 'true');
        s.classList.add('is-on');
      }));
    });

    // Category filters on the menu page.
    const filters = $$('[data-filter]');
    if (!filters.length) return;
    function apply(id) {
      let shown = 0;
      $$('[data-item]').forEach(c => {
        const hit = id === 'all' || c.dataset.cat === id;
        c.classList.toggle('hidden', !hit);
        if (hit) shown++;
      });
      const n = $('#filterCount');
      if (n) n.textContent = shown + (shown === 1 ? ' item' : ' items');
    }
    filters.forEach(f => on(f, 'click', () => {
      filters.forEach(x => x.setAttribute('aria-pressed', 'false'));
      f.setAttribute('aria-pressed', 'true');
      apply(f.dataset.filter);
      if (f.dataset.filter !== 'all') history.replaceState(null, '', '#' + f.dataset.filter);
      else history.replaceState(null, '', location.pathname);
    }));

    // Deep link /menu#beverages should pre-select that filter.
    const h = location.hash.replace('#', '');
    if (h && SITE.categories.some(c => c.id === h)) {
      const f = filters.find(x => x.dataset.filter === h);
      if (f) { f.click(); }
    } else if (filters.length) {
      apply('all');
    }
  }

  /* ----------------------------------------------------------- boot */
  function init() {
    initDrawer();
    initButtons();
    render();
    document.addEventListener('money:change', paintTotals);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  /* Exposed for the console and for tests. */
  window.CART = { add, setQty, remove, clear, count, subtotal, totals, items: () => items.slice() };
})();
