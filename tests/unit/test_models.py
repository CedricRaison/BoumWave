"""Unit tests for models.py"""

from datetime import date

import pytest
from pydantic import ValidationError

from boumwave.config import BoumWaveConfig
from boumwave.models import EnrichedPost, Now, Post


class TestPost:
    """Tests for Post model"""

    def test_post_creation_valid(self, sample_post: Post):
        """Test creating a valid post"""
        assert sample_post.title == "My Awesome Post"
        assert sample_post.slug == "my-awesome-post"
        assert sample_post.published_date == date(2025, 10, 23)
        assert sample_post.lang == "en"

    def test_post_slug_validation_lowercase(self):
        """Test slug must be lowercase"""
        with pytest.raises(ValidationError) as exc_info:
            Post(
                title="Test",
                slug="My-Awesome-Post",  # Invalid: uppercase
                published_date=date(2025, 10, 23),
                lang="en",
            )
        assert "slug" in str(exc_info.value)

    def test_post_slug_validation_hyphens(self):
        """Test slug can only contain lowercase alphanumeric and hyphens"""
        # Valid slug
        post = Post(
            title="Test",
            slug="my-awesome-post-123",
            published_date=date(2025, 10, 23),
            lang="en",
        )
        assert post.slug == "my-awesome-post-123"

        # Invalid slug with underscore
        with pytest.raises(ValidationError):
            Post(
                title="Test",
                slug="my_awesome_post",
                published_date=date(2025, 10, 23),
                lang="en",
            )

    def test_post_lang_validation(self):
        """Test lang must be exactly 2 lowercase letters"""
        # Valid
        post = Post(
            title="Test",
            slug="test",
            published_date=date(2025, 10, 23),
            lang="fr",
        )
        assert post.lang == "fr"

        # Invalid: uppercase
        with pytest.raises(ValidationError):
            Post(
                title="Test",
                slug="test",
                published_date=date(2025, 10, 23),
                lang="EN",
            )

        # Invalid: too long
        with pytest.raises(ValidationError):
            Post(
                title="Test",
                slug="test",
                published_date=date(2025, 10, 23),
                lang="eng",
            )

    def test_post_missing_required_field(self):
        """Test that missing required fields raise validation error"""
        with pytest.raises(ValidationError) as exc_info:
            Post(
                title="Test",
                slug="test",
                # Missing published_date
                lang="en",
            )
        assert "published_date" in str(exc_info.value)

    def test_published_datetime_iso(self, sample_post: Post):
        """Test ISO 8601 datetime computed field"""
        assert sample_post.published_datetime_iso == "2025-10-23T00:00:00Z"

    def test_get_relative_url(self, sample_post: Post, sample_config: BoumWaveConfig):
        """Test relative URL generation"""
        url = sample_post.get_relative_url(sample_config)
        assert url == "/posts/en/my-awesome-post"

    def test_get_relative_url_different_lang(
        self, sample_post_fr: Post, sample_config: BoumWaveConfig
    ):
        """Test relative URL with French language"""
        url = sample_post_fr.get_relative_url(sample_config)
        assert url == "/posts/fr/mon-super-article"

    def test_get_full_url(self, sample_post: Post, sample_config: BoumWaveConfig):
        """Test full URL generation"""
        url = sample_post.get_full_url(sample_config)
        assert url == "https://example.com/posts/en/my-awesome-post"

    def test_get_published_on_date_en(
        self, sample_post: Post, sample_config: BoumWaveConfig
    ):
        """Test localized publication date in English"""
        date_str = sample_post.get_published_on_date(sample_config)
        assert "Published on" in date_str
        assert "October" in date_str or "23" in date_str

    def test_get_published_on_date_fr(
        self, sample_post_fr: Post, sample_config: BoumWaveConfig
    ):
        """Test localized publication date in French"""
        date_str = sample_post_fr.get_published_on_date(sample_config)
        assert "Publié le" in date_str
        assert "octobre" in date_str or "24" in date_str

    def test_get_image_path_with_image(self, sample_config: BoumWaveConfig, tmp_path):
        """Test get_image_path when post has an image"""
        # Create a temporary image file
        image_path = tmp_path / "test.jpg"
        image_path.write_text("fake image")

        post = Post(
            title="Test",
            slug="test",
            published_date=date(2025, 10, 23),
            lang="en",
            image_path=image_path,
        )

        assert post.get_image_path(sample_config) == str(image_path)

    def test_get_image_path_fallback_to_logo(
        self, sample_post: Post, sample_config: BoumWaveConfig
    ):
        """Test get_image_path falls back to logo when no image"""
        assert sample_post.image_path is None
        assert sample_post.get_image_path(sample_config) == "assets/logo.jpg"


class TestEnrichedPost:
    """Tests for EnrichedPost model"""

    def test_enriched_post_creation(
        self, sample_post: Post, sample_config: BoumWaveConfig
    ):
        """Test creating an enriched post"""
        enriched = EnrichedPost(
            post=sample_post,
            description="Test description",
            content_html="<p>Test content</p>",
            config=sample_config,
        )

        assert enriched.post == sample_post
        assert enriched.description == "Test description"
        assert enriched.content_html == "<p>Test content</p>"
        assert enriched.config == sample_config

    def test_relative_url_computed_field(self, sample_enriched_post: EnrichedPost):
        """Test relative_url computed field"""
        assert sample_enriched_post.relative_url == "/posts/en/my-awesome-post"

    def test_full_url_computed_field(self, sample_enriched_post: EnrichedPost):
        """Test full_url computed field"""
        assert (
            sample_enriched_post.full_url == "https://example.com/posts/en/my-awesome-post"
        )

    def test_published_on_date_computed_field(self, sample_enriched_post: EnrichedPost):
        """Test published_on_date computed field"""
        date_str = sample_enriched_post.published_on_date
        assert "Published on" in date_str

    def test_image_path_computed_field(self, sample_enriched_post: EnrichedPost):
        """Test image_path computed field"""
        # Should fall back to logo since sample_post has no image
        assert sample_enriched_post.image_path == "assets/logo.jpg"


class TestNow:
    """Tests for Now model"""

    def test_now_creation_valid(self):
        """Test creating a valid Now post"""
        now = Now(
            post_date=date(2025, 10, 28),
            content="<p>What I'm doing now</p>",
        )

        assert now.post_date == date(2025, 10, 28)
        assert now.content == "<p>What I'm doing now</p>"

    def test_now_missing_required_field(self):
        """Test that missing required fields raise validation error"""
        with pytest.raises(ValidationError) as exc_info:
            Now(
                post_date=date(2025, 10, 28),
                # Missing content
            )
        assert "content" in str(exc_info.value)

    def test_published_datetime_iso(self):
        """Test ISO 8601 datetime for Now posts"""
        now = Now(
            post_date=date(2025, 10, 28),
            content="<p>Content</p>",
        )
        assert now.published_datetime_iso == "2025-10-28T00:00:00Z"

    def test_get_date_formatted_en(self, sample_config: BoumWaveConfig):
        """Test formatted date for Now posts in English"""
        now = Now(
            post_date=date(2025, 10, 28),
            content="<p>Content</p>",
        )
        date_str = now.get_date_formatted(sample_config)
        # Should use first language (en)
        assert "October" in date_str or "28" in date_str

    def test_get_date_formatted_fallback_to_en(self):
        """Test formatted date falls back to English when no languages configured"""
        from boumwave.config import (
            BoumWaveConfig,
            PathsConfig,
            SiteConfig,
            Translations,
        )

        config = BoumWaveConfig(
            paths=PathsConfig(
                template_folder="templates",
                content_folder="content",
                output_folder="posts",
                post_template="post.html",
                link_template="link.html",
                index_template="index.html",
                sitemap_template="sitemap.xml",
            ),
            site=SiteConfig(
                languages=[],  # Empty languages list
                site_url="https://example.com",
                logo_path="logo.jpg",
                date_format="long",
                posts_start_marker="<!-- POSTS_START -->",
                posts_end_marker="<!-- POSTS_END -->",
                sitemap_start_marker="<!-- SITEMAP_START -->",
                sitemap_end_marker="<!-- SITEMAP_END -->",
                translations={},
            ),
        )

        now = Now(
            post_date=date(2025, 10, 28),
            content="<p>Content</p>",
        )
        date_str = now.get_date_formatted(config)
        # Should fall back to English
        assert "October" in date_str or "28" in date_str
