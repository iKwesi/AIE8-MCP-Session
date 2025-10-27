# Adaptive MCP Assistant - Activity #2

A production-ready multi-step agent with intelligent tool selection, quality validation, and MCP integration.

## 🎯 Features

✅ **Intelligent Tool Selection** - Pattern-based classification with sophisticated regex (negative lookahead)  
✅ **Multi-Step Workflows** - Declarative workflow configuration for each task type  
✅ **Quality Validation** - Validates analysis quality before proceeding (skips for dice_action)  
✅ **Retry Logic** - Automatically retries low-quality responses with feedback  
✅ **Content Synthesis** - Uses Claude to create coherent answers from tool results  
✅ **Professional Formatting** - Formatted output with metadata and processing steps  
✅ **Detailed Logging** - Shows which tools are called with parameters and results  
✅ **Dynamic Adaptation** - Adds web search to general queries when current info is needed  

## 📁 Architecture

```
langgraph_app/
├── config/                   # Configuration module
│   ├── __init__.py           # Clean exports
│   ├── settings.py           # AgentConfig, config, PROJECT_ROOT
│   └── task_mappings.py      # Task patterns & workflows
│
├── utils/                    # Utility functions
│   ├── __init__.py
│   ├── query_classifier.py   # Pattern matching, should_use_web_search
│   └── tool_logger.py        # Detailed logging utilities
│
├── nodes/                    # Workflow nodes (6 nodes)
│   ├── __init__.py
│   ├── analyze_query.py      # Query analysis & planning
│   ├── tool_executor.py      # Intelligent tool execution
│   ├── synthesize_with_claude.py  # Content synthesis
│   ├── quality_check.py      # Quality validation
│   ├── retry.py              # Retry handling
│   └── format_output.py      # Output formatting
│
├── routing/                  # Conditional routing logic
│   ├── __init__.py
│   ├── quality_router.py     # Route by quality score
│   └── retry_router.py       # Route by retry count
│
├── state.py                  # ResearchState schema
├── agent.py                  # Production workflow builder
└── README.md                 # This file
```

## 🔄 Complete Workflow

```
START
  ↓
1. analyze_query_node
   - Classifies query (dice_action, research, general)
   - Selects tools based on task_mappings
   - Checks should_use_web_search() for dynamic adaptation
   - Creates execution plan
  ↓
2. tool_executor_node
   - Executes workflow steps from plan
   - Logs each tool call with parameters
   - Returns results
  ↓
3. synthesize_with_claude_node
   - Creates coherent answer from tool results
   - Skips for dice_action (results are final)
   - Uses creative mode for research
  ↓
4. quality_check_node
   - Validates answer quality (0-10)
   - Skips for dice_action (auto-pass 10.0)
  ↓
(conditional routing)
  ├─→ pass? → format_output_node → END
  └─→ retry? → retry_handler_node → analyze_query_node (re-analyze)
  ↓
5. format_output_node
   - Formats with headers and metadata
   - Includes processing steps
   - Shows workflow execution details
  ↓
END
```

## 🎨 Task Types & Workflows

### dice_action
**Patterns:**
- `roll.*dice`, `dice.*roll`, `\d+d\d+`

**Workflow:**
```
Step 1: roll_dice → Returns actual dice rolls
```

**Example:** "roll a dice 5 times" → `ROLLS: 4, 3, 3, 1, 1`

### research
**Patterns:**
- `research|study|analyze|investigate`
- `latest|recent|current|news|update`
- `what is.*(latest|current|comprehensive|detailed)` (depth indicators)
- `compare|contrast|difference between`

**Workflow:**
```
Step 1: web_search → Search for current information
Step 2: ask_specialized_claude(summarize) → Summarize findings
Step 3: ask_specialized_claude(explain) → Explain simply
```

**Example:** "What is the latest AI news?" → Web search + Summary + Explanation

### general
**Patterns:**
- `what is\b(?!.*(latest|current|recent))` (negative lookahead!)
- `define|definition`
- `^(who|what|when|where|why|how)\s`

**Workflow:**
```
Step 1: ask_specialized_claude(general) → Direct answer
```

**Dynamic:** Adds web_search if `should_use_web_search()` detects current info keywords

**Example:** "What is MCP?" → Just Claude (no web search)

## 🚀 Usage

### Basic Usage

```python
from langgraph_app import create_research_agent
from langchain_core.messages import HumanMessage

# Create agent with context manager
async with create_research_agent() as agent:
    result = await agent.ainvoke({
        "query": "What is quantum computing?",
        "messages": [HumanMessage(content="What is quantum computing?")],
        "task_type": "general",
        "selected_tools": [],
        "workflow_plan": [],
        "processing_steps": [],
        "question_type": "factual",
        "tools_used": [],
        "workflow_steps": [],
        "search_results": "",
        "analysis": "",
        "quality_score": 0.0,
        "retry_count": 0,
        "final_answer": "",
        "error": None
    })
    
    # Get formatted answer
    print(result['final_answer'])

# MCP connection automatically closed
```

### Run Demo

```bash
# Run demo with example queries
uv run python examples/research_demo.py

# Run single query
uv run python examples/research_demo.py -q "What is AI?"

# Interactive mode
uv run python examples/research_demo.py -i
```

## ⚙️ Configuration

Configure via environment variables with `AGENT_` prefix:

```bash
# .env
AGENT_MODEL_NAME=openai:gpt-4o
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=2048
AGENT_QUALITY_THRESHOLD=7.0
AGENT_MAX_RETRIES=2
```

Or in code:

```python
from langgraph_app.config import config

config.quality_threshold = 8.0
config.max_retries = 3
```

## 🔧 Design Principles

### Single Responsibility Principle (SRP)
- Each node has ONE job
- Each file has ONE clear purpose
- Separation of analysis, execution, synthesis, validation, formatting

### Open/Closed Principle (OCP)
- Easy to add new task types (just update config/task_mappings.py)
- Easy to add new workflow steps
- Extensible through configuration

### DRY (Don't Repeat Yourself)
- Shared state schema
- Reusable routing functions
- Centralized logging utilities
- Declarative workflow configuration

### KISS (Keep It Simple, Stupid)
- Small, focused files (20-80 lines each)
- Clear naming conventions
- Configuration over code

## 🧪 Testing

```python
# Test query classification
from langgraph_app.utils import classify_query

assert classify_query("roll a dice") == "dice_action"
assert classify_query("latest AI news") == "research"
assert classify_query("What is Python?") == "general"

# Test should_use_web_search
from langgraph_app.utils import should_use_web_search

assert should_use_web_search("latest news") == True
assert should_use_web_search("What is Python?") == False

# Test routing logic
from langgraph_app.routing import check_quality

state = {"quality_score": 8.0, "retry_count": 0}
assert check_quality(state) == "pass"
```

## 📊 MCP Tools Used

### From Activity #1:

1. **web_search** (Tavily API)
   - Used by: research workflow (step 1)
   - Purpose: Gather current web information
   - Logged with query parameters

2. **ask_specialized_claude** (Anthropic API)
   - Used by: All workflows with different profiles
   - Profiles: general, summarize, explain, creative
   - Logged with task_type and action

3. **roll_dice** (D&D dice roller)
   - Used by: dice_action workflow
   - Purpose: Generate random dice rolls
   - Logged with notation and num_rolls

## 🎓 Learning Outcomes

This implementation demonstrates:

✅ **LangGraph Fundamentals**
- StateGraph construction
- Conditional edges
- Multi-node workflows

✅ **MCP Integration**
- Connecting to MCP servers
- Loading and using MCP tools
- Tool orchestration with logging

✅ **Production Patterns**
- Sophisticated pattern matching (negative lookahead)
- Error handling and retry logic
- Quality validation
- Detailed observability

✅ **Software Engineering**
- Modular architecture (config/, nodes/, utils/, routing/)
- Design principles (SOLID)
- Declarative configuration
- Clean code practices

## 🚀 Advanced Features

### Sophisticated Pattern Matching
```python
# Negative lookahead for precise classification
r"what is\b(?!.*(latest|current|recent))"  # Matches "what is X" but not "what is the latest X"

# Conditional depth matching
r"what is.*\b(latest|current|comprehensive|detailed)"  # Only research if depth indicators present
```

### Dynamic Web Search
```python
# Automatically adds web search to general queries when needed
if task_type == "general" and should_use_web_search(query):
    # Prepends web_search step to workflow
```

### Tool Name Clarity
```python
# Shows task_type in tool names
Tools: web_search, ask_specialized_claude(summarize), ask_specialized_claude(explain)
```

## 📈 Example Outputs

### Dice Action
```
Query: "roll a dice 5 times"
Task Type: DICE_ACTION
Tools: roll_dice
Result: Roll 1: ROLLS: 4 -> RETURNS: 4
        Roll 2: ROLLS: 3 -> RETURNS: 3
        ...
```

### Research
```
Query: "What is the latest AI news?"
Task Type: RESEARCH
Tools: web_search, ask_specialized_claude(summarize), ask_specialized_claude(explain)
Result: [Comprehensive answer with current information]
```

### General
```
Query: "What is MCP?"
Task Type: GENERAL
Tools: ask_specialized_claude(general)
Result: [Direct answer without web search]
```

## 🔗 Related

- **Activity #1**: MCP Server (`server.py`, `tools/`, `core/`)
- **MCP Docs**: https://modelcontextprotocol.io
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph
- **LangChain MCP Adapters**: https://github.com/langchain-ai/langchain-mcp-adapters
