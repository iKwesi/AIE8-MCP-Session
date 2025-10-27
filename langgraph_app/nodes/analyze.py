"""
Question analysis node.

Analyzes the user's question to determine its type and appropriate workflow path.
"""

from ..state import ResearchState


async def analyze_question_node(state: ResearchState, tools: dict) -> dict:
    """
    Analyzes question to determine type and workflow path.
    
    Uses the ask_specialized_claude tool to classify the question into
    one of four types: factual, analytical, creative, or technical.
    
    Args:
        state: Current research state
        tools: Dictionary of available MCP tools
        
    Returns:
        Updated state with question_type and initialized retry_count
    """
    # Get the specialized Claude tool
    claude_tool = tools.get("ask_specialized_claude")
    
    if not claude_tool:
        return {
            "question_type": "factual",  # Default fallback
            "retry_count": 0,
            "error": "ask_specialized_claude tool not available"
        }
    
    # Build classification prompt
    classifier_prompt = f"""Analyze this question and classify it into ONE of these categories:

Question: {state['query']}

Categories:
- factual: Needs web search for current facts, news, or real-world information
- analytical: Needs deep reasoning, analysis, or problem-solving
- creative: Needs creative generation, storytelling, or ideation
- technical: Needs technical explanation or how-to guidance

Return ONLY the category name (factual, analytical, creative, or technical).
No explanation, just the single word."""
    
    try:
        # Call Claude for classification
        result = await claude_tool.ainvoke({
            "prompt": classifier_prompt,
            "task_type": "general",
            "max_tokens": 50
        })
        
        # Extract and validate question type
        question_type = result.strip().lower()
        
        # Validate it's one of our expected types
        valid_types = ["factual", "analytical", "creative", "technical"]
        if question_type not in valid_types:
            question_type = "factual"  # Default fallback
        
        return {
            "question_type": question_type,
            "retry_count": 0
        }
        
    except Exception as e:
        return {
            "question_type": "factual",  # Default fallback
            "retry_count": 0,
            "error": f"Error in question analysis: {str(e)}"
        }
