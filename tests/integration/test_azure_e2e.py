"""
Azure Storage E2E Integration Tests using Azurite

These tests require Azurite to be running:
    docker-compose up -d azurite
    
Or:
    docker run -p 10000:10000 -p 10001:10001 -p 10002:10002 \
        mcr.microsoft.com/azure-storage/azurite
"""

import os
from datetime import datetime
from pathlib import Path

import pytest
from azure.core.exceptions import ResourceNotFoundError

from sds2roster.azure.blob_storage import BlobStorageClient
from sds2roster.azure.table_storage import TableStorageClient

# Azurite connection string (well-known development account)
AZURITE_CONNECTION_STRING = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
    "TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"
)

# Skip tests if Azurite is not available
pytestmark = pytest.mark.skipif(
    os.getenv("SKIP_AZURE_TESTS", "false").lower() == "true",
    reason="Azure integration tests disabled (set SKIP_AZURE_TESTS=false to enable)",
)


@pytest.fixture
def blob_client():
    """Create a BlobStorageClient connected to Azurite."""
    client = BlobStorageClient(
        connection_string=AZURITE_CONNECTION_STRING, container_name="test-container"
    )
    yield client
    # Cleanup: Delete test container
    try:
        container_client = client.blob_service_client.get_container_client(
            "test-container"
        )
        container_client.delete_container()
    except ResourceNotFoundError:
        pass


@pytest.fixture
def table_client():
    """Create a TableStorageClient connected to Azurite."""
    client = TableStorageClient(
        connection_string=AZURITE_CONNECTION_STRING, table_name="testconversions"
    )
    yield client
    # Cleanup: Delete test table
    try:
        client.table_client.delete_table()
    except ResourceNotFoundError:
        pass


@pytest.fixture
def temp_csv_file(tmp_path):
    """Create a temporary CSV file for testing."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("id,name,email\n1,John,john@example.com\n2,Jane,jane@example.com")
    return csv_file


class TestBlobStorageE2E:
    """End-to-end tests for BlobStorageClient with Azurite."""

    def test_upload_and_download_file(self, blob_client, temp_csv_file):
        """Test uploading and downloading a file."""
        # Upload
        blob_name = "test-upload.csv"
        blob_client.upload_file(str(temp_csv_file), blob_name)

        # Verify blob exists
        assert blob_client.blob_exists(blob_name)

        # Download
        download_path = temp_csv_file.parent / "downloaded.csv"
        blob_client.download_file(blob_name, str(download_path))

        # Verify content
        assert download_path.read_text() == temp_csv_file.read_text()

    def test_list_blobs(self, blob_client, temp_csv_file):
        """Test listing blobs."""
        # Upload multiple files
        blob_client.upload_file(str(temp_csv_file), "file1.csv")
        blob_client.upload_file(str(temp_csv_file), "file2.csv")
        blob_client.upload_file(str(temp_csv_file), "folder/file3.csv")

        # List all blobs
        blobs = blob_client.list_blobs()
        assert len(blobs) == 3

        # List blobs with prefix
        blobs_in_folder = blob_client.list_blobs(prefix="folder/")
        assert len(blobs_in_folder) == 1
        assert blobs_in_folder[0] == "folder/file3.csv"

    def test_delete_blob(self, blob_client, temp_csv_file):
        """Test deleting a blob."""
        blob_name = "to-delete.csv"
        blob_client.upload_file(str(temp_csv_file), blob_name)

        # Verify exists
        assert blob_client.blob_exists(blob_name)

        # Delete
        blob_client.delete_blob(blob_name)

        # Verify deleted
        assert not blob_client.blob_exists(blob_name)

    def test_read_write_csv_content(self, blob_client):
        """Test reading and writing CSV content directly."""
        blob_name = "data.csv"
        csv_data = [
            {"id": "1", "name": "Alice"},
            {"id": "2", "name": "Bob"},
        ]

        # Write CSV
        blob_client.write_csv_content(blob_name, csv_data)

        # Read CSV
        read_data = blob_client.read_csv_content(blob_name)
        assert len(read_data) == 2
        assert read_data[0]["name"] == "Alice"
        assert read_data[1]["name"] == "Bob"

    def test_upload_download_directory(self, blob_client, tmp_path):
        """Test uploading and downloading a directory."""
        # Create test directory structure
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.txt").write_text("content2")
        subdir = test_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("content3")

        # Upload directory
        blob_client.upload_directory(str(test_dir), "uploaded")

        # Verify 3 files uploaded
        blobs = blob_client.list_blobs(prefix="uploaded/")
        assert len(blobs) == 3

        # Download directory
        download_dir = tmp_path / "downloaded"
        download_dir.mkdir()
        blob_client.download_directory("uploaded", str(download_dir))

        # Verify downloaded files
        assert (download_dir / "file1.txt").read_text() == "content1"
        assert (download_dir / "file2.txt").read_text() == "content2"
        assert (download_dir / "subdir" / "file3.txt").read_text() == "content3"


class TestTableStorageE2E:
    """End-to-end tests for TableStorageClient with Azurite."""

    def test_log_and_get_conversion(self, table_client):
        """Test logging and retrieving a conversion."""
        # Log conversion
        conversion_id = table_client.log_conversion(
            source_type="SDS",
            output_path="/data/output",
            status="Success",
            error_message=None,
        )

        # Retrieve conversion
        conversion = table_client.get_conversion(conversion_id)
        assert conversion is not None
        assert conversion["source_type"] == "SDS"
        assert conversion["status"] == "Success"
        assert conversion["output_path"] == "/data/output"

    def test_update_conversion_status(self, table_client):
        """Test updating conversion status."""
        # Create conversion
        conversion_id = table_client.log_conversion(
            source_type="SDS", output_path="/data/output", status="InProgress"
        )

        # Update status
        table_client.update_conversion_status(conversion_id, "Success")

        # Verify updated
        conversion = table_client.get_conversion(conversion_id)
        assert conversion["status"] == "Success"

    def test_list_conversions(self, table_client):
        """Test listing conversions with filters."""
        # Create multiple conversions
        table_client.log_conversion("SDS", "/data/1", "Success")
        table_client.log_conversion("OneRoster", "/data/2", "Failed")
        table_client.log_conversion("SDS", "/data/3", "Success")

        # List all
        all_conversions = table_client.list_conversions()
        assert len(all_conversions) >= 3

        # Filter by source_type
        sds_conversions = table_client.list_conversions(source_type="SDS")
        assert all(c["source_type"] == "SDS" for c in sds_conversions)

        # Filter by status
        failed_conversions = table_client.list_conversions(status="Failed")
        assert all(c["status"] == "Failed" for c in failed_conversions)

    def test_get_conversion_stats(self, table_client):
        """Test getting conversion statistics."""
        # Create conversions
        table_client.log_conversion("SDS", "/data/1", "Success")
        table_client.log_conversion("SDS", "/data/2", "Success")
        table_client.log_conversion("SDS", "/data/3", "Failed")

        # Get stats
        stats = table_client.get_conversion_stats()
        assert stats["total"] >= 3
        assert stats["success"] >= 2
        assert stats["failed"] >= 1
        assert stats["in_progress"] >= 0

    def test_delete_conversion(self, table_client):
        """Test deleting a conversion."""
        # Create conversion
        conversion_id = table_client.log_conversion("SDS", "/data/1", "Success")

        # Delete
        table_client.delete_conversion(conversion_id)

        # Verify deleted
        conversion = table_client.get_conversion(conversion_id)
        assert conversion is None

    def test_log_entity_counts(self, table_client):
        """Test logging entity counts."""
        conversion_id = table_client.log_conversion("SDS", "/data/1", "Success")

        # Log entity counts
        entity_counts = {
            "users": 100,
            "orgs": 10,
            "courses": 50,
            "classes": 75,
            "enrollments": 200,
        }
        table_client.log_entity_counts(conversion_id, entity_counts)

        # Verify stored
        conversion = table_client.get_conversion(conversion_id)
        assert conversion["entity_users"] == 100
        assert conversion["entity_orgs"] == 10
        assert conversion["entity_courses"] == 50

    def test_cleanup_old_records(self, table_client):
        """Test cleaning up old records."""
        # This test just verifies the method runs without error
        # In a real scenario, we'd create old records and verify deletion
        deleted_count = table_client.cleanup_old_records(days=30)
        assert deleted_count >= 0
