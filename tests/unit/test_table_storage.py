"""Unit tests for Azure Table Storage client."""

from unittest.mock import MagicMock, patch

import pytest

from sds2roster.azure.table_storage import TableStorageClient


@pytest.fixture
def mock_table_service():
    """Mock TableServiceClient and its components."""
    with patch("sds2roster.azure.table_storage.TableServiceClient") as mock_service_cls:
        mock_service_instance = MagicMock()
        mock_table_client = MagicMock()
        
        # Setup the chain of mocks
        mock_service_cls.from_connection_string.return_value = mock_service_instance
        mock_service_cls.return_value = mock_service_instance
        mock_service_instance.get_table_client.return_value = mock_table_client
        
        yield {
            "service_cls": mock_service_cls,
            "service": mock_service_instance,
            "table": mock_table_client,
        }


def test_init_with_connection_string(mock_table_service):
    """Test initialization with connection string."""
    client = TableStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )

    assert client is not None
    mock_table_service["service_cls"].from_connection_string.assert_called_once()


def test_init_with_account_credentials(mock_table_service):
    """Test initialization with account name and key."""
    client = TableStorageClient(account_name="testaccount", account_key="testkey")

    assert client is not None
    assert mock_table_service["service_cls"].called


def test_init_without_credentials():
    """Test initialization without any credentials."""
    with pytest.raises(ValueError):
        TableStorageClient()


def test_log_conversion(mock_table_service):
    """Test logging a conversion."""
    mock_table = mock_table_service["table"]
    client = TableStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )

    entity = client.log_conversion(
        conversion_id="test-id",
        source_type="SDS",
        target_type="OneRoster",
        status="success",
        metadata={"files": 5, "records": 100},
    )

    mock_table.create_entity.assert_called_once()
    assert entity["PartitionKey"] == "SDS"
    assert entity["RowKey"] == "test-id"
    assert entity["Status"] == "success"


def test_update_conversion_status(mock_table_service):
    """Test updating conversion status."""
    mock_table = mock_table_service["table"]
    client = TableStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )

    client.update_conversion_status(
        conversion_id="test-id",
        source_type="SDS",
        status="failed",
        error_message="Test error",
    )

    mock_table.update_entity.assert_called_once()


def test_get_conversion(mock_table_service):
    """Test retrieving a conversion."""
    mock_table = mock_table_service["table"]
    mock_table.get_entity.return_value = {
        "PartitionKey": "SDS",
        "RowKey": "test-id",
        "Status": "success",
    }

    client = TableStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )
    entity = client.get_conversion(conversion_id="test-id", source_type="SDS")

    assert entity is not None
    assert entity["RowKey"] == "test-id"


def test_list_conversions(mock_table_service):
    """Test listing conversions."""
    mock_table = mock_table_service["table"]
    mock_table.query_entities.return_value = [
        {"PartitionKey": "SDS", "RowKey": "id1", "Status": "success"},
        {"PartitionKey": "SDS", "RowKey": "id2", "Status": "failed"},
    ]

    client = TableStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )
    entities = client.list_conversions(source_type="SDS")

    assert len(entities) == 2
    assert entities[0]["Status"] == "success"


def test_delete_conversion(mock_table_service):
    """Test deleting a conversion."""
    mock_table = mock_table_service["table"]
    client = TableStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )

    client.delete_conversion(conversion_id="test-id", source_type="SDS")

    mock_table.delete_entity.assert_called_once()


def test_get_conversion_stats(mock_table_service):
    """Test getting conversion statistics."""
    mock_table = mock_table_service["table"]
    mock_table.query_entities.return_value = [
        {"Status": "success"},
        {"Status": "success"},
        {"Status": "failed"},
        {"Status": "in_progress"},
    ]

    client = TableStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )
    stats = client.get_conversion_stats(source_type="SDS")

    assert stats["total"] == 4
    assert stats["success"] == 2
    assert stats["failed"] == 1
    assert stats["in_progress"] == 1


def test_log_entity_counts(mock_table_service):
    """Test logging entity counts."""
    mock_table = mock_table_service["table"]
    client = TableStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )

    client.log_entity_counts(
        conversion_id="test-id",
        source_type="SDS",
        counts={"schools": 5, "students": 100, "teachers": 20},
    )

    mock_table.create_entity.assert_called_once()


def test_get_conversion_not_found(mock_table_service):
    """Test retrieving a non-existent conversion."""
    mock_table = mock_table_service["table"]
    
    from azure.core.exceptions import ResourceNotFoundError
    mock_table.get_entity.side_effect = ResourceNotFoundError("Not found")

    client = TableStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )
    entity = client.get_conversion(conversion_id="not-exists", source_type="SDS")

    assert entity is None


def test_cleanup_old_records(mock_table_service):
    """Test cleaning up old records."""
    mock_table = mock_table_service["table"]
    
    # Mock old entities
    old_entity = {
        "PartitionKey": "SDS",
        "RowKey": "old-job",
        "Timestamp": MagicMock(timestamp=MagicMock(return_value=0))
    }
    mock_table.list_entities.return_value = [old_entity]

    client = TableStorageClient(
        connection_string="DefaultEndpointsProtocol=https;AccountName=test"
    )
    deleted = client.cleanup_old_records(days=30)

    assert deleted >= 0
