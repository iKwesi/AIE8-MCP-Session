"""
Deep analysis node.

Performs in-depth analysis using specialized Claude with appropriate task profiles.
"""

from ..state import ResearchState


async def deep_analysis_node(state: ResearchState, tools: dict) -> dict:
    """
    Performs deep analysis with specialized Claude.
    
    Selects the appropriate Claude profile based on question type
    and provides comprehensive analysis, optionally incorporating
    web search results if available.
    
    Args:
        state: Current research state
        tools: Dictionary of available MCP tools
        
    Returns:
        Updated state with analysis
    """
    # Get the specialized Claude tool
    claude_tool = tools.get("ask_specialized_claude")
    
    if not claude_tool:
        return {
            "analysis": "",
            "error": "ask_specialized_claude tool not available"
        }
    
    # Map question types to Claude task profiles
    task_type_map = {
        "factual": "summarize",      # Summarize search results
        "analytical": "code_review",  # Deep analytical thinking
        "creative": "creative",       # Creative generation
        "technical": "explain"        # Technical explanations
    }
    
    question_type = state.get("question_type", "factual")
    task_type = task_type_map.get(question_type, "general")
    
    # Build context-aware prompt
    if state.get("search_results"):
        # Include search results in analysis
        prompt = f"""Question: {state['query']}

Web Search Results:
{state['search_results']}

Based on the search results above, provide a comprehensive analysis that directly answers the question.
Focus on accuracy, relevance, and clarity."""
    else:
        # Direct analysis without search results
        prompt = f"""Question: {state['query']}

Provide a comprehensive analysis that directly answers this question.
Focus on accuracy, depth, and clarity."""
    
    try:
        # Call specialized Claude
        result = await claude_tool.ainvoke({
            "prompt": prompt,
            "task_type": task_type,
            "max_tokens": 2048
        })
        
        return {"analysis": result}
        
    except Exception as e:
        return {
            "analysis": "",
            "error": f"Error in deep analysis: {str(e)}"
        }
