"""Omniboard Docker container management."""
import subprocess
import socket
import hashlib
import uuid
import sys
import time
import os
from typing import List, Optional

from urllib.parse import urlparse, urlunparse


class OmniboardManager:
    """Manages Omniboard Docker containers."""
    
    @staticmethod
    def is_running_in_docker() -> bool:
        """Check if the application is running inside a Docker container.
        
        Returns:
            True if running in Docker, False otherwise
        """
        # Check for Docker environment indicators
        if os.path.exists('/.dockerenv'):
            return True
        if os.environ.get('DOCKER_MODE') == 'true':
            return True
        try:
            with open('/proc/1/cgroup', 'rt') as f:
                return 'docker' in f.read()
        except:
            return False
    
    @staticmethod
    def is_docker_running() -> bool:
        """Check if Docker daemon is running.
        
        Returns:
            True if Docker is running, False otherwise
        """
        try:
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=5,
                creationflags=creationflags,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    @staticmethod
    def start_docker_desktop():
        """Attempt to start Docker Desktop.
        
        Raises:
            Exception: If Docker Desktop cannot be started
        """
        if sys.platform.startswith("win"):
            # Windows
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            subprocess.Popen(
                ["powershell", "-Command", "Start-Process", "'C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe'"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creationflags,
            )
        elif sys.platform == "darwin":
            # macOS
            subprocess.Popen(
                ["open", "-a", "Docker"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            # Linux - typically systemd
            subprocess.Popen(
                ["systemctl", "start", "docker"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        # Wait up to 30 seconds for Docker to start
        for _ in range(30):
            time.sleep(1)
            if OmniboardManager.is_docker_running():
                return
        
        raise Exception("Docker Desktop failed to start within 30 seconds")
    
    @staticmethod
    def ensure_docker_running():
        """Ensure Docker is running, start it if needed.
        
        Skips check if running inside Docker (container mode).
        
        Raises:
            Exception: If Docker cannot be started
        """
        # Skip Docker checks if we're running inside a Docker container
        if OmniboardManager.is_running_in_docker():
            return

        # For desktop usage we no longer try to auto-start Docker Desktop or
        # poll repeatedly, as that caused a poor UX (flashing Docker console
        # windows and long waits). Instead we simply check once and, if Docker
        # is not available, raise a clear error so the UI can display a
        # helpful message to the user.
        if not OmniboardManager.is_docker_running():
            raise RuntimeError(
                "Docker does not appear to be running. Please start Docker Desktop "
                "(or the Docker daemon) and try again."
            )
    
    @staticmethod
    def generate_port_for_database(db_name: str, base: int = 20000, span: int = 10000) -> int:
        """Generate a deterministic port number based on database name.
        
        Args:
            db_name: Database name
            base: Base port number
            span: Port range span
            
        Returns:
            Port number
        """
        h = int(hashlib.sha256(db_name.encode()).hexdigest(), 16)
        return base + (h % span)
    
    @staticmethod
    def find_available_port(start_port: int) -> int:
        """Find an available port starting from the given port.
        
        Args:
            start_port: Starting port to search from
            
        Returns:
            Available port number
        """
        port = start_port
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("", port))
                    # Also check if Docker is using this port
                    try:
                        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
                        result = subprocess.run(
                            ["docker", "ps", "--filter", f"publish={port}", "--format", "{{.ID}}"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                            creationflags=creationflags,
                        )
                        if result.stdout.strip() == "":
                            return port
                    except (subprocess.TimeoutExpired, FileNotFoundError):
                        return port
                except OSError:
                    port += 1
    
    @staticmethod
    def adjust_mongo_host_for_docker(mongo_host: str) -> str:
        """Adjust MongoDB host for Docker networking.
        
        Args:
            mongo_host: Original MongoDB host
            
        Returns:
            Adjusted host for Docker
        """
        if sys.platform.startswith("win") or sys.platform == "darwin":
            if mongo_host in ["localhost", "127.0.0.1"]:
                return "host.docker.internal"
        return mongo_host

    def _adjust_mongo_uri_for_docker(self, mongo_uri: str, db_name: Optional[str] = None) -> str:
        """Adjust a full MongoDB URI for Docker networking when needed.

        When connecting to a local MongoDB instance from a container on
        Windows/macOS, we need to replace ``localhost``/``127.0.0.1`` with
        ``host.docker.internal``. This helper performs that substitution
        while preserving user info, port and query parameters. If a
        ``db_name`` is provided, it is injected as the path component of
        the URI (``/<db_name>``) so Omniboard connects to the selected
        database, with any authentication or options remaining in the
        query string.
        """

        try:
            parsed = urlparse(mongo_uri)
        except Exception:
            # If parsing fails for any reason, fall back to the original
            # URI rather than breaking Omniboard launch.
            return mongo_uri

        host = parsed.hostname
        if not host:
            return mongo_uri

        adjusted_host = self.adjust_mongo_host_for_docker(host)

        # Rebuild netloc preserving credentials and port
        netloc = ""
        if parsed.username:
            netloc += parsed.username
            if parsed.password:
                netloc += f":{parsed.password}"
            netloc += "@"

        netloc += adjusted_host
        if parsed.port:
            netloc += f":{parsed.port}"

        # Inject selected database into the path, if provided
        path = parsed.path
        if db_name:
            path = f"/{db_name}"

        new_parsed = parsed._replace(netloc=netloc, path=path)
        return urlunparse(new_parsed)
    
    def launch(
        self,
        db_name: str,
        mongo_host: str,
        mongo_port: int,
        host_port: Optional[int] = None,
        mongo_uri: Optional[str] = None,
    ) -> tuple[str, int]:
        """Launch an Omniboard Docker container.
        
        Args:
            db_name: Database name to connect to
            mongo_host: MongoDB host
            mongo_port: MongoDB port
            host_port: Optional host port (will find available if not provided)
            
        Returns:
            Tuple of (container_name, host_port)
            
        Raises:
            Exception: If Docker launch fails
        """
        # Ensure Docker is running
        self.ensure_docker_running()
        
        # Find an available port if not specified
        if host_port is None:
            preferred_port = self.generate_port_for_database(db_name)
            host_port = self.find_available_port(preferred_port)
        
        # Build Mongo connection argument for Omniboard. When a full
        # MongoDB URI is available (typically for remote/Atlas-style
        # deployments with authentication), reuse it so that credentials
        # and options are preserved. Otherwise, fall back to the legacy
        # host:port:db form for simple local setups.
        if mongo_uri:
            mongo_arg = self._adjust_mongo_uri_for_docker(mongo_uri, db_name=db_name)
            mongo_flag = "--mu"  # Omniboard expects full URIs with --mu
        else:
            docker_mongo_host = self.adjust_mongo_host_for_docker(mongo_host)
            mongo_arg = f"{docker_mongo_host}:{mongo_port}:{db_name}"
            mongo_flag = "-m"     # host:port:database form
        container_name = f"omniboard_{uuid.uuid4().hex[:8]}"
        
        docker_cmd = [
            "docker", "run", "-d", "--rm",
            "-p", f"{host_port}:9000",
            "--name", container_name,
            "vivekratnavel/omniboard",
            mongo_flag, mongo_arg,
        ]
        
        # Launch container in detached mode
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.Popen(
            docker_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        
        return container_name, host_port
    
    @staticmethod
    def list_containers() -> List[str]:
        """List all Omniboard container IDs.
        
        Returns:
            List of container IDs
        """
        try:
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            result = subprocess.run(
                'docker ps -a --filter "name=omniboard_" --format "{{.ID}}"',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=creationflags,
            )
            return result.stdout.strip().splitlines()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []
    
    def clear_all_containers(self) -> int:
        """Remove all Omniboard Docker containers.
        
        Returns:
            Number of containers removed
        """
        container_ids = self.list_containers()
        
        if not container_ids:
            return 0
        
        for cid in container_ids:
            try:
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
                subprocess.run(
                    f"docker rm -f {cid}",
                    shell=True,
                    timeout=10,
                    creationflags=creationflags,
                )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        return len(container_ids)
