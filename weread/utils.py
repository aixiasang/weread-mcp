from typing import Dict, List, Any, Optional, Union


def get_heading(level: int, content: str) -> Dict[str, Any]:
    """
    Create a heading block for Notion.
    
    Args:
        level: Heading level (1-3)
        content: The text content of the heading
        
    Returns:
        Dict containing the heading block structure
    """
    if level == 1:
        heading = "heading_1"
    elif level == 2:
        heading = "heading_2"
    else:
        heading = "heading_3"
    
    return {
        "type": heading,
        heading: {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": content,
                    },
                }
            ],
            "color": "default",
            "is_toggleable": False,
        },
    }


def get_table_of_contents() -> Dict[str, Any]:
    """Get a table of contents block for Notion."""
    return {"type": "table_of_contents", "table_of_contents": {"color": "default"}}


def get_title(content: str) -> Dict[str, Any]:
    """Create a title property for Notion."""
    return {"title": [{"type": "text", "text": {"content": content}}]}


def get_rich_text(content: str) -> Dict[str, Any]:
    """Create a rich text property for Notion."""
    return {"rich_text": [{"type": "text", "text": {"content": content}}]}


def get_url(url: str) -> Dict[str, Any]:
    """Create a URL property for Notion."""
    return {"url": url}


def get_file(url: str) -> Dict[str, Any]:
    """Create a file property for Notion using an external URL."""
    return {"files": [{"type": "external", "name": "Cover", "external": {"url": url}}]}


def get_multi_select(names: List[str]) -> Dict[str, Any]:
    """Create a multi-select property for Notion."""
    return {"multi_select": [{"name": name} for name in names]}


def get_date(start: str) -> Dict[str, Any]:
    """Create a date property for Notion."""
    return {
        "date": {
            "start": start,
            "time_zone": "Asia/Shanghai",
        }
    }


def get_icon(url: str) -> Dict[str, Any]:
    """Create an icon for Notion pages."""
    return {"type": "external", "external": {"url": url}}


def get_select(name: str) -> Dict[str, Any]:
    """Create a select property for Notion."""
    return {"select": {"name": name}}


def get_number(number: Union[int, float]) -> Dict[str, Any]:
    """Create a number property for Notion."""
    return {"number": number}


def get_quote(content: str) -> Dict[str, Any]:
    """Create a quote block for Notion."""
    return {
        "type": "quote",
        "quote": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": content},
                }
            ],
            "color": "default",
        },
    }


def get_callout(content: str, style: Optional[int] = None, 
                colorStyle: Optional[int] = None, 
                reviewId: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a callout block for Notion.
    
    Args:
        content: The text content of the callout
        style: Highlight style (0=straight line, 1=background, 2=wavy line)
        colorStyle: Color style (1=red, 2=purple, 3=blue, 4=green, 5=yellow)
        reviewId: ID for notes/reviews
        
    Returns:
        Dict containing the callout block structure
    """
    # Select emoji based on highlight style
    emoji = "〰️"  # Default wavy line
    if style == 0:
        emoji = "💡"  # Straight line
    elif style == 1:
        emoji = "⭐"  # Background
    
    # If reviewId is not None, it's a note
    if reviewId is not None:
        emoji = "✍️"
    
    # Select color based on colorStyle
    color = "default"
    if colorStyle == 1:
        color = "red"
    elif colorStyle == 2:
        color = "purple"
    elif colorStyle == 3:
        color = "blue"
    elif colorStyle == 4:
        color = "green"
    elif colorStyle == 5:
        color = "yellow"
    
    return {
        "type": "callout",
        "callout": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": content,
                    },
                }
            ],
            "icon": {"emoji": emoji},
            "color": color,
        },
    } 