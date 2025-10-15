import schedule
import time
import logging
from datetime import datetime, timedelta
import pytz
from typing import Callable, Optional
import asyncio
import threading
from config import settings

logger = logging.getLogger(__name__)

class LinkedInScheduler:
    """Scheduler for LinkedIn automation tasks"""
    
    def __init__(self):
        self.timezone = pytz.timezone(settings.timezone)
        self.is_running = False
        self.scheduler_thread = None
        self.current_session = None
        
    def schedule_automation_tasks(self, 
                                 engagement_callback: Callable,
                                 posting_callback: Callable,
                                 session_end_callback: Optional[Callable] = None):
        """
        Schedule the automation tasks for Wednesday and Saturday
        
        Args:
            engagement_callback: Function to call for engagement activities
            posting_callback: Function to call for posting content
            session_end_callback: Optional function to call when session ends
        """
        
        # Schedule for Wednesday
        schedule.every().wednesday.at("12:00").do(
            self._start_automation_session,
            engagement_callback=engagement_callback,
            posting_callback=posting_callback,
            session_end_callback=session_end_callback
        )
        
        # Schedule for Saturday
        schedule.every().saturday.at("09:00").do(
            self._start_automation_session,
            engagement_callback=engagement_callback,
            posting_callback=posting_callback,
            session_end_callback=session_end_callback
        )
        
        logger.info("Scheduled automation tasks for Wednesdays at 12:00 PM and Saturdays at 9:00 AM")
    
    def _start_automation_session(self, 
                                 engagement_callback: Callable,
                                 posting_callback: Callable,
                                 session_end_callback: Optional[Callable] = None):
        """Start a complete automation session"""
        
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session = {
            'id': session_id,
            'start_time': datetime.now(self.timezone),
            'status': 'running'
        }
        
        logger.info(f"Starting automation session: {session_id}")
        
        try:
            # Run the session in a separate thread to avoid blocking
            session_thread = threading.Thread(
                target=self._run_automation_session,
                args=(engagement_callback, posting_callback, session_end_callback)
            )
            session_thread.start()
            
        except Exception as e:
            logger.error(f"Error starting automation session: {e}")
            if self.current_session:
                self.current_session['status'] = 'error'
    
    def _run_automation_session(self, 
                               engagement_callback: Callable,
                               posting_callback: Callable,
                               session_end_callback: Optional[Callable] = None):
        """Run the complete automation session with proper timing"""
        
        try:
            session_start = datetime.now(self.timezone)
            logger.info(f"Automation session started at {session_start}")
            
            # Phase 1: Pre-posting engagement (30 minutes)
            logger.info("Starting pre-posting engagement phase")
            asyncio.run(engagement_callback(phase="pre_posting", duration_minutes=30))
            
            # Wait until exactly 30 minutes after session start for posting
            post_time = session_start + timedelta(minutes=30)
            current_time = datetime.now(self.timezone)
            
            if current_time < post_time:
                wait_seconds = (post_time - current_time).total_seconds()
                logger.info(f"Waiting {wait_seconds} seconds until posting time ({post_time.strftime('%H:%M')})")
                time.sleep(wait_seconds)
            
            # Phase 2: Main posting (exactly 30 minutes after session start)
            logger.info("Starting main posting phase")
            asyncio.run(posting_callback())
            
            # Phase 3: Post-posting engagement (30 minutes after posting)
            logger.info("Starting post-posting engagement phase")
            asyncio.run(engagement_callback(phase="post_posting", duration_minutes=30))
            
            # Session completed
            session_end = datetime.now(self.timezone)
            logger.info(f"Automation session completed at {session_end}")
            
            if self.current_session:
                self.current_session['status'] = 'completed'
                self.current_session['end_time'] = session_end
                self.current_session['duration'] = (session_end - session_start).total_seconds()
            
            # Call session end callback if provided
            if session_end_callback:
                asyncio.run(session_end_callback(self.current_session))
                
        except Exception as e:
            logger.error(f"Error during automation session: {e}")
            if self.current_session:
                self.current_session['status'] = 'error'
                self.current_session['error'] = str(e)
    
    def start_scheduler(self):
        """Start the scheduler in a background thread"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        
        def run_scheduler():
            logger.info("LinkedIn automation scheduler started")
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            logger.info("LinkedIn automation scheduler stopped")
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Scheduler thread started")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Scheduler stopped")
    
    def get_next_run_time(self) -> Optional[datetime]:
        """Get the next scheduled run time"""
        jobs = schedule.jobs
        if not jobs:
            return None
        
        next_run = min(job.next_run for job in jobs)
        return next_run
    
    def get_current_session_status(self) -> Optional[dict]:
        """Get the status of the current session"""
        return self.current_session
    
    def is_session_active(self) -> bool:
        """Check if a session is currently active"""
        if not self.current_session:
            return False
        
        return self.current_session.get('status') == 'running'
    
    def schedule_one_time_task(self, 
                              task_callback: Callable,
                              run_time: datetime,
                              task_name: str = "one_time_task"):
        """
        Schedule a one-time task
        
        Args:
            task_callback: Function to call
            run_time: When to run the task
            task_name: Name for logging
        """
        
        def run_task():
            try:
                logger.info(f"Running one-time task: {task_name}")
                asyncio.run(task_callback())
                logger.info(f"Completed one-time task: {task_name}")
            except Exception as e:
                logger.error(f"Error in one-time task {task_name}: {e}")
            
            # Remove the job after execution
            return schedule.CancelJob
        
        # Schedule the task
        schedule.every().day.at(run_time.strftime("%H:%M")).do(run_task)
        logger.info(f"Scheduled one-time task '{task_name}' for {run_time}")
    
    def get_schedule_info(self) -> dict:
        """Get information about scheduled jobs"""
        jobs_info = []
        
        for job in schedule.jobs:
            jobs_info.append({
                'job': str(job.job_func),
                'next_run': job.next_run,
                'interval': job.interval,
                'unit': job.unit
            })
        
        return {
            'total_jobs': len(schedule.jobs),
            'jobs': jobs_info,
            'next_run': self.get_next_run_time(),
            'scheduler_running': self.is_running,
            'current_session': self.current_session
        }
    
    def clear_schedule(self):
        """Clear all scheduled jobs"""
        schedule.clear()
        logger.info("All scheduled jobs cleared")
    
    def is_business_hours(self) -> bool:
        """Check if current time is within business hours (9 AM - 6 PM)"""
        current_time = datetime.now(self.timezone)
        return 9 <= current_time.hour < 18
    
    def time_until_next_session(self) -> Optional[timedelta]:
        """Calculate time until next automation session"""
        next_run = self.get_next_run_time()
        if not next_run:
            return None
        
        current_time = datetime.now(self.timezone)
        # Convert next_run to timezone-aware datetime if it isn't already
        if next_run.tzinfo is None:
            next_run = self.timezone.localize(next_run)
        
        return next_run - current_time