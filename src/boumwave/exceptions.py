"""Custom exceptions for BoumWave"""


class BoumWaveError(Exception):
    """Base exception for all BoumWave errors."""

    def __init__(self, message: str, hint: str | None = None):
        """
        Initialize BoumWave error.

        Args:
            message: Error message describing what went wrong
            hint: Optional suggestion on how to fix the error
        """
        self.message = message
        self.hint = hint
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation of the error."""
        return self.message


# Configuration errors
class ConfigurationError(BoumWaveError):
    """Configuration-related errors."""

    pass


class ConfigNotFoundError(ConfigurationError):
    """Configuration file not found."""

    def __init__(self):
        super().__init__(
            message="boumwave.toml not found.",
            hint="Run 'bw init' first to create the configuration file.",
        )


class ConfigValidationError(ConfigurationError):
    """Configuration file has invalid content."""

    pass


# Validation errors
class ValidationError(BoumWaveError):
    """Validation errors (can contain multiple error messages)."""

    def __init__(self, errors: list[str], hint: str | None = None):
        """
        Initialize validation error with multiple error messages.

        Args:
            errors: List of error messages
            hint: Optional suggestion on how to fix the errors
        """
        self.errors = errors
        message = "\n".join(errors)
        super().__init__(message, hint)

    def add_error(self, error: str) -> None:
        """Add an error to the list."""
        self.errors.append(error)
        self.message = "\n".join(self.errors)


class EnvironmentValidationError(ValidationError):
    """Environment validation failed before generation."""

    def __init__(self, errors: list[str]):
        super().__init__(
            errors=errors, hint="Fix the above issues before running 'bw generate'"
        )


class PostValidationError(ValidationError):
    """Post front matter validation failed."""

    pass


# Template errors
class TemplateError(BoumWaveError):
    """Template-related errors."""

    pass


class TemplateNotFoundError(TemplateError):
    """Template file not found."""

    pass


class TemplateRenderError(TemplateError):
    """Template rendering failed."""

    pass


# File system errors
class FileSystemError(BoumWaveError):
    """File system operation errors."""

    pass


class FileNotFoundError(FileSystemError):
    """Required file not found."""

    pass


class FileCreationError(FileSystemError):
    """Failed to create file or directory."""

    pass


class FileAlreadyExistsError(FileSystemError):
    """File or directory already exists."""

    pass


# Post processing errors
class PostProcessingError(BoumWaveError):
    """Post processing errors."""

    pass


class MarkdownParseError(PostProcessingError):
    """Failed to parse markdown file."""

    pass


class MetadataExtractionError(PostProcessingError):
    """Failed to extract metadata from content."""

    pass
