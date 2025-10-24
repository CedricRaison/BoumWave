"""Markdown to HTML conversion"""

import markdown


def render_markdown(markdown_content: str) -> str:
    """
    Convert markdown content to HTML.

    Args:
        markdown_content: Raw markdown text

    Returns:
        Rendered HTML content
    """
    return markdown.markdown(markdown_content)
