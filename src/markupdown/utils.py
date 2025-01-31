import os
from pathlib import Path


def get_relative_path(path: Path, staging_dir: Path) -> str:
    """
    Generate a relative web path from a file or directory path relative to the staging directory.
    
    Args:
        path: Path to the file or directory
        staging_dir: Path to the staging directory
    
    Returns:
        str: Web-friendly relative path starting with '/' and without file extension
    """
    rel_path = path.relative_to(staging_dir)
    rel_path = rel_path.with_suffix("")
    if rel_path.name == "index":
        rel_path = rel_path.parent
    return "/" + str(rel_path).replace(os.sep, "/")
