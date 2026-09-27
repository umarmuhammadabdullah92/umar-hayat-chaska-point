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

---

## Read this before the site goes live

**Nothing on this site is real business data.** The address, phone number,
WhatsApp number, email, opening hours, social links, founding year, and
almost all of the prose are invented so the layout could be built and
judged. They must be replaced. See *Placeholder data* below.

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
  every one.
- Address, phone, WhatsApp number, email, all social links
- Opening hours, and the largest table the room seats
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
phone:     '+92 300 0000000',   // tel: link, footer and WhatsApp all read this
whatsapp:  '923000000000',      // country code + number, no +, no spaces
email:     'hello@example.com',
currency:  { code: 'PKR', symbol: 'PKR' },
```

`build.py` reads this file with a small parser and fails loudly if a value
it needs is missing, rather than printing "None" into the page.

### Menu items
Live in `build.py` (the `ITEMS` list) because the markup is generated. After
editing, run:

```bash
python3 build.py
```

It rewrites all six pages and `favicon.svg`, then checks that every page
has **exactly one `<h1>`** and never skips a heading level, that every
`id` on a page is unique, that every link to another page points at a page
that is actually built, that every same-page `#anchor` resolves, and that
every local file a page asks for is on disk. Each of those renders a
usable-looking page when it is wrong, so none of them is obvious by eye.

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
- `img/social.jpg` is the `og:image` for link previews on WhatsApp,
  Facebook and X. Until it exists the logo is used, which previews badly.

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

Builds the site, serves it, and drives it in headless Chrome: 271
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

Several of them are guards against a decision being quietly undone:

- The menu check reads every description and serving note out of
  `build.py` and fails if any appears anywhere in any page.
- The hours check fails if a day is listed twice, left out, or given a row
  of its own when it shares hours with the day next to it.
- `build.py` fails if a page has other than exactly one `<h1>`, which is
  how five pages were caught having none.
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
