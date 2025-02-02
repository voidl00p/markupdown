from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable

import frontmatter
import jmespath
import mistune
import yaml

PAGE_TITLE_AST_PATH = "([?type=='heading' && attrs.level==`1`])[0].children[0].raw"
AST_RENDERER = mistune.create_markdown(renderer=None)


class SiteFile:
    root: Path
    _site: dict[str, object]

    def __init__(self, root: Path) -> None:
        self.root = root
        self._site = {}

        site_path = self.root / "site.yaml"
        site_path.parent.mkdir(parents=True, exist_ok=True)

        if site_path.is_file():
            self._site = yaml.safe_load(site_path.read_text(encoding="utf-8"))

    def metadata(self) -> dict[str, object]:
        return self._site

    def set_metadata(self, metadata: dict[str, object]) -> None:
        self._site = metadata

    def update_metadata(self, metadata: dict[str, object]) -> None:
        self._site.update(metadata)

    def save(self) -> None:
        (self.root / "site.yaml").parent.mkdir(parents=True, exist_ok=True)
        with open(self.root / "site.yaml", "w", encoding="utf-8") as f:
            yaml.dump(self._site, f)


class MarkdownFile:
    root: Path
    path: Path
    _post: frontmatter.Post
    _ast: list[dict[str, object]]

    def __init__(self, root: Path, path: Path) -> None:
        self.root = root
        self.path = path

        # Load frontmatter and content
        with open(self.root / self.path, "r", encoding="utf-8") as f:
            self._post = frontmatter.load(f)

        # Load markdown AST
        ast = AST_RENDERER(self.content())
        assert isinstance(ast, list)
        self._ast = ast

    def frontmatter(self) -> dict[str, object]:
        return self._post.metadata

    def content(self) -> str:
        return self._post.content

    def ast(self) -> list[dict[str, object]]:
        return self._ast

    def set_content(self, content: str) -> None:
        self._post.content = content

    def update_frontmatter(self, metadata: dict[str, object]) -> None:
        self._post.metadata.update(metadata)

    def del_frontmatter_key(self, key: str) -> None:
        self._post.metadata.pop(key)

    def default_title(self, ast_pattern: str | None = None) -> str:
        ast_pattern = ast_pattern or PAGE_TITLE_AST_PATH
        if title := jmespath.search(ast_pattern, self.ast()):
            return title
        return self.path.stem.replace("-", " ").capitalize()

    def link(self) -> str:
        link = self.path.with_suffix("")
        if link.name == "index":
            link = link.parent

        return str(link)

    def save(self) -> None:
        (self.root / self.path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.root / self.path, "wb") as f:
            frontmatter.dump(self._post, f)

    @classmethod
    def create(cls, source: Path, root: Path, path: Path) -> MarkdownFile:
        # Parse frontmatter and content from the source file
        with open(source, "r", encoding="utf-8") as f:
            metadata, content = frontmatter.parse(f.read())

        # Inject source if it's not already set
        metadata["source"] = metadata.get("source", str(source.absolute()))

        # Create parent directories
        (root / path).parent.mkdir(parents=True, exist_ok=True)

        # Write the file
        with open(root / path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(frontmatter.Post(content, metadata=metadata)))

        return cls(root, path)


def cp(
    glob_pattern: str,
    dest_dir: Path | str = "site",
    relative_to: Path | str = ".",
) -> None:
    root, paths = ls(glob_pattern)
    dest_dir = Path(dest_dir)
    relative_to = Path(relative_to)

    for src_file in paths:
        dest_file = src_file.relative_to(root).relative_to(relative_to)
        dest_file = dest_dir / dest_file
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)


def transform(
    glob_pattern: str, func: Callable[[MarkdownFile, SiteFile], None]
) -> None:
    root, paths = ls(glob_pattern)
    site_root = root / "site"

    for path in paths:
        if path.is_file():
            path = path.relative_to(site_root)
            func(MarkdownFile(site_root, path), SiteFile(site_root))


def ls(glob_pattern: str, root: Path | None = None) -> tuple[Path, list[Path]]:
    root = root or Path.cwd()

    # list() to snap shot the directory contents so we don't go into a recursive loop.
    # not memory efficient, but it fixes the issue.
    return root, list(root.glob(glob_pattern))


def title(glob_pattern: str, ast_pattern: str | None = None) -> None:
    """
    Sets titles for markdown files that don't have a `title` field in their frontmatter.
    Uses the first # h1 as the title if ast_pattern is not provided. If no # h1 is found,
    the filename is used with the following rules:

    - Replace .md with empty string
    - Replace - with spaces
    - Capitalize

    Args:
        glob_pattern: The glob pattern of the markdown files to update.
        ast_pattern: The jsonpath expression to select the title.
            Defaults to the first # h1.
    """
    ast_pattern = ast_pattern or PAGE_TITLE_AST_PATH

    def _title(md_file: MarkdownFile, _: SiteFile) -> None:
        if not md_file.frontmatter().get("title"):
            title = md_file.default_title(ast_pattern)
            md_file.update_frontmatter({"title": title})
            md_file.save()

    transform(glob_pattern, _title)


def nav(glob_pattern: str) -> None:
    """
    Update site.yaml in the staging directory with a "nav" field containing a list of
    title/path entries based on the following criteria:
    - Pages with nav: true in frontmatter
    - First-level index.md files without nav: false in frontmatter
    - Root-level non-index.md files without nav: false in frontmatter

    Args:
        glob_pattern: The glob pattern of the markdown files to update.
    """

    def _nav(md_file: MarkdownFile, site_file: SiteFile) -> None:
        frontmatter = md_file.frontmatter()
        nav_entries = site_file.metadata().get("nav", [])
        assert isinstance(nav_entries, list)

        # Skip if nav is explicitly set to false
        if frontmatter.get("nav") is False:
            return

        # Calculate relative path parts from site directory
        file_name = md_file.path.name

        # Include if any of these conditions are met:
        # 1. nav is explicitly set to true
        # 2. file is index.md in first level of children
        # 3. file is in root and not index.md
        if (
            frontmatter.get("nav") is True
            or (file_name == "index.md" and len(md_file.path.parts) == 2)
            or (len(md_file.path.parts) == 1 and file_name != "index.md")
        ):
            # Get the title from frontmatter, fallback to filename without extension
            title = frontmatter.get("title", md_file.default_title())

            # Create new nav entry
            new_entry = {"title": title, "path": md_file.link()}

            # Remove any existing entries with the same title
            nav_entries = [entry for entry in nav_entries if entry["title"] != title]

            # Add nav entry
            nav_entries.append(new_entry)

            # Sort nav entries by title
            nav_entries.sort(key=lambda x: x["title"])

            # Update site file with new nav entries
            site_file.update_metadata({"nav": nav_entries})
            site_file.save()

    transform(glob_pattern, _nav)


def index(glob_pattern: str) -> None:
    """
    Add child page links to the frontmatter of index.md files.
    Each entry will contain title and link for the pages in that directory.
    Don't include the root index.md file.

    For each index.md file:
    - Find all sibling .md files (excluding index.md itself)
    - Find all subdirectories containing an index.md file
    - Add these as children in the frontmatter

    Args:
        glob_pattern: The glob pattern of the markdown files to update.
    """

    def _index(index_file: MarkdownFile, _: SiteFile) -> None:
        # Only process index.md files
        if index_file.path.name != "index.md":
            return

        # Get the directory containing this index.md
        dir_path = index_file.path.parent
        root = index_file.root

        children = []

        # Process sibling markdown files (excluding index.md)
        for sibling in (root / dir_path).glob("*.md"):
            if sibling.name == "index.md":
                continue
            sibling_md = MarkdownFile(root, dir_path / sibling.name)
            children.append({
                "title": sibling_md.frontmatter().get("title", sibling_md.default_title()),
                "path": sibling_md.link()
            })

        # Sort children by title
        children.sort(key=lambda x: x["title"])

        # Update frontmatter with children
        if children:
            index_file.update_frontmatter({"children": children})
            index_file.save()

    transform(glob_pattern, _index)
