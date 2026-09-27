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

# Every image the site can show is a slot named by its filename in img/.
# Drop a file in and it appears; leave it out and an empty frame renders in
# its place, so the page never shows a broken image icon and the layout
# never reflows when the photo arrives.
# Only the menu carries photos. Slots elsewhere on the site were removed
# on request, so keep this table to the menu plus the social share card.
SLOTS = {
    'nashta':    ('16/9', 'Nashta'),
    'barbecue':  ('16/9', 'Barbecue'),
    'fried':     ('16/9', 'Fried items'),
    'social':    ('1200/630', 'Social share card'),
}
EXTS = ('.jpg', '.jpeg', '.png', '.webp', '.avif')

def find_image(key):
    for ext in EXTS:
        path = os.path.join(IMG_DIR, key + ext)
        if os.path.exists(path):
            return key + ext
    return None

def fig(key, cls='', eager=False, cap=''):
    """Render one image slot.

    A real file becomes a <img> with the alt text from SLOTS. A missing
    file becomes an empty frame of the same aspect ratio, labelled with
    the filename to drop in, so the gap is obvious in the browser.
    """
    ratio, alt = SLOTS[key]
    found = find_image(key)
    inner = ('<img src="/img/%s" alt="%s" loading="%s" decoding="async"%s>'
             % (found, alt, 'eager' if eager else 'lazy',
                ' fetchpriority="high"' if eager else '')) if found else (
        '<span class="fig-slot">'
        '<span class="fig-slot-ico" aria-hidden="true">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">'
        '<rect x="3" y="5" width="18" height="14" rx="2"/>'
        '<circle cx="8.5" cy="10" r="1.6"/>'
        '<path d="m4 17 5-4 4 3 3-2 4 3" stroke-linecap="round" stroke-linejoin="round"/>'
        '</svg></span>'
        '<span class="fig-slot-txt">img/%s</span></span>' % key)
    label = '<figcaption class="fig-cap">%s</figcaption>' % cap if cap else ''
    return ('<figure class="fig %s" style="--fig-ar:%s">'
            '<div class="fig-frame">%s</div>%s</figure>'
            % (cls, ratio, inner, label))

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
NAV = [
    ('Home',     '/'),
    ('Menu',     '/menu'),
    ('About Us', '/about'),
    ('Contact',  '/contact'),
]

def nav_links(active):
    """Primary nav. Used in the topbar AND the mobile drawer, so the two
    can never disagree about what the current page is."""
    return '\n'.join(
        f'      <a href="{href}" data-nav="page"'
        + (' aria-current="page"' if href == active else '') + f'>{lbl}</a>'
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
      <a class="nav-cta" href="/contact">Order Now</a>
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
 ('halwa-puri','Halwa Puri','nashta',180,['Regular','Large'],
  'Hot puri, sweet halwa and chana, served with a spoon of ghee.'),
 ('choley-bhature','Choley Bhature','nashta',320,['Single','Pair'],
  'Punjabi chickpeas with a fried bread. Breakfast of champions.'),
 ('samosa-puri','Samosa (2 pc)','nashta',120,[],
  'Crushed inside, aloo and peas, with chutney.'),
 ('aloo-paratha','Aloo Paratha','nashta',130,['Single','Pair'],
  'Flaky paratha with spiced potato filling.'),
 ('sheermal','Sheermal','nashta',150,['1 pc','2 pc'],
  'Saffron-tinted milk bread, best with chai.'),
 ('bun-maska','Bun Maska','nashta',110,[],
  'Butter-fried bun with butter, straight off the tawa.'),
 ('dahi-bhalla','Dahi Bhalla','nashta',180,[],
  'Soft lentil dumplings in thick yoghurt.'),
 ('nihari','Nihari','nashta',420,['Regular'],
  'Shank stew simmered overnight with ginger and achar.'),

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
 ('chicken-pakora','Chicken Pakora','fried',380,['250g','500g'],
  'Gram-flour battered chicken, fried to order.'),
 ('fried-wings','Fried Chicken Wings','fried',420,['6 pc','12 pc'],
  'Crisp wings with a choice of buffalo or BBQ glaze.'),
 ('nuggets','Chicken Nuggets','fried',350,['6 pc','12 pc'],
  'Breading made in-house, with dip.'),
 ('fries','French Fries','fried',200,['Regular','Large'],
  'Double-cooked, salted on request.'),
 ('loaded-fries','Loaded Fries','fried',380,[],
  'Cheese sauce, jalape&ntilde;os and coriander.'),
 ('egg-fried','Fried Egg','fried',80,['1 pc','2 pc'],
  'Crisp edges, any way you like it.'),
 ('fried-chicken-piece','Fried Chicken (2 pc)','fried',480,[],
  'Buttermilk-brisketed, fried to order.'),
 ('shami-kebab-fried','Fried Shami Kebab','fried',390,[],
  'Shami kebab flattened and fried, with chutney.'),
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

HOME = f'''  <section class="wrap" style="text-align:center">
    <p class="eyebrow" style="color:var(--accent);font-size:.68rem;font-weight:700;letter-spacing:.24em;text-transform:uppercase;margin-bottom:18px">Nashta &middot; Barbecue &middot; Fried</p>
    <h1 style="font-size:clamp(2.2rem,6vw,4rem);max-width:17ch;margin:0 auto 20px">Charcoal-grilled barbecue and nashta done properly</h1>
    <p style="color:var(--fg-muted);max-width:52ch;margin:0 auto 32px;line-height:1.85">
      Fried batter mixed by hand, malai boti marinated overnight, and
      breakfast served from the time the shop opens.</p>
    <div class="band-cta">
      <a class="btn btn-accent" href="/menu">See the menu</a>
      <a class="btn btn-ghost" href="/contact">Find us</a>
    </div>
  </section>
'''

MENU = f'''  <div class="wrap">
    <header class="page-head">
      <p class="eyebrow">{ICON['bag']} Menu</p>
      <h1>The menu</h1>
      <p>Nashta from opening time, barbecue over charcoal in the evening, and
        fried items to order throughout. Prices are shown in your selected
        currency.</p>
    </header>

    <div class="filters" role="group" aria-label="Filter by category">
{cat_buttons()}
      <span class="price-note" id="filterCount" style="align-self:center;margin-left:auto"></span>
    </div>

    <div class="grid grid--3" style="margin-bottom:44px">
{fig('nashta', 'fig--cat', cap='Nashta')}
{fig('barbecue', 'fig--cat', cap='Barbecue')}
{fig('fried', 'fig--cat', cap='Fried Items')}
    </div>

    <div class="grid grid--menu">
{MENU_CARDS}
    </div>
  </div>'''

ABOUT = f'''  <div class="wrap">
    <header class="page-head">
      <p class="eyebrow">{ICON['user']} About Us</p>
      <h1>Our story</h1>
      <p>A roadside nashta stall that grew into a proper barbecue kitchen.</p>
    </header>

    <div class="detail" style="grid-template-columns:1fr 1fr">
      <div>
        <h2>What we cook</h2>
        <p>Three things, done properly. Nashta in the morning, barbecue in the
          evening, and fried items whenever the grill is between batches.</p>
        <ul class="list">
          <li>Halwa puri, choley bhature, samosa and sheermal to start the day</li>
          <li>Malai boti, seekh kebab and tikka off the charcoal</li>
          <li>Pakoras, wings, nuggets and fries battered and fried to order</li>
        </ul>
        <a class="btn btn-accent" href="/menu">See the menu</a>
      </div>
      <div>
        <h2>How we cook</h2>
        <ul class="list">
          <li>Chicken and meat marinated overnight, never the same day</li>
          <li>Live charcoal, skewers turned by hand</li>
          <li>Batter mixed in small batches through the day</li>
        </ul>
        <a class="btn btn-ghost" href="/contact">Find us</a>
      </div>
    </div>
  </div>'''

CONTACT = f'''  <div class="wrap">
    <header class="page-head">
      <p class="eyebrow">{ICON['pin']} Locations &amp; Contact</p>
      <h1>Find us</h1>
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
        <h2 style="font-size:1.4rem;margin-bottom:18px">Opening hours</h2>
        <div class="hours" id="hours"></div>
        <p class="note">Hours are rendered from
          <code>SITE.hours</code> so they stay in step with the config.</p>
      </div>
    </div>
  </div>'''

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

PAGES = [
  ('index.html',   'Umar Hayat Chaska Point — Nashta, Barbecue &amp; Fried',
   'Nashta, charcoal barbecue and fried items, cooked to order in Sahiwal.', HOME, '/'),
  ('menu.html',    'Menu — Umar Hayat Chaska Point',
   'Nashta, charcoal barbecue and fried items, cooked to order.', MENU, '/menu'),
  ('about.html',   'About Us — Umar Hayat Chaska Point',
   'A roadside nashta stall that grew into a proper barbecue kitchen.', ABOUT, '/about'),
  ('contact.html', 'Locations &amp; Contact — Umar Hayat Chaska Point',
   'Find us in Sahiwal. Opening hours, address and WhatsApp ordering.',
   CONTACT, '/contact'),
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
        if fn == 'contact.html':
            html = html.replace('</body>', HOURS_JS + '</body>')
        with open(os.path.join(ROOT, fn), 'w', encoding='utf-8') as f:
            f.write(html)
        print('  %-13s %6d bytes' % (fn, len(html.encode())))

    with open(os.path.join(ROOT, 'favicon.svg'), 'w', encoding='utf-8') as f:
        f.write(FAVICON)
    print('  %-13s %6d bytes' % ('favicon.svg', len(FAVICON.encode())))

    # Guard against the drift this generator exists to prevent.
    heads = [re.search(r'<header class="site-hdr">.*?</header>', open(os.path.join(ROOT, p[0]), encoding='utf-8').read(), re.S).group(0) for p in PAGES]
    norm = lambda h: re.sub(r'\s+', ' ', re.sub(r'\s*aria-current="page"', '', h))
    same = len({norm(h) for h in heads}) == 1
    print('\n  header identical across all %d pages: %s' % (len(PAGES), 'YES' if same else 'NO — DRIFT'))
    sys.exit(0 if same else 1)
