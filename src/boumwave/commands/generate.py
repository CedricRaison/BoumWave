"""Generate HTML from markdown posts"""

import sys
from pathlib import Path

from boumwave.config import BoumWaveConfig, load_config
from boumwave.exceptions import BoumWaveError, EnvironmentValidationError
from boumwave.generation import (
    extract_description,
    extract_first_image,
    find_post_files,
    generate_seo_tags,
    inject_meta_tags_and_canonical,
    parse_post_file,
    render_markdown,
    render_template,
    update_index,
)
from boumwave.models import EnrichedPost


def validate_environment(config: BoumWaveConfig, post_name: str) -> None:
    """
    Validate the environment before generating posts.
    Checks that all required files and folders exist.

    Args:
        config: BoumWave configuration
        post_name: Name of the post folder to generate

    Raises:
        EnvironmentValidationError: If any validation fails
    """
    errors = []

    # 1. Check logo exists
    logo_path = Path(config.site.logo_path)
    if not logo_path.exists():
        errors.append(f"Logo file not found: {logo_path}")
        errors.append("  Check 'logo_path' in boumwave.toml")

    # 2. Check template folder exists
    template_folder = Path(config.paths.template_folder)
    if not template_folder.exists():
        errors.append(f"Template folder not found: {template_folder}")
        errors.append("  Run 'bw scaffold' to create it")

    # 3. Check post template exists
    post_template_path = template_folder / config.paths.post_template
    if not post_template_path.exists():
        errors.append(f"Post template not found: {post_template_path}")
        errors.append("  Run 'bw scaffold' to create it")

    # 4. Check link template exists
    link_template_path = template_folder / config.paths.link_template
    if not link_template_path.exists():
        errors.append(f"Link template not found: {link_template_path}")
        errors.append("  Run 'bw scaffold' to create it")

    # 5. Check index.html exists
    index_path = Path(config.paths.index_template)
    if not index_path.exists():
        errors.append(f"Index file not found: {index_path}")
        errors.append("  Run 'bw scaffold' to create it")

    # 6. Check markers exist in index.html (only if file exists)
    if index_path.exists():
        try:
            index_content = index_path.read_text(encoding="utf-8")
            start_marker = config.site.posts_start_marker
            end_marker = config.site.posts_end_marker

            if start_marker not in index_content:
                errors.append(f"Start marker not found in {index_path}")
                errors.append(f"  Expected: {start_marker}")
                errors.append(
                    "  Add this marker where you want the post list to appear"
                )

            if end_marker not in index_content:
                errors.append(f"End marker not found in {index_path}")
                errors.append(f"  Expected: {end_marker}")
                errors.append("  Add this marker where you want the post list to end")
        except Exception as e:
            errors.append(f"Could not read index file: {e}")

    # 7. Check post folder exists
    content_folder = Path(config.paths.content_folder)
    post_folder = content_folder / post_name
    if not post_folder.exists():
        errors.append(f"Post folder not found: {post_folder}")
        errors.append(f"  Expected location: {post_folder}")
        errors.append(f"  Run 'bw new_post \"{post_name}\"' to create it")
    elif not post_folder.is_dir():
        errors.append(f"Not a directory: {post_folder}")

    # If any errors, raise exception with all errors
    if errors:
        raise EnvironmentValidationError(["Environment validation failed\n"] + errors)


def generate(post_name: str) -> None:
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
    validate_environment(config, post_name)

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

        # 5. Create EnrichedPost model (URLs are computed automatically)
        enriched_post = EnrichedPost(
            post=post,
            description=description,
            image=image_path,
            content_html=content_html,
            config=config,
        )

        # 6. Render user template
        template_path = Path(config.paths.template_folder) / config.paths.post_template
        rendered_html = render_template(template_path, enriched_post)

        # 7. Generate SEO tags (meta tags + JSON-LD)
        seo_tags = generate_seo_tags(enriched_post)

        # 8. Inject SEO tags and canonical into HTML
        final_html = inject_meta_tags_and_canonical(
            rendered_html, seo_tags, enriched_post.full_url
        )

        # 9. Write output file
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
    update_index(config)
    print("✓ Updated index.html with post list")
