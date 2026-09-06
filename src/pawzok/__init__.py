"""Pawzok public API."""

from .exceptions import PawzokAssertionError
from .result import SQLResult
from .sql import assert_sql

__all__ = ["assert_sql", "PawzokAssertionError", "SQLResult"]
__version__ = "0.1.1"
