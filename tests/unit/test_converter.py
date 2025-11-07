"""Unit tests for SDS to OneRoster converter."""

from datetime import datetime, timezone

from sds2roster.converter import SDSToOneRosterConverter
from sds2roster.models.oneroster import (
    ClassType,
    EnrollmentRole,
    OneRosterStatus,
    OrgType,
    RoleType,
)
from sds2roster.models.sds import SDSDataModel, SDSEnrollment, SDSSchool, SDSSection, SDSStudent, SDSTeacher


class TestSDSToOneRosterConverter:
    """Test suite for SDSToOneRosterConverter."""

    def test_converter_initialization(self) -> None:
        """Test converter can be initialized."""
        converter = SDSToOneRosterConverter()
        assert converter is not None
        assert hasattr(converter, "conversion_timestamp")

    def test_convert_empty_data(self) -> None:
        """Test convert with empty SDS data model."""
        converter = SDSToOneRosterConverter()
        empty_data = SDSDataModel()

        result = converter.convert(empty_data)

        assert result is not None
        assert len(result.orgs) == 0
        assert len(result.users) == 0
        assert len(result.courses) == 0
        assert len(result.classes) == 0
        assert len(result.enrollments) == 0
        assert len(result.academic_sessions) == 0

    def test_convert_organizations(self) -> None:
        """Test converting schools to organizations."""
        converter = SDSToOneRosterConverter()
        school = SDSSchool(
            sis_id="school001",
            name="Test School",
            school_number="001",
        )
        sds_data = SDSDataModel(schools=[school])

        result = converter.convert(sds_data)

        assert len(result.orgs) == 1
        org = result.orgs[0]
        assert org.name == "Test School"
        assert org.type == OrgType.SCHOOL
        assert org.identifier == "001"
        assert org.status == OneRosterStatus.ACTIVE
        assert org.parent_sourced_id is None  # Should be None for schools without parent

    def test_convert_users_students(self) -> None:
        """Test converting students to users."""
        converter = SDSToOneRosterConverter()
        student = SDSStudent(
            sis_id="student001",
            school_sis_id="school001",
            username="john.doe",
            first_name="John",
            last_name="Doe",
            grade="10",
        )
        sds_data = SDSDataModel(students=[student])

        result = converter.convert(sds_data)

        assert len(result.users) == 1
        user = result.users[0]
        assert user.role == RoleType.STUDENT
        assert user.given_name == "John"
        assert user.family_name == "Doe"
        assert user.username == "john.doe"
        assert user.grades == "10"
        assert user.status == OneRosterStatus.ACTIVE

    def test_convert_users_teachers(self) -> None:
        """Test converting teachers to users."""
        converter = SDSToOneRosterConverter()
        teacher = SDSTeacher(
            sis_id="teacher001",
            school_sis_id="school001",
            username="jane.smith",
            first_name="Jane",
            last_name="Smith",
        )
        sds_data = SDSDataModel(teachers=[teacher])

        result = converter.convert(sds_data)

        assert len(result.users) == 1
        user = result.users[0]
        assert user.role == RoleType.TEACHER
        assert user.given_name == "Jane"
        assert user.family_name == "Smith"
        assert user.username == "jane.smith"
        assert user.status == OneRosterStatus.ACTIVE

    def test_convert_courses_from_sections(self) -> None:
        """Test extracting unique courses from sections."""
        converter = SDSToOneRosterConverter()
        section1 = SDSSection(
            sis_id="section001",
            school_sis_id="school001",
            section_name="Math 101 A",
            section_number="101A",
            course_name="Mathematics 101",
            course_number="MATH101",
        )
        section2 = SDSSection(
            sis_id="section002",
            school_sis_id="school001",
            section_name="Math 101 B",
            section_number="101B",
            course_name="Mathematics 101",
            course_number="MATH101",
        )
        sds_data = SDSDataModel(sections=[section1, section2])

        result = converter.convert(sds_data)

        # Should create only one course (deduplicated)
        assert len(result.courses) == 1
        course = result.courses[0]
        assert course.title == "Mathematics 101"
        assert course.course_code == "MATH101"
        assert course.status == OneRosterStatus.ACTIVE

    def test_convert_classes_from_sections(self) -> None:
        """Test converting sections to classes."""
        converter = SDSToOneRosterConverter()
        section = SDSSection(
            sis_id="section001",
            school_sis_id="school001",
            section_name="Math 101 A",
            section_number="101A",
            course_name="Mathematics 101",
            course_number="MATH101",
            term_sis_id="fall2024",
        )
        sds_data = SDSDataModel(sections=[section])

        result = converter.convert(sds_data)

        assert len(result.classes) == 1
        cls = result.classes[0]
        assert cls.title == "Math 101 A"
        assert cls.class_code == "101A"
        assert cls.class_type == ClassType.SCHEDULED
        assert cls.status == OneRosterStatus.ACTIVE

    def test_convert_enrollments_student(self) -> None:
        """Test converting student enrollments."""
        converter = SDSToOneRosterConverter()
        section = SDSSection(
            sis_id="section001",
            school_sis_id="school001",
            section_name="Math 101 A",
            section_number="101A",
        )
        enrollment = SDSEnrollment(
            sis_id="student001",
            section_sis_id="section001",
            role="student",
        )
        sds_data = SDSDataModel(sections=[section], enrollments=[enrollment])

        result = converter.convert(sds_data)

        assert len(result.enrollments) == 1
        enr = result.enrollments[0]
        assert enr.role == EnrollmentRole.STUDENT
        assert enr.primary is None  # Students don't have primary flag
        assert enr.status == OneRosterStatus.ACTIVE

    def test_convert_enrollments_teacher(self) -> None:
        """Test converting teacher enrollments."""
        converter = SDSToOneRosterConverter()
        section = SDSSection(
            sis_id="section001",
            school_sis_id="school001",
            section_name="Math 101 A",
            section_number="101A",
        )
        enrollment = SDSEnrollment(
            sis_id="teacher001",
            section_sis_id="section001",
            role="teacher",
        )
        sds_data = SDSDataModel(sections=[section], enrollments=[enrollment])

        result = converter.convert(sds_data)

        assert len(result.enrollments) == 1
        enr = result.enrollments[0]
        assert enr.role == EnrollmentRole.TEACHER
        assert enr.primary is True  # Teachers are primary by default
        assert enr.status == OneRosterStatus.ACTIVE

    def test_convert_academic_sessions(self) -> None:
        """Test extracting academic sessions from sections."""
        converter = SDSToOneRosterConverter()
        section1 = SDSSection(
            sis_id="section001",
            school_sis_id="school001",
            section_name="Math 101 A",
            section_number="101A",
            term_sis_id="fall2024",
            term_name="Fall 2024",
            term_start_date=datetime(2024, 9, 1, tzinfo=timezone.utc),
            term_end_date=datetime(2024, 12, 20, tzinfo=timezone.utc),
        )
        section2 = SDSSection(
            sis_id="section002",
            school_sis_id="school001",
            section_name="Math 101 B",
            section_number="101B",
            term_sis_id="fall2024",  # Same term
            term_name="Fall 2024",
            term_start_date=datetime(2024, 9, 1, tzinfo=timezone.utc),
            term_end_date=datetime(2024, 12, 20, tzinfo=timezone.utc),
        )
        sds_data = SDSDataModel(sections=[section1, section2])

        result = converter.convert(sds_data)

        # Should create only one academic session (deduplicated)
        assert len(result.academic_sessions) == 1
        session = result.academic_sessions[0]
        assert session.title == "Fall 2024"
        assert session.type == "term"
        assert session.school_year == "2024"
        assert session.status == OneRosterStatus.ACTIVE

    def test_convert_full_dataset(self) -> None:
        """Test converting a complete SDS dataset."""
        converter = SDSToOneRosterConverter()

        # Create complete test data
        school = SDSSchool(
            sis_id="school001",
            name="Test School",
            school_number="001",
        )
        student = SDSStudent(
            sis_id="student001",
            school_sis_id="school001",
            username="john.doe",
            first_name="John",
            last_name="Doe",
            grade="10",
        )
        teacher = SDSTeacher(
            sis_id="teacher001",
            school_sis_id="school001",
            username="jane.smith",
            first_name="Jane",
            last_name="Smith",
        )
        section = SDSSection(
            sis_id="section001",
            school_sis_id="school001",
            section_name="Math 101",
            section_number="101",
            course_name="Mathematics",
            course_number="MATH101",
            term_sis_id="fall2024",
            term_name="Fall 2024",
            term_start_date=datetime(2024, 9, 1, tzinfo=timezone.utc),
            term_end_date=datetime(2024, 12, 20, tzinfo=timezone.utc),
        )
        student_enrollment = SDSEnrollment(
            sis_id="student001",
            section_sis_id="section001",
            role="student",
        )
        teacher_enrollment = SDSEnrollment(
            sis_id="teacher001",
            section_sis_id="section001",
            role="teacher",
        )

        sds_data = SDSDataModel(
            schools=[school],
            students=[student],
            teachers=[teacher],
            sections=[section],
            enrollments=[student_enrollment, teacher_enrollment],
        )

        result = converter.convert(sds_data)

        # Verify all entities were created
        assert len(result.orgs) == 1
        assert len(result.users) == 2  # 1 student + 1 teacher
        assert len(result.courses) == 1
        assert len(result.classes) == 1
        assert len(result.enrollments) == 2  # 1 student + 1 teacher enrollment
        assert len(result.academic_sessions) == 1

        # Verify data integrity
        assert result.orgs[0].name == "Test School"
        assert any(u.role == RoleType.STUDENT for u in result.users)
        assert any(u.role == RoleType.TEACHER for u in result.users)
        assert result.courses[0].title == "Mathematics"
        assert result.classes[0].title == "Math 101"
        assert any(e.role == EnrollmentRole.STUDENT for e in result.enrollments)
        assert any(e.role == EnrollmentRole.TEACHER for e in result.enrollments)
        assert result.academic_sessions[0].title == "Fall 2024"

