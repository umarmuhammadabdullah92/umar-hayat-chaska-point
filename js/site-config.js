/* =====================================================================
   Business configuration
   ---------------------------------------------------------------------
   Every editable detail lives here. Nothing else needs touching to
   rebrand the site.

   !! PLACEHOLDERS !!
   Almost every value below marked TODO is invented, so the layout has
   something real to render. Replace them with the actual business
   details before this goes live. Run SITE.todos() in the browser console
   to list what is still outstanding; it is generated from this file, so
   it cannot drift out of step with it.
   ===================================================================== */

window.SITE = {
  /* --- where the site lives --------------------------------------------
     The one absolute address everything is built from: the canonical URL
     on every page, og:url, sitemap.xml, robots.txt and the JSON-LD all
     derive from this string, so moving the site is a one-line edit here
     and a rebuild.

     It must be a real, resolvable origin and must match the host the site
     is actually served from. A canonical pointing somewhere the site is
     not is worse than no canonical at all: it tells a search engine the
     pages you own live on a domain you do not control.

     No trailing slash, no trailing path. TODO: swap to the real domain
     the day the site is published. */
  url: 'https://umar-hayat-chaska-point.vercel.app',

  /* --- identity ------------------------------------------------------- */
  name: 'Umar Hayat Chaska Point',   // the real name, kept as given
  /* What the room actually is. The old one described the categories. */
  tagline: 'Charcoal Grill & Nashta House',
  /* Shown under the hero wordmark and in the footer. TODO: real year. */
  est: 'Est. 1974',
  city: 'Sahiwal',
  /* Above the hero headline. TODO: rewrite to whatever it really is. */
  heroKicker: 'Charcoal, smoke and slow hours',
  /* Under the hero headline, one sentence. TODO: rewrite. */
  heroLede:
    'A long table, a live coal fire and a kitchen that has been doing this ' +
    'for three generations. Come hungry, stay late.',

  /* --- contact --------------------------------------------------------
     TODO: replace with the real number, address and email. The tel:
     link, the WhatsApp links, the reservation hand-off and the footer
     all read from here, so this is the only place to edit them. */
  phone: '+92 300 0000000',
  phoneHref: '+923000000000',         // TODO — tel: target, no spaces
  whatsapp: '923000000000',           // TODO — country code + number, no +, no spaces
  email: 'umarmuhammadabdullah92@gmail.com',
  address: {
    line1: 'Shop 12, Mall Road',      // TODO
    line2: 'Sahiwal, Punjab',         // TODO
    city: 'Sahiwal',                  // TODO
    country: 'Pakistan',
    countryCode: 'PK',                // ISO 3166-1 alpha-2, for the JSON-LD
    postcode: '60050'                 // TODO
  },

  /* --- cuisine ---------------------------------------------------------
     What the room actually serves, in the vocabulary a search engine and
     a guest both use. Separate from the menu categories above, which are
     how the menu is filed: "From the Coal" is a section heading and not
     a cuisine, and putting section names in servesCuisine tells Google
     the restaurant serves something called "From the Coal". */
  cuisine: ['Pakistani', 'North Indian', 'Barbecue'],

  /* --- social ---------------------------------------------------------
     TODO: fill in the real profiles, or delete the keys you don't use.
     build.py reads this block and bakes the links into the HTML, so the
     icons still work with JavaScript disabled. Deleting a key removes
     its icon. */
  social: {
    instagram: 'https://instagram.com/',   // TODO
    facebook:  'https://facebook.com/',    // TODO
    tiktok:    'https://tiktok.com/'       // TODO
  },

  /* --- opening hours ---
     0 = Sunday … 6 = Saturday, matching Date.prototype.getDay().
     Omit a day, or set both times to null, and it reads as closed.
     TODO: confirm the real hours. The hero strip, the visit section and
     the footer all render from this, so it only has to be right here. */
  hours: [
    { day: 0, open: '11:00', close: '23:00' },
    { day: 1, open: '11:00', close: '23:00' },
    { day: 2, open: '11:00', close: '23:00' },
    { day: 3, open: '11:00', close: '23:00' },
    { day: 4, open: '11:00', close: '23:00' },
    { day: 5, open: '11:00', close: '23:00' },
    { day: 6, open: '12:00', close: '00:30' }
  ],

  /* --- menu categories ---
     These ids are the data-cat on every dish in the ITEMS list in
     build.py, so a dish whose category is not listed here is filtered
     out of every view and can never be found. build.py checks this and
     fails rather than publishing a dish nobody can reach.

     `note` is the one line of copy under each category heading on the
     menu. TODO: all three are placeholders. */
  categories: [
    { id: 'nashta',   label: 'Nashta',   note: 'The morning counter. Slow-cooked, spiced the long way, served all day.' },
    { id: 'barbecue', label: 'From the Coal', note: 'Marinated overnight, grilled over live charcoal, carried to the table hot.' },
    { id: 'fried',    label: 'Fried',    note: 'Crushed by hand to order, never held, never reheated.' }
  ],

  /* --- reservations ---
     A reservation on this site is a REQUEST that opens WhatsApp with
     the details filled in. Nothing is sent anywhere and nothing is
     stored. The restaurant confirms by phone. That is deliberate: a
     form that silently drops bookings is worse than a form that hands
     the guest straight to WhatsApp, where a person actually sees it.

     TODO: confirm the real service slots, the largest table and the
     occasions worth offering. */
  reservations: {
    /* Bookings are for this month and the next. A restaurant taking
       requests online is not taking bookings a year out. */
    monthsAhead: 2,
    /* Largest party the form will seat. TODO */
    maxParty: 12,
    /* Above this the hint tells the guest it has stopped being a table.
       Below it, nothing: a party of four should not be warned about
       anything. */
    largeParty: 7,
    /* Anything above maxParty is directed to WhatsApp instead, where
       the restaurant can quote for a private room. */
    slots: [
      '12:00', '13:00', '14:00',
      '18:00', '18:30', '19:00', '19:30', '20:00', '20:30',
      '21:00', '21:30', '22:00', '22:30'
    ],
    occasions: [
      'No occasion',
      'Birthday',
      'Anniversary',
      'Business dinner',
      'Family meal',
      'Celebration'
    ],
    /* Under the submit button. This is the single most important line of
       copy on the site, because it is the difference between a guest
       believing they have a table and a guest believing they have a
       request. Keep it. */
    notice:
      'This is a request, not a confirmed table. We confirm by phone, ' +
      'usually within the hour between 12:00 and 23:00.'
  },

  /* --- private dining ---
     TODO: confirm the real rooms, capacities and terms. `seats` and
     `terms` are shown verbatim on the page, so make them the sentence
     you would actually say to a guest on the phone. */
  privateDining: [
    {
      id: 'private-room',
      name: 'The Private Room',
      seats: 'Seats 14',
      terms: 'Set menu, three courses, agreed in advance. Minimum spend applies.',
      body: 'A room of your own off the main hall, with its own charcoal ' +
            'fire and a server who stays with the table all evening. The ' +
            'most requested booking in the house, so it goes early.'
    },
    {
      id: 'chefs-table',
      name: "The Chef's Table",
      seats: 'Seats 6',
      terms: 'Six courses, served by the kitchen. Booked a week ahead.',
      body: 'Six seats at the pass. Everything comes off the fire in front ' +
            'of you, one course at a time, with whatever the coals decided ' +
            'to be good that evening. It is not a performance and it is not ' +
            'written down in advance.'
    },
    {
      id: 'buyout',
      name: 'A Whole Evening',
      seats: 'Full house',
      terms: 'From 40 guests. The kitchen closes to the public from 19:00.',
      body: 'The whole room, the whole fire, and a menu written with you in ' +
            'advance. Weddings, engagements, the annual dinner that nobody ' +
            'wants to organise. Call, and we will send the floor plan.'
    }
  ],

  /* --- the room, in four steps ---
     Drives the numbered grid in the experience section. TODO: placeholder
     copy, written to sound like a place rather than a process. */
  experience: [
    {
      title: 'The fire',
      body: 'Briquettes lit at eleven and buried under ash until the coals ' +
            'settle. Nothing is grilled over gas on this site, ever.'
    },
    {
      title: 'The night before',
      body: 'Meat is marinated in the afternoon, not the morning, and never ' +
            'in a rush. That is the whole difference between a skewer that ' +
            'tastes of something and one that tastes of salt.'
    },
    {
      title: 'The grill',
      body: 'Cooked in small batches so every skewer gets the same heat, and ' +
            'carried to the table the moment it leaves the grate.'
    },
    {
      title: 'The last hour',
      body: 'The kitchen stops at eleven. What is left is what was started ' +
            'that evening, and the fire burns down slowly in an empty room.'
    }
  ],

  /* --- the house, in four facts ---
     The detail list beside the story. TODO: every value is invented. */
  house: [
    { label: 'The house',  value: 'Family run, three generations' },
    { label: 'The grill',  value: 'Live charcoal, binchotan and hardwood' },
    { label: 'The room',   value: 'Sixty covers, one long hall' },
    { label: 'The service', value: 'Dinner from 18:00, last table 22:30' }
  ],

  /* --- the pull quote in the interlude band ---
     TODO: replace with something the restaurant would actually stand
     behind. A fabricated quote attributed to a real-sounding person is
     the easiest thing on this site to get wrong, so leave the
     attribution blank until there is a real person to attribute it to. */
  quote: {
    text: 'TODO — a sentence about the food or the room, in the owner\u2019s ' +
          'own words. It is set large and attributed below, so it reads as ' +
          'a quote from a person and had better be one.',
    by: 'TODO — name and role, or leave blank to drop the attribution'
  },

  /* --- currency ---
     A restaurant menu quotes the currency of the room it is in. There is
     no visitor-side conversion anywhere on this site, which is why this
     is a symbol and a code rather than a table of exchange rates.
     build.py reads it to format every price, so changing the symbol here
     changes the whole menu. */
  currency: {
    code: 'PKR',
    /* The code rather than "Rs". On its own "Rs" is ambiguous outside
       Pakistan, and a price a guest cannot identify is a price they will
       ask about. Three characters wider, and worth it. */
    symbol: 'PKR'
  }
};

/* ---------------------------------------------------------------------
   Single place to count what still needs real data, so it cannot be
   quietly forgotten. Run: SITE.todos()
   --------------------------------------------------------------------- */
window.SITE.todos = function () {
  const t = [];
  const ph = v => typeof v === 'string' && /example\.com|0000000|\bTODO\b/i.test(v);
  const flag = (label, value) => { if (ph(value)) t.push(label); };

  flag('phone', SITE.phone);
  flag('whatsapp', SITE.whatsapp);
  flag('email', SITE.email);
  flag('address', SITE.address.line1);
  for (const k in SITE.social) flag('social.' + k, SITE.social[k]);
  flag('establishing year', SITE.est);
  flag('hero kicker', SITE.heroKicker);
  flag('hero lede', SITE.heroLede);
  /* The canonical, sitemap and JSON-LD are all built from SITE.url, so a
     placeholder host here is published to every search engine that reads
     the site. Checked separately from the rest because a real-looking
     hosting domain does not contain "TODO" or "example.com". */
  if (!/^https:\/\//.test(SITE.url || '') || /vercel\.app|\bTODO\b/i.test(SITE.url || '')) {
    t.push('site url (canonical, sitemap, robots and JSON-LD are built from it)');
  }
  SITE.categories.forEach(c => { if (ph(c.note)) t.push('menu category note: ' + c.label); });
  SITE.house.forEach(h => { if (ph(h.value)) t.push('house detail: ' + h.label); });
  SITE.experience.forEach(x => { if (ph(x.body)) t.push('experience step: ' + x.title); });
  SITE.privateDining.forEach(p => {
    if (ph(p.body)) t.push('private dining copy: ' + p.name);
    if (ph(p.terms)) t.push('private dining terms: ' + p.name);
  });
  if (ph(SITE.reservations.notice)) t.push('reservation notice');
  flag('interlude quote', SITE.quote.text);
  flag('interlude attribution', SITE.quote.by);

  /* Things with no value to match a regex against, so they are listed
     here rather than flagged. */
  t.push('opening hours (unconfirmed)');
  t.push('menu prices (see the sentinel report from build.py)');
  t.push('cuisine list (inferred, confirm it describes the food actually served)');
  /* The menu is names and prices only, and so are the signature cards.
     These descriptions and serving notes are written but not rendered
     anywhere, and search matches on the dish name alone. They are listed
     here because the real copy still has to be written and approved
     before any of it is put back on the page. */
  t.push('dish descriptions and serving notes (written, not displayed anywhere)');
  t.push('story, signature and experience copy (placeholder)');
  t.push('dish photography (none in the repo — see img/README.md)');
  return t;
};
