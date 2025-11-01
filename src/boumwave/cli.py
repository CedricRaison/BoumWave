"""CLI entry point for BoumWave"""

import argparse
import sys

from boumwave.commands import (
    generate_command,
    generate_now_command,
    generate_sitemap_command,
    init_command,
    new_now_command,
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
        "new_post", help='Create a new post with language files (usage: bw new_post "Post Title")'
    )
    new_post_parser.add_argument("title", help="Title of the new post")

    # 'generate' subcommand
    generate_parser = subparsers.add_parser(
        "generate", help="Generate HTML from markdown post (usage: bw generate <post_folder_name>)"
    )
    generate_parser.add_argument(
        "post_name", help="Name of the post folder to generate"
    )

    # 'generate_sitemap' subcommand
    subparsers.add_parser(
        "generate_sitemap", help="Generate sitemap.xml with all blog post URLs"
    )

    # 'new_now' subcommand
    subparsers.add_parser("new_now", help="Create a new Now. post for today's date")

    # 'generate_now' subcommand
    subparsers.add_parser(
        "generate_now", help="Generate Now. feature and update index.html"
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
    elif args.command == "new_post":
        new_post_command(args.title)
    elif args.command == "generate":
        generate_command(args.post_name)
    elif args.command == "generate_sitemap":
        generate_sitemap_command()
    elif args.command == "new_now":
        new_now_command()
    elif args.command == "generate_now":
        generate_now_command()


if __name__ == "__main__":
    main()
