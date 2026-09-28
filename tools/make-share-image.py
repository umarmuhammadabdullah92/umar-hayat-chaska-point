#!/usr/bin/env python3
"""
Renders the share card: tools/share-card.html -> img/social.png.

    python3 tools/make-share-image.py

A link to the site on WhatsApp, Facebook or X is shown to someone who has
never heard of it, in a feed, at thumbnail size. What they see is one
image, and the logo on its own is 426x278 -- a quarter of the width it is
displayed at, blurred, in the corner of a grey box. 1200x630 is the size
those platforms ask for, so the card is laid out at that size rather than
cropped from something smaller.

The card is kept as HTML next to this script, so the wordmark, the palette
and the two typefaces are the site's own and there is nothing to keep in
step by hand. Changing the card means editing the HTML and running this.

This is a typographic card, not a photograph. A photograph of the room or
the grill is better and should replace it: save it as img/social.jpg and
rebuild, and build.py prefers the photograph over this one without any
other change. See img/README.md.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'share-card.html')
OUT = os.path.join(ROOT, 'img', 'social.png')
TMP = os.path.join(ROOT, 'img', '.social-render.png')

W, H = 1200, 630
CHROME_CANDIDATES = ('google-chrome', 'chromium', 'chromium-browser')


def find_chrome():
    for name in CHROME_CANDIDATES:
        path = subprocess.run(['which', name], capture_output=True,
                              text=True).stdout.strip()
        if path:
            return path
    raise SystemExit('no Chrome found; set CHROME=/path/to/chrome')


def main():
    chrome = os.environ.get('CHROME') or find_chrome()
    if not os.path.exists(SRC):
        raise SystemExit('missing source card: ' + SRC)

    # Render to a hidden name and rename at the end, so an interrupted run
    # cannot leave a truncated card sitting at the path the site reads.
    subprocess.run(
        [chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars',
         '--no-sandbox', '--force-device-scale-factor=1',
         '--window-size=%d,%d' % (W, H),
         '--default-background-color=00000000',
         '--screenshot=' + TMP, 'file://' + SRC],
        check=True, capture_output=True)

    if not os.path.exists(TMP):
        raise SystemExit('chrome wrote no screenshot')
    size = os.path.getsize(TMP)
    if size < 5000:
        os.remove(TMP)
        raise SystemExit('screenshot is %d bytes, which is a blank card. '
                         'The fonts are loaded over file:// and will not '
                         'load if the card is opened from a different path.' % size)

    # PNG rather than JPEG on purpose: the card is flat colour and text, so
    # JPEG's artefacts land exactly on the letterforms, and lossless is also
    # about a fifth of the size here.
    os.replace(TMP, OUT)
    print('  %-24s %7d bytes  %dx%d' % ('img/social.png', size, W, H))
    print('  rebuild to publish:  python3 build.py')


if __name__ == '__main__':
    main()
