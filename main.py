#!/usr/bin/env python3
"""
LinkedIn Automation Agent - Main Orchestrator

This is the main entry point for the LinkedIn automation system that:
- Schedules and manages automated posting twice weekly (Wed 12 PM/Sat 9 AM)
- Handles intelligent engagement with top 50 connections
- Generates content using Perplexity AI
- Maintains comprehensive logging and monitoring
"""

import asyncio
import sys
import signal
import time
from datetime import datetime
from typing import Optional

# Import our modules
from config import settings, validate_config, update_weekly_topics
from linkedin_client import LinkedInClient
from linkedin_official_client import LinkedInOfficialClient
from perplexity_client import PerplexityClient
from engagement_manager import EngagementManager
from scheduler import LinkedInScheduler
from logger_config import automation_logger, log_activity, log_error, create_alert
import pytz
import re

class LinkedInAutomationAgent:
    """Main orchestrator for LinkedIn automation"""
    
    def __init__(self):
        self.linkedin_client = None
        self.linkedin_official_client = None
        self.perplexity_client = None
        self.engagement_manager = None
        self.scheduler = None
        self.is_running = False
        self.current_session = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _get_access_token(self) -> str:
        """Get LinkedIn access token from settings or token file"""
        # Prefer .env token, else fall back to linkedin_token.json created by OAuth
        if settings.linkedin_access_token:
            return settings.linkedin_access_token
        try:
            import json
            with open("linkedin_token.json", "r", encoding="utf-8") as f:
                token_json = json.load(f)
                return token_json.get("access_token", "")
        except Exception:
            return ""
    
    def _select_topic_for_today(self, topics: list) -> str:
        """Select topic based on current day"""
        if not topics:
            return "Professional Insights"
        day = _day_name_lower()
        # Map: Wednesday -> first, Saturday -> second, else first
        if day == "wednesday":
            return topics[0]
        if day == "saturday":
            return topics[1] if len(topics) > 1 else topics[0]
        return topics[0]
    
    def _generate_image_urls(self, topic: str) -> list:
        """Generate image URLs for a given topic"""
        slug = _slugify(topic) or "linkedin-topic"
        seeds = [slug, f"{slug}-2"]
        return [f"https://picsum.photos/seed/{s}/1200/675" for s in seeds]
    
    async def initialize(self):
        """Initialize all components"""
        
        try:
            automation_logger.logger.info("Initializing LinkedIn Automation Agent...")
            
            # Validate configuration
            validate_config()
            automation_logger.logger.info("Configuration validated successfully")
            
            # Initialize clients
            self.linkedin_client = LinkedInClient()
            self.perplexity_client = PerplexityClient()

            # Initialize official LinkedIn client (for image posts)
            access_token = self._get_access_token()
            if access_token:
                self.linkedin_official_client = LinkedInOfficialClient(access_token)
                automation_logger.logger.info("Initialized LinkedInOfficialClient for image posts")
            else:
                automation_logger.logger.warning("No LinkedIn access token found; falling back to text-only posts")
            
            # Initialize engagement manager
            self.engagement_manager = EngagementManager(
                self.linkedin_client,
                self.perplexity_client
            )
            
            # Initialize scheduler
            self.scheduler = LinkedInScheduler()
            
            # Schedule automation tasks
            self.scheduler.schedule_automation_tasks(
                engagement_callback=self._handle_engagement_session,
                posting_callback=self._handle_posting_session,
                session_end_callback=self._handle_session_end
            )
            
            automation_logger.logger.info("All components initialized successfully")
            log_activity("system_initialization", {"status": "success"}, success=True)
            
        except Exception as e:
            error_msg = f"Failed to initialize automation agent: {e}"
            automation_logger.logger.error(error_msg)
            log_error("initialization_error", error_msg)
            create_alert("initialization_failure", error_msg)
            raise
    
    async def start(self):
        """Start the automation agent"""
        
        if self.is_running:
            automation_logger.logger.warning("Agent is already running")
            return
        
        try:
            self.is_running = True
            automation_logger.logger.info("Starting LinkedIn Automation Agent")
            
            # Start the scheduler
            self.scheduler.start_scheduler()
            
            # Log system start
            log_activity("system_start", {
                "start_time": datetime.now().isoformat(),
                "next_scheduled_run": self.scheduler.get_next_run_time().isoformat() if self.scheduler.get_next_run_time() else None
            })
            
            automation_logger.logger.info("LinkedIn Automation Agent started successfully")
            automation_logger.logger.info(f"Next scheduled run: {self.scheduler.get_next_run_time()}")
            
            # Keep the main thread alive
            await self._main_loop()
            
        except Exception as e:
            error_msg = f"Error starting automation agent: {e}"
            automation_logger.logger.error(error_msg)
            log_error("startup_error", error_msg)
            create_alert("startup_failure", error_msg)
            raise
    
    async def _main_loop(self):
        """Main event loop"""
        
        try:
            while self.is_running:
                # Check system health periodically
                await self._health_check()
                
                # Sleep for a minute before next check
                await asyncio.sleep(60)
                
        except asyncio.CancelledError:
            automation_logger.logger.info("Main loop cancelled")
        except Exception as e:
            error_msg = f"Error in main loop: {e}"
            automation_logger.logger.error(error_msg)
            log_error("main_loop_error", error_msg)
    
    async def _health_check(self):
        """Perform periodic health checks"""
        
        try:
            health_status = automation_logger.get_system_health()
            
            # Log health status if there are issues
            if health_status['status'] != 'healthy':
                automation_logger.logger.warning(f"System health: {health_status['status']}")
                
                if health_status['status'] == 'critical':
                    create_alert("system_health_critical", 
                                f"System health is critical: {health_status}")
            
            # Check for unresolved alerts
            unresolved_alerts = automation_logger.get_unresolved_alerts()
            if len(unresolved_alerts) > 5:
                create_alert("too_many_alerts", 
                           f"Too many unresolved alerts: {len(unresolved_alerts)}")
            
        except Exception as e:
            log_error("health_check_error", f"Error during health check: {e}")
    
    async def _handle_engagement_session(self, phase: str, duration_minutes: int = 30):
        """Handle engagement session callback from scheduler"""
        
        session_id = f"engagement_{phase}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            automation_logger.log_session_start(session_id, f"engagement_{phase}")
            
            start_time = time.time()
            
            # Run engagement session
            await self.engagement_manager.run_engagement_session(phase, duration_minutes)
            
            duration = time.time() - start_time
            
            # Get session stats
            stats = self.engagement_manager.get_engagement_stats()
            
            automation_logger.log_session_end(session_id, stats)
            automation_logger.log_performance(f"engagement_session_{phase}", duration, stats)
            
            automation_logger.logger.info(f"Engagement session ({phase}) completed successfully")
            
        except Exception as e:
            error_msg = f"Error in engagement session ({phase}): {e}"
            automation_logger.logger.error(error_msg)
            log_error("engagement_session_error", error_msg, {"phase": phase, "session_id": session_id})
            create_alert("engagement_failure", error_msg, {"phase": phase})
    
    async def _handle_posting_session(self):
        """Handle posting session callback from scheduler"""
        
        session_id = f"posting_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            automation_logger.log_session_start(session_id, "posting")
            
            start_time = time.time()
            
            # Check if we have topics to work with
            if not settings.weekly_topics:
                error_msg = "No weekly topics configured for content generation"
                automation_logger.logger.error(error_msg)
                log_error("configuration_error", error_msg)
                create_alert("no_topics_configured", error_msg)
                return
            
            # Select topic based on today (Wed vs Sat)
            selected_topic = self._select_topic_for_today(settings.weekly_topics)
            
            # Generate post content (~500 words)
            automation_logger.logger.info(f"Generating LinkedIn post content for topic: {selected_topic}")
            context = (
                "Write ~500 words (450–550) in a professional, warm tone. "
                "Open with a strong hook, include concrete examples and practical tips, "
                "add a brief CTA, include 3–5 relevant hashtags, and end with a thoughtful question."
            )
            post_content = await self.perplexity_client.generate_linkedin_post(
                topic=selected_topic,
                context=context
            )
            
            if not post_content:
                error_msg = "Failed to generate post content"
                automation_logger.logger.error(error_msg)
                log_error("content_generation_error", error_msg)
                create_alert("content_generation_failure", error_msg)
                return
            
            # Post to LinkedIn with images when possible
            image_urls = self._generate_image_urls(selected_topic)
            automation_logger.logger.info("Posting content to LinkedIn with images...")
            if self.linkedin_official_client:
                success = await self.linkedin_official_client.post_content_with_images(
                    content=post_content,
                    image_urls=image_urls
                )
            else:
                # No fallback - linkedin_client doesn't support posting
                error_msg = "LinkedIn Official Client not available and linkedin_client doesn't support posting"
                automation_logger.logger.error(error_msg)
                log_error("posting_error", error_msg)
                create_alert("no_posting_client", error_msg)
                success = False
            
            duration = time.time() - start_time
            
            # Log the posting activity
            automation_logger.log_post_creation(post_content, success)
            automation_logger.log_performance("posting_session", duration, {
                "content_length": len(post_content),
                "success": success
            })
            
            if success:
                automation_logger.logger.info("LinkedIn post published successfully")
                log_activity("post_published", {
                    "content_preview": post_content[:100] + "...",
                    "content_length": len(post_content),
                    "topic": selected_topic,
                    "images": image_urls
                }, success=True)
            else:
                error_msg = "Failed to publish LinkedIn post"
                automation_logger.logger.error(error_msg)
                log_error("posting_error", error_msg)
                create_alert("posting_failure", error_msg)
            
            automation_logger.log_session_end(session_id, {
                "success": success,
                "content_length": len(post_content),
                "duration": duration,
                "topic": selected_topic
            })
            
        except Exception as e:
            error_msg = f"Error in posting session: {e}"
            automation_logger.logger.error(error_msg)
            log_error("posting_session_error", error_msg, {"session_id": session_id})
            create_alert("posting_session_failure", error_msg)
    
    async def _handle_session_end(self, session_info: dict):
        """Handle session end callback"""
        
        try:
            automation_logger.logger.info(f"Session completed: {session_info.get('id', 'unknown')}")
            
            # Reset daily stats if it's a new day
            current_date = datetime.now().date()
            if hasattr(self, '_last_reset_date') and self._last_reset_date != current_date:
                self.engagement_manager.reset_daily_stats()
                self._last_reset_date = current_date
            elif not hasattr(self, '_last_reset_date'):
                self._last_reset_date = current_date
            
        except Exception as e:
            log_error("session_end_error", f"Error handling session end: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        automation_logger.logger.info(f"Received signal {signum}, shutting down gracefully...")
        asyncio.create_task(self.stop())
    
    async def stop(self):
        """Stop the automation agent gracefully"""
        
        if not self.is_running:
            return
        
        try:
            automation_logger.logger.info("Stopping LinkedIn Automation Agent...")
            
            self.is_running = False
            
            # Stop scheduler
            if self.scheduler:
                self.scheduler.stop_scheduler()
            
            # Log system stop
            log_activity("system_stop", {
                "stop_time": datetime.now().isoformat(),
                "reason": "graceful_shutdown"
            })
            
            automation_logger.logger.info("LinkedIn Automation Agent stopped successfully")
            
        except Exception as e:
            error_msg = f"Error stopping automation agent: {e}"
            automation_logger.logger.error(error_msg)
            log_error("shutdown_error", error_msg)
    
    def update_topics(self, topics: list):
        """Update weekly topics for content generation"""
        
        try:
            update_weekly_topics(topics)
            automation_logger.logger.info(f"Updated weekly topics: {topics}")
            log_activity("topics_updated", {"topics": topics})
            
        except Exception as e:
            error_msg = f"Error updating topics: {e}"
            automation_logger.logger.error(error_msg)
            log_error("topics_update_error", error_msg)
    
    def get_status(self) -> dict:
        """Get current status of the automation agent"""
        
        try:
            status = {
                "is_running": self.is_running,
                "current_session": self.current_session,
                "next_scheduled_run": self.scheduler.get_next_run_time().isoformat() if self.scheduler and self.scheduler.get_next_run_time() else None,
                "system_health": automation_logger.get_system_health(),
                "engagement_stats": self.engagement_manager.get_engagement_stats() if self.engagement_manager else {},
                "weekly_topics": settings.weekly_topics,
                "unresolved_alerts": len(automation_logger.get_unresolved_alerts())
            }
            
            return status
            
        except Exception as e:
            log_error("status_error", f"Error getting status: {e}")
            return {"error": str(e)}

async def main():
    """Main entry point"""
    
    agent = LinkedInAutomationAgent()
    
    try:
        # Initialize the agent
        await agent.initialize()
        
        # Start the agent
        await agent.start()
        
    except KeyboardInterrupt:
        automation_logger.logger.info("Received keyboard interrupt")
    except Exception as e:
        automation_logger.logger.error(f"Fatal error: {e}")
        create_alert("fatal_error", f"Fatal error occurred: {e}")
    finally:
        # Ensure graceful shutdown
        await agent.stop()

if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    
    # Run the main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

# Helper methods appended to class
def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def _now_in_tz() -> datetime:
    tz = pytz.timezone(settings.timezone)
    return datetime.now(tz)

def _day_name_lower() -> str:
    return _now_in_tz().strftime("%A").lower()