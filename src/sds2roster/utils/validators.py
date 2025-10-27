"""Validation and utility functions for SDS to OneRoster conversion.

This module provides helper functions for:
- GUID generation using UUID v5
- Date validation and formatting
- Email validation
- String sanitization
"""

import re
import uuid
from datetime import datetime
from typing import Optional


# OneRoster namespace UUID for generating deterministic GUIDs
ONEROSTER_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def generate_guid(entity_type: str, sis_id: str) -> str:
    """Generate a deterministic GUID using UUID v5.

    Args:
        entity_type: Type of entity (e.g., "org", "user", "class", "course", "enrollment")
        sis_id: Source system identifier

    Returns:
        A GUID string in lowercase format (e.g., "550e8400-e29b-41d4-a716-446655440000")

    Example:
        >>> generate_guid("org", "SCH001")
        '...-...-...-...-...'  # Deterministic GUID
        >>> generate_guid("user", "STU001")
        '...-...-...-...-...'  # Different GUID
    """
    if not entity_type:
        raise ValueError("entity_type cannot be empty")
    if not sis_id:
        raise ValueError("sis_id cannot be empty")

    # Create a name string combining entity type and SIS ID
    name = f"{entity_type}:{sis_id}"

    # Generate UUID v5 using OneRoster namespace
    generated_uuid = uuid.uuid5(ONEROSTER_NAMESPACE, name)

    # Return as lowercase string
    return str(generated_uuid).lower()


def validate_guid(guid_string: str) -> bool:
    """Validate that a string is a valid GUID/UUID format.

    Args:
        guid_string: String to validate

    Returns:
        True if valid GUID format, False otherwise

    Example:
        >>> validate_guid("550e8400-e29b-41d4-a716-446655440000")
        True
        >>> validate_guid("invalid-guid")
        False
    """
    if not guid_string:
        return False

    try:
        # Try to parse as UUID
        uuid.UUID(guid_string)
        return True
    except (ValueError, AttributeError):
        return False


def validate_email(email: str) -> bool:
    """Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format, False otherwise

    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    if not email:
        return False

    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_date(date_string: str) -> bool:
    """Validate date string in ISO 8601 format.

    Args:
        date_string: Date string to validate (ISO 8601 format)

    Returns:
        True if valid ISO 8601 date, False otherwise

    Example:
        >>> validate_date("2025-10-27")
        True
        >>> validate_date("2025-10-27T10:30:00Z")
        True
        >>> validate_date("invalid-date")
        False
    """
    if not date_string:
        return False

    # Try common ISO 8601 formats
    formats = [
        "%Y-%m-%d",  # 2025-10-27
        "%Y-%m-%dT%H:%M:%S",  # 2025-10-27T10:30:00
        "%Y-%m-%dT%H:%M:%SZ",  # 2025-10-27T10:30:00Z
        "%Y-%m-%dT%H:%M:%S.%f",  # 2025-10-27T10:30:00.123456
        "%Y-%m-%dT%H:%M:%S.%fZ",  # 2025-10-27T10:30:00.123456Z
        "%Y-%m-%dT%H:%M:%S%z",  # 2025-10-27T10:30:00+09:00
    ]

    for fmt in formats:
        try:
            datetime.strptime(date_string, fmt)
            return True
        except ValueError:
            continue

    return False


def format_iso8601(dt: Optional[datetime] = None, with_timezone: bool = True) -> str:
    """Format datetime as ISO 8601 string.

    Args:
        dt: Datetime object to format (defaults to current UTC time)
        with_timezone: Include timezone indicator (default: True)

    Returns:
        ISO 8601 formatted datetime string

    Example:
        >>> format_iso8601(datetime(2025, 10, 27, 10, 30, 0))
        '2025-10-27T10:30:00Z'
    """
    if dt is None:
        from datetime import timezone
        dt = datetime.now(timezone.utc).replace(tzinfo=None)

    if with_timezone:
        # Format with Z timezone indicator
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        # Format without timezone
        return dt.strftime("%Y-%m-%dT%H:%M:%S")


def sanitize_string(value: Optional[str], max_length: Optional[int] = None) -> Optional[str]:
    """Sanitize string value by stripping whitespace and truncating if needed.

    Args:
        value: String value to sanitize
        max_length: Maximum length to truncate to (None for no truncation)

    Returns:
        Sanitized string or None if input is None/empty

    Example:
        >>> sanitize_string("  Hello World  ")
        'Hello World'
        >>> sanitize_string("Very long string", max_length=10)
        'Very long '
    """
    if not value:
        return None

    # Strip whitespace
    sanitized = value.strip()

    if not sanitized:
        return None

    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def create_metadata_json(sis_id: str, additional_data: Optional[dict] = None) -> str:
    """Create metadata JSON string for OneRoster with SIS ID.

    Args:
        sis_id: Source system identifier
        additional_data: Optional additional metadata key-value pairs

    Returns:
        JSON string with metadata

    Example:
        >>> create_metadata_json("SCH001")
        '{"sis_id":"SCH001"}'
        >>> create_metadata_json("SCH001", {"type": "school"})
        '{"sis_id":"SCH001","type":"school"}'
    """
    import json

    metadata = {"sis_id": sis_id}

    if additional_data:
        metadata.update(additional_data)

    # Return compact JSON (no extra spaces)
    return json.dumps(metadata, separators=(",", ":"))


def create_user_ids_json(sis_id: str, identifier_type: str = "sisId") -> str:
    """Create userIds JSON array for OneRoster users.

    Args:
        sis_id: Source system identifier
        identifier_type: Type of identifier (default: "sisId")

    Returns:
        JSON array string with user identifiers

    Example:
        >>> create_user_ids_json("STU001")
        '[{"type":"sisId","identifier":"STU001"}]'
    """
    import json

    user_ids = [{"type": identifier_type, "identifier": sis_id}]

    # Return compact JSON
    return json.dumps(user_ids, separators=(",", ":"))
