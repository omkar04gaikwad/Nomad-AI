import json
import os
from datetime import datetime, date
from typing import Dict, Any
from pathlib import Path

class RateLimiter:
    """
    Simple rate limiter to track and limit user requests per day.
    Stores data in a JSON file for persistence.
    """
    
    def __init__(self, limit: int = 5, data_file: str = "data/rate_limits.json"):
        self.limit = limit
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_data()
    
    def _load_data(self):
        """Load rate limit data from file."""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
            else:
                self.data = {}
        except Exception:
            self.data = {}
    
    def _save_data(self):
        """Save rate limit data to file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save rate limit data: {e}")
    
    def _get_user_key(self, user_id: str = "default") -> str:
        """Generate a key for user tracking."""
        today = date.today().isoformat()
        return f"{user_id}_{today}"
    
    def _cleanup_old_data(self):
        """Remove old rate limit data (older than 7 days)."""
        today = date.today()
        keys_to_remove = []
        
        for key in self.data.keys():
            try:
                # Extract date from key (format: user_id_YYYY-MM-DD)
                date_str = key.split('_', 1)[1]
                key_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                
                # Remove data older than 7 days
                if (today - key_date).days > 7:
                    keys_to_remove.append(key)
            except Exception:
                # If key format is invalid, remove it
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.data[key]
        
        if keys_to_remove:
            self._save_data()
    
    def check_limit(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Check if user has exceeded the daily limit.
        
        Args:
            user_id: Unique identifier for the user (default: "default")
            
        Returns:
            Dictionary with limit status and remaining requests
        """
        self._cleanup_old_data()
        user_key = self._get_user_key(user_id)
        
        # Get current count for today
        current_count = self.data.get(user_key, 0)
        
        # Check if limit exceeded
        if current_count >= self.limit:
            return {
                "allowed": False,
                "current_count": current_count,
                "limit": self.limit,
                "remaining": 0,
                "reset_date": date.today().isoformat(),
                "message": f"Daily limit of {self.limit} requests exceeded. Please try again tomorrow."
            }
        
        return {
            "allowed": True,
            "current_count": current_count,
            "limit": self.limit,
            "remaining": self.limit - current_count,
            "reset_date": date.today().isoformat(),
            "message": f"You have {self.limit - current_count} requests remaining today."
        }
    
    def increment_request(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Increment the request count for a user.
        
        Args:
            user_id: Unique identifier for the user (default: "default")
            
        Returns:
            Dictionary with updated limit status
        """
        user_key = self._get_user_key(user_id)
        
        # Get current count
        current_count = self.data.get(user_key, 0)
        
        # Increment count
        new_count = current_count + 1
        self.data[user_key] = new_count
        
        # Save updated data
        self._save_data()
        
        return {
            "allowed": new_count <= self.limit,
            "current_count": new_count,
            "limit": self.limit,
            "remaining": max(0, self.limit - new_count),
            "reset_date": date.today().isoformat(),
            "message": f"Request recorded. {max(0, self.limit - new_count)} requests remaining today."
        }
    
    def get_user_stats(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Get statistics for a user.
        
        Args:
            user_id: Unique identifier for the user (default: "default")
            
        Returns:
            Dictionary with user statistics
        """
        user_key = self._get_user_key(user_id)
        current_count = self.data.get(user_key, 0)
        
        return {
            "user_id": user_id,
            "current_count": current_count,
            "limit": self.limit,
            "remaining": max(0, self.limit - current_count),
            "reset_date": date.today().isoformat(),
            "percentage_used": (current_count / self.limit) * 100
        }
    
    def reset_user_limit(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Reset the limit for a user (admin function).
        
        Args:
            user_id: Unique identifier for the user (default: "default")
            
        Returns:
            Dictionary with reset confirmation
        """
        user_key = self._get_user_key(user_id)
        
        if user_key in self.data:
            del self.data[user_key]
            self._save_data()
        
        return {
            "success": True,
            "message": f"Rate limit reset for user {user_id}",
            "user_id": user_id
        }
