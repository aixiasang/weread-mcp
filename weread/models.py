from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union


class WeReadAuthConfig(BaseModel):
    """WeRead authentication configuration."""
    cookie: str = Field(..., description="WeRead cookie string")


class BookListResponse(BaseModel):
    """Response model for the book list endpoint."""
    books: List[Dict[str, Any]] = Field(default_factory=list, description="List of books")


class BookInfoResponse(BaseModel):
    """Response model for the book info endpoint."""
    id: str = Field(..., description="Book ID")
    title: str = Field(..., description="Book title")
    author: str = Field(..., description="Book author")
    cover: str = Field(..., description="Cover image URL")
    isbn: str = Field("", description="ISBN")
    rating: float = Field(0, description="Book rating")
    categories: Optional[List[str]] = Field(None, description="Book categories")
    bookmark_count: int = Field(0, description="Number of bookmarks/highlights")
    review_count: int = Field(0, description="Number of reviews/notes")


class BookmarkResponse(BaseModel):
    """Response model for the bookmark endpoint."""
    bookmarks: List[Dict[str, Any]] = Field(default_factory=list, description="List of bookmarks/highlights")


class ChapterResponse(BaseModel):
    """Response model for the chapter info endpoint."""
    chapters: Dict[str, Any] = Field(default_factory=dict, description="Chapter information")


class ReadInfoResponse(BaseModel):
    """Response model for the reading info endpoint."""
    reading_time: int = Field(0, description="Reading time in seconds")
    progress: int = Field(0, description="Reading progress (0-100)")
    status: str = Field("", description="Reading status")
    finished_date: Optional[str] = Field(None, description="Date when book was finished")


class ReviewResponse(BaseModel):
    """Response model for the review list endpoint."""
    summary: List[Dict[str, Any]] = Field(default_factory=list, description="Summary reviews")
    reviews: List[Dict[str, Any]] = Field(default_factory=list, description="Normal reviews/notes") 