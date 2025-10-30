"""Unit tests for generation/template_engine.py"""

from pathlib import Path

import pytest

from boumwave.exceptions import TemplateNotFoundError, TemplateRenderError
from boumwave.generation.template_engine import render_template
from boumwave.models import EnrichedPost


class TestRenderTemplate:
    """Tests for render_template"""

    def test_render_template_success(
        self, tmp_path: Path, sample_enriched_post: EnrichedPost
    ):
        """Test rendering a valid template"""
        template_file = tmp_path / "post.html"
        template_file.write_text(
            """<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
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

        result = render_template(template_file, sample_enriched_post)

        assert f'<html lang="{sample_enriched_post.post.lang}">' in result
        assert f"<title>{sample_enriched_post.post.title}</title>" in result
        assert f"<h1>{sample_enriched_post.post.title}</h1>" in result
        assert sample_enriched_post.content_html in result

    def test_render_template_not_found(
        self, tmp_path: Path, sample_enriched_post: EnrichedPost
    ):
        """Test rendering when template file doesn't exist"""
        template_file = tmp_path / "nonexistent.html"

        with pytest.raises(TemplateNotFoundError) as exc_info:
            render_template(template_file, sample_enriched_post)

        assert "Template file not found" in str(exc_info.value)

    def test_render_template_invalid_syntax(
        self, tmp_path: Path, sample_enriched_post: EnrichedPost
    ):
        """Test rendering template with invalid Jinja2 syntax"""
        template_file = tmp_path / "post.html"
        template_file.write_text(
            """<!DOCTYPE html>
<html>
<head>
    <title>{{ title }</title>  <!-- Missing closing brace -->
</head>
<body></body>
</html>
"""
        )

        with pytest.raises(TemplateRenderError) as exc_info:
            render_template(template_file, sample_enriched_post)

        # Can be either "Error loading template" or "Error rendering template"
        assert "Error" in str(exc_info.value) and "template" in str(exc_info.value)

    def test_render_template_undefined_variable(
        self, tmp_path: Path, sample_enriched_post: EnrichedPost
    ):
        """Test rendering template with undefined variable"""
        template_file = tmp_path / "post.html"
        template_file.write_text(
            """<!DOCTYPE html>
<html>
<head>
    <title>{{ undefined_variable }}</title>
</head>
<body></body>
</html>
"""
        )

        # Jinja2 by default doesn't error on undefined variables
        # It just renders them as empty strings
        result = render_template(template_file, sample_enriched_post)
        assert "<title></title>" in result

    def test_render_template_all_variables(
        self, tmp_path: Path, sample_enriched_post: EnrichedPost
    ):
        """Test that all expected variables are available in template"""
        template_file = tmp_path / "post.html"
        template_file.write_text(
            """lang: {{ lang }}
title: {{ title }}
published_datetime_iso: {{ published_datetime_iso }}
published_on_date: {{ published_on_date }}
content: {{ content }}
image_path: {{ image_path }}
"""
        )

        result = render_template(template_file, sample_enriched_post)

        assert f"lang: {sample_enriched_post.post.lang}" in result
        assert f"title: {sample_enriched_post.post.title}" in result
        assert (
            f"published_datetime_iso: {sample_enriched_post.post.published_datetime_iso}"
            in result
        )
        assert f"published_on_date: {sample_enriched_post.published_on_date}" in result
        assert f"content: {sample_enriched_post.content_html}" in result
        assert f"image_path: {sample_enriched_post.image_path}" in result

    def test_render_template_with_conditionals(
        self, tmp_path: Path, sample_enriched_post: EnrichedPost
    ):
        """Test template with Jinja2 conditionals"""
        template_file = tmp_path / "post.html"
        template_file.write_text(
            """{% if lang == "en" %}
English content
{% else %}
Other language
{% endif %}
"""
        )

        result = render_template(template_file, sample_enriched_post)

        if sample_enriched_post.post.lang == "en":
            assert "English content" in result
        else:
            assert "Other language" in result
