"""Metadata extraction and meta tag generation"""

from pathlib import Path

import markdown
from bs4 import BeautifulSoup

from boumwave.models import Post


def extract_description(markdown_content: str, max_length: int = 155) -> str:
    """
    Extract a description from markdown content.
    Ignores headings (H1-H6) and takes the first paragraph of text.

    Args:
        markdown_content: Markdown content (without front matter)
        max_length: Maximum length for description (default: 155)

    Returns:
        Description truncated properly without cutting words
    """
    # Convert markdown to HTML
    html = markdown.markdown(markdown_content)

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Remove all headings (h1, h2, h3, etc.)
    for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        heading.decompose()

    # Extract clean text
    text = soup.get_text(separator=" ", strip=True)

    # Truncate to max_length without cutting a word
    if len(text) <= max_length:
        return text

    truncated = text[:max_length]
    last_space = truncated.rfind(" ")

    if last_space > 0:
        truncated = truncated[:last_space]

    return truncated + "..."


def extract_first_image(html_content: str) -> Path | None:
    """
    Extract the first image from HTML content.

    Args:
        html_content: Rendered HTML content

    Returns:
        Path to the first image found, or None if no image exists
    """
    soup = BeautifulSoup(html_content, "html.parser")
    img_tag = soup.find("img")

    if img_tag and img_tag.get("src"):
        return Path(img_tag["src"])

    return None


def generate_meta_tags(
    post: Post, full_url: str, image_path: Path, description: str
) -> str:
    """
    Generate all meta tags for SEO and social media.

    Args:
        post: Validated Post model
        full_url: Complete URL of the post
        image_path: Path to the image for social media
        description: SEO description (155 characters extracted from content)

    Returns:
        HTML string with all meta tags
    """
    meta_tags = f"""    <!-- SEO -->
    <meta name="description" content="{description}">

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{post.title}">
    <meta property="og:description" content="{description}">
    <meta property="og:url" content="{full_url}">
    <meta property="og:image" content="{image_path}">
    <meta property="og:locale" content="{post.lang}">
    <meta property="article:published_time" content="{post.published_datetime_iso}">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{post.title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{image_path}">"""

    return meta_tags


def inject_meta_tags_and_canonical(
    html: str, meta_tags: str, canonical_url: str
) -> str:
    """
    Inject meta tags and canonical link into the HTML <head>.

    Args:
        html: Complete HTML from user template
        meta_tags: Generated meta tags HTML
        canonical_url: Canonical URL for the post

    Returns:
        HTML with injected meta tags and canonical link

    Raises:
        ValueError: If no <head> tag is found in the HTML
    """
    soup = BeautifulSoup(html, "html.parser")
    head = soup.find("head")

    if not head:
        raise ValueError("No <head> tag found in template")

    # Create and insert canonical link
    canonical_tag = soup.new_tag("link", rel="canonical", href=canonical_url)

    # Find charset meta tag to insert canonical after it
    charset_meta = head.find("meta", charset=True)
    if charset_meta:
        charset_meta.insert_after(canonical_tag)
    else:
        # If no charset, insert at the beginning of head
        head.insert(0, canonical_tag)

    # Parse and append meta tags
    meta_soup = BeautifulSoup(meta_tags, "html.parser")
    for tag in meta_soup:
        if tag.name:  # Skip text nodes
            head.append(tag)

    return soup.prettify()
