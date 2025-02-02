from pathlib import Path
from urllib.parse import urlparse

import frontmatter
import mistune
from liquid import Environment, FileSystemLoader


class LinkRenderer(mistune.HTMLRenderer):
    def __init__(self, staging_dir: Path | str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.staging_dir = Path(staging_dir)

    def link(self, text, url, title=None):
        """
        If the URL is relative, append ".html" to it.
        """

        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = url.strip(".md")
            url = url.strip("/")
            if not (self.staging_dir / url).is_dir():
                url += ".html"
            url = "/" + url
        return super().link(text, url, title)


def render(site: Site) -> None:
    """
    Render staged markdown files using liquid templates.

    Args:
        site: Site object containing the site directory

    Raises:
        FileNotFoundError: If template directory doesn't exist
        OSError: If there are issues creating directories or writing files
    """

    # Initialize Liquid environment
    env = Environment(loader=FileSystemLoader(site.template_dir))

    # Walk through staged files
    for source_file in site.site_dir.rglob("*.md"):
        # Calculate relative path and create target HTML file path
        rel_path = source_file.relative_to(site.site_dir)
        target_file = site.site_dir / rel_path.with_suffix(".html")

        # Create parent directories if they don't exist
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # Read markdown content and parse frontmatter
        with open(source_file, "r", encoding="utf-8") as f:
            page = frontmatter.load(f)

        # Convert markdown to HTML
        format_markdown = mistune.create_markdown(
            escape=False,
            plugins=["strikethrough", "footnotes", "table", "speedup"],
            renderer=LinkRenderer(site.site_dir),
        )
        html_content = format_markdown(page.content)

        # Get template name from frontmatter or use default
        if page_template := page.metadata.get("template"):
            page_template = str(page_template)
        elif page_template := site.default_template:
            page_template = str(page_template)
        else:
            raise ValueError(
                f"No template specified in site.yaml or frontmatter for: {source_file}"
            )

        # Ensure the template ends with ".liquid"
        if not page_template.endswith(".liquid"):
            page_template += ".liquid"

        # Render template with content and frontmatter variables
        page_template = env.get_template(page_template)
        rendered = page_template.render(
            content=html_content,
            site=site.template_vars,
            page=page.metadata,
        )

        # Write rendered content to file
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(rendered)
