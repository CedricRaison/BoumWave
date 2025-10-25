"""Data models for BoumWave"""

from datetime import date

from babel.dates import format_date
from pydantic import BaseModel, Field, FilePath, computed_field

from boumwave.config import BoumWaveConfig


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

    @computed_field
    @property
    def published_datetime_iso(self) -> str:
        """
        ISO 8601 datetime format for meta tags.
        Converts the date to datetime with 00:00:00 UTC.
        """
        return f"{self.published_date}T00:00:00Z"

    def get_relative_url(self, config: BoumWaveConfig) -> str:
        """
        Calculate the relative URL path for this post.

        Args:
            config: BoumWave configuration

        Returns:
            Relative URL (e.g., "/posts/en/my-slug")
        """
        return f"/{config.paths.output_folder}/{self.lang}/{self.slug}"

    def get_full_url(self, config: BoumWaveConfig) -> str:
        """
        Calculate the complete URL for this post.

        Args:
            config: BoumWave configuration

        Returns:
            Full URL (e.g., "https://example.com/posts/en/my-slug")
        """
        return f"{str(config.site.site_url)}{self.get_relative_url(config)}"

    def get_published_on_date(self, config: BoumWaveConfig) -> str:
        """
        Get the localized publication message.

        Args:
            config: BoumWave configuration

        Returns:
            Formatted message (e.g., "Published on October 24, 2025")
        """
        formatted_date = format_date(
            self.published_date,
            format=config.site.date_format.value,
            locale=self.lang,
        )
        translation = config.site.translations[self.lang].published_on
        return f"{translation} {formatted_date}"

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


class EnrichedPost(BaseModel):
    """
    Post enriched with calculated metadata for generation.

    This model extends the basic Post with additional fields needed
    for generating HTML pages with proper SEO metadata.
    """

    post: Post = Field(..., description="Validated post front matter")
    description: str = Field(
        ..., description="SEO description (max 155 characters, extracted from content)"
    )
    image: FilePath = Field(
        ..., description="Path to image for social media (first image or logo)"
    )
    content_html: str = Field(..., description="Rendered HTML content from markdown")
    config: BoumWaveConfig = Field(..., description="Complete BoumWave configuration")

    @computed_field
    @property
    def relative_url(self) -> str:
        """
        Relative URL path for the post.

        Example: /posts/fr/my-slug
        """
        return self.post.get_relative_url(self.config)

    @computed_field
    @property
    def full_url(self) -> str:
        """
        Complete URL for the post.

        Example: https://example.com/posts/fr/my-slug
        """
        return self.post.get_full_url(self.config)

    @computed_field
    @property
    def published_on_date(self) -> str:
        """
        Complete publication message combining translation and formatted date.
        Uses config.site.translations[lang].published_on and config.site.date_format.

        Example: "Published on October 24, 2025"
        """
        return self.post.get_published_on_date(self.config)
