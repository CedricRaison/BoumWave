"""Scaffold command: creates the folder structure based on boumwave.toml"""

import sys
import tomllib
from pathlib import Path


def scaffold_command() -> None:
    """
    Scaffold command: creates the folder structure based on boumwave.toml.
    """
    config_file = Path("boumwave.toml")

    # Check if config file exists
    if not config_file.exists():
        print("Error: boumwave.toml not found.", file=sys.stderr)
        print("Run 'bw init' first to create the configuration file.", file=sys.stderr)
        sys.exit(1)

    # Read the configuration file
    try:
        with open(config_file, "rb") as f:
            config = tomllib.load(f)
    except Exception as e:
        print(f"Error reading configuration file: {e}", file=sys.stderr)
        sys.exit(1)

    # Get folder paths from config
    paths_config = config.get("paths", {})
    template_folder = paths_config.get("template_folder", "templates")
    content_folder = paths_config.get("content_folder", "content")
    output_folder = paths_config.get("output_folder", "posts")

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
