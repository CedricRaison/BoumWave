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

    # Get the templates folder path from config
    templates_folder = config.get("paths", {}).get("templates_folder", "templates")
    templates_path = Path(templates_folder)

    # Create the folder if it doesn't exist
    if templates_path.exists():
        print(f"⚠ Warning: '{templates_folder}' already exists, skipping creation.")
    else:
        try:
            templates_path.mkdir(parents=True, exist_ok=False)
            print(f"✓ Created folder: {templates_folder}")
        except Exception as e:
            print(f"Error creating folder '{templates_folder}': {e}", file=sys.stderr)
            sys.exit(1)

    print()
    print("Scaffold completed! Your project structure is ready.")
