"""SDS (School Data Sync) data models.

This module contains Pydantic models for Microsoft SDS CSV format.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SDSStatus(str, Enum):
    """SDS entity status."""

    ACTIVE = "Active"
    INACTIVE = "Inactive"


class SDSSchool(BaseModel):
    """SDS School model (school.csv)."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    sis_id: str = Field(..., description="School SIS ID")
    name: str = Field(..., description="School name")
    school_number: Optional[str] = Field(None, description="School identifier number")

    @field_validator("sis_id", "name")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class SDSStudent(BaseModel):
    """SDS Student model (student.csv)."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    sis_id: str = Field(..., description="Student SIS ID")
    school_sis_id: str = Field(..., description="School SIS ID")
    username: str = Field(..., description="Student username")
    first_name: str = Field(..., description="Student first name")
    last_name: str = Field(..., description="Student last name")
    middle_name: Optional[str] = Field(None, description="Student middle name")
    grade: Optional[str] = Field(None, description="Student grade level")
    secondary_email: Optional[str] = Field(None, description="Student secondary email")
    student_number: Optional[str] = Field(None, description="Student number")
    status: SDSStatus = Field(SDSStatus.ACTIVE, description="Student status")

    @field_validator("sis_id", "school_sis_id", "username", "first_name", "last_name")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class SDSTeacher(BaseModel):
    """SDS Teacher model (teacher.csv)."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    sis_id: str = Field(..., description="Teacher SIS ID")
    school_sis_id: str = Field(..., description="School SIS ID")
    username: str = Field(..., description="Teacher username")
    first_name: str = Field(..., description="Teacher first name")
    last_name: str = Field(..., description="Teacher last name")
    middle_name: Optional[str] = Field(None, description="Teacher middle name")
    secondary_email: Optional[str] = Field(None, description="Teacher secondary email")
    teacher_number: Optional[str] = Field(None, description="Teacher number")
    status: SDSStatus = Field(SDSStatus.ACTIVE, description="Teacher status")

    @field_validator("sis_id", "school_sis_id", "username", "first_name", "last_name")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class SDSSection(BaseModel):
    """SDS Section model (section.csv)."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    sis_id: str = Field(..., description="Section SIS ID")
    school_sis_id: str = Field(..., description="School SIS ID")
    section_name: str = Field(..., description="Section name")
    section_number: Optional[str] = Field(None, description="Section number")
    term_sis_id: Optional[str] = Field(None, description="Term SIS ID")
    term_name: Optional[str] = Field(None, description="Term name")
    term_start_date: Optional[datetime] = Field(None, description="Term start date")
    term_end_date: Optional[datetime] = Field(None, description="Term end date")
    course_name: Optional[str] = Field(None, description="Course name")
    course_number: Optional[str] = Field(None, description="Course number")
    course_description: Optional[str] = Field(None, description="Course description")
    status: SDSStatus = Field(SDSStatus.ACTIVE, description="Section status")

    @field_validator("sis_id", "school_sis_id", "section_name")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class SDSEnrollment(BaseModel):
    """SDS Enrollment model (studentEnrollment.csv / teacherRoster.csv)."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    section_sis_id: str = Field(..., description="Section SIS ID")
    sis_id: str = Field(..., description="Student or Teacher SIS ID")
    role: str = Field(..., description="Role (student or teacher)")

    @field_validator("section_sis_id", "sis_id", "role")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate that role is either student or teacher."""
        v = v.strip().lower()
        if v not in ("student", "teacher"):
            raise ValueError("Role must be 'student' or 'teacher'")
        return v


class SDSDataModel(BaseModel):
    """Complete SDS data model container."""

    model_config = ConfigDict(populate_by_name=True)

    schools: list[SDSSchool] = Field(default_factory=list, description="List of schools")
    students: list[SDSStudent] = Field(default_factory=list, description="List of students")
    teachers: list[SDSTeacher] = Field(default_factory=list, description="List of teachers")
    sections: list[SDSSection] = Field(default_factory=list, description="List of sections")
    enrollments: list[SDSEnrollment] = Field(
        default_factory=list, description="List of enrollments"
    )

    def get_school_by_sis_id(self, sis_id: str) -> Optional[SDSSchool]:
        """Get school by SIS ID."""
        return next((s for s in self.schools if s.sis_id == sis_id), None)

    def get_student_by_sis_id(self, sis_id: str) -> Optional[SDSStudent]:
        """Get student by SIS ID."""
        return next((s for s in self.students if s.sis_id == sis_id), None)

    def get_teacher_by_sis_id(self, sis_id: str) -> Optional[SDSTeacher]:
        """Get teacher by SIS ID."""
        return next((t for t in self.teachers if t.sis_id == sis_id), None)

    def get_section_by_sis_id(self, sis_id: str) -> Optional[SDSSection]:
        """Get section by SIS ID."""
        return next((s for s in self.sections if s.sis_id == sis_id), None)
