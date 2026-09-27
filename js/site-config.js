/* =====================================================================
   Business configuration
   ---------------------------------------------------------------------
   Every editable detail lives here. Nothing else needs touching to
   rebrand the site.

   !! PLACEHOLDERS !!
   The values marked TODO are invented so the layout has something real
   to render. Replace them with the actual business details before this
   goes live. See TODO COUNT at the bottom of this file.
   ===================================================================== */

window.SITE = {
  /* --- identity --- */
  name: 'Umar Hayat Chaska Point',        // kept as-is on request
  logo: '/umarhayatchaskapoint-trimmed.png',
  logoAlt: 'Umar Hayat Chaska Point',
  /* What the kitchen actually serves. */
  tagline: 'Nashta, Barbecue &amp; Fried Items',

  /* --- contact --- */
  /* TODO: replace with the real number, address and email. The tel:
     link, the WhatsApp link and the footer all read from here. */
  phone: '+92 300 0000000',
  phoneHref: '+923000000000',              // TODO
  whatsapp: '923000000000',                // TODO — country code + number, no +, no spaces
  email: 'hello@example.com',              // TODO
  address: {
    line1: 'Shop 12, Mall Road',           // TODO
    line2: 'Sahiwal, Punjab',              // TODO
    city: 'Sahiwal',
    country: 'Pakistan',
    postcode: '60050'                      // TODO
  },

  /* --- social --- */
  /* TODO: fill in the real profiles, or delete the keys you don't use. */
  social: {
    instagram: 'https://instagram.com/',   // TODO
    facebook:  'https://facebook.com/',    // TODO
    tiktok:    'https://tiktok.com/'       // TODO
  },

  /* --- opening hours ---
     0 = Sunday … 6 = Saturday, matching Date.prototype.getDay().
     null means closed. TODO: confirm real hours. */
  hours: [
    { day: 0, open: '11:00', close: '23:00' },
    { day: 1, open: '11:00', close: '23:00' },
    { day: 2, open: '11:00', close: '23:00' },
    { day: 3, open: '11:00', close: '23:00' },
    { day: 4, open: '11:00', close: '23:00' },
    { day: 5, open: '11:00', close: '23:00' },
    { day: 6, open: '12:00', close: '00:00' }
  ],

  /* --- categories ---
     Drives the menu page filter buttons and the search index. The
     category nav was removed from the header on request, so `path` is
     only used for deep links like /menu#barbecue. */
  categories: [
    { id: 'nashta',   label: 'Nashta',   path: '/menu#nashta' },
    { id: 'barbecue', label: 'Barbecue', path: '/menu#barbecue' },
    { id: 'fried',    label: 'Fried Items', path: '/menu#fried' }
  ],

  /* --- currency ---
     Prices are stored once, in PKR, as integers. Everything else is
     derived, so there is only ever one number to edit per item. */
  currency: {
    default: 'PKR',
    /* TODO: this rate is a guess and will drift. It is display-only —
       no payment is taken anywhere on this site, so it must never be
       treated as a real conversion. Update it, or wire up a live feed. */
    rate: { PKR: 1, USD: 0.0036 },
    symbols: { PKR: 'Rs', USD: '$' },
    /* How to round each currency, so USD never shows stray decimals. */
    decimals: { PKR: 0, USD: 2 }
  },

  /* --- delivery --- */
  /* TODO: confirm real fees and thresholds. */
  delivery: {
    fee: 150,            // PKR
    freeOver: 3000,      // PKR
    minOrder: 500        // PKR
  },

  /* --- commerce ---
     This is a static site. There is no Shopify backend, no payment
     processor and no server. The cart lives in the visitor's browser
     and is lost if they clear site data. See README.md. */
  commerce: {
    live: false,
    checkoutNote: 'Static demo — no checkout, no payment is taken.'
  }
};

/* Single place to count what still needs real data, so it can't be
   quietly forgotten. Run: SITE.todos() */
window.SITE.todos = function () {
  const t = [];
  const flag = (label, value, isPlaceholder) => {
    if (isPlaceholder(value)) t.push(label);
  };
  const ph = v => typeof v === 'string' && /example\.com|0000000|TODO/i.test(v);

  flag('phone', SITE.phone, ph);
  flag('whatsapp', SITE.whatsapp, ph);
  flag('email', SITE.email, ph);
  flag('address', SITE.address.line1, ph);
  for (const k in SITE.social) flag('social.' + k, SITE.social[k], ph);
  flag('currency.rate.USD (guess, drifts)', SITE.currency.rate.USD, () => true);
  flag('opening hours (unconfirmed)', '', () => true);
  flag('categories (unconfirmed)', '', () => true);
  flag('delivery fees (unconfirmed)', '', () => true);
  flag('menu items + prices (placeholder)', '', () => true);
  flag('about copy (placeholder)', '', () => true);
  return t;
};
