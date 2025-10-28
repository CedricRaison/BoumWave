"""Generate Now. posts and update index.html"""

import sys
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

from boumwave.config import load_config
from boumwave.exceptions import (
    BoumWaveError,
    FileCreationError,
    TemplateRenderError,
)
from boumwave.generation.renderers import render_markdown
from boumwave.models import Now
from boumwave.validation import validate_now_environment


def generate_now_command() -> None:
    """
    Generate Now. posts and update index.html with the latest update.
    CLI wrapper that handles exceptions.
    """
    try:
        _generate_now_impl()
    except BoumWaveError as e:
        print(f"Error: {e}", file=sys.stderr)
        if e.hint:
            print(f"Hint: {e.hint}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def _collect_all_now_posts() -> list[Now]:
    """
    Collect all Now. posts from the now_folder.

    Returns:
        List of Now objects, sorted by date (most recent first)

    Raises:
        FileCreationError: If reading files fails

    Note:
        Assumes environment has been validated (now_folder exists and has .md files).
        Should be called after validate_now_environment().
    """
    config = load_config()
    now_folder = Path(config.paths.now_folder)

    # Collect all .md files
    md_files = list(now_folder.glob("*.md"))

    now_posts = []
    for md_file in md_files:
        # Extract date from filename (e.g., "2025-10-28.md")
        try:
            date_str = md_file.stem  # Get filename without extension
            post_date = date.fromisoformat(date_str)
        except ValueError:
            print(
                f"Warning: Skipping '{md_file.name}' - invalid date format. "
                f"Expected format: YYYY-MM-DD.md",
                file=sys.stderr,
            )
            continue

        # Read and convert markdown to HTML
        try:
            markdown_content = md_file.read_text(encoding="utf-8")
            html_content = render_markdown(markdown_content)
        except Exception as e:
            raise FileCreationError(
                message=f"Error reading file '{md_file.name}': {e}",
                hint="Check file permissions and encoding",
            ) from e

        # Create Now object
        now_post = Now(post_date=post_date, content=html_content)
        now_posts.append(now_post)

    # Sort by date, most recent first
    now_posts.sort(key=lambda n: n.post_date, reverse=True)

    return now_posts


def _update_index_with_now(latest_now: Now) -> None:
    """
    Update index.html with the latest Now. post.

    Args:
        latest_now: The most recent Now object to insert

    Raises:
        TemplateRenderError: If template rendering fails
        FileCreationError: If writing to index.html fails

    Note:
        Assumes environment has been validated (all templates and markers exist).
        Should be called after validate_now_environment().
    """
    config = load_config()

    # fix to prevent Astral ty warning
    assert config.paths.now_template is not None
    assert config.paths.now_index_template is not None
    assert config.site.now_start_marker is not None
    assert config.site.now_end_marker is not None
    assert config.paths.now_template is not None

    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(config.paths.template_folder))
    template = env.get_template(config.paths.now_index_template)

    # Prepare context for template
    context = {
        "published_datetime_iso": latest_now.published_datetime_iso,
        "date_formatted": latest_now.get_date_formatted(config),
        "content": latest_now.content,
    }

    # Render template
    try:
        now_html = template.render(context)
    except Exception as e:
        raise TemplateRenderError(
            message=f"Error rendering now_index template: {e}",
            hint="Check the template syntax and that all required variables are available",
        ) from e

    # Read index.html
    index_path = Path(config.paths.index_template)
    index_content = index_path.read_text(encoding="utf-8")

    # Replace content between markers
    start_marker = config.site.now_start_marker
    end_marker = config.site.now_end_marker
    start_pos = index_content.find(start_marker)
    end_pos = index_content.find(end_marker)

    # Build new content: before marker + marker + new content + marker + after marker
    new_content = (
        index_content[: start_pos + len(start_marker)]
        + "\n"
        + now_html
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


def _generate_now_page(now_posts: list[Now]) -> None:
    """
    Generate the now.html page with all Now. posts.

    Args:
        now_posts: List of all Now objects (sorted by date)

    Raises:
        TemplateRenderError: If template rendering fails
        FileCreationError: If writing now.html fails

    Note:
        Assumes environment has been validated (now_template exists).
        Should be called after validate_now_environment().
    """
    config = load_config()

    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(config.paths.template_folder))
    # fix to prevent Astral ty warning
    assert config.paths.now_template is not None
    template = env.get_template(config.paths.now_template)

    # Render template with all Now posts
    context = {
        "now_posts": now_posts,
        "config": config,
    }

    try:
        rendered_html = template.render(context)
    except Exception as e:
        raise TemplateRenderError(
            message=f"Error rendering now template: {e}",
            hint="Check the template syntax and that all required variables are available",
        ) from e

    # Write now.html to project root
    now_output_path = Path(config.paths.now_template)

    try:
        now_output_path.write_text(rendered_html, encoding="utf-8")
    except Exception as e:
        raise FileCreationError(
            message=f"Error writing now file '{now_output_path}': {e}",
            hint="Check file permissions and disk space",
        ) from e


def _generate_now_impl() -> None:
    """
    Generate Now. posts and update index.html with the latest update.
    Raises exceptions instead of calling sys.exit().
    """
    # Validate environment before doing any work
    validate_now_environment()

    # Collect all Now. posts
    print("Collecting Now. posts...")
    now_posts = _collect_all_now_posts()
    print(f"  Found {len(now_posts)} Now. post(s)")

    # Update index.html with latest Now. post
    print("\nUpdating index.html with latest Now. post...")
    latest_now = now_posts[0]  # Already sorted, most recent first
    _update_index_with_now(latest_now)
    print(f"  ✓ Updated index.html with post from {latest_now.post_date.isoformat()}")

    # Generate now.html page
    print("\nGenerating now.html page...")
    _generate_now_page(now_posts)
    print("  ✓ Generated now.html")

    print(f"\n✓ Successfully generated Now. feature with {len(now_posts)} post(s)")
