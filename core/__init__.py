# core/__init__.py
"""
Core module for MCP server infrastructure.
Contains shared MCP instance and configuration management.
"""

from .mcp_instance import mcp
from .config import init_config

__all__ = ["mcp", "init_config"]