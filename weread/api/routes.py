import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from weread.client import WeReadClient
from weread.models import (
    WeReadAuthConfig,
    BookListResponse,
    BookInfoResponse,
    BookmarkResponse,
    ChapterResponse,
    ReadInfoResponse,
    ReviewResponse,
)

# Create a shared helper function
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
    # Load default cookie from environment variables
    DEFAULT_COOKIE = os.getenv("WEREAD_COOKIE", "")
    
    cookie = cookie or DEFAULT_COOKIE
    
    if not cookie:
        raise Exception("WeRead cookie is required")

    # We're using a simple implementation without caching for clarity
    # In production, consider using a proper cache
    try:
        client = WeReadClient(cookie)
        return client
    except Exception as e:
        raise Exception(f"Failed to authenticate with WeRead: {str(e)}")

# Create router
router = APIRouter()

@router.post("/auth", response_model=Dict[str, bool])
async def authenticate(config: WeReadAuthConfig):
    """
    Authenticate with WeRead using the provided cookie.
    
    Args:
        config: WeRead authentication configuration
        
    Returns:
        Dictionary with authentication status
    """
    try:
        get_weread_client(config.cookie)
        return {"authenticated": True}
    except Exception as e:
        return JSONResponse(status_code=401, content={"authenticated": False, "error": str(e)})


@router.post("/books", response_model=BookListResponse)
async def get_books(config: Optional[WeReadAuthConfig] = None):
    """
    Get the list of books from WeRead.
    
    Args:
        config: Optional WeRead authentication configuration
        
    Returns:
        List of books
    """
    try:
        client = get_weread_client(config.cookie if config else None)
        books = client.get_notebooklist()
        
        if books is None:
            raise HTTPException(status_code=500, detail="Failed to fetch books from WeRead")
        
        return BookListResponse(books=books)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/books/{book_id}", response_model=BookInfoResponse)
async def get_book_info(book_id: str, config: Optional[WeReadAuthConfig] = None):
    """
    Get detailed information for a specific book.
    
    Args:
        book_id: Book ID
        config: Optional WeRead authentication configuration
        
    Returns:
        Book information
    """
    try:
        client = get_weread_client(config.cookie if config else None)
        
        # Get basic notebook info first
        books = client.get_notebooklist()
        if books is None:
            raise HTTPException(status_code=500, detail="Failed to fetch books from WeRead")
        
        # Find the specific book
        book_data = None
        for book in books:
            if book.get("book", {}).get("bookId") == book_id:
                book_data = book.get("book", {})
                break
        
        if book_data is None:
            raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
        
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/books/{book_id}/bookmarks", response_model=BookmarkResponse)
async def get_book_bookmarks(book_id: str, config: Optional[WeReadAuthConfig] = None):
    """
    Get bookmarks/highlights for a specific book.
    
    Args:
        book_id: Book ID
        config: Optional WeRead authentication configuration
        
    Returns:
        List of bookmarks
    """
    try:
        client = get_weread_client(config.cookie if config else None)
        bookmarks = client.get_bookmark_list(book_id)
        
        if bookmarks is None:
            bookmarks = []
        
        return BookmarkResponse(bookmarks=bookmarks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/books/{book_id}/chapters", response_model=ChapterResponse)
async def get_book_chapters(book_id: str, config: Optional[WeReadAuthConfig] = None):
    """
    Get chapter information for a specific book.
    
    Args:
        book_id: Book ID
        config: Optional WeRead authentication configuration
        
    Returns:
        Chapter information
    """
    try:
        client = get_weread_client(config.cookie if config else None)
        chapters = client.get_chapter_info(book_id)
        
        if chapters is None:
            chapters = {}
        
        return ChapterResponse(chapters=chapters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/books/{book_id}/readinfo", response_model=ReadInfoResponse)
async def get_book_read_info(book_id: str, config: Optional[WeReadAuthConfig] = None):
    """
    Get reading information for a specific book.
    
    Args:
        book_id: Book ID
        config: Optional WeRead authentication configuration
        
    Returns:
        Reading information
    """
    try:
        client = get_weread_client(config.cookie if config else None)
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/books/{book_id}/reviews", response_model=ReviewResponse)
async def get_book_reviews(book_id: str, config: Optional[WeReadAuthConfig] = None):
    """
    Get reviews and notes for a specific book.
    
    Args:
        book_id: Book ID
        config: Optional WeRead authentication configuration
        
    Returns:
        Reviews and notes
    """
    try:
        client = get_weread_client(config.cookie if config else None)
        summary, reviews = client.get_review_list(book_id)
        
        return ReviewResponse(
            summary=summary,
            reviews=reviews
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/web_url/{book_id}", response_model=Dict[str, str])
async def get_web_url(book_id: str, config: Optional[WeReadAuthConfig] = None):
    """
    Get the WeRead web URL for a specific book.
    
    Args:
        book_id: Book ID
        config: Optional WeRead authentication configuration
        
    Returns:
        Web URL
    """
    # We don't need to validate the cookie for this operation
    # but we'll accept it for API consistency
    try:
        web_id = WeReadClient.calculate_book_str_id(book_id)
        url = f"https://weread.qq.com/web/reader/{web_id}"
        
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 