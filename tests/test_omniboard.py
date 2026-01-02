"""Unit tests for Omniboard manager module."""
import pytest
import sys
from src.omniboard import OmniboardManager


class TestOmniboardManager:
    """Test Omniboard manager functionality."""
    
    def test_generate_port_for_database(self):
        """Test deterministic port generation."""
        manager = OmniboardManager()
        
        # Same database should always get same port
        port1 = manager.generate_port_for_database("test_db")
        port2 = manager.generate_port_for_database("test_db")
        assert port1 == port2
        
        # Different databases should get different ports
        port3 = manager.generate_port_for_database("other_db")
        assert port1 != port3
        
        # Port should be in valid range
        assert 20000 <= port1 < 30000
    
    def test_generate_port_custom_range(self):
        """Test port generation with custom range."""
        manager = OmniboardManager()
        port = manager.generate_port_for_database("test", base=5000, span=1000)
        assert 5000 <= port < 6000
    
    def test_adjust_mongo_host_for_docker_localhost_windows(self):
        """Test host adjustment for Windows/Mac localhost."""
        manager = OmniboardManager()
        
        if sys.platform.startswith("win") or sys.platform == "darwin":
            assert manager.adjust_mongo_host_for_docker("localhost") == "host.docker.internal"
            assert manager.adjust_mongo_host_for_docker("127.0.0.1") == "host.docker.internal"
        else:
            # On Linux, localhost stays as is
            assert manager.adjust_mongo_host_for_docker("localhost") in ["localhost", "host.docker.internal"]
    
    def test_adjust_mongo_host_for_docker_remote(self):
        """Test host adjustment for remote hosts."""
        manager = OmniboardManager()
        
        # Remote hosts should not be changed
        assert manager.adjust_mongo_host_for_docker("192.168.1.100") == "192.168.1.100"
        assert manager.adjust_mongo_host_for_docker("mongo.example.com") == "mongo.example.com"
    
    def test_find_available_port(self):
        """Test finding available port."""
        manager = OmniboardManager()
        
        # Should find a port (this is a basic smoke test)
        port = manager.find_available_port(25000)
        assert port >= 25000
        assert isinstance(port, int)
    
    def test_list_containers(self):
        """Test listing containers."""
        manager = OmniboardManager()
        
        # Should return a list (empty or with IDs)
        containers = manager.list_containers()
        assert isinstance(containers, list)
