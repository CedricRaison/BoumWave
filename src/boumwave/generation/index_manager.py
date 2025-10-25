"""Index.html management for post list generation"""

from pathlib import Path

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

from boumwave.config import get_config
from boumwave.exceptions import (
    FileCreationError,
    TemplateNotFoundError,
    TemplateRenderError,
)
from boumwave.generation.parsers import collect_all_posts
from boumwave.models import Post


def render_post_links(posts: list[Post]) -> str:
    """
    Generate HTML for all post links using the link template.

    Args:
        posts: List of Post objects

    Returns:
        HTML string with all post links, sorted by date (most recent first)

    Raises:
        TemplateNotFoundError: If link template cannot be loaded
        TemplateRenderError: If template rendering fails
    """
    config = get_config()
    # Sort posts by date, most recent first
    sorted_posts = sorted(posts, key=lambda p: p.published_date, reverse=True)

    # Setup Jinja2 environment for link template
    template_folder = Path(config.paths.template_folder)
    template_name = config.paths.link_template

    try:
        env = Environment(loader=FileSystemLoader(template_folder))
        template = env.get_template(template_name)
    except Exception as e:
        raise TemplateNotFoundError(
            message=f"Error loading link template '{template_name}': {e}",
            hint="Run 'bw scaffold' to create it",
        ) from e

    # Render each post link
    rendered_links = []
    for post in sorted_posts:
        # Prepare context for link template
        context = {
            "lang": post.lang,
            "title": post.title,
            "slug": post.slug,
            "relative_url": post.get_relative_url(config),
            "published_datetime_iso": post.published_datetime_iso,
            "published_on_date": post.get_published_on_date(config),
            "image_path": post.get_image_path(config),
        }

        # Render link template
        try:
            rendered_link = template.render(context)
            rendered_links.append(rendered_link)
        except Exception as e:
            raise TemplateRenderError(
                message=f"Error rendering link for post '{post.title}': {e}",
                hint="Check the link template syntax and that all required variables are available",
            ) from e

    # Join all links with newlines
    return "\n".join(rendered_links)


def update_index() -> None:
    """
    Update index.html with the complete list of blog posts.

    This function:
    1. Reads the index.html file
    2. Collects all posts from content folder
    3. Generates HTML for all post links (sorted by date)
    4. Replaces content between markers
    5. Saves the updated index.html

    Note:
        Assumes environment has been validated (index.html and markers exist).
        Should be called after validate_environment() in generate command.
    """
    config = get_config()
    index_path = Path(config.paths.index_template)
    start_marker = config.site.posts_start_marker
    end_marker = config.site.posts_end_marker

    # Read index.html
    index_content = index_path.read_text(encoding="utf-8")

    # Collect all posts
    posts = collect_all_posts()

    # Generate post links HTML
    if posts:
        post_links_html = render_post_links(posts)
    else:
        post_links_html = "<!-- No posts yet -->"

    # Replace content between markers
    start_pos = index_content.find(start_marker)
    end_pos = index_content.find(end_marker)

    # Build new content: before marker + marker + new content + marker + after marker
    new_content = (
        index_content[: start_pos + len(start_marker)]
        + "\n"
        + post_links_html
        + "\n"
        + index_content[end_pos:]
    )

    # Format with BeautifulSoup for proper indentation
    soup = BeautifulSoup(new_content, "html.parser")
    formatted_html = soup.prettify()

    # Write updated index.html
    try:
        index_path.write_text(formatted_html, encoding="utf-8")
    except Exception as e:
        raise FileCreationError(
            message=f"Error writing index file '{index_path}': {e}",
            hint="Check file permissions and disk space",
        ) from e
