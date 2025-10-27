"""Azure Table Storage client for logging and tracking conversions."""

import logging
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.data.tables import TableClient, TableServiceClient

logger = logging.getLogger(__name__)


class TableStorageClient:
    """Client for Azure Table Storage operations.

    This client provides methods for logging conversion operations,
    tracking conversion history, and storing metadata.
    """

    def __init__(
        self,
        connection_string: Optional[str] = None,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
        table_name: str = "ConversionHistory",
    ) -> None:
        """Initialize Table Storage client.

        Args:
            connection_string: Azure Storage connection string
            account_name: Storage account name (alternative to connection string)
            account_key: Storage account key (alternative to connection string)
            table_name: Name of the table

        Raises:
            ValueError: If neither connection_string nor account credentials provided
        """
        if connection_string:
            self.table_service_client = TableServiceClient.from_connection_string(
                connection_string
            )
        elif account_name and account_key:
            account_url = f"https://{account_name}.table.core.windows.net"
            self.table_service_client = TableServiceClient(
                endpoint=account_url, credential=account_key
            )
        else:
            raise ValueError(
                "Either connection_string or both account_name and account_key must be provided"
            )

        self.table_name = table_name
        self.table_client: TableClient = self.table_service_client.get_table_client(
            table_name
        )

        # Create table if it doesn't exist
        try:
            self.table_service_client.create_table(table_name)
            logger.info(f"Created table: {table_name}")
        except ResourceExistsError:
            logger.debug(f"Table already exists: {table_name}")

    def log_conversion(
        self,
        conversion_id: str,
        source_type: str,
        target_type: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Log a conversion operation.

        Args:
            conversion_id: Unique identifier for the conversion
            source_type: Source data format (e.g., "SDS")
            target_type: Target data format (e.g., "OneRoster")
            status: Conversion status (e.g., "success", "failed", "in_progress")
            metadata: Optional metadata dictionary

        Returns:
            Entity dictionary with all properties
        """
        entity = {
            "PartitionKey": source_type,
            "RowKey": conversion_id,
            "SourceType": source_type,
            "TargetType": target_type,
            "Status": status,
            "Timestamp": datetime.now(UTC).isoformat(),
        }

        # Add metadata fields
        if metadata:
            for key, value in metadata.items():
                # Azure Table Storage has limitations on property names
                safe_key = key.replace(".", "_").replace("/", "_")
                entity[safe_key] = str(value)

        logger.info(
            f"Logging conversion: {conversion_id} ({source_type} -> {target_type}): {status}"
        )
        self.table_client.create_entity(entity)

        return entity

    def update_conversion_status(
        self,
        conversion_id: str,
        source_type: str,
        status: str,
        error_message: Optional[str] = None,
    ) -> None:
        """Update the status of a conversion.

        Args:
            conversion_id: Unique identifier for the conversion
            source_type: Source data format (used as partition key)
            status: New status
            error_message: Optional error message for failed conversions
        """
        entity = {
            "PartitionKey": source_type,
            "RowKey": conversion_id,
            "Status": status,
            "LastUpdated": datetime.now(UTC).isoformat(),
        }

        if error_message:
            entity["ErrorMessage"] = error_message

        logger.info(f"Updating conversion {conversion_id}: {status}")
        self.table_client.update_entity(entity, mode="merge")

    def get_conversion(
        self, conversion_id: str, source_type: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a conversion record.

        Args:
            conversion_id: Unique identifier for the conversion
            source_type: Source data format (used as partition key)

        Returns:
            Entity dictionary or None if not found
        """
        try:
            entity = self.table_client.get_entity(
                partition_key=source_type, row_key=conversion_id
            )
            return dict(entity)
        except ResourceNotFoundError:
            logger.warning(f"Conversion not found: {conversion_id}")
            return None

    def list_conversions(
        self,
        source_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List conversion records with optional filters.

        Args:
            source_type: Optional filter by source type
            status: Optional filter by status
            limit: Maximum number of records to return

        Returns:
            List of entity dictionaries
        """
        # Build filter query
        filters = []
        if source_type:
            filters.append(f"PartitionKey eq '{source_type}'")
        if status:
            filters.append(f"Status eq '{status}'")

        query_filter = " and ".join(filters) if filters else None

        entities = self.table_client.query_entities(
            query_filter=query_filter, results_per_page=limit
        )

        return [dict(entity) for entity in entities]

    def delete_conversion(self, conversion_id: str, source_type: str) -> None:
        """Delete a conversion record.

        Args:
            conversion_id: Unique identifier for the conversion
            source_type: Source data format (used as partition key)
        """
        logger.info(f"Deleting conversion: {conversion_id}")
        self.table_client.delete_entity(
            partition_key=source_type, row_key=conversion_id
        )

    def get_conversion_stats(
        self, source_type: Optional[str] = None
    ) -> Dict[str, int]:
        """Get statistics about conversions.

        Args:
            source_type: Optional filter by source type

        Returns:
            Dictionary with conversion statistics
        """
        conversions = self.list_conversions(source_type=source_type, limit=1000)

        stats = {
            "total": len(conversions),
            "success": 0,
            "failed": 0,
            "in_progress": 0,
        }

        for conversion in conversions:
            status = conversion.get("Status", "").lower()
            if status == "success":
                stats["success"] += 1
            elif status == "failed":
                stats["failed"] += 1
            elif status == "in_progress":
                stats["in_progress"] += 1

        return stats

    def log_entity_counts(
        self, conversion_id: str, source_type: str, counts: Dict[str, int]
    ) -> None:
        """Log entity counts for a conversion.

        Args:
            conversion_id: Unique identifier for the conversion
            source_type: Source data format
            counts: Dictionary of entity type to count
        """
        entity = {
            "PartitionKey": f"{source_type}_counts",
            "RowKey": conversion_id,
            "ConversionId": conversion_id,
            "Timestamp": datetime.now(UTC).isoformat(),
        }

        # Add count fields
        for entity_type, count in counts.items():
            safe_key = entity_type.replace(".", "_").replace("/", "_")
            entity[f"Count_{safe_key}"] = count

        logger.info(f"Logging entity counts for conversion: {conversion_id}")
        self.table_client.create_entity(entity)

    def cleanup_old_records(self, days: int = 30) -> int:
        """Delete conversion records older than specified days.

        Args:
            days: Number of days to keep

        Returns:
            Number of deleted records
        """
        cutoff_date = datetime.now(UTC).timestamp() - (days * 24 * 60 * 60)
        entities = self.table_client.list_entities()

        deleted_count = 0
        for entity in entities:
            # Azure Table Storage Timestamp is in datetime format
            timestamp = entity.get("Timestamp")
            if timestamp and timestamp.timestamp() < cutoff_date:
                self.table_client.delete_entity(
                    partition_key=entity["PartitionKey"], row_key=entity["RowKey"]
                )
                deleted_count += 1
                logger.debug(f"Deleted old record: {entity['RowKey']}")

        logger.info(f"Deleted {deleted_count} old conversion records")
        return deleted_count
