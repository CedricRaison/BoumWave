"""Unit tests for exceptions.py"""

from boumwave.exceptions import (
    BoumWaveError,
    ConfigNotFoundError,
    ConfigValidationError,
    ConfigurationError,
    EnvironmentValidationError,
    FileAlreadyExistsError,
    FileCreationError,
    FileNotFoundError,
    FileSystemError,
    MarkdownParseError,
    MetadataExtractionError,
    PostProcessingError,
    PostValidationError,
    TemplateError,
    TemplateNotFoundError,
    TemplateRenderError,
    ValidationError,
)


class TestBoumWaveError:
    """Tests for base BoumWaveError"""

    def test_error_with_message_only(self):
        """Test creating error with message only"""
        error = BoumWaveError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.hint is None
        assert str(error) == "Something went wrong"

    def test_error_with_message_and_hint(self):
        """Test creating error with message and hint"""
        error = BoumWaveError("Something went wrong", hint="Try this fix")
        assert error.message == "Something went wrong"
        assert error.hint == "Try this fix"


class TestConfigurationErrors:
    """Tests for configuration-related errors"""

    def test_configuration_error_inheritance(self):
        """Test ConfigurationError inherits from BoumWaveError"""
        error = ConfigurationError("Config error")
        assert isinstance(error, BoumWaveError)

    def test_config_not_found_error(self):
        """Test ConfigNotFoundError has default message"""
        error = ConfigNotFoundError()
        assert "boumwave.toml not found" in error.message
        assert error.hint is not None
        assert "bw init" in error.hint

    def test_config_validation_error(self):
        """Test ConfigValidationError"""
        error = ConfigValidationError(message="Invalid config", hint="Check your TOML")
        assert error.message == "Invalid config"
        assert error.hint == "Check your TOML"


class TestValidationErrors:
    """Tests for validation errors"""

    def test_validation_error_single_error(self):
        """Test ValidationError with single error"""
        error = ValidationError(["Error 1"], hint="Fix this")
        assert error.errors == ["Error 1"]
        assert error.message == "Error 1"
        assert error.hint == "Fix this"

    def test_validation_error_multiple_errors(self):
        """Test ValidationError with multiple errors"""
        error = ValidationError(["Error 1", "Error 2", "Error 3"])
        assert error.errors == ["Error 1", "Error 2", "Error 3"]
        assert "Error 1" in error.message
        assert "Error 2" in error.message
        assert "Error 3" in error.message

    def test_validation_error_add_error(self):
        """Test adding errors dynamically"""
        error = ValidationError(["Error 1"])
        assert len(error.errors) == 1

        error.add_error("Error 2")
        assert len(error.errors) == 2
        assert "Error 2" in error.message

    def test_environment_validation_error(self):
        """Test EnvironmentValidationError"""
        error = EnvironmentValidationError(["Missing file", "Invalid config"])
        assert "Missing file" in error.message
        assert "Invalid config" in error.message
        assert "bw generate" in error.hint

    def test_post_validation_error(self):
        """Test PostValidationError"""
        error = PostValidationError(["Invalid slug", "Missing date"])
        assert "Invalid slug" in error.message
        assert "Missing date" in error.message


class TestTemplateErrors:
    """Tests for template-related errors"""

    def test_template_error_inheritance(self):
        """Test TemplateError inherits from BoumWaveError"""
        error = TemplateError("Template error")
        assert isinstance(error, BoumWaveError)

    def test_template_not_found_error(self):
        """Test TemplateNotFoundError"""
        error = TemplateNotFoundError(
            message="Template not found", hint="Run bw scaffold"
        )
        assert error.message == "Template not found"
        assert error.hint == "Run bw scaffold"

    def test_template_render_error(self):
        """Test TemplateRenderError"""
        error = TemplateRenderError(
            message="Render failed", hint="Check template syntax"
        )
        assert error.message == "Render failed"
        assert error.hint == "Check template syntax"


class TestFileSystemErrors:
    """Tests for filesystem-related errors"""

    def test_filesystem_error_inheritance(self):
        """Test FileSystemError inherits from BoumWaveError"""
        error = FileSystemError("File error")
        assert isinstance(error, BoumWaveError)

    def test_file_not_found_error(self):
        """Test FileNotFoundError"""
        error = FileNotFoundError(message="File not found", hint="Check the path")
        assert error.message == "File not found"
        assert error.hint == "Check the path"

    def test_file_creation_error(self):
        """Test FileCreationError"""
        error = FileCreationError(
            message="Cannot create file", hint="Check permissions"
        )
        assert error.message == "Cannot create file"
        assert error.hint == "Check permissions"

    def test_file_already_exists_error(self):
        """Test FileAlreadyExistsError"""
        error = FileAlreadyExistsError(message="File exists", hint="Use different name")
        assert error.message == "File exists"
        assert error.hint == "Use different name"


class TestPostProcessingErrors:
    """Tests for post processing errors"""

    def test_post_processing_error_inheritance(self):
        """Test PostProcessingError inherits from BoumWaveError"""
        error = PostProcessingError("Processing error")
        assert isinstance(error, BoumWaveError)

    def test_markdown_parse_error(self):
        """Test MarkdownParseError"""
        error = MarkdownParseError(
            message="Cannot parse markdown", hint="Check file format"
        )
        assert error.message == "Cannot parse markdown"
        assert error.hint == "Check file format"

    def test_metadata_extraction_error(self):
        """Test MetadataExtractionError"""
        error = MetadataExtractionError(
            message="Cannot extract metadata", hint="Check front matter"
        )
        assert error.message == "Cannot extract metadata"
        assert error.hint == "Check front matter"
