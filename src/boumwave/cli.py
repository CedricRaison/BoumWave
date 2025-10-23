"""CLI entry point for BoumWave"""

import argparse
import sys

from boumwave.commands import (
    init_command,
    new_post_command,
    scaffold_command,
)


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

    # 'new_post' subcommand
    new_post_parser = subparsers.add_parser(
        "new_post", help="Create a new post with language files"
    )
    new_post_parser.add_argument("title", help="Title of the new post")

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
    elif args.command == "new_post":
        new_post_command(args.title)


if __name__ == "__main__":
    main()
