"""Unit tests for CLI module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from sds2roster.cli import app

runner = CliRunner()


class TestCLI:
    """Test suite for CLI commands."""

    def test_help_command(self) -> None:
        """Test --help flag."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Microsoft SDS to OneRoster CSV converter" in result.stdout

    def test_version_command(self) -> None:
        """Test version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Version" in result.stdout
        assert "0.1.0" in result.stdout

    def test_convert_command_help(self) -> None:
        """Test convert command help."""
        result = runner.invoke(app, ["convert", "--help"])
        assert result.exit_code == 0
        assert "Convert SDS CSV files to OneRoster format" in result.stdout

    def test_validate_command_help(self) -> None:
        """Test validate command help."""
        result = runner.invoke(app, ["validate", "--help"])
        assert result.exit_code == 0
        assert "Validate SDS CSV files" in result.stdout

    def test_convert_missing_directory(self) -> None:
        """Test convert command with missing directory."""
        result = runner.invoke(app, ["convert", "/nonexistent/path", "/tmp/output"])
        assert result.exit_code == 1
        assert "Error: Input directory not found" in result.stdout

    def test_validate_missing_directory(self) -> None:
        """Test validate command with missing directory."""
        result = runner.invoke(app, ["validate", "/nonexistent/path"])
        assert result.exit_code == 1
        assert "Error: Input directory not found" in result.stdout

    def test_convert_with_test_fixtures(self, tmp_path: Path) -> None:
        """Test convert command with test fixtures."""
        fixtures_path = Path("tests/fixtures/sds")
        if not fixtures_path.exists():
            pytest.skip("Test fixtures not available")

        output_path = tmp_path / "oneroster_output"

        result = runner.invoke(
            app, ["convert", str(fixtures_path), str(output_path), "-v"]
        )

        assert result.exit_code == 0
        assert "Conversion completed successfully" in result.stdout
        assert output_path.exists()

        # Check that output files were created
        expected_files = [
            "orgs.csv",
            "users.csv",
            "courses.csv",
            "classes.csv",
            "enrollments.csv",
            "academicSessions.csv",
        ]

        for file in expected_files:
            assert (output_path / file).exists(), f"{file} should exist"

    def test_validate_with_test_fixtures(self) -> None:
        """Test validate command with test fixtures."""
        fixtures_path = Path("tests/fixtures/sds")
        if not fixtures_path.exists():
            pytest.skip("Test fixtures not available")

        result = runner.invoke(app, ["validate", str(fixtures_path), "-v"])

        assert result.exit_code == 0
        assert "All files validated successfully" in result.stdout
        assert "Schools" in result.stdout
        assert "Students" in result.stdout

    def test_convert_missing_required_files(self, tmp_path: Path) -> None:
        """Test convert with incomplete SDS files."""
        # Create a directory with only some files
        incomplete_dir = tmp_path / "incomplete"
        incomplete_dir.mkdir()

        # Create only school.csv
        (incomplete_dir / "school.csv").write_text("SIS ID,Name,School Number\n")

        result = runner.invoke(
            app, ["convert", str(incomplete_dir), str(tmp_path / "output")]
        )

        assert result.exit_code == 1
        assert "Missing required SDS files" in result.stdout

    def test_validate_missing_required_files(self, tmp_path: Path) -> None:
        """Test validate with incomplete SDS files."""
        # Create a directory with only some files
        incomplete_dir = tmp_path / "incomplete"
        incomplete_dir.mkdir()

        # Create only school.csv
        (incomplete_dir / "school.csv").write_text("SIS ID,Name,School Number\n")

        result = runner.invoke(app, ["validate", str(incomplete_dir)])

        assert result.exit_code == 1
        assert "missing" in result.stdout.lower()

    def test_convert_with_invalid_csv(self, tmp_path: Path) -> None:
        """Test convert with invalid CSV data."""
        invalid_dir = tmp_path / "invalid"
        invalid_dir.mkdir()

        # Create all required files but with invalid data
        required_files = [
            "school.csv",
            "student.csv",
            "teacher.csv",
            "section.csv",
            "studentEnrollment.csv",
            "teacherRoster.csv",
        ]

        for file in required_files:
            (invalid_dir / file).write_text("invalid,header\ninvalid,data\n")

        result = runner.invoke(
            app, ["convert", str(invalid_dir), str(tmp_path / "output")]
        )

        assert result.exit_code == 1
        assert "Error during conversion" in result.stdout

    def test_validate_with_invalid_csv(self, tmp_path: Path) -> None:
        """Test validate with invalid CSV data."""
        invalid_dir = tmp_path / "invalid"
        invalid_dir.mkdir()

        # Create all required files but with invalid data
        required_files = [
            "school.csv",
            "student.csv",
            "teacher.csv",
            "section.csv",
            "studentEnrollment.csv",
            "teacherRoster.csv",
        ]

        for file in required_files:
            (invalid_dir / file).write_text("invalid,header\ninvalid,data\n")

        result = runner.invoke(app, ["validate", str(invalid_dir)])

        assert result.exit_code == 1
        assert "Validation failed" in result.stdout
