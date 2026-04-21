from blender_mcp.server import main as server_main
import sys

def main():
    """Entry point for the blender-mcp package.
    
    Runs the MCP server that connects Blender to AI assistants.
    
    Make sure Blender is running with the blender-mcp addon enabled
    before starting this server, otherwise the connection will fail.
    
    Steps to get started:
      1. Open Blender and enable the blender-mcp addon in Preferences > Add-ons
      2. In the addon panel, click 'Start MCP Server'
      3. Then run this script to connect your AI assistant
    """
    # Print a startup message so it's clear the server is launching
    print("Starting Blender MCP server...", file=sys.stderr)
    print("Tip: Ensure the Blender addon is active before connecting.", file=sys.stderr)
    server_main()

if __name__ == "__main__":
    main()
