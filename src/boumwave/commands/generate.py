"""Generate HTML from markdown posts"""

import sys
from pathlib import Path

from boumwave.config import load_config
from boumwave.exceptions import BoumWaveError
from boumwave.generation import (
    extract_description,
    find_post_files,
    generate_seo_tags,
    inject_meta_tags_and_canonical,
    parse_post_file,
    render_markdown,
    render_template,
    update_index,
)
from boumwave.models import EnrichedPost
from boumwave.validation import validate_generate_environment


def generate_command(post_name: str) -> None:
    """
    Generate HTML for a given post in all available languages.
    CLI wrapper that handles exceptions.

    Args:
        post_name: Name of the post folder (e.g., "my_amazing_post")
    """
    try:
        _generate_impl(post_name)
    except BoumWaveError as e:
        print(f"Error: {e}", file=sys.stderr)
        if e.hint:
            print(f"Hint: {e.hint}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def _generate_impl(post_name: str) -> None:
    """
    Generate HTML for a given post in all available languages.
    Raises exceptions instead of calling sys.exit().

    Args:
        post_name: Name of the post folder (e.g., "my_amazing_post")
    """
    # Load configuration
    config = load_config()

    # Validate environment before doing any work
    validate_generate_environment(post_name)

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

        # 4. Create EnrichedPost model (URLs and image_path are computed automatically)
        enriched_post = EnrichedPost(
            post=post,
            description=description,
            content_html=content_html,
            config=config,
        )

        # 5. Render user template
        template_path = Path(config.paths.template_folder) / config.paths.post_template
        rendered_html = render_template(template_path, enriched_post)

        # 6. Generate SEO tags (meta tags + JSON-LD)
        seo_tags = generate_seo_tags(enriched_post)

        # 7. Inject SEO tags and canonical into HTML
        final_html = inject_meta_tags_and_canonical(
            rendered_html, seo_tags, enriched_post.full_url
        )

        # 8. Write output file
        output_path = (
            Path(config.paths.output_folder) / post.lang / post.slug / "index.html"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(final_html, encoding="utf-8")

        print(f"  ✓ Generated: {output_path}")
        generated_count += 1

    print(f"\n✓ Successfully generated {generated_count} post(s) for '{post_name}'")

    # Update index.html with all posts
    print("\nUpdating index.html...")
    update_index()
    print("✓ Updated index.html with post list")
