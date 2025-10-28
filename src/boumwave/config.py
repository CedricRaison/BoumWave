"""Configuration management for BoumWave"""

import tomllib
from enum import Enum
from pathlib import Path

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    ValidationError,
    computed_field,
    model_validator,
)

from boumwave.exceptions import ConfigNotFoundError, ConfigValidationError


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
    link_template: str = Field(
        description="HTML template file for generating post links (must be in template_folder)"
    )
    index_template: str = Field(
        description="HTML file for the blog's index/home page (created at project root)"
    )
    sitemap_template: str = Field(
        description="XML file for the sitemap (created at project root)"
    )
    now_folder: str | None = Field(
        default=None,
        description="Folder where 'Now.' posts are stored (optional, enables Now. feature)",
    )
    now_template: str | None = Field(
        default=None,
        description="HTML file for listing all Now. posts (optional, requires now_folder)",
    )
    now_index_template: str | None = Field(
        default=None,
        description="HTML template for displaying Now. post in index.html (optional, requires now_folder)",
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
    posts_start_marker: str = Field(
        description="HTML comment marker to indicate where post list starts in index.html"
    )
    posts_end_marker: str = Field(
        description="HTML comment marker to indicate where post list ends in index.html"
    )
    sitemap_start_marker: str = Field(
        description="XML comment marker to indicate where BoumWave posts start in sitemap.xml"
    )
    sitemap_end_marker: str = Field(
        description="XML comment marker to indicate where BoumWave posts end in sitemap.xml"
    )
    now_start_marker: str | None = Field(
        default=None,
        description="HTML comment marker to indicate where Now. post starts in index.html (optional)",
    )
    now_end_marker: str | None = Field(
        default=None,
        description="HTML comment marker to indicate where Now. post ends in index.html (optional)",
    )
    translations: dict[str, Translations] = Field(
        description="Translations for template text, keyed by language code"
    )

    @computed_field
    @property
    def site_url_base(self) -> str:
        """Site URL without trailing slash (for URL concatenation)."""
        return str(self.site_url).rstrip("/")

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
        ConfigNotFoundError: If the config file doesn't exist
        ConfigValidationError: If the config file is invalid
    """
    config_file = Path("boumwave.toml")

    # Check if config file exists
    if not config_file.exists():
        raise ConfigNotFoundError()

    # Read and parse TOML file
    try:
        with open(config_file, "rb") as f:
            config_data = tomllib.load(f)
    except Exception as e:
        raise ConfigValidationError(
            message=f"Error reading configuration file: {e}",
            hint="Check that boumwave.toml is a valid TOML file",
        ) from e

    # Validate with Pydantic
    try:
        return BoumWaveConfig.model_validate(config_data)
    except ValidationError as e:
        errors = ["Invalid configuration in boumwave.toml"]
        for error in e.errors():
            field_name = error["loc"][-1]  # Get the last part of the path
            if error["type"] == "missing":
                errors.append(f"  Missing required config: {field_name}")
            else:
                errors.append(f"  Invalid config '{field_name}': {error['msg']}")

        raise ConfigValidationError(
            message="\n".join(errors),
            hint="Review your boumwave.toml file and fix the above issues",
        ) from e


# Global config cache
_config: BoumWaveConfig | None = None


def get_config() -> BoumWaveConfig:
    """
    Get or load configuration (cached after first call).

    This function loads the configuration once and caches it for subsequent calls,
    avoiding multiple file reads and parsing operations.

    Returns:
        Cached or newly loaded BoumWaveConfig object

    Raises:
        ConfigNotFoundError: If the config file doesn't exist
        ConfigValidationError: If the config file is invalid
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config
