import os
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from .site import Site


class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.strip("/")
        # If the request does not contain a file extension
        if not os.path.exists(path):
            possible_html_path = path + ".html"
            if os.path.exists(possible_html_path):
                self.path = "/" + possible_html_path

        return super().do_GET()


def serve(site: Site, port: int = 8000):
    handler = partial(CustomHandler, directory=str(site.site_dir))
    server = HTTPServer(("0.0.0.0", port), handler)

    print(f"Serving on http://localhost:{port}")
    server.serve_forever()
