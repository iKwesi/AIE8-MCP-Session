"""
Research Agent Demo

Demonstrates the advanced multi-step research assistant with
conditional routing, quality checks, and retry logic.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from langgraph_app import create_research_agent
from langchain_core.messages import HumanMessage


async def run_research_query(query: str):
    """
    Run a single research query through the agent.
    
    Args:
        query: The research question to answer
    """
    print("\n" + "=" * 80)
    print(f"🔍 RESEARCH QUERY: {query}")
    print("=" * 80)
    
    # Create the research agent with proper context management
    print("\n📡 Connecting to MCP server and loading tools...")
    
    async with create_research_agent() as agent:
        # Prepare initial state
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "query": query,
            "task_type": "general",  # Will be set by analyze_query_node
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
        }
        
        print("🚀 Starting research workflow...\n")
        
        # Run the agent
        result = await agent.ainvoke(initial_state)
        
        # Display results
        print("\n" + "=" * 80)
        print("📊 WORKFLOW RESULTS")
        print("=" * 80)
        
        print(f"\n📌 Question Type: {result.get('question_type', 'unknown')}")
        print(f"⭐ Quality Score: {result.get('quality_score', 0):.1f}/10")
        print(f"🔄 Retry Count: {result.get('retry_count', 0)}")
        
        if result.get('error'):
            print(f"\n⚠️  Errors: {result['error']}")
        
        print("\n" + "-" * 80)
        print("💡 FINAL ANSWER")
        print("-" * 80)
        print(result.get('final_answer', 'No answer generated'))
        print("-" * 80)
    
    # MCP connection automatically closed by context manager
    print("\n🔌 MCP connection closed")


async def run_demo():
    """Run demo with multiple example queries."""
    
    print("\n" + "🤖" * 40)
    print("ADVANCED RESEARCH ASSISTANT DEMO")
    print("Activity #2: LangGraph + MCP Integration")
    print("🤖" * 40)
    
    # Example queries demonstrating different question types
    queries = [
        # Factual question (will use web_search)
        "What are the latest developments in quantum computing in 2025?",
        
        # Technical question (will use deep_analysis with explain profile)
        "How does a transformer neural network architecture work?",
        
        # Analytical question (will use deep_analysis with code_review profile)
        "What are the trade-offs between microservices and monolithic architecture?",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n\n{'#' * 80}")
        print(f"EXAMPLE {i}/{len(queries)}")
        print(f"{'#' * 80}")
        
        await run_research_query(query)
        
        if i < len(queries):
            print("\n⏳ Waiting 3 seconds before next query...")
            await asyncio.sleep(3)
    
    print("\n\n" + "=" * 80)
    print("✅ DEMO COMPLETED")
    print("=" * 80)
    print("\nThe research agent successfully demonstrated:")
    print("  ✅ Question type analysis")
    print("  ✅ Conditional routing (search vs direct analysis)")
    print("  ✅ Multi-step workflows")
    print("  ✅ Quality checks")
    print("  ✅ MCP tool integration")
    print("\n")


async def interactive_mode():
    """Interactive mode for custom queries."""
    
    print("\n" + "🤖" * 40)
    print("INTERACTIVE RESEARCH ASSISTANT")
    print("🤖" * 40)
    print("\nEnter your research questions (or 'quit' to exit)")
    print("-" * 80)
    
    while True:
        try:
            query = input("\n🔍 Your question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not query:
                print("⚠️  Please enter a question.")
                continue
            
            await run_research_query(query)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Research Agent Demo")
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        help="Run a single query"
    )
    
    args = parser.parse_args()
    
    if args.query:
        # Single query mode
        asyncio.run(run_research_query(args.query))
    elif args.interactive:
        # Interactive mode
        asyncio.run(interactive_mode())
    else:
        # Demo mode (default)
        asyncio.run(run_demo())
