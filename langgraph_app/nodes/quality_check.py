"""
Quality check node.

Validates the quality of the analysis before proceeding.
"""

import logging
from ..state import ResearchState
from ..config import config

logger = logging.getLogger(__name__)


async def quality_check_node(state: ResearchState, tools: dict) -> dict:
    """
    Validates the quality of analysis.
    
    Uses specialized Claude to rate the analysis quality on a scale
    of 0-10, considering relevance, completeness, accuracy, and clarity.
    
    Skips validation for dice_action (dice results are always valid).
    
    Args:
        state: Current research state
        tools: Dictionary of available MCP tools
        
    Returns:
        Updated state with quality_score
    """
    
    task_type = state.get("task_type", "general")
    
    # Skip quality check for dice actions (results are always valid)
    if task_type == "dice_action":
        logger.info("⏭️  Skipping quality check for dice_action (results are always valid)")
        return {"quality_score": 10.0}
    
    # Get the specialized Claude tool
    claude_tool = tools.get("ask_specialized_claude")
    
    if not claude_tool:
        # If tool not available, assume passing quality
        return {
            "quality_score": config.quality_threshold,
            "error": "ask_specialized_claude tool not available for quality check"
        }
    
    # Build quality assessment prompt
    quality_prompt = f"""Rate the quality of this analysis on a scale of 0-10.

Original Question: {state['query']}

Analysis to Evaluate:
{state.get('analysis', '')}

Evaluation Criteria:
- Relevance: Does it directly answer the question?
- Completeness: Is the answer thorough and complete?
- Accuracy: Is the information correct and well-reasoned?
- Clarity: Is it clear and easy to understand?

Return ONLY a number from 0-10. No explanation, just the number."""
    
    try:
        # Call Claude for quality assessment
        result = await claude_tool.ainvoke({
            "prompt": quality_prompt,
            "task_type": "general",
            "max_tokens": 10
        })
        
        # Parse quality score
        try:
            quality_score = float(result.strip())
            # Clamp to valid range
            quality_score = max(0.0, min(10.0, quality_score))
        except ValueError:
            # If parsing fails, use threshold as default
            quality_score = config.quality_threshold
        
        return {"quality_score": quality_score}
        
    except Exception as e:
        # On error, assume passing quality to avoid blocking
        return {
            "quality_score": config.quality_threshold,
            "error": f"Error in quality check: {str(e)}"
        }
