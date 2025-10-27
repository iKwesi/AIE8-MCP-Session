"""
Retry handler node.

Manages retry logic when analysis quality is below threshold.
"""

from ..state import ResearchState
from langchain_core.messages import HumanMessage


async def retry_handler_node(state: ResearchState, tools: dict) -> dict:
    """
    Handles retry logic with improved prompting.
    
    Increments retry count and provides feedback to improve
    the next analysis attempt.
    
    Args:
        state: Current research state
        tools: Dictionary of available MCP tools (not used in this node)
        
    Returns:
        Updated state with incremented retry_count and feedback message
    """
    retry_count = state.get("retry_count", 0)
    quality_score = state.get("quality_score", 0)
    
    # Build feedback message for retry
    feedback_message = f"""Previous analysis quality was below threshold (score: {quality_score:.1f}/10).

Original question: {state['query']}

Previous analysis:
{state.get('analysis', '')}

Please provide a more detailed and accurate analysis. Focus on:
1. Directly answering the question
2. Providing specific details and examples
3. Being clear and concise
4. Ensuring accuracy and completeness"""
    
    return {
        "retry_count": retry_count + 1,
        "messages": [HumanMessage(content=feedback_message)]
    }
