"""Unit tests for Azure Blob Storage client."""

from unittest.mock import MagicMock, patch

import pytest

from sds2roster.azure.blob_storage import BlobStorageClient


@pytest.fixture
def mock_blob_service():
    """Mock BlobServiceClient and its components."""
    with patch("sds2roster.azure.blob_storage.BlobServiceClient") as mock_service_cls:
        mock_service_instance = MagicMock()
        mock_container_client = MagicMock()
        mock_blob_client = MagicMock()
        
        # Setup the chain of mocks
        mock_service_cls.from_connection_string.return_value = mock_service_instance
        mock_service_cls.return_value = mock_service_instance
        mock_service_instance.get_container_client.return_value = mock_container_client
        mock_container_client.get_blob_client.return_value = mock_blob_client
        
        yield {
            "service_cls": mock_service_cls,
            "service": mock_service_instance,
            "container": mock_container_client,
            "blob": mock_blob_client,
        }


def test_init_with_connection_string(mock_blob_service):
    """Test initialization with connection string."""
    client = BlobStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )

    assert client is not None
    mock_blob_service["service_cls"].from_connection_string.assert_called_once()


def test_init_with_account_credentials(mock_blob_service):
    """Test initialization with account name and key."""
    client = BlobStorageClient(account_name="testaccount", account_key="testkey")

    assert client is not None
    assert mock_blob_service["service_cls"].called


def test_init_without_credentials():
    """Test initialization without any credentials."""
    with pytest.raises(ValueError):
        BlobStorageClient()


def test_upload_file(mock_blob_service, tmp_path):
    """Test file upload."""
    mock_blob_client = mock_blob_service["blob"]
    mock_blob_client.url = "https://test.blob.core.windows.net/container/test.csv"

    # Create test file
    test_file = tmp_path / "test.csv"
    test_file.write_text("test,data\n1,2")

    client = BlobStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )
    url = client.upload_file(str(test_file), "test.csv")

    mock_blob_client.upload_blob.assert_called_once()
    assert isinstance(url, str)
    assert "test.csv" in url


def test_download_file(mock_blob_service, tmp_path):
    """Test file download."""
    mock_blob_client = mock_blob_service["blob"]
    mock_download = MagicMock()
    mock_download.readall.return_value = b"test data"
    mock_blob_client.download_blob.return_value = mock_download

    destination = tmp_path / "download.csv"
    client = BlobStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )
    result = client.download_file("test.csv", str(destination))

    mock_blob_client.download_blob.assert_called_once()
    assert result.exists()
    assert result.read_text() == "test data"


def test_list_blobs(mock_blob_service):
    """Test listing blobs."""
    mock_container = mock_blob_service["container"]
    mock_blob1 = MagicMock()
    mock_blob1.name = "test1.csv"
    mock_blob2 = MagicMock()
    mock_blob2.name = "test2.csv"
    mock_container.list_blobs.return_value = [mock_blob1, mock_blob2]

    client = BlobStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )
    blobs = client.list_blobs()

    assert len(blobs) == 2
    assert "test1.csv" in blobs
    assert "test2.csv" in blobs


def test_delete_blob(mock_blob_service):
    """Test blob deletion."""
    mock_blob_client = mock_blob_service["blob"]

    client = BlobStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )
    client.delete_blob("test.csv")

    mock_blob_client.delete_blob.assert_called_once()


def test_blob_exists(mock_blob_service):
    """Test checking blob existence."""
    mock_blob_client = mock_blob_service["blob"]
    mock_blob_client.exists.return_value = True

    client = BlobStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )
    exists = client.blob_exists("test.csv")

    assert exists is True
    mock_blob_client.exists.assert_called_once()


def test_read_csv_content(mock_blob_service):
    """Test reading CSV content."""
    mock_blob_client = mock_blob_service["blob"]
    mock_download = MagicMock()
    mock_download.readall.return_value = b"test,data\n1,2"
    mock_blob_client.download_blob.return_value = mock_download

    client = BlobStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )
    content = client.read_csv_content("test.csv")

    assert content == "test,data\n1,2"
    mock_blob_client.download_blob.assert_called_once()


def test_write_csv_content(mock_blob_service):
    """Test writing CSV content."""
    mock_blob_client = mock_blob_service["blob"]
    mock_blob_client.url = "https://test.blob.core.windows.net/container/test.csv"

    client = BlobStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )
    url = client.write_csv_content("test.csv", "test,data\n1,2")

    mock_blob_client.upload_blob.assert_called_once()
    assert isinstance(url, str)


def test_upload_directory(mock_blob_service, tmp_path):
    """Test uploading entire directory."""
    mock_blob_client = mock_blob_service["blob"]
    mock_blob_client.url = "https://test.blob.core.windows.net/container/file.csv"

    # Create test files
    (tmp_path / "file1.csv").write_text("data1")
    (tmp_path / "file2.csv").write_text("data2")

    client = BlobStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )
    urls = client.upload_directory(str(tmp_path), prefix="test/")

    assert len(urls) == 2
    assert "file1.csv" in urls
    assert "file2.csv" in urls


def test_download_directory(mock_blob_service, tmp_path):
    """Test downloading multiple blobs."""
    mock_container = mock_blob_service["container"]
    mock_blob_client = mock_blob_service["blob"]
    
    # Mock blobs list
    mock_blob1 = MagicMock()
    mock_blob1.name = "file1.csv"
    mock_blob2 = MagicMock()
    mock_blob2.name = "file2.csv"
    mock_container.list_blobs.return_value = [mock_blob1, mock_blob2]
    
    # Mock downloads
    mock_download = MagicMock()
    mock_download.readall.return_value = b"test data"
    mock_blob_client.download_blob.return_value = mock_download

    client = BlobStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )
    files = client.download_directory(str(tmp_path), prefix="test/")

    assert len(files) == 2


def test_get_blob_url(mock_blob_service):
    """Test getting blob URL."""
    mock_blob_client = mock_blob_service["blob"]
    mock_blob_client.url = "https://test.blob.core.windows.net/container/test.csv"

    client = BlobStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )
    url = client.get_blob_url("test.csv")

    assert "test.csv" in url


def test_upload_file_not_found(mock_blob_service, tmp_path):
    """Test upload with non-existent file."""
    client = BlobStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )
    
    non_existent = tmp_path / "does_not_exist.csv"
    
    with pytest.raises(FileNotFoundError):
        client.upload_file(str(non_existent), "test.csv")
