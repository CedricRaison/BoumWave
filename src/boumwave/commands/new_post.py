"""New post command: creates a new post with all language files"""

import re
import sys
from datetime import date
from importlib.resources import files
from pathlib import Path

from boumwave.config import load_config
from boumwave.exceptions import (
    BoumWaveError,
    FileAlreadyExistsError,
    FileCreationError,
    ValidationError,
)


def slugify(text: str) -> str:
    """
    Convert text to a URL-friendly slug.

    Args:
        text: Text to convert to slug

    Returns:
        Slugified text (lowercase, hyphens instead of spaces)
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)
    # Remove any character that is not alphanumeric or hyphen
    text = re.sub(r"[^a-z0-9-]", "", text)
    # Remove multiple consecutive hyphens
    text = re.sub(r"-+", "-", text)
    # Remove leading/trailing hyphens
    text = text.strip("-")
    return text


def filesify(text: str) -> str:
    """
    Convert text to a filesystem-friendly name while preserving accents.

    Args:
        text: Text to convert to filesystem name

    Returns:
        Filesified text (lowercase, underscores instead of spaces, preserves Unicode)
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and hyphens with underscores
    text = re.sub(r"[\s-]+", "_", text)
    # Remove only problematic filesystem characters, keeping Unicode letters and digits
    # Remove: / \ : * ? " < > |
    text = re.sub(r'[/\\:*?"<>|]', "", text)
    # Remove multiple consecutive underscores
    text = re.sub(r"_+", "_", text)
    # Remove leading/trailing underscores
    text = text.strip("_")
    return text


def new_post_command(title: str) -> None:
    """
    New post command: creates a new post with files for all configured languages.
    CLI wrapper that handles exceptions.

    Args:
        title: Title of the new post
    """
    try:
        _new_post_impl(title)
    except BoumWaveError as e:
        print(f"Error: {e}", file=sys.stderr)
        if e.hint:
            print(f"Hint: {e.hint}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def _new_post_impl(title: str) -> None:
    """
    New post command implementation: creates a new post with files for all configured languages.
    Raises exceptions instead of calling sys.exit().

    Args:
        title: Title of the new post
    """
    # Load and validate configuration
    config = load_config()

    # Get configuration values
    content_folder = config.paths.content_folder
    output_folder = config.paths.output_folder
    languages = config.site.languages

    # Generate slug from title (for URLs and front matter)
    slug = slugify(title)
    if not slug:
        raise ValidationError(
            errors=["Could not generate a valid slug from the title."],
            hint="Use a title with at least some alphanumeric characters",
        )

    # Generate filesystem-friendly name (for folders and files)
    fs_name = filesify(title)
    if not fs_name:
        raise ValidationError(
            errors=["Could not generate a valid filename from the title."],
            hint="Use a title with at least some valid filesystem characters",
        )

    # Create post directory
    post_dir = Path(content_folder) / fs_name
    if post_dir.exists():
        raise FileAlreadyExistsError(
            message=f"Post directory '{post_dir}' already exists.",
            hint="Use a different title or remove the existing directory",
        )

    try:
        post_dir.mkdir(parents=True, exist_ok=False)
    except Exception as e:
        raise FileCreationError(
            message=f"Error creating post directory: {e}",
            hint="Check file permissions and disk space",
        ) from e

    # Get today's date
    today = date.today().isoformat()

    # Load post template from package resources
    try:
        template_path = files("boumwave").joinpath("templates/post_template.md")
        post_template = template_path.read_text(encoding="utf-8")
    except Exception as e:
        raise FileCreationError(
            message=f"Error loading post template: {e}",
            hint="Check that BoumWave is correctly installed",
        ) from e

    # Create a file for each language
    created_files = []
    for lang in languages:
        filename = f"{fs_name}.{lang}.md"
        file_path = post_dir / filename

        # Fill template with actual values
        content = post_template.format(
            title=title, slug=slug, date=today, lang=lang, output_folder=output_folder
        )

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            created_files.append(filename)
        except Exception as e:
            raise FileCreationError(
                message=f"Error creating file '{filename}': {e}",
                hint="Check file permissions and disk space",
            ) from e

    # Success message
    print(f"✓ Created new post: {fs_name}")
    print(f"  Location: {post_dir}")
    print("  Files created:")
    for filename in created_files:
        print(f"    - {filename}")
    print()
    print("You can now edit these files to write your post in different languages.")

    # Show tip about removing translations only if multiple languages are configured
    if len(languages) > 1:
        print(
            "Tip: You can delete any language file if you don't need that translation."
        )
