import os
from pathlib import Path

import frontmatter


def index(
    staging_dir: Path | str = Path("build/staging"),
) -> None:
    """
    Add index links to the end of index.md files in the staging directory.
    Each entry will contain title and url information for the pages in that directory.

    Args:
        staging_dir: Path to the staging directory containing the markdown files
    """
    # Convert string paths to Path objects
    staging_dir = Path(staging_dir)

    for root, _, files in os.walk(staging_dir):
        # Skip if there's no index.md in this directory
        if "index.md" not in files:
            continue

        index_path = os.path.join(root, "index.md")
        index_links = []

        # Get all markdown files in the current directory except index.md
        md_files = [f for f in files if f.endswith(".md") and f != "index.md"]

        # Get subdirectories in the current directory that contain index.md
        subdirs = []
        for name in os.listdir(root):
            subdir_path = os.path.join(root, name)
            if os.path.isdir(subdir_path):
                if "index.md" in os.listdir(subdir_path):
                    # Calculate relative URL from staging directory
                    rel_path = os.path.relpath(subdir_path, staging_dir)
                    # Get the title from the index.md frontmatter
                    with open(
                        os.path.join(subdir_path, "index.md"), "r", encoding="utf-8"
                    ) as f:
                        index_post = frontmatter.load(f)
                    # Get the child folder name
                    title = index_post.get("title", os.path.basename(subdir_path))
                    subdirs.append(f"- [{title}]({rel_path})")

        for md_file in md_files:
            file_path = os.path.join(root, md_file)

            # Read the markdown file's frontmatter
            with open(file_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)

            # Get the title from frontmatter, fallback to filename without extension
            title = post.get("title", os.path.splitext(md_file)[0])

            # Calculate relative URL from staging directory
            rel_path = os.path.relpath(file_path, staging_dir)
            url = os.path.splitext(rel_path)[0]  # Remove .md extension

            # Create markdown link
            index_links.append(f"- [{title}]({url})")

        # Read the index.md file
        with open(index_path, "r", encoding="utf-8") as f:
            index_post = frontmatter.load(f)

        # Add index links to the end of the content if there are any
        if index_links or subdirs:
            content = index_post.content.rstrip()  # Remove trailing whitespace
            content += "\n\n## Index\n"
            if subdirs:
                content += "### Directories\n" + "\n".join(subdirs) + "\n"
            if index_links:
                content += "\n### Files\n" + "\n".join(index_links) + "\n"
            index_post.content = content

        # Write back to the file
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(index_post))
