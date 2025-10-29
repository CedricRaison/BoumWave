"""Integration tests for the complete generation flow"""

from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from boumwave.config import BoumWaveConfig
from boumwave.generation.metadata import extract_description, generate_seo_tags
from boumwave.generation.parsers import parse_post_file
from boumwave.generation.renderers import render_markdown
from boumwave.generation.template_engine import render_template
from boumwave.models import EnrichedPost


class TestGenerationFlow:
    """Integration tests for the complete post generation flow"""

    def test_complete_generation_pipeline(self, tmp_path: Path, sample_config: BoumWaveConfig):
        """Test the complete flow from markdown to HTML with SEO"""
        # 1. Create a markdown file
        post_file = tmp_path / "test_post.md"
        post_file.write_text(
            """---
title: "Integration Test Post"
slug: "integration-test-post"
published_date: 2025-10-25
lang: en
---

# Integration Test Post

This is the first paragraph that will be extracted as the description.

This is the second paragraph with more content.

## Section 1

Some additional content here.
"""
        )

        # 2. Parse the post file
        post, markdown_content = parse_post_file(post_file)

        assert post.title == "Integration Test Post"
        assert post.slug == "integration-test-post"
        assert "# Integration Test Post" in markdown_content

        # 3. Render markdown to HTML
        content_html = render_markdown(markdown_content)

        assert "<h1>Integration Test Post</h1>" in content_html
        assert "<p>This is the first paragraph" in content_html

        # 4. Extract description
        description = extract_description(markdown_content)

        assert "first paragraph" in description
        assert len(description) <= 158  # 155 + "..."

        # 5. Create EnrichedPost
        enriched_post = EnrichedPost(
            post=post,
            description=description,
            content_html=content_html,
            config=sample_config,
        )

        assert enriched_post.relative_url == "/posts/en/integration-test-post"
        assert enriched_post.full_url == "https://example.com/posts/en/integration-test-post"

        # 6. Generate SEO tags
        seo_tags = generate_seo_tags(enriched_post)

        assert '<meta name="description"' in seo_tags
        assert '<meta property="og:title"' in seo_tags
        assert '"@type": "BlogPosting"' in seo_tags

        # 7. Render template
        template_file = tmp_path / "post.html"
        template_file.write_text(
            """<!DOCTYPE html>
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
        )

        final_html = render_template(template_file, enriched_post)

        assert "<title>Integration Test Post</title>" in final_html
        assert '<html lang="en">' in final_html
        assert "<h1>Integration Test Post</h1>" in final_html
        assert enriched_post.content_html in final_html

    def test_multilingual_generation(self, tmp_path: Path, sample_config: BoumWaveConfig):
        """Test generating posts in multiple languages"""
        # Create English post
        en_file = tmp_path / "test_en.md"
        en_file.write_text(
            """---
title: "English Post"
slug: "english-post"
published_date: 2025-10-25
lang: en
---

# English Post

This is content in English.
"""
        )

        # Create French post
        fr_file = tmp_path / "test_fr.md"
        fr_file.write_text(
            """---
title: "Article français"
slug: "article-francais"
published_date: 2025-10-25
lang: fr
---

# Article français

Ceci est du contenu en français.
"""
        )

        # Parse both posts
        en_post, en_content = parse_post_file(en_file)
        fr_post, fr_content = parse_post_file(fr_file)

        assert en_post.lang == "en"
        assert fr_post.lang == "fr"

        # Check URLs are correct for each language
        assert en_post.get_relative_url(sample_config) == "/posts/en/english-post"
        assert fr_post.get_relative_url(sample_config) == "/posts/fr/article-francais"

        # Check date formatting uses correct language
        en_date = en_post.get_published_on_date(sample_config)
        fr_date = fr_post.get_published_on_date(sample_config)

        assert "Published on" in en_date
        assert "Publié le" in fr_date

    def test_generation_with_image(self, tmp_path: Path, sample_config: BoumWaveConfig):
        """Test generation with post image"""
        # Create image file
        image_path = tmp_path / "hero.jpg"
        image_path.write_text("fake image data")

        # Create post with image
        post_file = tmp_path / "test.md"
        post_file.write_text(
            f"""---
title: "Post with Image"
slug: "post-with-image"
published_date: 2025-10-25
lang: en
image_path: {image_path}
---

Content
"""
        )

        post, content = parse_post_file(post_file)

        assert post.image_path == image_path
        assert post.get_image_path(sample_config) == str(image_path)

        # Create enriched post
        enriched_post = EnrichedPost(
            post=post,
            description="Description",
            content_html="<p>Content</p>",
            config=sample_config,
        )

        assert enriched_post.image_path == str(image_path)

        # Generate SEO tags - should use post image
        seo_tags = generate_seo_tags(enriched_post)
        assert str(image_path) in seo_tags

    def test_generation_without_image_uses_logo(
        self, tmp_path: Path, sample_config: BoumWaveConfig
    ):
        """Test generation without post image falls back to logo"""
        post_file = tmp_path / "test.md"
        post_file.write_text(
            """---
title: "Post without Image"
slug: "post-without-image"
published_date: 2025-10-25
lang: en
---

Content
"""
        )

        post, content = parse_post_file(post_file)

        assert post.image_path is None
        assert post.get_image_path(sample_config) == "assets/logo.jpg"

        enriched_post = EnrichedPost(
            post=post,
            description="Description",
            content_html="<p>Content</p>",
            config=sample_config,
        )

        # Should use logo
        assert enriched_post.image_path == "assets/logo.jpg"

        seo_tags = generate_seo_tags(enriched_post)
        assert "assets/logo.jpg" in seo_tags
