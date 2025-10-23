"""Create command: reads a file and displays its content"""

import sys
from pathlib import Path


def create_command(filepath: str) -> None:
    """
    Create command: reads a file and displays its content.

    Args:
        filepath: The path to the file to read
    """
    # Convert path to Path object for easier manipulation
    file_path = Path(filepath)

    # Check if file exists
    if not file_path.exists():
        print(f"Error: The file '{filepath}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Check if it's a file (not a directory)
    if not file_path.is_file():
        print(f"Error: '{filepath}' is not a file.", file=sys.stderr)
        sys.exit(1)

    # Read and display file content
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        print(f"=== Content of {filepath} ===")
        print(content)
        print("=== End of file ===")

    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
