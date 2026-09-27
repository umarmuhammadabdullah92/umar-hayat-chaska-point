/* =====================================================================
   Reservations
   ---------------------------------------------------------------------
   There is no server, so this cannot book anything. What it does is
   validate the request, write it out as a message, and hand the guest
   to WhatsApp, where a person at the restaurant actually sees it. That
   is the honest version of a booking form on a static site: the
   alternative is a form that looks like it books a table and silently
   drops it.

   Nothing is stored. No cookies, no localStorage, no network request
   except the WhatsApp link the guest clicks.
   ===================================================================== */

(function () {
  'use strict';

  const $  = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.prototype.slice.call((r || document).querySelectorAll(s));
  const on = (el, ev, fn) => el && el.addEventListener(ev, fn);

  const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  function toMin(t) {
    const p = String(t).split(':');
    return (+p[0]) * 60 + (+(p[1] || 0));
  }

  function iso(d) {
    return d.getFullYear() + '-' +
      String(d.getMonth() + 1).padStart(2, '0') + '-' +
      String(d.getDate()).padStart(2, '0');
  }

  function longDate(yyyyMmDd) {
    const d = new Date(yyyyMmDd + 'T00:00:00');
    if (isNaN(d)) return yyyyMmDd;
    return d.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' });
  }

  function init() {
    const form = $('#resForm');
    if (!form || !window.SITE) return;
    const R = window.SITE.reservations;

    const done = $('#resDone');
    const doneLink = $('#resDoneLink');
    const again = $('#resAgain');
    const dateEl = $('#rDate');
    const partyEl = $('#rParty');
    const hint = $('#rPartyHint');

    /* ---------------------------------------------------------- setup */
    /* The date field is bounded to the window the restaurant actually
       takes requests for, so the browser's own picker never offers a
       date that cannot be honoured. */
    const today = new Date();
    const last = new Date(today.getFullYear(), today.getMonth() + (R.monthsAhead || 1), today.getDate());
    dateEl.min = iso(today);
    dateEl.max = iso(last);

    if (partyEl && !partyEl.options.length) {
      for (let n = 1; n <= (R.maxParty || 8); n++) {
        const o = document.createElement('option');
        o.value = n;
        o.textContent = n === 1 ? '1 guest' : n + ' guests';
        partyEl.appendChild(o);
      }
      if (partyEl.options.length > 1) partyEl.selectedIndex = 1;
    }

    /* A table this size stops being a table, so say so rather than
       letting someone discover it on the phone. */
    if (partyEl && hint) {
      const check = () => {
        hint.hidden = !(R.largeParty && +partyEl.value >= R.largeParty);
      };
      on(partyEl, 'change', check);
      check();
    }

    /* ----------------------------------------------------- validation */
    function say(field, msg) {
      const box = $('[data-err-for="' + field.id + '"]', form);
      if (msg) {
        box.textContent = msg;
        box.hidden = false;
        field.setAttribute('aria-invalid', 'true');
      } else {
        box.hidden = true;
        field.removeAttribute('aria-invalid');
      }
    }

    function closedOn(dateStr) {
      const d = new Date(dateStr + 'T00:00:00');
      if (isNaN(d)) return null;
      const h = (window.SITE.hours || []).filter(x => x.day === d.getDay())[0];
      return h && h.open && h.close ? null : DAYS[d.getDay()];
    }

    function validate() {
      let first = null;
      const fail = (field, msg) => {
        say(field, msg);
        if (!first) first = field;
      };
      const ok = field => { say(field, ''); };

      const name = $('#rName');
      const phone = $('#rPhone');

      if (!dateEl.value) fail(dateEl, 'Pick a date.');
      else if (dateEl.value < dateEl.min) fail(dateEl, 'That date has passed.');
      else if (dateEl.value > dateEl.max) {
        fail(dateEl, 'We only take requests ' + (R.monthsAhead || 1) + ' months ahead. Please call for anything later.');
      } else {
        const shut = closedOn(dateEl.value);
        if (shut) fail(dateEl, 'We are closed on ' + shut + 's. Pick another day.');
        else ok(dateEl);
      }

      if (!name.value.trim()) fail(name, 'We need a name for the table.');
      else if (name.value.trim().length > 80) fail(name, 'That name is too long.');
      else ok(name);

      /* Loose on purpose. Pakistan has many valid formats and a
         restaurant is not a bank; this only catches a digit that cannot
         be dialled at all. */
      const digits = phone.value.replace(/[^\d]/g, '');
      if (!phone.value.trim()) fail(phone, 'A number we can confirm on, please.');
      else if (digits.length < 7) fail(phone, 'That looks too short to call.');
      else if (digits.length > 15) fail(phone, 'That looks too long to call.');
      else ok(phone);

      if (first) {
        first.focus();
        window.toast('Check the highlighted field');
      }
      return !first;
    }

    /* --------------------------------------------------------- submit */
    function message() {
      const lines = [
        'Hello ' + window.SITE.name + '.',
        '',
        'I would like to request a table.',
        '',
        'Date: ' + longDate(dateEl.value),
        'Time: ' + $('#rTime').value,
        'Guests: ' + partyEl.value,
        'Name: ' + $('#rName').value.trim(),
        'Phone: ' + $('#rPhone').value.trim()
      ];
      const occ = $('#rOcc').value;
      if (occ && occ !== 'No occasion') lines.push('Occasion: ' + occ);
      const notes = $('#rNotes').value.trim();
      if (notes) lines.push('Notes: ' + notes);
      lines.push('', 'Sent from the website.');
      return lines.join('\n');
    }

    function waUrl() {
      return 'https://wa.me/' + window.SITE.whatsapp +
        '?text=' + encodeURIComponent(message());
    }

    on(form, 'submit', function (e) {
      e.preventDefault();
      if (!validate()) return;

      const url = waUrl();
      if (doneLink) doneLink.href = url;

      form.hidden = true;
      if (done) done.hidden = false;
      if (done) done.scrollIntoView({ block: 'nearest' });

      /* Try to open WhatsApp, but never depend on it: the confirmation
         panel with a real link is already on screen either way, because
         a popup blocker is common and a guest who cannot reach the
         restaurant has been failed at the last step. */
      const w = window.open(url, '_blank', 'noopener');
      window.toast(w ? 'Opening WhatsApp with your request' : 'Your request is ready to send');
    });

    on(again, 'click', function () {
      form.hidden = false;
      if (done) done.hidden = true;
      $('#rName').focus();
    });

    /* Clear an error as soon as the guest starts fixing it, rather than
       making them submit again to find out. */
    ['rDate', 'rName', 'rPhone'].forEach(function (id) {
      const f = document.getElementById(id);
      on(f, 'input', () => { if (f.getAttribute('aria-invalid')) say(f, ''); });
      on(f, 'change', () => { if (f.getAttribute('aria-invalid')) say(f, ''); });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
