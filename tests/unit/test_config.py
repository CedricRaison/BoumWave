"""Unit tests for config.py"""

import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from boumwave.config import (
    BoumWaveConfig,
    DateFormat,
    PathsConfig,
    SiteConfig,
    Translations,
    load_config,
)
from boumwave.exceptions import ConfigNotFoundError, ConfigValidationError


class TestDateFormat:
    """Tests for DateFormat enum"""

    def test_date_format_values(self):
        """Test DateFormat enum values"""
        assert DateFormat.SHORT.value == "short"
        assert DateFormat.MEDIUM.value == "medium"
        assert DateFormat.LONG.value == "long"
        assert DateFormat.FULL.value == "full"


class TestTranslations:
    """Tests for Translations model"""

    def test_translations_creation(self):
        """Test creating translations"""
        trans = Translations(published_on="Published on")
        assert trans.published_on == "Published on"

    def test_translations_missing_field(self):
        """Test missing required field"""
        with pytest.raises(ValidationError):
            Translations()


class TestPathsConfig:
    """Tests for PathsConfig model"""

    def test_paths_config_creation(self, sample_paths_config: PathsConfig):
        """Test creating PathsConfig"""
        assert sample_paths_config.template_folder == "templates"
        assert sample_paths_config.content_folder == "content"
        assert sample_paths_config.output_folder == "posts"
        assert sample_paths_config.post_template == "post.html"
        assert sample_paths_config.link_template == "link.html"
        assert sample_paths_config.index_template == "index.html"

    def test_paths_config_missing_required_field(self):
        """Test missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            PathsConfig(
                template_folder="templates",
                content_folder="content",
                # Missing output_folder and other required fields
            )
        assert "output_folder" in str(exc_info.value)


class TestSiteConfig:
    """Tests for SiteConfig model"""

    def test_site_config_creation(self, sample_site_config: SiteConfig):
        """Test creating SiteConfig"""
        assert sample_site_config.languages == ["en", "fr"]
        assert str(sample_site_config.site_url) == "https://example.com/"
        assert sample_site_config.logo_path == "assets/logo.jpg"
        assert sample_site_config.date_format == DateFormat.LONG

    def test_site_url_base_computed_field(self, sample_site_config: SiteConfig):
        """Test site_url_base removes trailing slash"""
        assert sample_site_config.site_url_base == "https://example.com"

    def test_site_url_base_no_trailing_slash(self):
        """Test site_url_base when URL has no trailing slash"""
        config = SiteConfig(
            languages=["en"],
            site_url="https://example.com",
            logo_path="logo.jpg",
            date_format=DateFormat.LONG,
            posts_start_marker="<!-- POSTS_START -->",
            posts_end_marker="<!-- POSTS_END -->",
            sitemap_start_marker="<!-- SITEMAP_START -->",
            sitemap_end_marker="<!-- SITEMAP_END -->",
            translations={"en": Translations(published_on="Published on")},
        )
        assert config.site_url_base == "https://example.com"

    def test_translations_validation_all_languages(self):
        """Test that translations must exist for all configured languages"""
        with pytest.raises(ValidationError) as exc_info:
            SiteConfig(
                languages=["en", "fr", "de"],
                site_url="https://example.com",
                logo_path="logo.jpg",
                date_format=DateFormat.LONG,
                posts_start_marker="<!-- POSTS_START -->",
                posts_end_marker="<!-- POSTS_END -->",
                sitemap_start_marker="<!-- SITEMAP_START -->",
                sitemap_end_marker="<!-- SITEMAP_END -->",
                translations={
                    "en": Translations(published_on="Published on"),
                    "fr": Translations(published_on="Publié le"),
                    # Missing "de"
                },
            )
        error_str = str(exc_info.value)
        assert "Missing translations" in error_str
        assert "de" in error_str

    def test_invalid_site_url(self):
        """Test invalid URL format"""
        with pytest.raises(ValidationError):
            SiteConfig(
                languages=["en"],
                site_url="not-a-valid-url",
                logo_path="logo.jpg",
                date_format=DateFormat.LONG,
                posts_start_marker="<!-- POSTS_START -->",
                posts_end_marker="<!-- POSTS_END -->",
                sitemap_start_marker="<!-- SITEMAP_START -->",
                sitemap_end_marker="<!-- SITEMAP_END -->",
                translations={"en": Translations(published_on="Published on")},
            )


class TestBoumWaveConfig:
    """Tests for BoumWaveConfig model"""

    def test_config_creation(self, sample_config: BoumWaveConfig):
        """Test creating complete BoumWave config"""
        assert isinstance(sample_config.paths, PathsConfig)
        assert isinstance(sample_config.site, SiteConfig)

    def test_config_missing_section(self):
        """Test missing required section"""
        with pytest.raises(ValidationError):
            BoumWaveConfig(
                paths=PathsConfig(
                    template_folder="templates",
                    content_folder="content",
                    output_folder="posts",
                    post_template="post.html",
                    link_template="link.html",
                    index_template="index.html",
                    sitemap_template="sitemap.xml",
                )
                # Missing site section
            )


class TestLoadConfig:
    """Tests for load_config function"""

    def test_load_config_file_not_found(self, tmp_path: Path, monkeypatch):
        """Test loading config when file doesn't exist"""
        monkeypatch.chdir(tmp_path)

        with pytest.raises(ConfigNotFoundError) as exc_info:
            load_config()

        assert "boumwave.toml not found" in str(exc_info.value)
        assert exc_info.value.hint is not None

    def test_load_config_invalid_toml(self, tmp_path: Path, monkeypatch):
        """Test loading config with invalid TOML syntax"""
        monkeypatch.chdir(tmp_path)

        # Create invalid TOML file
        config_path = tmp_path / "boumwave.toml"
        config_path.write_text("this is [not valid TOML")

        with pytest.raises(ConfigValidationError) as exc_info:
            load_config()

        assert "Error reading configuration file" in str(exc_info.value)

    def test_load_config_missing_required_field(self, tmp_path: Path, monkeypatch):
        """Test loading config with missing required fields"""
        monkeypatch.chdir(tmp_path)

        # Create config with missing fields
        config_path = tmp_path / "boumwave.toml"
        config_path.write_text(
            """
[paths]
template_folder = "templates"
# Missing other required fields

[site]
languages = ["en"]
"""
        )

        with pytest.raises(ConfigValidationError) as exc_info:
            load_config()

        assert "Invalid configuration" in str(exc_info.value)
        assert "Missing required config" in str(exc_info.value)

    def test_load_config_invalid_field_value(self, tmp_path: Path, monkeypatch):
        """Test loading config with invalid field values"""
        monkeypatch.chdir(tmp_path)

        config_path = tmp_path / "boumwave.toml"
        config_path.write_text(
            """
[paths]
template_folder = "templates"
content_folder = "content"
output_folder = "posts"
post_template = "post.html"
link_template = "link.html"
index_template = "index.html"
sitemap_template = "sitemap.xml"

[site]
languages = ["en"]
site_url = "not-a-valid-url"
logo_path = "logo.jpg"
date_format = "long"
posts_start_marker = "<!-- POSTS_START -->"
posts_end_marker = "<!-- POSTS_END -->"
sitemap_start_marker = "<!-- SITEMAP_START -->"
sitemap_end_marker = "<!-- SITEMAP_END -->"

[site.translations.en]
published_on = "Published on"
"""
        )

        with pytest.raises(ConfigValidationError) as exc_info:
            load_config()

        assert "Invalid configuration" in str(exc_info.value)

    def test_load_config_success(self, tmp_path: Path, monkeypatch):
        """Test successfully loading a valid config"""
        monkeypatch.chdir(tmp_path)

        config_path = tmp_path / "boumwave.toml"
        config_path.write_text(
            """
[paths]
template_folder = "templates"
content_folder = "content"
output_folder = "posts"
post_template = "post.html"
link_template = "link.html"
index_template = "index.html"
sitemap_template = "sitemap.xml"

[site]
languages = ["en", "fr"]
site_url = "https://example.com"
logo_path = "assets/logo.jpg"
date_format = "long"
posts_start_marker = "<!-- POSTS_START -->"
posts_end_marker = "<!-- POSTS_END -->"
sitemap_start_marker = "<!-- SITEMAP_START -->"
sitemap_end_marker = "<!-- SITEMAP_END -->"

[site.translations.en]
published_on = "Published on"

[site.translations.fr]
published_on = "Publié le"
"""
        )

        config = load_config()

        assert config.paths.template_folder == "templates"
        assert config.site.languages == ["en", "fr"]
        assert config.site.site_url_base == "https://example.com"
