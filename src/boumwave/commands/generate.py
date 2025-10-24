"""Generate HTML from markdown posts"""

import sys
from pathlib import Path

from boumwave.config import load_config
from boumwave.generation import (
    extract_description,
    extract_first_image,
    find_post_files,
    generate_meta_tags,
    inject_meta_tags_and_canonical,
    parse_post_file,
    render_markdown,
    render_template,
)
from boumwave.models import EnrichedPost


def generate(post_name: str) -> None:
    """
    Generate HTML for a given post in all available languages.

    Args:
        post_name: Name of the post folder (e.g., "my_amazing_post")
    """
    # Load configuration
    config = load_config()

    # Validate that logo file exists
    logo_path = Path(config.site.logo_path)
    if not logo_path.exists():
        print(f"Error: Logo file not found: {logo_path}", file=sys.stderr)
        print("Please check the 'logo_path' setting in boumwave.toml", file=sys.stderr)
        sys.exit(1)

    # Find all markdown files for this post
    content_folder = Path(config.paths.content_folder)
    post_files = find_post_files(post_name, content_folder)

    generated_count = 0

    # Process each language file
    for post_file in post_files:
        print(f"Processing {post_file.name}...")

        # 1. Parse front matter and markdown content
        post, markdown_content = parse_post_file(post_file)

        # 2. Convert markdown to HTML
        content_html = render_markdown(markdown_content)

        # 3. Extract metadata
        description = extract_description(markdown_content)
        first_image = extract_first_image(content_html)

        # 4. Determine image for social media (first image or logo)
        image_path = first_image if first_image else Path(config.site.logo_path)

        # 5. Build URLs
        relative_url = f"/{config.paths.output_folder}/{post.lang}/{post.slug}"
        full_url = f"{config.site.site_url}{relative_url}"

        # 6. Create EnrichedPost model
        enriched_post = EnrichedPost(
            post=post,
            full_url=full_url,
            relative_url=relative_url,
            description=description,
            image=image_path,
            content_html=content_html,
        )

        # 7. Render user template
        template_path = Path(config.paths.template_folder) / config.paths.post_template
        rendered_html = render_template(template_path, enriched_post)

        # 8. Generate meta tags
        meta_tags = generate_meta_tags(post, full_url, image_path, description)

        # 9. Inject meta tags and canonical into HTML
        final_html = inject_meta_tags_and_canonical(rendered_html, meta_tags, full_url)

        # 10. Write output file
        output_path = (
            Path(config.paths.output_folder) / post.lang / post.slug / "index.html"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(final_html, encoding="utf-8")

        print(f"  ✓ Generated: {output_path}")
        generated_count += 1

    print(f"\n✓ Successfully generated {generated_count} post(s) for '{post_name}'")
