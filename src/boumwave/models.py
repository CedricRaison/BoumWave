"""Data models for BoumWave"""

from datetime import date

from babel.dates import format_date
from pydantic import BaseModel, Field, FilePath, HttpUrl, computed_field

from boumwave.config import SiteConfig


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
    full_url: HttpUrl = Field(
        ..., description="Complete URL (e.g., https://example.com/posts/fr/mon-slug)"
    )
    relative_url: str = Field(
        ..., description="Relative URL path (e.g., /posts/fr/mon-slug)"
    )
    description: str = Field(
        ..., description="SEO description (max 155 characters, extracted from content)"
    )
    image: FilePath = Field(
        ..., description="Path to image for social media (first image or logo)"
    )
    content_html: str = Field(..., description="Rendered HTML content from markdown")
    site_config: SiteConfig = Field(
        ..., description="Site configuration for accessing date format and translations"
    )

    @computed_field
    @property
    def published_on_date(self) -> str:
        """
        Complete publication message combining translation and formatted date.
        Uses site_config.translations[lang].published_on and site_config.date_format.

        Example: "Published on October 24, 2025"
        """
        # Format the date according to config and language
        formatted_date = format_date(
            self.post.published_date,
            format=self.site_config.date_format.value,
            locale=self.post.lang,
        )

        # Get the translation for "Published on"
        translation = self.site_config.translations[self.post.lang].published_on

        return f"{translation} {formatted_date}"
