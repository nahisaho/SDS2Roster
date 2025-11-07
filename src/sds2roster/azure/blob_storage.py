"""Azure Blob Storage client for SDS2Roster."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, ContainerClient

logger = logging.getLogger(__name__)


class BlobStorageClient:
    """Client for Azure Blob Storage operations.

    This client provides methods for uploading and downloading CSV files
    from Azure Blob Storage, supporting both SDS and OneRoster formats.
    """

    def __init__(
        self,
        connection_string: Optional[str] = None,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
        container_name: str = "sds2roster",
    ) -> None:
        """Initialize Blob Storage client.

        Args:
            connection_string: Azure Storage connection string
            account_name: Storage account name (alternative to connection string)
            account_key: Storage account key (alternative to connection string)
            container_name: Name of the blob container

        Raises:
            ValueError: If neither connection_string nor account credentials provided
        """
        if connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                connection_string
            )
        elif account_name and account_key:
            account_url = f"https://{account_name}.blob.core.windows.net"
            self.blob_service_client = BlobServiceClient(
                account_url=account_url, credential=account_key
            )
        else:
            raise ValueError(
                "Either connection_string or both account_name and account_key must be provided"
            )

        self.container_name = container_name
        self.container_client: ContainerClient = (
            self.blob_service_client.get_container_client(container_name)
        )

        # Create container if it doesn't exist
        try:
            self.container_client.get_container_properties()
        except ResourceNotFoundError:
            logger.info(f"Creating container: {container_name}")
            self.container_client.create_container()

    def upload_file(
        self, file_path: Union[str, Path], blob_name: Optional[str] = None
    ) -> str:
        """Upload a file to blob storage.

        Args:
            file_path: Path to the file to upload
            blob_name: Name for the blob (defaults to file name)

        Returns:
            URL of the uploaded blob

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if blob_name is None:
            blob_name = file_path.name

        logger.info(f"Uploading {file_path} to {blob_name}")

        with open(file_path, "rb") as data:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.upload_blob(data, overwrite=True)

        return blob_client.url

    def upload_directory(
        self, directory: Union[str, Path], prefix: str = ""
    ) -> Dict[str, str]:
        """Upload all files in a directory to blob storage.

        Args:
            directory: Path to the directory
            prefix: Optional prefix for blob names

        Returns:
            Dictionary mapping filenames to URLs
        """
        directory = Path(directory)
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        uploaded = {}
        for file_path in directory.glob("*.csv"):
            blob_name = f"{prefix}{file_path.name}" if prefix else file_path.name
            url = self.upload_file(file_path, blob_name)
            uploaded[file_path.name] = url
            logger.info(f"Uploaded {file_path.name} -> {blob_name}")

        return uploaded

    def download_file(self, blob_name: str, destination: Union[str, Path]) -> Path:
        """Download a blob to a local file.

        Args:
            blob_name: Name of the blob to download
            destination: Local file path for download

        Returns:
            Path to downloaded file

        Raises:
            ResourceNotFoundError: If blob doesn't exist
        """
        destination = Path(destination)
        logger.info(f"Downloading {blob_name} to {destination}")

        # Create parent directory if needed
        destination.parent.mkdir(parents=True, exist_ok=True)

        blob_client = self.container_client.get_blob_client(blob_name)
        with open(destination, "wb") as file:
            data = blob_client.download_blob()
            file.write(data.readall())
        
        return destination

    def download_directory(
        self, destination: Union[str, Path], prefix: str = ""
    ) -> List[Path]:
        """Download all blobs with a given prefix.

        Args:
            destination: Local directory path
            prefix: Optional prefix filter for blobs

        Returns:
            List of downloaded file paths
        """
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)

        downloaded = []
        blob_list = self.container_client.list_blobs(name_starts_with=prefix)

        for blob in blob_list:
            if blob.name.endswith(".csv"):
                file_path = destination / Path(blob.name).name
                self.download_file(blob.name, file_path)
                downloaded.append(file_path)
                logger.info(f"Downloaded {blob.name}")

        return downloaded

    def list_blobs(self, prefix: str = "") -> List[str]:
        """List all blobs in the container.

        Args:
            prefix: Optional prefix filter

        Returns:
            List of blob names
        """
        blob_list = self.container_client.list_blobs(name_starts_with=prefix)
        return [blob.name for blob in blob_list]

    def delete_blob(self, blob_name: str) -> None:
        """Delete a blob from storage.

        Args:
            blob_name: Name of the blob to delete
        """
        logger.info(f"Deleting blob: {blob_name}")
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_client.delete_blob()

    def blob_exists(self, blob_name: str) -> bool:
        """Check if a blob exists.

        Args:
            blob_name: Name of the blob

        Returns:
            True if blob exists, False otherwise
        """
        blob_client = self.container_client.get_blob_client(blob_name)
        return blob_client.exists()

    def get_blob_url(self, blob_name: str) -> str:
        """Get the URL for a blob.

        Args:
            blob_name: Name of the blob

        Returns:
            URL of the blob
        """
        blob_client = self.container_client.get_blob_client(blob_name)
        return blob_client.url

    def read_csv_content(self, blob_name: str) -> str:
        """Read CSV content from a blob as a string.

        Args:
            blob_name: Name of the blob

        Returns:
            CSV content as string

        Raises:
            ResourceNotFoundError: If blob doesn't exist
        """
        blob_client = self.container_client.get_blob_client(blob_name)
        download_stream = blob_client.download_blob()
        return download_stream.readall().decode("utf-8")

    def write_csv_content(self, blob_name: str, content: str) -> str:
        """Write CSV content to a blob.

        Args:
            blob_name: Name of the blob
            content: CSV content as string

        Returns:
            URL of the uploaded blob
        """
        logger.info(f"Writing CSV content to {blob_name}")
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_client.upload_blob(content.encode("utf-8"), overwrite=True)
        return blob_client.url
