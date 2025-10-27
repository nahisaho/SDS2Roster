"""Unit tests for SDS CSV parser."""

from pathlib import Path

import pytest

from sds2roster.models.sds import SDSStatus
from sds2roster.parsers.sds_parser import SDSCSVParser


@pytest.fixture
def fixtures_dir() -> Path:
    """Get path to test fixtures directory."""
    return Path(__file__).parent.parent / "fixtures" / "sds"


@pytest.fixture
def parser(fixtures_dir: Path) -> SDSCSVParser:
    """Create SDS CSV parser with fixtures directory."""
    return SDSCSVParser(fixtures_dir)


class TestSDSCSVParser:
    """Tests for SDS CSV parser."""

    def test_parse_schools(self, parser: SDSCSVParser) -> None:
        """Test parsing school.csv file."""
        schools = parser.parse_schools(Path("school.csv"))

        assert len(schools) == 2
        assert schools[0].sis_id == "SCH001"
        assert schools[0].name == "Tokyo International School"
        assert schools[0].school_number == "TIS-001"
        assert schools[1].sis_id == "SCH002"
        assert schools[1].name == "Osaka Tech High School"

    def test_parse_students(self, parser: SDSCSVParser) -> None:
        """Test parsing student.csv file."""
        students = parser.parse_students(Path("student.csv"))

        assert len(students) == 3
        assert students[0].sis_id == "STU001"
        assert students[0].school_sis_id == "SCH001"
        assert students[0].username == "taro.yamada"
        assert students[0].first_name == "Taro"
        assert students[0].last_name == "Yamada"
        assert students[0].grade == "10"
        assert students[0].secondary_email == "taro@example.com"
        assert students[0].status == SDSStatus.ACTIVE

    def test_parse_students_with_middle_name(self, parser: SDSCSVParser) -> None:
        """Test parsing student with middle name."""
        students = parser.parse_students(Path("student.csv"))

        assert students[1].middle_name == "M"

    def test_parse_teachers(self, parser: SDSCSVParser) -> None:
        """Test parsing teacher.csv file."""
        teachers = parser.parse_teachers(Path("teacher.csv"))

        assert len(teachers) == 2
        assert teachers[0].sis_id == "TEA001"
        assert teachers[0].school_sis_id == "SCH001"
        assert teachers[0].username == "john.smith"
        assert teachers[0].first_name == "John"
        assert teachers[0].last_name == "Smith"
        assert teachers[0].secondary_email == "john.smith@example.com"
        assert teachers[0].teacher_number == "T001"

    def test_parse_sections(self, parser: SDSCSVParser) -> None:
        """Test parsing section.csv file."""
        sections = parser.parse_sections(Path("section.csv"))

        assert len(sections) == 2
        assert sections[0].sis_id == "SEC001"
        assert sections[0].school_sis_id == "SCH001"
        assert sections[0].section_name == "Math 101 - Period 1"
        assert sections[0].section_number == "SEC-001"
        assert sections[0].term_sis_id == "TERM001"
        assert sections[0].term_name == "Fall 2025"
        assert sections[0].course_name == "Mathematics I"
        assert sections[0].course_number == "MATH101"

    def test_parse_sections_with_dates(self, parser: SDSCSVParser) -> None:
        """Test parsing sections with term dates."""
        from datetime import datetime

        sections = parser.parse_sections(Path("section.csv"))

        assert sections[0].term_start_date == datetime(2025, 9, 1)
        assert sections[0].term_end_date == datetime(2025, 12, 20)

    def test_parse_student_enrollments(self, parser: SDSCSVParser) -> None:
        """Test parsing studentEnrollment.csv file."""
        enrollments = parser.parse_enrollments(Path("studentEnrollment.csv"), "student")

        assert len(enrollments) == 3
        assert enrollments[0].section_sis_id == "SEC001"
        assert enrollments[0].sis_id == "STU001"
        assert enrollments[0].role == "student"

    def test_parse_teacher_enrollments(self, parser: SDSCSVParser) -> None:
        """Test parsing teacherRoster.csv file."""
        enrollments = parser.parse_enrollments(Path("teacherRoster.csv"), "teacher")

        assert len(enrollments) == 2
        assert enrollments[0].section_sis_id == "SEC001"
        assert enrollments[0].sis_id == "TEA001"
        assert enrollments[0].role == "teacher"

    def test_parse_enrollments_invalid_role_raises_error(self, parser: SDSCSVParser) -> None:
        """Test that invalid role raises error."""
        with pytest.raises(ValueError, match="Role must be 'student' or 'teacher'"):
            parser.parse_enrollments(Path("studentEnrollment.csv"), "invalid")

    def test_parse_all(self, parser: SDSCSVParser) -> None:
        """Test parsing all SDS files into complete data model."""
        data_model = parser.parse_all(
            school_file=Path("school.csv"),
            student_file=Path("student.csv"),
            teacher_file=Path("teacher.csv"),
            section_file=Path("section.csv"),
            student_enrollment_file=Path("studentEnrollment.csv"),
            teacher_roster_file=Path("teacherRoster.csv"),
        )

        assert len(data_model.schools) == 2
        assert len(data_model.students) == 3
        assert len(data_model.teachers) == 2
        assert len(data_model.sections) == 2
        assert len(data_model.enrollments) == 5  # 3 students + 2 teachers

    def test_parse_all_enrollments_combined(self, parser: SDSCSVParser) -> None:
        """Test that parse_all combines student and teacher enrollments."""
        data_model = parser.parse_all(
            school_file=Path("school.csv"),
            student_file=Path("student.csv"),
            teacher_file=Path("teacher.csv"),
            section_file=Path("section.csv"),
            student_enrollment_file=Path("studentEnrollment.csv"),
            teacher_roster_file=Path("teacherRoster.csv"),
        )

        student_enrollments = [e for e in data_model.enrollments if e.role == "student"]
        teacher_enrollments = [e for e in data_model.enrollments if e.role == "teacher"]

        assert len(student_enrollments) == 3
        assert len(teacher_enrollments) == 2

    def test_parse_file_not_found(self, parser: SDSCSVParser) -> None:
        """Test that FileNotFoundError is raised for missing file."""
        with pytest.raises(FileNotFoundError):
            parser.parse_schools(Path("nonexistent.csv"))

    def test_resolve_absolute_path(self, parser: SDSCSVParser, tmp_path: Path) -> None:
        """Test that absolute paths are used as-is."""
        # Create a temporary CSV file
        test_file = tmp_path / "test.csv"
        test_file.write_text("SIS ID,Name,School Number\nTEST,Test School,T001\n")

        schools = parser.parse_schools(test_file)
        assert len(schools) == 1
        assert schools[0].sis_id == "TEST"
