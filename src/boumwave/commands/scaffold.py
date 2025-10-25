"""Scaffold command: creates the folder structure based on boumwave.toml"""

import sys
from pathlib import Path

from importlib.resources import files

from boumwave.config import load_config


def _copy_template_file(
    source_filename: str, destination_path: Path, file_type: str = "file"
) -> bool:
    """
    Copy a template file from package resources to destination.

    Args:
        source_filename: Name of the file in the templates/ directory (e.g., "example_post.html")
        destination_path: Path where the file should be copied
        file_type: Description of the file type for user messages (e.g., "template file", "index file")

    Returns:
        True if file was created, False if it already existed

    Raises:
        SystemExit: If an error occurs during file creation
    """
    if destination_path.exists():
        print(
            f"Warning: {file_type.capitalize()} '{destination_path}' already exists, skipping copy."
        )
        return False

    try:
        # Get template from package resources
        source = files("boumwave").joinpath(f"templates/{source_filename}")
        content = source.read_text(encoding="utf-8")

        # Write to destination
        destination_path.write_text(content, encoding="utf-8")
        print(f"✓ Created {file_type}: {destination_path}")
        return True
    except Exception as e:
        print(f"Error creating {file_type} '{destination_path}': {e}", file=sys.stderr)
        sys.exit(1)


def scaffold_command() -> None:
    """
    Scaffold command: creates the folder structure based on boumwave.toml.
    """
    # Load and validate configuration
    config = load_config()

    # Get folder paths from config
    template_folder = config.paths.template_folder
    content_folder = config.paths.content_folder
    output_folder = config.paths.output_folder

    folders_to_create = [
        ("template", template_folder),
        ("content", content_folder),
        ("output", output_folder),
    ]

    # Create folders if they don't exist
    created_folders = []
    for folder_type, folder_path in folders_to_create:
        path = Path(folder_path)
        if path.exists():
            print(f"Warning: '{folder_path}' folder already exists, skipping creation.")
        else:
            try:
                path.mkdir(parents=True, exist_ok=False)
                print(f"✓ Created {folder_type} folder: {folder_path}")
                created_folders.append(folder_path)
            except Exception as e:
                print(f"Error creating folder '{folder_path}': {e}", file=sys.stderr)
                sys.exit(1)

    # Copy template files if they don't exist
    files_created = []

    # Post template
    post_template_destination = Path(template_folder) / config.paths.post_template
    files_created.append(
        _copy_template_file(
            "example_post.html", post_template_destination, "template file"
        )
    )

    # Link template
    link_template_destination = Path(template_folder) / config.paths.link_template
    files_created.append(
        _copy_template_file(
            "example_link.html", link_template_destination, "template file"
        )
    )

    # Index file (at project root)
    index_destination = Path(config.paths.index_template)
    files_created.append(
        _copy_template_file("example_index.html", index_destination, "index file")
    )

    if created_folders or any(files_created):
        print("Scaffold completed! Your project structure is ready.")
    else:
        print("Scaffold completed! All folders and files already exist.")
