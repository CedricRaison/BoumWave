"""Scaffold command: creates the folder structure based on boumwave.toml"""

import sys
from pathlib import Path

from importlib.resources import files

from boumwave.config import load_config


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
            print(f"⚠ Warning: '{folder_path}' already exists, skipping creation.")
        else:
            try:
                path.mkdir(parents=True, exist_ok=False)
                print(f"✓ Created {folder_type} folder: {folder_path}")
                created_folders.append(folder_path)
            except Exception as e:
                print(f"Error creating folder '{folder_path}': {e}", file=sys.stderr)
                sys.exit(1)

    # Copy default post template if it doesn't exist
    template_destination = Path(template_folder) / config.paths.post_template
    template_was_created = False

    if template_destination.exists():
        print(
            f"⚠ Warning: Template '{template_destination}' already exists, skipping copy."
        )
    else:
        try:
            # Get default template from package resources
            template_source = files("boumwave").joinpath("templates/example_post.html")
            template_content = template_source.read_text(encoding="utf-8")

            # Write to destination
            template_destination.write_text(template_content, encoding="utf-8")
            print(f"✓ Created template file: {template_destination}")
            template_was_created = True
        except Exception as e:
            print(
                f"Error creating template file '{template_destination}': {e}",
                file=sys.stderr,
            )
            sys.exit(1)

    print()
    if created_folders or template_was_created:
        print("Scaffold completed! Your project structure is ready.")
    else:
        print("Scaffold completed! All folders already exist.")
