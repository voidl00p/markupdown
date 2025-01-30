import os
import frontmatter
from pathlib import Path

def index(
    staging_dir: Path | str = Path("build/staging"),
) -> None:
    """
    Add index frontmatter to index.md files in the staging directory.
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
        entries = []

        # Get all markdown files in the current directory except index.md
        md_files = [f for f in files if f.endswith(".md") and f != "index.md"]
        
        for md_file in md_files:
            file_path = os.path.join(root, md_file)
            
            # Read the markdown file's frontmatter
            with open(file_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
            
            # Get the title from frontmatter, fallback to filename without extension
            title = post.get("title", os.path.splitext(md_file)[0])
            
            # Calculate relative URL from staging directory
            rel_path = os.path.relpath(file_path, staging_dir)
            url = "/" + os.path.splitext(rel_path)[0]  # Remove .md extension
            
            entries.append({
                "title": title,
                "path": url
            })

        # Update the index.md file with the new entries
        with open(index_path, "r", encoding="utf-8") as f:
            index_post = frontmatter.load(f)
        
        # Add or update the index field
        index_post["template"] = "index"
        index_post["index"] = entries
        
        # Write back to the file
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(index_post))