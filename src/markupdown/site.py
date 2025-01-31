import yaml
from pathlib import Path
from typing import Optional


def site(
    title: str = "markupdown Example Site",
    default_template: str = "layout.liquid",
    staging_dir: Path | str = Path("build/staging"),
    **kwargs,
) -> None:
    """
    Write site configuration to site.yaml in the staging directory.

    Args:
        title: Site title
        default_template: Default template to use for pages
        staging_dir: Directory to write site.yaml. Defaults to "build/staging"

    Raises:
        OSError: If there are issues creating directories or writing the file
    """
    staging_dir = Path(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    site_config = kwargs
    site_config |= {
        "title": title,
        "default_template": default_template,
    }

    with open(staging_dir / "site.yaml", "w") as f:
        yaml.safe_dump(site_config, f, default_flow_style=False)