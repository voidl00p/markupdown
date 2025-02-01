import os
from pathlib import Path

import frontmatter
import yaml

from .site import Site
from .utils import get_relative_path


def nav(site: Site) -> Site:
    """
    Update site.yaml in the staging directory with a "nav" field containing a list of
    title/path entries based on the following criteria:
    - Pages with nav: true in frontmatter
    - First-level index.md files without nav: false in frontmatter
    - Root-level non-index.md files without nav: false in frontmatter

    Args:
        site: Site object containing the site directory
    """
    # Initialize nav entries list
    nav_entries = []

    # Process all markdown files in staging directory
    for root, _, files in os.walk(site.site_dir):
        root_path = Path(root)
        rel_path = root_path.relative_to(site.site_dir)

        for file in files:
            if not file.endswith(".md"):
                continue

            file_path = root_path / file
            with open(file_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)

            # Skip if nav is explicitly set to false
            if post.get("nav") is False:
                continue

            # Calculate relative URL from staging directory
            path = get_relative_path(file_path, site.site_dir)

            # Get the title from frontmatter, fallback to filename without extension
            title = post.get("title", file_path.stem)

            # Include if any of these conditions are met:
            # 1. nav is explicitly set to true
            # 2. file is index.md in first level of children
            # 3. file is in root and not index.md
            if (
                post.get("nav") is True
                or (file == "index.md" and len(rel_path.parts) == 1)
                or (len(rel_path.parts) == 0 and file != "index.md")
            ):
                nav_entries.append({"title": title, "path": path})

    # Sort nav entries by title
    nav_entries.sort(key=lambda x: x["title"])

    site.template_vars["nav"] = nav_entries

    return site
