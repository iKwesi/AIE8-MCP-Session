# core/mcp_instance.py
"""
Shared FastMCP instance - single source of truth for all tools.

This module provides a global MCP server instance that all tools
register themselves to. This ensures:
- Single coherent namespace for all tools
- One protocol endpoint for Cursor/Claude to discover
- Consistent tool registration pattern
"""

from mcp.server.fastmcp import FastMCP

# Shared global instance for all tools
# All tools will use @mcp.tool() decorator from this instance
mcp = FastMCP("mcp-server")