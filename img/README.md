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

| File | Goes on | Ratio | Subject |
|---|---|---|---|
| `hero.jpg` | Home | 21:9 | The grill, mid-service |
| `gallery-1.jpg` | Home | 4:3 | Gallery photo 1 |
| `gallery-2.jpg` | Home | 4:3 | Gallery photo 2 |
| `gallery-3.jpg` | Home | 4:3 | Gallery photo 3 |
| `story.jpg` | About | 16:9 | The shopfront or the counter |
| `kitchen-1.jpg` | About | 4:3 | Kitchen photo 1 |
| `kitchen-2.jpg` | About | 4:3 | Kitchen photo 2 |
| `nashta.jpg` | Menu | 16:9 | Nashta |
| `barbecue.jpg` | Menu | 16:9 | Barbecue |
| `fried.jpg` | Menu | 16:9 | Fried items |
| `social.jpg` | — | 1200x630 | Social share card |

## Notes

**`social.jpg` is the one that matters most for sharing.** Until it exists,
`og:image` falls back to the logo, which renders as a small square in a link
preview. 1200x630 is the size every platform expects.

**The hero is the only eagerly loaded image** — it is almost certainly your
largest contentful paint, so it gets `fetchpriority="high"` and does not wait
for the lazy loader. Everything else is lazy.

**Before launch, no slot should be empty.** Run:

    python3 build.py

and look for a slot left showing a filename instead of a photo. `git status`
will also list any image files you have not committed yet.

**Keep files small.** These are displayed at most 1200px wide, so anything
larger is wasted upload on a phone connection. Target under 300KB each.
