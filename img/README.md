# Images

Drop photo files in this folder. The filename is what wires them up — there
is nothing else to edit.

## How it works

`build.py` looks for each slot by name and extension. A file that exists
becomes an `<img>`; a file that does not exist becomes an empty frame of the
same aspect ratio, labelled with the filename to drop in. So you can see
exactly where each photo goes before you have it, and the layout does not
change when the photo arrives.

Run `python3 build.py` after adding files.

Accepted extensions, in priority order — if two files share a name, the
first one listed wins:

    .jpg   .jpeg   .png   .webp   .avif

## The slots

Photos live on the menu only. The home and about pages deliberately have
no image slots.

| File | Goes on | Ratio | Subject |
|---|---|---|---|
| `nashta.jpg` | Menu | 16:9 | Nashta |
| `barbecue.jpg` | Menu | 16:9 | Barbecue |
| `fried.jpg` | Menu | 16:9 | Fried items |
| `social.jpg` | — | 1200x630 | Social share card |

Each of the three menu photos is captioned with its category name, so they
read as the menu's three sections.

## Notes

**`social.jpg` is the one that matters most for sharing.** Until it exists,
`og:image` falls back to the logo, which renders as a small square in a link
preview. 1200x630 is the size every platform expects.

**All three menu photos are lazy loaded**, so they never delay the page.
There is no eager image on the site now that the hero is gone.

**Before launch, no slot should be empty.** Run:

    python3 build.py

and look for a slot left showing a filename instead of a photo. `git status`
will also list any image files you have not committed yet.

**Menu items have no photo slots yet.** If you want a picture on each of
the 23 dishes rather than one per category, that is a change to
`item_card()` in `build.py` and a per-item `img` field on `ITEMS` — say the
word and it can be added.

**Keep files small.** These are displayed at most 1200px wide, so anything
larger is wasted upload on a phone connection. Target under 300KB each.
