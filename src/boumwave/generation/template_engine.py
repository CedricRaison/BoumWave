"""Jinja2 template rendering"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from jinja2 import TemplateNotFound as Jinja2TemplateNotFound

from boumwave.exceptions import TemplateNotFoundError, TemplateRenderError
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
        TemplateNotFoundError: If template file is not found
        TemplateRenderError: If rendering fails
    """
    # Setup Jinja2 environment
    template_dir = template_path.parent
    template_name = template_path.name

    try:
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_name)
    except Jinja2TemplateNotFound:
        raise TemplateNotFoundError(
            message=f"Template file not found: {template_path}",
            hint="Run 'bw scaffold' to create it",
        )
    except Exception as e:
        raise TemplateRenderError(
            message=f"Error loading template '{template_path}': {e}",
            hint="Check that the template file is valid and readable",
        ) from e

    # Prepare context for template
    context = {
        "lang": enriched_post.post.lang,
        "title": enriched_post.post.title,
        "published_datetime_iso": enriched_post.post.published_datetime_iso,
        "published_on_date": enriched_post.published_on_date,
        "content": enriched_post.content_html,
    }

    # Render template
    try:
        return template.render(context)
    except Exception as e:
        raise TemplateRenderError(
            message=f"Error rendering template '{template_path}': {e}",
            hint="Check your template syntax and variables",
        ) from e
