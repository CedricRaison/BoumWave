"""Data models for BoumWave"""

from datetime import date

from pydantic import BaseModel, Field, FilePath, HttpUrl


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
