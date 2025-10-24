"""Data models for BoumWave"""

import sys
import tomllib
from datetime import date
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError


class PathsConfig(BaseModel):
    """Configuration for file paths"""

    template_folder: str = Field(description="Folder where HTML templates are stored")
    content_folder: str = Field(description="Folder where markdown content is stored")
    output_folder: str = Field(
        description="Folder where generated posts will be output (also used in URLs)"
    )
    post_template: str = Field(
        description="HTML template file for generating posts (must be in template_folder)"
    )


class SiteConfig(BaseModel):
    """Configuration for site settings"""

    languages: list[str] = Field(
        description="List of language codes supported by the site (e.g., ['en', 'fr'])"
    )
    logo_path: str = Field(
        description="Path to the site logo for social media meta tags (fallback when post has no image)"
    )


class BoumWaveConfig(BaseModel):
    """Root configuration model for boumwave.toml"""

    paths: PathsConfig
    site: SiteConfig


def load_config() -> BoumWaveConfig:
    """
    Load and validate the BoumWave configuration file.

    Returns:
        Validated BoumWaveConfig object

    Raises:
        SystemExit: If the config file doesn't exist or is invalid
    """
    config_file = Path("boumwave.toml")

    # Check if config file exists
    if not config_file.exists():
        print("Error: boumwave.toml not found.", file=sys.stderr)
        print("Run 'bw init' first to create the configuration file.", file=sys.stderr)
        sys.exit(1)

    # Read and parse TOML file
    try:
        with open(config_file, "rb") as f:
            config_data = tomllib.load(f)
    except Exception as e:
        print(f"Error reading configuration file: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate with Pydantic
    try:
        return BoumWaveConfig.model_validate(config_data)
    except ValidationError as e:
        print("Error: Invalid configuration in boumwave.toml", file=sys.stderr)
        for error in e.errors():
            field_name = error["loc"][-1]  # Get the last part of the path
            if error["type"] == "missing":
                print(f"  Missing required config: {field_name}", file=sys.stderr)
            else:
                print(
                    f"  Invalid config '{field_name}': {error['msg']}", file=sys.stderr
                )
        sys.exit(1)


class Post(BaseModel):
    """
    Model representing a blog post.

    This model defines the structure of a post's front matter metadata.
    """

    title: str = Field(..., description="Title of the post")
    slug: str = Field(
        ...,
        description="URL-friendly slug (e.g., 'my-awesome-post')",
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    published_date: date = Field(..., description="Publication date of the post")
    lang: str = Field(
        ..., description="Language code (e.g., 'en', 'fr')", pattern=r"^[a-z]{2}$"
    )

    class Config:
        """Pydantic configuration"""

        json_schema_extra = {
            "example": {
                "title": "My Awesome Post",
                "slug": "my-awesome-post",
                "published_date": "2025-10-23",
                "lang": "en",
            }
        }
