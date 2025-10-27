"""OneRoster CSV file writer.

This module provides functionality to write OneRoster data models to CSV files.
"""

import csv
from pathlib import Path
from typing import Optional

from ..models.oneroster import OneRosterDataModel


class OneRosterCSVWriter:
    """Writer for OneRoster CSV files.

    This class writes OneRoster data models to CSV files following
    OneRoster v1.2 CSV specification.
    """

    def __init__(self, output_dir: Path) -> None:
        """Initialize OneRoster CSV writer.

        Args:
            output_dir: Directory where CSV files will be written
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_orgs(self, data_model: OneRosterDataModel, file_name: str = "orgs.csv") -> Path:
        """Write organizations to orgs.csv.

        Args:
            data_model: OneRoster data model containing organizations
            file_name: Output file name (default: orgs.csv)

        Returns:
            Path to written file
        """
        file_path = self.output_dir / file_name

        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "sourcedId",
                    "status",
                    "dateLastModified",
                    "name",
                    "type",
                    "identifier",
                    "metadata",
                ],
            )
            writer.writeheader()

            for org in data_model.orgs:
                writer.writerow(
                    {
                        "sourcedId": org.sourced_id,
                        "status": org.status.value,
                        "dateLastModified": org.date_last_modified.strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        "name": org.name,
                        "type": org.type.value,
                        "identifier": org.identifier or "",
                        "metadata": org.metadata or "",
                    }
                )

        return file_path

    def write_users(self, data_model: OneRosterDataModel, file_name: str = "users.csv") -> Path:
        """Write users to users.csv.

        Args:
            data_model: OneRoster data model containing users
            file_name: Output file name (default: users.csv)

        Returns:
            Path to written file
        """
        file_path = self.output_dir / file_name

        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "sourcedId",
                    "status",
                    "dateLastModified",
                    "enabledUser",
                    "orgSourcedIds",
                    "role",
                    "username",
                    "userIds",
                    "givenName",
                    "familyName",
                    "middleName",
                    "email",
                    "sms",
                    "phone",
                    "agents",
                    "grades",
                    "password",
                ],
            )
            writer.writeheader()

            for user in data_model.users:
                writer.writerow(
                    {
                        "sourcedId": user.sourced_id,
                        "status": user.status.value,
                        "dateLastModified": user.date_last_modified.strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        "enabledUser": str(user.enabled_user).upper(),
                        "orgSourcedIds": user.org_sourced_ids,
                        "role": user.role.value,
                        "username": user.username,
                        "userIds": user.user_ids or "",
                        "givenName": user.given_name,
                        "familyName": user.family_name,
                        "middleName": user.middle_name or "",
                        "email": user.email or "",
                        "sms": user.sms or "",
                        "phone": user.phone or "",
                        "agents": user.agents or "",
                        "grades": user.grades or "",
                        "password": user.password or "",
                    }
                )

        return file_path

    def write_courses(
        self, data_model: OneRosterDataModel, file_name: str = "courses.csv"
    ) -> Path:
        """Write courses to courses.csv.

        Args:
            data_model: OneRoster data model containing courses
            file_name: Output file name (default: courses.csv)

        Returns:
            Path to written file
        """
        file_path = self.output_dir / file_name

        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "sourcedId",
                    "status",
                    "dateLastModified",
                    "schoolYearSourcedId",
                    "title",
                    "courseCode",
                    "grades",
                    "orgSourcedId",
                    "subjects",
                    "subjectCodes",
                    "metadata",
                ],
            )
            writer.writeheader()

            for course in data_model.courses:
                writer.writerow(
                    {
                        "sourcedId": course.sourced_id,
                        "status": course.status.value,
                        "dateLastModified": course.date_last_modified.strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        "schoolYearSourcedId": course.school_year_sourced_id or "",
                        "title": course.title,
                        "courseCode": course.course_code or "",
                        "grades": course.grades or "",
                        "orgSourcedId": course.org_sourced_id,
                        "subjects": course.subjects or "",
                        "subjectCodes": course.subject_codes or "",
                        "metadata": course.metadata or "",
                    }
                )

        return file_path

    def write_classes(
        self, data_model: OneRosterDataModel, file_name: str = "classes.csv"
    ) -> Path:
        """Write classes to classes.csv.

        Args:
            data_model: OneRoster data model containing classes
            file_name: Output file name (default: classes.csv)

        Returns:
            Path to written file
        """
        file_path = self.output_dir / file_name

        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "sourcedId",
                    "status",
                    "dateLastModified",
                    "title",
                    "classCode",
                    "classType",
                    "location",
                    "grades",
                    "subjects",
                    "courseSourcedId",
                    "schoolSourcedId",
                    "termSourcedIds",
                    "periods",
                    "metadata",
                ],
            )
            writer.writeheader()

            for cls in data_model.classes:
                writer.writerow(
                    {
                        "sourcedId": cls.sourced_id,
                        "status": cls.status.value,
                        "dateLastModified": cls.date_last_modified.strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        "title": cls.title,
                        "classCode": cls.class_code or "",
                        "classType": cls.class_type.value,
                        "location": cls.location or "",
                        "grades": cls.grades or "",
                        "subjects": cls.subjects or "",
                        "courseSourcedId": cls.course_sourced_id,
                        "schoolSourcedId": cls.school_sourced_id,
                        "termSourcedIds": cls.term_sourced_ids or "",
                        "periods": cls.periods or "",
                        "metadata": cls.metadata or "",
                    }
                )

        return file_path

    def write_enrollments(
        self, data_model: OneRosterDataModel, file_name: str = "enrollments.csv"
    ) -> Path:
        """Write enrollments to enrollments.csv.

        Args:
            data_model: OneRoster data model containing enrollments
            file_name: Output file name (default: enrollments.csv)

        Returns:
            Path to written file
        """
        file_path = self.output_dir / file_name

        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "sourcedId",
                    "status",
                    "dateLastModified",
                    "classSourcedId",
                    "schoolSourcedId",
                    "userSourcedId",
                    "role",
                    "primary",
                    "beginDate",
                    "endDate",
                    "metadata",
                ],
            )
            writer.writeheader()

            for enrollment in data_model.enrollments:
                # Format dates if present
                begin_date = ""
                if enrollment.begin_date:
                    begin_date = enrollment.begin_date.strftime("%Y-%m-%d")
                end_date = ""
                if enrollment.end_date:
                    end_date = enrollment.end_date.strftime("%Y-%m-%d")

                # Format primary field
                primary = ""
                if enrollment.primary is not None:
                    primary = str(enrollment.primary).upper()

                writer.writerow(
                    {
                        "sourcedId": enrollment.sourced_id,
                        "status": enrollment.status.value,
                        "dateLastModified": enrollment.date_last_modified.strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        "classSourcedId": enrollment.class_sourced_id,
                        "schoolSourcedId": enrollment.school_sourced_id,
                        "userSourcedId": enrollment.user_sourced_id,
                        "role": enrollment.role.value,
                        "primary": primary,
                        "beginDate": begin_date,
                        "endDate": end_date,
                        "metadata": enrollment.metadata or "",
                    }
                )

        return file_path

    def write_academic_sessions(
        self, data_model: OneRosterDataModel, file_name: str = "academicSessions.csv"
    ) -> Path:
        """Write academic sessions to academicSessions.csv.

        Args:
            data_model: OneRoster data model containing academic sessions
            file_name: Output file name (default: academicSessions.csv)

        Returns:
            Path to written file
        """
        file_path = self.output_dir / file_name

        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "sourcedId",
                    "status",
                    "dateLastModified",
                    "title",
                    "type",
                    "startDate",
                    "endDate",
                    "parentSourcedId",
                    "schoolYear",
                    "metadata",
                ],
            )
            writer.writeheader()

            for session in data_model.academic_sessions:
                writer.writerow(
                    {
                        "sourcedId": session.sourced_id,
                        "status": session.status.value,
                        "dateLastModified": session.date_last_modified.strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        "title": session.title,
                        "type": session.type,
                        "startDate": session.start_date.strftime("%Y-%m-%d"),
                        "endDate": session.end_date.strftime("%Y-%m-%d"),
                        "parentSourcedId": session.parent_sourced_id or "",
                        "schoolYear": session.school_year,
                        "metadata": session.metadata or "",
                    }
                )

        return file_path

    def write_all(self, data_model: OneRosterDataModel) -> dict[str, Path]:
        """Write all OneRoster CSV files.

        Args:
            data_model: Complete OneRoster data model

        Returns:
            Dictionary mapping file type to written file path
        """
        written_files = {}

        if data_model.orgs:
            written_files["orgs"] = self.write_orgs(data_model)

        if data_model.users:
            written_files["users"] = self.write_users(data_model)

        if data_model.courses:
            written_files["courses"] = self.write_courses(data_model)

        if data_model.classes:
            written_files["classes"] = self.write_classes(data_model)

        if data_model.enrollments:
            written_files["enrollments"] = self.write_enrollments(data_model)

        if data_model.academic_sessions:
            written_files["academicSessions"] = self.write_academic_sessions(data_model)

        return written_files
