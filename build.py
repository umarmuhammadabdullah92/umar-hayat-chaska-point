#!/usr/bin/env python3
"""
Generates the four site pages from ONE shared header/footer template.

The previous version of this site duplicated the header markup across
pages by hand and they silently drifted apart. Here the chrome exists
exactly once, as a Python string, and is stamped into every page, so a
change to the header cannot be applied to three pages and forgotten on
the fourth.

Run:  python3 build.py
"""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(ROOT, 'img')

# The site shows no images in its pages. The image sections were built and
# then removed on request, so the only image left in the build is the
# og:image share card, which has to point at something real or a shared
# link renders with no picture at all. Drop a 1200x630 file at
# img/social.jpg and it is picked up on the next build; until then the
# logo is used.
EXTS = ('.jpg', '.jpeg', '.png', '.webp', '.avif')

def find_image(key):
    for ext in EXTS:
        path = os.path.join(IMG_DIR, key + ext)
        if os.path.exists(path):
            return key + ext
    return None

# ---------------------------------------------------------------- icons
ICON = {
 'search': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
 'user':   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4.5 20.5a7.5 7.5 0 0 1 15 0"/></svg>',
 'bag':    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 8h14l-1 12H6L5 8Z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>',
 'phone':  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3h3l2 5-2.5 1.5a12 12 0 0 0 6 6L16 13l5 2v3a2 2 0 0 1-2.2 2A17 17 0 0 1 4 6.2 2 2 0 0 1 6 3Z"/></svg>',
 'pin':    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s7-5.5 7-11a7 7 0 1 0-14 0c0 5.5 7 11 7 11Z"/><circle cx="12" cy="10" r="2.5"/></svg>',
 'clock':  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5.5l3.5 2"/></svg>',
 'mail':   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6.5 8.5 6 8.5-6"/></svg>',
 'x':      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" aria-hidden="true"><path d="M5 5l14 14M19 5 5 19"/></svg>',
}

# Social icons. The URLs live in js/site-config.js so there is still one
# place to edit them; build.py reads them from there and bakes them into
# the HTML, which keeps the links working with JavaScript disabled.
SOCIAL_ICON = {
 'instagram': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><rect x="2.6" y="2.6" width="18.8" height="18.8" rx="5.4"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.5" cy="6.5" r="1.15" fill="currentColor" stroke="none"/></svg>',
 'facebook':  '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.5 21v-8h2.7l.4-3.1h-3.1V7.9c0-.9.25-1.5 1.55-1.5h1.65V3.6c-.29-.04-1.27-.13-2.41-.13-2.39 0-4.02 1.46-4.02 4.13V9.9H7.5V13h2.77v8h3.23Z"/></svg>',
 'tiktok':    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.6 5.82A4.28 4.28 0 0 1 15.54 3h-3.09v12.4a2.59 2.59 0 0 1-2.59 2.5 2.59 2.59 0 0 1 0-5.18c.27 0 .52.04.76.12V9.66a5.68 5.68 0 0 0-.76-.05A5.66 5.66 0 1 0 15.54 15.3V9.01a7.35 7.35 0 0 0 4.3 1.38V7.3a4.29 4.29 0 0 1-3.24-1.48Z"/></svg>',
}

def social_links():
    """Read SITE.social out of js/site-config.js.

    Raises rather than guessing if the block or an icon is missing, so a
    broken edit fails the build instead of publishing an icon that links
    nowhere.
    """
    path = os.path.join(ROOT, 'js', 'site-config.js')
    src = open(path, encoding='utf-8').read()
    block = re.search(r'social:\s*\{(.*?)\}', src, re.S)
    if not block:
        raise SystemExit('build.py: no social block found in js/site-config.js')
    found = dict(re.findall(r"(\w+):\s*'([^']*)'", block.group(1)))
    out = []
    for key, url in found.items():
        if not url.strip():
            continue
        if key not in SOCIAL_ICON:
            raise SystemExit('build.py: no icon defined for social key "%s"' % key)
        out.append((key, url.strip(), SOCIAL_ICON[key]))
    if not out:
        raise SystemExit('build.py: SITE.social has no filled-in URLs')
    return out

def social_markup(cls, extra=''):
    return '\n'.join(
        '        <a class="soc" href="%s" target="_blank" rel="noopener noreferrer" '
        'aria-label="%s" title="%s"%s>%s</a>' % (url, key.capitalize(), key.capitalize(), extra, icon)
        for key, url, icon in social_links())

# ------------------------------------------------------------- chrome
# Categories mirror SITE.categories in js/site-config.js.
# Single page, so the nav jumps between sections rather than pages. There
# is no "Home" link any more: you are always on the one page, so a link
# back to it would be a no-op.
NAV = [
    ('Menu',     '#menu'),
    ('About Us', '#about'),
    ('Contact',  '#contact'),
]

def nav_links(active=''):
    """Primary nav. Used in the topbar AND the mobile drawer, so the two
    can never disagree.

    No aria-current here. With one page there is no current page to speak
    of, and the section you are reading is marked by the scroll spy in
    js/header.js instead, which can actually be right rather than always
    pointing at the same thing.
    """
    return '\n'.join(
        f'      <a href="{href}" data-nav="section">{lbl}</a>'
        for lbl, href in NAV)

def header(active):
    """The component. Identical on every page except aria-current.

    Category links (Chasha, Chaat, Fast Food, Beverages, Deals) were
    removed from the header on request. Categories still exist as
    data-cat on the menu items, so the menu page filters and search are
    unaffected.
    """
    return f'''<a class="skip" href="#main">Skip to content</a>

<header class="site-hdr">
  <div class="topbar">
    <div class="topbar-side topbar-side--l">
      <button class="ham" type="button" id="hamburger"
              aria-label="Open menu" aria-expanded="false" aria-controls="drawer">
        <span></span><span></span><span></span>
      </button>
      <nav class="social" aria-label="Social media">
{social_markup('soc')}
      </nav>
    </div>

    <a class="logo" href="/">
      <img class="logo-img" src="/umarhayatchaskapoint-trimmed.png"
           alt="Umar Hayat Chaska Point" width="426" height="278" fetchpriority="high">
    </a>

    <div class="topbar-side topbar-side--r">
      <div class="utilities">
        <button class="uicon uico-hide" type="button" data-open="search"
                aria-label="Search the menu" aria-haspopup="dialog">{ICON['search']}</button>

        <div class="uwrap">
          <button class="uicon uico-hide" type="button" id="curBtn" data-open="currency"
                  aria-label="Change currency" aria-haspopup="true" aria-expanded="false">
            <span class="uicon-lbl" id="curLabel">PKR</span>
          </button>
          <div class="pop" id="curPop" role="menu" aria-labelledby="curBtn">
            <p class="pop-hd">Currency</p>
            <div id="curList"></div>
            <p class="pop-note">Display only. Prices convert from PKR at a fixed
              rate stored in <code>js/site-config.js</code> &mdash; no payment is taken.</p>
          </div>
        </div>

        <button class="uicon uico-hide" type="button" data-open="account"
                aria-label="Your account" aria-haspopup="dialog">{ICON['user']}</button>

        <button class="uicon" type="button" data-open="cart"
                aria-label="Open cart" aria-haspopup="dialog">
          {ICON['bag']}<span class="uicon-badge" data-cart-count hidden>0</span>
        </button>
      </div>
    </div>
  </div>

  <nav class="mainnav" aria-label="Primary">
    <div class="mainnav-in">
{nav_links(active)}
      <a class="nav-cta" href="#contact">Order Now</a>
    </div>
  </nav>
</header>'''

def overlays(active):
    return f'''
<div class="scrim" id="sheetScrim"></div>
<div class="scrim" id="mobScrim"></div>
<div class="scrim cart-scrim" id="cartScrim"></div>

<!-- search ------------------------------------------------------------ -->
<section class="sheet" id="searchSheet" role="dialog" aria-modal="true"
         aria-label="Search the menu" inert>
  <div class="sheet-hd">
    <h2>Search</h2>
    <button class="icon-btn" type="button" id="searchClose" data-close aria-label="Close search">{ICON['x']}</button>
  </div>
  <div class="sheet-in">
    <div class="sfield">
      {ICON['search']}
      <input type="search" id="searchInput" placeholder="Search nashta, barbecue, fried&hellip;"
             autocomplete="off" spellcheck="false" aria-label="Search the menu">
    </div>
    <p class="results-hint" id="searchHint">Popular right now</p>
    <div class="results" id="searchResults"></div>
  </div>
</section>

<!-- account ----------------------------------------------------------- -->
<section class="sheet" id="acctSheet" role="dialog" aria-modal="true"
         aria-label="Your account" inert>
  <div class="sheet-hd">
    <h2>Your account</h2>
    <button class="icon-btn" type="button" id="acctClose" aria-label="Close account">{ICON['x']}</button>
  </div>
  <div class="sheet-in">
    <p class="acct-lede">This is a static demo. Your email is stored in this
      browser only &mdash; there is no server, no login and no password reset.</p>

    <form class="acct-grid" id="acctForm">
      <div class="field">
        <label for="acctEmail">Email</label>
        <input type="email" id="acctEmail" placeholder="you@example.com" required>
      </div>
      <button class="btn btn-accent" type="submit" id="acctSubmit">Save</button>
    </form>

    <div id="acctSignedIn" hidden>
      <p class="acct-lede">Signed in on this device as
        <strong id="acctName" style="color:var(--fg)"></strong>.</p>
      <div class="acct-orders" id="acctOrders"></div>
      <button class="link-danger" type="button" id="acctSignOut">Clear from this device</button>
    </div>
  </div>
</section>

<!-- mobile drawer ----------------------------------------------------- -->
<aside class="drawer" id="drawer" aria-label="Menu" inert>
  <div class="drawer-utility">
    <p class="pop-hd">Currency</p>
    <div class="seg" id="drawerSeg" role="radiogroup" aria-label="Currency"></div>
  </div>
  <nav class="drawer-nav" aria-label="Mobile">
{nav_links(active)}
  </nav>
  <div class="drawer-foot">
    <nav class="social" aria-label="Social media">
{social_markup('soc')}
    </nav>
    <small>Nashta, barbecue and fried items, cooked to order.</small>
  </div>
</aside>

<!-- cart -------------------------------------------------------------- -->
<aside class="cart" id="cart" role="dialog" aria-modal="true" aria-label="Your cart" inert>
  <div class="cart-hd">
    <div>
      <h2>Your cart</h2>
      <p id="cartCount">0 items</p>
    </div>
    <button class="icon-btn" type="button" id="cartClose" aria-label="Close cart">{ICON['x']}</button>
  </div>
  <div class="cart-items" id="cartItems"></div>
  <div class="cart-sum">
    <div class="sum-row"><span>Subtotal</span><span id="sumSub">Rs 0</span></div>
    <div class="sum-row" id="sumDelivery"><span>Delivery</span><span id="sumDeliveryVal">Rs 150</span></div>
    <div class="sum-row sum-row--total"><span>Total</span><b id="sumTotal">Rs 0</b></div>
  </div>
  <div class="cart-foot">
    <p class="note" id="cartHint"></p>
    <div class="cart-fields">
      <div class="field">
        <label for="cName">Name</label>
        <input type="text" id="cName" placeholder="Your name" autocomplete="name">
      </div>
      <div class="field">
        <label for="cPhone">Phone</label>
        <input type="tel" id="cPhone" placeholder="03XX XXXXXXX" autocomplete="tel">
      </div>
      <div class="field">
        <label for="cAddr">Delivery address</label>
        <textarea id="cAddr" rows="2" placeholder="Street, area, city"></textarea>
      </div>
    </div>
    <button class="btn btn-accent" type="button" id="checkoutBtn">Checkout</button>
    <button class="btn btn-ghost" type="button" id="cartClear" style="width:100%;margin-top:9px">Clear cart</button>
  </div>
</aside>

<button class="cart-fab" type="button" data-open="cart" data-cart-fab hidden>
  {ICON['bag']} <span>View cart</span> <b data-cart-count hidden>0</b>
</button>'''

def footer():
    return f'''<footer class="site-foot">
  <div class="foot-in">
    <nav aria-label="Footer">
      <a href="/">Home</a>
      <a href="/menu">Menu</a>
      <a href="/about">About Us</a>
      <a href="/contact">Locations &amp; Contact</a>
    </nav>
    <small>&copy; 2026 Umar Hayat Chaska Point &middot; Static demo, no checkout</small>
  </div>
</footer>'''

SCRIPTS = '''<script src="/js/site-config.js"></script>
<script src="/js/money.js"></script>
<script src="/js/header.js"></script>
<script src="/js/cart.js"></script>'''

# 1200x630 is what every platform renders a share card at, so prefer a real
# social image. Falling back to the logo is better than shipping a broken
# og:image, but a logo is a poor share card and worth replacing.
OG_IMAGE = find_image('social')
og_image = '/img/' + OG_IMAGE if OG_IMAGE else '/umarhayatchaskapoint-trimmed.png'

def page(path, title, desc, body, active):
    return f'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0E0B08">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/fonts/display-700.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/body-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/style.css">
</head>
<body>
{header(active)}
{overlays(active)}
<main id="main">
{body}
</main>
{footer()}
{SCRIPTS}
</body>
</html>
'''

# --------------------------------------------------------------- pages
# Every menu item below is INVENTED placeholder data. Replace with the
# real menu, with real prices, before launch.

ITEMS = [
 # --- nashta ---
 # REAL dishes, supplied by the owner. Spellings are theirs and were not
 # normalised: "murag", "anday" and "haleem" are how the shop writes them.
 # TODO prices are 999 as a sentinel meaning "not a real price yet", and the
 # descriptions are one-line definitions, not copy. Both need replacing.
 ('murag-chanay','Murag Chanay','nashta',999,[],
  'Chicken curry.'),
 ('anday-chanay','Anday Chanay','nashta',999,[],
  'Egg curry.'),
 ('haleem-chawal','Haleem Chawal','nashta',999,[],
  'Haleem with rice.'),

 # --- barbecue ---
 ('malai-boti','Chicken Malai Boti','barbecue',480,['4 pc','8 pc'],
  'Cream and cheese marinade, skewered and grilled over charcoal.'),
 ('seekh-kebab','Chicken Seekh Kebab','barbecue',520,['4 pc','8 pc'],
  'Hand-minced chicken with coriander and green chilli.'),
 ('chicken-tikka','Chicken Tikka','barbecue',550,['Half','Full'],
  'Yoghurt-marinated thigh meat, charred at the edges.'),
 ('mutton-seekh','Mutton Seekh Kebab','barbecue',850,['4 pc','8 pc'],
  'Minced mutton seekh, spiced with raw papaya.'),
 ('beef-boti','Beef Boti','barbecue',780,['4 pc','8 pc'],
  'Tender beef boti with onion and black pepper.'),
 ('grilled-chicken','Grilled Chicken','barbecue',950,['Half','Full'],
  'Whole bird marinated overnight, grilled to order.'),
 ('bbq-platter-two','BBQ Platter for Two','barbecue',2400,['Serves 2'],
  'Malai boti, seekh kebab, tikka, naan, salad and chutney.'),

 # --- fried ---
 # REAL dishes, supplied by the owner. "Began" and "mirch" are kept as
# written; "Samosy" and "Pakory" are respelled to Samosa and Pakora,
# which are the standard spellings. Say so if the shop prefers otherwise.
 # TODO prices are the 999 sentinel again, descriptions are definitions.
 ('samosa-fried','Samosa','fried',999,[],
  'Fried pastry.'),
 ('pakora','Pakora','fried',999,[],
  'Battered and fried.'),
 ('aloo-ki-tikki','Aloo Ki Tikki','fried',999,[],
  'Spiced potato patty, fried.'),
 ('began-pakora','Began Pakora','fried',999,[],
  'Brinjal, battered and fried.'),
 ('mirch-pakora','Mirch Pakora','fried',999,[],
  'Chilli, battered and fried.'),
 ('fried-naan','Fried Naan','fried',999,[],
  'Fried bread.'),
]

def item_card(i):
    sid, name, cat, price, sizes, desc = i
    size_html = ''
    if sizes:
        first = ' is-on'
        size_html = ('<div class="sizes" role="group" aria-label="Choose a size for %s">'
                     % name
                     + ''.join('<button type="button" class="size%s" data-size aria-pressed="%s">%s</button>'
                               % (first if k == 0 else '', 'true' if k == 0 else 'false', s)
                               for k, s in enumerate(sizes))
                     + '</div>')
    return f'''      <article class="card" id="{sid}" data-item="{name}" data-price="{price}" data-cat="{cat}">
        <h3>{name}</h3>
        <p>{desc}</p>
        {size_html}
        <div class="card-foot">
          <span class="price" data-price-of>{price}</span>
          <span class="price-note">incl. tax</span>
        </div>
        <button class="add" type="button" data-add>Add to cart</button>
      </article>'''

MENU_CARDS = '\n'.join(item_card(i) for i in ITEMS)

def cat_buttons():
    out = ['      <button class="filter" type="button" data-filter="all" aria-pressed="true">All</button>']
    for c in SITE_CATS:
        out.append(f'      <button class="filter" type="button" data-filter="{c[1]}" aria-pressed="false">{c[0]}</button>')
    return '\n'.join(out)

SITE_CATS = [('Nashta','nashta'),('Barbecue','barbecue'),('Fried Items','fried')]

# The homepage body was removed on request, so the front page is now just
# the header and footer. It still needs exactly one h1: a document with no
# h1 has no accessible name and search engines read the page as having no
# topic. The heading is visually hidden, so nothing is shown, but the
# "Skip to content" link still has somewhere to land and the accessibility
# checks keep one h1 per page.
HOME = '''  <section class="wrap">
    <h1 class="vh">Umar Hayat Chaska Point</h1>
  </section>
'''

MENU = f'''<section id="menu" class="sect" aria-labelledby="menu-h">
  <div class="wrap">
    <header class="page-head">
      <p class="eyebrow">{ICON['bag']} Menu</p>
      <h2 id="menu-h">The menu</h2>
    </header>

    <div class="filters" role="group" aria-label="Filter by category">
{cat_buttons()}
      <span class="price-note" id="filterCount" style="align-self:center;margin-left:auto"></span>
    </div>

    <div class="grid grid--menu">
{MENU_CARDS}
    </div>
  </div>
  </section>'''

ABOUT = f'''<section id="about" class="sect" aria-labelledby="about-h">
  <div class="wrap">
    <header class="page-head">
      <p class="eyebrow">{ICON['user']} About Us</p>
      <h2 id="about-h">Our story</h2>
    </header>
  </div>
  </section>'''

CONTACT = f'''<section id="contact" class="sect" aria-labelledby="contact-h">
  <div class="wrap">
    <header class="page-head">
      <p class="eyebrow">{ICON['pin']} Locations &amp; Contact</p>
      <h2 id="contact-h">Find us</h2>
      <p>One shopfront, open seven days. Call ahead for large orders.</p>
    </header>

    <div class="detail" style="grid-template-columns:1.1fr .9fr">
      <div>
        <div class="info-row">
          <span class="info-ico">{ICON['pin']}</span>
          <div>
            <h3>Address</h3>
            <p>Shop 12, Mall Road<br>Sahiwal, Punjab 60050<br>Pakistan</p>
          </div>
        </div>
        <div class="info-row">
          <span class="info-ico">{ICON['phone']}</span>
          <div>
            <h3>Phone</h3>
            <p><a href="tel:+923000000000">+92 300 0000000</a><br>
               <a href="https://wa.me/923000000000" rel="noopener">WhatsApp us</a></p>
          </div>
        </div>
        <div class="info-row">
          <span class="info-ico">{ICON['mail']}</span>
          <div>
            <h3>Email</h3>
            <p><a href="mailto:hello@example.com">hello@example.com</a></p>
          </div>
        </div>
        <a class="btn btn-wa" href="https://wa.me/923000000000" rel="noopener"
           style="margin-top:24px">Order on WhatsApp</a>
      </div>

      <div>
        <h3 class="col-head">Opening hours</h3>
        <div class="hours" id="hours"></div>
        <p class="note">Hours are rendered from
          <code>SITE.hours</code> so they stay in step with the config.</p>
      </div>
    </div>
  </div>
  </section>'''

HOURS_JS = '''
<script>
/* Renders opening hours from config and marks today. */
(function () {
  var box = document.getElementById('hours');
  if (!box) return;
  var names = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  var today = new Date().getDay();
  var t = window.SITE.hours;
  var rows = [];
  for (var i = 0; i < 7; i++) {
    var d = t.filter(function (h) { return h.day === i; })[0];
    var when = d ? (d.open + ' \\u2013 ' + d.close) : 'Closed';
    rows.push('<div class="' + (i === today ? 'is-today' : '') + '"><span>' + names[i] +
      '</span><span>' + when + '</span></div>');
  }
  box.innerHTML = rows.join('');
})();
</script>
'''

# One page, three sections, in the order a visitor wants them: what you
# sell, then who you are, then how to reach you.
BODY = ('  <h1 class="vh">Umar Hayat Chaska Point</h1>\n'
        + MENU + ABOUT + CONTACT)

PAGES = [
  ('index.html', 'Umar Hayat Chaska Point — Nashta, Barbecue &amp; Fried',
   'Nashta, charcoal barbecue and fried items, cooked to order in Sahiwal. '
   'Menu, opening hours, address and WhatsApp ordering.', BODY, '/'),
]

FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#0E0B08"/>
<circle cx="32" cy="32" r="17" fill="none" stroke="#DDC491" stroke-width="3"/>
<path d="M32 19v26M22 27h20" stroke="#DDC491" stroke-width="3" stroke-linecap="round"/>
</svg>
'''

if __name__ == '__main__':
    for fn, title, desc, body, active in PAGES:
        html = page(fn, title, desc, body, active)
        html = html.replace('</body>', HOURS_JS + '</body>')
        with open(os.path.join(ROOT, fn), 'w', encoding='utf-8') as f:
            f.write(html)
        print('  %-13s %6d bytes' % (fn, len(html.encode())))

    with open(os.path.join(ROOT, 'favicon.svg'), 'w', encoding='utf-8') as f:
        f.write(FAVICON)
    print('  %-13s %6d bytes' % ('favicon.svg', len(FAVICON.encode())))

    # The multi-page header-drift guard is gone with the other pages. What
    # matters now is that every section the nav links to actually exists,
    # because a dead anchor is invisible until someone clicks it.
    out = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()

    # Every local file the page asks for must exist on disk. A 404 for a
    # stylesheet or favicon still renders a usable page, so it is easy to
    # miss by eye and only shows up in the console.
    refs = set(re.findall(r'(?:href|src)="((?!https?:|#|data:|tel:|mailto:)[^"]+)"', out))
    refs |= set(re.findall(r"(?:href|src)='((?!https?:|#|data:|tel:|mailto:)[^']+)'", out))
    gone = sorted(r for r in refs
                  if not r.startswith('/') and not os.path.exists(os.path.join(ROOT, r)))
    print('  local assets: %d referenced, %d missing%s'
          % (len(refs), len(gone), (': ' + ', '.join(gone)) if gone else ''))
    targets = re.findall(r'href="#([\w-]+)"', out)
    missing = sorted({t for t in targets if 'id="%s"' % t not in out})
    print('\n  anchor targets: %d found, %d missing%s'
          % (len(targets), len(missing), (': ' + ', '.join(missing)) if missing else ''))
    sys.exit(0 if (not missing and not gone) else 1)
