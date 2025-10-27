"""Unit tests for SDS data models."""

import pytest
from datetime import datetime
from sds2roster.models.sds import (
    SDSSchool,
    SDSStudent,
    SDSTeacher,
    SDSSection,
    SDSEnrollment,
    SDSDataModel,
    SDSStatus,
)


class TestSDSSchool:
    """Test suite for SDSSchool model."""

    def test_create_valid_school(self) -> None:
        """Test creating a valid school."""
        school = SDSSchool(
            sis_id="SCH001",
            name="Tokyo International School",
            school_number="TIS-001",
        )
        assert school.sis_id == "SCH001"
        assert school.name == "Tokyo International School"
        assert school.school_number == "TIS-001"

    def test_create_school_without_optional_fields(self) -> None:
        """Test creating a school without optional fields."""
        school = SDSSchool(sis_id="SCH001", name="Test School")
        assert school.sis_id == "SCH001"
        assert school.name == "Test School"
        assert school.school_number is None

    def test_school_strips_whitespace(self) -> None:
        """Test that school model strips whitespace."""
        school = SDSSchool(
            sis_id="  SCH001  ", name="  Test School  ", school_number="  NUM001  "
        )
        assert school.sis_id == "SCH001"
        assert school.name == "Test School"
        assert school.school_number == "NUM001"  # All string fields are stripped

    def test_school_empty_sis_id_raises_error(self) -> None:
        """Test that empty SIS ID raises validation error."""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            SDSSchool(sis_id="", name="Test School")

    def test_school_empty_name_raises_error(self) -> None:
        """Test that empty name raises validation error."""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            SDSSchool(sis_id="SCH001", name="")


class TestSDSStudent:
    """Test suite for SDSStudent model."""

    def test_create_valid_student(self) -> None:
        """Test creating a valid student."""
        student = SDSStudent(
            sis_id="STU001",
            school_sis_id="SCH001",
            username="john.doe",
            first_name="John",
            last_name="Doe",
            middle_name="M",
            grade="10",
            secondary_email="john@example.com",
            student_number="2024001",
        )
        assert student.sis_id == "STU001"
        assert student.username == "john.doe"
        assert student.first_name == "John"
        assert student.last_name == "Doe"
        assert student.grade == "10"
        assert student.status == SDSStatus.ACTIVE

    def test_student_required_fields_only(self) -> None:
        """Test creating a student with required fields only."""
        student = SDSStudent(
            sis_id="STU001",
            school_sis_id="SCH001",
            username="jane.doe",
            first_name="Jane",
            last_name="Doe",
        )
        assert student.middle_name is None
        assert student.grade is None
        assert student.secondary_email is None

    def test_student_empty_required_field_raises_error(self) -> None:
        """Test that empty required field raises validation error."""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            SDSStudent(
                sis_id="",
                school_sis_id="SCH001",
                username="test",
                first_name="Test",
                last_name="User",
            )

    def test_student_empty_username_raises_error(self) -> None:
        """Test that empty username raises validation error."""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            SDSStudent(
                sis_id="STU001",
                school_sis_id="SCH001",
                username="",
                first_name="Test",
                last_name="User",
            )


class TestSDSTeacher:
    """Test suite for SDSTeacher model."""

    def test_create_valid_teacher(self) -> None:
        """Test creating a valid teacher."""
        teacher = SDSTeacher(
            sis_id="TEA001",
            school_sis_id="SCH001",
            username="teacher.one",
            first_name="Alice",
            last_name="Smith",
            middle_name="B",
            secondary_email="alice@school.com",
            teacher_number="T001",
        )
        assert teacher.sis_id == "TEA001"
        assert teacher.username == "teacher.one"
        assert teacher.first_name == "Alice"
        assert teacher.last_name == "Smith"
        assert teacher.status == SDSStatus.ACTIVE


class TestSDSSection:
    """Test suite for SDSSection model."""

    def test_create_valid_section(self) -> None:
        """Test creating a valid section."""
        section = SDSSection(
            sis_id="SEC001",
            school_sis_id="SCH001",
            section_name="Math 101",
            section_number="M101",
            course_name="Mathematics",
            course_number="MATH101",
        )
        assert section.sis_id == "SEC001"
        assert section.section_name == "Math 101"
        assert section.course_name == "Mathematics"

    def test_section_with_term_dates(self) -> None:
        """Test creating a section with term dates."""
        start_date = datetime(2025, 9, 1)
        end_date = datetime(2025, 12, 20)

        section = SDSSection(
            sis_id="SEC001",
            school_sis_id="SCH001",
            section_name="Math 101",
            term_start_date=start_date,
            term_end_date=end_date,
        )
        assert section.term_start_date == start_date
        assert section.term_end_date == end_date

    def test_section_empty_sis_id_raises_error(self) -> None:
        """Test that empty sis_id raises validation error."""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            SDSSection(
                sis_id="",
                school_sis_id="SCH001",
                section_name="Math 101",
                section_number="M101",
                course_name="Mathematics",
                course_number="MATH101",
            )


class TestSDSEnrollment:
    """Test suite for SDSEnrollment model."""

    def test_create_student_enrollment(self) -> None:
        """Test creating a student enrollment."""
        enrollment = SDSEnrollment(
            section_sis_id="SEC001", sis_id="STU001", role="student"
        )
        assert enrollment.section_sis_id == "SEC001"
        assert enrollment.sis_id == "STU001"
        assert enrollment.role == "student"

    def test_create_teacher_enrollment(self) -> None:
        """Test creating a teacher enrollment."""
        enrollment = SDSEnrollment(
            section_sis_id="SEC001", sis_id="TEA001", role="teacher"
        )
        assert enrollment.role == "teacher"

    def test_enrollment_role_case_insensitive(self) -> None:
        """Test that role validation is case insensitive."""
        enrollment = SDSEnrollment(
            section_sis_id="SEC001", sis_id="STU001", role="STUDENT"
        )
        assert enrollment.role == "student"

    def test_enrollment_invalid_role_raises_error(self) -> None:
        """Test that invalid role raises validation error."""
        with pytest.raises(ValueError, match="Role must be 'student' or 'teacher'"):
            SDSEnrollment(section_sis_id="SEC001", sis_id="STU001", role="invalid")


class TestSDSDataModel:
    """Test suite for SDSDataModel container."""

    def test_create_empty_data_model(self) -> None:
        """Test creating an empty data model."""
        model = SDSDataModel()
        assert len(model.schools) == 0
        assert len(model.students) == 0
        assert len(model.teachers) == 0
        assert len(model.sections) == 0
        assert len(model.enrollments) == 0

    def test_create_data_model_with_data(self) -> None:
        """Test creating a data model with data."""
        school = SDSSchool(sis_id="SCH001", name="Test School")
        student = SDSStudent(
            sis_id="STU001",
            school_sis_id="SCH001",
            username="student1",
            first_name="Test",
            last_name="Student",
        )

        model = SDSDataModel(schools=[school], students=[student])
        assert len(model.schools) == 1
        assert len(model.students) == 1

    def test_get_school_by_sis_id(self) -> None:
        """Test getting school by SIS ID."""
        school = SDSSchool(sis_id="SCH001", name="Test School")
        model = SDSDataModel(schools=[school])

        found_school = model.get_school_by_sis_id("SCH001")
        assert found_school is not None
        assert found_school.sis_id == "SCH001"

    def test_get_school_by_sis_id_not_found(self) -> None:
        """Test getting school by SIS ID when not found."""
        model = SDSDataModel()
        found_school = model.get_school_by_sis_id("INVALID")
        assert found_school is None

    def test_get_student_by_sis_id(self) -> None:
        """Test getting student by SIS ID."""
        student = SDSStudent(
            sis_id="STU001",
            school_sis_id="SCH001",
            username="test",
            first_name="Test",
            last_name="Student",
        )
        model = SDSDataModel(students=[student])

        found_student = model.get_student_by_sis_id("STU001")
        assert found_student is not None
        assert found_student.username == "test"
