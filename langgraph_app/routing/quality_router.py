"""
Quality-based routing logic.

Determines whether to proceed, retry, or fail based on quality score.
"""

from ..state import ResearchState
from ..config import config


def check_quality(state: ResearchState) -> str:
    """
    Determines routing based on analysis quality.
    
    Checks if the quality score meets the threshold and decides
    whether to proceed with synthesis, retry the analysis, or
    give up and synthesize anyway.
    
    Args:
        state: Current research state
        
    Returns:
        Next node identifier:
        - "pass": Quality is acceptable, proceed to synthesize_node
        - "retry": Quality is low and retries available, go to retry_handler_node
        - "fail": Quality is low but max retries reached, proceed to synthesize_node anyway
    """
    quality_score = state.get("quality_score", 0.0)
    retry_count = state.get("retry_count", 0)
    
    # Check if quality meets threshold
    if quality_score >= config.quality_threshold:
        return "pass"
    
    # Quality is below threshold - check if we can retry
    if retry_count < config.max_retries:
        return "retry"
    
    # Max retries reached - proceed anyway with warning
    return "fail"
