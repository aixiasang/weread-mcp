#!/usr/bin/env python
"""
WeRead API Server (FastAPI compatibility layer)

This server provides a traditional REST API interface alongside the MCP interface.
It uses FastAPI to expose the same functionality as the MCP server.
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the FastAPI app
from weread.api.app import app

if __name__ == "__main__":
    # Use environment variables for host and port if available
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    # Run the FastAPI server
    uvicorn.run("weread.api.app:app", host=host, port=port, reload=True) 