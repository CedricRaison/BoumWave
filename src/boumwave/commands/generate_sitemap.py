"""Generate sitemap.xml from all posts"""

import sys

from boumwave.exceptions import BoumWaveError
from boumwave.generation import update_sitemap
from boumwave.validation import validate_sitemap_environment


def generate_sitemap_command() -> None:
    """
    Generate sitemap.xml with URLs for index page and all blog posts.
    CLI wrapper that handles exceptions.
    """
    try:
        _generate_sitemap_impl()
    except BoumWaveError as e:
        print(f"Error: {e}", file=sys.stderr)
        if e.hint:
            print(f"Hint: {e.hint}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def _generate_sitemap_impl() -> None:
    """
    Generate sitemap.xml with URLs for index page and all blog posts.
    Raises exceptions instead of calling sys.exit().
    """
    # Validate environment before doing any work
    validate_sitemap_environment()

    # Update sitemap.xml with all URLs
    print("Generating sitemap.xml...")
    update_sitemap()
    print("✓ Sitemap updated successfully!")
