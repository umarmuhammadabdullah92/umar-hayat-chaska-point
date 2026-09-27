/* =====================================================================
   Money — PKR is the single source of truth
   ---------------------------------------------------------------------
   Prices are authored once, in PKR integers, on the item itself. Every
   display currency is derived from that, so switching currency can
   never desync the cart total from the line items.
   ===================================================================== */

window.MONEY = (function () {
  const C = () => window.SITE.currency;
  const KEY = 'uhcp-currency';

  function load() {
    try {
      const v = localStorage.getItem(KEY);
      return C().rate[v] ? v : C().default;
    } catch (e) { return C().default; }
  }

  function save(cur) {
    try { localStorage.setItem(KEY, cur); } catch (e) {}
  }

  function current() { return load(); }

  /* 1500 PKR -> "$5.40". Accepts a PKR amount, returns a display string. */
  function format(pkr, cur) {
    cur = cur || current();
    const rate = C().rate[cur] || 1;
    const dec = C().decimals[cur] != null ? C().decimals[cur] : 0;
    const value = pkr * rate;
    return C().symbols[cur] + value.toLocaleString('en-US', {
      minimumFractionDigits: dec,
      maximumFractionDigits: dec
    });
  }

  function set(cur) {
    if (C().rate[cur]) { save(cur); return true; }
    return false;
  }

  /* Which currencies the selector offers, in configured order. */
  function options() { return Object.keys(C().rate); }

  return { current, set, format, options, KEY };
})();
