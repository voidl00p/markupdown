import os
import shutil
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


def copy_files(
    src_dir: Path,
    dest_dir: Path,
    patterns: str | list[str],
    include_src_dir: bool = False,
    recursive: bool = True,
    err_on_missing: bool = False,
) -> None:
    """
    Copies files from src_dir to dest_dir matching the given glob pattern(s).

    :param src_dir: The source directory from which to copy files.
    :param dest_dir: The destination directory to which to copy files.
    :param patterns: A glob pattern (or list of patterns) to match files.
    :param include_src_dir: If True, the source directory’s name will be included
                            in the destination path. For example, if copying from 'css'
                            and include_src_dir is True, a file found at
                            'css/style.css' will be copied to 'site/css/style.css'.
                            For pages this should be False.
    :param recursive: If True, search the src_dir recursively.
    """
    if not src_dir.exists():
        if err_on_missing:
            raise FileNotFoundError(f"No {src_dir} directory found")
        else:
            return

    # Ensure patterns is a list.
    if isinstance(patterns, str):
        patterns = [patterns]

    # When including the source directory in the destination,
    # set the base to the parent of src_dir; otherwise, use src_dir itself.
    base_dir = src_dir.parent if include_src_dir else src_dir

    for pattern in patterns:
        # Use rglob if recursive is True, else glob.
        files = src_dir.rglob(pattern) if recursive else src_dir.glob(pattern)
        for file in files:
            # Compute the relative path with respect to the chosen base.
            rel_path = file.relative_to(base_dir)
            dest_file = dest_dir / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, dest_file)
