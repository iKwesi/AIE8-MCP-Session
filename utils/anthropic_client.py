# utils/anthropic_client.py
"""
Cached Anthropic API client.

Uses functools.lru_cache to ensure we only create one client instance
per process, avoiding unnecessary initialization overhead.
"""

import os
from anthropic import Anthropic
from functools import lru_cache


@lru_cache(maxsize=1)
def get_anthropic_client() -> Anthropic:
    """
    Return a cached Anthropic client using API key from environment.
    
    The client is initialized once and reused across all calls.
    Fails fast if the API key is missing with a clear error message.
    
    Returns:
        Anthropic: Configured Anthropic client instance
        
    Raises:
        EnvironmentError: If ANTHROPIC_API_KEY is not set
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        raise EnvironmentError(
            "Missing Anthropic API key. Please set ANTHROPIC_API_KEY in your .env file."
        )
    
    return Anthropic(api_key=api_key)