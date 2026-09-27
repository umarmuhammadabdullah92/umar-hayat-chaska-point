/* =====================================================================
   Menu: category filter
   ---------------------------------------------------------------------
   Filtering is a progressive enhancement in both directions. Without
   this file every category is on screen at once, which is a complete
   and perfectly usable menu. With it, the buttons narrow the view.
   ===================================================================== */

(function () {
  'use strict';

  const $  = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.prototype.slice.call((r || document).querySelectorAll(s));
  const on = (el, ev, fn) => el && el.addEventListener(ev, fn);

  function init() {
    const filters = $$('[data-filter]');
    const cats = $$('.cat');
    if (!filters.length || !cats.length) return;

    const count = $('#filterCount');
    const known = cats.map(c => c.id);

    function apply(id) {
      let shown = 0;
      cats.forEach(cat => {
        /* Hiding the whole category block rather than the individual rows:
           the heading and its note describe the category, so leaving them
           above an empty gap would be worse than hiding all three. */
        const hit = id === 'all' || cat.id === id;
        cat.hidden = !hit;
        if (hit) shown += $$('.dish', cat).length;
      });
      if (count) count.textContent = shown + (shown === 1 ? ' dish' : ' dishes');
    }

    /* One place decides which filter is on, so the pressed state of the
       buttons and what is actually on screen cannot drift apart. */
    function pick(id, record) {
      const want = (id === 'all' || known.indexOf(id) > -1) ? id : 'all';
      filters.forEach(x => x.setAttribute('aria-pressed',
        x.dataset.filter === want ? 'true' : 'false'));
      apply(want);
      /* A category deep link, so a filter can be shared or bookmarked.
         The page URL is the real URL; this only records which category
         the guest is looking at. replaceState rather than a new entry,
         so filtering does not fill the back button with filters. */
      if (record && history.replaceState) {
        history.replaceState(null, '', location.pathname + (want === 'all' ? '' : '#' + want));
      }
      return want;
    }

    filters.forEach(f => on(f, 'click', () => pick(f.dataset.filter, true)));

    /* Deep link: /menu#barbecue opens the menu already filtered. The nav
       marks the menu page from the server, so there is nothing to keep in
       step here beyond the filter itself. */
    pick(location.hash.replace('#', ''), false);

    /* Arriving on a category or a dish while already on the menu is a
       same-document navigation: the page does not reload and none of the
       above runs again. That is how a guest who narrowed the menu and
       then followed a search result would be sent to a dish their own
       filter had hidden, with the link appearing to do nothing at all.
       Opening the category is the fix; the alternative is following the
       guest to an empty screen. */
    on(window, 'hashchange', () => {
      const want = location.hash.replace('#', '');
      if (!want) { pick('all', false); return; }
      if (known.indexOf(want) > -1) { pick(want, false); return; }
      const dish = document.getElementById(want);
      const cat = dish && dish.closest('.cat');
      if (!cat || !cat.hidden) return;
      pick(cat.id, false);
      /* The filter changed the layout after the browser had already
         worked out where to scroll, so the target is found again. */
      requestAnimationFrame(() => {
        const again = document.getElementById(want);
        if (again) again.scrollIntoView({ block: 'center' });
      });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
