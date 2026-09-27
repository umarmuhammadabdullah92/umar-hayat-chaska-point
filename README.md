# Umar Hayat Chaska Point

Static site. **One page**, no build step and no framework.

```
index.html    The whole site, as three sections:
              #menu  #about  #contact
```

The nav is in-page anchors, not links to separate documents, so there is
no page to load between sections. The old `/menu`, `/about` and
`/contact` URLs are kept alive as 301s in `vercel.json`, each pointing at
its section, so links shared before the collapse still land in the right
place.

---

## Read this before the site goes live

**This is not a Shopify theme and it is not a working shop.** It is static
HTML on Vercel. The header, navigation, search, currency selector and cart
all work, but every one of them runs in the visitor's browser with nothing
behind it.

| Feature | What actually happens |
|---|---|
| Cart | An array in `localStorage`, on that one device. Not shared between devices or browsers. Lost if site data is cleared. |
| Checkout | **Nothing.** No payment processor, no order, no server. The button shows a notice and stops. |
| Account | An email string in `localStorage`. No login, no password, no session, no order history. |
| Currency | Display-only. Prices are stored once in PKR and converted at a fixed rate. Never treat the figure as a real conversion. |
| Menu | Static HTML. Prices do not come from a database and cannot be changed without editing and re-committing. |

If you need real commerce, this needs to move to Shopify (or another
platform) — the theme there is Liquid and shares no structure with this.

### Images

Every dish has a photo slot above its name, price and Add to cart button.
The frame is a fixed 4:3 whether or not a photo is in it, so the grid
cannot reflow when the photos land. Drop a file named after the dish id
into `img/` — `img/samosa-fried.jpg` fills the Samosa slot — and run
`python3 build.py`. No markup to edit. See `img/README.md`.

`img/social.jpg` is separate: it becomes the `og:image` used for link
previews on WhatsApp, Facebook and X. Drop a 1200x630 file there too.
Until then the logo is used, which renders poorly in a share preview.

## Theming

White is the default. Rebrand by editing the `:root` block at the top of
`css/style.css` only. The Eerie Black palette is still there under
`html[data-theme="dark"]` for anyone who sets it, but nothing links to it.

The page ground is a warm off-white (`#F7F4EF`) and the dish cards are pure
white (`#FFFFFF`), not the other way round. On a pure white page the white
cards would have nothing but a hairline between them and the grid would
read as one flat sheet. Keep the two grounds distinct if you rebrand.

The accent is the logo's gold, darkened from `#DDC491` to `#8A6634` so it
carries text contrast on a white ground. The original only worked on a
dark background.

Two things to know if you edit the palette:

- The page and the card grounds are close in value (`#F7F4EF` against
  `#FFFFFF`), so `--shadow-1` and `--line` are what separate them, on top
  of the difference between the grounds themselves. If the menu ever looks
  like flat text, those are the reason.
- Body copy sits at about 5.2:1 and muted text at the same, against a
  4.5:1 requirement. There is not much headroom, so lightening `--fg`
  further will fail the contrast check.

## The brand mark

There isn't one. The header shows the name as live text in the display
face (`.wordmark` in `css/style.css`), which stays selectable, searchable
and crisp at any zoom and cannot fail to load. Size is
`clamp(17px, 2.15vw, 30px)`: 30px at the top so it carries the same
visual weight as the 72px logo image it replaced, down to a 17px floor
that still fits a 320px screen.

`umarhayatchaskapoint-trimmed.png` is still in the repo for one reason
only: it is the `og:image`, so a shared link has something to render. It
is a poor share card. Drop a 1200x630 `img/social.jpg` in and that
becomes the preview instead, at which point the PNG can go too.
`umarhayatchaskapoint.png` is the untrimmed original, referenced by nothing.

The favicon is a generated `U` monogram (`FAVICON` in `build.py`), not an
image file.

## Placeholder data

These are **invented**, not real, and must be replaced before launch:

- **Every barbecue item, its description and its price** (`build.py`, the
  `ITEMS` list). The nashta and fried lists are real dishes but their
  prices and descriptions are not, see below.
- Address, phone, WhatsApp number, email
- All social profile URLs
- Opening hours
- Category names
- Delivery fee, free-delivery threshold, minimum order
- The USD exchange rate (a guess, and it will drift)

To see what is still outstanding, open the browser console on any page:

```js
SITE.todos()
```

### The nashta and fried dishes are real

These were supplied by the owner, and the spellings are theirs rather than
normalised, with one exception noted below.

**Nashta** — Murag Chanay, Anday Chanay, Haleem Chawal

**Fried** — Samosa, Pakora, Aloo Ki Tikki, Began Pakora, Mirch Pakora,
Fried Naan

Three spellings were changed, deliberately: the owner wrote "samosy",
"pakory" and "pakore", which were respelled to the standard "Samosa" and
"Pakora". "Began" and "Mirch" were left as written, since those are
correct regional spellings rather than typos. This is the one place the
owner's wording was not preserved verbatim.

Two things about all nine dishes are still placeholders:

- **Prices are `999`, used as a sentinel for "not a real price yet".**
  All nine real dishes carry it, so the menu total is 9 sentinels and 7
  real-looking-but-invented barbecue prices. Grep the `ITEMS` list for
  `999` to find every one. The value is deliberately higher than the
  minimum order so the cart behaves, and deliberately round so it is
  obviously not a price anyone charged.
- **Descriptions are one-line definitions** ("Egg curry.", "Brinjal,
  battered and fried."), not copy. They say what the dish is without
  claiming anything about how it is made, because nothing is known yet.

To find all outstanding prices at once:

```sh
grep -n "999" build.py
```

---

## Editing

### Business details, prices, hours, currencies
Everything is in **`js/site-config.js`**. No other file needs touching.

```js
phone: '+92 300 0000000',   // the tel: link, footer and WhatsApp all read this
rate:  { PKR: 1, USD: 0.0036 },
delivery: { fee: 150, freeOver: 3000, minOrder: 500 },
```

Prices are authored **once, in PKR integers**. Every other currency is
derived from that single number, so the cart total can never drift out of
step with the line items.

### Menu items
Menu items live in `build.py` (the `ITEMS` list) because the markup is
generated. After editing, run:

```bash
python3 build.py
```

It rewrites `index.html`, then fails the build if a nav anchor has no
matching section, or if the page references a local file that is not on
disk. Both of those render a usable page, so neither is obvious by eye.

### Do not hand-edit the HTML
`build.py` is the source of truth for the shared header, footer and
overlays. Anything typed into `index.html` will be overwritten on the next
`python3 build.py`. This is deliberate: the header used to be copy-pasted
into each page and the copies silently drifted apart.

### Colours and typefaces
The palette is in `:root` at the top of `css/style.css`. The gold accent
was sampled from the logo artwork, but the logo's own gold (`#DDC491`) only
works on black: on white it measures about 1.6:1. The default light theme
therefore darkens it to `#8A6634`, the same hue at a usable contrast.

Fonts are self-hosted and subset to Latin in `fonts/`. Drop in four new
`woff2` files and update the `@font-face` rules. Nothing loads from
Google, so the site makes zero third-party requests.

---

## The header

`js/header.js`. Centred logo in a `1fr auto 1fr` grid over a separate nav
row, utility icons
(search, account, currency, cart) on the right, category nav beneath,
replaced by a drawer below 860px.

- **Progressive enhancement.** Every link works and the page is navigable
  with JavaScript disabled. JS only adds the search sheet, the currency
  popover, drawer animation and current-page marking.
- **Prices are PKR-authoritative**, formatted by `js/money.js`.
- **Overlays** (search, account, drawer, cart) are focus-trapped, close on
  Escape, and restore focus to the button that opened them.
- The scroll spy marks the section you are reading with
  `aria-current="true"`, in both copies of the nav. With one page there is
  no "current page", so nothing claims `aria-current="page"`.
- Section ids carry a `scroll-margin-top` measured from the real header
  height, so jumping to `#contact` never hides its heading under the
  sticky bar.

---

## Testing

`/tmp/opencode/header-test.js` runs 320 checks in headless Chrome:
geometry and accessibility at five widths, cart arithmetic, currency
switching and persistence, search, the mobile drawer, category filters,
deep links, WCAG contrast in both themes, the anchor navigation and scroll
spy, the heading outline, the photo slots, and a check that the site makes no third-party
requests.

It also asserts the three deleted page files are still gone and that no
`.html` link survives anywhere in the source, which is the failure mode
that would otherwise only show up as a 404 in a browser console.

Not covered: real visual review, real payment, and behaviour in Safari or
Firefox — only Chrome was tested.
