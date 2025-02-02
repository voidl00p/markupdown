from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from .site import Site


class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        url_path = Path(self.path.strip("/"))
        file_path = self.directory / url_path

        if not file_path.exists():
            # Check if there's an .html file
            possible_html_path = file_path.with_suffix(".html")
            if possible_html_path.exists():
                self.path = str(possible_html_path.relative_to(self.directory))
                print(f" Serving {self.path}")

        return super().do_GET()


def serve(site: Site | None = None, port: int = 8000):
    site = site or Site()

    handler = partial(CustomHandler, directory=str(site.site_dir))
    server = HTTPServer(("0.0.0.0", port), handler)

    print(f"Serving on http://localhost:{port}")
    server.serve_forever()
