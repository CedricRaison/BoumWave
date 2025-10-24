"""Jinja2 template rendering"""

import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from boumwave.models import EnrichedPost


def render_template(template_path: Path, enriched_post: EnrichedPost) -> str:
    """
    Render a Jinja2 template with post data.

    Args:
        template_path: Path to the Jinja2 template file
        enriched_post: EnrichedPost model with all necessary data

    Returns:
        Rendered HTML string

    Raises:
        SystemExit: If template file is not found or rendering fails
    """
    # Setup Jinja2 environment
    template_dir = template_path.parent
    template_name = template_path.name

    try:
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_name)
    except TemplateNotFound:
        print(f"Error: Template file not found: {template_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading template '{template_path}': {e}", file=sys.stderr)
        sys.exit(1)

    # Prepare context for template
    context = {
        "lang": enriched_post.post.lang,
        "title": enriched_post.post.title,
        "published_date": enriched_post.post.published_date,
        "content": enriched_post.content_html,
    }

    # Render template
    try:
        return template.render(context)
    except Exception as e:
        print(f"Error rendering template '{template_path}': {e}", file=sys.stderr)
        sys.exit(1)
