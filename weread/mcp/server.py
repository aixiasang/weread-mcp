import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from weread.client import WeReadClient
from weread.models import (
    BookListResponse,
    BookInfoResponse,
    BookmarkResponse,
    ChapterResponse,
    ReadInfoResponse,
    ReviewResponse,
)
from weread.mcp.utils import register_prompts, format_book_summary, format_highlights

# Load environment variables
DEFAULT_COOKIE = os.getenv("WEREAD_COOKIE", "")

# Client cache - This is a simple in-memory cache, for production consider Redis or similar
client_cache: Dict[str, WeReadClient] = {}

# Create the FastMCP server
mcp = FastMCP("WeRead MCP API")

# Register helpful prompts
register_prompts(mcp)


# Helper function to get or create a WeRead client
def get_weread_client(cookie: str = None) -> WeReadClient:
    """
    Get or create a WeRead client.
    
    Args:
        cookie: Optional WeRead cookie string
        
    Returns:
        WeReadClient instance
        
    Raises:
        Exception: If authentication fails
    """
    cookie = cookie or DEFAULT_COOKIE
    
    if not cookie:
        raise Exception("WeRead cookie is required")

    # Use cached client if available
    if cookie in client_cache:
        return client_cache[cookie]
    
    try:
        client = WeReadClient(cookie)
        client_cache[cookie] = client
        return client
    except Exception as e:
        raise Exception(f"Failed to authenticate with WeRead: {str(e)}")


# Authentication tool
@mcp.tool()
def authenticate(cookie: str) -> Dict[str, bool]:
    """
    Test if your WeRead cookie is valid.
    
    Args:
        cookie: WeRead cookie string
        
    Returns:
        Dictionary with authentication status
    """
    try:
        get_weread_client(cookie)
        return {"authenticated": True}
    except Exception as e:
        return {"authenticated": False, "error": str(e)}


# Books tools
@mcp.tool()
def get_books(cookie: Optional[str] = None) -> BookListResponse:
    """
    Get a list of all books in your WeRead library.
    
    Args:
        cookie: Optional WeRead cookie string
        
    Returns:
        List of books
    """
    client = get_weread_client(cookie)
    books = client.get_notebooklist()
    
    if books is None:
        raise Exception("Failed to fetch books from WeRead")
    
    return BookListResponse(books=books)


@mcp.tool()
def get_book_info(book_id: str, cookie: Optional[str] = None) -> BookInfoResponse:
    """
    Get detailed information for a specific book.
    
    Args:
        book_id: Book ID
        cookie: Optional WeRead cookie string
        
    Returns:
        Book information
    """
    client = get_weread_client(cookie)
    
    # Get basic notebook info first
    books = client.get_notebooklist()
    if books is None:
        raise Exception("Failed to fetch books from WeRead")
    
    # Find the specific book
    book_data = None
    for book in books:
        if book.get("book", {}).get("bookId") == book_id:
            book_data = book.get("book", {})
            break
    
    if book_data is None:
        raise Exception(f"Book with ID {book_id} not found")
    
    # Get additional info
    isbn, rating = client.get_bookinfo(book_id)
    
    # Get bookmark and review counts
    bookmarks = client.get_bookmark_list(book_id) or []
    summary, reviews = client.get_review_list(book_id)
    
    # Extract categories if available
    categories = None
    if "categories" in book_data and book_data["categories"]:
        categories = [category["title"] for category in book_data["categories"]]
    
    return BookInfoResponse(
        id=book_id,
        title=book_data.get("title", ""),
        author=book_data.get("author", ""),
        cover=book_data.get("cover", "").replace("/s_", "/t7_"),
        isbn=isbn,
        rating=rating,
        categories=categories,
        bookmark_count=len(bookmarks),
        review_count=len(reviews) + len(summary)
    )


@mcp.tool()
def get_book_bookmarks(book_id: str, cookie: Optional[str] = None) -> BookmarkResponse:
    """
    Get bookmarks/highlights for a specific book.
    
    Args:
        book_id: Book ID
        cookie: Optional WeRead cookie string
        
    Returns:
        List of bookmarks
    """
    client = get_weread_client(cookie)
    bookmarks = client.get_bookmark_list(book_id)
    
    if bookmarks is None:
        bookmarks = []
    
    return BookmarkResponse(bookmarks=bookmarks)


@mcp.tool()
def get_book_chapters(book_id: str, cookie: Optional[str] = None) -> ChapterResponse:
    """
    Get chapter information for a specific book.
    
    Args:
        book_id: Book ID
        cookie: Optional WeRead cookie string
        
    Returns:
        Chapter information
    """
    client = get_weread_client(cookie)
    chapters = client.get_chapter_info(book_id)
    
    if chapters is None:
        chapters = {}
    
    return ChapterResponse(chapters=chapters)


@mcp.tool()
def get_book_read_info(book_id: str, cookie: Optional[str] = None) -> ReadInfoResponse:
    """
    Get reading information for a specific book.
    
    Args:
        book_id: Book ID
        cookie: Optional WeRead cookie string
        
    Returns:
        Reading information
    """
    client = get_weread_client(cookie)
    read_info = client.get_read_info(book_id)
    
    if read_info is None:
        return ReadInfoResponse()
    
    # Process reading info
    reading_time = read_info.get("readingTime", 0)
    progress = read_info.get("readingProgress", 0)
    status = "读完" if read_info.get("markedStatus", 0) == 4 else "在读"
    
    # Format finished date if available
    finished_date = None
    if "finishedDate" in read_info:
        finished_date = datetime.utcfromtimestamp(read_info.get("finishedDate")).strftime("%Y-%m-%d %H:%M:%S")
    
    return ReadInfoResponse(
        reading_time=reading_time,
        progress=progress,
        status=status,
        finished_date=finished_date
    )


@mcp.tool()
def get_book_reviews(book_id: str, cookie: Optional[str] = None) -> ReviewResponse:
    """
    Get reviews and notes for a specific book.
    
    Args:
        book_id: Book ID
        cookie: Optional WeRead cookie string
        
    Returns:
        Reviews and notes
    """
    client = get_weread_client(cookie)
    summary, reviews = client.get_review_list(book_id)
    
    return ReviewResponse(
        summary=summary,
        reviews=reviews
    )


@mcp.tool()
def get_web_url(book_id: str) -> Dict[str, str]:
    """
    Get the WeRead web URL for a specific book.
    
    Args:
        book_id: Book ID
        
    Returns:
        Web URL
    """
    web_id = WeReadClient.calculate_book_str_id(book_id)
    url = f"https://weread.qq.com/web/reader/{web_id}"
    
    return {"url": url}


@mcp.tool()
def format_book_highlights(book_id: str, max_highlights: Optional[int] = 10, cookie: Optional[str] = None) -> str:
    """
    Get and format highlights for a book into a nicely formatted string.
    
    Args:
        book_id: Book ID
        max_highlights: Maximum number of highlights to include (default: 10)
        cookie: Optional WeRead cookie string
        
    Returns:
        Formatted highlights string
    """
    client = get_weread_client(cookie)
    
    # Get book details first to include title
    book_info = None
    books = client.get_notebooklist()
    if books:
        for book in books:
            if book.get("book", {}).get("bookId") == book_id:
                book_info = book
                break
    
    # Get bookmarks
    bookmarks = client.get_bookmark_list(book_id) or []
    
    # Format the output
    if book_info:
        book_details = book_info.get("book", {})
        title = book_details.get("title", "Unknown")
        author = book_details.get("author", "Unknown")
        result = f"# Highlights from {title} by {author}\n\n"
    else:
        result = f"# Highlights for book ID: {book_id}\n\n"
    
    # Add the formatted highlights
    result += format_highlights(bookmarks, max_highlights)
    
    return result


@mcp.tool()
def search_books(query: str, cookie: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search for books in your WeRead library by title or author.
    
    Args:
        query: Search query string
        cookie: Optional WeRead cookie string
        
    Returns:
        List of matching books
    """
    query = query.lower()
    client = get_weread_client(cookie)
    books = client.get_notebooklist()
    
    if not books:
        return []
    
    # Filter books based on query
    results = []
    for book_data in books:
        book = book_data.get("book", {})
        title = book.get("title", "").lower()
        author = book.get("author", "").lower()
        
        if query in title or query in author:
            results.append({
                "id": book.get("bookId", ""),
                "title": book.get("title", ""),
                "author": book.get("author", ""),
                "cover": book.get("cover", "").replace("/s_", "/t7_")
            })
    
    return results


# Set up a resource for health check
@mcp.resource("data://health")
def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()} 