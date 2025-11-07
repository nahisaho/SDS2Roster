"""Data models package."""

from sds2roster.models.oneroster import (
    OneRosterAcademicSession,
    OneRosterClass,
    OneRosterCourse,
    OneRosterDataModel,
    OneRosterEnrollment,
    OneRosterOrg,
    OneRosterRole,
    OneRosterUser,
)
from sds2roster.models.sds import (
    SDSDataModel,
    SDSEnrollment,
    SDSSchool,
    SDSSection,
    SDSStudent,
    SDSTeacher,
)

__all__ = [
    # SDS Models
    "SDSDataModel",
    "SDSSchool",
    "SDSStudent",
    "SDSTeacher",
    "SDSSection",
    "SDSEnrollment",
    # OneRoster Models
    "OneRosterDataModel",
    "OneRosterOrg",
    "OneRosterUser",
    "OneRosterCourse",
    "OneRosterClass",
    "OneRosterEnrollment",
    "OneRosterAcademicSession",
    "OneRosterRole",
]
