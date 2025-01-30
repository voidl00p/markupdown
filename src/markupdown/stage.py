from pathlib import Path
import shutil
from typing import Optional, Pattern
import re


def stage(
    source_dir: Path | str = Path("pages"),
    staging_dir: Path | str = Path("build/staging"),
    pattern: Pattern[str] | str = r".*\.md$"
) -> None:
    """
    Copy files matching a pattern from source directory to staging directory.
    
    Args:
        source_dir: Directory containing source files. Defaults to "pages"
        staging_dir: Directory to stage files. Defaults to "build/staging"
        pattern: Pattern to match files. Can be a string or compiled regex pattern.
                Defaults to ".*\.md$"
    
    Raises:
        FileNotFoundError: If source directory doesn't exist
        OSError: If there are issues creating directories or copying files
    """
    # Convert string paths to Path objects
    source_dir = Path(source_dir)
    staging_dir = Path(staging_dir)
    
    # Convert string pattern to compiled regex
    if isinstance(pattern, str):
        pattern = re.compile(pattern)
    
    # Ensure source directory exists
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory {source_dir} does not exist")
    
    # Create staging directory if it doesn't exist
    staging_dir.mkdir(parents=True, exist_ok=True)
    
    # Walk through source directory
    for source_file in source_dir.rglob("*"):
        if source_file.is_file() and pattern.match(str(source_file)):
            # Calculate relative path to maintain directory structure
            rel_path = source_file.relative_to(source_dir)
            target_file = staging_dir / rel_path
            
            # Create parent directories if they don't exist
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            shutil.copy2(source_file, target_file)
