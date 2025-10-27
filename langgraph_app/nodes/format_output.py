"""
Output formatting node.

Formats the final response for user presentation.
"""

import logging
from ..state import ResearchState

logger = logging.getLogger(__name__)


async def format_output_node(state: ResearchState, tools: dict) -> dict:
    """
    Format the final response for presentation.
    
    This node:
    - Formats the answer nicely
    - Adds metadata (query type, tools used, quality score)
    - Includes processing steps for transparency
    - Prepares for output
    
    Args:
        state: Current research state
        tools: Dictionary of available MCP tools (not used in this node)
        
    Returns:
        Updated state with formatted final_answer
    """
    
    logger.info(f"\n{'='*60}")
    logger.info(f"📄 OUTPUT FORMATTING")
    logger.info(f"{'='*60}\n")
    
    final_answer = state.get("final_answer", "")
    processing_steps = state.get("processing_steps", [])
    task_type = state.get("task_type", "general")
    tools_used = state.get("tools_used", [])
    quality_score = state.get("quality_score", 0.0)
    workflow_steps = state.get("workflow_steps", [])
    
    # Build formatted response
    formatted_response = f"""{'='*80}
🎯 Research Assistant Result
{'='*80}

Task Type: {task_type.upper()}
Tools Used: {', '.join(tools_used) if tools_used else 'None'}
Quality Score: {quality_score:.1f}/10
Workflow Steps: {len(workflow_steps)}

{'='*80}
💡 ANSWER
{'='*80}

{final_answer}

{'='*80}
📊 Processing Steps
{'='*80}
"""
    
    for i, step in enumerate(processing_steps, 1):
        formatted_response += f"\n{i}. {step}"
    
    # Add workflow execution details
    if workflow_steps:
        formatted_response += f"\n\n{'='*80}\n🔧 Workflow Execution\n{'='*80}\n"
        for step in workflow_steps:
            status = "✅" if step.get("success", True) else "❌"
            formatted_response += f"\n{status} Step {step['step']}: {step['action']} ({step['tool']})"
            if not step.get("success", True):
                formatted_response += f" - Error: {step.get('error', 'Unknown')}"
    
    # Add errors if any
    if state.get("error"):
        formatted_response += f"\n\n{'='*80}\n⚠️  Errors Encountered\n{'='*80}\n"
        formatted_response += f"\n• {state['error']}"
    
    formatted_response += f"\n\n{'='*80}\n"
    
    logger.info("✅ Output formatted successfully\n")
    
    return {"final_answer": formatted_response}
