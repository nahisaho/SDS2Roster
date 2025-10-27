"""Unit tests for validation utilities."""

from datetime import datetime

import pytest

from sds2roster.utils.validators import (
    create_metadata_json,
    create_user_ids_json,
    format_iso8601,
    generate_guid,
    sanitize_string,
    validate_date,
    validate_email,
    validate_guid,
)


class TestGenerateGuid:
    """Tests for GUID generation."""

    def test_generate_guid_for_org(self) -> None:
        """Test GUID generation for organization."""
        guid = generate_guid("org", "SCH001")
        assert isinstance(guid, str)
        assert len(guid) == 36  # UUID format: 8-4-4-4-12
        assert validate_guid(guid)

    def test_generate_guid_deterministic(self) -> None:
        """Test that GUID generation is deterministic."""
        guid1 = generate_guid("org", "SCH001")
        guid2 = generate_guid("org", "SCH001")
        assert guid1 == guid2

    def test_generate_guid_different_for_different_ids(self) -> None:
        """Test that different IDs generate different GUIDs."""
        guid1 = generate_guid("org", "SCH001")
        guid2 = generate_guid("org", "SCH002")
        assert guid1 != guid2

    def test_generate_guid_different_for_different_types(self) -> None:
        """Test that different entity types generate different GUIDs."""
        guid1 = generate_guid("org", "SCH001")
        guid2 = generate_guid("user", "SCH001")
        assert guid1 != guid2

    def test_generate_guid_empty_entity_type_raises_error(self) -> None:
        """Test that empty entity type raises error."""
        with pytest.raises(ValueError, match="entity_type cannot be empty"):
            generate_guid("", "SCH001")

    def test_generate_guid_empty_sis_id_raises_error(self) -> None:
        """Test that empty SIS ID raises error."""
        with pytest.raises(ValueError, match="sis_id cannot be empty"):
            generate_guid("org", "")


class TestValidateGuid:
    """Tests for GUID validation."""

    def test_validate_valid_guid(self) -> None:
        """Test validation of valid GUID."""
        assert validate_guid("550e8400-e29b-41d4-a716-446655440000") is True

    def test_validate_valid_guid_uppercase(self) -> None:
        """Test validation of valid GUID in uppercase."""
        assert validate_guid("550E8400-E29B-41D4-A716-446655440000") is True

    def test_validate_invalid_guid(self) -> None:
        """Test validation of invalid GUID."""
        assert validate_guid("invalid-guid") is False

    def test_validate_empty_guid(self) -> None:
        """Test validation of empty GUID."""
        assert validate_guid("") is False

    def test_validate_none_guid(self) -> None:
        """Test validation of None GUID."""
        assert validate_guid(None) is False  # type: ignore


class TestValidateEmail:
    """Tests for email validation."""

    def test_validate_valid_email(self) -> None:
        """Test validation of valid email."""
        assert validate_email("user@example.com") is True

    def test_validate_email_with_subdomain(self) -> None:
        """Test validation of email with subdomain."""
        assert validate_email("user@mail.example.com") is True

    def test_validate_email_with_plus(self) -> None:
        """Test validation of email with plus sign."""
        assert validate_email("user+tag@example.com") is True

    def test_validate_invalid_email_no_at(self) -> None:
        """Test validation of invalid email without @."""
        assert validate_email("userexample.com") is False

    def test_validate_invalid_email_no_domain(self) -> None:
        """Test validation of invalid email without domain."""
        assert validate_email("user@") is False

    def test_validate_empty_email(self) -> None:
        """Test validation of empty email."""
        assert validate_email("") is False


class TestValidateDate:
    """Tests for date validation."""

    def test_validate_date_only(self) -> None:
        """Test validation of date-only string."""
        assert validate_date("2025-10-27") is True

    def test_validate_datetime_with_z(self) -> None:
        """Test validation of datetime with Z timezone."""
        assert validate_date("2025-10-27T10:30:00Z") is True

    def test_validate_datetime_without_z(self) -> None:
        """Test validation of datetime without timezone."""
        assert validate_date("2025-10-27T10:30:00") is True

    def test_validate_datetime_with_microseconds(self) -> None:
        """Test validation of datetime with microseconds."""
        assert validate_date("2025-10-27T10:30:00.123456Z") is True

    def test_validate_datetime_with_timezone_offset(self) -> None:
        """Test validation of datetime with timezone offset."""
        assert validate_date("2025-10-27T10:30:00+09:00") is True

    def test_validate_invalid_date(self) -> None:
        """Test validation of invalid date."""
        assert validate_date("invalid-date") is False

    def test_validate_empty_date(self) -> None:
        """Test validation of empty date."""
        assert validate_date("") is False


class TestFormatIso8601:
    """Tests for ISO 8601 formatting."""

    def test_format_with_specific_datetime(self) -> None:
        """Test formatting with specific datetime."""
        dt = datetime(2025, 10, 27, 10, 30, 0)
        result = format_iso8601(dt)
        assert result == "2025-10-27T10:30:00Z"

    def test_format_without_timezone(self) -> None:
        """Test formatting without timezone indicator."""
        dt = datetime(2025, 10, 27, 10, 30, 0)
        result = format_iso8601(dt, with_timezone=False)
        assert result == "2025-10-27T10:30:00"

    def test_format_with_none_uses_current_time(self) -> None:
        """Test that None datetime uses current time."""
        result = format_iso8601()
        assert isinstance(result, str)
        assert "T" in result
        assert result.endswith("Z")


class TestSanitizeString:
    """Tests for string sanitization."""

    def test_sanitize_strips_whitespace(self) -> None:
        """Test that sanitization strips whitespace."""
        assert sanitize_string("  Hello World  ") == "Hello World"

    def test_sanitize_returns_none_for_empty(self) -> None:
        """Test that empty string returns None."""
        assert sanitize_string("") is None

    def test_sanitize_returns_none_for_whitespace_only(self) -> None:
        """Test that whitespace-only string returns None."""
        assert sanitize_string("   ") is None

    def test_sanitize_returns_none_for_none(self) -> None:
        """Test that None input returns None."""
        assert sanitize_string(None) is None

    def test_sanitize_truncates_to_max_length(self) -> None:
        """Test that string is truncated to max length."""
        result = sanitize_string("Very long string", max_length=10)
        assert result == "Very long "
        assert len(result) == 10

    def test_sanitize_no_truncation_if_shorter(self) -> None:
        """Test that string is not truncated if shorter than max."""
        result = sanitize_string("Short", max_length=10)
        assert result == "Short"


class TestCreateMetadataJson:
    """Tests for metadata JSON creation."""

    def test_create_metadata_with_sis_id_only(self) -> None:
        """Test metadata creation with only SIS ID."""
        result = create_metadata_json("SCH001")
        assert result == '{"sis_id":"SCH001"}'

    def test_create_metadata_with_additional_data(self) -> None:
        """Test metadata creation with additional data."""
        result = create_metadata_json("SCH001", {"type": "school"})
        assert '"sis_id":"SCH001"' in result
        assert '"type":"school"' in result

    def test_create_metadata_json_is_valid(self) -> None:
        """Test that created metadata is valid JSON."""
        import json

        result = create_metadata_json("SCH001")
        parsed = json.loads(result)
        assert parsed["sis_id"] == "SCH001"


class TestCreateUserIdsJson:
    """Tests for userIds JSON creation."""

    def test_create_user_ids_default_type(self) -> None:
        """Test userIds creation with default type."""
        result = create_user_ids_json("STU001")
        assert result == '[{"type":"sisId","identifier":"STU001"}]'

    def test_create_user_ids_custom_type(self) -> None:
        """Test userIds creation with custom identifier type."""
        result = create_user_ids_json("STU001", "customId")
        assert '"type":"customId"' in result
        assert '"identifier":"STU001"' in result

    def test_create_user_ids_json_is_valid(self) -> None:
        """Test that created userIds is valid JSON."""
        import json

        result = create_user_ids_json("STU001")
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == 1
        assert parsed[0]["type"] == "sisId"
        assert parsed[0]["identifier"] == "STU001"
