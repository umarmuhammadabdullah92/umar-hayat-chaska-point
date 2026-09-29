#!/usr/bin/env python3
"""
Builds the site: one page, generated from js/site-config.js.

    python3 build.py

Everything on the page is written here. The chrome (header, footer,
overlays) exists once, as Python strings, so a change to the header
cannot be applied in one place and forgotten in another. index.html is
generated output: never hand-edit it.

The business details — name, address, phone, hours, menu categories,
reservation slots — live in js/site-config.js, because they are also
needed at runtime by the browser. build.py reads that file and bakes
them into the HTML, which is what keeps a single source of truth while
still producing a page that works with JavaScript switched off.

The build fails on anything that renders a broken page: a nav anchor
with no section, a referenced file that is not on disk, a dish in a
category nobody filters to, or a duplicated element id.
"""

import os
import re
import sys
import json
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(ROOT, 'img')

# Menu prices are authored in PKR integers, and a price of exactly this
# value means "no real price yet". It is deliberately round so it is
# obviously not a price anyone charged, and every build reports each one.
PRICE_TODO = 999


# ===================================================================
# js/site-config.js  ->  a Python dict
# ---------------------------------------------------------------------
# site-config.js is the one place a non-programmer edits the business,
# so it is written as a comment-rich JS object literal rather than JSON.
# This parses exactly that dialect: objects, arrays, quoted and bare
# keys, strings with escapes, numbers, true/false/null, // and /* */
# comments and trailing commas. Anything else raises, so a malformed
# edit fails the build instead of silently producing a blank section.

class ConfigError(Exception):
    pass


class _JS:
    """A recursive-descent parser for one JS object literal."""

    def __init__(self, src):
        self.s = src
        self.i = 0

    def ws(self):
        s, n = self.s, len(self.s)
        while self.i < n:
            c = s[self.i]
            if c in ' \t\r\n':
                self.i += 1
            elif c == '/' and self.i + 1 < n and s[self.i + 1] == '/':
                j = s.find('\n', self.i)
                self.i = n if j < 0 else j + 1
            elif c == '/' and self.i + 1 < n and s[self.i + 1] == '*':
                j = s.find('*/', self.i + 2)
                if j < 0:
                    raise ConfigError('unterminated /* comment')
                self.i = j + 2
            else:
                return

    def value(self):
        v = self.atom()
        # JS string concatenation, so long copy can be wrapped across
        # source lines. The result is always a string, because the only
        # thing in this file that uses + is a string being continued.
        while True:
            save = self.i
            self.ws()
            if self.i < len(self.s) and self.s[self.i] == '+':
                self.i += 1
                v = str(v) + str(self.atom())
            else:
                self.i = save
                return v

    def atom(self):
        self.ws()
        if self.i >= len(self.s):
            raise ConfigError('unexpected end of file')
        c = self.s[self.i]
        if c == '{':
            return self.obj()
        if c == '[':
            return self.arr()
        if c in '"\'':
            return self.string()
        for word, val in (('true', True), ('false', False), ('null', None)):
            if self.s.startswith(word, self.i):
                self.i += len(word)
                return val
        return self.number()

    def obj(self):
        self.i += 1  # {
        out = {}
        while True:
            self.ws()
            if self.i >= len(self.s):
                raise ConfigError('unterminated object')
            if self.s[self.i] == '}':
                self.i += 1
                return out
            key = self.string() if self.s[self.i] in '"\'' else self.bare()
            self.ws()
            if self.i >= len(self.s) or self.s[self.i] != ':':
                raise ConfigError('expected ":" after key %r' % key)
            self.i += 1
            out[key] = self.value()
            self.ws()
            if self.i < len(self.s) and self.s[self.i] == ',':
                self.i += 1
            elif self.i < len(self.s) and self.s[self.i] != '}':
                raise ConfigError('expected "," or "}" in object')

    def arr(self):
        self.i += 1  # [
        out = []
        while True:
            self.ws()
            if self.i >= len(self.s):
                raise ConfigError('unterminated array')
            if self.s[self.i] == ']':
                self.i += 1
                return out
            out.append(self.value())
            self.ws()
            if self.i < len(self.s) and self.s[self.i] == ',':
                self.i += 1
            elif self.i < len(self.s) and self.s[self.i] != ']':
                raise ConfigError('expected "," or "]" in array')

    def string(self):
        q = self.s[self.i]
        self.i += 1
        buf = []
        while True:
            if self.i >= len(self.s):
                raise ConfigError('unterminated string')
            c = self.s[self.i]
            if c == '\\':
                nxt = self.s[self.i + 1]
                if nxt == 'u':
                    m = re.compile(r'[0-9a-fA-F]{4}').match(self.s, self.i + 2)
                    if not m:
                        raise ConfigError('bad \\u escape')
                    buf.append(chr(int(m.group(0), 16)))
                    self.i = m.end()
                else:
                    buf.append({'n': '\n', 't': '\t', 'r': '\r', 'b': '\b',
                                'f': '\f', '0': '\0'}.get(nxt, nxt))
                    self.i += 2
            elif c == q:
                self.i += 1
                return ''.join(buf)
            else:
                buf.append(c)
                self.i += 1

    def bare(self):
        m = re.compile(r'[A-Za-z_$][A-Za-z0-9_$]*').match(self.s, self.i)
        if not m:
            raise ConfigError('expected a key at %r' % self.s[self.i:self.i + 20])
        self.i = m.end()
        return m.group(0)

    def number(self):
        m = re.compile(r'-?\d+(?:\.\d+)?').match(self.s, self.i)
        if not m:
            raise ConfigError('expected a value at %r' % self.s[self.i:self.i + 20])
        self.i = m.end()
        text = m.group(0)
        return float(text) if '.' in text else int(text)


def load_config():
    """Read window.SITE = {...} out of js/site-config.js.

    Only the object literal is parsed. The SITE.todos() function that
    follows it is left alone, so the file can stay ordinary readable
    JavaScript with comments in it.
    """
    path = os.path.join(ROOT, 'js', 'site-config.js')
    src = open(path, encoding='utf-8').read()
    start = re.search(r'window\.SITE\s*=\s*', src)
    if not start:
        raise ConfigError('no "window.SITE =" in js/site-config.js')
    p = _JS(src)
    p.i = start.end()
    try:
        cfg = p.value()
    except ConfigError as e:
        raise ConfigError('js/site-config.js: %s' % e)
    if not isinstance(cfg, dict):
        raise ConfigError('window.SITE must be an object')
    return cfg


try:
    C = load_config()
except ConfigError as e:
    sys.exit('build.py: %s' % e)


def need(*path):
    """Fetch a nested config value, failing loudly rather than with a
    TypeError three frames deep in the middle of a template."""
    v = C
    for k in path:
        if not isinstance(v, dict) or k not in v:
            raise ConfigError('site-config.js is missing %s' % '.'.join(path))
        v = v[k]
    return v


def esc(s):
    """Escape text for use in HTML body content or a double-quoted
    attribute. Config values come from a human-editable file, so they
    are treated as untrusted."""
    return (str(s).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


# ===================================================================
# Images
# ---------------------------------------------------------------------
# Every photograph on the site is a slot with a fixed aspect ratio, so
# the layout cannot reflow when real photography lands. Naming a file
# after the slot key is all it takes; there is no markup to edit.

EXTS = ('.jpg', '.jpeg', '.png', '.webp', '.avif', '.svg')


def find_image(key):
    for ext in EXTS:
        if os.path.exists(os.path.join(IMG_DIR, key + ext)):
            return key + ext
    return None


def read_palette(*names):
    """Custom properties out of the :root block in css/style.css.

    Read rather than repeated here, because a colour written twice is a
    colour that has to be changed twice: the manifest and the
    <meta name="theme-color"> already quote the page ground, and a
    palette edit that missed them would show a home-screen icon on a
    background the site does not use."""
    src = open(os.path.join(ROOT, 'css', 'style.css'), encoding='utf-8').read()
    root = re.search(r':root\s*\{(.*?)\}', src, re.S)
    if not root:
        raise ConfigError('no :root block in css/style.css')
    out = {}
    for name in names:
        m = re.search(r'--%s\s*:\s*(#[0-9A-Fa-f]{3,8})' % re.escape(name), root.group(1))
        if not m:
            raise ConfigError('css/style.css :root has no --%s' % name)
        out[name] = m.group(1)
    return out


# ===================================================================
# Icons
# ---------------------------------------------------------------------

ICON = {
    'search': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    'arrow':  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h13"/><path d="m12 6 6 6-6 6"/></svg>',
    'down':   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v13"/><path d="m6 12 6 6 6-6"/></svg>',
    'phone':  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3h3l2 5-2.5 1.5a12 12 0 0 0 6 6L16 13l5 2v3a2 2 0 0 1-2.2 2A17 17 0 0 1 4 6.2 2 2 0 0 1 6 3Z"/></svg>',
    'pin':    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s7-5.5 7-11a7 7 0 1 0-14 0c0 5.5 7 11 7 11Z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    'clock':  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5.5l3.5 2"/></svg>',
    'mail':   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6.5 8.5 6 8.5-6"/></svg>',
    'x':      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M5 5l14 14M19 5 5 19"/></svg>',
    'at':     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-4 8"/></svg>',
}

SOCIAL_ICON = {
    'instagram': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><rect x="2.6" y="2.6" width="18.8" height="18.8" rx="5.4"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.5" cy="6.5" r="1.15" fill="currentColor" stroke="none"/></svg>',
    'facebook':  '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.5 21v-8h2.7l.4-3.1h-3.1V7.9c0-.9.25-1.5 1.55-1.5h1.65V3.6c-.29-.04-1.27-.13-2.41-.13-2.39 0-4.02 1.46-4.02 4.13V9.9H7.5V13h2.77v8h3.23Z"/></svg>',
    'tiktok':    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.6 5.82A4.28 4.28 0 0 1 15.54 3h-3.09v12.4a2.59 2.59 0 0 1-2.59 2.5 2.59 2.59 0 0 1 0-5.18c.27 0 .52.04.76.12V9.66a5.68 5.68 0 0 0-.76-.05A5.66 5.66 0 1 0 15.54 15.3V9.01a7.35 7.35 0 0 0 4.3 1.38V7.3a4.29 4.29 0 0 1-3.24-1.48Z"/></svg>',
}


def social_links():
    """SITE.social out of the config, so there is one place to edit the
    URLs. Raise rather than guess: a broken edit should fail the build,
    not publish an icon that links nowhere."""
    block = need('social')
    out = []
    for key, url in block.items():
        url = (url or '').strip()
        if not url:
            continue
        if key not in SOCIAL_ICON:
            raise ConfigError('no icon defined for social key %r' % key)
        out.append((key, url, SOCIAL_ICON[key]))
    if not out:
        raise ConfigError('SITE.social has no filled-in URLs')
    return out


def social_markup(indent='      '):
    return '\n'.join(
        '%s<a class="soc" href="%s" target="_blank" rel="noopener noreferrer" '
        'aria-label="%s">%s</a>'
        % (indent, esc(url), esc(key.capitalize()), icon)
        for key, url, icon in social_links())


# ===================================================================
# Chrome
# ---------------------------------------------------------------------
# The site is several pages, so the nav is a list of pages and each page
# marks itself with aria-current="page". There is no scroll spy any more:
# marking the section being read made sense on one long page, but with
# real pages the page itself is the thing you are on, and the server
# already knows which one that is.
#
# Each entry is (filename, url, label, in_nav). The url is what links
# must use; the filename is what the build writes. in_nav is False for
# the reservation, which is reached through the standing button rather
# than a quiet link in the list.
#
PAGES = [
    ('index.html',          '/',               'Home',            True),
    ('menu.html',           '/menu',           'Menu',            True),
    ('story.html',          '/story',          'Our Story',       True),
    ('private-dining.html', '/private-dining', 'Private Dining',  True),
    ('visit.html',          '/visit',          'Visit',           True),
    ('reserve.html',        '/reserve',        'Reserve a table', False),
]

RESERVE = '/reserve'


def url_for(name):
    """The url of a page, by its filename. Used by the build to keep
    body links pointing at real pages instead of at anchors."""
    for fn, url, _label, _nav in PAGES:
        if fn == name:
            return url
    raise KeyError('no such page: ' + name)


def aria_current(current, url):
    """Marks the link that points at the page already open.

    The Reserve button is a call to action rather than a nav item, so
    nav_links never marks it. Without this the reserve page has nothing
    marked anywhere in the header, and the one page a guest most needs
    to recognise is the one that does not say where it is."""
    return ' aria-current="page"' if url == current else ''


def nav_links(current):
    out = []
    for _fn, url, label, in_nav in PAGES:
        if not in_nav:
            continue
        cur = ' aria-current="page"' if url == current else ''
        out.append('      <a href="%s" data-nav="page"%s>%s</a>' % (url, cur, label))
    return '\n'.join(out)


def header(current):
    phone = need('phone')
    tel = need('phoneHref')
    return '''<a class="skip" href="#main">Skip to content</a>

<header class="site-hdr" id="siteHdr">
  <div class="topbar">
    <div class="topbar-l">
      <button class="ham" type="button" id="hamburger"
              aria-label="Open menu" aria-expanded="false" aria-controls="drawer">
        <span></span><span></span><span></span>
      </button>
      <a class="topbar-tel" href="tel:{tel}">{phoneicon}
        <span>{phone}</span></a>
    </div>

    <a class="logo" href="/">
      <span class="wordmark">{name}</span>
    </a>

    <div class="topbar-r">
      <button class="uicon uico-hide" type="button" data-open="search"
              aria-label="Search the menu" aria-haspopup="dialog">{search}</button>
      <a class="btn btn-gold btn-sm topbar-cta" href="{reserve}"{rc}>Reserve a table</a>
    </div>
  </div>

  <nav class="mainnav" aria-label="Primary">
    <div class="mainnav-in">
{nav}
      <a class="nav-cta" href="{reserve}"{rc}>Reserve</a>
    </div>
  </nav>
</header>'''.format(
        tel=esc(tel), phone=esc(phone), name=esc(need('name')),
        phoneicon=ICON['phone'], search=ICON['search'],
        nav=nav_links(current), reserve=RESERVE,
        rc=aria_current(current, RESERVE))


def overlays(current):
    """Search sheet and the mobile drawer. There is no cart and no
    account: this is a restaurant that takes reservations, not a shop
    that takes payments."""
    return '''
<div class="scrim" id="sheetScrim"></div>
<div class="scrim" id="mobScrim"></div>

<!-- search ------------------------------------------------------------ -->
<section class="sheet" id="searchSheet" role="dialog" aria-modal="true"
         aria-label="Search the menu" inert>
  <div class="sheet-hd">
    <h2>Search the menu</h2>
    <button class="icon-btn" type="button" id="searchClose" data-close aria-label="Close search">{x}</button>
  </div>
  <div class="sheet-in">
    <div class="sfield">
      {search}
      <input type="search" id="searchInput" placeholder="Nashta, barbecue, fried&hellip;"
             autocomplete="off" spellcheck="false" aria-label="Search the menu">
    </div>
    <p class="results-hint" id="searchHint">Start with these</p>
    <div class="results" id="searchResults"></div>
  </div>
</section>

<!-- mobile drawer ----------------------------------------------------- -->
<aside class="drawer" id="drawer" aria-label="Menu" inert>
  <button class="icon-btn drawer-x" type="button" id="drawerClose" aria-label="Close menu">{x}</button>
  <nav class="drawer-nav" aria-label="Mobile">
{nav}
  </nav>
  <a class="btn btn-gold drawer-cta" href="{reserve}"{rc}>Reserve a table</a>
  <div class="drawer-foot">
    <nav class="social" aria-label="Social media">
{soc}
    </nav>
    <a class="drawer-tel" href="tel:{tel}">{phone}</a>
    <small>{tagline}</small>
  </div>
</aside>'''.format(
        x=ICON['x'], search=ICON['search'], nav=nav_links(current),
        reserve=RESERVE, soc=social_markup('    '),
        rc=aria_current(current, RESERVE),
        tel=esc(need('phoneHref')),
        phone=esc(need('phone')), tagline=esc(need('tagline')))


def footer():
    addr = need('address')
    hours = hours_table()
    return '''<footer class="site-foot">
  <div class="wrap foot-top">
    <div class="foot-brand">
      <p class="foot-mark">{name}</p>
      <p class="foot-tag">{tagline}</p>
      <p class="foot-est">{est}</p>
      <nav class="social" aria-label="Social media">
{soc}
      </nav>
    </div>

    <nav class="foot-col" aria-label="Footer">
      <h2>Explore</h2>
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/menu">The menu</a></li>
        <li><a href="/story">Our story</a></li>
        <li><a href="/private-dining">Private dining</a></li>
        <li><a href="/visit">Visit us</a></li>
        <li><a href="/reserve">Reserve a table</a></li>
      </ul>
    </nav>

    <div class="foot-col">
      <h2>Visit</h2>
      <address>
        {l1}<br>{l2}<br>{city} {post}<br>{country}
      </address>
      <a href="tel:{tel}">{phone}</a>
      <a href="https://wa.me/{wa}" rel="noopener">WhatsApp</a>
    </div>

    <div class="foot-col">
      <h2>Hours</h2>
      {hours}
    </div>
  </div>

  <div class="wrap foot-bot">
    <small>&copy; 2026 {name}</small>
    <small>Reservations are a request. We confirm by phone.</small>
  </div>
</footer>'''.format(
        name=esc(need('name')), tagline=esc(need('tagline')),
        est=esc(need('est')), soc=social_markup('        '),
        l1=esc(addr['line1']), l2=esc(addr['line2']), city=esc(addr['city']),
        post=esc(addr.get('postcode', '')), country=esc(addr['country']),
        tel=esc(need('phoneHref')), phone=esc(need('phone')),
        wa=esc(need('whatsapp')), hours=hours)


# ===================================================================
# The menu
# ---------------------------------------------------------------------
# (id, name, category, price in PKR, tags, description, service note)
#
# The nashta and fried dishes are the real menu, supplied by the owner.
# Their spellings are theirs, with three deliberate exceptions: "Samosy"
# and "Pakory" were respelled to the standard Samosa and Pakora, and
# "Pakore" likewise. "Began" and "Mirch" were left as written, because
# those are regional spellings rather than typos.
#
# The barbecue list is INVENTED, as are every description and every
# price. Prices of exactly %d mean "no real price yet"; every other
# price is a plausible invention. build.py lists both on every run.
#
# Prices are shown exactly as authored. A restaurant menu quotes its own
# currency; there is no visitor-side conversion anywhere on the site.

PRICE_TODO = 999

ITEMS = [
    # --- nashta: the real dishes -------------------------------------
    ('murag-chanay', 'Murag Chanay', 'nashta', PRICE_TODO, [],
     'Chicken cooked down slowly in a dark masala until the meat gives way.',
     'Served with rice or a warm flatbread.'),
    ('anday-chanay', 'Anday Chanay', 'nashta', PRICE_TODO, [],
     'Eggs simmered in the same masala as the murag, never fried first.',
     'A full pot, or a single egg with bread.'),
    ('haleem-chawal', 'Haleem Chawal', 'nashta', PRICE_TODO, [],
     'Haleem finished with rice and fried onion, stirred at the table.',
     'Made in small pots, so it runs out.'),

    # --- barbecue: INVENTED, replace before launch -------------------
    ('malai-boti', 'Chicken Malai Boti', 'barbecue', 480, ['Signature'],
     'Cream cheese and white pepper left on the meat overnight, skewered '
     'wet, and grilled close to the coals until the outside catches.',
     'Four or eight pieces. Mint chutney alongside.'),
    ('mutton-seekh', 'Mutton Seekh Kebab', 'barbecue', 850, ['Signature'],
     'Minced mutton worked by hand with raw papaya and green chilli. No '
     'binder, so it is looser than most and better for it.',
     'Four or eight pieces. Grilled to order.'),
    ('grilled-chicken', 'Grilled Chicken', 'barbecue', 950, ['Signature'],
     'The whole bird, marinated overnight, salted at the last minute and '
     'turned over the coals for two hours.',
     'Half or full. Takes twenty minutes, so order it first.'),
    ('chicken-tikka', 'Chicken Tikka', 'barbecue', 550, [],
     'Thigh meat in yoghurt and ajwain, charred at the edges and left pink '
     'in the middle.',
     'Half or full.'),
    ('beef-boti', 'Beef Boti', 'barbecue', 780, [],
     'Sirloin in large pieces, onion and black pepper, nothing else in the '
     'marinade.',
     'Four or eight pieces.'),
    ('seekh-kebab', 'Chicken Seekh Kebab', 'barbecue', 520, [],
     'Chicken mince with coriander stem and green chilli, moulded by hand on '
     'the skewer.',
     'Four or eight pieces.'),
    ('bbq-platter-two', 'BBQ Platter for Two', 'barbecue', 2400, [],
     'Malai boti, seekh kebab, tikka, grilled chicken, naan, salad and three '
     'chutneys, for people who cannot choose.',
     'Serves two. Twenty-five minutes.'),

    # --- fried: the real dishes, standard spellings ------------------
    ('samosa-fried', 'Samosa', 'fried', PRICE_TODO, [],
     'Flaky pastry, potato and a little ajwain, crimped by hand and dropped '
     'into hot oil to order.',
     ''),
    ('pakora', 'Pakora', 'fried', PRICE_TODO, [],
     'Gram flour, onion and green chilli in a batter that is supposed to be '
     'lumpy.',
     ''),
    ('aloo-ki-tikki', 'Aloo Ki Tikki', 'fried', PRICE_TODO, [],
     'Potato and chickpea flour pressed into a patty and fried until it '
     'cracks at the edge.',
     'Served with yoghurt and tamarind.'),
    ('began-pakora', 'Began Pakora', 'fried', PRICE_TODO, [],
     'Brinjal, split and battered. The one people order twice.',
     ''),
    ('mirch-pakora', 'Mirch Pakora', 'fried', PRICE_TODO, [],
     'Green chilli, battered. Very hot, and not pretending otherwise.',
     ''),
    ('fried-naan', 'Fried Naan', 'fried', PRICE_TODO, [],
     'A ball of dough, fried rather than baked, so it is blistered and chewy '
     'at the same time.',
     ''),
]

FIELDS = ('id', 'name', 'cat', 'price', 'tags', 'desc', 'note')


def dishes():
    for row in ITEMS:
        d = dict(zip(FIELDS, row))
        d['tags'] = list(d['tags'] or [])
        yield d


def money(pkr):
    """Prices are authored in PKR integers and quoted in PKR, the way a
    menu in the room would."""
    return need('currency', 'symbol') + ' ' + format(int(pkr), ',d')


def dish_row(d):
    tags = ''.join('<span class="tag">%s</span>' % esc(t) for t in d['tags'])
    # Name and price only. The description and the service note stay in
    # ITEMS because the signature cards still use them and because they
    # are what search matches on, but the menu itself reads as a printed
    # menu: a line of names, a leader, a price. The quantity control
    # beside the price is what turns a printed menu into an order.
    return '''        <li class="dish" id="dish-{id}" data-item="{name}"
            data-anchor="dish-{id}" data-price="{price}" data-cat="{cat}">
          <div class="dish-head">
            <h3 class="dish-name">{name}{tags}</h3>
            <span class="dish-lead" aria-hidden="true"></span>
            <span class="dish-price">{price_fmt}</span>
            <span class="qty" data-qty>
              <button type="button" class="qty-btn" data-qty-sub
                aria-label="Take one out of {name}" disabled>&minus;</button>
              <span class="qty-n" data-qty-n>0</span>
              <button type="button" class="qty-btn qty-btn--add" data-qty-add
                aria-label="Add one {name}">+</button>
            </span>
          </div>
        </li>'''.format(
        id=esc(d['id']), name=esc(d['name']), tags=tags,
        price=int(d['price']), price_fmt=esc(money(d['price'])),
        cat=esc(d['cat']))


def head(level, ident, text):
    """A page or section heading at the right level.

    The top heading of a page is its <h1>; the same block reused
    further down a page is an <h2>. Passing the level in keeps that a
    decision made once, here, instead of a hand-edited tag in five
    places that have to agree."""
    tag = 'h%d' % level
    return '<%s id="%s">%s</%s>' % (tag, ident, text, tag)


def order_bar():
    """The sticky tray at the bottom of the menu page.

    It is in the markup, empty and hidden, so the page never depends on
    js/order.js: without JavaScript it stays hidden and the fine print
    above sends the guest to the phone instead."""
    note = need('ordering', 'note')
    return '''  <div class="orderbar" id="orderBar" hidden>
    <div class="wrap orderbar-in">
      <p class="orderbar-what">
        <span class="orderbar-count" id="orderCount" aria-live="polite">0 items</span>
        <span class="orderbar-sep" aria-hidden="true"></span>
        <span class="orderbar-total" id="orderTotal">{zero}</span>
      </p>
      <div class="orderbar-acts">
        <button type="button" class="btn btn-wa" id="orderSend" disabled>Send order</button>
        <button type="button" class="orderbar-clear" id="orderClear">Clear the order</button>
      </div>
      <p class="orderbar-note">{note}</p>
    </div>
  </div>'''.format(zero=esc(money(0)), note=esc(note))


def menu_section(level=2):
    cats = need('categories')
    groups = []
    for c in cats:
        rows = [dish_row(d) for d in dishes() if d['cat'] == c['id']]
        if not rows:
            continue
        groups.append('''      <div class="cat" id="{id}">
        <header class="cat-head">
          <h3>{label}</h3>
          <span class="cat-rule" aria-hidden="true"></span>
        </header>
        <p class="cat-note">{note}</p>
        <ul class="dishes">
{rows}
        </ul>
      </div>'''.format(
            id=esc(c['id']), label=esc(c['label']),
            note=esc(c.get('note', '')), rows='\n'.join(rows)))

    # "Everything" is an extra button in front of the categories, not a
    # stand-in for the first one -- otherwise that category is on the page
    # but can never be filtered to.
    filters = '\n'.join(
        ['        <button class="filter" type="button" data-filter="all" '
         'aria-pressed="true">Everything</button>'] +
        ['        <button class="filter" type="button" data-filter="%s" '
         'aria-pressed="false">%s</button>' % (esc(c['id']), esc(c['label']))
         for c in cats])

    return '''<section id="menu" class="sect sect--menu" aria-labelledby="menu-h">
  <div class="wrap">
    <header class="sec-head" data-reveal>
      <p class="eyebrow">The Menu</p>
      <{h} id="menu-h">What we cook</{h}>
      <p class="lede">Everything is made in the room behind this page, by
        people you can watch. The menu moves with the market and with the
        weather, so treat it as tonight&rsquo;s list rather than a contract.</p>
    </header>

    <div class="filters" role="group" aria-label="Filter the menu by course">
{filters}
      <span class="filter-count" id="filterCount" aria-live="polite"></span>
    </div>

    <div class="cats">
{groups}
    </div>

    <p class="menu-fine">Prices include tax. Grill dishes are cooked to order
      and take longer than everything else on this page. <span
      class="js-order-note">To order, tap&nbsp;+ beside a dish and send the
      list on WhatsApp.</span><span class="nojs-order-note">To order,
      call {phone} or message the kitchen on WhatsApp.</span></p>
  </div>
{orderbar}
</section>'''.format(filters=filters, groups='\n'.join(groups),
                   h='h%d' % level, phone=esc(need('phone')),
                   orderbar=order_bar())


def signature_section():
    sigs = [d for d in dishes() if 'Signature' in d['tags']]
    cards = []
    for i, d in enumerate(sigs):
        # Name and price. The description is not shown here either: the
        # dish is called Murag Chanay, and "chicken curry" underneath it
        # is the guest reading the name back to us.
        cards.append('''      <article class="sig" data-reveal>
        <figure class="shot shot--tall">{shot}</figure>
        <p class="sig-idx">{n:02d}</p>
        <h3 class="sig-name">{name}</h3>
        <p class="sig-price">{price}</p>
      </article>'''.format(
            n=i + 1, name=esc(d['name']),
            price=esc(money(d['price'])), shot=shot('signature-' + d['id'], d['name'])))

    return '''<section id="signature" class="sect sect--sig" aria-labelledby="sig-h">
  <div class="wrap">
    <header class="sec-head" data-reveal>
      <p class="eyebrow">Signature</p>
      <h2 id="sig-h">Three to order first</h2>
      <p class="lede">If it is your first visit, the kitchen will tell you to
        start here. If it is not your first visit, you were going to order
        these three anyway.</p>
    </header>
    <div class="sig-grid">
{cards}
    </div>
  </div>
</section>'''.format(cards='\n'.join(cards))


# ===================================================================
# Photograph slots
# ---------------------------------------------------------------------
# A slot is a fixed-ratio frame, filled or empty. Empty is not an
# apology: it is a dark panel with a hairline and the name, so an
# unfinished site still looks designed rather than broken. Drop
# img/<key>.jpg in and run the build; the slot fills itself.

def shot(key, label, ratio='landscape'):
    src = find_image(key)
    if src:
        return ('<img src="/img/%s" alt="%s photo" loading="lazy" '
                'decoding="async" width="1200" height="900">' % (esc(src), esc(label)))
    return '<span class="shot-ph"><span class="shot-rule" aria-hidden="true"></span>%s</span>' % esc(label)


def story_figure():
    src = find_image('story')
    if src:
        inner = ('<img src="/img/%s" alt="The dining room" loading="lazy" '
                 'decoding="async" width="900" height="1200">' % esc(src))
    else:
        inner = ('<span class="shot-ph shot-ph--stack">'
                 '<span class="shot-rule" aria-hidden="true"></span>'
                 'The long hall</span>')
    return '<figure class="shot shot--story" data-reveal>%s</figure>' % inner


# ===================================================================
# Story, experience, private dining
# ---------------------------------------------------------------------

STORY = '''<section id="story" class="sect" aria-labelledby="story-h">
  <div class="wrap story">
    <div class="story-fig">
      {figure}
    </div>
    <div class="story-body" data-reveal>
      <p class="eyebrow">Our Story</p>
      <{h} id="story-h">Three generations,<br>one fire</{h}>
      <p>Umar Hayat started with a coal stove behind a sweets shop and a queue
        that formed before the shutters went up. The queue is still there. The
        stove is bigger now and there is a dining room in front of it, but the
        method has not moved: the fire is lit in the morning, the meat goes in
        the afternoon, and the last skewer leaves the grate at eleven at
        night.</p>
      <p>Most of what is served here was not invented in a kitchen. The nashta
        was cooked in this family&rsquo;s houses for three generations, on
        ordinary mornings, the way it is cooked in every home in the district
        &mdash; slow, unhurried, and with considerably more chilli than a menu
        would dare put in writing. We did not refine it. We stopped apologising
        for it.</p>
      <p>What did change is the grill. Hardwood gave way to binchotan, and the
        skewer stopped being something you eat standing up and became the
        reason people book a table two weeks out. Everything else in the room
        is ours to arrange.</p>
      <p class="story-close">Come at noon for the nashta. Come after dark for
        the fire.</p>
    </div>
  </div>

  <div class="wrap">
    <dl class="facts" data-reveal>
{facts}
    </dl>
  </div>
</section>'''


def facts():
    return '\n'.join(
        '      <div class="fact"><dt>%s</dt><dd>%s</dd></div>'
        % (esc(f['label']), esc(f['value'])) for f in need('house'))


def experience_section():
    steps = []
    for i, s in enumerate(need('experience')):        steps.append('''      <li class="step" data-reveal>
        <p class="step-n">%02d</p>
        <h3 class="step-t">%s</h3>
        <p class="step-b">%s</p>
      </li>''' % (i + 1, esc(s['title']), esc(s['body'])))

    q = need('quote')
    band = ('interlude.jpg' if find_image('interlude') else None)
    if band:
        band_html = ('<img src="/img/%s" alt="" loading="lazy" decoding="async" '
                     'width="2000" height="900">' % esc(band))
        band_cls = ' band--shot'
    else:
        band_html = '<span class="shot-ph shot-ph--wide">The room, after ten</span>'
        # As in the hero: the wash is for a photograph, not for the bare
        # ground, where it would black out the pull quote.
        band_cls = ''

    return '''<section id="experience" class="sect" aria-labelledby="exp-h">
  <div class="wrap">
    <header class="sec-head" data-reveal>
      <p class="eyebrow">The Evening</p>
      <h2 id="exp-h">How the night works</h2>
      <p class="lede">There is no rush and no fixed seating time. This is
        roughly how an evening goes here, from the first coal to the last
        skewer.</p>
    </header>
    <ol class="steps">
{steps}
    </ol>
  </div>

  <div class="band{band_cls}" data-reveal>
    <div class="band-shot">{band}</div>
    <blockquote class="band-quote">
      <p>{q}</p>
      <cite>{by}</cite>
    </blockquote>
  </div>
</section>'''.format(steps='\n'.join(steps), band=band_html, band_cls=band_cls,
                     q=esc(q['text']), by=esc(q['by']))


def private_dining_section(level=2):
    rooms = []
    for i, r in enumerate(need('privateDining')):
        rooms.append('''      <article class="room" data-reveal>
        <p class="room-seats">{seats}</p>
        <h3 class="room-name">{name}</h3>
        <p class="room-body">{body}</p>
        <p class="room-terms">{terms}</p>
      </article>'''.format(
            seats=esc(r['seats']), name=esc(r['name']),
            body=esc(r['body']), terms=esc(r['terms'])))

    wa = esc(need('whatsapp'))
    msg = esc('Hello, I would like to ask about %s')
    return '''<section id="private-dining" class="sect sect--deep" aria-labelledby="pd-h">
  <div class="wrap">
    <header class="sec-head" data-reveal>
      <p class="eyebrow">Private Dining</p>
      <{h} id="pd-h">The room, when it is yours</{h}>
      <p class="lede">Three ways to take the space. All of them start with a
        message, because the menu and the floor plan get written around the
        number of people you are bringing.</p>
    </header>
    <div class="rooms">
{rooms}
    </div>
    <p class="pd-cta" data-reveal>
      <a class="btn btn-gold" href="https://wa.me/{wa}?text={msg}" rel="noopener">Ask about a private booking</a>
      <a class="btn btn-line" href="tel:{tel}">Or call the room</a>
    </p>
  </div>
</section>'''.format(rooms='\n'.join(rooms), wa=wa, msg=msg,
                     tel=esc(need('phoneHref')), h='h%d' % level)


# ===================================================================
# Reservations
# ---------------------------------------------------------------------
# A request, not a booking. There is no server, so the form composes a
# message and hands the guest to WhatsApp, where a person sees it. That
# is the honest version of a reservation form on a static site: the
# alternative is a form that silently swallows bookings.
#
# With JavaScript off the selects would be empty, so the markup renders
# the fallback panel and JS removes it. The form is never the only way
# to reach the restaurant.

def reserve_section(level=2):
    r = need('reservations')
    slots = ''.join('            <option value="%s">%s</option>' % (esc(s), esc(s))
                    for s in r['slots'])
    return '''<section id="reserve" class="sect sect--deep sect--reserve" aria-labelledby="res-h">
  <div class="wrap res">
    <div class="res-body" data-reveal>
      <p class="eyebrow">Reservations</p>
      <{h} id="res-h">Book a table</{h}>
      <p class="lede">Tell us the day, the hour and how many of you there are.
        One of us will phone to confirm. Tables of thirteen or more go straight
        to WhatsApp so we can talk about the room.</p>
      <ul class="res-facts">
        <li>{clock} The kitchen stops at 23:00</li>
        <li>{phone_icon} {phone}</li>
        <li>{pin} {addr}</li>
      </ul>
      <p class="res-alt">
        Prefer to speak to someone?
        <a href="tel:{tel}">Call {phone}</a> or
        <a href="https://wa.me/{wa}" rel="noopener">send a WhatsApp</a>.
      </p>
    </div>

    <div class="res-panel" data-reveal>
      <form class="res-form" id="resForm" novalidate>
        <div class="field">
          <label for="rDate">Date</label>
          <input type="date" id="rDate" name="date" required>
          <p class="err" data-err-for="rDate" hidden></p>
        </div>
        <div class="field">
          <label for="rTime">Time</label>
          <select id="rTime" name="time" required>
{slots}
          </select>
        </div>
        <div class="field">
          <label for="rParty">Guests</label>
          <select id="rParty" name="party" required></select>
          <p class="field-hint" id="rPartyHint" hidden>A table this size has to
            be arranged, so send it anyway and we will ring you about the long
            table or the private room.</p>
        </div>
        <div class="field">
          <label for="rName">Name</label>
          <input type="text" id="rName" name="name" autocomplete="name"
                 placeholder="Who is the table under?" required>
          <p class="err" data-err-for="rName" hidden></p>
        </div>
        <div class="field">
          <label for="rPhone">Phone</label>
          <input type="tel" id="rPhone" name="phone" autocomplete="tel"
                 placeholder="03XX XXXXXXX" required>
          <p class="err" data-err-for="rPhone" hidden></p>
        </div>
        <div class="field">
          <label for="rOcc">Occasion <span class="opt">optional</span></label>
          <select id="rOcc" name="occasion">
{occasions}
          </select>
        </div>
        <div class="field field--wide">
          <label for="rNotes">Anything we should know <span class="opt">optional</span></label>
          <textarea id="rNotes" name="notes" rows="3"
            placeholder="Allergies, a wheelchair, a pushchair, a very long lunch"></textarea>
        </div>
        <div class="res-submit field--wide">
          <button class="btn btn-gold" type="submit" id="resSubmit">Request this table</button>
          <p class="res-notice">{notice}</p>
        </div>
      </form>

      <div class="res-done" id="resDone" hidden>
        <h3>Your request is ready to send</h3>
        <p>WhatsApp should have opened in a new tab with everything written
          out for you. If it did not, the button below carries the same
          message &mdash; it is already composed, so you do not need to type
          it again.</p>
        <a class="btn btn-wa" id="resDoneLink" href="#" rel="noopener" target="_blank">Open it in WhatsApp</a>
        <button class="link-btn" type="button" id="resAgain">Change something</button>
      </div>

      <div class="res-fallback">
        <h3>Reservations by phone or WhatsApp</h3>
        <p>The request form needs JavaScript, which is off. The restaurant does
          not. Call {phone}, or send a message and it will arrive in the room
          where the orders are taken.</p>
        <a class="btn btn-wa" href="https://wa.me/{wa}" rel="noopener">Message on WhatsApp</a>
        <a class="btn btn-line" href="tel:{tel}">Call {phone}</a>
      </div>
    </div>
  </div>
</section>'''.format(
        slots=slots, occasions='\n'.join(
            '            <option value="%s">%s</option>' % (esc(o), esc(o))
            for o in r['occasions']),
        notice=esc(r['notice']),
        clock=ICON['clock'], phone_icon=ICON['phone'], pin=ICON['pin'],
        phone=esc(need('phone')), tel=esc(need('phoneHref')),
        wa=esc(need('whatsapp')), addr=esc(need('address', 'line1')),
        h='h%d' % level)


# ===================================================================
# Visit
# ---------------------------------------------------------------------

def visit_section(level=2):
    addr = need('address')
    return '''<section id="visit" class="sect" aria-labelledby="visit-h">
  <div class="wrap">
    <header class="sec-head" data-reveal>
      <p class="eyebrow">Visit</p>
      <{h} id="visit-h">Find us</{h}>
      <p class="lede">One long room on Mall Road, {est}. It fills up after
        eight, so if you are coming for the grill, come early or book.</p>
    </header>

    <div class="visit">
      <div class="visit-col" data-reveal>
        <div class="info-row">
          <span class="info-ico">{pin}</span>
          <div>
            <h3>Address</h3>
            <address>{l1}<br>{l2}<br>{city} {post}<br>{country}</address>
          </div>
        </div>
        <div class="info-row">
          <span class="info-ico">{phone_icon}</span>
          <div>
            <h3>Phone</h3>
            <p><a href="tel:{tel}">{phone}</a></p>
          </div>
        </div>
        <div class="info-row">
          <span class="info-ico">{mail}</span>
          <div>
            <h3>Email</h3>
            <p><a href="mailto:{email}">{email}</a></p>
          </div>
        </div>
        <div class="info-row">
          <span class="info-ico">{at}</span>
          <div>
            <h3>Online</h3>
            <nav class="social social--row" aria-label="Social media">
{soc}
            </nav>
          </div>
        </div>
      </div>

      <div class="visit-col" data-reveal>
        <h3 class="col-head">Opening hours</h3>
        {hours}
        <p class="visit-note">The grill stops twenty minutes before closing.
          The nashta runs all day.</p>
        <div class="visit-cta">
          <a class="btn btn-gold" href="https://wa.me/{wa}" rel="noopener">Message on WhatsApp</a>
        </div>
      </div>
    </div>
  </div>
</section>'''.format(
        est=esc(need('est')), pin=ICON['pin'], phone_icon=ICON['phone'],
        mail=ICON['mail'], at=ICON['at'], clock=ICON['clock'],
        soc=social_markup('        '), hours=hours_table(),
        l1=esc(addr['line1']), l2=esc(addr['line2']), city=esc(addr['city']),
        post=esc(addr.get('postcode', '')), country=esc(addr['country']),
        tel=esc(need('phoneHref')), phone=esc(need('phone')),
        email=esc(need('email')), wa=esc(need('whatsapp')),
        h='h%d' % level)


DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


def hours_table():
    """Rendered at build time, not by script: hours are the first thing
    a guest looks for and they must be there with JavaScript off. The
    only thing JS adds is marking which row is today.

    Consecutive days that share the same hours are collapsed into one row.
    Printing the same 11:00 - 23:00 six times says "nobody filled this
    in", which is the opposite of what a room open for three generations
    wants to say, and it is six lines of the footer for no information.
    """
    by_day = {h['day']: h for h in need('hours')}

    def when(d):
        h = by_day.get(d)
        if not h or not h.get('open') or not h.get('close'):
            return 'Closed'
        return '%s &ndash; %s' % (esc(h['open']), esc(h['close']))

    groups = []
    for d in range(7):
        w = when(d)
        if groups and groups[-1][1] == w:
            groups[-1][0].append(d)
        else:
            groups.append(([d], w))

    rows = []
    for days, w in groups:
        if len(days) == 1:
            label = DAYS[days[0]]
        elif len(days) == 7:
            label = 'Every day'
        elif days == list(range(days[0], days[-1] + 1)):
            label = '%s &ndash; %s' % (DAYS[days[0]], DAYS[days[-1]])
        else:
            # Non-contiguous, so it has to be spelled out rather than
            # implied by an en dash that would include the days between.
            label = ' &middot; '.join(DAYS[d] for d in days)
        rows.append('        <div data-days="%s"><span>%s</span><span>%s</span></div>'
                    % (' '.join(str(d) for d in days), label, w))
    return '<div class="hours">\n%s\n      </div>' % '\n'.join(rows)


# ===================================================================
# Hero
# =================================================================-----

def hero_lines(name):
    """Break the name over two lines at its midpoint, so the display
    face can be set as large as the viewport allows without one line
    running off the edge. Four words become two and two."""
    words = name.split()
    if len(words) < 2:
        return [name]
    mid = (len(words) + 1) // 2
    return [' '.join(words[:mid]), ' '.join(words[mid:])]


def hero():
    lines = hero_lines(need('name'))
    src = find_image('hero')
    if src:
        bg = ('<img class="hero-img" src="/img/%s" alt="" fetchpriority="high" '
              'decoding="async" width="2000" height="1200">' % esc(src))
        bg_cls = ' hero-bg--shot'
    else:
        bg = ''
        # No photograph means no scrim: the dark wash exists to hold the
        # name over a bright photo, and over the bare ground it would
        # only paint the white hero black behind dark text.
        bg_cls = ''

    a = need('address')
    return '''<section class="hero" id="top">
  <div class="hero-bg{bg_cls}" aria-hidden="true">{bg}<span class="hero-grain"></span></div>
  <div class="hero-in">
    <p class="hero-kicker">{kicker}</p>
    <h1 class="hero-title">
      <span class="hero-line">{line1}</span>
      <span class="hero-line">{line2}</span>
    </h1>
    <span class="rule" aria-hidden="true"></span>
    <p class="hero-lede">{lede}</p>
    <p class="hero-cta">
      <a class="btn btn-gold" href="{reserve}">Reserve a table</a>
      <a class="btn btn-line" href="{menu}">See the menu</a>
    </p>
  </div>
  <div class="hero-strip">
    <p class="strip-open"><span class="dot" data-open-dot aria-hidden="true"></span><span data-open-label>{open_hours}</span></p>
    <p class="strip-addr">{addr}</p>
    <p class="strip-links">
      <a href="tel:{tel}">Call</a>
      <span aria-hidden="true">&middot;</span>
      <a href="https://wa.me/{wa}" rel="noopener">WhatsApp</a>
    </p>
  </div>
</section>'''.format(
        bg=bg,     bg_cls=bg_cls,
        kicker=esc(need('heroKicker')),
        line1=esc(lines[0]), line2=esc(lines[-1]),
        lede=esc(need('heroLede')),
        open_hours=esc('Open %s &ndash; %s' % (
            min(h['open'] for h in need('hours') if h.get('open')),
            max(h['close'] for h in need('hours') if h.get('close')))),
        addr=esc('%s, %s' % (a['line1'], a['city'])),
        reserve=RESERVE, menu=url_for('menu.html'),
        tel=esc(need('phoneHref')), wa=esc(need('whatsapp')))


# ===================================================================
# The page
# ---------------------------------------------------------------------

SCRIPTS = '''<script src="/js/site-config.js" defer></script>
<script src="/js/header.js" defer></script>
<script src="/js/menu.js" defer></script>
<script src="/js/order.js" defer></script>
<script src="/js/reserve.js" defer></script>'''
def menu_index_json():
    """The dish list, as JSON, inlined into every page.

    Search used to scrape the rendered menu out of the DOM, which worked
    because the menu was on the only page. With the menu on its own page
    that would leave search empty on the other five, so the index travels
    with the page instead. It is about a kilobyte and costs no request."""
    rows = [{'id': d['id'], 'name': d['name'], 'cat': d['cat'],
             'price': int(d['price'])} for d in dishes()]
    # Names and categories are the config's own strings, but escape "<"
    # anyway: a dish called "</script>" would end the block early.
    body = json.dumps(rows, ensure_ascii=False).replace('<', '\\u003c')
    return ('<script type="application/json" id="menuIndex">%s</script>'
            % body)


OG_IMAGE = find_image('social')
og_image = '/img/' + OG_IMAGE if OG_IMAGE else '/umarhayatchaskapoint-trimmed.png'
PALETTE = read_palette('bg')


# ===================================================================
# The origin the site is served from
# ---------------------------------------------------------------------
# A link preview, a canonical URL and a schema.org address are all read
# by something other than a browser sitting on this domain, and all three
# have to be absolute. A root-relative "/img/social.jpg" is meaningless to
# WhatsApp, which fetches the image on its own servers; it has no idea
# which host the link came from.
#
# So every one of them is built from SITE.url in the config, through
# absolute(), rather than being written inline where a half of them would
# quietly stay relative.

def _base_url():
    url = str(need('url')).strip().rstrip('/')
    if not re.match(r'^https://[^\s/]+$', url):
        raise ConfigError(
            'SITE.url must be an https origin with no path, e.g. '
            '"https://example.com" -- got %r' % need('url'))
    return url


SITE_URL = _base_url()


def absolute(path):
    """A root-relative site path as a full URL. '/menu' -> the site's
    /menu. Anything already absolute is left alone, so a config value that
    is a full URL in one place and a path in another cannot produce a
    double-prefixed link."""
    if re.match(r'^[a-z]+:', path):
        return path
    return SITE_URL + (path if path.startswith('/') else '/' + path)


NAME = need('name')
TITLE = '%s &mdash; %s' % (NAME, need('tagline'))
DESC = ('%s in %s. Nashta cooked the way it has been cooked here for three '
        'generations, and a charcoal grill that runs until midnight. Read the '
        'menu, see the hours, book a table.'
        % (NAME, need('address', 'city')))

# One line per page, saying only what is on that page. Derived from the
# page's own content rather than written per page, so a page cannot end
# up described as something it is not.
PAGE_DESC = {
    '/': DESC,
    '/menu': 'The full menu at %s: %s cooked the long way, a charcoal grill '
            'that runs late, and fried food made to order.'
            % (NAME, need('address', 'city')),
    '/story': 'How %s came to be, and how an evening here actually works.'
              % NAME,
    '/private-dining': 'The rooms at %s, for private dining, small '
                       'celebrations and long tables.' % NAME,
    '/visit': 'Where to find %s in %s, the opening hours, the phone number '
              'and how to get in touch.' % (NAME, need('address', 'city')),
    '/reserve': 'Request a table at %s. Send the details and we will confirm '
                'by phone.' % NAME,
}


def page_title(url):
    for _fn, u, label, _nav in PAGES:
        if u == url:
            if u == '/':
                return TITLE
            return '%s &mdash; %s' % (label, NAME)
    raise KeyError('no such page url: ' + url)


# ===================================================================
# Structured data
# ---------------------------------------------------------------------
# A <script type="application/ld+json"> block, which is the only thing on
# this site that a search engine reads as a statement of fact rather than
# as prose. It is what puts the restaurant's name, address, hours and
# prices into a Google knowledge panel instead of leaving a blue link.
#
# It is generated from the same config as the visible page, which is the
# only way it can be kept honest: the schema cannot say the kitchen closes
# at eleven if the page under it says midnight, because both are reading
# SITE.hours. That also means the placeholder phone number and the sentinel
# prices are published here as well, and are fixed by fixing the config.

# schema.org day names, against the numeric days the config uses.
SCHEMA_DAY = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
              'Friday', 'Saturday']


def opening_hours_spec():
    """SITE.hours as openingHoursSpecification, grouping the days that
    share hours exactly the way hours_table() groups them for the page.

    Google reads one entry per distinct set of hours. Six identical rows
    for six days is six ways to be wrong, and it is the same reasoning
    that put the grouped table in the footer."""
    rows = {}
    for h in need('hours'):
        rows.setdefault((h.get('open'), h.get('close')), []).append(int(h['day']))
    out = []
    for (open_, close), days in sorted(rows.items(), key=lambda kv: min(kv[1])):
        if not open_ or not close:
            continue          # a closed day is simply absent, which is correct
        out.append({
            '@type': 'OpeningHoursSpecification',
            'dayOfWeek': ['https://schema.org/' + SCHEMA_DAY[d] for d in sorted(days)],
            'opens': open_,
            'closes': close,
        })
    return out


def menu_schema():
    """The menu as schema.org Menu/MenuSection/MenuItem, straight off the
    same ITEMS list the page renders and the menu filters read.

    Prices are quoted exactly as the page quotes them, sentinel included.
    A schema that disagreed with the page it sits on is worse than no
    schema: the prices are the part a guest acts on."""
    sections = []
    for c in need('categories'):
        rows = [d for d in dishes() if d['cat'] == c['id']]
        if not rows:
            continue
        sections.append({
            '@type': 'MenuSection',
            'name': c['label'],
            'hasMenuItem': [{
                '@type': 'MenuItem',
                'name': d['name'],
                'offers': {
                    '@type': 'Offer',
                    'price': str(int(d['price'])),
                    'priceCurrency': need('currency', 'code'),
                },
            } for d in rows],
        })
    return {'@type': 'Menu', 'name': 'Menu', 'hasMenuSection': sections}


def price_range():
    """priceRange is a single string, so it is the real span of the menu
    rather than a currency symbol on its own."""
    prices = [int(d['price']) for d in dishes() if int(d['price']) > 0]
    if not prices:
        return ''
    sym = need('currency', 'symbol')
    fmt = lambda n: format(n, ',d')
    return '%s %s%s%s' % (sym, fmt(min(prices)),
                          ' to ' if min(prices) != max(prices) else '',
                          fmt(max(prices)) if min(prices) != max(prices) else '')


def json_ld(url):
    """The Restaurant block for one page.

    Only fields the config actually has are emitted. A property invented
    to fill the schema -- a star rating, a review count, a founding date
    parsed out of "Est. 1974" -- is a claim the site cannot support, and
    fabricated review markup is the single fastest way to have structured
    data ignored or a manual action applied. So: no aggregateRating, and
    nothing derived by guessing."""
    addr = need('address')
    hours = opening_hours_spec()
    data = {
        '@context': 'https://schema.org',
        '@type': 'Restaurant',
        'name': NAME,
        'description': PAGE_DESC[url],
        'url': absolute(url),
        'image': absolute(og_image),
        'telephone': need('phone'),
        'email': need('email'),
        'address': {
            '@type': 'PostalAddress',
            'streetAddress': addr['line1'],
            'addressLocality': addr['city'],
            'postalCode': addr['postcode'],
            'addressCountry': addr.get('countryCode', addr['country']),
        },
        'currenciesAccepted': need('currency', 'code'),
        'priceRange': price_range(),
        'hasMenu': absolute('/menu'),
        'menu': menu_schema(),
        'acceptsReservations': 'True',
        'sameAs': [url_ for _k, url_, _i in social_links()],
    }
    if hours:
        data['openingHoursSpecification'] = hours
    if need('cuisine'):
        data['servesCuisine'] = list(need('cuisine'))
    if OG_IMAGE:
        # Only claim a photo if one is actually there to point at.
        data['photo'] = [absolute(og_image)]

    body = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=None)
    # "<" cannot survive inside a <script> block, and a config value is
    # not trusted input. \u003c is the same character to a JSON parser.
    return '<script type="application/ld+json">%s</script>' % body.replace('<', '\\u003c')


def page(body, url):
    return '''<!DOCTYPE html>
<html lang="en" class="no-js" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#FFFFFF">
<meta name="color-scheme" content="light">
<meta property="og:site_name" content="{name}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_GB">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{og}">
<link rel="manifest" href="/site.webmanifest">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/umarhayatchaskapoint.png">
<meta name="apple-mobile-web-app-title" content="{name}">
<link rel="preload" href="/fonts/brand-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/display-700.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/body-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/style.css">
{ld}
<script>document.documentElement.className=document.documentElement.className.replace('no-js','js')</script>
</head>
<body data-page="{url}">
{header}
{overlays}
<main id="main">
{body}
</main>
{footer}
{menuindex}
{scripts}
</body>
</html>
'''.format(
        title=page_title(url), desc=esc(PAGE_DESC[url]), name=esc(NAME),
        url=url, og=esc(absolute(og_image)), canonical=esc(absolute(url)),
        ld=json_ld(url),
        header=header(url), overlays=overlays(url), menuindex=menu_index_json(),
        body=body, footer=footer(), scripts=SCRIPTS)


# Which blocks go on which page. Every block appears on exactly one page,
# so there is no prose to keep in two places at once and nothing to
# unpublish when one side is rewritten.
BODY = {
    '/':               lambda: '\n'.join([hero(), signature_section(),
                                          experience_section()]),
    # On its own page, a block's top heading is the page's <h1>. On the
    # home page the same blocks sit under the hero, so they stay <h2>.
    '/menu':            lambda: menu_section(level=1),
    '/story':           lambda: STORY.format(figure=story_figure(),
                                            facts=facts(), h='h1'),
    '/private-dining':  lambda: private_dining_section(level=1),
    '/visit':           lambda: visit_section(level=1),
    '/reserve':         lambda: reserve_section(level=1),
}


FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" fill="#FFFFFF"/>
<text x="32" y="46" font-family="Georgia,serif" font-size="36" font-weight="700"
      text-anchor="middle" fill="#8A6634">U</text>
</svg>
'''


# ===================================================================
# Files that exist for machines rather than guests
# ---------------------------------------------------------------------
# sitemap.xml, robots.txt and the web manifest are all generated, because
# a hand-kept sitemap goes stale the first time a page is added and a
# stale sitemap is worse than none: it advertises a URL that 404s.
#
# 404.html is generated for a different reason. Vercel serves it for any
# unmatched path, which means a guest who mistypes the address, or follows
# a stale link, or lands on a page that has been renamed, gets the host's
# generic error page. That is the one screen on the site with no way back
# to the menu, and it is the screen that most needs the site's own header
# and footer on it.

def lastmod():
    """The build's date, as W3C format.

    This is when the page was last generated, which is what lastmod means.
    It is not a claim about when the prose was written.

    SOURCE_DATE_EPOCH is honoured because it is the standard way to ask
    for a reproducible build, and a sitemap whose date moves on every
    rebuild makes every deploy a diff that means nothing."""
    epoch = os.environ.get('SOURCE_DATE_EPOCH')
    when = int(epoch) if epoch and epoch.isdigit() else time.time()
    return time.strftime('%Y-%m-%d', time.gmtime(when))


def sitemap_xml():
    """One entry per page in PAGES, in nav order rather than alphabetical,
    so the file reads in the order the site does.

    The 404 page is deliberately absent: it is a response to a URL that
    does not exist, and listing it would invite it to be crawled."""
    # changefreq and priority are advisory fields that every crawler since
    # Google stopped using them has ignored. Emitting priorities that
    # nothing reads is decoration, so only lastmod and loc are written.
    rows = []
    for _fn, url, _label, _nav in PAGES:
        rows.append('  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </url>'
                    % (esc(absolute(url)), lastmod()))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            '%s\n</urlset>\n' % '\n'.join(rows))


def robots_txt():
    """Crawl rules, kept to what is actually true.

    /test/ is the build harness: 68KB of test script that describes every
    check the site has to pass. There is no reason for a crawler to have
    it, and .vercelignore keeps it off the deployment as well, so this
    line is the belt to that braces."""
    return '''# %s/robots.txt
# There is nothing to hide on this site and no analytics, no tracking and
# no third-party requests, so nothing is disallowed except the test
# harness, which is not part of the site.

User-agent: *
Disallow: /test/
Allow: /

Sitemap: %s/sitemap.xml
''' % (SITE_URL, SITE_URL)


def manifest_json():
    """The web manifest: what the site is called when it is installed to a
    phone home screen, which is its own small SEO surface. Colours are the
    page's own, read from the palette, so it cannot drift from the site."""
    icons = [{'src': '/favicon.svg', 'sizes': 'any',
              'type': 'image/svg+xml', 'purpose': 'any'}]
    logo = find_image('logo-mark') or find_image('social')
    if logo:
        icons.append({'src': '/img/' + logo, 'sizes': '512x512',
                      'type': 'image/png', 'purpose': 'any'})
    data = {
        'name': NAME,
        'short_name': 'Chaska Point',
        'description': PAGE_DESC['/'],
        'start_url': '/',
        'scope': '/',
        'display': 'standalone',
        'orientation': 'portrait',
        'background_color': PALETTE['bg'],
        'theme_color': PALETTE['bg'],
        'lang': 'en',
        'dir': 'ltr',
        'categories': ['food', 'restaurant', 'lifestyle'],
        'icons': icons,
    }
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n'


def not_found_page():
    """The 404, in the site's own chrome.

    Served by the host for any path that is not a page, at whatever URL
    the guest actually asked for. So it cannot be canonical, and it asks
    not to be indexed: it is not a document, and indexing it would put a
    dead link in a search result. No JSON-LD either -- there is no
    restaurant described here, and a Restaurant block on a 404 would be
    structured data attached to the wrong URL."""
    links = '\n'.join(
        '            <li><a href="%s">%s</a></li>' % (url, esc(label))
        for _fn, url, label, _nav in PAGES if _nav)
    return '''<!DOCTYPE html>
<html lang="en" class="no-js" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found &mdash; %(name)s</title>
<meta name="description" content="That page is not one of ours. The menu, the story, the hours and the reservation form all are.">
<meta name="robots" content="noindex, follow">
<meta name="theme-color" content="%(bg)s">
<meta name="color-scheme" content="light">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/fonts/brand-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/display-700.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/body-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/style.css">
<script>document.documentElement.className=document.documentElement.className.replace('no-js','js')</script>
</head>
<body data-page="/404">
<a class="skip" href="#main">Skip to content</a>
%(header)s
%(overlays)s
<main id="main">
  <section class="sect" id="notfound" aria-labelledby="nf-h">
    <div class="wrap">
      <div class="sec-head">
        <p class="eyebrow">Error 404</p>
        <h1 id="nf-h">Nothing at this address</h1>
        <span class="rule" aria-hidden="true"></span>
        <p class="lede">The page you asked for is not one of ours. Nothing is
          broken &mdash; there is simply nothing at that door, and we would
          rather say so than show you an error from the host. Everything the
          site does have is below.</p>
      </div>
      <ul class="nf-links">
%(links)s
      </ul>
      <p class="nf-alt">Or call the room on
        <a href="tel:%(tel)s">%(phone)s</a> and we will find you a table.</p>
    </div>
  </section>
</main>
%(footer)s
<script src="/js/site-config.js" defer></script>
<script src="/js/header.js" defer></script>
</body>
</html>
''' % {
        'name': esc(NAME), 'tel': esc(need('phoneHref')),
        'phone': esc(need('phone')), 'bg': esc(PALETTE['bg']),
        'header': header('/404'), 'overlays': overlays('/404'),
        'footer': footer(), 'links': links,
    }



# ===================================================================
# Run
# ===================================================================

def validate(pages):
    """Anything that renders a usable-looking page while being broken.
    A dead link is invisible until someone clicks it; a duplicated id
    makes every deep link to that element ambiguous; a dish in an
    unfiltered category is unreachable.

    `pages` is {url: html} for every page the build wrote, because the
    interesting mistakes are now cross-page: a link that points at a
    section which lives on a different page, or a page nobody generates.
    """
    problems = []
    known_urls = {u for _fn, u, _l, _n in PAGES}
    n_links = 0
    n_refs = 0

    for url, out in sorted(pages.items()):
        where = url

        # 1. Every in-page link resolves within the page it is on.
        targets = re.findall(r'href="#([\w-]+)"', out)
        n_links += len(targets)
        missing = sorted({t for t in targets if 'id="%s"' % t not in out})
        if missing:
            problems.append('%s: anchors with no target on this page: %s'
                            % (where, ', '.join(missing)))

        # 2. Every link to another page points at a page that exists.
        #    "/menue" renders a 404 that still looks like the site.
        page_links = re.findall(r'href="(/[a-z0-9/-]*)"', out)
        n_links += len(page_links)
        dead = sorted({p for p in page_links if p not in known_urls})
        if dead:
            problems.append('%s: links to pages that are not built: %s'
                            % (where, ', '.join(dead)))

        # 3. Element ids are unique within a page. They only have to be,
        #    since each page is its own document.
        ids = re.findall(r'\sid="([\w-]+)"', out)
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            problems.append('%s: duplicated element ids: %s'
                            % (where, ', '.join(dupes)))

        # 3b. Exactly one h1 per page. A screen reader and a search engine
        #     both use it to name the page, and a page with none is a page
        #     that announces itself as an unlabelled document. Two are
        #     worse: they disagree about what the page is called.
        h1s = re.findall(r'<h1[\s>]', out)
        if len(h1s) != 1:
            problems.append('%s: has %d <h1> elements, expected exactly 1'
                            % (where, len(h1s)))

        # 4. Every local file the page asks for exists on disk. A 404 for
        #    a stylesheet still renders a page, so it never shows by eye.
        refs = set(re.findall(
            r'(?:href|src)="((?!https?:|#|data:|tel:|mailto:)[^"]+)"', out))
        refs |= set(re.findall(
            r'content="(/[^"]+\.(?:png|jpg|jpeg|webp|avif|svg))"', out))
        n_refs += len(refs)
        gone = sorted(r for r in refs
                      if os.path.splitext(r)[1]
                      and r not in known_urls
                      and not os.path.exists(os.path.join(ROOT, r.lstrip('/'))))
        if gone:
            problems.append('%s: referenced files not on disk: %s'
                            % (where, ', '.join(gone)))

    # 5. Every dish is reachable. A category with no dish renders an
    #    empty heading; a dish in a category that is not listed renders a
    #    card that no filter can ever show.
    known = {c['id'] for c in need('categories')}
    unknown = sorted({d['cat'] for d in dishes()} - known)
    if unknown:
        problems.append('dishes in an unlisted category: ' + ', '.join(unknown))
    for c in need('categories'):
        if not any(d['cat'] == c['id'] for d in dishes()):
            problems.append('category with no dishes: ' + c['id'])

    # 6. Every price is rendered with currency.symbol, so code is the only
    #    other statement of what the numbers are. If the two disagree the
    #    menu and the config are telling a guest different things.
    if need('currency', 'code') != need('currency', 'symbol'):
        problems.append('currency code and symbol disagree')

    # 7. Every page the nav promises is actually written out. A page in
    #    PAGES with no body is a 404 that only shows on click.
    for fn, url, _l, _n in PAGES:
        if url not in pages:
            problems.append('page declared but not built: ' + url)

    # 8. The sitemap has to agree with the site. A page added to PAGES and
    #    left out of the sitemap is a page Google is never told about, and
    #    a page that is in the sitemap but not built is a 404 handed
    #    straight to a crawler. Both are invisible in a browser.
    sitemap = sitemap_xml()
    listed = re.findall(r'<loc>([^<]+)</loc>', sitemap)
    expected = [absolute(u) for _fn, u, _l, _n in PAGES]
    for miss in sorted(set(expected) - set(listed)):
        problems.append('page missing from sitemap.xml: ' + miss)
    for extra in sorted(set(listed) - set(expected)):
        problems.append('sitemap.xml lists a page that is not built: ' + extra)

    # 9. The canonical on every page is that page's own address. A
    #    canonical pointing somewhere else tells a search engine the pages
    #    you own are somewhere they are not, which is the single most
    #    expensive thing a head tag can get wrong.
    for url, out in sorted(pages.items()):
        canon = re.findall(r'<link rel="canonical" href="([^"]+)"', out)
        if canon != [absolute(url)]:
            problems.append('%s: canonical is %s, expected [%s]'
                            % (url, canon, absolute(url)))
        # The share card has to be absolute. WhatsApp fetches the image on
        # its own servers and has no idea which host the link came from, so
        # a root-relative og:image previews as nothing at all.
        for prop in re.findall(r'<meta property="og:(?:image|url)" content="([^"]+)"', out):
            if not prop.startswith('https://'):
                problems.append('%s: og image or url is not absolute: %s' % (url, prop))

    # 10. The JSON-LD has to be JSON, and has to be a Restaurant. A
    #     syntax error in it is silently ignored by every consumer, and a
    #     structured data block that never parses looks fine in the page.
    for url, out in sorted(pages.items()):
        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', out, re.S)
        if len(blocks) != 1:
            problems.append('%s: %d JSON-LD blocks, expected exactly 1'
                            % (url, len(blocks)))
            continue
        try:
            ld = json.loads(blocks[0].replace('\\u003c', '<'))
        except ValueError as e:
            problems.append('%s: JSON-LD does not parse: %s' % (url, e))
            continue
        if ld.get('@type') != 'Restaurant':
            problems.append('%s: JSON-LD @type is %r, expected Restaurant'
                            % (url, ld.get('@type')))
        # The schema is only worth anything if it agrees with the page it
        # is on, and it is generated from the same config, so the two can
        # only drift if someone hardcodes one of them.
        if ld.get('name') != need('name'):
            problems.append('%s: JSON-LD name disagrees with the config' % url)
        if ld.get('telephone') != need('phone'):
            problems.append('%s: JSON-LD telephone disagrees with the config' % url)
        if not ld.get('openingHoursSpecification'):
            problems.append('%s: JSON-LD has no opening hours' % url)

    # 11. The generated JSON/XML files have to parse. A sitemap that is not
    #     well-formed XML is silently discarded; a manifest that is not
    #     valid JSON installs nothing and says nothing.
    try:
        import xml.etree.ElementTree as ET
        ET.fromstring(sitemap)
    except Exception as e:
        problems.append('sitemap.xml is not well-formed XML: %s' % e)
    try:
        json.loads(manifest_json())
    except ValueError as e:
        problems.append('site.webmanifest is not valid JSON: %s' % e)

    # 12. robots.txt has to point at the sitemap the build just wrote, at
    #     the absolute URL, or the two files are not connected to anything.
    robots = robots_txt()
    if ('Sitemap: ' + absolute('/sitemap.xml')) not in robots:
        problems.append('robots.txt does not advertise the sitemap')

    return problems, n_links, n_refs


def placeholder_report():
    """The two kinds of invented price, separated, because they need
    different work: a sentinel has no number behind it at all, an
    invented one just needs replacing with the real figure."""
    sentinels, invented = [], []
    for d in dishes():
        line = '  %-18s %-22s %s' % (d['id'], d['name'], money(d['price']))
        (sentinels if d['price'] == PRICE_TODO else invented).append(line)
    return sentinels, invented


if __name__ == '__main__':
    written = {}
    for fn, url, _label, _nav in PAGES:
        if url not in BODY:
            raise SystemExit('no body defined for %s' % url)
        html = page(BODY[url](), url)
        with open(os.path.join(ROOT, fn), 'w', encoding='utf-8') as f:
            f.write(html)
        written[url] = html
        print('  %-20s %7d bytes  %s' % (fn, len(html.encode()), url))

    with open(os.path.join(ROOT, 'favicon.svg'), 'w', encoding='utf-8') as f:
        f.write(FAVICON)
    print('  %-20s %7d bytes' % ('favicon.svg', len(FAVICON.encode())))

    # Generated for machines, not for guests. None of them is linked from
    # the markup, so validate() has no reason to look at them; they get
    # their own checks below instead.
    for fn, text in (('sitemap.xml', sitemap_xml()),
                     ('robots.txt', robots_txt()),
                     ('site.webmanifest', manifest_json()),
                     ('404.html', not_found_page())):
        with open(os.path.join(ROOT, fn), 'w', encoding='utf-8') as f:
            f.write(text)
        print('  %-20s %7d bytes' % (fn, len(text.encode())))

    problems, n_links, n_refs = validate(written)
    print('  %d dishes, %d links, %d local files, all ids unique per page'
          % (len(ITEMS), n_links, n_refs))

    sentinels, invented = placeholder_report()
    print('\n  PLACEHOLDER PRICES -- this site is not ready to publish')
    print('  %d dish(es) priced at the %d sentinel, meaning no price yet:'
          % (len(sentinels), PRICE_TODO))
    for line in sentinels:
        print(line)
    print('  %d dish(es) carrying an INVENTED price that looks real:'
          % len(invented))
    for line in invented:
        print(line)
    if need('email').endswith('example.com'):
        print('  contact details, hours, address and all prose are placeholders too.')
        print('  run SITE.todos() in the browser console for the full list.')

    if problems:
        print('\n  BUILD FAILED')
        for p in problems:
            print('   - %s' % p)
        sys.exit(1)
    print('\n  ok')
