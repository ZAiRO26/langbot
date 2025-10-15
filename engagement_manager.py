import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
from linkedin_client import LinkedInClient
from perplexity_client import PerplexityClient
from config import settings

logger = logging.getLogger(__name__)

class EngagementManager:
    """Manages LinkedIn engagement activities with rate limiting and intelligent distribution"""
    
    def __init__(self, linkedin_client: LinkedInClient, perplexity_client: PerplexityClient):
        self.linkedin_client = linkedin_client
        self.perplexity_client = perplexity_client
        self.engagement_history = []
        self.daily_limits = {
            'comments': settings.max_comments_per_session,
            'likes': settings.max_comments_per_session * 2,  # Allow more likes than comments
        }
        self.session_stats = {
            'comments_made': 0,
            'likes_made': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    async def run_engagement_session(self, phase: str, duration_minutes: int = 30):
        """
        Run an engagement session for the specified duration
        
        Args:
            phase: 'pre_posting' or 'post_posting'
            duration_minutes: Duration of the engagement session
        """
        
        logger.info(f"Starting {phase} engagement session for {duration_minutes} minutes")
        
        self.session_stats['start_time'] = datetime.now()
        self.session_stats['comments_made'] = 0
        self.session_stats['likes_made'] = 0
        self.session_stats['errors'] = 0
        
        try:
            # Get top connections
            connections = await self.linkedin_client.get_top_connections(
                limit=settings.top_connections_count
            )
            
            if not connections:
                logger.warning("No connections found")
                return
            
            # Get user profile for personalization
            user_profile = self.linkedin_client.get_profile_info()
            
            # Collect posts from connections
            all_posts = await self._collect_posts_from_connections(connections)
            
            if not all_posts:
                logger.warning("No posts found from connections")
                return
            
            # Filter and prioritize posts
            target_posts = self._prioritize_posts(all_posts, phase)
            
            # Calculate engagement distribution
            engagement_plan = self._create_engagement_plan(target_posts, duration_minutes)
            
            # Execute engagement plan
            await self._execute_engagement_plan(engagement_plan, user_profile)
            
        except Exception as e:
            logger.error(f"Error during engagement session: {e}")
            self.session_stats['errors'] += 1
        
        finally:
            self.session_stats['end_time'] = datetime.now()
            self._log_session_summary(phase)
    
    async def _collect_posts_from_connections(self, connections: List[Dict]) -> List[Dict]:
        """Collect recent posts from all connections"""
        
        all_posts = []
        
        for connection in connections:
            try:
                connection_id = connection.get('public_id') or connection.get('id')
                if not connection_id:
                    continue
                
                posts = await self.linkedin_client.get_connection_posts(
                    connection_id=connection_id,
                    days_back=settings.posts_lookback_days
                )
                
                # Add connection info to each post
                for post in posts:
                    post['connection_info'] = {
                        'name': f"{connection.get('firstName', '')} {connection.get('lastName', '')}".strip(),
                        'headline': connection.get('headline', ''),
                        'connection_id': connection_id
                    }
                
                all_posts.extend(posts)
                
                # Add delay to avoid rate limiting
                await asyncio.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"Error collecting posts from connection {connection.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Collected {len(all_posts)} posts from {len(connections)} connections")
        return all_posts
    
    def _prioritize_posts(self, posts: List[Dict], phase: str) -> List[Dict]:
        """
        Prioritize posts based on engagement potential and recency
        
        Args:
            posts: List of posts to prioritize
            phase: Current engagement phase
            
        Returns:
            Prioritized list of posts
        """
        
        # Filter out posts we've already engaged with
        engaged_post_ids = {entry['post_id'] for entry in self.engagement_history}
        new_posts = [post for post in posts if post.get('id') not in engaged_post_ids]
        
        # Score posts based on various factors
        scored_posts = []
        for post in new_posts:
            score = self._calculate_post_score(post)
            scored_posts.append((score, post))
        
        # Sort by score (highest first)
        scored_posts.sort(key=lambda x: x[0], reverse=True)
        
        # Return top posts based on phase
        max_posts = settings.max_comments_per_session // 2 if phase == "pre_posting" else settings.max_comments_per_session // 2
        
        return [post for score, post in scored_posts[:max_posts]]
    
    def _calculate_post_score(self, post: Dict) -> float:
        """Calculate engagement score for a post"""
        
        score = 0.0
        
        # Recency score (newer posts get higher score)
        post_time = post.get('time', 0)
        if post_time:
            hours_ago = (time.time() * 1000 - post_time) / (1000 * 3600)
            recency_score = max(0, 24 - hours_ago) / 24  # Higher score for posts < 24h old
            score += recency_score * 3
        
        # Engagement score (posts with more likes/comments get higher score)
        likes = post.get('numLikes', 0)
        comments = post.get('numComments', 0)
        engagement_score = min((likes + comments * 2) / 100, 2)  # Cap at 2 points
        score += engagement_score
        
        # Content length score (prefer posts with substantial content)
        content_length = len(post.get('text', ''))
        if 100 <= content_length <= 1000:  # Sweet spot for engagement
            score += 1
        elif content_length > 50:
            score += 0.5
        
        # Connection relationship score (could be enhanced with more data)
        connection_info = post.get('connection_info', {})
        if connection_info.get('headline'):
            score += 0.5  # Bonus for connections with complete profiles
        
        return score
    
    def _create_engagement_plan(self, posts: List[Dict], duration_minutes: int) -> List[Dict]:
        """Create a time-distributed engagement plan"""
        
        if not posts:
            return []
        
        # Calculate timing intervals
        total_seconds = duration_minutes * 60
        num_engagements = min(len(posts), settings.max_comments_per_session // 2)
        
        if num_engagements == 0:
            return []
        
        # Distribute engagements over time with some randomness
        base_interval = total_seconds / num_engagements
        
        engagement_plan = []
        current_time = 0
        
        for i, post in enumerate(posts[:num_engagements]):
            # Add some randomness to timing
            jitter = random.uniform(-base_interval * 0.3, base_interval * 0.3)
            scheduled_time = current_time + jitter
            
            # Determine engagement type (comment vs like)
            engagement_type = self._determine_engagement_type(post)
            
            engagement_plan.append({
                'post': post,
                'scheduled_time': max(0, scheduled_time),
                'engagement_type': engagement_type
            })
            
            current_time += base_interval
        
        # Sort by scheduled time
        engagement_plan.sort(key=lambda x: x['scheduled_time'])
        
        logger.info(f"Created engagement plan with {len(engagement_plan)} activities over {duration_minutes} minutes")
        return engagement_plan
    
    def _determine_engagement_type(self, post: Dict) -> str:
        """Determine whether to comment or like based on post characteristics"""
        
        # Analyze post content to determine best engagement type
        content = post.get('text', '')
        
        # Posts with questions or calls for discussion get comments
        question_indicators = ['?', 'what do you think', 'thoughts?', 'agree?', 'disagree?', 'opinion']
        if any(indicator in content.lower() for indicator in question_indicators):
            return 'comment'
        
        # Posts about achievements or announcements get likes more often
        celebration_indicators = ['excited', 'proud', 'announce', 'launch', 'achievement', 'milestone']
        if any(indicator in content.lower() for indicator in celebration_indicators):
            return 'like' if random.random() < 0.7 else 'comment'
        
        # Default: 60% comment, 40% like
        return 'comment' if random.random() < 0.6 else 'like'
    
    async def _execute_engagement_plan(self, engagement_plan: List[Dict], user_profile: Dict):
        """Execute the engagement plan with proper timing"""
        
        start_time = time.time()
        
        for activity in engagement_plan:
            try:
                # Wait until scheduled time
                elapsed_time = time.time() - start_time
                wait_time = activity['scheduled_time'] - elapsed_time
                
                if wait_time > 0:
                    logger.debug(f"Waiting {wait_time:.1f} seconds for next engagement")
                    await asyncio.sleep(wait_time)
                
                # Execute the engagement
                success = await self._execute_single_engagement(activity, user_profile)
                
                if success:
                    # Record the engagement
                    self.engagement_history.append({
                        'post_id': activity['post'].get('id'),
                        'engagement_type': activity['engagement_type'],
                        'timestamp': datetime.now(),
                        'connection_name': activity['post'].get('connection_info', {}).get('name', 'Unknown')
                    })
                
                # Add random delay between actions
                delay = random.uniform(
                    settings.min_delay_between_actions,
                    settings.max_delay_between_actions
                )
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error executing engagement activity: {e}")
                self.session_stats['errors'] += 1
                continue
    
    async def _execute_single_engagement(self, activity: Dict, user_profile: Dict) -> bool:
        """Execute a single engagement activity"""
        
        post = activity['post']
        engagement_type = activity['engagement_type']
        post_id = post.get('id')
        
        if not post_id:
            logger.warning("Post ID not found, skipping engagement")
            return False
        
        try:
            if engagement_type == 'comment':
                # Generate and post comment
                comment = await self.perplexity_client.generate_comment(
                    post_content=post.get('text', ''),
                    author_name=post.get('connection_info', {}).get('name', '')
                )
                
                if comment:
                    success = await self.linkedin_client.comment_on_post(post_id, comment)
                    if success:
                        self.session_stats['comments_made'] += 1
                        logger.info(f"Commented on post by {post.get('connection_info', {}).get('name', 'Unknown')}")
                    return success
                else:
                    logger.warning("Failed to generate comment")
                    return False
            
            elif engagement_type == 'like':
                success = await self.linkedin_client.like_post(post_id)
                if success:
                    self.session_stats['likes_made'] += 1
                    logger.info(f"Liked post by {post.get('connection_info', {}).get('name', 'Unknown')}")
                return success
            
        except Exception as e:
            logger.error(f"Error executing {engagement_type} on post {post_id}: {e}")
            return False
        
        return False
    
    def _log_session_summary(self, phase: str):
        """Log summary of the engagement session"""
        
        duration = None
        if self.session_stats['start_time'] and self.session_stats['end_time']:
            duration = (self.session_stats['end_time'] - self.session_stats['start_time']).total_seconds() / 60
        
        logger.info(f"""
        Engagement Session Summary ({phase}):
        - Duration: {duration:.1f} minutes
        - Comments made: {self.session_stats['comments_made']}
        - Likes made: {self.session_stats['likes_made']}
        - Errors: {self.session_stats['errors']}
        - Total engagements: {self.session_stats['comments_made'] + self.session_stats['likes_made']}
        """)
    
    def get_engagement_stats(self) -> Dict:
        """Get current engagement statistics"""
        
        return {
            'session_stats': self.session_stats.copy(),
            'total_historical_engagements': len(self.engagement_history),
            'daily_limits': self.daily_limits.copy(),
            'recent_engagements': self.engagement_history[-10:] if self.engagement_history else []
        }
    
    def reset_daily_stats(self):
        """Reset daily engagement statistics"""
        
        self.session_stats = {
            'comments_made': 0,
            'likes_made': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Keep only recent engagement history (last 7 days)
        cutoff_date = datetime.now() - timedelta(days=7)
        self.engagement_history = [
            entry for entry in self.engagement_history
            if entry['timestamp'] > cutoff_date
        ]
        
        logger.info("Daily engagement stats reset")