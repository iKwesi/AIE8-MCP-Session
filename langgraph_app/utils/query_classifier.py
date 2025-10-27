"""
Query classification using pattern matching.

Classifies queries into task types based on regex patterns.
"""

import re
import logging
from ..config.task_mappings import TASK_PATTERNS, TASK_WORKFLOWS, TaskType

logger = logging.getLogger(__name__)


def classify_query(query: str) -> TaskType:
    """
    Classify query into a task type using pattern matching.
    
    Patterns are checked in priority order:
    1. dice_action (most specific)
    2. research (specific keywords)
    3. general (fallback)
    
    Args:
        query: User query string
        
    Returns:
        TaskType: One of "dice_action", "research", or "general"
    """
    query_lower = query.lower()
    
    # Try each task type in priority order
    for task_type in ["dice_action", "research"]:
        patterns = TASK_PATTERNS[task_type]
        
        # Check if any pattern matches
        for pattern in patterns:
            if re.search(pattern, query_lower):
                logger.info(f"📋 Classified as '{task_type}' (matched pattern: {pattern})")
                return task_type
    
    # Fallback to general
    logger.info(f"📋 Classified as 'general' (no specific pattern matched)")
    return "general"


def get_workflow_for_task(task_type: TaskType) -> list:
    """
    Get the workflow steps for a given task type.
    
    Args:
        task_type: The classified task type
        
    Returns:
        List of workflow steps
    """
    return TASK_WORKFLOWS[task_type]


def should_use_web_search(query: str) -> bool:
    """
    Determine if web search should be added as a fallback.
    
    Checks for keywords that suggest need for current information.
    
    Args:
        query: User's query
        
    Returns:
        Boolean indicating if web search should be used
    """
    # Keywords that suggest need for current information
    current_info_keywords = [
        "latest", "current", "recent", "today", "now",
        "news", "update", "2024", "2025", "this year"
    ]
    
    query_lower = query.lower()
    has_current_keyword = any(keyword in query_lower for keyword in current_info_keywords)
    
    if has_current_keyword:
        logger.info(f"🔍 Detected need for current information in query")
    
    return has_current_keyword
