"""Unit tests for OneRoster data models."""

import pytest
from datetime import datetime
from sds2roster.models.oneroster import (
    OneRosterOrg,
    OneRosterUser,
    OneRosterClass,
    OneRosterEnrollment,
    OneRosterRole,
    OneRosterDataModel,
    OneRosterStatus,
    OrgType,
    RoleType,
    ClassType,
    EnrollmentRole,
)


class TestOneRosterOrg:
    """Test suite for OneRosterOrg model."""

    def test_create_valid_org(self) -> None:
        """Test creating a valid organization."""
        org = OneRosterOrg(
            sourced_id="550e8400-e29b-41d4-a716-446655440001",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=datetime(2025, 10, 27, 10, 30, 0),
            name="Tokyo International School",
            type=OrgType.SCHOOL,
            identifier="TIS-001",
            parent_sourced_id="550e8400-e29b-41d4-a716-446655440000",
            metadata='{"sis_id":"SCH001"}',
        )
        assert org.sourced_id == "550e8400-e29b-41d4-a716-446655440001"
        assert org.status == OneRosterStatus.ACTIVE
        assert org.name == "Tokyo International School"
        assert org.type == OrgType.SCHOOL
        assert org.parent_sourced_id == "550e8400-e29b-41d4-a716-446655440000"

    def test_org_without_optional_fields(self) -> None:
        """Test creating an org without optional fields."""
        org = OneRosterOrg(
            sourced_id="550e8400-e29b-41d4-a716-446655440001",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=datetime(2025, 10, 27),
            name="Test School",
            type=OrgType.SCHOOL,
        )
        assert org.identifier is None
        assert org.parent_sourced_id is None
        assert org.metadata is None

    def test_org_empty_name_raises_error(self) -> None:
        """Test that empty name raises validation error."""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            OneRosterOrg(
                sourced_id="550e8400-e29b-41d4-a716-446655440001",
                status=OneRosterStatus.ACTIVE,
                date_last_modified=datetime(2025, 10, 27),
                name="",
                type=OrgType.SCHOOL,
            )

    def test_org_empty_sourced_id_raises_error(self) -> None:
        """Test that empty sourced_id raises validation error."""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            OneRosterOrg(
                sourced_id="",
                status=OneRosterStatus.ACTIVE,
                date_last_modified=datetime(2025, 10, 27),
                name="Test School",
                type=OrgType.SCHOOL,
            )


class TestOneRosterUser:
    """Test suite for OneRosterUser model."""

    def test_create_valid_student(self) -> None:
        """Test creating a valid student user."""
        user = OneRosterUser(
            sourced_id="550e8400-e29b-41d4-a716-446655440010",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=datetime(2025, 10, 27),
            enabled_user=True,
            org_sourced_ids="550e8400-e29b-41d4-a716-446655440001",
            role=RoleType.STUDENT,
            username="john.doe",
            given_name="John",
            family_name="Doe",
            middle_name="M",
            email="john@example.com",
            grades="10",
        )
        assert user.role == RoleType.STUDENT
        assert user.username == "john.doe"
        assert user.given_name == "John"
        assert user.family_name == "Doe"
        assert user.grades == "10"

    def test_create_valid_teacher(self) -> None:
        """Test creating a valid teacher user."""
        user = OneRosterUser(
            sourced_id="550e8400-e29b-41d4-a716-446655440020",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=datetime(2025, 10, 27),
            enabled_user=True,
            org_sourced_ids="550e8400-e29b-41d4-a716-446655440001",
            role=RoleType.TEACHER,
            username="alice.smith",
            given_name="Alice",
            family_name="Smith",
            email="alice@school.com",
        )
        assert user.role == RoleType.TEACHER
        assert user.grades is None  # Teachers don't have grades

    def test_user_required_fields_only(self) -> None:
        """Test creating a user with required fields only."""
        user = OneRosterUser(
            sourced_id="550e8400-e29b-41d4-a716-446655440010",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=datetime(2025, 10, 27),
            enabled_user=True,
            org_sourced_ids="550e8400-e29b-41d4-a716-446655440001",
            role=RoleType.STUDENT,
            username="test.user",
            given_name="Test",
            family_name="User",
        )
        assert user.middle_name is None
        assert user.email is None
        assert user.grades is None

    def test_user_empty_username_raises_error(self) -> None:
        """Test that empty username raises validation error."""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            OneRosterUser(
                sourced_id="550e8400-e29b-41d4-a716-446655440010",
                status=OneRosterStatus.ACTIVE,
                date_last_modified=datetime(2025, 10, 27),
                enabled_user=True,
                org_sourced_ids="550e8400-e29b-41d4-a716-446655440001",
                role=RoleType.STUDENT,
                username="",
                given_name="Test",
                family_name="User",
            )


class TestOneRosterClass:
    """Test suite for OneRosterClass model."""

    def test_create_valid_class(self) -> None:
        """Test creating a valid class."""
        cls = OneRosterClass(
            sourced_id="550e8400-e29b-41d4-a716-446655440030",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=datetime(2025, 10, 27),
            title="Math 101 - Section A",
            class_code="MATH101-A",
            class_type=ClassType.SCHEDULED,
            course_sourced_id="550e8400-e29b-41d4-a716-446655440040",
            school_sourced_id="550e8400-e29b-41d4-a716-446655440001",
            grades="10",
        )
        assert cls.title == "Math 101 - Section A"
        assert cls.class_type == ClassType.SCHEDULED
        assert cls.grades == "10"

    def test_class_homeroom_type(self) -> None:
        """Test creating a homeroom class."""
        cls = OneRosterClass(
            sourced_id="550e8400-e29b-41d4-a716-446655440030",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=datetime(2025, 10, 27),
            title="Homeroom 10A",
            class_type=ClassType.HOMEROOM,
            course_sourced_id="550e8400-e29b-41d4-a716-446655440040",
            school_sourced_id="550e8400-e29b-41d4-a716-446655440001",
        )
        assert cls.class_type == ClassType.HOMEROOM

    def test_class_empty_title_raises_error(self) -> None:
        """Test that empty title raises validation error."""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            OneRosterClass(
                sourced_id="550e8400-e29b-41d4-a716-446655440030",
                status=OneRosterStatus.ACTIVE,
                date_last_modified=datetime(2025, 10, 27),
                title="",
                class_type=ClassType.SCHEDULED,
                course_sourced_id="550e8400-e29b-41d4-a716-446655440040",
                school_sourced_id="550e8400-e29b-41d4-a716-446655440001",
            )


class TestOneRosterEnrollment:
    """Test suite for OneRosterEnrollment model."""

    def test_create_student_enrollment(self) -> None:
        """Test creating a student enrollment."""
        enrollment = OneRosterEnrollment(
            sourced_id="550e8400-e29b-41d4-a716-446655440050",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=datetime(2025, 10, 27),
            class_sourced_id="550e8400-e29b-41d4-a716-446655440030",
            school_sourced_id="550e8400-e29b-41d4-a716-446655440001",
            user_sourced_id="550e8400-e29b-41d4-a716-446655440010",
            role=EnrollmentRole.STUDENT,
        )
        assert enrollment.role == EnrollmentRole.STUDENT
        assert enrollment.primary is None

    def test_create_teacher_enrollment(self) -> None:
        """Test creating a teacher enrollment."""
        enrollment = OneRosterEnrollment(
            sourced_id="550e8400-e29b-41d4-a716-446655440051",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=datetime(2025, 10, 27),
            class_sourced_id="550e8400-e29b-41d4-a716-446655440030",
            school_sourced_id="550e8400-e29b-41d4-a716-446655440001",
            user_sourced_id="550e8400-e29b-41d4-a716-446655440020",
            role=EnrollmentRole.TEACHER,
            primary=True,
        )
        assert enrollment.role == EnrollmentRole.TEACHER
        assert enrollment.primary is True

    def test_enrollment_with_dates(self) -> None:
        """Test creating an enrollment with begin and end dates."""
        begin_date = datetime(2025, 9, 1)
        end_date = datetime(2025, 12, 20)

        enrollment = OneRosterEnrollment(
            sourced_id="550e8400-e29b-41d4-a716-446655440050",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=datetime(2025, 10, 27),
            class_sourced_id="550e8400-e29b-41d4-a716-446655440030",
            school_sourced_id="550e8400-e29b-41d4-a716-446655440001",
            user_sourced_id="550e8400-e29b-41d4-a716-446655440010",
            role=EnrollmentRole.STUDENT,
            begin_date=begin_date,
            end_date=end_date,
        )
        assert enrollment.begin_date == begin_date
        assert enrollment.end_date == end_date


class TestOneRosterDataModel:
    """Test suite for OneRosterDataModel container."""

    def test_create_empty_data_model(self) -> None:
        """Test creating an empty data model."""
        model = OneRosterDataModel()
        assert len(model.orgs) == 0
        assert len(model.users) == 0
        assert len(model.classes) == 0
        assert len(model.enrollments) == 0

    def test_create_data_model_with_data(self) -> None:
        """Test creating a data model with data."""
        org = OneRosterOrg(
            sourced_id="550e8400-e29b-41d4-a716-446655440001",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=datetime(2025, 10, 27),
            name="Test School",
            type=OrgType.SCHOOL,
        )

        user = OneRosterUser(
            sourced_id="550e8400-e29b-41d4-a716-446655440010",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=datetime(2025, 10, 27),
            enabled_user=True,
            org_sourced_ids="550e8400-e29b-41d4-a716-446655440001",
            role=RoleType.STUDENT,
            username="test.user",
            given_name="Test",
            family_name="User",
        )

        model = OneRosterDataModel(orgs=[org], users=[user])
        assert len(model.orgs) == 1
        assert len(model.users) == 1

    def test_get_org_by_sourced_id(self) -> None:
        """Test getting org by sourced ID."""
        org = OneRosterOrg(
            sourced_id="550e8400-e29b-41d4-a716-446655440001",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=datetime(2025, 10, 27),
            name="Test School",
            type=OrgType.SCHOOL,
        )
        model = OneRosterDataModel(orgs=[org])

        found_org = model.get_org_by_sourced_id("550e8400-e29b-41d4-a716-446655440001")
        assert found_org is not None
        assert found_org.name == "Test School"

    def test_get_org_by_sourced_id_not_found(self) -> None:
        """Test getting org by sourced ID when not found."""
        model = OneRosterDataModel()
        found_org = model.get_org_by_sourced_id("invalid-id")
        assert found_org is None


class TestOneRosterRole:
    """Test suite for OneRosterRole model."""

    def test_create_valid_role(self) -> None:
        """Test creating a valid role."""
        role = OneRosterRole(
            sourced_id="550e8400-e29b-41d4-a716-446655440100",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=datetime(2025, 10, 27, 10, 30, 0),
            user_sourced_id="550e8400-e29b-41d4-a716-446655440002",
            role_type="primary",
            role="student",
            org_sourced_id="550e8400-e29b-41d4-a716-446655440001",
            user_profile_sourced_id=None,
        )
        assert role.sourced_id == "550e8400-e29b-41d4-a716-446655440100"
        assert role.user_sourced_id == "550e8400-e29b-41d4-a716-446655440002"
        assert role.role_type == "primary"
        assert role.role == "student"
        assert role.org_sourced_id == "550e8400-e29b-41d4-a716-446655440001"

    def test_role_without_optional_fields(self) -> None:
        """Test creating a role without optional fields."""
        role = OneRosterRole(
            sourced_id="550e8400-e29b-41d4-a716-446655440101",
            status=OneRosterStatus.ACTIVE,
            date_last_modified=datetime(2025, 10, 27),
            user_sourced_id="550e8400-e29b-41d4-a716-446655440002",
            role_type="secondary",
            role="teacher",
            org_sourced_id="550e8400-e29b-41d4-a716-446655440001",
        )
        assert role.user_profile_sourced_id is None

    def test_role_empty_user_sourced_id_raises_error(self) -> None:
        """Test that empty user_sourced_id raises validation error."""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            OneRosterRole(
                sourced_id="550e8400-e29b-41d4-a716-446655440102",
                status=OneRosterStatus.ACTIVE,
                date_last_modified=datetime(2025, 10, 27),
                user_sourced_id="",
                role_type="primary",
                role="student",
                org_sourced_id="550e8400-e29b-41d4-a716-446655440001",
            )

    def test_role_empty_role_raises_error(self) -> None:
        """Test that empty role raises validation error."""
        with pytest.raises(ValueError, match="Field cannot be empty"):
            OneRosterRole(
                sourced_id="550e8400-e29b-41d4-a716-446655440103",
                status=OneRosterStatus.ACTIVE,
                date_last_modified=datetime(2025, 10, 27),
                user_sourced_id="550e8400-e29b-41d4-a716-446655440002",
                role_type="primary",
                role="",
                org_sourced_id="550e8400-e29b-41d4-a716-446655440001",
            )

