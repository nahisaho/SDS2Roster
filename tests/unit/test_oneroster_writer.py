"""Unit tests for OneRoster CSV writer."""

import csv
from datetime import datetime
from pathlib import Path

import pytest

from sds2roster.models.oneroster import (
    ClassType,
    EnrollmentRole,
    OneRosterAcademicSession,
    OneRosterClass,
    OneRosterDataModel,
    OneRosterEnrollment,
    OneRosterOrg,
    OneRosterStatus,
    OneRosterUser,
    OrgType,
    RoleType,
)
from sds2roster.parsers.oneroster_writer import OneRosterCSVWriter


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Create temporary output directory."""
    return tmp_path / "output"


@pytest.fixture
def writer(output_dir: Path) -> OneRosterCSVWriter:
    """Create OneRoster CSV writer."""
    return OneRosterCSVWriter(output_dir)


@pytest.fixture
def sample_data_model() -> OneRosterDataModel:
    """Create sample OneRoster data model for testing."""
    now = datetime(2025, 10, 27, 10, 30, 0)

    org = OneRosterOrg(
        sourced_id="550e8400-e29b-41d4-a716-446655440001",
        status=OneRosterStatus.ACTIVE,
        date_last_modified=now,
        name="Tokyo International School",
        type=OrgType.SCHOOL,
        identifier="TIS-001",
        metadata='{"sis_id":"SCH001"}',
    )

    user = OneRosterUser(
        sourced_id="550e8400-e29b-41d4-a716-446655440002",
        status=OneRosterStatus.ACTIVE,
        date_last_modified=now,
        enabled_user=True,
        org_sourced_ids="550e8400-e29b-41d4-a716-446655440001",
        role=RoleType.STUDENT,
        username="taro.yamada",
        user_ids='[{"type":"sisId","identifier":"STU001"}]',
        given_name="Taro",
        family_name="Yamada",
        email="taro@example.com",
        grades="10",
    )

    return OneRosterDataModel(orgs=[org], users=[user])


class TestOneRosterCSVWriter:
    """Tests for OneRoster CSV writer."""

    def test_writer_creates_output_directory(self, output_dir: Path) -> None:
        """Test that writer creates output directory."""
        assert not output_dir.exists()
        OneRosterCSVWriter(output_dir)
        assert output_dir.exists()
        assert output_dir.is_dir()

    def test_write_orgs(
        self, writer: OneRosterCSVWriter, sample_data_model: OneRosterDataModel
    ) -> None:
        """Test writing organizations to CSV."""
        file_path = writer.write_orgs(sample_data_model)

        assert file_path.exists()
        assert file_path.name == "orgs.csv"

        # Verify content
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["sourcedId"] == "550e8400-e29b-41d4-a716-446655440001"
        assert rows[0]["name"] == "Tokyo International School"
        assert rows[0]["type"] == "school"
        assert rows[0]["status"] == "active"

    def test_write_users(
        self, writer: OneRosterCSVWriter, sample_data_model: OneRosterDataModel
    ) -> None:
        """Test writing users to CSV."""
        file_path = writer.write_users(sample_data_model)

        assert file_path.exists()
        assert file_path.name == "users.csv"

        # Verify content
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["sourcedId"] == "550e8400-e29b-41d4-a716-446655440002"
        assert rows[0]["username"] == "taro.yamada"
        assert rows[0]["role"] == "student"
        assert rows[0]["enabledUser"] == "TRUE"
        assert rows[0]["givenName"] == "Taro"
        assert rows[0]["familyName"] == "Yamada"

    def test_write_users_with_optional_fields(
        self, writer: OneRosterCSVWriter, output_dir: Path
    ) -> None:
        """Test writing users with optional fields as empty strings."""
        now = datetime(2025, 10, 27, 10, 30, 0)

        user = OneRosterUser(
            sourced_id="550e8400-e29b-41d4-a716-446655440003",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=now,
            enabled_user=True,
            org_sourced_ids="550e8400-e29b-41d4-a716-446655440001",
            role=RoleType.TEACHER,
            username="john.smith",
            given_name="John",
            family_name="Smith",
            # No optional fields
        )

        data_model = OneRosterDataModel(users=[user])
        file_path = writer.write_users(data_model)

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert rows[0]["middleName"] == ""
        assert rows[0]["email"] == ""
        assert rows[0]["grades"] == ""

    def test_write_classes(self, writer: OneRosterCSVWriter, output_dir: Path) -> None:
        """Test writing classes to CSV."""
        now = datetime(2025, 10, 27, 10, 30, 0)

        cls = OneRosterClass(
            sourced_id="550e8400-e29b-41d4-a716-446655440004",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=now,
            title="Math 101 - Period 1",
            class_type=ClassType.SCHEDULED,
            course_sourced_id="550e8400-e29b-41d4-a716-446655440005",
            school_sourced_id="550e8400-e29b-41d4-a716-446655440001",
        )

        data_model = OneRosterDataModel(classes=[cls])
        file_path = writer.write_classes(data_model)

        assert file_path.exists()
        assert file_path.name == "classes.csv"

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["title"] == "Math 101 - Period 1"
        assert rows[0]["classType"] == "scheduled"

    def test_write_enrollments(self, writer: OneRosterCSVWriter, output_dir: Path) -> None:
        """Test writing enrollments to CSV."""
        now = datetime(2025, 10, 27, 10, 30, 0)

        enrollment = OneRosterEnrollment(
            sourced_id="550e8400-e29b-41d4-a716-446655440006",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=now,
            class_sourced_id="550e8400-e29b-41d4-a716-446655440004",
            school_sourced_id="550e8400-e29b-41d4-a716-446655440001",
            user_sourced_id="550e8400-e29b-41d4-a716-446655440002",
            role=EnrollmentRole.STUDENT,
        )

        data_model = OneRosterDataModel(enrollments=[enrollment])
        file_path = writer.write_enrollments(data_model)

        assert file_path.exists()

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["role"] == "student"

    def test_write_enrollments_with_dates(
        self, writer: OneRosterCSVWriter, output_dir: Path
    ) -> None:
        """Test writing enrollments with begin and end dates."""
        now = datetime(2025, 10, 27, 10, 30, 0)
        begin_date = datetime(2025, 9, 1)
        end_date = datetime(2025, 12, 20)

        enrollment = OneRosterEnrollment(
            sourced_id="550e8400-e29b-41d4-a716-446655440007",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=now,
            class_sourced_id="550e8400-e29b-41d4-a716-446655440004",
            school_sourced_id="550e8400-e29b-41d4-a716-446655440001",
            user_sourced_id="550e8400-e29b-41d4-a716-446655440002",
            role=EnrollmentRole.TEACHER,
            primary=True,
            begin_date=begin_date,
            end_date=end_date,
        )

        data_model = OneRosterDataModel(enrollments=[enrollment])
        file_path = writer.write_enrollments(data_model)

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert rows[0]["beginDate"] == "2025-09-01"
        assert rows[0]["endDate"] == "2025-12-20"
        assert rows[0]["primary"] == "TRUE"

    def test_write_academic_sessions(
        self, writer: OneRosterCSVWriter, output_dir: Path
    ) -> None:
        """Test writing academic sessions to CSV."""
        now = datetime(2025, 10, 27, 10, 30, 0)
        start_date = datetime(2025, 9, 1)
        end_date = datetime(2025, 12, 20)

        session = OneRosterAcademicSession(
            sourced_id="550e8400-e29b-41d4-a716-446655440008",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=now,
            title="Fall 2025",
            type="term",
            start_date=start_date,
            end_date=end_date,
            school_year="2025",
        )

        data_model = OneRosterDataModel(academic_sessions=[session])
        file_path = writer.write_academic_sessions(data_model)

        assert file_path.exists()
        assert file_path.name == "academicSessions.csv"

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["title"] == "Fall 2025"
        assert rows[0]["startDate"] == "2025-09-01"
        assert rows[0]["endDate"] == "2025-12-20"

    def test_write_all(
        self, writer: OneRosterCSVWriter, sample_data_model: OneRosterDataModel
    ) -> None:
        """Test writing all OneRoster files."""
        written_files = writer.write_all(sample_data_model)

        assert "orgs" in written_files
        assert "users" in written_files
        assert written_files["orgs"].exists()
        assert written_files["users"].exists()

    def test_write_all_only_writes_non_empty_lists(
        self, writer: OneRosterCSVWriter, output_dir: Path
    ) -> None:
        """Test that write_all only creates files for non-empty entity lists."""
        # Create data model with only orgs
        now = datetime(2025, 10, 27, 10, 30, 0)
        org = OneRosterOrg(
            sourced_id="550e8400-e29b-41d4-a716-446655440001",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=now,
            name="Test School",
            type=OrgType.SCHOOL,
        )

        data_model = OneRosterDataModel(orgs=[org])
        written_files = writer.write_all(data_model)

        # Only orgs file should be written
        assert "orgs" in written_files
        assert "users" not in written_files
        assert "classes" not in written_files
