from __future__ import annotations

import frontmatter
from pathlib import Path
import jsonpath_ng
import shutil
from typing import Callable
import yaml
import mistune


PAGE_TITLE_AST_PATH = "$[?(@.type=='heading' && @.attrs.level==1)][0].children[0].raw"
AST_RENDERER = mistune.create_markdown(renderer=None)


class MarkdownFile:
    root: Path
    path: Path
    _post: frontmatter.Post
    _site: dict[str, object]

    def __init__(self, root: Path, path: Path) -> None:
        self.root = root
        self.path = path

    def _load(self) -> None:
        if not self._post:
            with open(self.root / self.path, "r", encoding="utf-8") as f:
                self._post = frontmatter.load(f)
        if not self._site:
            self._site = yaml.safe_load((self.root / "site.yaml").read_text(encoding="utf-8"))

    def frontmatter(self) -> dict[str, object]:
        self._load()
        return self._post.metadata

    def site(self) -> dict[str, object]:
        self._load()
        return self._site

    def content(self) -> str:
        self._load()
        return self._post.content

    def ast(self) -> dict[str, object]:
        ast = AST_RENDERER(self.content())
        assert isinstance(ast, dict)
        return ast

    def set_content(self, content: str) -> None:
        self._load()
        self._post.content = content

    def set_metadata(self, metadata: dict[str, object]) -> None:
        self._load()
        self._post.metadata = metadata

    def update_metadata(self, metadata: dict[str, object]) -> None:
        self._load()
        self._post.metadata.update(metadata)

    def set_site(self, site: dict[str, object]) -> None:
        self._load()
        self._site = site

    def save(self) -> None:
        self._load()
        (self.root / self.path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.root / self.path, "w", encoding="utf-8") as f:
            frontmatter.dump(self._post, f)
        with open(self.root / "site.yaml", "w", encoding="utf-8") as f:
            yaml.dump(self._site, f)

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
) -> None:
    root, paths = ls(glob_pattern)
    dest_dir = Path(dest_dir)

    for src_file in paths:
        dest_file = src_file.relative_to(root)
        dest_file = dest_dir / dest_file
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)


def transform(glob_pattern: str, func: Callable[[MarkdownFile], None]) -> None:
    root, paths = ls(glob_pattern)

    for path in paths:
        if path.is_file():
            func(MarkdownFile(root, path))


def ls(glob_pattern: str, root: Path | None = None) -> tuple[Path, list[Path]]:
    root = root or Path.cwd()

    # list() to snap shot the directory contents so we don't go into a recursive loop.
    # not memory efficient, but it fixes the issue.
    return root, list(root.rglob(glob_pattern))


def title(glob_pattern: str, ast_pattern: str | None = None) -> None:
    """
    Update the site.yaml title field based on the first markdown file matching the
    given glob pattern.

    Args:
        glob_pattern: The glob pattern of the markdown files to update.
        ast_pattern: The jsonpath expression to select the title.
            Defaults to the first # h1.
    """
    jsonpath = jsonpath_ng.parse(ast_pattern or PAGE_TITLE_AST_PATH)

    def _title(f: MarkdownFile) -> None:
        title = jsonpath.find(f.ast())
        if title:
            f.update_metadata({"title": title[0]})

    transform(glob_pattern, _title)
