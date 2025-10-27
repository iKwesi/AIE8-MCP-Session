"""
Query analysis node.

Analyzes query, classifies type, and creates execution plan.
"""

import logging
from ..state import ResearchState
from ..utils.query_classifier import classify_query, get_workflow_for_task, should_use_web_search

logger = logging.getLogger(__name__)


async def analyze_query_node(state: ResearchState, tools: dict) -> dict:
    """
    Analyze query and create execution plan.
    
    This node:
    - Classifies the query type
    - Selects appropriate tools based on task_mappings
    - Checks if web search should be added dynamically
    - Creates a workflow plan
    
    Args:
        state: Current research state
        tools: Dictionary of available MCP tools
        
    Returns:
        Updated state with analysis and execution plan
    """
    
    query = state['query']
    
    logger.info(f"\n{'='*60}")
    logger.info(f"📊 QUERY ANALYSIS")
    logger.info(f"{'='*60}")
    
    # Step 1: Classify query
    task_type = classify_query(query)
    logger.info(f"   Type: {task_type}")
    
    # Step 2: Get base workflow
    workflow_plan = get_workflow_for_task(task_type)
    
    # Step 3: Check if we should add web search dynamically (for general queries)
    if task_type == "general" and should_use_web_search(query):
        logger.info(f"   🔍 Adding web_search to general workflow (detected current info need)")
        
        # Prepend web search to general workflow
        workflow_plan = [
            {
                "step": 0,
                "tool": "web_search",
                "action": "Search for current information",
                "task_type": None
            },
            *workflow_plan
        ]
    
    # Step 4: Extract tool names WITH task_type for clarity
    selected_tools = []
    for step in workflow_plan:
        tool_name = step['tool']
        task_type_param = step.get('task_type')
        
        if task_type_param:
            # Show task_type for ask_specialized_claude
            selected_tools.append(f"{tool_name}({task_type_param})")
        else:
            selected_tools.append(tool_name)
    
    logger.info(f"   Tools: {', '.join(selected_tools)}")
    logger.info(f"   Workflow steps: {len(workflow_plan)}")
    logger.info(f"{'='*60}\n")
    
    # Step 5: Create processing log
    step_log = (
        f"📊 Query Analysis:\n"
        f"  Type: {task_type}\n"
        f"  Tools: {', '.join(selected_tools)}\n"
        f"  Steps: {len(workflow_plan)}"
    )
    
    # Update state
    return {
        "task_type": task_type,
        "selected_tools": selected_tools,
        "workflow_plan": workflow_plan,
        "processing_steps": [step_log]
    }
