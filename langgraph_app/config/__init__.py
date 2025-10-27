"""
Configuration module for LangGraph application.

Contains task type definitions, workflow mappings, and agent settings.
"""

from .settings import AgentConfig, config, PROJECT_ROOT
from .task_mappings import (
    TaskType,
    WorkflowStep,
    TASK_PATTERNS,
    TASK_WORKFLOWS,
)

__all__ = [
    "AgentConfig",
    "config",
    "PROJECT_ROOT",
    "TaskType",
    "WorkflowStep",
    "TASK_PATTERNS",
    "TASK_WORKFLOWS",
]
