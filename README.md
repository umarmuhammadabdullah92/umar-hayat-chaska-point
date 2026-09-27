# Umar Hayat Chaska Point

Static site. Four pages, one shared header, no build step and no framework.

```
index.html    Homepage
menu.html     Menu
about.html    About Us
contact.html  Locations & Contact
```

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

### Placeholder data

These are **invented**, not real, and must be replaced before launch:

- **Every menu item, description and price** (`build.py`, the `ITEMS` list)
- Address, phone, WhatsApp number, email
- All social profile URLs
- Opening hours
- Category names
- Delivery fee, free-delivery threshold, minimum order
- The USD exchange rate (a guess, and it will drift)
- All About Us copy

To see what is still outstanding, open the browser console on any page:

```js
SITE.todos()
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

It rewrites all four pages and then verifies the header markup is still
byte-identical across them.

### Do not hand-edit the HTML
`build.py` is the source of truth for the shared header, footer and
overlays. Anything typed into `index.html` will be overwritten on the next
`python3 build.py`. This is deliberate: the header used to be copy-pasted
into each page and the copies silently drifted apart.

### Colours and typefaces
The palette is in `:root` at the top of `css/style.css`. The gold accent
(`--accent: #DDC491`) was sampled from the logo artwork.

Fonts are self-hosted and subset to Latin in `fonts/`. Drop in four new
`woff2` files and update the `@font-face` rules. Nothing loads from
Google, so the site makes zero third-party requests.

---

## The header

`js/header.js`. Centred logo in a `1fr auto 1fr` grid, utility icons
(search, account, currency, cart) on the right, category nav beneath,
replaced by a drawer below 860px.

- **Progressive enhancement.** Every link works and the page is navigable
  with JavaScript disabled. JS only adds the search sheet, the currency
  popover, drawer animation and current-page marking.
- **Prices are PKR-authoritative**, formatted by `js/money.js`.
- **Overlays** (search, account, drawer, cart) are focus-trapped, close on
  Escape, and restore focus to the button that opened them.
- Exactly one nav item claims `aria-current="page"`. Category links share
  the `/menu` path, so they are matched on the hash instead.

---

## Testing

`/tmp/opencode/header-test.js` runs 274 checks in headless Chrome:
geometry and accessibility on all four pages at five widths, cart
arithmetic, currency switching and persistence, search, the mobile drawer,
category filters, deep links, WCAG contrast in both themes, and a check
that the site makes no third-party requests.

Not covered: real visual review, real payment, and behaviour in Safari or
Firefox — only Chrome was tested.
