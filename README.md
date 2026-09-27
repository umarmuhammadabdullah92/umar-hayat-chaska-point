# Website

Static HTML/CSS/JS. No build step, no framework, no dependencies.

## Setting up

1. Fill in `js/site-config.js` — name, tagline, phone, logo, currency.
2. Edit `index.html`: the `<head>` meta block and the `<main>` content.
3. Replace `favicon.svg` and the entries in `manifest.json`.
4. Rebuild `sitemap.xml` and `robots.txt` for your domain.

## Files

| File | Purpose |
| --- | --- |
| `js/site-config.js` | **Edit this first.** All business details in one place. |
| `js/main.js` | Theme, mobile drawer, footer year, order links. |
| `js/header.js` | Header behaviour, search, currency, account panel. |
| `js/cart.js` | Order cart (optional). |
| `css/style.css` | All styles. Rebrand via the `:root` variables. |

Delete `js/header.js` / `js/cart.js` and their `<script>` tags if you don't
need search or a cart — nothing else depends on them.

## Adding a product

The cart has no product markup of its own. Call it either way:

```js
App.addToCart({name:'Coffee', price:350, qty:1, unit:'cup', img:'images/coffee.jpg'});
```

Or declaratively, from a button inside an element with data attributes:

```html
<article data-name="Coffee" data-price="350" data-unit="cup" data-img="images/coffee.jpg">
  <span data-qty>1</span>
  <button onclick="App.addToCart(this)">Add to order</button>
</article>
```

Products are matched by `data-name`, so the same name merges quantities.
Prices are plain numbers in your base currency (PKR).

## Search

`SITE.searchIndexUrl` points search at the page listing your products; it
parses `data-name` / `data-price` attributes into a client-side index, cached
in `localStorage`. Leave it empty to disable search.

## Local preview

    python3 -m http.server 8000

## Deploy

Vercel, with `cleanUrls` enabled. The cart and account panel are
`localStorage`-only — there is no backend, so they are per-device.
