import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .utils import copy_files


@dataclass
class Site:
    title: str = "markupdown Example Site"
    markdown_dir: Path = Path("pages")
    template_dir: Path = Path("templates")
    css_dir: Path = Path("css")
    img_dir: Path = Path("img")
    js_dir: Path = Path("js")
    site_dir: Path = Path("site")
    default_template: str = "layout.liquid"
    template_vars: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.site_dir.mkdir(parents=True, exist_ok=True)

        # Copy CSS files (include the 'css' folder in the destination)
        copy_files(
            src_dir=self.css_dir,
            dest_dir=self.site_dir,
            patterns="*.css",
        )

        # Copy image files (include the 'img' folder in the destination)
        copy_files(
            src_dir=self.img_dir,
            dest_dir=self.site_dir,
            patterns=["*.png", "*.jpg", "*.jpeg"],
        )

        # Copy JavaScript files (include the 'js' folder in the destination)
        copy_files(
            src_dir=self.js_dir,
            dest_dir=self.site_dir,
            patterns="*.js",
        )

        # Copy markdown files (do NOT include the 'pages' folder in the destination)
        copy_files(
            src_dir=self.markdown_dir,
            dest_dir=self.site_dir,
            patterns="*.md",
            include_src_dir=False,
            err_on_missing=True,
        )
