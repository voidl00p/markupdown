from pathlib import Path
from typing import Any


class MarkdownTransformer:
    """
    A class to transform Markdown files.
    """

    def transform(self, path: Path, text: str, ast: list[dict[str, Any]]) -> str:
        """
        Transform the text of a Markdown file. Defaults to a no-op.

        Args:
            path: The path to the Markdown file.
            text: The text of the Markdown file (excluding frontmatter).
            ast: The abstract syntax tree of the Markdown file (excluding frontmatter).

        Returns:
            The transformed text of the Markdown file.
        """
        return text
