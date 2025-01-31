from pathlib import Path
from urllib.parse import urlparse

import frontmatter
import mistune
import yaml
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


def render(
    staging_dir: Path | str = Path("build/staging"),
    site_dir: Path | str = Path("build/site"),
    template_dir: Path | str = Path("templates"),
) -> None:
    """
    Render staged markdown files using liquid templates.

    Args:
        staging_dir: Directory containing staged markdown files. Defaults to "build/staging"
        site_dir: Directory to output rendered files. Defaults to "build/site"
        template_dir: Directory containing liquid templates. Defaults to "templates"
        default_template: Default liquid template to use for each page. Defaults to "layout.liquid"

    Raises:
        FileNotFoundError: If template directory doesn't exist
        OSError: If there are issues creating directories or writing files
    """
    # Convert string paths to Path objects
    staging_dir = Path(staging_dir)
    site_dir = Path(site_dir)
    template_dir = Path(template_dir)

    # Ensure required directories exist
    staging_dir.mkdir(parents=True, exist_ok=True)
    site_dir.mkdir(parents=True, exist_ok=True)
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory {template_dir} does not exist")

    # Initialize Liquid environment
    env = Environment(loader=FileSystemLoader(str(template_dir)))

    # Walk through staged files
    for source_file in staging_dir.rglob("*.md"):
        # Calculate relative path and create target HTML file path
        rel_path = source_file.relative_to(staging_dir)
        target_file = site_dir / rel_path.with_suffix(".html")

        # Create parent directories if they don't exist
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # Read markdown content and parse frontmatter
        with open(source_file, "r", encoding="utf-8") as f:
            page = frontmatter.load(f)

        # Convert markdown to HTML
        format_markdown = mistune.create_markdown(
            escape=False,
            plugins=["strikethrough", "footnotes", "table", "speedup"],
            renderer=LinkRenderer(staging_dir),
        )
        html_content = format_markdown(page.content)

        # Load site metadata
        site_yaml = staging_dir / "site.yaml"
        site_metadata = {}
        if site_yaml.exists():
            with open(site_yaml, "r") as f:
                site_metadata = yaml.safe_load(f)

        # Get template name from frontmatter or use default
        if page_template := page.metadata.get("template"):
            default_template = str(page_template)
        elif default_template := site_metadata.get("default_template"):
            default_template = str(default_template)
        else:
            raise ValueError("No default template specified")

        # Ensure the template ends with ".liquid"
        if not default_template.endswith(".liquid"):
            default_template += ".liquid"

        # Render template with content and frontmatter variables
        page_template = env.get_template(default_template)
        rendered = page_template.render(
            content=html_content,
            site=site_metadata,
            page=page.metadata,
        )

        # Write rendered content to file
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(rendered)
