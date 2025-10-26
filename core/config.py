# core/config.py
"""
Configuration management for the MCP server.

Handles environment variable loading and any early initialization
that needs to happen before tools are registered.
"""

from dotenv import load_dotenv


def init_config():
    """
    Load environment variables and perform any early setup.
    
    This should be called once at server startup before any
    tools attempt to access environment variables.
    """
    load_dotenv()
    
    # Future: Add logging configuration, feature flags, etc.
    # For now, just load environment variables