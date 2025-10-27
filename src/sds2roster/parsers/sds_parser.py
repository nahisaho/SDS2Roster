"""SDS CSV file parser.

This module provides functionality to parse Microsoft School Data Sync (SDS)
CSV files into SDS data models.
"""

import csv
from pathlib import Path
from typing import Optional

from ..models.sds import (
    SDSDataModel,
    SDSEnrollment,
    SDSSchool,
    SDSSection,
    SDSStatus,
    SDSStudent,
    SDSTeacher,
)


class SDSCSVParser:
    """Parser for SDS CSV files.

    This class reads SDS CSV files and creates SDSDataModel instances.
    Supports all SDS entity types: schools, students, teachers, sections, and enrollments.
    """

    def __init__(self, base_path: Optional[Path] = None) -> None:
        """Initialize SDS CSV parser.

        Args:
            base_path: Base directory path containing SDS CSV files.
                      If None, file paths must be provided as absolute paths.
        """
        self.base_path = base_path or Path.cwd()

    def parse_schools(self, file_path: Path) -> list[SDSSchool]:
        """Parse school.csv file.

        Expected columns: SIS ID, Name, School Number

        Args:
            file_path: Path to school.csv file

        Returns:
            List of SDSSchool objects

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If CSV format is invalid
        """
        schools = []
        full_path = self._resolve_path(file_path)

        with open(full_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                school = SDSSchool(
                    sis_id=row["SIS ID"],
                    name=row["Name"],
                    school_number=row.get("School Number"),
                )
                schools.append(school)

        return schools

    def parse_students(self, file_path: Path) -> list[SDSStudent]:
        """Parse student.csv file.

        Expected columns: SIS ID, School SIS ID, Username, First Name, Last Name,
                         Middle Name (optional), Grade (optional), Secondary Email (optional),
                         Student Number (optional), Status (optional)

        Args:
            file_path: Path to student.csv file

        Returns:
            List of SDSStudent objects

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If CSV format is invalid
        """
        students = []
        full_path = self._resolve_path(file_path)

        with open(full_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse status if provided
                status = SDSStatus.ACTIVE
                if row.get("Status"):
                    status_value = row["Status"]
                    status = (
                        SDSStatus.ACTIVE
                        if status_value.lower() == "active"
                        else SDSStatus.INACTIVE
                    )

                student = SDSStudent(
                    sis_id=row["SIS ID"],
                    school_sis_id=row["School SIS ID"],
                    username=row["Username"],
                    first_name=row["First Name"],
                    last_name=row["Last Name"],
                    middle_name=row.get("Middle Name"),
                    grade=row.get("Grade"),
                    secondary_email=row.get("Secondary Email"),
                    student_number=row.get("Student Number"),
                    status=status,
                )
                students.append(student)

        return students

    def parse_teachers(self, file_path: Path) -> list[SDSTeacher]:
        """Parse teacher.csv file.

        Expected columns: SIS ID, School SIS ID, Username, First Name, Last Name,
                         Middle Name (optional), Secondary Email (optional),
                         Teacher Number (optional), Status (optional)

        Args:
            file_path: Path to teacher.csv file

        Returns:
            List of SDSTeacher objects

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If CSV format is invalid
        """
        teachers = []
        full_path = self._resolve_path(file_path)

        with open(full_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse status if provided
                status = SDSStatus.ACTIVE
                if row.get("Status"):
                    status_value = row["Status"]
                    status = (
                        SDSStatus.ACTIVE
                        if status_value.lower() == "active"
                        else SDSStatus.INACTIVE
                    )

                teacher = SDSTeacher(
                    sis_id=row["SIS ID"],
                    school_sis_id=row["School SIS ID"],
                    username=row["Username"],
                    first_name=row["First Name"],
                    last_name=row["Last Name"],
                    middle_name=row.get("Middle Name"),
                    secondary_email=row.get("Secondary Email"),
                    teacher_number=row.get("Teacher Number"),
                    status=status,
                )
                teachers.append(teacher)

        return teachers

    def parse_sections(self, file_path: Path) -> list[SDSSection]:
        """Parse section.csv file.

        Expected columns: SIS ID, School SIS ID, Section Name, Section Number (optional),
                         Term SIS ID (optional), Term Name (optional), Term Start Date (optional),
                         Term End Date (optional), Course Name (optional), Course Number (optional),
                         Course Description (optional), Status (optional)

        Args:
            file_path: Path to section.csv file

        Returns:
            List of SDSSection objects

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If CSV format is invalid
        """
        from datetime import datetime

        sections = []
        full_path = self._resolve_path(file_path)

        with open(full_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse dates if provided
                term_start_date = None
                term_end_date = None
                if row.get("Term Start Date"):
                    term_start_date = datetime.fromisoformat(row["Term Start Date"])
                if row.get("Term End Date"):
                    term_end_date = datetime.fromisoformat(row["Term End Date"])

                # Parse status if provided
                status = SDSStatus.ACTIVE
                if row.get("Status"):
                    status_value = row["Status"]
                    status = (
                        SDSStatus.ACTIVE
                        if status_value.lower() == "active"
                        else SDSStatus.INACTIVE
                    )

                section = SDSSection(
                    sis_id=row["SIS ID"],
                    school_sis_id=row["School SIS ID"],
                    section_name=row["Section Name"],
                    section_number=row.get("Section Number"),
                    term_sis_id=row.get("Term SIS ID"),
                    term_name=row.get("Term Name"),
                    term_start_date=term_start_date,
                    term_end_date=term_end_date,
                    course_name=row.get("Course Name"),
                    course_number=row.get("Course Number"),
                    course_description=row.get("Course Description"),
                    status=status,
                )
                sections.append(section)

        return sections

    def parse_enrollments(self, file_path: Path, role: str = "student") -> list[SDSEnrollment]:
        """Parse enrollment CSV file (studentEnrollment.csv or teacherRoster.csv).

        Expected columns: Section SIS ID, SIS ID

        Args:
            file_path: Path to enrollment CSV file
            role: Role type - "student" or "teacher"

        Returns:
            List of SDSEnrollment objects

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If CSV format is invalid or role is invalid
        """
        if role.lower() not in ("student", "teacher"):
            raise ValueError("Role must be 'student' or 'teacher'")

        enrollments = []
        full_path = self._resolve_path(file_path)

        with open(full_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                enrollment = SDSEnrollment(
                    section_sis_id=row["Section SIS ID"],
                    sis_id=row["SIS ID"],
                    role=role.lower(),
                )
                enrollments.append(enrollment)

        return enrollments

    def parse_all(
        self,
        school_file: Path,
        student_file: Path,
        teacher_file: Path,
        section_file: Path,
        student_enrollment_file: Path,
        teacher_roster_file: Path,
    ) -> SDSDataModel:
        """Parse all SDS CSV files and create a complete data model.

        Args:
            school_file: Path to school.csv
            student_file: Path to student.csv
            teacher_file: Path to teacher.csv
            section_file: Path to section.csv
            student_enrollment_file: Path to studentEnrollment.csv
            teacher_roster_file: Path to teacherRoster.csv

        Returns:
            Complete SDSDataModel with all entities

        Raises:
            FileNotFoundError: If any file does not exist
            ValueError: If any CSV format is invalid
        """
        schools = self.parse_schools(school_file)
        students = self.parse_students(student_file)
        teachers = self.parse_teachers(teacher_file)
        sections = self.parse_sections(section_file)

        # Parse both student and teacher enrollments
        student_enrollments = self.parse_enrollments(student_enrollment_file, "student")
        teacher_enrollments = self.parse_enrollments(teacher_roster_file, "teacher")

        # Combine all enrollments
        all_enrollments = student_enrollments + teacher_enrollments

        return SDSDataModel(
            schools=schools,
            students=students,
            teachers=teachers,
            sections=sections,
            enrollments=all_enrollments,
        )

    def _resolve_path(self, file_path: Path) -> Path:
        """Resolve file path relative to base_path if not absolute.

        Args:
            file_path: File path to resolve

        Returns:
            Absolute file path
        """
        if file_path.is_absolute():
            return file_path
        return self.base_path / file_path
