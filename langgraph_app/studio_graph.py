"""
LangGraph Studio Entry Point

Provides a synchronous function that returns a compiled graph for Studio.
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.graph import StateGraph, START, END

from .state import ResearchState
from .config import config
from .nodes import (
    analyze_query_node,
    tool_executor_node,
    synthesize_with_claude_node,
    quality_check_node,
    retry_handler_node,
    format_output_node,
)
from .routing import (
    check_quality,
    should_retry,
)


def create_studio_graph():
    """
    Creates a compiled graph for LangGraph Studio.
    
    Note: This is a simplified version that doesn't connect to MCP
    for Studio visualization purposes. The actual MCP connection
    happens at runtime when you execute queries in Studio.
    
    Returns:
        Compiled LangGraph workflow
    """
    
    # Create mock tools dictionary for graph structure
    # Studio will handle actual tool execution at runtime
    mock_tools = {}
    
    # Create wrapper functions
    async def analyze_node(state: ResearchState):
        return await analyze_query_node(state, mock_tools)
    
    async def executor_node(state: ResearchState):
        return await tool_executor_node(state, mock_tools)
    
    async def synthesis_node(state: ResearchState):
        return await synthesize_with_claude_node(state, mock_tools)
    
    async def quality_node(state: ResearchState):
        return await quality_check_node(state, mock_tools)
    
    async def retry_node(state: ResearchState):
        return await retry_handler_node(state, mock_tools)
    
    async def format_node(state: ResearchState):
        return await format_output_node(state, mock_tools)
    
    # Build the graph
    workflow = StateGraph(ResearchState)
    
    # Add all nodes
    workflow.add_node("analyze_query", analyze_node)
    workflow.add_node("tool_executor", executor_node)
    workflow.add_node("synthesize_with_claude", synthesis_node)
    workflow.add_node("quality_check", quality_node)
    workflow.add_node("retry_handler", retry_node)
    workflow.add_node("format_output", format_node)
    
    # Build the workflow
    workflow.add_edge(START, "analyze_query")
    workflow.add_edge("analyze_query", "tool_executor")
    workflow.add_edge("tool_executor", "synthesize_with_claude")
    workflow.add_edge("synthesize_with_claude", "quality_check")
    
    workflow.add_conditional_edges(
        "quality_check",
        check_quality,
        {
            "pass": "format_output",
            "retry": "retry_handler",
            "fail": "format_output"
        }
    )
    
    workflow.add_conditional_edges(
        "retry_handler",
        should_retry,
        {
            "retry": "analyze_query",
            "give_up": "format_output"
        }
    )
    
    workflow.add_edge("format_output", END)
    
    # Return compiled graph
    return workflow.compile()
