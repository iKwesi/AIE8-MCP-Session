"""
Tool executor node.

Executes tools based on declarative workflow configuration.
"""

import re
import logging
from ..state import ResearchState
from ..config.task_mappings import WorkflowStep
from ..utils.query_classifier import classify_query, get_workflow_for_task
from ..utils.tool_logger import log_tool_call, log_tool_result, log_tool_error

logger = logging.getLogger(__name__)


async def tool_executor_node(state: ResearchState, tools: dict) -> dict:
    """
    Execute tools based on the plan created by analyze_query_node.
    
    Reads workflow_plan from state and executes it step-by-step.
    
    Args:
        state: Current research state
        tools: Dictionary of available MCP tools
        
    Returns:
        Updated state with execution results
    """
    
    # Get workflow plan from state (created by analyze_query_node)
    workflow_plan = state.get("workflow_plan")
    
    if not workflow_plan:
        logger.error("❌ No workflow plan found in state")
        return {"error": "No workflow plan found in state"}
    
    task_type = state.get("task_type", "general")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"🚀 TOOL EXECUTION")
    logger.info(f"{'='*60}")
    logger.info(f"   Task type: {task_type}")
    logger.info(f"   Workflow steps: {len(workflow_plan)}")
    logger.info(f"{'='*60}\n")
    
    # Execute the workflow
    return await _execute_workflow(task_type, workflow_plan, state, tools)


async def _execute_workflow(
    task_type: str,
    workflow_steps: list[WorkflowStep],
    state: ResearchState,
    tools: dict
) -> dict:
    """
    Execute a multi-step workflow.
    
    Each step is executed in order, with results passed to subsequent steps.
    
    Args:
        task_type: The classified task type
        workflow_steps: List of workflow steps to execute
        state: Current research state
        tools: Dictionary of available MCP tools
        
    Returns:
        Updated state with all execution results
    """
    
    results = {
        "task_type": task_type,
        "tools_used": [],
        "workflow_steps": []
    }
    
    # Context that accumulates across steps
    context = {
        "query": state['query'],
        "search_results": None,
        "summary": None,
        "explanation": None
    }
    
    # Execute each step in order
    for step_config in workflow_steps:
        step_num = step_config["step"]
        tool_name = step_config["tool"]
        action = step_config["action"]
        task_type_param = step_config.get("task_type")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📍 Step {step_num}: {action}")
        logger.info(f"🔧 Tool: {tool_name}")
        if task_type_param:
            logger.info(f"🎨 Task Type: {task_type_param}")
        logger.info(f"{'='*60}")
        
        try:
            # Execute the step
            step_result = await _execute_step(
                tool_name=tool_name,
                action=action,
                task_type_param=task_type_param,
                context=context,
                tools=tools
            )
            
            # Record step execution
            results["tools_used"].append(tool_name)
            results["workflow_steps"].append({
                "step": step_num,
                "tool": tool_name,
                "action": action,
                "success": True
            })
            
            # Update context for next step
            _update_context(context, tool_name, action, step_result)
            
        except Exception as e:
            log_tool_error(tool_name, e)
            results["workflow_steps"].append({
                "step": step_num,
                "tool": tool_name,
                "action": action,
                "success": False,
                "error": str(e)
            })
            # Continue with remaining steps even if one fails
    
    # Set final results based on what's available in context
    if context.get("explanation"):
        results["final_answer"] = context["explanation"]
    elif context.get("summary"):
        results["final_answer"] = context["summary"]
    elif context.get("search_results"):
        results["search_results"] = context["search_results"]
        if not context.get("summary"):
            # If we only have search results, use them as final answer
            results["final_answer"] = context["search_results"]
    
    # For dice rolls, the result is stored differently
    if task_type == "dice_action" and "dice_result" in context:
        results["final_answer"] = context["dice_result"]
    
    return results


async def _execute_step(
    tool_name: str,
    action: str,
    task_type_param: str | None,
    context: dict,
    tools: dict
) -> str:
    """
    Execute a single workflow step.
    
    Args:
        tool_name: Name of the tool to execute
        action: Description of what this step does
        task_type_param: Task type for ask_specialized_claude (None for other tools)
        context: Accumulated context from previous steps
        tools: Dictionary of available MCP tools
        
    Returns:
        Result from the tool execution
    """
    
    tool = tools.get(tool_name)
    if not tool:
        raise ValueError(f"Tool '{tool_name}' not available")
    
    if tool_name == "roll_dice":
        # Parse dice parameters from query
        notation, num_rolls = _parse_dice_query(context["query"])
        
        log_tool_call("roll_dice", {
            "notation": notation,
            "num_rolls": num_rolls,
            "action": action
        })
        
        result = await tool.ainvoke({
            "notation": notation,
            "num_rolls": num_rolls
        })
        
        log_tool_result("roll_dice", result)
        return result
    
    elif tool_name == "web_search":
        log_tool_call("web_search", {
            "query": context["query"],
            "action": action
        })
        
        result = await tool.ainvoke({"query": context["query"]})
        
        log_tool_result("web_search", result)
        return result
    
    elif tool_name == "ask_specialized_claude":
        # Build prompt based on available context and action
        prompt = _build_claude_prompt(action, context)
        
        log_tool_call("ask_specialized_claude", {
            "task_type": task_type_param,
            "action": action,
            "prompt_length": len(prompt)
        })
        
        result = await tool.ainvoke({
            "prompt": prompt,
            "task_type": task_type_param or "general",
            "max_tokens": 2048
        })
        
        log_tool_result("ask_specialized_claude", result)
        return result
    
    else:
        raise ValueError(f"Unknown tool: {tool_name}")


def _build_claude_prompt(action: str, context: dict) -> str:
    """
    Build Claude prompt based on action and available context.
    
    Args:
        action: Description of what this step should do
        context: Accumulated context from previous steps
        
    Returns:
        Formatted prompt for Claude
    """
    
    query = context["query"]
    
    if action == "Summarize findings" and context.get("search_results"):
        return f"""Question: {query}

Web Search Results:
{context['search_results']}

Based on the search results above, provide a comprehensive summary that answers the question."""
    
    elif action == "Explain simply" and context.get("summary"):
        return f"""Question: {query}

Summary:
{context['summary']}

Explain this in simple, easy-to-understand terms as if teaching someone new to the topic."""
    
    else:
        # Default: just the query
        return query


def _update_context(context: dict, tool_name: str, action: str, result: str) -> None:
    """
    Update context with step results.
    
    Args:
        context: Context dictionary to update
        tool_name: Name of the tool that was executed
        action: Description of what the step did
        result: Result from the tool execution
    """
    
    if tool_name == "roll_dice":
        context["dice_result"] = result
    
    elif tool_name == "web_search":
        context["search_results"] = result
    
    elif tool_name == "ask_specialized_claude":
        # Determine what type of result this is based on action
        if "Summarize" in action:
            context["summary"] = result
        elif "Explain" in action:
            context["explanation"] = result
        else:
            # General answer
            context["answer"] = result


def _parse_dice_query(query: str) -> tuple[str, int]:
    """
    Parse dice notation and number of rolls from query.
    
    Examples:
        "roll a dice 5 times" → ("1d6", 5)
        "roll 2d20" → ("2d20", 1)
        "roll 3d6k2 four times" → ("3d6k2", 4)
    
    Args:
        query: User query string
        
    Returns:
        Tuple of (notation, num_rolls)
    """
    
    query_lower = query.lower()
    
    # Find dice notation (e.g., "2d20", "3d6k2")
    dice_match = re.search(r'(\d+d\d+(?:k\d+)?)', query_lower)
    notation = dice_match.group(1) if dice_match else "1d6"
    
    # Find number of rolls
    num_match = re.search(r'(\d+)\s*times?', query_lower)
    num_rolls = int(num_match.group(1)) if num_match else 1
    
    logger.info(f"📊 Parsed dice: notation={notation}, num_rolls={num_rolls}")
    
    return notation, num_rolls
