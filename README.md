# AltarViewer

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPL%20v3-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0--dev-orange.svg)](https://github.com/Alienor134/launch_omniboard/releases)

A graphical user interface application for launching and managing [Omniboard](https://vivekratnavel.github.io/omniboard/) instances to visualize and track MongoDB-backed experiments from the DREAM/Altar ecosystem.

<div align="center">
  <img src="assets/image_ctk.png" width="26%" />
  <img src="assets/image_omniboard.png" width="70%" />
</div>

## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [From Source](#from-source)
  - [From Binary Release](#from-binary-release)
- [Usage](#usage)
  - [Quick Start](#quick-start)
  - [Configuration](#configuration)
- [Development](#development)
  - [Setting Up Development Environment](#setting-up-development-environment)
  - [Running Tests](#running-tests)
  - [Building the Executable](#building-the-executable)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [Versioning](#versioning)
- [License](#license)

## Features

- **MongoDB Connection Management**: Connect to local or remote MongoDB instances
- **Database Discovery**: Automatically list all available databases
- **One-Click Omniboard Launch**: Deploy Omniboard in isolated Docker containers
- **Modern GUI**: Built with CustomTkinter for a clean, modern interface
- **Docker Integration**: Automatic container management and cleanup
- **Multi-Instance Support**: Run multiple Omniboard instances on different ports
- **Deterministic Port Assignment**: Hash-based port generation preserves browser cookies per database
- **Container Cleanup**: Easy removal of all Omniboard containers

## Installation

### Prerequisites

#### System Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux
- **Python**: 3.8 or higher
- **Docker Desktop**: Latest version ([Download](https://www.docker.com/products/docker-desktop/))
- **MongoDB**: Running instance (local or remote)

#### Verify Prerequisites
```bash
# Check Python version
python --version  # Should be 3.8+

# Check Docker is running
docker --version
docker ps

# Check MongoDB is accessible
mongosh --version  # or mongo --version
```

### From Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/DreamRepo/Altar.git
   cd Altar/AltarViewer
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python src/main.py
   ```

### From Binary Release

Download the latest executable from the [releases page](https://github.com/Alienor134/launch_omniboard/releases) and run directly. No Python installation required.

## Usage

### Quick Start

1. **Launch the application**
   ```bash
   python src/main.py
   ```

2. **Connect to MongoDB**
   - Enter your MongoDB host and port (default: `localhost:27017`)
   - Click "Connect" to list available databases

3. **Select a database**
   - Choose a database from the dropdown list
   - Click "Launch Omniboard"

4. **Access Omniboard**
   - A clickable link will appear in the interface
   - Omniboard opens automatically in your default browser

### Configuration

#### MongoDB Connection
- **Default Port**: 27017
- **Connection String**: Supports standard MongoDB URIs
- **Authentication**: Configure in MongoDB settings (currently local connections)

#### Port Management
- **Deterministic Port Assignment**: Ports are generated using a hash of the database name (base: 20000, range: 10000)
- **Browser Cookie Preservation**: The same database always gets the same port, preserving Omniboard customizations and cookies in your browser
- **Automatic Conflict Resolution**: If the preferred port is unavailable, the next free port is automatically selected
- **Port Range**: 20000-29999 (based on SHA-256 hash of database name)

## Development

### Setting Up Development Environment

1. **Clone and setup**
   ```bash
   git clone https://github.com/DreamRepo/Altar.git
   cd Altar/AltarViewer
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

2. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```


### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_mongodb.py

# Run with verbose output
pytest -v
```

### Building the Executable

Build a standalone executable using PyInstaller:

```bash
# Install PyInstaller (if not in requirements-dev.txt)
pip install pyinstaller

# Build executable
pyinstaller OmniboardLauncher.spec

# Output will be in dist/ directory
```

#### Customizing the Build

Edit [OmniboardLauncher.spec](OmniboardLauncher.spec) to customize:
- Application name and icon
- Bundled data files
- Hidden imports
- Build options

## Architecture

```
AltarViewer/
├── src/
│   ├── main.py          # Application entry point
│   ├── gui.py           # GUI implementation (CustomTkinter)
│   ├── mongodb.py       # MongoDB connection logic
│   └── omniboard.py     # Docker/Omniboard management
├── tests/
│   ├── conftest.py      # Pytest configuration
│   ├── test_mongodb.py  # MongoDB tests
│   └── test_omniboard.py # Omniboard tests
├── assets/              # Images and resources
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Development dependencies
└── OmniboardLauncher.spec # PyInstaller specification
```

### Key Components

- **GUI Layer** ([gui.py](src/gui.py)): CustomTkinter-based interface
- **MongoDB Layer** ([mongodb.py](src/mongodb.py)): Database connection and queries
- **Omniboard Layer** ([omniboard.py](src/omniboard.py)): Docker container management with hash-based port assignment
- **Main Controller** ([main.py](src/main.py)): Application orchestration

### Port Assignment Algorithm

The application uses a deterministic hash-based port assignment:
```python
port = 20000 + (SHA256(database_name) % 10000)
```
This ensures:
- **Consistency**: Same database → same port
- **Browser Persistence**: Cookies and customizations are preserved
- **Conflict Handling**: Automatic fallback to next available port if needed

## Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
   ```bash
   git clone https://github.com/YOUR_USERNAME/Altar.git
   cd Altar/AltarViewer
   ```
3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Workflow

1. **Make your changes**
   - Follow [PEP 8](https://pep8.org/) style guidelines
   - Add tests for new features
   - Update documentation as needed

2. **Run tests and linting**
   ```bash
   pytest
   # Add linting tools as configured
   ```

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```
   
   Use [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions or changes
   - `refactor:` Code refactoring
   - `chore:` Maintenance tasks

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure all tests pass

### Code Style

- Follow PEP 8 conventions
- Maximum line length: 100 characters
- Use type hints where applicable
- Document all public functions and classes

### Reporting Issues

- Use the [GitHub issue tracker](https://github.com/DreamRepo/Altar/issues)
- Include Python version, OS, and steps to reproduce
- Provide error messages and logs when applicable

## Troubleshooting

### Connection Errors

**Problem**: "Connection Error" when connecting to MongoDB

**Solutions**:
- Ensure MongoDB is running: `mongosh` or `mongo`
- Check the port number (default: 27017)
- Verify firewall settings allow connections
- Check MongoDB logs for authentication issues

### Docker Issues

**Problem**: Docker-related errors when launching Omniboard

**Solutions**:
- Verify Docker Desktop is running: `docker ps`
- Check Docker has sufficient resources allocated
- Ensure port 9005+ are not in use by other applications
- Try clearing old containers: Use the cleanup button in the app

### Port Conflicts

**Problem**: "Port already in use" errors

**Solutions**:
- The application automatically finds the next available port if the preferred port is busy
- Use the "Clear Omniboard Docker Containers" button to remove old containers
- Manually check and stop containers:
  ```bash
  docker ps
  docker stop <container_id>
  ```
- Check for other applications using ports 20000-29999

**Note**: Each database consistently uses the same port (hash-based), allowing your browser to remember Omniboard customizations and preferences per database

### Import Errors

**Problem**: Missing module errors when running from source

**Solutions**:
- Reinstall dependencies: `pip install -r requirements.txt`
- Ensure virtual environment is activated
- Check Python version compatibility (3.8+)

### Getting Help

- Check existing [GitHub Issues](https://github.com/DreamRepo/Altar/issues)
- Review [Omniboard documentation](https://vivekratnavel.github.io/omniboard/)
- Contact the DREAM/Altar team

## Versioning

This project uses [Semantic Versioning](https://semver.org/) (SemVer):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes
- **-dev**, **-alpha**, **-beta** suffixes for pre-release versions

### Current Version: 1.0.0-dev

### Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and release notes.

### Release Process

1. Update version in relevant files
2. Update CHANGELOG.md with release notes
3. Create a git tag: `git tag -a v1.0.0 -m "Release version 1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. Build and publish release manually

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

---

**Part of the DREAM/Altar Ecosystem**

- [AltarDocker](../AltarDocker/): Docker deployment infrastructure
- [AltarExtractor](../AltarExtractor/): Data extraction and visualization
- [AltarSender](../AltarSender/): Experiment data submission
- [Altar Documentation](../README.md): Main project documentation