"""Scaffold command: creates the folder structure based on boumwave.toml"""

import sys
from pathlib import Path

from boumwave.models import load_config


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

    print()
    if created_folders:
        print("Scaffold completed! Your project structure is ready.")
    else:
        print("Scaffold completed! All folders already exist.")
