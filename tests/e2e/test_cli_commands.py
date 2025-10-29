"""End-to-end tests for CLI commands"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from boumwave.cli import main


class TestInitCommand:
    """E2E tests for 'bw init' command"""

    def test_init_creates_config(self, tmp_path: Path, monkeypatch):
        """Test that 'bw init' creates boumwave.toml"""
        monkeypatch.chdir(tmp_path)

        with patch.object(sys, "argv", ["bw", "init"]):
            # Should not raise
            main()

        config_file = tmp_path / "boumwave.toml"
        assert config_file.exists()

        content = config_file.read_text()
        assert "[paths]" in content
        assert "[site]" in content

    def test_init_when_config_exists(self, tmp_path: Path, monkeypatch, capsys):
        """Test that 'bw init' handles existing config"""
        monkeypatch.chdir(tmp_path)

        # Create existing config
        (tmp_path / "boumwave.toml").write_text("existing config")

        with patch.object(sys, "argv", ["bw", "init"]):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        assert "already exists" in captured.err.lower() or "already exists" in captured.out.lower()


class TestScaffoldCommand:
    """E2E tests for 'bw scaffold' command"""

    def test_scaffold_creates_structure(self, tmp_path: Path, monkeypatch, sample_config_file: Path):
        """Test that 'bw scaffold' creates folder structure"""
        monkeypatch.chdir(tmp_path)

        with patch.object(sys, "argv", ["bw", "scaffold"]):
            main()

        # Check folders created
        assert (tmp_path / "templates").exists()
        assert (tmp_path / "content").exists()
        assert (tmp_path / "posts").exists()

        # Check example templates created
        assert (tmp_path / "templates" / "post.html").exists()
        assert (tmp_path / "templates" / "link.html").exists()
        assert (tmp_path / "index.html").exists()


class TestNewPostCommand:
    """E2E tests for 'bw new_post' command"""

    def test_new_post_creates_files(self, tmp_path: Path, monkeypatch, sample_config_file: Path):
        """Test that 'bw new_post' creates post files"""
        monkeypatch.chdir(tmp_path)

        # Content folder is already created by sample_config_file fixture

        with patch.object(sys, "argv", ["bw", "new_post", "My Test Post"]):
            main()

        # Check post folder created
        post_folder = tmp_path / "content" / "my_test_post"
        assert post_folder.exists()

        # Check language files created
        assert (post_folder / "my_test_post.en.md").exists()
        assert (post_folder / "my_test_post.fr.md").exists()

        # Check front matter
        en_content = (post_folder / "my_test_post.en.md").read_text()
        assert "title: \"My Test Post\"" in en_content
        assert "slug: \"my-test-post\"" in en_content
        assert "lang: en" in en_content


class TestGenerateCommand:
    """E2E tests for 'bw generate' command"""

    def test_generate_missing_config(self, tmp_path: Path, monkeypatch, capsys):
        """Test 'bw generate' fails when config missing"""
        monkeypatch.chdir(tmp_path)

        with patch.object(sys, "argv", ["bw", "generate", "test_post"]):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        assert "boumwave.toml not found" in captured.err

    def test_generate_creates_html(self, tmp_path: Path, monkeypatch, sample_config_file: Path):
        """Test that 'bw generate' creates HTML files"""
        monkeypatch.chdir(tmp_path)

        # Templates folder is already created by sample_config_file fixture
        # Just add the template files
        (tmp_path / "templates" / "post.html").write_text(
            """<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
</head>
<body>
    <article>
        <h1>{{ title }}</h1>
        <div>{{ content }}</div>
    </article>
</body>
</html>
"""
        )
        (tmp_path / "templates" / "link.html").write_text(
            '<li><a href="{{ relative_url }}">{{ title }}</a></li>'
        )
        (tmp_path / "index.html").write_text(
            "<!-- POSTS_START --><!-- POSTS_END -->"
        )

        # Create post (content folder already exists from fixture)
        content_folder = tmp_path / "content"
        post_folder = content_folder / "test_post"
        post_folder.mkdir()
        (post_folder / "test_post.en.md").write_text(
            """---
title: "Test Post"
slug: "test-post"
published_date: 2025-10-20
lang: en
---

# Test Post

This is test content.
"""
        )

        with patch.object(sys, "argv", ["bw", "generate", "test_post"]):
            main()

        # Check HTML was created
        output_file = tmp_path / "posts" / "en" / "test-post" / "index.html"
        assert output_file.exists()

        html_content = output_file.read_text()
        # BeautifulSoup formats the HTML, so check for content rather than exact format
        assert "Test Post" in html_content
        assert "<h1>" in html_content
        assert "This is test content" in html_content
        assert '<link href="https://example.com/posts/en/test-post" rel="canonical"' in html_content


class TestNewNowCommand:
    """E2E tests for 'bw new_now' command"""

    def test_new_now_creates_file(self, tmp_path: Path, monkeypatch):
        """Test that 'bw new_now' creates a file for today"""
        monkeypatch.chdir(tmp_path)

        # Create config with Now. feature enabled
        (tmp_path / "boumwave.toml").write_text(
            """
[paths]
template_folder = "templates"
content_folder = "content"
output_folder = "posts"
post_template = "post.html"
link_template = "link.html"
index_template = "index.html"
sitemap_template = "sitemap.xml"
now_folder = "now"
now_template = "now.html"
now_index_template = "now_index.html"

[site]
languages = ["en", "fr"]
site_url = "https://example.com"
logo_path = "assets/logo.jpg"
date_format = "long"
posts_start_marker = "<!-- POSTS_START -->"
posts_end_marker = "<!-- POSTS_END -->"
sitemap_start_marker = "<!-- SITEMAP_START -->"
sitemap_end_marker = "<!-- SITEMAP_END -->"
now_start_marker = "<!-- NOW_START -->"
now_end_marker = "<!-- NOW_END -->"

[site.translations.en]
published_on = "Published on"

[site.translations.fr]
published_on = "Publié le"
"""
        )

        with patch.object(sys, "argv", ["bw", "new_now"]):
            main()

        # Check file was created
        from datetime import date

        today = date.today()
        expected_file = tmp_path / "now" / f"{today.isoformat()}.md"
        assert expected_file.exists()

    def test_new_now_feature_disabled(self, tmp_path: Path, monkeypatch, sample_config_file: Path, capsys):
        """Test error when Now. feature is not configured"""
        monkeypatch.chdir(tmp_path)

        with patch.object(sys, "argv", ["bw", "new_now"]):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        assert "Now. feature is not enabled" in captured.err


class TestGenerateNowCommand:
    """E2E tests for 'bw generate_now' command"""

    def test_generate_now_creates_pages(self, tmp_path: Path, monkeypatch):
        """Test that 'bw generate_now' creates now.html and updates index"""
        monkeypatch.chdir(tmp_path)

        # Create full configuration
        (tmp_path / "boumwave.toml").write_text(
            """
[paths]
template_folder = "templates"
content_folder = "content"
output_folder = "posts"
post_template = "post.html"
link_template = "link.html"
index_template = "index.html"
sitemap_template = "sitemap.xml"
now_folder = "now"
now_template = "now.html"
now_index_template = "now_index.html"

[site]
languages = ["en"]
site_url = "https://example.com"
logo_path = "logo.jpg"
date_format = "long"
posts_start_marker = "<!-- POSTS_START -->"
posts_end_marker = "<!-- POSTS_END -->"
sitemap_start_marker = "<!-- SITEMAP_START -->"
sitemap_end_marker = "<!-- SITEMAP_END -->"
now_start_marker = "<!-- NOW_START -->"
now_end_marker = "<!-- NOW_END -->"

[site.translations.en]
published_on = "Published on"
"""
        )

        # Create templates
        (tmp_path / "templates").mkdir()
        (tmp_path / "templates" / "now.html").write_text("<html><body>Now page</body></html>")
        (tmp_path / "templates" / "now_index.html").write_text(
            '<div class="now">{{ content }}</div>'
        )

        # Create index.html with markers
        (tmp_path / "index.html").write_text(
            "<!DOCTYPE html><html><body><!-- NOW_START --><!-- NOW_END --></body></html>"
        )

        # Create a Now. post
        (tmp_path / "now").mkdir()
        (tmp_path / "now" / "2025-10-28.md").write_text("# My status\n\nWorking on tests!")

        with patch.object(sys, "argv", ["bw", "generate_now"]):
            main()

        # Check now.html was created
        assert (tmp_path / "now.html").exists()

        # Check index.html was updated
        index_content = (tmp_path / "index.html").read_text()
        assert "Working on tests" in index_content


class TestCLIHelp:
    """E2E tests for CLI help and errors"""

    def test_no_command_shows_help(self, capsys):
        """Test that running without command shows help"""
        with patch.object(sys, "argv", ["bw"]):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower() or "usage:" in captured.err.lower()

    def test_invalid_command(self, capsys):
        """Test that invalid command shows error"""
        with patch.object(sys, "argv", ["bw", "invalid_command"]):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        # Should show error about invalid command
        assert captured.err or captured.out
