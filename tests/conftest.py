"""Test configuration and fixtures.

Ensure the project root (which contains the ``src`` package) is on ``sys.path``
so imports like ``from src.mongodb import MongoDBClient`` work regardless of
where pytest is invoked from.
"""
import pytest
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
	sys.path.insert(0, str(project_root))
