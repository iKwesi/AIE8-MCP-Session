"""
LangGraph Workflow Visualization

Generates a PNG diagram of the Adaptive MCP Assistant workflow.
"""

import asyncio
from langgraph_app import create_research_agent


async def generate_graph_visualization():
    """
    Generate PNG visualization of the LangGraph workflow.
    
    Saves the diagram to langgraph_app/workflow_diagram.png
    """
    print("🎨 Generating LangGraph workflow visualization...")
    
    try:
        # Create the agent to get the compiled graph
        async with create_research_agent() as agent:
            print("✅ Agent created successfully")
            
            # Generate Mermaid PNG
            try:
                png_data = agent.get_graph().draw_mermaid_png()
                
                # Save to file
                output_path = "langgraph_app/workflow_diagram.png"
                with open(output_path, "wb") as f:
                    f.write(png_data)
                
                print(f"✅ Graph visualization saved to: {output_path}")
                print("\nYou can now:")
                print("  1. Open the PNG file to view the diagram")
                print("  2. Add it to your README")
                print("  3. Use it in presentations")
                
            except Exception as e:
                print(f"⚠️  PNG generation failed: {str(e)}")
                print("Note: PNG generation requires graphviz to be installed")
                print("Install with: brew install graphviz")
                
                # Fallback: Generate Mermaid text
                print("\n📝 Generating Mermaid diagram instead...")
                mermaid = agent.get_graph().draw_mermaid()
                
                output_path = "langgraph_app/workflow_diagram.mmd"
                with open(output_path, "w") as f:
                    f.write(mermaid)
                
                print(f"✅ Mermaid diagram saved to: {output_path}")
                print("You can paste this into GitHub README or mermaid.live")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(generate_graph_visualization())
