#!/usr/bin/env python3
"""Static file server for the browser tests.

python3 -m http.server is not enough any more. The site links to /menu,
/story and /reserve, and the host serves those by rewriting them to
menu.html, story.html and reserve.html. The stock server has no such
rule, so every clean URL 404s and the suite would be testing a site that
only works on the one page the server happens to resolve.

So this resolves them the same way, and nothing else. It serves the
directory it is pointed at, refuses to escape it, and sets the handful of
headers the real host sets, so cache and content-type behaviour is close
enough to production for the tests to mean something.
"""
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.realpath(sys.argv[1] if len(sys.argv) > 1 else '.')
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8931


class Handler(SimpleHTTPRequestHandler):
    extensions_map = dict(SimpleHTTPRequestHandler.extensions_map)
    extensions_map.update({
        '.woff2': 'font/woff2',
        '.svg': 'image/svg+xml',
        '.webp': 'image/webp',
        '.avif': 'image/avif',
        '.json': 'application/json',
    })

    def translate_path(self, path):
        # Strip the query and any trailing slash, then try the exact
        # name, then name.html, so /menu finds menu.html. Anything that
        # would climb out of ROOT is refused by super().
        clean = path.split('?', 1)[0].split('#', 1)[0]
        if clean.endswith('/'):
            clean += 'index.html'
        full = super().translate_path(clean)
        if os.path.isfile(full + '.html'):
            return full + '.html'
        return full

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, *args):
        pass  # the suite output is the log


if __name__ == '__main__':
    os.chdir(ROOT)
    ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
