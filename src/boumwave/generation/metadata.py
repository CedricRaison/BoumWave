"""Metadata extraction and meta tag generation"""

import html
import json

import markdown
from bs4 import BeautifulSoup

from boumwave.exceptions import TemplateError
from boumwave.models import EnrichedPost


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


def generate_meta_tags(enriched_post: EnrichedPost) -> str:
    """
    Generate Open Graph and Twitter Card meta tags.

    Args:
        enriched_post: EnrichedPost with all necessary metadata

    Returns:
        HTML string with meta tags
    """
    post = enriched_post.post

    # Escape HTML special characters in user-provided content
    title = html.escape(post.title, quote=True)
    description = html.escape(enriched_post.description, quote=True)

    # Build full image URL (site_url + image_path)
    image_url = f"{enriched_post.config.site.site_url_base}/{enriched_post.image_path}"

    meta_tags = f"""    <!-- SEO -->
    <meta name="description" content="{description}">

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:url" content="{enriched_post.full_url}">
    <meta property="og:image" content="{image_url}">
    <meta property="og:locale" content="{post.lang}">
    <meta property="article:published_time" content="{post.published_datetime_iso}">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{image_url}">"""

    return meta_tags


def generate_json_ld(enriched_post: EnrichedPost) -> str:
    """
    Generate JSON-LD structured data for SEO.

    Args:
        enriched_post: EnrichedPost with all necessary metadata

    Returns:
        JSON-LD script tag as string
    """
    post = enriched_post.post

    # Build full image URL (site_url + image_path)
    image_url = f"{enriched_post.config.site.site_url_base}/{enriched_post.image_path}"

    json_ld_data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "datePublished": post.published_datetime_iso,
        "url": enriched_post.full_url,
        "image": image_url,
        "description": enriched_post.description,
        "inLanguage": post.lang,
    }

    json_str = json.dumps(json_ld_data, ensure_ascii=False, indent=2)

    return f'    <script type="application/ld+json">\n{json_str}\n    </script>'


def generate_seo_tags(enriched_post: EnrichedPost) -> str:
    """
    Generate all SEO elements (meta tags + JSON-LD).

    Args:
        enriched_post: EnrichedPost with all necessary metadata

    Returns:
        Combined HTML string with meta tags and JSON-LD script
    """
    meta_tags = generate_meta_tags(enriched_post)
    json_ld = generate_json_ld(enriched_post)

    return meta_tags + "\n\n" + json_ld


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
        TemplateError: If no <head> tag is found in the HTML
    """
    soup = BeautifulSoup(html, "html.parser")
    head = soup.find("head")

    if not head:
        raise TemplateError(
            message="No <head> tag found in template",
            hint="Add a <head> section to your HTML template",
        )

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
