"""Utility functions for MCP server."""
from typing import Dict, Any, Optional, List
from fastmcp import FastMCP

def register_prompts(mcp: FastMCP) -> None:
    """
    Register helpful prompts for the MCP server.
    
    Args:
        mcp: The FastMCP instance to register prompts with
    """
    # Help prompt
    @mcp.prompt("help")
    def help_prompt():
        """WeRead MCP API help documentation."""
        return """
        # WeRead MCP API
        
        This MCP server allows you to interact with your WeRead (微信读书) account.
        
        ## Available Tools
        
        - `authenticate(cookie: str)`: Test if your WeRead cookie is valid
        - `get_books(cookie?: str)`: Get a list of all books in your WeRead library
        - `get_book_info(book_id: str, cookie?: str)`: Get detailed information for a specific book
        - `get_book_bookmarks(book_id: str, cookie?: str)`: Get highlights/bookmarks for a specific book
        - `get_book_chapters(book_id: str, cookie?: str)`: Get chapter information for a specific book
        - `get_book_read_info(book_id: str, cookie?: str)`: Get reading progress and information for a specific book
        - `get_book_reviews(book_id: str, cookie?: str)`: Get reviews and notes for a specific book
        - `get_web_url(book_id: str)`: Get the WeRead web URL for a specific book
        - `format_book_highlights(book_id: str, max_highlights?: int, cookie?: str)`: Format book highlights into a markdown string
        - `search_books(query: str, cookie?: str)`: Search for books in your WeRead library by title or author
        
        ## Authentication
        
        Most tools require authentication with a WeRead cookie. There are two ways to provide this:
        
        1. Set the `WEREAD_COOKIE` environment variable in your `.env` file.
        2. Pass the cookie parameter to each tool call.
        
        ## Example Usage
        
        ```python
        # Get a list of books
        books = await client.call_tool("get_books", {"cookie": "your_weread_cookie_here"})
        
        # Get book details
        book_info = await client.call_tool("get_book_info", {"book_id": "book12345", "cookie": "your_weread_cookie_here"})
        
        # Get highlights for a book
        bookmarks = await client.call_tool("get_book_bookmarks", {"book_id": "book12345", "cookie": "your_weread_cookie_here"})
        ```
        """
    
    # Example prompt
    @mcp.prompt("examples")
    def examples_prompt():
        """Examples of using the WeRead MCP API."""
        return """
        # WeRead MCP API Examples
        
        Here are some example tasks you can perform with this MCP server:
        
        ## Get All Books
        
        ```python
        books = await client.call_tool("get_books", {"cookie": "your_weread_cookie_here"})
        print(f"Found {len(books.books)} books in your library")
        ```
        
        ## Get Book Details
        
        ```python
        book_info = await client.call_tool("get_book_info", {"book_id": "book12345", "cookie": "your_weread_cookie_here"})
        print(f"Title: {book_info.title}")
        print(f"Author: {book_info.author}")
        print(f"Rating: {book_info.rating}/5")
        ```
        
        ## Get Book Highlights
        
        ```python
        bookmarks = await client.call_tool("get_book_bookmarks", {"book_id": "book12345", "cookie": "your_weread_cookie_here"})
        for bookmark in bookmarks.bookmarks:
            print(f"- {bookmark.get('markText')}")
        ```
        
        ## Get Reading Progress
        
        ```python
        read_info = await client.call_tool("get_book_read_info", {"book_id": "book12345", "cookie": "your_weread_cookie_here"})
        print(f"Progress: {read_info.progress}%")
        print(f"Status: {read_info.status}")
        ```
        
        ## Get Web URL
        
        ```python
        url_info = await client.call_tool("get_web_url", {"book_id": "book12345"})
        print(f"WeRead URL: {url_info['url']}")
        ```
        """


def format_book_summary(book_data: Dict[str, Any]) -> str:
    """
    Format book data into a readable summary.
    
    Args:
        book_data: Book data dictionary
        
    Returns:
        Formatted book summary string
    """
    book = book_data.get("book", {})
    return (
        f"Title: {book.get('title', 'Unknown')}\n"
        f"Author: {book.get('author', 'Unknown')}\n"
        f"Publisher: {book.get('publisher', 'Unknown')}\n"
        f"ID: {book.get('bookId', 'Unknown')}\n"
    )


def format_highlights(bookmarks: List[Dict[str, Any]], 
                      max_highlights: Optional[int] = None) -> str:
    """
    Format bookmarks/highlights into a readable string.
    
    Args:
        bookmarks: List of bookmark dictionaries
        max_highlights: Maximum number of highlights to include
        
    Returns:
        Formatted highlights string
    """
    if not bookmarks:
        return "No highlights found."
    
    if max_highlights:
        bookmarks = bookmarks[:max_highlights]
    
    result = []
    for bm in bookmarks:
        text = bm.get("markText", "")
        chapter = bm.get("chapterTitle", "")
        result.append(f"\"{text}\" - {chapter}")
    
    return "\n".join(result) 