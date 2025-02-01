import os
from pathlib import Path

import frontmatter

from .site import Site
from .utils import get_relative_path


def _handle_file(file_path: Path, staging_dir: Path) -> dict:
    """
    Process a single markdown file and return its index entry.

    Args:
        file_path: Path to the markdown file
        staging_dir: Path to the staging directory

    Returns:
        dict: Index entry containing title and url
    """
    # Read the markdown file's frontmatter
    with open(file_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)

    # Get the title from frontmatter, fallback to filename without extension
    title = post.get("title", file_path.stem)

    # Calculate relative URL from staging directory
    path = get_relative_path(file_path, staging_dir)

    return {"title": title, "path": path}


def _handle_directory(dir_path: Path, staging_dir: Path) -> dict | None:
    """
    Process a directory containing index.md and return its index entry.

    Args:
        dir_path: Path to the directory
        staging_dir: Path to the staging directory

    Returns:
        dict | None: Index entry containing title and url if index.md exists, None otherwise
    """
    index_path = dir_path / "index.md"
    if not index_path.exists():
        return None

    # Calculate relative URL from staging directory
    rel_path = get_relative_path(dir_path, staging_dir)

    # Get the title from the index.md frontmatter
    with open(index_path, "r", encoding="utf-8") as f:
        index_post = frontmatter.load(f)

    # Get the child folder name
    title = index_post.get("title", dir_path.name)
    return {"title": title, "path": rel_path}


def index(site: Site) -> Site:
    """
    Add index links to the end of index.md files in the staging directory.
    Each entry will contain title and url information for the pages in that directory.

    Args:
        site: Site object containing the site directory
    """
    list()
    for root, _, files in os.walk(site.site_dir):
        root_path = Path(root)

        # Skip if there's no index.md in this directory
        if "index.md" not in files:
            continue

        index_path = root_path / "index.md"
        index_links = []

        # Get all markdown files in the current directory except index.md
        md_files = [f for f in files if f.endswith(".md") and f != "index.md"]

        # Process subdirectories that contain index.md
        for name in os.listdir(root):
            subdir_path = root_path / name
            if subdir_path.is_dir():
                if dir_entry := _handle_directory(subdir_path, site.site_dir):
                    index_links.append(dir_entry)

        # Process markdown files
        for md_file in md_files:
            file_entry = _handle_file(root_path / md_file, site.site_dir)
            index_links.append(file_entry)

        # Read the index.md file
        with open(index_path, "r", encoding="utf-8") as f:
            index_post = frontmatter.load(f)

        # Add index links to the frontmatter if there are any
        if index_links:
            index_post["children"] = index_links

        # Write back to the file
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(index_post))

    return site
