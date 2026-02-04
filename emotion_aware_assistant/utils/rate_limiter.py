"""
Rate limiter for OpenAI API calls
"""
import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Simple rate limiter for API calls
    
    Implements token bucket algorithm
    """
    
    def __init__(self, max_calls: int = 60, time_window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        
    def is_allowed(self) -> bool:
        """Check if a call is allowed"""
        now = time.time()
        
        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls 
                      if now - call_time < self.time_window]
        
        # Check if we're under the limit
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        
        return False
    
    def wait_if_needed(self):
        """Wait if rate limit is exceeded"""
        while not self.is_allowed():
            wait_time = self.time_window - (time.time() - self.calls[0])
            if wait_time > 0:
                logger.warning(f"Rate limit reached. Waiting {wait_time:.1f}s...")
                time.sleep(min(wait_time, 1))
            else:
                break

# Global rate limiter for OpenAI calls
# Default: 60 calls per minute (adjust based on your tier)
openai_limiter = RateLimiter(max_calls=60, time_window=60)

def rate_limited(func: Callable) -> Callable:
    """
    Decorator to rate limit OpenAI API calls
    
    Usage:
        @rate_limited
        def call_openai(...):
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        openai_limiter.wait_if_needed()
        return func(*args, **kwargs)
    
    return wrapper
