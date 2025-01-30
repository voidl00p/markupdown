import os
import shutil
from pathlib import Path

def init(root_dir: str = ".") -> None:
    """
    Initialize a new markupdown project by copying the example directory structure.
    
    Args:
        root_dir: The target directory where the example should be copied. Defaults
                to current directory.
    """
    # Get the example directory path
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    example_dir = os.path.join(os.path.dirname(os.path.dirname(pkg_dir)), 'example')
    
    # Create root directory if it doesn't exist
    root_path = Path(root_dir)
    root_path.mkdir(parents=True, exist_ok=True)
    
    # Copy example directory contents to root directory
    for item in os.listdir(example_dir):
        src = os.path.join(example_dir, item)
        dst = os.path.join(root_dir, item)
        
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)