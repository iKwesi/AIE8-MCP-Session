"""
Web search node.

Performs web search using the Tavily API via MCP.
"""

from ..state import ResearchState


async def web_search_node(state: ResearchState, tools: dict) -> dict:
    """
    Searches the web for information related to the query.
    
    Uses the web_search MCP tool (Tavily API) to gather current
    information from the internet.
    
    Args:
        state: Current research state
        tools: Dictionary of available MCP tools
        
    Returns:
        Updated state with search_results
    """
    # Get the web search tool
    search_tool = tools.get("web_search")
    
    if not search_tool:
        return {
            "search_results": "",
            "error": "web_search tool not available"
        }
    
    try:
        # Perform web search
        result = await search_tool.ainvoke({
            "query": state['query']
        })
        
        return {"search_results": result}
        
    except Exception as e:
        return {
            "search_results": "",
            "error": f"Error in web search: {str(e)}"
        }
