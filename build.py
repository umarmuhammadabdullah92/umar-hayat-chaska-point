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
    """The component. Identical on every page except aria-current."""
    cats = [('Chasha','chasha'),('Chaat','chaat'),('Fast Food','fastfood'),
            ('Beverages','beverages'),('Deals','deals')]

    cat_links = '\n'.join(
        f'      <a href="/menu#{cid}" data-nav="cat" data-cat="{cid}">{lbl}</a>'
        for lbl, cid in cats)

    return f'''<a class="skip" href="#main">Skip to content</a>

<header class="site-hdr">
  <div class="topbar">
    <div class="topbar-side topbar-side--l">
      <button class="ham" type="button" id="hamburger"
              aria-label="Open menu" aria-expanded="false" aria-controls="drawer">
        <span></span><span></span><span></span>
      </button>
      <a class="hdr-contact" href="tel:+923000000000">{ICON['phone']}<span>Order by phone</span></a>
      <span class="hdr-tagline">Chashai &amp; Chaat</span>
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

  <nav class="catnav" aria-label="Categories">
    <div class="catnav-in">
{nav_links(active)}
{cat_links}
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
      <input type="search" id="searchInput" placeholder="Search chasha, chaat, drinks&hellip;"
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
    <a href="/contact">{ICON['phone']} Order by phone</a>
    <small>Chashai &amp; chaat, made to order.<br>Placeholder details &mdash; see README.</small>
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
<meta property="og:image" content="/umarhayatchaskapoint-trimmed.png">
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
 ('chasha-classic','Chasha Classic','chasha',450,['Regular','Large'],
  'Slow-cooked mutton, rice, fried onion and spices.'),
 ('chasha-special','Chasha Special','chasha',720,['Regular','Large'],
  'Mutton and chicken together, with a fried egg on top.'),
 ('chasha-beef','Beef Chasha','chasha',520,['Regular','Large'],
  'Beef shank, potato and rice.'),
 ('chasha-chicken','Chicken Chasha','chasha',480,['Regular','Large'],
  'Chicken, rice, ginger and fried onion.'),
 ('chapati-roll','Chapati Roll','chaat',260,[],
  'Flaky chapati, raita, onion and chutney, rolled to order.'),
 ('papri-chaat','Papri Chaat','chaat',340,[],
  'Crisp papri, raita, tamarind and yoghurt drizzle.'),
 ('dahi-phulki','Dahi Phulki','chaat',290,[],
  'Soft buns soaked in sweetened yoghurt.'),
 ('samosa-chaat','Samosa Chaat','chaat',320,[],
  'Crushed samosa, chana, yoghurt and chutneys.'),
 ('zinger-burger','Zinger Burger','fastfood',480,['Single','Double'],
  'Crispy chicken fillet in a toasted bun.'),
 ('club-sandwich','Club Sandwich','fastfood',420,[],
  'Chicken, cheese, salad and mayo, triple-decker.'),
 ('loaded-fries','Loaded Fries','fastfood',350,[],
  'Fries with cheese sauce, jalape&ntilde;os and herbs.'),
 ('chashai-pulao','Special Pulao','deals',650,['Regular','Large'],
  'Basmati rice with bone-in mutton.'),
 ('family-box','Family Feast Box','deals',2450,['Serves 4'],
  'Two chashas, two rolls, fries and two drinks.'),
 ('doodh-patti','Doodh Patti','beverages',180,['Regular','Large'],
  'Sweet thickened milk, served chilled.'),
 ('lassi','Sweet Lassi','beverages',260,['Regular','Large'],
  'Yoghurt drink blended with ice.'),
 ('mango-malai','Mango Malai','beverages',320,['Regular'],
  'Mango pulp and cream.'),
 ('soft-drink','Soft Drink','beverages',150,['Can','Bottle'],
  'Chilled, ask for flavours.'),
 ('chai','Masala Chai','beverages',120,['Cup'],
  'Slow-boiled with whole spices.'),
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

SITE_CATS = [('Chasha','chasha'),('Chaat','chaat'),('Fast Food','fastfood'),
             ('Beverages','beverages'),('Deals','deals')]

HOME = f'''  <section class="wrap" style="text-align:center">
    <p class="eyebrow" style="color:var(--accent);font-size:.68rem;font-weight:700;letter-spacing:.24em;text-transform:uppercase;margin-bottom:18px">Chashai &amp; Chaat</p>
    <h1 style="font-size:clamp(2.2rem,6vw,4rem);max-width:16ch;margin:0 auto 20px">Slow-cooked chasha, made the long way</h1>
    <p style="color:var(--fg-muted);max-width:52ch;margin:0 auto 32px;line-height:1.85">
      Mutton simmered overnight until it falls apart, poured over rice you
      want to eat straight from the bowl.</p>
    <div class="band-cta">
      <a class="btn btn-accent" href="/menu">See the menu</a>
      <a class="btn btn-ghost" href="/contact">Find us</a>
    </div>
  </section>

  <section class="band">
    <h2>This is a static demo</h2>
    <p>The header, navigation, search, currency selector and cart all work,
      but there is no server behind them. Menu items and prices are
      placeholders.</p>
    <div class="band-cta">
      <a class="btn btn-ghost" href="/about">About Us</a>
      <a class="btn btn-ghost" href="/menu">Menu</a>
    </div>
  </section>'''

MENU = f'''  <div class="wrap">
    <header class="page-head">
      <p class="eyebrow">{ICON['bag']} Menu</p>
      <h1>The menu</h1>
      <p>Everything is cooked to order, so allow a little time at busy hours.
        Prices are shown in your selected currency.</p>
    </header>

    <div class="filters" role="group" aria-label="Filter by category">
{cat_buttons()}
      <span class="price-note" id="filterCount" style="align-self:center;margin-left:auto"></span>
    </div>

    <div class="todo" style="margin-bottom:32px">
      <h2>Placeholder data</h2>
      <p>The {len(ITEMS)} items below are <strong>invented</strong> so the layout has
        something to render. Names, descriptions and prices are not real and
        must be replaced before launch &mdash; see <code>README.md</code>.</p>
    </div>

    <div class="grid grid--menu">
{MENU_CARDS}
    </div>
  </div>'''

ABOUT = f'''  <div class="wrap">
    <header class="page-head">
      <p class="eyebrow">{ICON['user']} About Us</p>
      <h1>Our story</h1>
      <p>A family kitchen that grew into a neighbourhood chasha house.</p>
    </header>

    <div class="todo" style="margin-bottom:40px">
      <h2>Placeholder copy</h2>
      <p>This page is an empty frame. The real story, the founder&rsquo;s name,
        the years in business and the kitchen photographs all still need to be
        written. See <code>README.md</code>.</p>
    </div>

    <div class="detail" style="grid-template-columns:1fr 1fr">
      <div>
        <h2>What we cook</h2>
        <p>Chasha is the centre of the menu &mdash; a whole pot of meat and
          rice, finished with fried onion and ginger. It is not assembled to
          order; it is one pot, and it is why we run out.</p>
        <ul class="list">
          <li>Mutton and chicken chasha, plus beef and vegetarian</li>
          <li>Chaat built on the same dough, fried to order</li>
          <li>Rolls, burgers and loaded fries for the younger crowd</li>
        </ul>
        <a class="btn btn-accent" href="/menu">See the menu</a>
      </div>
      <div>
        <h2>How we cook</h2>
        <p>Placeholder. The method, the sourcing and the equipment notes are
          all still to be written.</p>
        <ul class="list">
          <li>Meat from a named local supplier</li>
          <li>Rice washed and soaked the same morning</li>
          <li>No shortcuts in the biryani masala</li>
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

    <div class="todo" style="margin-bottom:40px">
      <h2>Placeholder details</h2>
      <p>The address, phone number, opening hours and map below are
        <strong>invented</strong>. Every one of them is a single edit in
        <code>js/site-config.js</code>. Run <code>SITE.todos()</code> in the
        console to list what is still outstanding.</p>
    </div>

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
  ('index.html',   'Umar Hayat Chaska Point — Chashai &amp; Chaat',
   'Slow-cooked chasha and chaat. Order by phone or WhatsApp.', HOME, '/'),
  ('menu.html',    'Menu — Umar Hayat Chaska Point',
   'Chasha, chaat, fast food and drinks, cooked to order.', MENU, '/menu'),
  ('about.html',   'About Us — Umar Hayat Chaska Point',
   'A family kitchen that grew into a neighbourhood chasha house.', ABOUT, '/about'),
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
