"""
Synthesis node.

Creates the final polished answer from the analysis.
"""

from ..state import ResearchState


async def synthesize_node(state: ResearchState, tools: dict) -> dict:
    """
    Synthesizes final answer from analysis.
    
    Uses specialized Claude in creative mode to produce a polished,
    well-formatted final answer that directly addresses the user's question.
    
    Args:
        state: Current research state
        tools: Dictionary of available MCP tools
        
    Returns:
        Updated state with final_answer
    """
    # Get the specialized Claude tool
    claude_tool = tools.get("ask_specialized_claude")
    
    if not claude_tool:
        # Fallback to using the analysis directly
        return {
            "final_answer": state.get("analysis", "Unable to generate answer."),
            "error": "ask_specialized_claude tool not available for synthesis"
        }
    
    # Build synthesis prompt
    synthesis_prompt = f"""Create a final, polished answer to this question.

Original Question: {state['query']}

Analysis:
{state.get('analysis', '')}

Create a clear, well-structured final answer that:
1. Directly answers the question
2. Is easy to understand
3. Is properly formatted
4. Includes key insights from the analysis

Make it concise but complete."""
    
    try:
        # Call specialized Claude in creative mode for polished output
        result = await claude_tool.ainvoke({
            "prompt": synthesis_prompt,
            "task_type": "creative",
            "max_tokens": 1024
        })
        
        return {"final_answer": result}
        
    except Exception as e:
        # Fallback to using the analysis directly
        return {
            "final_answer": state.get("analysis", "Unable to generate answer."),
            "error": f"Error in synthesis: {str(e)}"
        }
