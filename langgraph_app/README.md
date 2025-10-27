# Advanced Research Assistant - Activity #2

A sophisticated multi-step research agent built with LangGraph that integrates with the MCP server from Activity #1.

## 🎯 Features

✅ **Question Type Analysis** - Automatically classifies questions as factual, analytical, creative, or technical  
✅ **Conditional Routing** - Routes to appropriate workflow based on question type  
✅ **Multi-Step Workflows** - Coordinates multiple MCP tools in sequence  
✅ **Quality Checks** - Validates analysis quality before proceeding  
✅ **Retry Logic** - Automatically retries low-quality responses  
✅ **MCP Integration** - Uses tools from Activity #1 (web_search, ask_specialized_claude)  

## 📁 Architecture

```
langgraph_app/
├── __init__.py           # Package exports
├── state.py              # State schema (ResearchState)
├── config.py             # Configuration settings
├── agent.py              # Main graph definition
│
├── nodes/                # Workflow nodes
│   ├── analyze.py        # Question classification
│   ├── search.py         # Web search
│   ├── deep_analysis.py  # Deep analysis with specialized Claude
│   ├── quality_check.py  # Quality validation
│   ├── retry.py          # Retry handling
│   └── synthesize.py     # Final answer synthesis
│
└── routing/              # Conditional routing logic
    ├── question_router.py  # Route by question type
    ├── quality_router.py   # Route by quality score
    └── retry_router.py     # Route by retry count
```

## 🔄 Workflow

```
START
  ↓
analyze_question (classify question type)
  ↓
  ├─→ factual? → web_search → deep_analysis
  ├─→ analytical/technical? → deep_analysis
  └─→ creative? → synthesize
       ↓
quality_check (rate 0-10)
  ↓
  ├─→ score ≥ 7.0? → synthesize → END
  ├─→ score < 7.0 & retries < 2? → retry_handler → deep_analysis
  └─→ score < 7.0 & retries ≥ 2? → synthesize → END
```

## 🚀 Usage

### Basic Usage

```python
from langgraph_app import create_research_agent
from langchain_core.messages import HumanMessage

# Create agent
agent, session = await create_research_agent()

# Run query
result = await agent.ainvoke({
    "messages": [HumanMessage(content="What is quantum computing?")],
    "query": "What is quantum computing?",
    "question_type": "factual",
    "search_results": "",
    "analysis": "",
    "quality_score": 0.0,
    "retry_count": 0,
    "final_answer": "",
    "error": None
})

# Get answer
print(result['final_answer'])

# Clean up
await session.__aexit__(None, None, None)
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
- Each router has ONE decision to make
- Each file has ONE clear purpose

### Open/Closed Principle (OCP)
- Easy to add new nodes without modifying existing code
- Easy to add new routing logic
- Extensible through composition

### DRY (Don't Repeat Yourself)
- Shared state schema
- Reusable routing functions
- Common tool access pattern

### KISS (Keep It Simple, Stupid)
- Small, focused files (20-50 lines each)
- Clear naming conventions
- Minimal abstractions

## 🧪 Testing

```python
# Test individual nodes
from langgraph_app.nodes import analyze_question_node

state = {"query": "What is AI?"}
tools = {"ask_specialized_claude": mock_tool}
result = await analyze_question_node(state, tools)
assert result["question_type"] in ["factual", "analytical", "creative", "technical"]

# Test routing logic
from langgraph_app.routing import route_by_question_type

state = {"question_type": "factual"}
assert route_by_question_type(state) == "needs_search"
```

## 📊 MCP Tools Used

### From Activity #1:

1. **web_search** (Tavily API)
   - Used by: `nodes/search.py`
   - Purpose: Gather current web information

2. **ask_specialized_claude** (Anthropic API)
   - Used by: `nodes/analyze.py`, `nodes/deep_analysis.py`, `nodes/quality_check.py`, `nodes/synthesize.py`
   - Profiles: general, summarize, code_review, explain, creative

3. **roll_dice** (D&D dice roller)
   - Available but not used in research workflow
   - Could be added for fun queries

## 🎓 Learning Outcomes

This implementation demonstrates:

✅ **LangGraph Fundamentals**
- StateGraph construction
- Conditional edges
- Node composition

✅ **MCP Integration**
- Connecting to MCP servers
- Loading and using MCP tools
- Tool orchestration

✅ **Production Patterns**
- Error handling
- Retry logic
- Quality validation
- Logging and observability

✅ **Software Engineering**
- Modular architecture
- Design principles (SOLID)
- Clean code practices

## 🔗 Related

- **Activity #1**: MCP Server (`server.py`, `tools/`, `core/`)
- **MCP Docs**: https://modelcontextprotocol.io
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph
- **LangChain MCP Adapters**: https://github.com/langchain-ai/langchain-mcp-adapters

## 📝 License

Same as parent project.
