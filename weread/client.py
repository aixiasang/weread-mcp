import hashlib
import re
import json
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from http.cookies import SimpleCookie
import requests
from requests.utils import cookiejar_from_dict


class WeReadClient:
    """
    Client for interacting with the WeRead API.
    Handles authentication and provides methods for fetching data from WeRead.
    """
    
    # Base URLs
    WEREAD_URL = "https://weread.qq.com/"
    WEREAD_NOTEBOOKS_URL = "https://i.weread.qq.com/user/notebooks"
    WEREAD_BOOKMARKLIST_URL = "https://i.weread.qq.com/book/bookmarklist"
    WEREAD_CHAPTER_INFO = "https://i.weread.qq.com/book/chapterInfos"
    WEREAD_READ_INFO_URL = "https://i.weread.qq.com/book/readinfo"
    WEREAD_REVIEW_LIST_URL = "https://i.weread.qq.com/review/list"
    WEREAD_BOOK_INFO = "https://i.weread.qq.com/book/info"
    
    def __init__(self, cookie_string: str):
        """
        Initialize the WeRead client with authentication cookies.
        
        Args:
            cookie_string: Cookie string from WeRead web session
        """
        self.session = requests.Session()
        self.session.cookies = self._parse_cookie_string(cookie_string)
        # Test the connection
        self.session.get(self.WEREAD_URL)
    
    def _parse_cookie_string(self, cookie_string: str):
        """
        Parse a cookie string into a cookiejar.
        
        Args:
            cookie_string: Cookie string in format "name=value; name2=value2"
            
        Returns:
            A cookiejar object containing the parsed cookies
        """
        cookie = SimpleCookie()
        cookie.load(cookie_string)
        cookies_dict = {}
        cookiejar = None
        for key, morsel in cookie.items():
            cookies_dict[key] = morsel.value
            cookiejar = cookiejar_from_dict(cookies_dict, cookiejar=None, overwrite=True)
        return cookiejar
    
    def get_notebooklist(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get the user's book list.
        
        Returns:
            List of book data dictionaries, or None if the request fails
        """
        response = self.session.get(self.WEREAD_NOTEBOOKS_URL)
        if response.ok:
            data = response.json()
            books = data.get("books", [])
            books.sort(key=lambda x: x["sort"])
            return books
        else:
            print(f"Failed to get notebook list: {response.text}")
        return None
    
    def get_bookmark_list(self, book_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get highlights for a specific book.
        
        Args:
            book_id: The ID of the book
            
        Returns:
            List of highlight dictionaries, or None if the request fails
        """
        params = {"bookId": book_id}
        response = self.session.get(self.WEREAD_BOOKMARKLIST_URL, params=params)
        if response.ok:
            updated = response.json().get("updated", [])
            # Sort by chapter and position
            updated = sorted(
                updated,
                key=lambda x: (x.get("chapterUid", 1), int(x.get("range", "0-0").split("-")[0] or 0)),
            )
            return updated
        return None
    
    def get_read_info(self, book_id: str) -> Optional[Dict[str, Any]]:
        """
        Get reading information for a specific book.
        
        Args:
            book_id: The ID of the book
            
        Returns:
            Dictionary containing reading info, or None if the request fails
        """
        params = {
            "bookId": book_id, 
            "readingDetail": 1, 
            "readingBookIndex": 1, 
            "finishedDate": 1
        }
        response = self.session.get(self.WEREAD_READ_INFO_URL, params=params)
        if response.ok:
            return response.json()
        return None
    
    def get_bookinfo(self, book_id: str) -> Tuple[str, float]:
        """
        Get detailed information for a specific book.
        
        Args:
            book_id: The ID of the book
            
        Returns:
            Tuple containing (ISBN, rating)
        """
        params = {"bookId": book_id}
        response = self.session.get(self.WEREAD_BOOK_INFO, params=params)
        isbn = ""
        rating = 0
        if response.ok:
            data = response.json()
            isbn = data.get("isbn", "")
            # Rating is scaled by 1000 in the API
            new_rating = data.get("newRating", 0) / 1000
            return (isbn, new_rating)
        else:
            print(f"Failed to get book info for {book_id}: {response.text}")
        return ("", 0)
    
    def get_review_list(self, book_id: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Get reviews and notes for a specific book.
        
        Args:
            book_id: The ID of the book
            
        Returns:
            Tuple containing (summary reviews, normal reviews)
        """
        params = {"bookId": book_id, "listType": 11, "mine": 1, "syncKey": 0}
        response = self.session.get(self.WEREAD_REVIEW_LIST_URL, params=params)
        
        if not response.ok:
            return [], []
            
        reviews = response.json().get("reviews", [])
        # Filter for summary reviews (type 4)
        summary = list(filter(lambda x: x.get("review", {}).get("type") == 4, reviews))
        # Filter for normal reviews (type 1)
        reviews = list(filter(lambda x: x.get("review", {}).get("type") == 1, reviews))
        # Extract the review field and rename content to markText
        reviews = list(map(lambda x: x.get("review"), reviews))
        reviews = list(map(lambda x: {**x, "markText": x.pop("content")}, reviews))
        
        return summary, reviews
    
    def get_chapter_info(self, book_id: str) -> Optional[Dict[int, Dict[str, Any]]]:
        """
        Get chapter information for a specific book.
        
        Args:
            book_id: The ID of the book
            
        Returns:
            Dictionary mapping chapter UIDs to chapter information, or None if the request fails
        """
        body = {"bookIds": [book_id], "synckeys": [0], "teenmode": 0}
        response = self.session.post(self.WEREAD_CHAPTER_INFO, json=body)
        
        if (response.ok and 
            "data" in response.json() and 
            len(response.json()["data"]) == 1 and 
            "updated" in response.json()["data"][0]):
            
            update = response.json()["data"][0]["updated"]
            return {item["chapterUid"]: item for item in update}
        
        return None
    
    @staticmethod
    def calculate_book_str_id(book_id: str) -> str:
        """
        Calculate a string ID used in WeRead web URLs.
        
        Args:
            book_id: The book ID
            
        Returns:
            Transformed book ID for use in web URLs
        """
        md5 = hashlib.md5()
        md5.update(book_id.encode("utf-8"))
        digest = md5.hexdigest()
        result = digest[0:3]
        code, transformed_ids = WeReadClient.transform_id(book_id)
        result += code + "2" + digest[-2:]

        for i in range(len(transformed_ids)):
            hex_length_str = format(len(transformed_ids[i]), "x")
            if len(hex_length_str) == 1:
                hex_length_str = "0" + hex_length_str

            result += hex_length_str + transformed_ids[i]

            if i < len(transformed_ids) - 1:
                result += "g"

        if len(result) < 20:
            result += digest[0: 20 - len(result)]

        md5 = hashlib.md5()
        md5.update(result.encode("utf-8"))
        result += md5.hexdigest()[0:3]
        return result
    
    @staticmethod
    def transform_id(book_id: str) -> Tuple[str, List[str]]:
        """
        Transform a book ID for use in calculating web URLs.
        
        Args:
            book_id: The book ID
            
        Returns:
            Tuple containing (code, transformed IDs)
        """
        id_length = len(book_id)

        if re.match("^\\d*$", book_id):
            ary = []
            for i in range(0, id_length, 9):
                ary.append(format(int(book_id[i: min(i + 9, id_length)]), "x"))
            return "3", ary

        result = ""
        for i in range(id_length):
            result += format(ord(book_id[i]), "x")
        return "4", [result] 