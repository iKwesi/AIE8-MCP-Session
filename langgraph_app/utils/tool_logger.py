"""
Tool logging utilities.

Provides consistent, detailed logging for all MCP tool calls.
"""

import logging

logger = logging.getLogger(__name__)


def log_tool_call(tool_name: str, params: dict) -> None:
    """
    Log when a tool is being called.
    
    Args:
        tool_name: Name of the MCP tool being called
        params: Parameters being passed to the tool
    """
    logger.info(f"🔧 Calling tool: {tool_name}")
    logger.info(f"   Parameters: {params}")


def log_tool_result(tool_name: str, result: str, truncate: int = 100) -> None:
    """
    Log the result of a tool call.
    
    Args:
        tool_name: Name of the MCP tool that was called
        result: Result returned by the tool
        truncate: Maximum length for result preview (default 100)
    """
    result_preview = result[:truncate] + "..." if len(result) > truncate else result
    logger.info(f"✅ Tool {tool_name} returned: {result_preview}")
    logger.info(f"   Total length: {len(result)} characters")


def log_tool_error(tool_name: str, error: Exception) -> None:
    """
    Log when a tool call fails.
    
    Args:
        tool_name: Name of the MCP tool that failed
        error: Exception that was raised
    """
    logger.error(f"❌ Tool {tool_name} failed: {str(error)}")
