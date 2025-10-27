"""Azure integration modules."""

from sds2roster.azure.blob_storage import BlobStorageClient
from sds2roster.azure.table_storage import TableStorageClient

__all__ = ["BlobStorageClient", "TableStorageClient"]
