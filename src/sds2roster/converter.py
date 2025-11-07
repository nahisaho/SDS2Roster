"""Converter module for transforming SDS data to OneRoster format."""

from datetime import datetime, timezone

from sds2roster.models.oneroster import (
    ClassType,
    EnrollmentRole,
    OneRosterAcademicSession,
    OneRosterClass,
    OneRosterCourse,
    OneRosterDataModel,
    OneRosterEnrollment,
    OneRosterOrg,
    OneRosterRole,
    OneRosterStatus,
    OneRosterUser,
    OrgType,
    RoleType,
)
from .models.sds import SDSDataModel
from .utils.validators import (
    create_metadata_json,
    create_user_ids_json,
    generate_guid,
)


class SDSToOneRosterConverter:
    """Convert SDS data model to OneRoster data model.

    This class implements the complete transformation logic from Microsoft SDS
    CSV format to OneRoster v1.2 CSV format, following the data mapping specification.
    """

    def __init__(self) -> None:
        """Initialize the converter."""
        self.conversion_timestamp = datetime.now(timezone.utc)

    def convert(self, sds_data: SDSDataModel) -> OneRosterDataModel:
        """Convert SDS data model to OneRoster data model.

        Args:
            sds_data: Complete SDS data model to convert

        Returns:
            Complete OneRoster data model

        Raises:
            ValueError: If data validation fails
        """
        # Convert organizations (schools)
        orgs = self._convert_organizations(sds_data)

        # Convert users (students and teachers)
        users = self._convert_users(sds_data)

        # Convert courses (extracted from sections)
        courses = self._convert_courses(sds_data)

        # Convert classes (sections)
        classes = self._convert_classes(sds_data)

        # Convert enrollments
        enrollments = self._convert_enrollments(sds_data)

        # Convert academic sessions (from section term information)
        academic_sessions = self._convert_academic_sessions(sds_data)

        # Convert roles (user role assignments)
        roles = self._convert_roles(sds_data)

        return OneRosterDataModel(
            orgs=orgs,
            users=users,
            courses=courses,
            classes=classes,
            enrollments=enrollments,
            academic_sessions=academic_sessions,
            roles=roles,
        )

    def _convert_organizations(self, sds_data: SDSDataModel) -> list[OneRosterOrg]:
        """Convert SDS schools to OneRoster organizations.

        Args:
            sds_data: SDS data model

        Returns:
            List of OneRoster organizations
        """
        orgs = []

        for school in sds_data.schools:
            org = OneRosterOrg(
                sourced_id=generate_guid("org", school.sis_id),
                status=OneRosterStatus.ACTIVE,
                date_last_modified=self.conversion_timestamp,
                name=school.name,
                type=OrgType.SCHOOL,
                identifier=school.school_number,
                parent_sourced_id=None,  # Can be set if district information is available
                metadata=create_metadata_json(school.sis_id),
            )
            orgs.append(org)

        return orgs

    def _convert_users(self, sds_data: SDSDataModel) -> list[OneRosterUser]:
        """Convert SDS students and teachers to OneRoster users.

        Args:
            sds_data: SDS data model

        Returns:
            List of OneRoster users (students + teachers)
        """
        users = []

        # Convert students
        for student in sds_data.students:
            org_sourced_id = generate_guid("org", student.school_sis_id)

            user = OneRosterUser(
                sourced_id=generate_guid("user", student.sis_id),
                status=OneRosterStatus.ACTIVE,
                date_last_modified=self.conversion_timestamp,
                enabled_user=True,
                org_sourced_ids=org_sourced_id,
                role=RoleType.STUDENT,
                username=student.username,
                user_ids=create_user_ids_json(student.sis_id),
                given_name=student.first_name,
                family_name=student.last_name,
                middle_name=student.middle_name,
                email=student.secondary_email,
                grades=student.grade,  # Single grade as string
            )
            users.append(user)

        # Convert teachers
        for teacher in sds_data.teachers:
            org_sourced_id = generate_guid("org", teacher.school_sis_id)

            user = OneRosterUser(
                sourced_id=generate_guid("user", teacher.sis_id),
                status=OneRosterStatus.ACTIVE,
                date_last_modified=self.conversion_timestamp,
                enabled_user=True,
                org_sourced_ids=org_sourced_id,
                role=RoleType.TEACHER,
                username=teacher.username,
                user_ids=create_user_ids_json(teacher.sis_id),
                given_name=teacher.first_name,
                family_name=teacher.last_name,
                middle_name=teacher.middle_name,
                email=teacher.secondary_email,
            )
            users.append(user)

        return users

    def _convert_courses(self, sds_data: SDSDataModel) -> list[OneRosterCourse]:
        """Convert SDS sections to OneRoster courses.

        Extracts unique courses from section data. Multiple sections with the same
        course information are consolidated into a single course.

        Args:
            sds_data: SDS data model

        Returns:
            List of unique OneRoster courses
        """
        courses = []
        seen_course_ids = set()

        for section in sds_data.sections:
            # Use course_number as course ID, or section SIS ID if not available
            course_id = section.course_number or section.sis_id

            # Skip if we've already created this course
            if course_id in seen_course_ids:
                continue

            seen_course_ids.add(course_id)

            # Use course_name, or section_name as fallback
            course_title = section.course_name or section.section_name

            org_sourced_id = generate_guid("org", section.school_sis_id)

            course = OneRosterCourse(
                sourced_id=generate_guid("course", course_id),
                status=OneRosterStatus.ACTIVE,
                date_last_modified=self.conversion_timestamp,
                title=course_title,
                course_code=section.course_number,
                org_sourced_id=org_sourced_id,
                metadata=create_metadata_json(
                    course_id, {"course_description": section.course_description}
                )
                if section.course_description
                else create_metadata_json(course_id),
            )
            courses.append(course)

        return courses

    def _convert_classes(self, sds_data: SDSDataModel) -> list[OneRosterClass]:
        """Convert SDS sections to OneRoster classes.

        Args:
            sds_data: SDS data model

        Returns:
            List of OneRoster classes
        """
        classes = []

        for section in sds_data.sections:
            # Generate course GUID using course_number or section SIS ID
            course_id = section.course_number or section.sis_id
            course_sourced_id = generate_guid("course", course_id)

            school_sourced_id = generate_guid("org", section.school_sis_id)

            # Generate term GUID if term information exists
            term_sourced_ids = None
            if section.term_sis_id:
                term_sourced_ids = generate_guid("term", section.term_sis_id)

            cls = OneRosterClass(
                sourced_id=generate_guid("class", section.sis_id),
                status=OneRosterStatus.ACTIVE,
                date_last_modified=self.conversion_timestamp,
                title=section.section_name,
                class_code=section.section_number,
                class_type=ClassType.SCHEDULED,  # Default to scheduled
                course_sourced_id=course_sourced_id,
                school_sourced_id=school_sourced_id,
                term_sourced_ids=term_sourced_ids,
                metadata=create_metadata_json(section.sis_id),
            )
            classes.append(cls)

        return classes

    def _convert_enrollments(self, sds_data: SDSDataModel) -> list[OneRosterEnrollment]:
        """Convert SDS enrollments to OneRoster enrollments.

        Args:
            sds_data: SDS data model

        Returns:
            List of OneRoster enrollments
        """
        enrollments = []

        for enrollment in sds_data.enrollments:
            class_sourced_id = generate_guid("class", enrollment.section_sis_id)
            user_sourced_id = generate_guid("user", enrollment.sis_id)

            # Determine school from section
            section = sds_data.get_section_by_sis_id(enrollment.section_sis_id)
            if not section:
                # Skip enrollment if section not found
                continue

            school_sourced_id = generate_guid("org", section.school_sis_id)

            # Map role
            role = (
                EnrollmentRole.STUDENT
                if enrollment.role == "student"
                else EnrollmentRole.TEACHER
            )

            # Teachers are primary by default
            primary = True if enrollment.role == "teacher" else None

            oneroster_enrollment = OneRosterEnrollment(
                sourced_id=generate_guid(
                    "enrollment", f"{enrollment.section_sis_id}:{enrollment.sis_id}"
                ),
                status=OneRosterStatus.ACTIVE,
                date_last_modified=self.conversion_timestamp,
                class_sourced_id=class_sourced_id,
                school_sourced_id=school_sourced_id,
                user_sourced_id=user_sourced_id,
                role=role,
                primary=primary,
            )
            enrollments.append(oneroster_enrollment)

        return enrollments

    def _convert_academic_sessions(
        self, sds_data: SDSDataModel
    ) -> list[OneRosterAcademicSession]:
        """Convert SDS section term information to OneRoster academic sessions.

        Extracts unique terms from section data and creates academic session records.

        Args:
            sds_data: SDS data model

        Returns:
            List of unique OneRoster academic sessions
        """
        sessions = []
        seen_term_ids = set()

        for section in sds_data.sections:
            # Skip if no term information
            if not section.term_sis_id:
                continue

            # Skip if we've already created this term
            if section.term_sis_id in seen_term_ids:
                continue

            seen_term_ids.add(section.term_sis_id)

            # Extract school year from term start date or use current year
            school_year = (
                str(section.term_start_date.year)
                if section.term_start_date
                else str(self.conversion_timestamp.year)
            )

            session = OneRosterAcademicSession(
                sourced_id=generate_guid("term", section.term_sis_id),
                status=OneRosterStatus.ACTIVE,
                date_last_modified=self.conversion_timestamp,
                title=section.term_name or section.term_sis_id,
                type="term",  # Default type
                start_date=section.term_start_date or self.conversion_timestamp,
                end_date=section.term_end_date or self.conversion_timestamp,
                school_year=school_year,
                metadata=create_metadata_json(section.term_sis_id),
            )
            sessions.append(session)

        return sessions

    def _convert_roles(self, sds_data: SDSDataModel) -> list[OneRosterRole]:
        """Convert SDS student and teacher data to OneRoster roles.

        Args:
            sds_data: SDS data model

        Returns:
            List of OneRoster roles
        """
        roles = []

        # Convert student roles
        for student in sds_data.students:
            role = OneRosterRole(
                sourced_id=generate_guid("role", f"{student.sis_id}_student"),
                status=OneRosterStatus.ACTIVE,
                date_last_modified=self.conversion_timestamp,
                user_sourced_id=generate_guid("user", student.sis_id),
                role_type="primary",
                role="student",
                org_sourced_id=generate_guid("org", student.school_sis_id),
                user_profile_sourced_id="",
            )
            roles.append(role)

        # Convert teacher roles
        for teacher in sds_data.teachers:
            role = OneRosterRole(
                sourced_id=generate_guid("role", f"{teacher.sis_id}_teacher"),
                status=OneRosterStatus.ACTIVE,
                date_last_modified=self.conversion_timestamp,
                user_sourced_id=generate_guid("user", teacher.sis_id),
                role_type="primary",
                role="teacher",
                org_sourced_id=generate_guid("org", teacher.school_sis_id),
                user_profile_sourced_id="",
            )
            roles.append(role)

        return roles

