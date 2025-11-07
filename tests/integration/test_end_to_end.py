"""End-to-end integration tests for SDS to OneRoster conversion.

These tests verify the complete conversion pipeline from reading SDS CSV files
to writing OneRoster CSV files, ensuring data integrity throughout the process.

These tests run locally without Azure dependencies.
"""

import csv
import json
from pathlib import Path

import pytest

from sds2roster.converter import SDSToOneRosterConverter
from sds2roster.parsers.oneroster_writer import OneRosterCSVWriter
from sds2roster.parsers.sds_parser import SDSCSVParser

# Mark all tests in this module as integration tests (local only)
pytestmark = pytest.mark.integration


class TestEndToEndConversion:
    """Test complete conversion pipeline using test fixtures."""

    @pytest.fixture
    def fixtures_path(self) -> Path:
        """Path to SDS test fixtures."""
        return Path("tests/fixtures/sds")

    @pytest.fixture
    def output_path(self, tmp_path: Path) -> Path:
        """Path for OneRoster output files."""
        return tmp_path / "oneroster_output"

    def test_complete_conversion_pipeline(
        self, fixtures_path: Path, output_path: Path
    ) -> None:
        """Test complete conversion from SDS CSV to OneRoster CSV.

        This test verifies:
        1. SDS files can be parsed
        2. Conversion completes without errors
        3. OneRoster files are written
        4. All expected files exist
        5. Basic data integrity checks pass
        """
        # Step 1: Parse SDS files
        parser = SDSCSVParser()
        sds_data = parser.parse_all(
            school_file=fixtures_path / "school.csv",
            student_file=fixtures_path / "student.csv",
            teacher_file=fixtures_path / "teacher.csv",
            section_file=fixtures_path / "section.csv",
            student_enrollment_file=fixtures_path / "studentEnrollment.csv",
            teacher_roster_file=fixtures_path / "teacherRoster.csv",
        )

        # Verify parsed data counts
        assert len(sds_data.schools) == 2
        assert len(sds_data.students) == 3
        assert len(sds_data.teachers) == 2
        assert len(sds_data.sections) == 2
        assert len(sds_data.enrollments) == 5

        # Step 2: Convert to OneRoster
        converter = SDSToOneRosterConverter()
        oneroster_data = converter.convert(sds_data)

        # Verify converted data counts
        assert len(oneroster_data.orgs) == 2
        assert len(oneroster_data.users) == 5  # 3 students + 2 teachers
        assert len(oneroster_data.courses) == 2
        assert len(oneroster_data.classes) == 2
        assert len(oneroster_data.enrollments) == 5
        assert len(oneroster_data.academic_sessions) == 1

        # Step 3: Write OneRoster files
        writer = OneRosterCSVWriter(output_path)
        writer.write_all(oneroster_data)

        # Step 4: Verify all files were created
        expected_files = [
            "orgs.csv",
            "users.csv",
            "courses.csv",
            "classes.csv",
            "enrollments.csv",
            "academicSessions.csv",
        ]

        for file_name in expected_files:
            file_path = output_path / file_name
            assert file_path.exists(), f"{file_name} should exist"
            assert file_path.stat().st_size > 0, f"{file_name} should not be empty"

    def test_orgs_data_integrity(
        self, fixtures_path: Path, output_path: Path
    ) -> None:
        """Test organizations data integrity after conversion."""
        # Convert
        parser = SDSCSVParser()
        sds_data = parser.parse_all(
            school_file=fixtures_path / "school.csv",
            student_file=fixtures_path / "student.csv",
            teacher_file=fixtures_path / "teacher.csv",
            section_file=fixtures_path / "section.csv",
            student_enrollment_file=fixtures_path / "studentEnrollment.csv",
            teacher_roster_file=fixtures_path / "teacherRoster.csv",
        )

        converter = SDSToOneRosterConverter()
        oneroster_data = converter.convert(sds_data)

        writer = OneRosterCSVWriter(output_path)
        writer.write_orgs(oneroster_data)

        # Read and verify orgs.csv
        orgs_file = output_path / "orgs.csv"
        with open(orgs_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            orgs = list(reader)

        assert len(orgs) == 2

        # Verify first org (Tokyo International School)
        tokyo_org = next(o for o in orgs if "Tokyo" in o["name"])
        assert tokyo_org["name"] == "Tokyo International School"
        assert tokyo_org["type"] == "school"
        assert tokyo_org["identifier"] == "TIS-001"
        # OneRoster 1.2 spec: status and dateLastModified should be empty
        assert tokyo_org["status"] == ""
        assert tokyo_org["dateLastModified"] == ""

        # Verify metadata contains sis_id (if metadata field exists)
        if "metadata" in tokyo_org and tokyo_org["metadata"]:
            metadata = json.loads(tokyo_org["metadata"])
            assert "sis_id" in metadata
            assert metadata["sis_id"] == "SCH001"

    def test_users_data_integrity(
        self, fixtures_path: Path, output_path: Path
    ) -> None:
        """Test users data integrity after conversion."""
        # Convert
        parser = SDSCSVParser()
        sds_data = parser.parse_all(
            school_file=fixtures_path / "school.csv",
            student_file=fixtures_path / "student.csv",
            teacher_file=fixtures_path / "teacher.csv",
            section_file=fixtures_path / "section.csv",
            student_enrollment_file=fixtures_path / "studentEnrollment.csv",
            teacher_roster_file=fixtures_path / "teacherRoster.csv",
        )

        converter = SDSToOneRosterConverter()
        oneroster_data = converter.convert(sds_data)

        writer = OneRosterCSVWriter(output_path)
        writer.write_all(oneroster_data)

        # Read and verify users.csv
        users_file = output_path / "users.csv"
        with open(users_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            users = list(reader)

        assert len(users) == 5

        # Read roles.csv to verify user roles (if it exists)
        roles_file = output_path / "roles.csv"
        if roles_file.exists():
            with open(roles_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                roles = list(reader)

            # Count roles by type
            student_roles = [r for r in roles if r["role"] == "student"]
            teacher_roles = [r for r in roles if r["role"] == "teacher"]

            assert len(student_roles) == 3
            assert len(teacher_roles) == 2

        # Verify a student
        taro = next(u for u in users if u["username"] == "taro.yamada")
        assert taro["givenName"] == "Taro"
        assert taro["familyName"] == "Yamada"
        assert taro["grades"] == "10"
        assert taro["enabledUser"] == "TRUE"
        # OneRoster 1.2 spec: status and dateLastModified should be empty
        assert taro["status"] == ""
        assert taro["dateLastModified"] == ""

        # Verify the user has a student role in roles.csv (if it exists)
        if roles_file.exists():
            taro_roles = [r for r in roles if r["userSourcedId"] == taro["sourcedId"]]
            assert len(taro_roles) > 0
            assert any(r["role"] == "student" for r in taro_roles)

        # Verify userIds JSON (if the field exists)
        if "userIds" in taro and taro["userIds"]:
            user_ids = json.loads(taro["userIds"])
            assert isinstance(user_ids, list)
            assert len(user_ids) > 0
            assert user_ids[0]["type"] == "sisId"
            assert user_ids[0]["identifier"] == "STU001"

    def test_courses_deduplication(
        self, fixtures_path: Path, output_path: Path
    ) -> None:
        """Test that courses are deduplicated correctly."""
        # Convert
        parser = SDSCSVParser()
        sds_data = parser.parse_all(
            school_file=fixtures_path / "school.csv",
            student_file=fixtures_path / "student.csv",
            teacher_file=fixtures_path / "teacher.csv",
            section_file=fixtures_path / "section.csv",
            student_enrollment_file=fixtures_path / "studentEnrollment.csv",
            teacher_roster_file=fixtures_path / "teacherRoster.csv",
        )

        converter = SDSToOneRosterConverter()
        oneroster_data = converter.convert(sds_data)

        # Should have 2 unique courses even if multiple sections share them
        assert len(oneroster_data.courses) == 2

        writer = OneRosterCSVWriter(output_path)
        writer.write_courses(oneroster_data)

        # Read and verify courses.csv
        courses_file = output_path / "courses.csv"
        with open(courses_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            courses = list(reader)

        assert len(courses) == 2

        # Verify course data
        for course in courses:
            # OneRoster 1.2 spec: status and dateLastModified should be empty
            assert course["status"] == ""
            assert course["dateLastModified"] == ""
            assert course["title"]  # Should have a title
            assert course["orgSourcedId"]  # Should reference an org

    def test_classes_reference_courses(
        self, fixtures_path: Path, output_path: Path
    ) -> None:
        """Test that classes correctly reference their courses."""
        # Convert
        parser = SDSCSVParser()
        sds_data = parser.parse_all(
            school_file=fixtures_path / "school.csv",
            student_file=fixtures_path / "student.csv",
            teacher_file=fixtures_path / "teacher.csv",
            section_file=fixtures_path / "section.csv",
            student_enrollment_file=fixtures_path / "studentEnrollment.csv",
            teacher_roster_file=fixtures_path / "teacherRoster.csv",
        )

        converter = SDSToOneRosterConverter()
        oneroster_data = converter.convert(sds_data)

        writer = OneRosterCSVWriter(output_path)
        writer.write_courses(oneroster_data)
        writer.write_classes(oneroster_data)

        # Read courses
        courses_file = output_path / "courses.csv"
        with open(courses_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            courses = {c["sourcedId"]: c for c in reader}

        # Read classes
        classes_file = output_path / "classes.csv"
        with open(classes_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            classes = list(reader)

        assert len(classes) == 2

        # Verify each class references a valid course
        for cls in classes:
            course_id = cls["courseSourcedId"]
            assert course_id in courses, f"Class references non-existent course: {course_id}"
            # OneRoster 1.2 spec: status and dateLastModified should be empty
            assert cls["status"] == ""
            assert cls["dateLastModified"] == ""
            assert cls["classType"] == "scheduled"

    def test_enrollments_reference_integrity(
        self, fixtures_path: Path, output_path: Path
    ) -> None:
        """Test that enrollments correctly reference classes and users."""
        # Convert
        parser = SDSCSVParser()
        sds_data = parser.parse_all(
            school_file=fixtures_path / "school.csv",
            student_file=fixtures_path / "student.csv",
            teacher_file=fixtures_path / "teacher.csv",
            section_file=fixtures_path / "section.csv",
            student_enrollment_file=fixtures_path / "studentEnrollment.csv",
            teacher_roster_file=fixtures_path / "teacherRoster.csv",
        )

        converter = SDSToOneRosterConverter()
        oneroster_data = converter.convert(sds_data)

        writer = OneRosterCSVWriter(output_path)
        writer.write_users(oneroster_data)
        writer.write_classes(oneroster_data)
        writer.write_enrollments(oneroster_data)

        # Read users
        users_file = output_path / "users.csv"
        with open(users_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            users = {u["sourcedId"]: u for u in reader}

        # Read classes
        classes_file = output_path / "classes.csv"
        with open(classes_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            classes = {c["sourcedId"]: c for c in reader}

        # Read enrollments
        enrollments_file = output_path / "enrollments.csv"
        with open(enrollments_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            enrollments = list(reader)

        assert len(enrollments) == 5

        # Verify each enrollment references valid class and user
        for enrollment in enrollments:
            class_id = enrollment["classSourcedId"]
            user_id = enrollment["userSourcedId"]

            assert class_id in classes, f"Enrollment references non-existent class: {class_id}"
            assert user_id in users, f"Enrollment references non-existent user: {user_id}"
            # OneRoster 1.2 spec: status and dateLastModified should be empty
            assert enrollment["status"] == ""
            assert enrollment["dateLastModified"] == ""
            assert enrollment["role"] in ["student", "teacher"]

        # Verify teacher enrollments have primary=TRUE
        teacher_enrollments = [e for e in enrollments if e["role"] == "teacher"]
        for te in teacher_enrollments:
            assert te["primary"] == "TRUE"

        # Verify student enrollments don't have primary field set (or empty)
        student_enrollments = [e for e in enrollments if e["role"] == "student"]
        for se in student_enrollments:
            assert se["primary"] == ""

    def test_academic_sessions_data(
        self, fixtures_path: Path, output_path: Path
    ) -> None:
        """Test academic sessions data integrity."""
        # Convert
        parser = SDSCSVParser()
        sds_data = parser.parse_all(
            school_file=fixtures_path / "school.csv",
            student_file=fixtures_path / "student.csv",
            teacher_file=fixtures_path / "teacher.csv",
            section_file=fixtures_path / "section.csv",
            student_enrollment_file=fixtures_path / "studentEnrollment.csv",
            teacher_roster_file=fixtures_path / "teacherRoster.csv",
        )

        converter = SDSToOneRosterConverter()
        oneroster_data = converter.convert(sds_data)

        writer = OneRosterCSVWriter(output_path)
        writer.write_academic_sessions(oneroster_data)

        # Read academic sessions
        sessions_file = output_path / "academicSessions.csv"
        with open(sessions_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            sessions = list(reader)

        assert len(sessions) == 1

        # Verify session data
        session = sessions[0]
        # OneRoster 1.2 spec: status and dateLastModified should be empty
        assert session["status"] == ""
        assert session["dateLastModified"] == ""
        assert session["type"] == "term"
        assert session["title"]  # Should have a title
        assert session["startDate"]  # Should have start date
        assert session["endDate"]  # Should have end date
        assert session["schoolYear"]  # Should have school year

    def test_guid_consistency(self, fixtures_path: Path, output_path: Path) -> None:
        """Test that GUIDs are consistent across multiple conversions."""
        # First conversion
        parser1 = SDSCSVParser()
        sds_data1 = parser1.parse_all(
            school_file=fixtures_path / "school.csv",
            student_file=fixtures_path / "student.csv",
            teacher_file=fixtures_path / "teacher.csv",
            section_file=fixtures_path / "section.csv",
            student_enrollment_file=fixtures_path / "studentEnrollment.csv",
            teacher_roster_file=fixtures_path / "teacherRoster.csv",
        )

        converter1 = SDSToOneRosterConverter()
        oneroster_data1 = converter1.convert(sds_data1)

        # Second conversion
        parser2 = SDSCSVParser()
        sds_data2 = parser2.parse_all(
            school_file=fixtures_path / "school.csv",
            student_file=fixtures_path / "student.csv",
            teacher_file=fixtures_path / "teacher.csv",
            section_file=fixtures_path / "section.csv",
            student_enrollment_file=fixtures_path / "studentEnrollment.csv",
            teacher_roster_file=fixtures_path / "teacherRoster.csv",
        )

        converter2 = SDSToOneRosterConverter()
        oneroster_data2 = converter2.convert(sds_data2)

        # Compare GUIDs - they should be identical
        assert len(oneroster_data1.orgs) == len(oneroster_data2.orgs)
        for org1, org2 in zip(oneroster_data1.orgs, oneroster_data2.orgs):
            assert org1.sourced_id == org2.sourced_id

        assert len(oneroster_data1.users) == len(oneroster_data2.users)
        for user1, user2 in zip(oneroster_data1.users, oneroster_data2.users):
            assert user1.sourced_id == user2.sourced_id

        assert len(oneroster_data1.courses) == len(oneroster_data2.courses)
        for course1, course2 in zip(oneroster_data1.courses, oneroster_data2.courses):
            assert course1.sourced_id == course2.sourced_id

    def test_csv_format_compliance(
        self, fixtures_path: Path, output_path: Path
    ) -> None:
        """Test that generated CSV files are properly formatted."""
        # Convert
        parser = SDSCSVParser()
        sds_data = parser.parse_all(
            school_file=fixtures_path / "school.csv",
            student_file=fixtures_path / "student.csv",
            teacher_file=fixtures_path / "teacher.csv",
            section_file=fixtures_path / "section.csv",
            student_enrollment_file=fixtures_path / "studentEnrollment.csv",
            teacher_roster_file=fixtures_path / "teacherRoster.csv",
        )

        converter = SDSToOneRosterConverter()
        oneroster_data = converter.convert(sds_data)

        writer = OneRosterCSVWriter(output_path)
        writer.write_all(oneroster_data)

        # Verify each file has proper CSV format
        expected_files = [
            "orgs.csv",
            "users.csv",
            "courses.csv",
            "classes.csv",
            "enrollments.csv",
            "academicSessions.csv",
        ]

        for file_name in expected_files:
            file_path = output_path / file_name

            # Should be readable as CSV
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                # Should have headers
                assert reader.fieldnames is not None
                assert len(reader.fieldnames) > 0

                # Should have data rows
                assert len(rows) > 0

                # All rows should have same number of fields as headers
                for row in rows:
                    assert len(row) == len(reader.fieldnames)
