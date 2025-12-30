"""MongoDB client management."""
from pymongo import MongoClient
from typing import List, Optional
from urllib.parse import urlparse


class MongoDBClient:
    """Handles MongoDB connections and database operations."""
    
    def __init__(self):
        """Initialize MongoDB client."""
        self.client: Optional[MongoClient] = None
        self.uri: Optional[str] = None
    
    def connect_by_port(self, port: str = "27017") -> List[str]:
        """Connect to MongoDB using localhost and port.
        
        Args:
            port: MongoDB port number
            
        Returns:
            List of database names
            
        Raises:
            Exception: If connection fails
        """
        self.uri = f"mongodb://localhost:{port}/"
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
        databases = self.client.list_database_names()
        return databases
    
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
