"""Environment validation for BoumWave commands"""

from pathlib import Path

from boumwave.config import get_config
from boumwave.exceptions import EnvironmentValidationError


def validate_generate_environment(post_name: str) -> None:
    """
    Validate the environment before generating posts.
    Checks that all required files and folders exist for post generation.

    Args:
        post_name: Name of the post folder to generate

    Raises:
        EnvironmentValidationError: If any validation fails
    """
    config = get_config()
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


def validate_sitemap_environment() -> None:
    """
    Validate the environment before generating sitemap.
    Checks that sitemap.xml exists and has the required markers.

    Raises:
        EnvironmentValidationError: If any validation fails
    """
    config = get_config()
    errors = []

    # 1. Check sitemap.xml exists
    sitemap_path = Path(config.paths.sitemap_template)
    if not sitemap_path.exists():
        errors.append(f"Sitemap file not found: {sitemap_path}")
        errors.append("  Run 'bw scaffold' to create it")

    # 2. Check markers exist in sitemap.xml (only if file exists)
    if sitemap_path.exists():
        try:
            sitemap_content = sitemap_path.read_text(encoding="utf-8")
            start_marker = config.site.sitemap_start_marker
            end_marker = config.site.sitemap_end_marker

            if start_marker not in sitemap_content:
                errors.append(f"Start marker not found in {sitemap_path}")
                errors.append(f"  Expected: {start_marker}")
                errors.append(
                    "  Add this marker where you want BoumWave URLs to appear"
                )

            if end_marker not in sitemap_content:
                errors.append(f"End marker not found in {sitemap_path}")
                errors.append(f"  Expected: {end_marker}")
                errors.append("  Add this marker where you want BoumWave URLs to end")
        except Exception as e:
            errors.append(f"Could not read sitemap file: {e}")

    # If any errors, raise exception with all errors
    if errors:
        raise EnvironmentValidationError(
            ["Sitemap environment validation failed\n"] + errors
        )
