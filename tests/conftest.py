"""Shared fixtures for all tests"""

from datetime import date
from pathlib import Path

import pytest

from boumwave.config import (
    BoumWaveConfig,
    DateFormat,
    PathsConfig,
    SiteConfig,
    Translations,
)
from boumwave.models import EnrichedPost, Post


@pytest.fixture(autouse=True)
def reset_config_cache():
    """Reset global config cache before each test"""
    import boumwave.config
    boumwave.config._config = None
    yield
    boumwave.config._config = None


@pytest.fixture
def sample_translations() -> dict[str, Translations]:
    """Sample translations for English and French"""
    return {
        "en": Translations(published_on="Published on"),
        "fr": Translations(published_on="Publié le"),
    }


@pytest.fixture
def sample_paths_config() -> PathsConfig:
    """Sample paths configuration"""
    return PathsConfig(
        template_folder="templates",
        content_folder="content",
        output_folder="posts",
        post_template="post.html",
        link_template="link.html",
        index_template="index.html",
        sitemap_template="sitemap.xml",
        now_folder="now",
        now_template="now.html",
        now_index_template="now_index.html",
    )


@pytest.fixture
def sample_site_config(sample_translations: dict[str, Translations]) -> SiteConfig:
    """Sample site configuration"""
    return SiteConfig(
        languages=["en", "fr"],
        site_url="https://example.com",
        logo_path="assets/logo.jpg",
        date_format=DateFormat.LONG,
        posts_start_marker="<!-- POSTS_START -->",
        posts_end_marker="<!-- POSTS_END -->",
        sitemap_start_marker="<!-- SITEMAP_START -->",
        sitemap_end_marker="<!-- SITEMAP_END -->",
        now_start_marker="<!-- NOW_START -->",
        now_end_marker="<!-- NOW_END -->",
        translations=sample_translations,
    )


@pytest.fixture
def sample_config(
    sample_paths_config: PathsConfig, sample_site_config: SiteConfig
) -> BoumWaveConfig:
    """Sample complete BoumWave configuration"""
    return BoumWaveConfig(paths=sample_paths_config, site=sample_site_config)


@pytest.fixture
def sample_post() -> Post:
    """Sample blog post"""
    return Post(
        title="My Awesome Post",
        slug="my-awesome-post",
        published_date=date(2025, 10, 23),
        lang="en",
    )


@pytest.fixture
def sample_post_fr() -> Post:
    """Sample French blog post"""
    return Post(
        title="Mon super article",
        slug="mon-super-article",
        published_date=date(2025, 10, 24),
        lang="fr",
    )


@pytest.fixture
def sample_enriched_post(sample_post: Post, sample_config: BoumWaveConfig) -> EnrichedPost:
    """Sample enriched post with HTML content"""
    return EnrichedPost(
        post=sample_post,
        description="This is a test post description that should be under 155 characters for SEO purposes.",
        content_html="<h1>My Awesome Post</h1><p>This is the content.</p>",
        config=sample_config,
    )


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Path:
    """Create a temporary project directory with standard structure"""
    # Create directories
    (tmp_path / "templates").mkdir()
    (tmp_path / "content").mkdir()
    (tmp_path / "posts").mkdir()

    # Create a sample logo
    logo_path = tmp_path / "assets" / "logo.jpg"
    logo_path.parent.mkdir()
    logo_path.write_text("fake image data")

    return tmp_path


@pytest.fixture
def sample_config_file(temp_project_dir: Path, sample_config: BoumWaveConfig) -> Path:
    """Create a sample boumwave.toml file"""
    config_path = temp_project_dir / "boumwave.toml"

    config_content = """[paths]
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

    config_path.write_text(config_content)
    return config_path


@pytest.fixture
def sample_markdown_post() -> str:
    """Sample markdown post content with front matter"""
    return """---
title: "Test Post"
slug: "test-post"
published_date: 2025-10-23
lang: en
---

# Test Post

This is a test post with **markdown** content.

## Section 1

Some content here.
"""


@pytest.fixture
def sample_html_template() -> str:
    """Sample HTML template for posts"""
    return """<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
</head>
<body>
    <article>
        <h1>{{ title }}</h1>
        <time datetime="{{ published_datetime_iso }}">{{ published_on_date }}</time>
        <div>{{ content }}</div>
    </article>
</body>
</html>
"""


@pytest.fixture
def sample_link_template() -> str:
    """Sample HTML template for post links"""
    return """<li>
    <a href="{{ relative_url }}">{{ title }}</a>
    <time datetime="{{ published_datetime_iso }}">{{ published_on_date }}</time>
</li>
"""


@pytest.fixture
def sample_index_html() -> str:
    """Sample index.html with post markers"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Blog</title>
</head>
<body>
    <h1>My Blog</h1>
    <ul>
        <!-- POSTS_START -->
        <!-- POSTS_END -->
    </ul>
</body>
</html>
"""
