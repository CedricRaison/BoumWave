"""Unit tests for generation/parsers.py"""

from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from boumwave.exceptions import (
    FileNotFoundError as BWFileNotFoundError,
)
from boumwave.exceptions import MarkdownParseError, PostValidationError
from boumwave.generation.parsers import (
    collect_all_posts,
    find_post_files,
    parse_post_file,
)


class TestParsePostFile:
    """Tests for parse_post_file"""

    def test_parse_valid_post_file(self, tmp_path: Path):
        """Test parsing a valid markdown file"""
        post_file = tmp_path / "test.md"
        post_file.write_text(
            """---
title: "Test Post"
slug: "test-post"
published_date: 2025-10-23
lang: en
---

# Test Post

This is the content.
"""
        )

        post, content = parse_post_file(post_file)

        assert post.title == "Test Post"
        assert post.slug == "test-post"
        assert post.published_date == date(2025, 10, 23)
        assert post.lang == "en"
        assert "# Test Post" in content
        assert "This is the content." in content

    def test_parse_file_not_found(self, tmp_path: Path):
        """Test parsing non-existent file"""
        post_file = tmp_path / "nonexistent.md"

        with pytest.raises(MarkdownParseError) as exc_info:
            parse_post_file(post_file)

        assert "Error reading file" in str(exc_info.value)

    def test_parse_invalid_front_matter(self, tmp_path: Path):
        """Test parsing file with invalid front matter"""
        post_file = tmp_path / "test.md"
        post_file.write_text(
            """---
title: "Test Post"
slug: "INVALID-SLUG-UPPERCASE"
published_date: 2025-10-23
lang: en
---

Content
"""
        )

        with pytest.raises(PostValidationError) as exc_info:
            parse_post_file(post_file)

        assert "Invalid front matter" in str(exc_info.value)
        assert "slug" in str(exc_info.value)

    def test_parse_missing_required_field(self, tmp_path: Path):
        """Test parsing file with missing required field"""
        post_file = tmp_path / "test.md"
        post_file.write_text(
            """---
title: "Test Post"
slug: "test-post"
# Missing published_date and lang
---

Content
"""
        )

        with pytest.raises(PostValidationError) as exc_info:
            parse_post_file(post_file)

        assert "Missing required field" in str(exc_info.value)


class TestFindPostFiles:
    """Tests for find_post_files"""

    def test_find_post_files_success(self, tmp_path: Path):
        """Test finding post files in a folder"""
        content_folder = tmp_path / "content"
        content_folder.mkdir()
        post_folder = content_folder / "test_post"
        post_folder.mkdir()

        # Create markdown files
        (post_folder / "test_post.en.md").write_text("English content")
        (post_folder / "test_post.fr.md").write_text("French content")

        files = find_post_files("test_post", content_folder)

        assert len(files) == 2
        assert any("en.md" in str(f) for f in files)
        assert any("fr.md" in str(f) for f in files)

    def test_find_post_files_folder_not_found(self, tmp_path: Path):
        """Test when post folder doesn't exist"""
        content_folder = tmp_path / "content"
        content_folder.mkdir()

        with pytest.raises(BWFileNotFoundError) as exc_info:
            find_post_files("nonexistent_post", content_folder)

        assert "Post folder" in str(exc_info.value)
        assert "not found" in str(exc_info.value)

    def test_find_post_files_not_a_directory(self, tmp_path: Path):
        """Test when path is a file, not a directory"""
        content_folder = tmp_path / "content"
        content_folder.mkdir()
        # Create a file instead of directory
        (content_folder / "test_post").write_text("not a directory")

        with pytest.raises(BWFileNotFoundError) as exc_info:
            find_post_files("test_post", content_folder)

        assert "not a directory" in str(exc_info.value)

    def test_find_post_files_no_markdown_files(self, tmp_path: Path):
        """Test when folder exists but has no markdown files"""
        content_folder = tmp_path / "content"
        content_folder.mkdir()
        post_folder = content_folder / "test_post"
        post_folder.mkdir()
        # Create non-markdown file
        (post_folder / "readme.txt").write_text("Not markdown")

        with pytest.raises(BWFileNotFoundError) as exc_info:
            find_post_files("test_post", content_folder)

        assert "No markdown files found" in str(exc_info.value)


class TestCollectAllPosts:
    """Tests for collect_all_posts"""

    def test_collect_all_posts_empty_folder(
        self, tmp_path: Path, sample_config, monkeypatch
    ):
        """Test collecting posts from empty content folder"""
        monkeypatch.chdir(tmp_path)
        content_folder = tmp_path / "content"
        content_folder.mkdir()

        with patch(
            "boumwave.generation.parsers.get_config", return_value=sample_config
        ):
            posts = collect_all_posts()
            assert posts == []

    def test_collect_all_posts_with_posts(
        self, tmp_path: Path, sample_config, monkeypatch
    ):
        """Test collecting posts from folder with posts"""
        monkeypatch.chdir(tmp_path)
        content_folder = tmp_path / "content"
        content_folder.mkdir()

        # Create first post
        post1_folder = content_folder / "post1"
        post1_folder.mkdir()
        (post1_folder / "post1.en.md").write_text(
            """---
title: "Post 1"
slug: "post-1"
published_date: 2025-10-20
lang: en
---

Content 1
"""
        )

        # Create second post
        post2_folder = content_folder / "post2"
        post2_folder.mkdir()
        (post2_folder / "post2.fr.md").write_text(
            """---
title: "Post 2"
slug: "post-2"
published_date: 2025-10-21
lang: fr
---

Content 2
"""
        )

        with patch(
            "boumwave.generation.parsers.get_config", return_value=sample_config
        ):
            posts = collect_all_posts()

            assert len(posts) == 2
            assert any(p.title == "Post 1" for p in posts)
            assert any(p.title == "Post 2" for p in posts)

    def test_collect_all_posts_excludes_future_posts(
        self, tmp_path: Path, sample_config, monkeypatch
    ):
        """Test that future posts are excluded"""
        monkeypatch.chdir(tmp_path)
        content_folder = tmp_path / "content"
        content_folder.mkdir()

        # Create past post
        past_folder = content_folder / "past_post"
        past_folder.mkdir()
        (past_folder / "past.en.md").write_text(
            """---
title: "Past Post"
slug: "past-post"
published_date: 2020-01-01
lang: en
---

Content
"""
        )

        # Create future post
        future_folder = content_folder / "future_post"
        future_folder.mkdir()
        (future_folder / "future.en.md").write_text(
            """---
title: "Future Post"
slug: "future-post"
published_date: 2099-12-31
lang: en
---

Content
"""
        )

        with patch(
            "boumwave.generation.parsers.get_config", return_value=sample_config
        ):
            posts = collect_all_posts()

            assert len(posts) == 1
            assert posts[0].title == "Past Post"

    def test_collect_all_posts_skips_invalid_files(
        self, tmp_path: Path, sample_config, monkeypatch
    ):
        """Test that invalid posts are skipped"""
        monkeypatch.chdir(tmp_path)
        content_folder = tmp_path / "content"
        content_folder.mkdir()

        # Create valid post
        valid_folder = content_folder / "valid_post"
        valid_folder.mkdir()
        (valid_folder / "valid.en.md").write_text(
            """---
title: "Valid Post"
slug: "valid-post"
published_date: 2025-10-20
lang: en
---

Content
"""
        )

        # Create invalid post
        invalid_folder = content_folder / "invalid_post"
        invalid_folder.mkdir()
        (invalid_folder / "invalid.en.md").write_text(
            """---
title: "Invalid Post"
slug: "INVALID-SLUG"
published_date: 2025-10-20
lang: en
---

Content
"""
        )

        with patch(
            "boumwave.generation.parsers.get_config", return_value=sample_config
        ):
            posts = collect_all_posts()

            # Should only get the valid post
            assert len(posts) == 1
            assert posts[0].title == "Valid Post"
