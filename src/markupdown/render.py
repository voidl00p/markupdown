from pathlib import Path

import frontmatter
import mistune
from liquid import Environment, FileSystemLoader


def render(
    staging_dir: Path | str = Path("build/staging"),
    site_dir: Path | str = Path("build/site"),
    template_dir: Path | str = Path("templates"),
    default_layout: str = "layout.liquid",
) -> None:
    """
    Render staged markdown files using liquid templates.

    Args:
        staging_dir: Directory containing staged markdown files. Defaults to "build/staging"
        site_dir: Directory to output rendered files. Defaults to "build/site"
        template_dir: Directory containing liquid templates. Defaults to "templates"
        default_layout: Default liquid template to use. Defaults to "layout.liquid"

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
        html_content = mistune.html(page.content)

        # Get template name from frontmatter or use default
        layout_template = str(page.metadata.get("layout", default_layout))

        # Ensure the template ends with ".liquid"
        if not layout_template.endswith(".liquid"):
            layout_template += ".liquid"

        # Render template with content and frontmatter variables
        layout_template = env.get_template(layout_template)
        rendered = layout_template.render(content=html_content, **page.metadata)

        # Write rendered content to file
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(rendered)
