# tools/anthropic_tools.py
"""
Specialized Claude Tool - Meta-AI Implementation

This tool demonstrates Claude calling Claude for specialized tasks.
It's "meta-AI" - an AI assistant using another AI assistant as a tool.

Architecture:
- Declarative profile system (CLAUDE_PROFILES dict)
- Single responsibility: orchestrate calls to specialized Claude instances
- Self-registers with shared MCP instance
- Cached client for performance
"""

from core.mcp_instance import mcp
from utils.anthropic_client import get_anthropic_client


# Declarative profile map - keeps logic clean and DRY
# Each profile defines a specialized Claude persona with:
# - system: The system prompt that shapes Claude's behavior
# - description: Human-readable explanation of the profile's purpose
CLAUDE_PROFILES = {
    "code_review": {
        "system": (
            "You are a senior software engineer specializing in code "
            "security, performance, and maintainability. Identify "
            "vulnerabilities, inefficiencies, and best practice violations "
            "clearly and concisely. Focus on actionable feedback."
        ),
        "description": "Performs detailed code and security reviews with actionable feedback."
    },
    "summarize": {
        "system": (
            "You are a precise summarizer. Extract key insights, remove "
            "redundancy, and produce clear, short summaries. Focus on "
            "the most important information and maintain accuracy."
        ),
        "description": "Summarizes text accurately and briefly, preserving key insights."
    },
    "explain": {
        "system": (
            "You are an educator specializing in making complex topics simple. "
            "Explain concepts for beginners using analogies, progressive "
            "explanations, and clear examples. Avoid jargon unless necessary."
        ),
        "description": "Explains complex topics in simple, beginner-friendly terms."
    },
    "creative": {
        "system": (
            "You are a creative writer. Generate imaginative, engaging, "
            "and original ideas with vivid language. Think outside the box "
            "and surprise the user with creative perspectives."
        ),
        "description": "Creative writing and ideation with imaginative perspectives."
    },
    "general": {
        "system": (
            "You are a helpful, knowledgeable AI assistant. Provide clear, "
            "accurate, and useful responses. Be concise but thorough."
        ),
        "description": "General-purpose reasoning and assistance."
    },
}


@mcp.tool(name="ask_specialized_claude")
def ask_specialized_claude(
    prompt: str, 
    task_type: str = "general", 
    max_tokens: int = 1024
) -> str:
    """
    Call a specialized Claude model for targeted reasoning tasks.
    
    This is "meta-AI" - Claude in Cursor calling another Claude instance
    with specialized system prompts for specific tasks. Each task_type
    activates a different Claude persona optimized for that use case.
    
    Args:
        prompt: User input for Claude to process
        task_type: Specialization mode, one of:
            - code_review: Security and quality code analysis
            - summarize: Concise text summarization
            - explain: Educational explanations (ELI5 style)
            - creative: Creative writing and ideation
            - general: General-purpose assistance
        max_tokens: Response length cap (default 1024, max 4096)
    
    Returns:
        A formatted string response from the specialized Claude instance
        
    Examples:
        >>> ask_specialized_claude("Explain quantum computing", "explain")
        >>> ask_specialized_claude("Review this code: def foo()...", "code_review")
        >>> ask_specialized_claude("Summarize this article...", "summarize")
    
    Raises:
        ValueError: If task_type is not recognized
        Exception: If API call fails (network, auth, rate limit, etc.)
    """
    
    # Validate task_type
    if task_type not in CLAUDE_PROFILES:
        valid = ", ".join(CLAUDE_PROFILES.keys())
        raise ValueError(
            f"Invalid task_type '{task_type}'. Must be one of: {valid}"
        )
    
    # Validate max_tokens
    if not (1 <= max_tokens <= 4096):
        raise ValueError(
            f"max_tokens must be between 1 and 4096, got {max_tokens}"
        )
    
    # Get the profile for this task type
    profile = CLAUDE_PROFILES[task_type]
    
    # Get cached Anthropic client
    try:
        client = get_anthropic_client()
    except EnvironmentError as e:
        return f"❌ Configuration Error: {str(e)}"
    
    try:
        # Call Claude with specialized system prompt
        response = client.messages.create(
            model="claude-sonnet-4-20250514",  # Latest Claude model
            system=profile["system"],
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        
        # Extract response text
        text = response.content[0].text.strip() if response.content else "[No content returned]"
        
        # Format with header showing which mode was used
        header = f"🤖 Specialized Claude ({task_type.replace('_', ' ').title()} Mode)"
        separator = "─" * len(header)
        
        return f"{header}\n{separator}\n\n{text}"
    
    except Exception as e:
        # Provide helpful error messages
        error_msg = str(e)
        
        # Check for common error types
        if "rate_limit" in error_msg.lower():
            return (
                f"❌ Rate Limit Error: Too many requests to Claude API.\n"
                f"Please wait a moment and try again."
            )
        elif "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
            return (
                f"❌ Authentication Error: Invalid ANTHROPIC_API_KEY.\n"
                f"Please check your .env file and verify your API key."
            )
        elif "timeout" in error_msg.lower():
            return (
                f"❌ Timeout Error: Request to Claude API timed out.\n"
                f"Please try again."
            )
        else:
            return (
                f"❌ Error invoking Claude ({task_type}): {error_msg}\n\n"
                f"If this persists, check your API key and network connection."
            )


# Self-registration confirmation
# When this module is imported, this tool is automatically registered
# with the shared MCP instance from core.mcp_instance
print("✅ Anthropic tools registered (ask_specialized_claude)")