from __future__ import annotations

from pathlib import Path

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
