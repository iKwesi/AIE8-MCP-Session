# server.py
"""
MCP Server - Main Entry Point

This is the single entrypoint for the MCP server. It's intentionally
minimal and declarative - all the heavy lifting happens in modules.

Architecture:
1. Load configuration (environment variables)
2. Import tools (they self-register with shared MCP instance)
3. Register any legacy tools (web_search, roll_dice)
4. Start the server
"""

from core.config import init_config
from core.mcp_instance import mcp
from tavily import TavilyClient
import os
from dice_roller import DiceRoller

# ============================================================================
# INITIALIZE CONFIGURATION
# ============================================================================
# Load environment variables before anything else
init_config()

# ============================================================================
# IMPORT TOOLS (they self-register on import)
# ============================================================================

# ✅ ACTIVE: Specialized Claude (Meta-AI)

import tools.anthropic_tools

# ============================================================================
# LEGACY TOOLS (Original from starter code)
# ============================================================================

# Initialize Tavily client for web search
tavily_client = TavilyClient(os.getenv("TAVILY_API_KEY"))


@mcp.tool()
def web_search(query: str) -> str:
    """
    Search the web for information using Tavily API.
    
    Args:
        query: Search query string
        
    Returns:
        Search results context from Tavily
    """
    try:
        search_results = tavily_client.get_search_context(query=query)
        return search_results
    except Exception as e:
        return f"Error performing web search: {str(e)}"


@mcp.tool()
def roll_dice(notation: str, num_rolls: int = 1) -> str:
    """
    Roll dice with D&D-style notation (e.g., 2d20k1).
    
    Args:
        notation: Dice notation (e.g., "2d20k1" = roll 2d20, keep highest 1)
        num_rolls: Number of times to roll (default 1)
        
    Returns:
        Formatted dice roll results
    """
    try:
        roller = DiceRoller(notation, num_rolls)
        return str(roller)
    except ValueError as e:
        return f"Invalid dice notation: {str(e)}"
    except Exception as e:
        return f"Error rolling dice: {str(e)}"


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Starting MCP Server")
    print("=" * 60)
    print("\nActive Tools:")
    print("  ✅ ask_specialized_claude (Meta-AI)")
    print("  ✅ web_search (Tavily)")
    print("  ✅ roll_dice (D&D dice roller)")
    print("\n" + "=" * 60)
    print("Server running on stdio transport...")
    print("=" * 60 + "\n")
    
    # Run the server with stdio transport (how Cursor communicates)
    mcp.run(transport="stdio")