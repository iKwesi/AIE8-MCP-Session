"""
Retry decision routing logic.

Determines whether to retry analysis or give up.
"""

from ..state import ResearchState
from ..config import config


def should_retry(state: ResearchState) -> str:
    """
    Decides whether to retry analysis or give up.
    
    Checks the retry count against the maximum allowed retries
    to determine if another attempt should be made.
    
    Args:
        state: Current research state
        
    Returns:
        Next node identifier:
        - "retry": Retry count below max, go back to deep_analysis_node
        - "give_up": Max retries reached, proceed to synthesize_node
    """
    retry_count = state.get("retry_count", 0)
    
    # Check if we can retry
    if retry_count < config.max_retries:
        return "retry"
    else:
        return "give_up"
