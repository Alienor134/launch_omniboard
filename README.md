# AltarViewer

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPL%20v3-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0--dev-orange.svg)](https://github.com/Alienor134/launch_omniboard/releases)

A graphical user interface application for launching and managing [Omniboard](https://vivekratnavel.github.io/omniboard/) instances to visualize and track MongoDB-backed experiments from the DREAM/Altar ecosystem.

<div align="center">
  <img src="https://raw.githubusercontent.com/DreamRepo/AltarViewer/refs/heads/main/assets/image_ctk.png" width="26%" />
  <img src="https://raw.githubusercontent.com/DreamRepo/AltarViewer/refs/heads/main/assets/image_omniboard.png" width="70%" />
</div>

## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [From Source](#from-source)
  - [From Binary Release](#from-binary-release)
- [Usage](#usage)
  - [Quick Start](#quick-start)
   - [How it works](#how-it-works)
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

- **MongoDB Connection Management**: Connect to local, remote, or Atlas MongoDB instances (port or full URI)
- **Database Discovery**: Automatically list available databases
 - **Web UI**: Dash-based web application served in your browser
 - **One-Click Omniboard Launch**: Starts Omniboard automatically (containerized)
 - **Multi-Instance Support**: Run multiple Omniboard instances on different ports
 - **Deterministic Port Assignment**: Hash-based port generation preserves browser cookies per database
 - **Container Cleanup**: Clear all launched Omniboard instances with one button


## Installation

You can use any of these options:

### Option 1 – Executable

Download the latest platform-specific launcher from the [AltarViewer releases](https://github.com/DreamRepo/AltarViewer/releases) and run it.

### Option 2 – Python app

```bash
git clone https://github.com/DreamRepo/Altar.git
cd Altar/AltarViewer
python -m venv venv

# Activate the venv (one of these)
venv\Scripts\activate      # Windows
source venv/bin/activate    # macOS/Linux

pip install -r requirements.txt
python -m src.main
```

### Prerequisites

- Docker Desktop (Windows/macOS) or Docker Engine (Linux) — required for launching Omniboard automatically
- Python 3.8+ (only required when running from source, see Option 2)


## Usage

1. **Ensure Docker is running**
   - Start Docker Desktop (Windows/macOS) or Docker daemon (Linux)

2. **Start AltarViewer**
   - Executable: double-click `OmniboardLauncher` (Windows: `OmniboardLauncher.exe`)
   - From source: in a venv, run `python -m src.main`

3. **Open the web UI**
   - Executable: your default browser opens automatically to `http://localhost:8060`
   - From source: manually navigate to `http://localhost:8060` (or the port set by `PORT`)

4. **Connect to MongoDB**
   - Enter your MongoDB host and port (default: `localhost:27017`)
   - Click "Connect" to list available databases

5. **Select a database**
   - Choose a database from the list
   - Click "Launch Omniboard"

6. **Access Omniboard**
   - A clickable link will appear in the interface
   - Click the link to open Omniboard in your browser (it starts in the background; refresh after a few seconds if it isn’t ready yet)

### How it works

- AltarViewer launches Omniboard automatically in the background. On desktop systems, Omniboard runs as a container orchestrated via the local Docker CLI.
- Ports are assigned deterministically per database, so your browser keeps Omniboard preferences per database.
- On Windows/macOS, when connecting to a local MongoDB from the container, `localhost` is transparently mapped to `host.docker.internal`.

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
│   ├── app.py           # Dash app factory
│   ├── layout.py        # Dash layout and components
│   ├── callbacks.py     # Dash callbacks wiring UI to logic
│   ├── mongodb.py       # MongoDB connection logic
│   └── omniboard.py     # Omniboard launcher (uses Docker CLI)
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

- **Web UI** ([app.py](src/app.py), [layout.py](src/layout.py), [callbacks.py](src/callbacks.py)): Dash-based interface
- **MongoDB Layer** ([mongodb.py](src/mongodb.py)): Database connection and queries
- **Omniboard Layer** ([omniboard.py](src/omniboard.py)): Omniboard launcher using the Docker CLI with hash-based port assignment
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


## Troubleshooting

### Connection Errors

**Problem**: "Connection Error" when connecting to MongoDB

**Solutions**:
- Ensure MongoDB is running: `mongosh` or `mongo`
- Check the port number (default: 27017)
- Verify firewall settings allow connections
- Check MongoDB logs for authentication issues

### Port Conflicts

**Problem**: "Port already in use" errors

**Solutions**:
- The application automatically finds the next available port if the preferred port is busy
- Check for other applications using ports 20000-29999

**Note**: Each database consistently uses the same port (hash-based), allowing your browser to remember Omniboard customizations and preferences per database

### Omniboard launch issues

**Problem**: Omniboard fails to launch or the link does not open

**Solutions**:
- Ensure Docker is installed and running (Desktop on Windows/macOS, daemon on Linux)
- Wait a few seconds and refresh; Omniboard starts in the background
- Verify you can run `docker info` successfully in a terminal (optional check)

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


### Release Process

1. Update version in relevant files
2. Create a git tag: `git tag -a v1.0.0 -m "Release version 1.0.0"`
3. Push tag: `git push origin v1.0.0`
4. Build and publish release manually (the tagged commit will only produce a draft release)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

