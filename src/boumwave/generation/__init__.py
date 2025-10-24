"""Generation module for converting markdown to HTML"""

from boumwave.generation.metadata import (
    extract_description,
    extract_first_image,
    generate_meta_tags,
    inject_meta_tags_and_canonical,
)
from boumwave.generation.parsers import find_post_files, parse_post_file
from boumwave.generation.renderers import render_markdown
from boumwave.generation.template_engine import render_template

__all__ = [
    "parse_post_file",
    "find_post_files",
    "render_markdown",
    "extract_description",
    "extract_first_image",
    "generate_meta_tags",
    "inject_meta_tags_and_canonical",
    "render_template",
]
