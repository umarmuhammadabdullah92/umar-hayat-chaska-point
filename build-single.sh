#!/usr/bin/env bash
# Regenerates presentation-single.html with all images embedded (base64).
# Run this after adding new images or editing presentation.html.
cd "$(dirname "$0")"

OUT="presentation-single.html"

python3 - "$OUT" << 'EOF'
import base64, os, re, sys

out = sys.argv[1]
html = open('presentation.html', encoding='utf-8').read()

def data_uri(path):
    ext = path.rsplit('.', 1)[-1].lower()
    mime = 'image/png' if ext == 'png' else 'image/jpeg'
    b = base64.b64encode(open(path, 'rb').read()).decode()
    return 'data:%s;base64,%s' % (mime, b)

out_html = re.sub(r'src="(images/[^"]+)"', lambda m: 'src="%s"' % data_uri(m.group(1)), html)
open(out, 'w', encoding='utf-8').write(out_html)
print('built %s (%d bytes)' % (out, len(out_html)))
EOF

if [ -d /home/abdullah/Desktop/slides ]; then
  cp -f "$OUT" /home/abdullah/Desktop/slides/
  echo "copied to /home/abdullah/Desktop/slides/"
fi
