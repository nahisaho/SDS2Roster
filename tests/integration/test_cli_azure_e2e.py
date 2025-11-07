"""
Azure CLI Commands E2E Integration Tests

These tests require Azurite to be running:
    docker-compose up -d azurite
    
Set environment variable for testing:
    export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"

To run these tests:
    pytest tests/integration/test_cli_azure_e2e.py -m azure
"""

import os
import subprocess

import pytest

# Azurite connection string
AZURITE_CONNECTION_STRING = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
    "TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"
)

# Mark all tests in this module as azure integration tests
pytestmark = [pytest.mark.azure, pytest.mark.integration]


@pytest.fixture
def temp_csv_file(tmp_path):
    """Create a temporary CSV file for testing."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("id,name\n1,John\n2,Jane")
    return csv_file


@pytest.fixture(autouse=True)
def set_azure_env():
    """Set Azure connection string for all tests."""
    original = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    os.environ["AZURE_STORAGE_CONNECTION_STRING"] = AZURITE_CONNECTION_STRING
    yield
    if original:
        os.environ["AZURE_STORAGE_CONNECTION_STRING"] = original
    else:
        os.environ.pop("AZURE_STORAGE_CONNECTION_STRING", None)


class TestAzureCLI:
    """E2E tests for Azure CLI commands."""

    def test_upload_command(self, temp_csv_file):
        """Test sds2roster upload command."""
        result = subprocess.run(
            [
                "sds2roster",
                "upload",
                str(temp_csv_file),
                "cli-test.csv",
                "--container",
                "test-cli",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Uploaded" in result.stdout or "Success" in result.stdout

    def test_download_command(self, temp_csv_file, tmp_path):
        """Test sds2roster download command."""
        # First upload a file
        subprocess.run(
            [
                "sds2roster",
                "upload",
                str(temp_csv_file),
                "download-test.csv",
                "--container",
                "test-cli",
            ],
            capture_output=True,
        )

        # Download it
        download_path = tmp_path / "downloaded.csv"
        result = subprocess.run(
            [
                "sds2roster",
                "download",
                "download-test.csv",
                str(download_path),
                "--container",
                "test-cli",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert download_path.exists()
        assert "Downloaded" in result.stdout or "Success" in result.stdout

    def test_log_command(self):
        """Test sds2roster log command."""
        result = subprocess.run(
            [
                "sds2roster",
                "log",
                "--source",
                "SDS",
                "--output",
                "/test/output",
                "--status",
                "Success",
                "--table",
                "testconversions",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Logged" in result.stdout or "Success" in result.stdout

    def test_list_jobs_command(self):
        """Test sds2roster list-jobs command."""
        # First log a conversion
        subprocess.run(
            [
                "sds2roster",
                "log",
                "--source",
                "SDS",
                "--output",
                "/test/output",
                "--status",
                "Success",
                "--table",
                "testconversions",
            ],
            capture_output=True,
        )

        # List jobs
        result = subprocess.run(
            ["sds2roster", "list-jobs", "--table", "testconversions"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should show the logged conversion
        assert "SDS" in result.stdout or "Success" in result.stdout
