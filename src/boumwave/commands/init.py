"""Init command: creates the boumwave.toml configuration file"""

import sys
from importlib.resources import files
from pathlib import Path

from boumwave.exceptions import BoumWaveError, FileAlreadyExistsError, FileCreationError


def init_command() -> None:
    """
    Init command: creates the boumwave.toml configuration file.
    CLI wrapper that handles exceptions.
    """
    try:
        _init_impl()
    except BoumWaveError as e:
        print(f"Error: {e}", file=sys.stderr)
        if e.hint:
            print(f"Hint: {e.hint}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def _init_impl() -> None:
    """
    Init command implementation: creates the boumwave.toml configuration file.
    Raises exceptions instead of calling sys.exit().
    """
    config_file = Path("boumwave.toml")

    # Check if config file already exists
    if config_file.exists():
        raise FileAlreadyExistsError(
            message="boumwave.toml already exists in this directory.",
            hint="Remove it first if you want to reinitialize.",
        )

    # Load default configuration template from package resources
    try:
        template_path = files("boumwave").joinpath("templates/default_config.toml")
        config_content = template_path.read_text(encoding="utf-8")
    except Exception as e:
        raise FileCreationError(
            message=f"Error loading configuration template: {e}",
            hint="Check that BoumWave is correctly installed",
        ) from e

    # Write the configuration file
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(config_content)

        print("✓ Configuration file 'boumwave.toml' created successfully!")
        print()
        print("You can now edit this file to customize your settings.")
        print("After configuration, run 'bw scaffold' to create the folder structure.")

    except Exception as e:
        raise FileCreationError(
            message=f"Error creating configuration file: {e}",
            hint="Check file permissions and disk space",
        ) from e
