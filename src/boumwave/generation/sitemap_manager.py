"""Sitemap.xml management for URL generation"""

from datetime import date
from pathlib import Path

from boumwave.config import get_config
from boumwave.exceptions import FileCreationError
from boumwave.generation.parsers import collect_all_posts
from boumwave.models import Post


def generate_sitemap_urls(posts: list[Post]) -> str:
    """
    Generate sitemap XML for index page and all posts.

    Args:
        posts: List of Post objects

    Returns:
        XML string with all sitemap URLs (always includes index page)
    """
    config = get_config()
    # Start with index page URL
    today = date.today().isoformat()
    site_url = config.site.site_url_base

    urls = []

    # Index page
    urls.append(
        f"""    <url>
        <loc>{site_url}/</loc>
        <lastmod>{today}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>"""
    )

    # Sort posts by date, most recent first
    sorted_posts = sorted(posts, key=lambda p: p.published_date, reverse=True)

    # Generate URL for each post
    for post in sorted_posts:
        full_url = post.get_full_url(config)
        lastmod = post.published_date.isoformat()

        urls.append(
            f"""    <url>
        <loc>{full_url}</loc>
        <lastmod>{lastmod}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>"""
        )

    return "\n".join(urls)


def update_sitemap() -> None:
    """
    Update sitemap.xml with the complete list of URLs (index + blog posts).

    This function:
    1. Reads the sitemap.xml file
    2. Collects all posts from content folder
    3. Generates XML for index page and all post URLs
    4. Replaces content between markers
    5. Saves the updated sitemap.xml

    Raises:
        FileCreationError: If sitemap cannot be written

    Note:
        Assumes environment has been validated (sitemap.xml and markers exist).
    """
    config = get_config()
    sitemap_path = Path(config.paths.sitemap_template)
    start_marker = config.site.sitemap_start_marker
    end_marker = config.site.sitemap_end_marker

    # Read sitemap.xml
    sitemap_content = sitemap_path.read_text(encoding="utf-8")

    # Collect all posts (excludes future posts)
    posts = collect_all_posts()

    # Generate sitemap URLs XML (always includes index page, even if no posts)
    sitemap_urls_xml = generate_sitemap_urls(posts)

    # Replace content between markers
    start_pos = sitemap_content.find(start_marker)
    end_pos = sitemap_content.find(end_marker)

    # Build new content: before marker + marker + new URLs + marker + after marker
    new_content = (
        sitemap_content[: start_pos + len(start_marker)]
        + "\n"
        + sitemap_urls_xml
        + "\n"
        + sitemap_content[end_pos:]
    )

    # Write updated sitemap.xml
    try:
        sitemap_path.write_text(new_content, encoding="utf-8")
    except Exception as e:
        raise FileCreationError(
            message=f"Error writing sitemap file '{sitemap_path}': {e}",
            hint="Check file permissions and disk space",
        ) from e
