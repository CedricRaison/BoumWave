"""Unit tests for generation/metadata.py"""

import pytest
from bs4 import BeautifulSoup

from boumwave.exceptions import TemplateError
from boumwave.generation.metadata import (
    extract_description,
    generate_json_ld,
    generate_meta_tags,
    generate_seo_tags,
    inject_meta_tags_and_canonical,
)
from boumwave.models import EnrichedPost


class TestExtractDescription:
    """Tests for extract_description"""

    def test_extract_description_simple(self):
        """Test extracting description from simple markdown"""
        markdown = "# Title\n\nThis is a paragraph that should be extracted."
        description = extract_description(markdown)

        assert "This is a paragraph" in description
        assert "Title" not in description  # Headings should be ignored

    def test_extract_description_max_length(self):
        """Test description is truncated to max length"""
        long_text = "a" * 200
        markdown = f"# Title\n\n{long_text}"
        description = extract_description(markdown, max_length=100)

        assert len(description) <= 103  # 100 + "..."
        assert description.endswith("...")

    def test_extract_description_word_boundary(self):
        """Test description is truncated at word boundary"""
        markdown = "# Title\n\nThis is a very long paragraph with many words that should be truncated at a word boundary and not in the middle of a word."
        description = extract_description(markdown, max_length=50)

        # Should end with "..." and not cut in middle of word
        assert description.endswith("...")
        # Last word before "..." should be complete
        words = description[:-3].strip().split()
        assert all(len(word) > 0 for word in words)

    def test_extract_description_ignores_headings(self):
        """Test that all heading levels are ignored"""
        markdown = """
# H1
## H2
### H3
#### H4
##### H5
###### H6

This is the first paragraph.
"""
        description = extract_description(markdown)

        assert "H1" not in description
        assert "H2" not in description
        assert "H3" not in description
        assert "This is the first paragraph" in description

    def test_extract_description_empty_content(self):
        """Test extracting from empty content"""
        description = extract_description("")
        assert description == ""

    def test_extract_description_only_headings(self):
        """Test extracting when content has only headings"""
        markdown = "# Title\n## Subtitle\n### Another heading"
        description = extract_description(markdown)

        assert description == ""


class TestGenerateMetaTags:
    """Tests for generate_meta_tags"""

    def test_generate_meta_tags(self, sample_enriched_post: EnrichedPost):
        """Test generating meta tags"""
        meta_tags = generate_meta_tags(sample_enriched_post)

        assert '<meta name="description"' in meta_tags
        assert sample_enriched_post.description in meta_tags
        assert '<meta property="og:type" content="article">' in meta_tags
        assert f'<meta property="og:title" content="{sample_enriched_post.post.title}">' in meta_tags
        assert f'<meta property="og:url" content="{sample_enriched_post.full_url}">' in meta_tags
        assert '<meta name="twitter:card" content="summary_large_image">' in meta_tags


class TestGenerateJsonLd:
    """Tests for generate_json_ld"""

    def test_generate_json_ld(self, sample_enriched_post: EnrichedPost):
        """Test generating JSON-LD structured data"""
        json_ld = generate_json_ld(sample_enriched_post)

        assert '<script type="application/ld+json">' in json_ld
        assert '"@context": "https://schema.org"' in json_ld
        assert '"@type": "BlogPosting"' in json_ld
        assert f'"headline": "{sample_enriched_post.post.title}"' in json_ld
        assert f'"url": "{sample_enriched_post.full_url}"' in json_ld
        assert f'"inLanguage": "{sample_enriched_post.post.lang}"' in json_ld


class TestGenerateSeoTags:
    """Tests for generate_seo_tags"""

    def test_generate_seo_tags(self, sample_enriched_post: EnrichedPost):
        """Test generating combined SEO tags"""
        seo_tags = generate_seo_tags(sample_enriched_post)

        # Should contain both meta tags and JSON-LD
        assert '<meta name="description"' in seo_tags
        assert '<meta property="og:' in seo_tags
        assert '<script type="application/ld+json">' in seo_tags
        assert '"@type": "BlogPosting"' in seo_tags


class TestInjectMetaTagsAndCanonical:
    """Tests for inject_meta_tags_and_canonical"""

    def test_inject_into_valid_html(self):
        """Test injecting meta tags into valid HTML"""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Test</title>
</head>
<body>
    <p>Content</p>
</body>
</html>
"""
        meta_tags = '<meta name="description" content="Test description">'
        canonical_url = "https://example.com/test"

        result = inject_meta_tags_and_canonical(html, meta_tags, canonical_url)

        assert '<link href="https://example.com/test" rel="canonical"/>' in result
        assert '<meta content="Test description" name="description"/>' in result

    def test_inject_no_head_tag(self):
        """Test error when HTML has no <head> tag"""
        html = "<body><p>Content</p></body>"
        meta_tags = '<meta name="description" content="Test">'
        canonical_url = "https://example.com/test"

        with pytest.raises(TemplateError) as exc_info:
            inject_meta_tags_and_canonical(html, meta_tags, canonical_url)

        assert "No <head> tag found" in str(exc_info.value)

    def test_inject_canonical_after_charset(self):
        """Test canonical link is inserted after charset meta"""
        html = """<html>
<head>
    <meta charset="UTF-8">
    <title>Test</title>
</head>
<body></body>
</html>
"""
        meta_tags = ""
        canonical_url = "https://example.com/test"

        result = inject_meta_tags_and_canonical(html, meta_tags, canonical_url)

        # Parse to check order
        soup = BeautifulSoup(result, "html.parser")
        head = soup.find("head")
        children = [c for c in head.children if c.name]

        # Find positions
        charset_pos = next(
            i for i, c in enumerate(children) if c.name == "meta" and c.get("charset")
        )
        canonical_pos = next(
            i for i, c in enumerate(children) if c.name == "link" and c.get("rel") == ["canonical"]
        )

        # Canonical should be after charset
        assert canonical_pos > charset_pos

    def test_inject_canonical_at_beginning_no_charset(self):
        """Test canonical link at beginning when no charset"""
        html = """<html>
<head>
    <title>Test</title>
</head>
<body></body>
</html>
"""
        meta_tags = ""
        canonical_url = "https://example.com/test"

        result = inject_meta_tags_and_canonical(html, meta_tags, canonical_url)

        soup = BeautifulSoup(result, "html.parser")
        head = soup.find("head")
        first_tag = next(c for c in head.children if c.name)

        # First tag should be canonical
        assert first_tag.name == "link"
        assert first_tag.get("rel") == ["canonical"]
