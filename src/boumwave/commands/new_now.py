"""New now command: creates a new Now. post for today's date"""

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


def new_now_command() -> None:
    """
    New now command: creates a new Now. post for today's date.
    CLI wrapper that handles exceptions.
    """
    try:
        _new_now_impl()
    except BoumWaveError as e:
        print(f"Error: {e}", file=sys.stderr)
        if e.hint:
            print(f"Hint: {e.hint}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def _new_now_impl() -> None:
    """
    New now command implementation: creates a new Now. post for today's date.
    Raises exceptions instead of calling sys.exit().
    """
    # Load and validate configuration
    config = load_config()

    # Check if Now. feature is enabled
    if not config.paths.now_folder:
        raise ValidationError(
            errors=["The Now. feature is not enabled in your configuration."],
            hint=(
                "To enable it, uncomment the 'now_folder' and 'now_template' lines "
                "in your boumwave.toml file"
            ),
        )

    # Get configuration values
    now_folder = config.paths.now_folder

    # Get today's date
    today = date.today()
    filename = f"{today.isoformat()}.md"

    # Create now folder if it doesn't exist
    now_dir = Path(now_folder)
    try:
        now_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise FileCreationError(
            message=f"Error creating now folder '{now_folder}': {e}",
            hint="Check file permissions and disk space",
        ) from e

    # Check if file already exists
    file_path = now_dir / filename
    if file_path.exists():
        raise FileAlreadyExistsError(
            message=f"A Now. post already exists for today: {filename}",
            hint="Edit the existing file or delete it to create a new one",
        )

    # Load now template from package resources
    try:
        template_path = files("boumwave").joinpath("templates/now_template.md")
        now_template = template_path.read_text(encoding="utf-8")
    except Exception as e:
        raise FileCreationError(
            message=f"Error loading now template: {e}",
            hint="Check that BoumWave is correctly installed",
        ) from e

    # Create the file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(now_template)
    except Exception as e:
        raise FileCreationError(
            message=f"Error creating file '{filename}': {e}",
            hint="Check file permissions and disk space",
        ) from e

    # Success message
    print(f"✓ Created new Now. post: {filename}")
    print(f"  Location: {file_path}")
    print()
    print("You can now edit this file to write your current status update.")
    print("When you're done, run 'bw generate_now' to publish it.")
