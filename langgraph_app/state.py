"""
State schema for the research agent.

Defines the data structure that flows through the LangGraph workflow.
"""

from typing import TypedDict, Annotated, Sequence, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ResearchState(TypedDict):
    """
    State for advanced research assistant with quality tracking.
    
    Attributes:
        messages: Conversation history with add_messages reducer
        query: Original user query
        task_type: Task classification (dice_action, research, general)
        selected_tools: List of tools selected by analyze_query_node
        workflow_plan: Execution plan created by analyze_query_node
        processing_steps: Log of processing steps for transparency
        question_type: Classification of question (factual, analytical, creative, technical)
        tools_used: List of tools that were executed
        workflow_steps: List of workflow steps executed
        search_results: Results from web search (if applicable)
        analysis: Deep analysis from specialized Claude
        quality_score: Quality rating of analysis (0-10)
        retry_count: Number of retry attempts
        final_answer: Synthesized final response
        error: Error message if something goes wrong
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    query: str
    task_type: Literal["dice_action", "research", "general"]
    selected_tools: list[str]
    workflow_plan: list[dict]
    processing_steps: list[str]
    question_type: Literal["factual", "analytical", "creative", "technical"]
    tools_used: list[str]
    workflow_steps: list[dict]
    search_results: str
    analysis: str
    quality_score: float
    retry_count: int
    final_answer: str
    error: str | None
