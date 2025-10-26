# utils/__init__.py
"""
Utility functions and API clients.
Each client is cached to avoid reinitializing on every call.
"""

from .anthropic_client import get_anthropic_client
from .wolfram_client import get_wolfram_client
from .github_client import get_github_client
from .nasa_client import get_nasa_api_key

__all__ = [
    "get_anthropic_client",
    "get_wolfram_client", 
    "get_github_client",
    "get_nasa_api_key",
]