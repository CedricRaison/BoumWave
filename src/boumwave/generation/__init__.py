"""Generation module for converting markdown to HTML"""

from boumwave.generation.index_manager import update_index
from boumwave.generation.metadata import (
    extract_description,
    generate_seo_tags,
    inject_meta_tags_and_canonical,
)
from boumwave.generation.parsers import (
    collect_all_posts,
    find_post_files,
    parse_post_file,
)
from boumwave.generation.renderers import render_markdown
from boumwave.generation.sitemap_manager import update_sitemap
from boumwave.generation.template_engine import render_template

__all__ = [
    "parse_post_file",
    "find_post_files",
    "collect_all_posts",
    "render_markdown",
    "extract_description",
    "generate_seo_tags",
    "inject_meta_tags_and_canonical",
    "render_template",
    "update_index",
    "update_sitemap",
]
