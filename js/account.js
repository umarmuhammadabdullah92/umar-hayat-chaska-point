/* The saved email for the account sheet, kept in localStorage because this
   is a static site with no backend: it remembers an address on one device
   and nothing leaves the browser. Nothing here is an order, and nothing
   here is an account in any real sense.

   This lives in its own file, loaded before header.js, because header.js
   reads window.ACCOUNT while painting the sheet at startup. It used to be
   defined at the bottom of cart.js, which loads after header.js, so that
   read threw a TypeError on every page load. A shared module has to be
   defined before its consumers, not inside a later feature file. */
(function () {
  const K = 'uhcp-account-v1';
  const get = () => { try { return JSON.parse(localStorage.getItem(K) || 'null'); } catch (e) { return null; } };
  window.ACCOUNT = {
    get,
    save(email) {
      try { localStorage.setItem(K, JSON.stringify({ email, at: Date.now() })); }
      catch (e) {}
      document.dispatchEvent(new CustomEvent('account:change'));
    },
    clear() { try { localStorage.removeItem(K); } catch (e) {} document.dispatchEvent(new CustomEvent('account:change')); },
    orders() { const a = get(); return a && a.orders ? a.orders : []; }
  };
})();
