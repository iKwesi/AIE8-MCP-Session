"""
Adaptive MCP Assistant - Production-Ready Architecture

An intelligent agent that adapts its workflow based on query type,
integrating MCP tools with quality assurance and retry logic.
"""

import logging
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

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResearchAgentContext:
    """Context manager for research agent with proper MCP session lifecycle."""
    
    def __init__(self):
        self.session = None
        self.stdio_context = None
        self.session_context = None
        self.agent = None
    
    async def __aenter__(self):
        """Set up MCP connection and create agent."""
        logger.info("Creating research agent...")
        
        # Connect to MCP server
        server_params = StdioServerParameters(
            command=config.mcp_server_command,
            args=config.mcp_server_args
        )
        
        logger.info(f"Connecting to MCP server: {config.mcp_server_command} {' '.join(config.mcp_server_args)}")
        
        # Establish stdio connection with proper context manager
        self.stdio_context = stdio_client(server_params)
        read, write = await self.stdio_context.__aenter__()
        
        # Create session with proper context manager
        self.session_context = ClientSession(read, write)
        self.session = await self.session_context.__aenter__()
        
        # Initialize MCP session
        await self.session.initialize()
        logger.info("MCP session initialized")
        
        # Load all MCP tools
        tools_list = await load_mcp_tools(self.session)
        
        # Convert tools list to dictionary for easier access
        tools = {tool.name: tool for tool in tools_list}
        
        logger.info(f"Loaded {len(tools)} MCP tools: {list(tools.keys())}")
        
        # Create the agent
        self.agent = await self._build_agent(tools)
        
        return self.agent
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up MCP connection."""
        logger.info("Closing MCP connection...")
        
        # Close session context
        if self.session_context:
            await self.session_context.__aexit__(exc_type, exc_val, exc_tb)
        
        # Close stdio context
        if self.stdio_context:
            await self.stdio_context.__aexit__(exc_type, exc_val, exc_tb)
        
        return False
    
    async def _build_agent(self, tools: dict):
        """Build the complete production-ready LangGraph workflow."""
        
        # Create wrapper functions that pass tools to nodes
        async def analyze_node(state: ResearchState):
            return await analyze_query_node(state, tools)
        
        async def executor_node(state: ResearchState):
            return await tool_executor_node(state, tools)
        
        async def synthesis_node(state: ResearchState):
            return await synthesize_with_claude_node(state, tools)
        
        async def quality_node(state: ResearchState):
            return await quality_check_node(state, tools)
        
        async def retry_node(state: ResearchState):
            return await retry_handler_node(state, tools)
        
        async def format_node(state: ResearchState):
            return await format_output_node(state, tools)
        
        # Build the graph
        logger.info("Building production LangGraph workflow...")
        workflow = StateGraph(ResearchState)
        
        # Add all nodes
        workflow.add_node("analyze_query", analyze_node)
        workflow.add_node("tool_executor", executor_node)
        workflow.add_node("synthesize_with_claude", synthesis_node)
        workflow.add_node("quality_check", quality_node)
        workflow.add_node("retry_handler", retry_node)
        workflow.add_node("format_output", format_node)
        
        # Build the workflow
        # Step 1: Analyze query and create execution plan
        workflow.add_edge(START, "analyze_query")
        
        # Step 2: Execute tools according to plan
        workflow.add_edge("analyze_query", "tool_executor")
        
        # Step 3: Synthesize results into coherent answer
        workflow.add_edge("tool_executor", "synthesize_with_claude")
        
        # Step 4: Check quality of synthesized answer
        workflow.add_edge("synthesize_with_claude", "quality_check")
        
        # Step 5: Quality-based routing
        workflow.add_conditional_edges(
            "quality_check",
            check_quality,
            {
                "pass": "format_output",
                "retry": "retry_handler",
                "fail": "format_output"  # Format anyway with warning
            }
        )
        
        # Step 6: Retry logic
        workflow.add_conditional_edges(
            "retry_handler",
            should_retry,
            {
                "retry": "analyze_query",  # Re-analyze with feedback
                "give_up": "format_output"
            }
        )
        
        # Step 7: Format output and end
        workflow.add_edge("format_output", END)
        
        # Compile the graph
        graph = workflow.compile()
        logger.info("Production LangGraph workflow compiled successfully")
        logger.info(f"Workflow: analyze → execute → synthesize → quality → (retry or format) → END")
        
        return graph


def create_research_agent():
    """
    Creates the research agent context manager.
    
    Returns:
        ResearchAgentContext: Context manager for the research agent
        
    Example:
        >>> async with create_research_agent() as agent:
        ...     result = await agent.ainvoke({
        ...         "query": "What is quantum computing?",
        ...         ...
        ...     })
    """
    return ResearchAgentContext()


# Module-level confirmation
logger.info("✅ Production LangGraph research agent module loaded")
