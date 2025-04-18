#!/usr/bin/env python
"""
WeRead MCP API Server

This is the main entry point for the WeRead MCP API server.
It uses FastMCP to provide tools for interacting with WeRead (微信读书) data.
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Import the MCP server
from weread.mcp.server import mcp

if __name__ == "__main__":
    print("Starting WeRead MCP server...")
    mcp.run()
    print("Server stopped.") 