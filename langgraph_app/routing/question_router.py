"""
Question type routing logic.

Determines which node to execute based on question classification.
"""

from ..state import ResearchState


def route_by_question_type(state: ResearchState) -> str:
    """
    Routes to appropriate node based on question classification.
    
    Determines the next step in the workflow based on the type
    of question that was identified in the analysis phase.
    
    Args:
        state: Current research state
        
    Returns:
        Next node identifier:
        - "needs_search": Route to web_search_node (for factual questions)
        - "needs_analysis": Route to deep_analysis_node (for analytical/technical)
        - "direct_answer": Route to synthesize_node (for creative questions)
    """
    question_type = state.get("question_type", "factual")
    
    # Routing logic based on question type
    if question_type == "factual":
        # Factual questions need web search for current information
        return "needs_search"
    
    elif question_type in ["analytical", "technical"]:
        # Analytical and technical questions need deep reasoning
        return "needs_analysis"
    
    elif question_type == "creative":
        # Creative questions can go directly to synthesis
        return "direct_answer"
    
    else:
        # Default to search for unknown types
        return "needs_search"
