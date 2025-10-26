# utils/__init__.py
"""
Utility functions and API clients.
Each client is cached to avoid reinitializing on every call.
"""

from .anthropic_client import get_anthropic_client


__all__ = [
    "get_anthropic_client",
]