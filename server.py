#!/usr/bin/env python3
import http.server, os, sys

PORT = int(os.environ.get("PORT", 4600))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silence access logs

with http.server.HTTPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"tictactoe serving on port {PORT}", flush=True)
    httpd.serve_forever()
