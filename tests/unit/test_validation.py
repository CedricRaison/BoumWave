"""Unit tests for validation.py"""

from pathlib import Path
from unittest.mock import patch

import pytest

from boumwave.exceptions import EnvironmentValidationError
from boumwave.validation import (
    validate_generate_environment,
    validate_now_environment,
    validate_sitemap_environment,
)


class TestValidateGenerateEnvironment:
    """Tests for validate_generate_environment"""

    def test_validate_all_files_exist(self, tmp_path: Path, monkeypatch, sample_config):
        """Test validation passes when all files exist"""
        monkeypatch.chdir(tmp_path)

        # Create all required files and folders
        (tmp_path / "assets").mkdir()
        (tmp_path / "assets" / "logo.jpg").write_text("logo")
        (tmp_path / "templates").mkdir()
        (tmp_path / "templates" / "post.html").write_text("template")
        (tmp_path / "templates" / "link.html").write_text("link")
        (tmp_path / "content").mkdir()
        (tmp_path / "content" / "test_post").mkdir()
        (tmp_path / "index.html").write_text("<!-- POSTS_START --><!-- POSTS_END -->")

        with patch("boumwave.validation.get_config", return_value=sample_config):
            # Should not raise
            validate_generate_environment("test_post")

    def test_validate_missing_logo(self, tmp_path: Path, monkeypatch, sample_config):
        """Test validation fails when logo is missing"""
        monkeypatch.chdir(tmp_path)

        with patch("boumwave.validation.get_config", return_value=sample_config):
            with pytest.raises(EnvironmentValidationError) as exc_info:
                validate_generate_environment("test_post")

            assert "Logo file not found" in str(exc_info.value)

    def test_validate_missing_template_folder(
        self, tmp_path: Path, monkeypatch, sample_config
    ):
        """Test validation fails when template folder is missing"""
        monkeypatch.chdir(tmp_path)

        # Create logo but not templates
        (tmp_path / "assets").mkdir()
        (tmp_path / "assets" / "logo.jpg").write_text("logo")

        with patch("boumwave.validation.get_config", return_value=sample_config):
            with pytest.raises(EnvironmentValidationError) as exc_info:
                validate_generate_environment("test_post")

            assert "Template folder not found" in str(exc_info.value)
            assert "bw scaffold" in str(exc_info.value)

    def test_validate_missing_post_template(
        self, tmp_path: Path, monkeypatch, sample_config
    ):
        """Test validation fails when post template is missing"""
        monkeypatch.chdir(tmp_path)

        (tmp_path / "assets").mkdir()
        (tmp_path / "assets" / "logo.jpg").write_text("logo")
        (tmp_path / "templates").mkdir()
        # Don't create post.html

        with patch("boumwave.validation.get_config", return_value=sample_config):
            with pytest.raises(EnvironmentValidationError) as exc_info:
                validate_generate_environment("test_post")

            assert "Post template not found" in str(exc_info.value)

    def test_validate_missing_index_file(
        self, tmp_path: Path, monkeypatch, sample_config
    ):
        """Test validation fails when index.html is missing"""
        monkeypatch.chdir(tmp_path)

        (tmp_path / "assets").mkdir()
        (tmp_path / "assets" / "logo.jpg").write_text("logo")
        (tmp_path / "templates").mkdir()
        (tmp_path / "templates" / "post.html").write_text("template")
        (tmp_path / "templates" / "link.html").write_text("link")
        # Don't create index.html

        with patch("boumwave.validation.get_config", return_value=sample_config):
            with pytest.raises(EnvironmentValidationError) as exc_info:
                validate_generate_environment("test_post")

            assert "Index file not found" in str(exc_info.value)

    def test_validate_missing_start_marker(
        self, tmp_path: Path, monkeypatch, sample_config
    ):
        """Test validation fails when start marker is missing from index.html"""
        monkeypatch.chdir(tmp_path)

        (tmp_path / "assets").mkdir()
        (tmp_path / "assets" / "logo.jpg").write_text("logo")
        (tmp_path / "templates").mkdir()
        (tmp_path / "templates" / "post.html").write_text("template")
        (tmp_path / "templates" / "link.html").write_text("link")
        (tmp_path / "index.html").write_text("No markers here")

        with patch("boumwave.validation.get_config", return_value=sample_config):
            with pytest.raises(EnvironmentValidationError) as exc_info:
                validate_generate_environment("test_post")

            assert "Start marker not found" in str(exc_info.value)

    def test_validate_missing_post_folder(
        self, tmp_path: Path, monkeypatch, sample_config
    ):
        """Test validation fails when post folder doesn't exist"""
        monkeypatch.chdir(tmp_path)

        (tmp_path / "assets").mkdir()
        (tmp_path / "assets" / "logo.jpg").write_text("logo")
        (tmp_path / "templates").mkdir()
        (tmp_path / "templates" / "post.html").write_text("template")
        (tmp_path / "templates" / "link.html").write_text("link")
        (tmp_path / "content").mkdir()
        (tmp_path / "index.html").write_text("<!-- POSTS_START --><!-- POSTS_END -->")
        # Don't create post folder

        with patch("boumwave.validation.get_config", return_value=sample_config):
            with pytest.raises(EnvironmentValidationError) as exc_info:
                validate_generate_environment("nonexistent_post")

            assert "Post folder not found" in str(exc_info.value)
            assert "bw new_post" in str(exc_info.value)


class TestValidateSitemapEnvironment:
    """Tests for validate_sitemap_environment"""

    def test_validate_sitemap_exists(self, tmp_path: Path, monkeypatch, sample_config):
        """Test validation passes when sitemap.xml exists with markers"""
        monkeypatch.chdir(tmp_path)

        (tmp_path / "sitemap.xml").write_text(
            "<!-- SITEMAP_START --><!-- SITEMAP_END -->"
        )

        with patch("boumwave.validation.get_config", return_value=sample_config):
            # Should not raise
            validate_sitemap_environment()

    def test_validate_sitemap_missing(self, tmp_path: Path, monkeypatch, sample_config):
        """Test validation fails when sitemap.xml is missing"""
        monkeypatch.chdir(tmp_path)

        with patch("boumwave.validation.get_config", return_value=sample_config):
            with pytest.raises(EnvironmentValidationError) as exc_info:
                validate_sitemap_environment()

            assert "Sitemap file not found" in str(exc_info.value)

    def test_validate_sitemap_missing_markers(
        self, tmp_path: Path, monkeypatch, sample_config
    ):
        """Test validation fails when markers are missing"""
        monkeypatch.chdir(tmp_path)

        (tmp_path / "sitemap.xml").write_text("No markers here")

        with patch("boumwave.validation.get_config", return_value=sample_config):
            with pytest.raises(EnvironmentValidationError) as exc_info:
                validate_sitemap_environment()

            assert "Start marker not found" in str(exc_info.value)


class TestValidateNowEnvironment:
    """Tests for validate_now_environment"""

    def test_validate_now_feature_disabled(
        self, tmp_path: Path, monkeypatch, sample_config
    ):
        """Test validation fails when Now. feature is not configured"""
        monkeypatch.chdir(tmp_path)

        # Create a config without now_folder
        from boumwave.config import BoumWaveConfig, PathsConfig

        config_no_now = BoumWaveConfig(
            paths=PathsConfig(
                template_folder="templates",
                content_folder="content",
                output_folder="posts",
                post_template="post.html",
                link_template="link.html",
                index_template="index.html",
                sitemap_template="sitemap.xml",
                now_folder=None,  # Not configured
                now_template=None,
                now_index_template=None,
            ),
            site=sample_config.site,
        )

        with patch("boumwave.validation.get_config", return_value=config_no_now):
            with pytest.raises(EnvironmentValidationError) as exc_info:
                validate_now_environment()

            assert "Now. feature is not enabled" in str(exc_info.value)

    def test_validate_now_folder_missing(
        self, tmp_path: Path, monkeypatch, sample_config
    ):
        """Test validation fails when now folder doesn't exist"""
        monkeypatch.chdir(tmp_path)

        # Create templates but not now folder
        (tmp_path / "templates").mkdir()
        (tmp_path / "templates" / "now.html").write_text("template")
        (tmp_path / "templates" / "now_index.html").write_text("template")
        (tmp_path / "index.html").write_text("<!-- NOW_START --><!-- NOW_END -->")

        with patch("boumwave.validation.get_config", return_value=sample_config):
            with pytest.raises(EnvironmentValidationError) as exc_info:
                validate_now_environment()

            assert "Now. folder not found" in str(exc_info.value)

    def test_validate_now_no_posts(self, tmp_path: Path, monkeypatch, sample_config):
        """Test validation fails when no Now. posts exist"""
        monkeypatch.chdir(tmp_path)

        (tmp_path / "now").mkdir()  # Empty folder
        (tmp_path / "templates").mkdir()
        (tmp_path / "templates" / "now.html").write_text("template")
        (tmp_path / "templates" / "now_index.html").write_text("template")
        (tmp_path / "index.html").write_text("<!-- NOW_START --><!-- NOW_END -->")

        with patch("boumwave.validation.get_config", return_value=sample_config):
            with pytest.raises(EnvironmentValidationError) as exc_info:
                validate_now_environment()

            assert "No Now. posts found" in str(exc_info.value)
            assert "bw new_now" in str(exc_info.value)
