# test_server.py
"""
MCP Server Test Suite

Tests the MCP server by connecting as a client and calling tools.
This simulates how Cursor/Claude will interact with your server.
"""

from fastmcp import Client
import asyncio


async def test_anthropic_tool():
    """Test the specialized Claude tool"""
    print("\n" + "=" * 60)
    print("Testing: ask_specialized_claude")
    print("=" * 60)
    
    async with Client("server.py") as client:
        # List all available tools
        tools = await client.list_tools()
        # print(f"\n✅ Available tools: {[t['name'] for t in tools]}\n")
        print(f"\n✅ Available tools: {[t.name for t in tools]}\n")
        
        # Test 1: Explain mode
        print("📝 Test 1: Explain quantum computing simply")
        print("-" * 60)
        result = await client.call_tool(
            "ask_specialized_claude",
            {
                "prompt": "Explain quantum computing like I'm 12 years old",
                "task_type": "explain"
            }
        )
        print(result)
        
        # Test 2: Code review mode
        print("\n\n📝 Test 2: Review code for security issues")
        print("-" * 60)
        code = """
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    return db.execute(query)
"""
        result = await client.call_tool(
            "ask_specialized_claude",
            {
                "prompt": f"Review this code for security issues:\n\n{code}",
                "task_type": "code_review"
            }
        )
        print(result)
        
        # Test 3: Summarize mode
        print("\n\n📝 Test 3: Summarize text")
        print("-" * 60)
        text = """
The Model Context Protocol (MCP) is an open protocol that standardizes 
how applications provide context to Large Language Models (LLMs). MCP 
enables developers to build secure, two-way connections between their 
data sources and AI-powered tools. It's designed to be universal, 
allowing seamless integration across different AI platforms.
"""
        result = await client.call_tool(
            "ask_specialized_claude",
            {
                "prompt": f"Summarize this in one sentence:\n\n{text}",
                "task_type": "summarize"
            }
        )
        print(result)


async def test_legacy_tools():
    """Test the original web_search and roll_dice tools"""
    print("\n\n" + "=" * 60)
    print("Testing: Legacy Tools (web_search, roll_dice)")
    print("=" * 60)
    
    async with Client("server.py") as client:
        # Test web_search
        print("\n📝 Test: Web Search")
        print("-" * 60)
        result = await client.call_tool("web_search", {"query": "What is MCP protocol?"})
        content = str(result.content[0].text) if hasattr(result, 'content') else str(result)
        print(content[:500] + "..." if len(content) > 500 else content)
        
        # Test roll_dice
        print("\n\n📝 Test: Roll Dice")
        print("-" * 60)
        result = await client.call_tool(
            "roll_dice",
            {"notation": "2d20k1", "num_rolls": 3}
        )
        print(result)


async def main():
    """Run all tests"""
    print("\n" + "🧪" * 30)
    print("MCP SERVER TEST SUITE")
    print("🧪" * 30)
    
    try:
        # Test main tool (Anthropic)
        await test_anthropic_tool()
        
        # Test legacy tools
        await test_legacy_tools()
        
        print("\n\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n\n❌ TEST FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())