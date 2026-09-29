/* =====================================================================
   Online ordering
   ---------------------------------------------------------------------
   There is no server, so nothing here sells anything. What it does is
   add up the quantities picked on the menu, write them out as a message,
   and hand the guest to WhatsApp, where a person at the restaurant
   actually sees it. That is the same honest hand-off as a reservation,
   and it works for the same reason: a page that quietly drops an order
   is worse than one that hands it straight to the counter.

   Nothing is stored. No cookies, no localStorage, no network request
   except the WhatsApp link the guest opens. The menu does not depend on
   this file: without it the steppers are hidden by css/style.css and the
   fine print sends the guest to the phone instead.
   ===================================================================== */

(function () {
  'use strict';

  const $  = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.prototype.slice.call((r || document).querySelectorAll(s));
  const on = (el, ev, fn) => el && el.addEventListener(ev, fn);

  function init() {
    const bar = $('#orderBar');
    if (!bar || !window.SITE) return;

    const count = $('#orderCount');
    const total = $('#orderTotal');
    const send = $('#orderSend');
    const clear = $('#orderClear');
    const symbol = (window.SITE.currency && window.SITE.currency.symbol) || 'PKR';

    /* The order is a map of dish name to quantity. Prices are read from
       the row on the page -- the same number the guest is looking at --
       rather than fetched from anywhere else, so the basket can never
       quote a price different from the menu. */
    const qty = new Map();
    const price = {};
    $$('.dish').forEach(d => {
      qty.set(d.dataset.item, 0);
      price[d.dataset.item] = +d.dataset.price;
    });

    /* Shown on screen and in the message. En-US grouping matches the
       thousands separator build.py uses when it prints the menu. */
    function money(v) {
      return symbol + ' ' + v.toLocaleString('en-US');
    }

    function refresh() {
      let units = 0, sum = 0;
      $$('.qty').forEach(group => {
        const name = group.closest('.dish').dataset.item;
        const amt = qty.get(name) || 0;
        units += amt;
        sum += amt * (price[name] || 0);
        group.querySelector('[data-qty-n]').textContent = amt;
        group.querySelector('[data-qty-sub]').disabled = amt === 0;
        group.querySelector('[data-qty-add]').disabled = amt >= 99;
      });
      if (count) count.textContent = units + (units === 1 ? ' item' : ' items');
      if (total) total.textContent = money(sum);
      bar.hidden = units === 0;
      if (send) send.disabled = units === 0;
    }

    $$('.qty').forEach(group => {
      const name = group.closest('.dish').dataset.item;
      on(group.querySelector('[data-qty-add]'), 'click', () => {
        qty.set(name, (qty.get(name) || 0) + 1);
        refresh();
      });
      on(group.querySelector('[data-qty-sub]'), 'click', () => {
        qty.set(name, Math.max(0, (qty.get(name) || 0) - 1));
        refresh();
      });
    });

    on(clear, 'click', () => {
      qty.forEach((val, name) => qty.set(name, 0));
      refresh();
    });

    on(send, 'click', () => {
      const lines = ['Hello ' + window.SITE.name + '.', '', 'I would like to order:', ''];
      let sum = 0;
      qty.forEach((amt, name) => {
        if (amt <= 0) return;
        const line = amt * (price[name] || 0);
        sum += line;
        lines.push(amt + ' \u00d7 ' + name + ' \u2014 ' + money(line));
      });
      if (sum <= 0) return;
      lines.push('', 'Total: ' + money(sum));
      lines.push('', 'Sent from the website.');

      const url = 'https://wa.me/' + window.SITE.whatsapp +
        '?text=' + encodeURIComponent(lines.join('\n'));
      const w = window.open(url, '_blank', 'noopener');
      window.toast(w ? 'Opening WhatsApp with your order'
                     : 'Your order is ready to send on WhatsApp');
    });

    refresh();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();