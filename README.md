# Umar Hayat Chaska Point

Static site. **Six pages**, no framework, and a small Python script that
generates all of the HTML.

```
build.py                generates every page from js/site-config.js + the ITEMS list
index.html              generated. Do not hand-edit.
menu.html               generated. Do not hand-edit.
story.html              generated. Do not hand-edit.
private-dining.html     generated. Do not hand-edit.
visit.html              generated. Do not hand-edit.
reserve.html            generated. Do not hand-edit.
404.html                generated. Served by the host for any unknown address.
sitemap.xml             generated. Machine-readable list of the six pages.
robots.txt              generated. Crawl rules; points at the sitemap.
site.webmanifest        generated. What the site is called when installed.
favicon.svg             generated. The U monogram.
tools/make-share-image.py  renders img/social.png, the 1200x630 link card.
```

| Route | Page | What is on it |
|---|---|---|
| `/` | Home | Hero, three dishes to order first, how the evening works |
| `/menu` | Menu | Every dish, name and price, filterable |
| `/story` | Our Story | The story and the facts |
| `/private-dining` | Private Dining | The three ways to take the room |
| `/visit` | Visit | Address, contact and opening hours |
| `/reserve` | Reserve | The reservation request form |

The nav carries the five browsing pages; **Reserve** is a standing call
to action rather than a quiet nav item, and is marked as the current page
in the same way the nav links are. Each page names itself in the browser
with its own `<title>`, description and `<h1>`.

Paths are clean (`/menu`, not `/menu.html`). `vercel.json` sets
`cleanUrls`, and `test/serve.py` reproduces that in the test server, so
the links in the markup are the links that are tested. Old addresses are
kept working by redirects: `/about` → `/story`, `/contact` → `/visit`,
`/dining` → `/private-dining`, `/reservation` → `/reserve`.

## Where the site is, and how a search engine reads it

Every page names itself a second time, to software that is not a browser
and cannot see the design: a canonical URL, an `og:url`, and an
`application/ld+json` block describing a **Restaurant** with its address,
phone, opening hours and the full menu and prices. All of it is generated
from the same `js/site-config.js` as the visible page, so the schema and
the page cannot drift apart: the hours in the structured data and the
hours in the footer are the same list of numbers, printed two ways.

Three things follow from that:

- **`/sitemap.xml`, `robots.txt` and `site.webmanifest` are generated** by
  every build, not kept by hand, because a hand-kept sitemap goes stale
  the first time a page is added and a stale sitemap advertises a URL
  that 404s. A page added to `PAGES` and not the sitemap fails the build.
- **`/404.html` is generated** in the site's own chrome. Vercel serves it
  for any unknown address, so a guest who mistypes, or follows a stale
  link, gets the site's header and footer and a list of every page rather
  than the host's generic error page. It is `noindex`, has no canonical
  and no structured data, because it is a response and not a document.
- **The one address everything is built from is `SITE.url`** in
  `js/site-config.js`. Change it there, rebuild, and the canonical, the
  sitemap, robots, the manifest and the JSON-LD all move with it. It is a
  TODO placeholder (`umar-hayat-chaska-point.vercel.app`) until the real
  domain exists, and `SITE.todos()` reports it as such.

`og:image` points at `img/social.png`, a 1200x630 card generated from the
site's own wordmark and palette (see `img/README.md`). A share card has to
be absolute -- WhatsApp fetches it on its own servers -- and it has to be
sized for the feed it appears in: the trimmed logo this used as a fallback
is 426x278, a blurred stamp at the size the platforms render it.

The test suite checks all of this, including that each new check can fail:
see *SEO guards* under Testing.

---

## Read this before the site goes live

**Nothing on this site is real business data except the email.** The
address, phone number, WhatsApp number, opening hours, social links,
founding year, the domain, and almost all of the prose are invented so the
layout could be built and judged. They must be replaced. See *Placeholder
data* below. Every one of them is source to both the visible page and the
structured data, so nothing is published in one and omitted from the
other.

The reservation form does not book anything. It validates what the guest
typed and hands the request to WhatsApp, where a person reads it.

| Feature | What actually happens |
|---|---|
| Reservation | Validated in the browser, then opens WhatsApp with the details filled in. Nothing is sent, stored or confirmed automatically. |
| Menu | Generated from the `ITEMS` list in `build.py`. Not editable from a browser. |
| Search | Searches a small JSON index of the dishes, in the header of every page. A result links to the dish on `/menu`. No server. |
| Opening hours | Read from the config and rendered on the page, so they show with JavaScript disabled. Days that share hours are grouped into one row. |

There is no cart, no checkout, no account and no currency conversion. A
restaurant site that pretends to take money it cannot take is worse than
one that asks for a phone call, and the cart code has been deleted rather
than hidden.

---

## Placeholder data

`build.py` prints a report on every build listing what is still fake. It
does not stop the build, because a placeholder build is the point: you
have to be able to see the design before you have the real details.

To see the same list from the browser console on any page:

```js
SITE.todos()
```

Currently outstanding:

- **Nine of the sixteen dishes carry a price of `999`**, a sentinel for
  "not a real price yet". The remaining seven are barbecue items with
  prices that look plausible and are not real. `python3 build.py` lists
  every one. The same prices are the `priceRange` and every `MenuItem` in
  the structured data, so they are the one placeholder this site now
  publishes as a fact to a search engine, on a page it calls the menu.
- Address, phone, WhatsApp number, all social links
- **`SITE.url`**, still the Vercel preview domain. Until it is the real
  one, every canonical on the site, the sitemap and the JSON-LD assert a
  domain that belongs to Vercel.
- Opening hours, and the largest table the room seats
- The cuisine list (`SITE.cuisine`) is inferred, not confirmed.
- The interlude quote and every paragraph of the story and experience copy
- The descriptions in `ITEMS` are one-line definitions ("Egg curry."),
  not copy. Nothing on the site displays them -- see *The menu format* --
  but they are the starting point for real menu writing.
- The opening hours, which currently say the same thing six days running

## The footer

The footer is a four-column grid: the mark and social links, the section
links, the address and phone, and the hours. It is kept short on purpose.
At 1280px it measures **399px tall**, down from 625px before the hours
were grouped and the padding was trimmed.

Most of that came from the hours. Six of the seven days are the same, so
`hours_table()` groups consecutive days that share hours and prints:

    Sunday – Friday        11:00 – 23:00
    Saturday               12:00 – 00:30

Printing the same hours six times says "nobody filled this in", which is
the opposite of what a room open for three generations wants to say. A row
carries the days it covers in `data-days`, so a day range survives the
grouping and the live "today" marker still works:

```html
<div data-days="0 1 2 3 4 5">Sunday – Friday …</div>
<div data-days="6">Saturday …</div>
```

The grouping is computed from `SITE.hours` at build time, not hardcoded,
so changing Saturday's hours in the config re-groups the table by itself.
Non-consecutive days that happen to share hours are spelled out rather
than implied by a range that would wrongly include the days between.

### The nashta and fried dishes are real

Nine dish names were supplied by the owner. Three spellings were changed
deliberately: "samosy", "pakory" and "pakore" were respelled to the
standard "Samosa" and "Pakora". "Began" and "Mirch" were left as written,
since those are correct regional spellings rather than typos.

---

## Editing

### Business details, hours, contact
Everything is in **`js/site-config.js`**. No other file needs touching.

```js
url:       'https://umar-hayat-chaska-point.vercel.app',  // the one domain; TODO
phone:     '+92 300 0000000',   // tel: link, footer, WhatsApp and JSON-LD all read this
whatsapp:  '923000000000',      // country code + number, no +, no spaces
email:     'umarmuhammadabdullah92@gmail.com',
currency:  { code: 'PKR', symbol: 'PKR' },
```

`build.py` reads this file with a small parser and fails loudly if a value
it needs is missing, rather than printing "None" into the page.

`url` is deliberately called out: it is the root of the canonical on every
page, of `sitemap.xml`, `robots.txt`, the manifest and the JSON-LD. It
must be an `https://` origin with no path, and the build refuses anything
else.

### Menu items
Live in `build.py` (the `ITEMS` list) because the markup is generated. After
editing, run:

```bash
python3 build.py
```

It rewrites all six pages, `favicon.svg`, `404.html`, `sitemap.xml`,
`robots.txt` and `site.webmanifest`, then checks that every page
has **exactly one `<h1>`** and never skips a heading level, that every
`id` on a page is unique, that every link to another page points at a page
that is actually built, that every same-page `#anchor` resolves, that
every local file a page asks for is on disk, that the canonical on each
page is that page's own absolute address, that the JSON-LD parses as a
Restaurant, and that the sitemap lists exactly the pages that are built.
Each of those renders a usable-looking page when it is wrong, so none of
them is obvious by eye.

It also refuses to publish a dish whose category is missing from the
config, and a category with no dishes. A dish nobody can filter to is a
dish nobody can find, and an empty category heading is worse than no
heading.

### Do not hand-edit the HTML
`build.py` is the source of truth for the header, footer, overlays and
every page's body. Anything typed into `index.html`, `menu.html`,
`story.html`, `private-dining.html`, `visit.html` or `reserve.html` is
overwritten on the next build. Business data goes in `js/site-config.js`
and `ITEMS` in `build.py`.

### Colours and typefaces
The palette is in `:root` at the top of `css/style.css`. The page is
deliberately near-black (`#0B0907`) with a warm off-black for alternating
sections, and the accent is the logo's own gold (`#DDC491`), which is
sampled from the artwork and only works on a dark ground.

The test suite checks the contrast of the text as it stands, so a palette
change that breaks WCAG AA fails the build rather than shipping.

Fonts are self-hosted and subset to Latin in `fonts/`. Nothing loads from
Google, and the test suite asserts the site makes zero third-party
requests.

---

## Images

There are no photographs yet. The layout reserves fixed-ratio slots so
that dropping images in later cannot reflow the page:

- hero and story slots are 4:5
- the signature dish slots are 4:5
- `img/social.png` is generated from the wordmark and palette as the
  1200x630 `og:image` and the JSON-LD `photo`. A real photograph, saved as
  `img/social.jpg`, replaces it without any other change at all.

Drop a file named after the slot into `img/` and rebuild. No markup to
edit. See `img/README.md`.

The brand mark is live text, not an image: it stays selectable, searchable
and crisp at any zoom, and it cannot fail to load. The favicon is a
generated `U` monogram written by `build.py`.

---

## The header and overlays

`js/header.js`. Centre wordmark over a nav row, with search and a phone
link on the right, replaced by a drawer below 860px.

- **Progressive enhancement.** Every link works and the page is navigable
  with JavaScript disabled. JS adds the search sheet, the drawer, the
  live "open now" status and the reveal transitions. If none of it loads,
  nothing is missed.
- **Overlays** (search, drawer) are focus-trapped, close on Escape, and
  restore focus to the control that opened them. They are `inert` while
  closed, so their links cannot be tabbed into.
- **Which page you are on is in the markup, not worked out in JS.** The
  server marks the current page with `aria-current="page"` in both copies
  of the nav, and marks the Reserve call to action on `/reserve`. There is
  no scroll spy: it existed to follow the reader down one long document,
  and each section is its own document now. A test checks the marking on
  all six pages, and that it does not change as the page scrolls.
- Section ids carry a `scroll-margin-top` measured from the real header
  height, so a jump to `#dish-...` never hides the dish under the bar.
- `js/menu.js` filters the menu and keeps the filter in the URL, so
  `/menu#fried` can be shared and arrives already filtered. It also
  watches the hash: following a search result to `#dish-...` while
  already on the menu is a same-document navigation, so nothing would
  re-run, and a guest who had narrowed the menu would be sent to a dish
  their own filter had hidden. The category holding the dish is opened
  and the target is scrolled to again.

## The menu format

The menu is a list of **names and prices**, nothing else: name on the
left, a dotted leader, price in gold on the right. No descriptions and no
serving notes, which is what a printed menu looks like and what makes two
columns of sixteen dishes scannable. The rows sit 15px apart for the same
reason.

The three signature cards are the same: a name and a price under the
photo. "Chicken curry" printed under a dish called Murag Chanay is a
guest reading the name back to us.

Prices are rendered with `currency.symbol`, which is `PKR` rather than
`Rs`. On its own "Rs" is ambiguous outside Pakistan, and a price a guest
cannot identify is a price they will ask about. It is three characters
wider and worth it. `build.py` fails if `currency.code` and
`currency.symbol` ever disagree, so the config cannot quietly end up
labelling a menu two different currencies.

The descriptions are still in `ITEMS` and are still worth keeping: they
are the raw material for real menu copy later. Nothing on the site reads
them. Search matches a dish **name** and its **category** only, so
removing the descriptions from the page did not cost search anything --
"charcoal" would not have found the grill dishes either way. The test
suite reads the description strings back out of `build.py` and fails if
any of them appear anywhere in the rendered page.

---

## Testing

```bash
bash test/run.sh
```

Builds the site, serves it, and drives it in headless Chrome: 418
assertions in the main pass and 8 in a second pass under
`--force-prefers-reduced-motion`, which confirms a guest who asks for less
motion is not left with a page of invisible content.

`test/serve.py` is the server, not `python3 -m http.server`. The site
links to `/menu` and `/story`, the host resolves those to `menu.html` and
`story.html`, and the stock server does not — with it, every clean URL
404s and the suite would be testing a site that only works on whichever
page the server happens to resolve.

Because the site is six pages, the suite drives six pages. Every page is
loaded and checked for its own title, description, single `<h1>`, unique
ids, nav that marks itself, and no link to a page or anchor that is not
there; text contrast is sampled on all six; the description leak, shop
copy and cart checks run on all six. The page-specific groups then say
which page they mean rather than inheriting whichever page the group
before them happened to leave: the menu is driven on `/menu`, the
reservation flow on `/reserve`, the hours on `/visit`, the hero and the
grids on `/`.

The main suite also covers alt text and accessible names, that the Vercel
redirects land on real destinations, the placeholder report, zero
third-party requests, geometry and horizontal overflow at five widths from
320px, tap-target sizes, WCAG AA contrast, the palette, header height,
search, the category filters and deep links including a hash change
arriving while the menu is already open, scroll reveal, the whole
reservation flow through to the generated WhatsApp message, opening hours
and the day grouping, the mobile drawer, and the column counts and
photo-slot ratios at each breakpoint.

### SEO guards

The newest group checks what software other than a browser reads, and it
checks it against the config rather than against the page, because a page
and its canonical are the kind of pair that drifts apart in silence:

- On every page: one canonical, and it is that page's own absolute
  address; `og:url` matches it; `og:image` is absolute; the manifest is
  linked.
- The JSON-LD on every page parses, declares a **Restaurant**, agrees with
  the config on name, phone, city and reservations, covers all seven days
  exactly once, groups the days the page groups, and lists every dish with
  a number for a price. The six pages must state the same facts about the
  restaurant and describe themselves with their own urls.
- `sitemap.xml` is served, lists exactly the pages `build.py` builds, and
  does not list the 404. `robots.txt` points at that sitemap by absolute
  url. `site.webmanifest` parses, names a real icon path, and uses the
  same `--bg` the stylesheet does.
- The 404 has one `<h1>`, the site's header and footer, no canonical and
  no structured data, `noindex, follow`, links that are large enough to
  tap, no sideways overflow at 360px, and nothing hidden behind a scroll
  reveal — the page is a response, not a document.
- Every page title is set at the size of *the same heading* on the home
  page. This group exists because it was once 30px everywhere: the
  stylesheet styled the section head as `h2`, and when each section
  became its own page and the top heading became an `<h1>`, every page
  title fell back to the browser default. The check compares sizes rather
  than asserting a number, so changing the type scale does not break it.
- What is flagged as a placeholder is tested from both ends: put
  `hello@example.com` into `SITE.email`, and `SITE.todos()` has to add
  exactly one line; take it out, and the line has to go.

Several of them are guards against a decision being quietly undone:

- The menu check reads every description and serving note out of
  `build.py` and fails if any appears anywhere in any page.
- The hours check fails if a day is listed twice, left out, or given a row
  of its own when it shares hours with the day next to it.
- `build.py` fails if a page has other than exactly one `<h1>`, which is
  how five pages were caught having none.
- `build.py` also fails if a page's canonical is not its own address, if
  the JSON-LD does not parse, if the sitemap and the built pages disagree,
  if robots does not point at the sitemap, or if the manifest or sitemap
  are not valid files -- and the browser suite independently re-proves
  each of those from the rendered output, so a check that only lives in
  one place cannot be talked out of working.
- `ok()` fails the run if an assertion name is used twice, because a stale
  copy of an old check is how a page quietly stops being tested while
  everything is still green. It caught one on the first run.

Each of these was confirmed to fail by putting the old code back before
being trusted.

`test/run.sh` also fails on a harness exception, and on a script that
never ran a single assertion. A throw part way through leaves a short but
entirely passing summary, because every assertion before it ran and none
of them failed — the page prints `HARNESS ERROR` and the runner treats it
as a failure rather than reporting a green run that only ran half the
checks. A syntax error in the test script prints nothing at all, which
looks identical to a hang, so the runner says so and names the group it
reached.

Two things the suite deliberately does not do: it does not compare against
screenshots, and it has only ever been run in Chrome. Nothing here has been
checked in Safari or Firefox.
