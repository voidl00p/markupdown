from __future__ import annotations

import shutil
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse
import time

import mistune
from liquid import Environment, FileSystemLoader

from .files import PAGE_TITLE_AST_PATH, MarkdownFile, SiteFile


def cp(
    glob_pattern: str,
    dest_dir: Path | str = "site",
    relative_to: Path | str = ".",
) -> None:
    """
    Copy files matching a glob pattern to a destination directory.

    Args:
        glob_pattern: The glob pattern to match files to copy.
        dest_dir: The destination directory to copy files to. Defaults to "site".
        relative_to: The path that the destination structure should be relative to. Defaults to current directory.
    """
    root, paths = ls(glob_pattern)
    dest_dir = Path(dest_dir)
    relative_to = Path(relative_to)

    for src_file in paths:
        dest_file = src_file.relative_to(root).relative_to(relative_to)
        dest_file = dest_dir / dest_file
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)


def transform(
    glob_pattern: str,
    func: Callable[[MarkdownFile, SiteFile], None],
) -> None:
    """
    Apply a transformation function to markdown files matching a glob pattern.

    Args:
        glob_pattern: The glob pattern to match markdown files to transform.
        func: A callable that takes a MarkdownFile and SiteFile as arguments and applies
            the desired transformation.
    """
    root, paths = ls(glob_pattern)
    site_root = root / "site"

    for path in paths:
        if path.is_file():
            path = path.relative_to(site_root)
            func(MarkdownFile(site_root, path), SiteFile(site_root))


def ls(glob_pattern: str, root: Path | None = None) -> tuple[Path, list[Path]]:
    """
    List files matching a glob pattern from a root directory.

    Args:
        glob_pattern: The glob pattern to match files.
        root: The root directory to start the search from. Defaults to current directory.

    Returns:
        A tuple containing (root_path, list_of_matching_paths).
    """
    root = root or Path.cwd()

    # list() to snap shot the directory contents so we don't go into a recursive loop.
    # not memory efficient, but it fixes the issue.
    return root, list(root.glob(glob_pattern))


def title(glob_pattern: str, ast_pattern: str | None = None) -> None:
    """
    Sets titles for markdown files that don't have a `title` field in their frontmatter.
    Uses the first # h1 as the title if ast_pattern is not provided. If no # h1 is found,
    the filename is used with the following rules:

    - Replace .md with empty string
    - Replace - with spaces
    - Capitalize

    Args:
        glob_pattern: The glob pattern of the markdown files to update.
        ast_pattern: The jsonpath expression to select the title.
            Defaults to the first # h1.
    """
    ast_pattern = ast_pattern or PAGE_TITLE_AST_PATH

    def _title(md_file: MarkdownFile, _: SiteFile) -> None:
        if not "title" in md_file.frontmatter():
            title = md_file.default_title(ast_pattern)
            md_file.update_frontmatter({"title": title})
            md_file.save()

    transform(glob_pattern, _title)


def nav(glob_pattern: str) -> None:
    """
    Update site.yaml in the staging directory with a "nav" field containing a list of
    title/link entries based on the following criteria:
    - Pages with nav: true in frontmatter
    - First-level index.md files without nav: false in frontmatter
    - Root-level non-index.md files without nav: false in frontmatter

    Args:
        glob_pattern: The glob pattern of the markdown files to update.
    """

    def _nav(md_file: MarkdownFile, site_file: SiteFile) -> None:
        frontmatter = md_file.frontmatter()
        nav_entries = site_file.metadata().get("nav", [])
        assert isinstance(nav_entries, list)

        # Skip if nav is explicitly set to false
        if frontmatter.get("nav") is False:
            return

        # Calculate relative path parts from site directory
        file_name = md_file.path.name

        # Include if any of these conditions are met:
        # 1. nav is explicitly set to true
        # 2. file is index.md in first level of children
        # 3. file is in root and not index.md
        if (
            frontmatter.get("nav") is True
            or (file_name == "index.md" and len(md_file.path.parts) == 2)
            or (len(md_file.path.parts) == 1 and file_name != "index.md")
        ):
            # Get the title from frontmatter, fallback to filename without extension
            title = frontmatter.get("title", md_file.default_title())

            # Create new nav entry
            new_entry = {"title": title, "link": md_file.link()}

            # Remove any existing entries with the same title
            nav_entries = [entry for entry in nav_entries if entry["title"] != title]

            # Add nav entry
            nav_entries.append(new_entry)

            # Sort nav entries by title
            nav_entries.sort(key=lambda x: x["title"])

            # Update site file with new nav entries
            site_file.update_metadata({"nav": nav_entries})
            site_file.save()

    transform(glob_pattern, _nav)


def index(glob_pattern: str) -> None:
    """
    Add page links to the frontmatter of index.md files for all of its siblings and
    subdirectories with an index.md. Each entry will contain title and link for the
    pages in that directory.

    For each index.md file:
    - Find all sibling .md files (excluding index.md itself)
    - Find all subdirectories containing an index.md file
    - Add links to these pages in a `pages` field in the frontmatter

    Args:
        glob_pattern: The glob pattern of the markdown files to update.
    """

    def _index(index_file: MarkdownFile, _: SiteFile) -> None:
        # Only process index.md files
        if index_file.path.name != "index.md":
            return

        # Get the directory containing this index.md
        dir_path = index_file.path.parent
        root = index_file.root

        pages = []

        # Process sibling markdown files (excluding index.md)
        for sibling in (root / dir_path).glob("*.md"):
            if sibling.name == "index.md":
                continue
            sibling_md = MarkdownFile(root, dir_path / sibling.name)
            pages.append(
                {
                    "title": sibling_md.frontmatter().get(
                        "title", sibling_md.default_title()
                    ),
                    "link": sibling_md.link(),
                }
            )

        # Process subdirectories containing index.md
        for subdir in (root / dir_path).iterdir():
            if not subdir.is_dir():
                continue
            index_path = subdir / "index.md"
            if not (root / index_path).is_file():
                continue
            index_path = index_path.relative_to(root)
            subdir_md = MarkdownFile(root, index_path)
            pages.append(
                {
                    "title": subdir_md.frontmatter().get(
                        "title", subdir_md.default_title()
                    ),
                    "link": subdir_md.link(),
                }
            )

        # Sort pages by title
        pages.sort(key=lambda x: x["title"])

        # Update frontmatter with pages
        if pages:
            index_file.update_frontmatter({"pages": pages})
            index_file.save()

    transform(glob_pattern, _index)


class LinkRenderer(mistune.HTMLRenderer):
    def __init__(self, root: Path | str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.root = Path(root)

    def link(self, text, url, title=None):
        """
        If the URL is relative, append ".html" to it.
        """
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = url.strip(".md")
            url = url.strip("/")
            if not (self.root / url).is_dir():
                url += ".html"
            url = "/" + url
        return super().link(text, url, title)


def render(
    glob_pattern: str,
    site: dict[str, object] = {},
    template_dir: str | Path = "templates",
) -> None:
    """
    Render markdown files to HTML using liquid templates.

    For each markdown file:
    - Convert markdown content to HTML
    - Apply liquid template specified in frontmatter (or default.liquid)
    - Write rendered HTML to the same location with .html extension

    Args:
        glob_pattern: The glob pattern of the markdown files to render.
        site: Dictionary of site configuration. Defaults to {}.
        template_dir: Directory containing liquid templates. Defaults to "templates".

    Raises:
        FileNotFoundError: If template directory doesn't exist
        ValueError: If no template is specified and no default.liquid exists
    """
    # Initialize Liquid environment
    template_dir = Path(template_dir).absolute()

    if not template_dir.is_dir():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")
    env = Environment(loader=FileSystemLoader(template_dir))

    def _render(md_file: MarkdownFile, _: SiteFile) -> None:
        # Create target HTML file path
        target_file = md_file.root / md_file.path.with_suffix(".html")

        # Convert markdown to HTML
        format_markdown = mistune.create_markdown(
            escape=False,
            plugins=["strikethrough", "footnotes", "table", "speedup"],
            renderer=LinkRenderer(md_file.root),
        )
        html_content = format_markdown(md_file.content())

        # Get template name from frontmatter or use default
        frontmatter = md_file.frontmatter()
        if page_template := frontmatter.get("template"):
            page_template = str(page_template)
        else:
            page_template = "default"

        if not page_template.endswith(".liquid"):
            page_template += ".liquid"

        # Render template with content and frontmatter variables
        try:
            template = env.get_template(page_template)
        except FileNotFoundError as e:
            raise ValueError(
                f"Template not found for {template_dir}: {page_template}"
            ) from e

        rendered = template.render(
            content=html_content,
            page=frontmatter,
            site=site | SiteFile(md_file.root).metadata(),
        )

        # Write rendered content to file
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(rendered)

    transform(glob_pattern, _render)


def init(root_path: Path | str = ".") -> None:
    """
    Initialize a new markupdown project by copying the example directory structure.

    Args:
        root_path: The target directory where the example should be copied.
            Defaults to current directory.
    """
    # Get the example directory path
    root_path = Path(root_path)

    # Find the example directory
    pkg_dir = Path(__file__).absolute().parent
    while pkg_dir.exists() and not (pkg_dir / "example").is_dir():
        pkg_dir = pkg_dir.parent

    if not pkg_dir.exists():
        raise ValueError(f"Example directory not found in path of {pkg_dir}")

    example_dir = pkg_dir / "example"

    # Create root directory if it doesn't exist
    shutil.copytree(example_dir, root_path, dirs_exist_ok=True)


class CustomHandler(SimpleHTTPRequestHandler):
    """
    Custom HTTP request handler for serving the static site during development.
    Extends SimpleHTTPRequestHandler to serve files from the site directory
    and properly handle .html extensions for clean URLs.
    """
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


def serve(port: int = 8000):
    """
    Start a local development server to preview the generated site.

    Args:
        port: The port number to run the server on. Defaults to 8000.
    """
    site_dir = Path.cwd() / "site"
    handler = partial(CustomHandler, directory=str(site_dir))
    server = HTTPServer(("0.0.0.0", port), handler)

    print(f"Serving {site_dir} on http://0.0.0.0:{port}")
    server.serve_forever()
