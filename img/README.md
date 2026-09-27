# Images

**The site currently shows no images in its pages.** The image sections
were built, then removed on request, so this folder is empty apart from
this file.

## The one image that still matters

`og:image` is what WhatsApp, Facebook, X and iMessage show when someone
shares a link to the site. It currently points at the logo, which is
426x258 and renders as a small, badly cropped square in a link preview.

Drop a **1200x630** image here as:

    img/social.jpg

and run `python3 build.py`. It is picked up automatically, with no other
edit. `.jpg`, `.jpeg`, `.png`, `.webp` and `.avif` all work.

Until that file exists the logo is used, which is better than a broken
preview but not good. This is the highest-value image on the site.

## If images come back

The machinery for drop-in image slots was removed along with the
sections. Rebuilding it means adding a `fig()` helper to `build.py` that
looks for `img/<name>.<ext>` and renders either an `<img>` or an empty
frame of a fixed aspect ratio, so a photo can be added later without
touching any markup.

Do not simply paste `<img>` tags into the generated HTML. Every page is
overwritten by `python3 build.py`, so hand edits do not survive a build.
