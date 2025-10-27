"""OneRoster v1.2 data models.

This module contains Pydantic models for OneRoster v1.2 CSV format.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OneRosterStatus(str, Enum):
    """OneRoster entity status."""

    ACTIVE = "active"
    TOBEDELETED = "tobedeleted"
    INACTIVE = "inactive"


class OrgType(str, Enum):
    """Organization type."""

    DEPARTMENT = "department"
    SCHOOL = "school"
    DISTRICT = "district"
    LOCAL = "local"
    STATE = "state"
    NATIONAL = "national"


class RoleType(str, Enum):
    """User role type."""

    ADMINISTRATOR = "administrator"
    AIDE = "aide"
    GUARDIAN = "guardian"
    PARENT = "parent"
    PROCTOR = "proctor"
    RELATIVE = "relative"
    STUDENT = "student"
    TEACHER = "teacher"


class ClassType(str, Enum):
    """Class type."""

    HOMEROOM = "homeroom"
    SCHEDULED = "scheduled"


class EnrollmentRole(str, Enum):
    """Enrollment role."""

    ADMINISTRATOR = "administrator"
    AIDE = "aide"
    PROCTOR = "proctor"
    STUDENT = "student"
    TEACHER = "teacher"


class OneRosterOrg(BaseModel):
    """OneRoster Organization model (orgs.csv)."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    sourced_id: str = Field(..., description="Unique identifier (GUID)")
    status: OneRosterStatus = Field(..., description="Status")
    date_last_modified: datetime = Field(..., description="Last modification date")
    name: str = Field(..., description="Organization name")
    type: OrgType = Field(..., description="Organization type")
    identifier: Optional[str] = Field(None, description="Human-readable identifier")
    metadata: Optional[str] = Field(None, description="Metadata in JSON format")

    @field_validator("sourced_id", "name")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class OneRosterUser(BaseModel):
    """OneRoster User model (users.csv)."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    sourced_id: str = Field(..., description="Unique identifier (GUID)")
    status: OneRosterStatus = Field(..., description="Status")
    date_last_modified: datetime = Field(..., description="Last modification date")
    enabled_user: bool = Field(..., description="Whether user is enabled")
    org_sourced_ids: str = Field(..., description="Comma-separated list of org GUIDs")
    role: RoleType = Field(..., description="User role")
    username: str = Field(..., description="Username")
    user_ids: Optional[str] = Field(None, description="User IDs in JSON format")
    given_name: str = Field(..., description="Given name")
    family_name: str = Field(..., description="Family name")
    middle_name: Optional[str] = Field(None, description="Middle name")
    email: Optional[str] = Field(None, description="Email address")
    sms: Optional[str] = Field(None, description="SMS number")
    phone: Optional[str] = Field(None, description="Phone number")
    agents: Optional[str] = Field(None, description="Agents (guardians) in JSON format")
    grades: Optional[str] = Field(None, description="Grade levels (students only)")
    password: Optional[str] = Field(None, description="Password")

    @field_validator("sourced_id", "username", "given_name", "family_name")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class OneRosterCourse(BaseModel):
    """OneRoster Course model (courses.csv)."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    sourced_id: str = Field(..., description="Unique identifier (GUID)")
    status: OneRosterStatus = Field(..., description="Status")
    date_last_modified: datetime = Field(..., description="Last modification date")
    school_year_sourced_id: Optional[str] = Field(None, description="School year GUID")
    title: str = Field(..., description="Course title")
    course_code: Optional[str] = Field(None, description="Course code")
    grades: Optional[str] = Field(None, description="Grade levels")
    org_sourced_id: str = Field(..., description="Organization GUID")
    subjects: Optional[str] = Field(None, description="Subject codes")
    subject_codes: Optional[str] = Field(None, description="Subject codes (alternative)")
    metadata: Optional[str] = Field(None, description="Metadata in JSON format")

    @field_validator("sourced_id", "title", "org_sourced_id")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class OneRosterClass(BaseModel):
    """OneRoster Class model (classes.csv)."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    sourced_id: str = Field(..., description="Unique identifier (GUID)")
    status: OneRosterStatus = Field(..., description="Status")
    date_last_modified: datetime = Field(..., description="Last modification date")
    title: str = Field(..., description="Class title")
    class_code: Optional[str] = Field(None, description="Class code")
    class_type: ClassType = Field(..., description="Class type")
    location: Optional[str] = Field(None, description="Location")
    grades: Optional[str] = Field(None, description="Grade levels")
    subjects: Optional[str] = Field(None, description="Subject codes")
    course_sourced_id: str = Field(..., description="Course GUID")
    school_sourced_id: str = Field(..., description="School GUID")
    term_sourced_ids: Optional[str] = Field(None, description="Term GUIDs")
    periods: Optional[str] = Field(None, description="Class periods")
    metadata: Optional[str] = Field(None, description="Metadata in JSON format")

    @field_validator("sourced_id", "title", "course_sourced_id", "school_sourced_id")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class OneRosterEnrollment(BaseModel):
    """OneRoster Enrollment model (enrollments.csv)."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    sourced_id: str = Field(..., description="Unique identifier (GUID)")
    status: OneRosterStatus = Field(..., description="Status")
    date_last_modified: datetime = Field(..., description="Last modification date")
    class_sourced_id: str = Field(..., description="Class GUID")
    school_sourced_id: str = Field(..., description="School GUID")
    user_sourced_id: str = Field(..., description="User GUID")
    role: EnrollmentRole = Field(..., description="Enrollment role")
    primary: Optional[bool] = Field(None, description="Is primary teacher")
    begin_date: Optional[datetime] = Field(None, description="Enrollment begin date")
    end_date: Optional[datetime] = Field(None, description="Enrollment end date")
    metadata: Optional[str] = Field(None, description="Metadata in JSON format")

    @field_validator(
        "sourced_id", "class_sourced_id", "school_sourced_id", "user_sourced_id"
    )
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class OneRosterAcademicSession(BaseModel):
    """OneRoster Academic Session model (academicSessions.csv)."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    sourced_id: str = Field(..., description="Unique identifier (GUID)")
    status: OneRosterStatus = Field(..., description="Status")
    date_last_modified: datetime = Field(..., description="Last modification date")
    title: str = Field(..., description="Session title")
    type: str = Field(..., description="Session type (term, semester, schoolYear)")
    start_date: datetime = Field(..., description="Session start date")
    end_date: datetime = Field(..., description="Session end date")
    parent_sourced_id: Optional[str] = Field(None, description="Parent session GUID")
    school_year: str = Field(..., description="School year")
    metadata: Optional[str] = Field(None, description="Metadata in JSON format")

    @field_validator("sourced_id", "title", "type", "school_year")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class OneRosterDataModel(BaseModel):
    """Complete OneRoster data model container."""

    model_config = ConfigDict(populate_by_name=True)

    orgs: list[OneRosterOrg] = Field(default_factory=list, description="List of organizations")
    users: list[OneRosterUser] = Field(default_factory=list, description="List of users")
    courses: list[OneRosterCourse] = Field(default_factory=list, description="List of courses")
    classes: list[OneRosterClass] = Field(default_factory=list, description="List of classes")
    enrollments: list[OneRosterEnrollment] = Field(
        default_factory=list, description="List of enrollments"
    )
    academic_sessions: list[OneRosterAcademicSession] = Field(
        default_factory=list, description="List of academic sessions"
    )

    def get_org_by_sourced_id(self, sourced_id: str) -> Optional[OneRosterOrg]:
        """Get organization by sourced ID."""
        return next((o for o in self.orgs if o.sourced_id == sourced_id), None)

    def get_user_by_sourced_id(self, sourced_id: str) -> Optional[OneRosterUser]:
        """Get user by sourced ID."""
        return next((u for u in self.users if u.sourced_id == sourced_id), None)

    def get_class_by_sourced_id(self, sourced_id: str) -> Optional[OneRosterClass]:
        """Get class by sourced ID."""
        return next((c for c in self.classes if c.sourced_id == sourced_id), None)

