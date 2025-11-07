"""OneRoster CSV file writer.

This module provides functionality to write OneRoster data models to CSV files.
"""

import csv
from pathlib import Path

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
                    "parentSourcedId",
                ],
            )
            writer.writeheader()

            for org in data_model.orgs:
                # Find parent sourced ID
                parent_sourced_id = ""
                if hasattr(org, 'parent_sourced_id') and org.parent_sourced_id:
                    parent_sourced_id = org.parent_sourced_id
                
                writer.writerow(
                    {
                        "sourcedId": org.sourced_id,
                        "status": "",  # Empty per sample
                        "dateLastModified": "",  # Empty per sample
                        "name": org.name,
                        "type": org.type.value,
                        "identifier": org.identifier or "",
                        "parentSourcedId": parent_sourced_id,
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
                    "username",
                    "givenName",
                    "familyName",
                    "middleName",
                    "email",
                    "grades",
                    "password",
                    "userMasterIdentifier",
                ],
            )
            writer.writeheader()

            for user in data_model.users:
                writer.writerow(
                    {
                        "sourcedId": user.sourced_id,
                        "status": "",  # Empty per sample
                        "dateLastModified": "",  # Empty per sample
                        "enabledUser": str(user.enabled_user).upper(),
                        "username": user.username,
                        "givenName": user.given_name,
                        "familyName": user.family_name,
                        "middleName": user.middle_name or "",
                        "email": user.email or "",
                        "grades": user.grades or "",
                        "password": user.password or "",
                        "userMasterIdentifier": user.sourced_id.lower(),  # Lowercase sourcedId
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
                    "orgSourcedId",
                ],
            )
            writer.writeheader()

            for course in data_model.courses:
                writer.writerow(
                    {
                        "sourcedId": course.sourced_id,
                        "status": "",  # Empty per sample
                        "dateLastModified": "",  # Empty per sample
                        "schoolYearSourcedId": course.school_year_sourced_id or "",
                        "title": course.title,
                        "orgSourcedId": course.org_sourced_id,
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
                    "courseSourcedId",
                    "classType",
                    "schoolSourcedId",
                    "termSourcedIds",
                ],
            )
            writer.writeheader()

            for cls in data_model.classes:
                writer.writerow(
                    {
                        "sourcedId": cls.sourced_id,
                        "status": "",  # Empty per sample
                        "dateLastModified": "",  # Empty per sample
                        "title": cls.title,
                        "courseSourcedId": cls.course_sourced_id,
                        "classType": cls.class_type.value,
                        "schoolSourcedId": cls.school_sourced_id,
                        "termSourcedIds": cls.term_sourced_ids or "",
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
                ],
            )
            writer.writeheader()

            for enrollment in data_model.enrollments:
                # Format primary field
                primary = ""
                if enrollment.primary is not None:
                    primary = str(enrollment.primary).upper()

                writer.writerow(
                    {
                        "sourcedId": enrollment.sourced_id,
                        "status": "",  # Empty per sample
                        "dateLastModified": "",  # Empty per sample
                        "classSourcedId": enrollment.class_sourced_id,
                        "schoolSourcedId": enrollment.school_sourced_id,
                        "userSourcedId": enrollment.user_sourced_id,
                        "role": enrollment.role.value,
                        "primary": primary,
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
                ],
            )
            writer.writeheader()

            for session in data_model.academic_sessions:
                writer.writerow(
                    {
                        "sourcedId": session.sourced_id,
                        "status": "",  # Empty per sample
                        "dateLastModified": "",  # Empty per sample
                        "title": session.title,
                        "type": session.type,
                        "startDate": session.start_date.strftime("%Y-%m-%d"),
                        "endDate": session.end_date.strftime("%Y-%m-%d"),
                        "parentSourcedId": session.parent_sourced_id or "",
                        "schoolYear": session.school_year,
                    }
                )

        return file_path

    def write_manifest(self, file_name: str = "manifest.csv") -> Path:
        """Write manifest.csv.

        Args:
            file_name: Output file name (default: manifest.csv)

        Returns:
            Path to written file
        """
        file_path = self.output_dir / file_name

        # Manifest properties based on OneRoster 1.2 specification
        manifest_properties = [
            ("manifest.version", "1.0"),
            ("oneroster.version", "1.2"),
            ("file.academicSessions", "bulk"),
            ("file.categories", "absent"),
            ("file.classes", "bulk"),
            ("file.classResources", "absent"),
            ("file.courses", "bulk"),
            ("file.courseResources", "absent"),
            ("file.demographics", "absent"),
            ("file.enrollments", "bulk"),
            ("file.lineItemLearningObjectiveIds", "absent"),
            ("file.lineItems", "absent"),
            ("file.lineItemScoreScales", "absent"),
            ("file.orgs", "bulk"),
            ("file.resources", "absent"),
            ("file.resultLearningObjectiveIds", "absent"),
            ("file.results", "absent"),
            ("file.resultScoreScales", "absent"),
            ("file.roles", "bulk"),
            ("file.scoreScales", "absent"),
            ("file.userProfiles", "absent"),
            ("file.userResources", "absent"),
            ("file.users", "bulk"),
            ("source.systemName", "SDS2Roster"),
            ("source.systemCode", "v0.2.0"),
        ]

        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["propertyName", "value"])
            writer.writeheader()

            for prop_name, prop_value in manifest_properties:
                writer.writerow({"propertyName": prop_name, "value": prop_value})

        return file_path

    def write_roles(self, data_model: OneRosterDataModel, file_name: str = "roles.csv") -> Path:
        """Write roles to roles.csv.

        Args:
            data_model: OneRoster data model containing roles
            file_name: Output file name (default: roles.csv)

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
                    "userSourcedId",
                    "roleType",
                    "role",
                    "orgSourcedId",
                    "userProfileSourcedId",
                ],
            )
            writer.writeheader()

            # Generate roles from data model if available
            if hasattr(data_model, 'roles'):
                for role in data_model.roles:
                    writer.writerow(
                        {
                            "sourcedId": role.sourced_id,
                            "status": "",  # Empty per sample
                            "dateLastModified": "",  # Empty per sample
                            "userSourcedId": role.user_sourced_id,
                            "roleType": role.role_type,
                            "role": role.role,
                            "orgSourcedId": role.org_sourced_id,
                            "userProfileSourcedId": role.user_profile_sourced_id or "",
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

        # Always write manifest first
        written_files["manifest"] = self.write_manifest()

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

        # Write roles if available
        if hasattr(data_model, 'roles') and data_model.roles:
            written_files["roles"] = self.write_roles(data_model)

        return written_files
