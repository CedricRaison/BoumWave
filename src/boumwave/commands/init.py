"""Init command: creates the boumwave.toml configuration file"""

import sys
from importlib.resources import files
from pathlib import Path


def init_command() -> None:
    """
    Init command: creates the boumwave.toml configuration file.
    """
    config_file = Path("boumwave.toml")

    # Check if config file already exists
    if config_file.exists():
        print("Error: boumwave.toml already exists in this directory.", file=sys.stderr)
        print("Remove it first if you want to reinitialize.", file=sys.stderr)
        sys.exit(1)

    # Load default configuration template from package resources
    try:
        template_path = files("boumwave").joinpath("templates/default_config.toml")
        config_content = template_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error loading configuration template: {e}", file=sys.stderr)
        sys.exit(1)

    # Write the configuration file
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(config_content)

        print("✓ Configuration file 'boumwave.toml' created successfully!")
        print()
        print("You can now edit this file to customize your settings.")
        print("After configuration, run 'bw scaffold' to create the folder structure.")

    except Exception as e:
        print(f"Error creating configuration file: {e}", file=sys.stderr)
        sys.exit(1)
