"""
Task type definitions and tool mappings.

Defines how different query types map to MCP tools with step-by-step workflows.
"""

from typing import Literal, TypedDict

# Task type definitions
TaskType = Literal["dice_action", "research", "general"]


class WorkflowStep(TypedDict):
    """Definition of a single workflow step."""
    step: int
    tool: str
    action: str
    task_type: str | None  # For ask_specialized_claude, None for other tools


# Pattern definitions for query classification
TASK_PATTERNS = {
    "dice_action": [
        r"\broll\b.*\bdice\b",
        r"\bdice\b.*\broll\b",
        r"\d+d\d+",  # Dice notation like 2d20, 3d6k2
    ],
    
    "research": [
        # Strong research indicators
        r"research|study|analyze|investigate|survey",
        r"latest|recent|current|today|news|update",  # Needs fresh data
        r"history of|background on|timeline of",
        r"compare|contrast|difference between|versus",
        r"comprehensive|detailed|in-depth",
        # Only use "what is" if combined with depth indicators
        r"what is.*\b(latest|current|comprehensive|detailed)",
        r"tell me about.*\b(latest|recent|news)",
        r"\b(2024|2025)\b",  # Year mentions
    ],
    
    "general": [
        # Simple questions that don't need research
        r"what is\b(?!.*(latest|current|recent))",  # "what is X" without depth
        r"define|definition",
        r"explain briefly|simple explanation",
        r"^(who|what|when|where|why|how)\s",  # Simple questions at start
    ],
}


# Workflow definitions - step-by-step execution plans
TASK_WORKFLOWS = {
    "dice_action": [
        {
            "step": 1,
            "tool": "roll_dice",
            "action": "Roll dice",
            "task_type": None  # roll_dice doesn't use task_type parameter
        }
    ],
    
    "research": [
        {
            "step": 1,
            "tool": "web_search",
            "action": "Research topic",
            "task_type": None  # web_search doesn't use task_type parameter
        },
        {
            "step": 2,
            "tool": "ask_specialized_claude",
            "action": "Summarize findings",
            "task_type": "summarize"  # Use summarize profile
        },
        {
            "step": 3,
            "tool": "ask_specialized_claude",
            "action": "Explain simply",
            "task_type": "explain"  # Use explain profile
        }
    ],
    
    "general": [
        {
            "step": 1,
            "tool": "ask_specialized_claude",
            "action": "Answer question",
            "task_type": "general"  # Use general profile
        }
    ]
}
