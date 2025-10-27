"""Test configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_sds_data():
    """Sample SDS data for testing."""
    return {
        "users": [],
        "schools": [],
        "sections": [],
    }


@pytest.fixture
def sample_oneroster_data():
    """Sample OneRoster data for testing."""
    return {
        "users": [],
        "orgs": [],
        "classes": [],
    }


@pytest.fixture
def test_data_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test data."""
    return tmp_path / "test_data"
