"""Parser for markdown files with YAML front matter"""

import sys
from pathlib import Path

import frontmatter
from pydantic import ValidationError

from boumwave.models import Post


def parse_post_file(file_path: Path) -> tuple[Post, str]:
    """
    Parse a markdown file with YAML front matter.

    Args:
        file_path: Path to the markdown file

    Returns:
        Tuple of (Post model, markdown content as string)

    Raises:
        SystemExit: If the file cannot be read or front matter is invalid
    """
    # Read and parse the file
    try:
        post_data = frontmatter.load(str(file_path))
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)

    # Validate front matter with Pydantic
    try:
        post = Post.model_validate(post_data.metadata)
    except ValidationError as e:
        print(f"Error: Invalid front matter in '{file_path}'", file=sys.stderr)
        for error in e.errors():
            field_name = error["loc"][-1]
            if error["type"] == "missing":
                print(f"  Missing required field: {field_name}", file=sys.stderr)
            else:
                print(
                    f"  Invalid field '{field_name}': {error['msg']}", file=sys.stderr
                )
        sys.exit(1)

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
        SystemExit: If the post folder doesn't exist or no markdown files found
    """
    post_folder = content_folder / post_name

    # Check if post folder exists
    if not post_folder.exists():
        print(
            f"Error: Post folder '{post_name}' not found in '{content_folder}'",
            file=sys.stderr,
        )
        print(f"Expected location: {post_folder}", file=sys.stderr)
        sys.exit(1)

    if not post_folder.is_dir():
        print(f"Error: '{post_folder}' is not a directory", file=sys.stderr)
        sys.exit(1)

    # Find all .md files in the post folder
    md_files = list(post_folder.glob("*.md"))

    if not md_files:
        print(f"Error: No markdown files found in '{post_folder}'", file=sys.stderr)
        sys.exit(1)

    return md_files
