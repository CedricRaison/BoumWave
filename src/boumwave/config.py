"""Configuration management for BoumWave"""

import sys
import tomllib
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, HttpUrl, ValidationError, model_validator


class DateFormat(str, Enum):
    """Available date formats for displaying publication dates"""

    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    FULL = "full"


class Translations(BaseModel):
    """Translations for template text"""

    published_on: str = Field(
        description="Translation for 'Published on' text in templates"
    )


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
    index_template: str = Field(
        description="HTML file for the blog's index/home page (created at project root)"
    )


class SiteConfig(BaseModel):
    """Configuration for site settings"""

    languages: list[str] = Field(
        description="List of language codes supported by the site (e.g., ['en', 'fr'])"
    )
    site_url: HttpUrl = Field(
        description="URL of the site (used for canonical links and Open Graph tags)"
    )
    logo_path: str = Field(
        description="Path to the site logo for social media meta tags (fallback when post has no image)"
    )
    date_format: DateFormat = Field(
        description="Date format for displaying publication dates (short, medium, long, or full)"
    )
    translations: dict[str, Translations] = Field(
        description="Translations for template text, keyed by language code"
    )

    @model_validator(mode="after")
    def validate_translations_for_all_languages(self) -> "SiteConfig":
        """
        Validate that translations exist for all configured languages.
        """
        missing_languages = []
        for lang in self.languages:
            if lang not in self.translations:
                missing_languages.append(lang)

        if missing_languages:
            langs_str = ", ".join(missing_languages)
            raise ValueError(
                f"Missing translations for language(s): {langs_str}. "
                f"Please add [site.translations.{missing_languages[0]}] section in boumwave.toml"
            )

        return self


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
