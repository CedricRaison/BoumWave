"""CLI entry point for BoumWave"""

import argparse
import sys

from boumwave.commands import create_command, init_command, scaffold_command


def main() -> None:
    """Main entry point for the BoumWave CLI"""

    # Create main parser
    parser = argparse.ArgumentParser(
        prog="bw", description="BoumWave - Easy static blog generator"
    )

    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 'init' subcommand
    subparsers.add_parser("init", help="Initialize a new BoumWave project")

    # 'scaffold' subcommand
    subparsers.add_parser("scaffold", help="Create folder structure from configuration")

    # 'create' subcommand
    create_parser = subparsers.add_parser(
        "create", help="Read and display file content"
    )
    create_parser.add_argument(
        "filepath", help="Path to the file to read (e.g., my_post.md)"
    )

    # Parse arguments
    args = parser.parse_args()

    # Check if a command was provided
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Execute appropriate command
    if args.command == "init":
        init_command()
    elif args.command == "scaffold":
        scaffold_command()
    elif args.command == "create":
        create_command(args.filepath)


if __name__ == "__main__":
    main()
