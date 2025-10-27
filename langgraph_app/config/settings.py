"""
Agent configuration settings.

Manages environment variables and runtime configuration.
"""

from pathlib import Path
from pydantic_settings import BaseSettings


# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


class AgentConfig(BaseSettings):
    """
    Configuration settings for the research agent.
    
    All settings can be overridden via environment variables
    with the AGENT_ prefix (e.g., AGENT_MODEL_NAME).
    """
    
    # LLM Configuration
    model_name: str = "openai:gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 2048
    
    # Agent Behavior
    max_iterations: int = 10
    quality_threshold: float = 7.0
    max_retries: int = 2
    
    # MCP Server Configuration
    mcp_server_command: str = "uv"
    mcp_server_args: list[str] = ["--directory", str(PROJECT_ROOT), "run", "server.py"]
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_prefix = "AGENT_"
        case_sensitive = False


# Global config instance
config = AgentConfig()
