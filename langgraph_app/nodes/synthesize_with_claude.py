"""
Synthesis node - Creates coherent answer from tool results.

Uses Claude to synthesize tool results into a coherent final answer.
"""

import logging
from ..state import ResearchState
from ..utils.tool_logger import log_tool_call, log_tool_result

logger = logging.getLogger(__name__)


async def synthesize_with_claude_node(state: ResearchState, tools: dict) -> dict:
    """
    Synthesize tool results into coherent answer.
    
    This node:
    - Takes results from tool_executor
    - Uses appropriate Claude specialization
    - Generates coherent final answer
    
    Args:
        state: Current research state
        tools: Dictionary of available MCP tools
        
    Returns:
        Updated state with synthesized final_answer
    """
    
    query = state['query']
    task_type = state.get('task_type', 'general')
    
    logger.info(f"\n{'='*60}")
    logger.info(f"✨ SYNTHESIS WITH CLAUDE")
    logger.info(f"{'='*60}")
    
    # Get Claude tool
    claude_tool = tools.get("ask_specialized_claude")
    
    if not claude_tool:
        logger.warning("⚠️  ask_specialized_claude not available, using raw results")
        return {"final_answer": state.get("final_answer", "")}
    
    # Determine Claude task type based on query type
    claude_task_map = {
        "dice_action": None,  # Skip synthesis for dice
        "research": "creative",  # Creative synthesis for research
        "general": "general"  # General synthesis
    }
    
    claude_task_type = claude_task_map.get(task_type, "general")
    
    # Skip synthesis for dice actions (results are already final)
    if task_type == "dice_action":
        logger.info("   Skipping synthesis for dice_action (results are final)")
        return {"final_answer": state.get("final_answer", "")}
    
    logger.info(f"   Claude mode: {claude_task_type}")
    
    # Build context from tool results
    context_parts = []
    
    if state.get("search_results"):
        context_parts.append(f"=== Web Search Results ===\n{state['search_results']}")
    
    if state.get("analysis"):
        context_parts.append(f"=== Analysis ===\n{state['analysis']}")
    
    # If tool_executor already produced a final_answer, use it
    if state.get("final_answer") and not context_parts:
        context_parts.append(f"=== Tool Results ===\n{state['final_answer']}")
    
    context = "\n\n".join(context_parts) if context_parts else ""
    
    # Build synthesis prompt
    if context:
        prompt = f"""Based on this information:

{context}

Create a comprehensive, coherent answer to: {query}

Synthesize the information into a clear, well-structured response."""
    else:
        prompt = query
    
    try:
        # Synthesize with Claude
        log_tool_call("ask_specialized_claude", {
            "task_type": claude_task_type,
            "action": "Synthesize final answer",
            "context_length": len(context)
        })
        
        result = await claude_tool.ainvoke({
            "prompt": prompt,
            "task_type": claude_task_type,
            "max_tokens": 2048
        })
        
        log_tool_result("ask_specialized_claude", result)
        
        logger.info(f"{'='*60}\n")
        
        # Add processing step
        step_log = f"✨ Synthesized with Claude ({claude_task_type} mode)"
        processing_steps = state.get("processing_steps", [])
        processing_steps.append(step_log)
        
        return {
            "final_answer": result,
            "processing_steps": processing_steps
        }
        
    except Exception as e:
        logger.error(f"❌ Error in synthesis: {str(e)}")
        
        # Fallback to using existing results
        fallback_answer = state.get("final_answer") or state.get("analysis") or "Unable to synthesize answer"
        
        return {
            "final_answer": fallback_answer,
            "error": f"Synthesis error: {str(e)}"
        }
