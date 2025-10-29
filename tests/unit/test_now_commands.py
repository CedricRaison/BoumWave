"""Unit tests for Now. commands"""

import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from boumwave.commands.generate_now import (
    _collect_all_now_posts,
    _generate_now_page,
    _update_index_with_now,
)
from boumwave.commands.new_now import _new_now_impl
from boumwave.exceptions import FileAlreadyExistsError, ValidationError
from boumwave.models import Now


class TestNewNowCommand:
    """Tests for new_now command"""

    def test_new_now_creates_file(self, tmp_path: Path, monkeypatch, sample_config):
        """Test that new_now creates a file with today's date"""
        monkeypatch.chdir(tmp_path)

        # Create config with Now. feature enabled
        config_with_now = sample_config
        config_with_now.paths.now_folder = "now"

        with patch("boumwave.commands.new_now.load_config", return_value=config_with_now):
            _new_now_impl()

        # Check file was created
        today = date.today()
        expected_file = tmp_path / "now" / f"{today.isoformat()}.md"
        assert expected_file.exists()

        # Check file has content
        content = expected_file.read_text()
        assert len(content) > 0  # Should have template content

    def test_new_now_feature_disabled(self, tmp_path: Path, monkeypatch, sample_config):
        """Test error when Now. feature is not enabled"""
        monkeypatch.chdir(tmp_path)

        # Config WITHOUT Now. feature
        config_without_now = sample_config
        config_without_now.paths.now_folder = None

        with patch("boumwave.commands.new_now.load_config", return_value=config_without_now):
            with pytest.raises(ValidationError) as exc_info:
                _new_now_impl()

            assert "Now. feature is not enabled" in str(exc_info.value)

    def test_new_now_file_already_exists(self, tmp_path: Path, monkeypatch, sample_config):
        """Test error when today's file already exists"""
        monkeypatch.chdir(tmp_path)

        # Create Now. folder and today's file
        now_folder = tmp_path / "now"
        now_folder.mkdir()
        today = date.today()
        existing_file = now_folder / f"{today.isoformat()}.md"
        existing_file.write_text("Existing content")

        config_with_now = sample_config
        config_with_now.paths.now_folder = "now"

        with patch("boumwave.commands.new_now.load_config", return_value=config_with_now):
            with pytest.raises(FileAlreadyExistsError) as exc_info:
                _new_now_impl()

            assert "already exists for today" in str(exc_info.value)


class TestCollectAllNowPosts:
    """Tests for _collect_all_now_posts function"""

    def test_collect_empty_folder(self, tmp_path: Path, monkeypatch, sample_config):
        """Test collecting from empty folder"""
        monkeypatch.chdir(tmp_path)

        # Create empty now folder
        now_folder = tmp_path / "now"
        now_folder.mkdir()

        config_with_now = sample_config
        config_with_now.paths.now_folder = "now"

        with patch("boumwave.commands.generate_now.load_config", return_value=config_with_now):
            posts = _collect_all_now_posts()
            assert posts == []

    def test_collect_single_post(self, tmp_path: Path, monkeypatch, sample_config):
        """Test collecting a single Now. post"""
        monkeypatch.chdir(tmp_path)

        # Create now folder with one post
        now_folder = tmp_path / "now"
        now_folder.mkdir()
        (now_folder / "2025-10-28.md").write_text("# Hello\n\nThis is my status.")

        config_with_now = sample_config
        config_with_now.paths.now_folder = "now"

        with patch("boumwave.commands.generate_now.load_config", return_value=config_with_now):
            posts = _collect_all_now_posts()

            assert len(posts) == 1
            assert posts[0].post_date == date(2025, 10, 28)
            assert "<h1>Hello</h1>" in posts[0].content

    def test_collect_multiple_posts_sorted(self, tmp_path: Path, monkeypatch, sample_config):
        """Test that posts are sorted by date (most recent first)"""
        monkeypatch.chdir(tmp_path)

        # Create multiple posts
        now_folder = tmp_path / "now"
        now_folder.mkdir()
        (now_folder / "2025-10-25.md").write_text("Old post")
        (now_folder / "2025-10-28.md").write_text("Recent post")
        (now_folder / "2025-10-26.md").write_text("Middle post")

        config_with_now = sample_config
        config_with_now.paths.now_folder = "now"

        with patch("boumwave.commands.generate_now.load_config", return_value=config_with_now):
            posts = _collect_all_now_posts()

            assert len(posts) == 3
            # Should be sorted most recent first
            assert posts[0].post_date == date(2025, 10, 28)
            assert posts[1].post_date == date(2025, 10, 26)
            assert posts[2].post_date == date(2025, 10, 25)

    def test_collect_skips_invalid_filenames(
        self, tmp_path: Path, monkeypatch, sample_config, capsys
    ):
        """Test that invalid filenames are skipped with warning"""
        monkeypatch.chdir(tmp_path)

        # Create posts with valid and invalid names
        now_folder = tmp_path / "now"
        now_folder.mkdir()
        (now_folder / "2025-10-28.md").write_text("Valid post")
        (now_folder / "invalid-name.md").write_text("Should be skipped")

        config_with_now = sample_config
        config_with_now.paths.now_folder = "now"

        with patch("boumwave.commands.generate_now.load_config", return_value=config_with_now):
            posts = _collect_all_now_posts()

            # Should only get valid post
            assert len(posts) == 1
            assert posts[0].post_date == date(2025, 10, 28)

            # Should have warning in stderr
            captured = capsys.readouterr()
            assert "Skipping" in captured.err
            assert "invalid-name.md" in captured.err


class TestUpdateIndexWithNow:
    """Tests for _update_index_with_now function"""

    def test_update_index_with_now_post(self, tmp_path: Path, monkeypatch, sample_config):
        """Test updating index.html with a Now. post"""
        monkeypatch.chdir(tmp_path)

        # Create index.html with markers
        (tmp_path / "index.html").write_text(
            """<!DOCTYPE html>
<html>
<head><title>Blog</title></head>
<body>
<h1>My Blog</h1>
<!-- NOW_START -->
<!-- NOW_END -->
</body>
</html>
"""
        )

        # Create now_index template
        templates_folder = tmp_path / "templates"
        templates_folder.mkdir()
        (templates_folder / "now_index.html").write_text(
            """<div class="now">
    <time datetime="{{ published_datetime_iso }}">{{ date_formatted }}</time>
    <div>{{ content }}</div>
</div>"""
        )

        # Create a Now post
        now_post = Now(
            post_date=date(2025, 10, 28),
            content="<p>What I'm doing now</p>",
        )

        # Update config
        config_with_now = sample_config
        config_with_now.paths.now_index_template = "now_index.html"

        with patch("boumwave.commands.generate_now.load_config", return_value=config_with_now):
            _update_index_with_now(now_post)

        # Check index was updated
        updated_content = (tmp_path / "index.html").read_text()
        assert "What I'm doing now" in updated_content
        assert "2025-10-28T00:00:00Z" in updated_content


class TestGenerateNowPage:
    """Tests for _generate_now_page function"""

    def test_generate_now_page(self, tmp_path: Path, monkeypatch, sample_config):
        """Test generating now.html page"""
        monkeypatch.chdir(tmp_path)

        # Create now template
        templates_folder = tmp_path / "templates"
        templates_folder.mkdir()
        (templates_folder / "now.html").write_text(
            """<!DOCTYPE html>
<html>
<head><title>Now</title></head>
<body>
<h1>What I'm doing now</h1>
{% for post in now_posts %}
<article>
    <time>{{ post.get_date_formatted(config) }}</time>
    <div>{{ post.content }}</div>
</article>
{% endfor %}
</body>
</html>
"""
        )

        # Create Now posts
        now_posts = [
            Now(post_date=date(2025, 10, 28), content="<p>Today's update</p>"),
            Now(post_date=date(2025, 10, 27), content="<p>Yesterday's update</p>"),
        ]

        # Update config
        config_with_now = sample_config
        config_with_now.paths.now_template = "now.html"

        with patch("boumwave.commands.generate_now.load_config", return_value=config_with_now):
            _generate_now_page(now_posts)

        # Check now.html was created
        now_file = tmp_path / "now.html"
        assert now_file.exists()

        content = now_file.read_text()
        assert "Today's update" in content
        assert "Yesterday's update" in content
