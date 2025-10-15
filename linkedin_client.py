import requests
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from linkedin_api import Linkedin
from config import settings
import asyncio
from asyncio_throttle import Throttler

logger = logging.getLogger(__name__)

class LinkedInClient:
    """LinkedIn API client for automation tasks"""
    
    def __init__(self):
        self.api = None
        self.throttler = Throttler(rate_limit=settings.linkedin_api_rate_limit, period=3600)  # per hour
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize LinkedIn API client"""
        try:
            if settings.linkedin_username and settings.linkedin_password:
                self.api = Linkedin(
                    username=settings.linkedin_username,
                    password=settings.linkedin_password
                )
                logger.info("LinkedIn client initialized successfully")
            else:
                logger.error("LinkedIn credentials not provided")
                raise ValueError("LinkedIn credentials required")
        except Exception as e:
            logger.error(f"Failed to initialize LinkedIn client: {e}")
            raise
    
    async def post_content(self, content: str, image_path: Optional[str] = None) -> bool:
        """
        Post content to LinkedIn - NOTE: linkedin-api library does not support posting
        This method will log an error and return False
        
        Args:
            content: The text content to post
            image_path: Optional path to image to include
            
        Returns:
            bool: Always False as linkedin-api doesn't support posting
        """
        logger.error("LinkedInClient does not support posting. The linkedin-api library only supports reading data, not posting content.")
        logger.info("Use LinkedInOfficialClient for posting functionality instead.")
        return False
    
    async def get_top_connections(self, limit: int = 50) -> List[Dict]:
        """
        Get top connections from LinkedIn
        
        Args:
            limit: Maximum number of connections to retrieve
            
        Returns:
            List of connection dictionaries
        """
        try:
            async with self.throttler:
                connections = self.api.get_connections(limit=limit)
                
                # Sort by activity/engagement if possible
                # For now, just return the first 'limit' connections
                top_connections = connections[:limit] if connections else []
                
                logger.info(f"Retrieved {len(top_connections)} top connections")
                return top_connections
                
        except Exception as e:
            logger.error(f"Error fetching connections: {e}")
            return []
    
    async def get_connection_posts(self, connection_id: str, days_back: int = 7) -> List[Dict]:
        """
        Get recent posts from a specific connection
        
        Args:
            connection_id: LinkedIn ID of the connection
            days_back: Number of days to look back for posts
            
        Returns:
            List of post dictionaries
        """
        try:
            async with self.throttler:
                # Calculate date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days_back)
                
                # Get posts from the connection's profile
                posts = self.api.get_profile_posts(
                    public_id=connection_id,
                    post_count=10  # Limit to recent posts
                )
                
                # Filter posts by date range
                recent_posts = []
                for post in posts:
                    post_date = datetime.fromtimestamp(post.get('time', 0) / 1000)
                    if start_date <= post_date <= end_date:
                        recent_posts.append(post)
                
                logger.info(f"Retrieved {len(recent_posts)} recent posts from connection {connection_id}")
                return recent_posts
                
        except Exception as e:
            logger.error(f"Error fetching posts for connection {connection_id}: {e}")
            return []
    
    async def comment_on_post(self, post_id: str, comment: str) -> bool:
        """
        Comment on a LinkedIn post
        
        Args:
            post_id: ID of the post to comment on
            comment: Comment text
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with self.throttler:
                result = self.api.add_post_comment(
                    post_id=post_id,
                    comment_text=comment
                )
                
                if result:
                    logger.info(f"Successfully commented on post {post_id}")
                    return True
                else:
                    logger.error(f"Failed to comment on post {post_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error commenting on post {post_id}: {e}")
            return False
    
    async def like_post(self, post_id: str) -> bool:
        """
        Like a LinkedIn post
        
        Args:
            post_id: ID of the post to like
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with self.throttler:
                result = self.api.like_post(post_id=post_id)
                
                if result:
                    logger.info(f"Successfully liked post {post_id}")
                    return True
                else:
                    logger.error(f"Failed to like post {post_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error liking post {post_id}: {e}")
            return False
    
    def get_profile_info(self) -> Dict:
        """Get current user's profile information"""
        try:
            profile = self.api.get_profile()
            logger.info("Retrieved profile information")
            return profile
        except Exception as e:
            logger.error(f"Error fetching profile info: {e}")
            return {}
    
    async def search_posts_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict]:
        """
        Search for posts by keyword
        
        Args:
            keyword: Keyword to search for
            limit: Maximum number of posts to return
            
        Returns:
            List of post dictionaries
        """
        try:
            async with self.throttler:
                posts = self.api.search_posts(
                    keywords=keyword,
                    limit=limit
                )
                
                logger.info(f"Found {len(posts)} posts for keyword: {keyword}")
                return posts
                
        except Exception as e:
            logger.error(f"Error searching posts with keyword {keyword}: {e}")
            return []