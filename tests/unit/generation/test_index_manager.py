"""Unit tests for generation/index_manager.py"""

from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from boumwave.exceptions import FileCreationError
from boumwave.generation.index_manager import render_post_links, update_index
from boumwave.models import Post


class TestRenderPostLinks:
    """Tests for render_post_links"""

    def test_render_post_links_empty_list(self, tmp_path: Path, sample_config, monkeypatch):
        """Test rendering with empty post list"""
        monkeypatch.chdir(tmp_path)
        # Create link template
        template_folder = tmp_path / "templates"
        template_folder.mkdir()
        (template_folder / "link.html").write_text(
            '<li><a href="{{ relative_url }}">{{ title }}</a></li>'
        )

        with patch("boumwave.generation.index_manager.get_config", return_value=sample_config):
            result = render_post_links([])
            assert result == ""

    def test_render_post_links_single_post(
        self, tmp_path: Path, sample_config, sample_post: Post, monkeypatch
    ):
        """Test rendering a single post link"""
        monkeypatch.chdir(tmp_path)
        # Create link template
        template_folder = tmp_path / "templates"
        template_folder.mkdir()
        (template_folder / "link.html").write_text(
            '<li><a href="{{ relative_url }}">{{ title }}</a></li>'
        )

        with patch("boumwave.generation.index_manager.get_config", return_value=sample_config):
            result = render_post_links([sample_post])

            assert sample_post.title in result
            assert sample_post.get_relative_url(sample_config) in result

    def test_render_post_links_sorted_by_date(
        self, tmp_path: Path, sample_config, monkeypatch
    ):
        """Test that posts are sorted by date (most recent first)"""
        monkeypatch.chdir(tmp_path)
        # Create posts with different dates
        old_post = Post(
            title="Old Post",
            slug="old-post",
            published_date=date(2025, 1, 1),
            lang="en",
        )
        new_post = Post(
            title="New Post",
            slug="new-post",
            published_date=date(2025, 12, 31),
            lang="en",
        )
        middle_post = Post(
            title="Middle Post",
            slug="middle-post",
            published_date=date(2025, 6, 15),
            lang="en",
        )

        # Create link template
        template_folder = tmp_path / "templates"
        template_folder.mkdir()
        (template_folder / "link.html").write_text('{{ title }}\n')

        with patch("boumwave.generation.index_manager.get_config", return_value=sample_config):
            # Pass in random order
            result = render_post_links([old_post, new_post, middle_post])

            # Should be sorted: new_post, middle_post, old_post
            new_pos = result.find("New Post")
            middle_pos = result.find("Middle Post")
            old_pos = result.find("Old Post")

            assert new_pos < middle_pos < old_pos

    def test_render_post_links_template_not_found(
        self, tmp_path: Path, sample_config, sample_post: Post, monkeypatch
    ):
        """Test error when link template doesn't exist"""
        monkeypatch.chdir(tmp_path)
        # Don't create template folder

        with patch("boumwave.generation.index_manager.get_config", return_value=sample_config):
            from boumwave.exceptions import TemplateNotFoundError

            with pytest.raises(TemplateNotFoundError):
                render_post_links([sample_post])


class TestUpdateIndex:
    """Tests for update_index"""

    def test_update_index_with_posts(self, tmp_path: Path, sample_config, monkeypatch):
        """Test updating index.html with posts"""
        monkeypatch.chdir(tmp_path)

        # Create index.html
        (tmp_path / "index.html").write_text(
            """<!DOCTYPE html>
<html>
<head><title>Blog</title></head>
<body>
<h1>My Blog</h1>
<ul>
<!-- POSTS_START -->
<!-- POSTS_END -->
</ul>
</body>
</html>
"""
        )

        # Create templates
        template_folder = tmp_path / "templates"
        template_folder.mkdir()
        (template_folder / "link.html").write_text(
            '<li><a href="{{ relative_url }}">{{ title }}</a></li>'
        )

        # Create a post
        content_folder = tmp_path / "content"
        content_folder.mkdir()
        post_folder = content_folder / "test_post"
        post_folder.mkdir()
        (post_folder / "test.en.md").write_text(
            """---
title: "Test Post"
slug: "test-post"
published_date: 2025-10-20
lang: en
---

Content
"""
        )

        # Mock both get_config locations
        with patch("boumwave.generation.index_manager.get_config", return_value=sample_config), \
             patch("boumwave.generation.parsers.get_config", return_value=sample_config):
            update_index()

            # Read updated index
            updated_content = (tmp_path / "index.html").read_text()

            assert "Test Post" in updated_content
            assert "/posts/en/test-post" in updated_content

    def test_update_index_no_posts(self, tmp_path: Path, sample_config, monkeypatch):
        """Test updating index.html when no posts exist"""
        monkeypatch.chdir(tmp_path)

        # Create index.html
        (tmp_path / "index.html").write_text(
            """<!DOCTYPE html>
<html>
<head><title>Blog</title></head>
<body>
<h1>My Blog</h1>
<ul>
<!-- POSTS_START -->
<!-- POSTS_END -->
</ul>
</body>
</html>
"""
        )

        # Create templates
        template_folder = tmp_path / "templates"
        template_folder.mkdir()
        (template_folder / "link.html").write_text(
            '<li><a href="{{ relative_url }}">{{ title }}</a></li>'
        )

        # Create empty content folder
        content_folder = tmp_path / "content"
        content_folder.mkdir()

        # Mock both get_config locations
        with patch("boumwave.generation.index_manager.get_config", return_value=sample_config), \
             patch("boumwave.generation.parsers.get_config", return_value=sample_config):
            update_index()

            # Read updated index
            updated_content = (tmp_path / "index.html").read_text()

            assert "<!-- No posts yet -->" in updated_content

    def test_update_index_preserves_other_content(
        self, tmp_path: Path, sample_config, monkeypatch
    ):
        """Test that update_index preserves content outside markers"""
        monkeypatch.chdir(tmp_path)

        # Create index.html with content before and after markers
        (tmp_path / "index.html").write_text(
            """<!DOCTYPE html>
<html>
<head><title>Blog</title></head>
<body>
<h1>My Blog</h1>
<p>This is some intro text</p>
<ul>
<!-- POSTS_START -->
Old content that should be replaced
<!-- POSTS_END -->
</ul>
<footer>Copyright 2025</footer>
</body>
</html>
"""
        )

        # Create templates
        template_folder = tmp_path / "templates"
        template_folder.mkdir()
        (template_folder / "link.html").write_text('<li>{{ title }}</li>')

        # Create empty content folder
        content_folder = tmp_path / "content"
        content_folder.mkdir()

        # Mock both get_config locations
        with patch("boumwave.generation.index_manager.get_config", return_value=sample_config), \
             patch("boumwave.generation.parsers.get_config", return_value=sample_config):
            update_index()

            updated_content = (tmp_path / "index.html").read_text()

            # Content before and after markers should be preserved
            assert "This is some intro text" in updated_content
            assert "Copyright 2025" in updated_content
            # Old content between markers should be replaced
            assert "Old content that should be replaced" not in updated_content
