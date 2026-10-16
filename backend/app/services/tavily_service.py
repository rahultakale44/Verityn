"""Tavily search API integration service."""
from typing import Optional
import logging
from tavily import TavilyClient
from app.core.config import settings


logger = logging.getLogger(__name__)


class TavilyConfigurationError(Exception):
    """Raised when Tavily API is not configured."""
    pass


class TavilySearchError(Exception):
    """Raised when Tavily search fails."""
    pass


class TavilyService:
    """Service for interacting with Tavily Search API."""
    
    def __init__(self):
        """Initialize Tavily client."""
        self._client: Optional[TavilyClient] = None
    
    def _get_client(self) -> TavilyClient:
        """
        Get or create Tavily client.
        
        Returns:
            TavilyClient instance
            
        Raises:
            TavilyConfigurationError: If API key is not configured
        """
        if not settings.tavily_api_key or settings.tavily_api_key == "your_tavily_api_key_here":
            raise TavilyConfigurationError(
                "Tavily API key is not configured. Set TAVILY_API_KEY in your environment."
            )
        
        if self._client is None:
            self._client = TavilyClient(api_key=settings.tavily_api_key)
        
        return self._client
    
    def search(self, query: str, max_results: Optional[int] = None) -> dict:
        """
        Perform a search using Tavily API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            Search results from Tavily
            
        Raises:
            TavilyConfigurationError: If API key is not configured
            TavilySearchError: If search fails
        """
        try:
            client = self._get_client()
            
            # Use configured max results if not specified
            if max_results is None:
                max_results = settings.tavily_max_results
            
            # Perform search with timeout
            response = client.search(
                query=query,
                max_results=max_results,
                search_depth="basic",
                include_answer=False,
                include_raw_content=False
            )
            
            return response
            
        except TavilyConfigurationError:
            raise
        except Exception as e:
            # Log the error but don't expose internal details
            logger.error(f"Tavily search failed for query '{query[:50]}...': {str(e)}")
            raise TavilySearchError(f"Search request failed: {type(e).__name__}")
    
    def is_configured(self) -> bool:
        """
        Check if Tavily API is properly configured.
        
        Returns:
            True if API key is configured, False otherwise
        """
        return bool(
            settings.tavily_api_key and 
            settings.tavily_api_key != "your_tavily_api_key_here"
        )


# Global service instance
tavily_service = TavilyService()
