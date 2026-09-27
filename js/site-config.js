'use strict';

/* =====================================================================
   SITE CONFIG
   ---------------------------------------------------------------------
   This is the ONLY file you need to edit to put your business back in.
   Every script on the site reads its values from here, so fill these in
   once and the header, cart, currency and WhatsApp links all update.

   Anything left as an empty string '' is simply hidden on the site.
   ===================================================================== */

window.SITE = {

  /* ---- Branding -------------------------------------------------- */
  name:      '',            // e.g. "Your Business Name"
  tagline:   '',            // short line shown under the logo, e.g. "Your City"
  logo:      '',            // path to your logo, e.g. "images/logo.png"
                            // leave '' to use the built-in SVG placeholder mark

  /* ---- Contact --------------------------------------------------- */
  /* International format, digits only, no "+" and no spaces.
     For Pakistan use 92 followed by the 10-digit mobile number.     */
  phone:     '',            // e.g. "923001234567"
  email:     '',            // e.g. "hello@example.com"
  address:   '',            // shown on the contact/visit page

  /* ---- Ordering -------------------------------------------------- */
  /* Set to true to hide the WhatsApp order button until you have a number. */
  whatsappOrdering: false,
  orderPrompt: '',         // default first message a customer sends you

  /* ---- Money ----------------------------------------------------- */
  currency:  'PKR',         // default currency on first visit
  /* Only used for the display-only USD toggle. Update this as the
     rate moves. Orders are always sent to you in your own currency. */
  ratePKRPerUSD: 278,

  /* ---- Pages ----------------------------------------------------- */
  /* Search reads the menu page to build its index. Point it at whichever
     page actually lists your products. Remove the entry to disable it.  */
  searchIndexUrl: '',      // e.g. "/menu"

  /* ---- Search suggestions ---------------------------------------- */
  /* Quick-pick chips shown in the empty search box. Leave [] for none. */
  searchChips: [],         // e.g. ["Category A", "Category B"]

};
