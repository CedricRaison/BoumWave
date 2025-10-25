"""Parser for markdown files with YAML front matter"""

from datetime import date
from pathlib import Path

import frontmatter
from pydantic import ValidationError

from boumwave.config import get_config
from boumwave.exceptions import (
    BoumWaveError,
    FileNotFoundError as BWFileNotFoundError,
    MarkdownParseError,
    PostValidationError,
)
from boumwave.models import Post


def parse_post_file(file_path: Path) -> tuple[Post, str]:
    """
    Parse a markdown file with YAML front matter.

    Args:
        file_path: Path to the markdown file

    Returns:
        Tuple of (Post model, markdown content as string)

    Raises:
        MarkdownParseError: If the file cannot be read
        PostValidationError: If front matter is invalid
    """
    # Read and parse the file
    try:
        post_data = frontmatter.load(str(file_path))
    except Exception as e:
        raise MarkdownParseError(
            message=f"Error reading file '{file_path}': {e}",
            hint="Check that the file exists and is a valid markdown file with YAML front matter",
        ) from e

    # Validate front matter with Pydantic
    try:
        post = Post.model_validate(post_data.metadata)
    except ValidationError as e:
        errors = [f"Invalid front matter in '{file_path}'"]
        for error in e.errors():
            field_name = error["loc"][-1]
            if error["type"] == "missing":
                errors.append(f"  Missing required field: {field_name}")
            else:
                errors.append(f"  Invalid field '{field_name}': {error['msg']}")

        raise PostValidationError(
            errors=errors, hint="Fix the front matter in your markdown file"
        ) from e

    # Return validated post and content
    return post, post_data.content


def find_post_files(post_name: str, content_folder: Path) -> list[Path]:
    """
    Find all markdown files for a given post name.

    Args:
        post_name: Name of the post folder (e.g., "my_amazing_post")
        content_folder: Path to the content folder

    Returns:
        List of Path objects for each language file

    Raises:
        FileNotFoundError: If the post folder doesn't exist or no markdown files found
    """
    post_folder = content_folder / post_name

    # Check if post folder exists
    if not post_folder.exists():
        raise BWFileNotFoundError(
            message=f"Post folder '{post_name}' not found in '{content_folder}'\n"
            f"Expected location: {post_folder}",
            hint=f"Run 'bw new_post \"{post_name}\"' to create it",
        )

    if not post_folder.is_dir():
        raise BWFileNotFoundError(
            message=f"'{post_folder}' is not a directory",
            hint="Check that the path points to a directory, not a file",
        )

    # Find all .md files in the post folder
    md_files = list(post_folder.glob("*.md"))

    if not md_files:
        raise BWFileNotFoundError(
            message=f"No markdown files found in '{post_folder}'",
            hint="Add at least one .md file to the post folder",
        )

    return md_files


def collect_all_posts() -> list[Post]:
    """
    Collect all posts from all subfolders in the content directory.
    Only includes posts with published_date <= today (excludes future posts).

    Returns:
        List of all Post objects found in content folder (excluding future posts)
    """
    config = get_config()
    content_folder = Path(config.paths.content_folder)
    posts = []
    today = date.today()

    # Check if content folder exists
    if not content_folder.exists():
        return posts

    # Iterate through all subdirectories in content folder
    for post_folder in content_folder.iterdir():
        if not post_folder.is_dir():
            continue

        # Find all .md files in this post folder
        md_files = list(post_folder.glob("*.md"))

        # Parse each markdown file
        for md_file in md_files:
            try:
                post, _ = parse_post_file(md_file)
                # Only include posts published today or in the past
                if post.published_date <= today:
                    posts.append(post)
            except BoumWaveError:
                # Skip files that fail to parse (will be caught in generate command)
                continue

    return posts
