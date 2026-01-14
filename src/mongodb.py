"""MongoDB client management."""
import os
from typing import List, Optional
from urllib.parse import urlparse

from pymongo import MongoClient
from pymongo.errors import OperationFailure


class MongoDBClient:
    """Handles MongoDB connections and database operations."""
    
    def __init__(self):
        """Initialize MongoDB client."""
        self.client: Optional[MongoClient] = None
        self.uri: Optional[str] = None
    
    def connect_by_port(self, port: str = "27017") -> List[str]:
        """Connect to MongoDB using default host and port.
        
        Args:
            port: MongoDB port number
            
        Returns:
            List of database names
            
        Raises:
            Exception: If connection fails
        """
        default_host = os.environ.get("MONGO_DEFAULT_HOST", "localhost")
        self.uri = f"mongodb://{default_host}:{port}/"
        return self._connect()
    
    def connect_by_url(self, url: str) -> List[str]:
        """Connect to MongoDB using full URL.
        
        Args:
            url: MongoDB connection URL
            
        Returns:
            List of database names
            
        Raises:
            Exception: If connection fails
        """
        if not url:
            raise ValueError("URL cannot be empty")
        
        # Ensure proper protocol
        if not url.startswith("mongodb://") and not url.startswith("mongodb+srv://"):
            url = "mongodb://" + url
        
        self.uri = url
        return self._connect()
    
    def _connect(self) -> List[str]:
        """Internal method to establish connection and list databases.
        
        Returns:
            List of database names
            
        Raises:
            Exception: If connection fails
        """
        if self.client:
            self.client.close()

        self.client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)

        try:
            # Standard behaviour: attempt to list all databases. This
            # requires appropriate permissions (typically admin-level).
            return self.client.list_database_names()
        except OperationFailure as exc:
            # Some MongoDB deployments (Atlas / VM with non-admin users)
            # do not allow the connected user to run the listDatabases
            # command. In that case, fall back to the database specified in
            # the connection URI (if any) instead of failing entirely.
            message = str(exc).lower()
            if "listdatabases" in message or "not authorized" in message:
                _, _, database = self.parse_connection_url()
                if database:
                    return [database]
            # For all other failures, or if no database is encoded in the
            # URI, propagate the original error so the UI can show it.
            raise

    def get_connection_uri(self) -> Optional[str]:
        """Return the current MongoDB connection URI, if any.

        This is used by downstream components (e.g. Omniboard launcher)
        when they need to reuse the exact connection string, including
        credentials and options.
        """

        return self.uri
    
    def parse_connection_url(self) -> tuple[str, int, Optional[str]]:
        """Parse the current connection URL.
        
        Returns:
            Tuple of (host, port, database)
        """
        if not self.uri:
            return "localhost", 27017, None
        
        parsed = urlparse(self.uri)
        host = parsed.hostname or "localhost"
        port = parsed.port or 27017
        database = parsed.path.strip("/") if parsed.path else None
        database = database if database else None  # Convert empty string to None
        
        return host, port, database
    
    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
