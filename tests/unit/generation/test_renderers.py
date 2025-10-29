"""Unit tests for generation/renderers.py"""

import pytest

from boumwave.generation.renderers import render_markdown


class TestRenderMarkdown:
    """Tests for render_markdown"""

    def test_render_simple_markdown(self):
        """Test rendering simple markdown"""
        markdown_text = "# Hello World\n\nThis is a paragraph."
        html = render_markdown(markdown_text)

        assert "<h1>Hello World</h1>" in html
        assert "<p>This is a paragraph.</p>" in html

    def test_render_bold_text(self):
        """Test rendering bold text"""
        markdown_text = "This is **bold** text."
        html = render_markdown(markdown_text)

        assert "<strong>bold</strong>" in html

    def test_render_italic_text(self):
        """Test rendering italic text"""
        markdown_text = "This is *italic* text."
        html = render_markdown(markdown_text)

        assert "<em>italic</em>" in html

    def test_render_links(self):
        """Test rendering links"""
        markdown_text = "[Link text](https://example.com)"
        html = render_markdown(markdown_text)

        assert '<a href="https://example.com">Link text</a>' in html

    def test_render_lists(self):
        """Test rendering lists"""
        markdown_text = "- Item 1\n- Item 2\n- Item 3"
        html = render_markdown(markdown_text)

        assert "<ul>" in html
        assert "<li>Item 1</li>" in html
        assert "<li>Item 2</li>" in html
        assert "<li>Item 3</li>" in html

    def test_render_code_blocks(self):
        """Test rendering code blocks"""
        markdown_text = "```python\nprint('hello')\n```"
        html = render_markdown(markdown_text)

        assert "<code>" in html
        assert "print('hello')" in html

    def test_render_empty_string(self):
        """Test rendering empty string"""
        html = render_markdown("")
        assert html == ""

    def test_render_multiple_paragraphs(self):
        """Test rendering multiple paragraphs"""
        markdown_text = "First paragraph.\n\nSecond paragraph."
        html = render_markdown(markdown_text)

        assert html.count("<p>") == 2
        assert "First paragraph." in html
        assert "Second paragraph." in html
