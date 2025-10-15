import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class LinkedInAutomationLogger:
    """Comprehensive logging system for LinkedIn automation"""
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        self.activity_log = []
        self.error_log = []
        self.alerts = []
        
        self._setup_logging()
        self._setup_file_handlers()
    
    def _setup_logging(self):
        """Setup basic logging configuration"""
        
        # Create main logger
        self.logger = logging.getLogger('linkedin_automation')
        self.logger.setLevel(getattr(logging, settings.log_level.upper()))
        
        # Prevent duplicate logs
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / settings.log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def _setup_file_handlers(self):
        """Setup specialized file handlers for different log types"""
        
        # Activity log handler
        self.activity_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "activity.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        activity_formatter = logging.Formatter(
            '%(asctime)s - ACTIVITY - %(message)s'
        )
        self.activity_handler.setFormatter(activity_formatter)
        
        # Error log handler
        self.error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "errors.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_formatter = logging.Formatter(
            '%(asctime)s - ERROR - %(funcName)s:%(lineno)d - %(message)s'
        )
        self.error_handler.setFormatter(error_formatter)
        
        # Performance log handler
        self.performance_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "performance.log",
            maxBytes=2*1024*1024,  # 2MB
            backupCount=2
        )
        performance_formatter = logging.Formatter(
            '%(asctime)s - PERFORMANCE - %(message)s'
        )
        self.performance_handler.setFormatter(performance_formatter)
    
    def log_activity(self, activity_type: str, details: Dict[str, Any], success: bool = True):
        """Log automation activities"""
        
        activity_entry = {
            'timestamp': datetime.now().isoformat(),
            'activity_type': activity_type,
            'success': success,
            'details': details
        }
        
        self.activity_log.append(activity_entry)
        
        # Log to file
        activity_logger = logging.getLogger('activity')
        activity_logger.addHandler(self.activity_handler)
        activity_logger.setLevel(logging.INFO)
        
        log_message = f"{activity_type} - Success: {success} - {json.dumps(details, default=str)}"
        activity_logger.info(log_message)
        
        # Also log to main logger
        if success:
            self.logger.info(f"Activity completed: {activity_type}")
        else:
            self.logger.warning(f"Activity failed: {activity_type}")
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Log errors with context"""
        
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {}
        }
        
        self.error_log.append(error_entry)
        
        # Log to error file
        error_logger = logging.getLogger('errors')
        error_logger.addHandler(self.error_handler)
        error_logger.setLevel(logging.ERROR)
        
        log_message = f"{error_type} - {error_message}"
        if context:
            log_message += f" - Context: {json.dumps(context, default=str)}"
        
        error_logger.error(log_message)
        self.logger.error(log_message)
        
        # Check if this error requires an alert
        self._check_error_alert(error_type, error_message, context)
    
    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """Log performance metrics"""
        
        performance_logger = logging.getLogger('performance')
        performance_logger.addHandler(self.performance_handler)
        performance_logger.setLevel(logging.INFO)
        
        log_message = f"{operation} - Duration: {duration:.2f}s"
        if details:
            log_message += f" - {json.dumps(details, default=str)}"
        
        performance_logger.info(log_message)
        
        # Log slow operations to main logger
        if duration > 30:  # Operations taking more than 30 seconds
            self.logger.warning(f"Slow operation detected: {operation} took {duration:.2f}s")
    
    def _check_error_alert(self, error_type: str, error_message: str, context: Dict[str, Any]):
        """Check if error requires immediate alert"""
        
        critical_errors = [
            'authentication_failed',
            'api_rate_limit_exceeded',
            'linkedin_account_restricted',
            'perplexity_api_error',
            'scheduler_failure'
        ]
        
        if error_type in critical_errors:
            self.create_alert(
                alert_type='critical_error',
                message=f"Critical error: {error_type} - {error_message}",
                context=context
            )
    
    def create_alert(self, alert_type: str, message: str, context: Dict[str, Any] = None):
        """Create an alert for manual attention"""
        
        alert = {
            'timestamp': datetime.now().isoformat(),
            'alert_type': alert_type,
            'message': message,
            'context': context or {},
            'resolved': False
        }
        
        self.alerts.append(alert)
        
        # Log alert
        self.logger.critical(f"ALERT: {alert_type} - {message}")
        
        # Send notification if configured
        self._send_alert_notification(alert)
    
    def _send_alert_notification(self, alert: Dict[str, Any]):
        """Send alert notification (email, webhook, etc.)"""
        
        # This is a placeholder for notification system
        # In a real implementation, you would integrate with:
        # - Email service (SMTP)
        # - Slack webhook
        # - Discord webhook
        # - SMS service
        # - Push notification service
        
        self.logger.info(f"Alert notification would be sent: {alert['alert_type']}")
    
    def log_session_start(self, session_id: str, session_type: str):
        """Log the start of an automation session"""
        
        self.log_activity(
            activity_type='session_start',
            details={
                'session_id': session_id,
                'session_type': session_type,
                'start_time': datetime.now().isoformat()
            }
        )
    
    def log_session_end(self, session_id: str, session_stats: Dict[str, Any]):
        """Log the end of an automation session"""
        
        self.log_activity(
            activity_type='session_end',
            details={
                'session_id': session_id,
                'end_time': datetime.now().isoformat(),
                'stats': session_stats
            }
        )
    
    def log_post_creation(self, post_content: str, success: bool, post_id: str = None):
        """Log LinkedIn post creation"""
        
        self.log_activity(
            activity_type='post_creation',
            details={
                'post_content_length': len(post_content),
                'post_preview': post_content[:100] + '...' if len(post_content) > 100 else post_content,
                'post_id': post_id
            },
            success=success
        )
    
    def log_engagement_activity(self, engagement_type: str, post_id: str, connection_name: str, success: bool):
        """Log engagement activities (comments, likes)"""
        
        self.log_activity(
            activity_type=f'engagement_{engagement_type}',
            details={
                'post_id': post_id,
                'connection_name': connection_name,
                'engagement_type': engagement_type
            },
            success=success
        )
    
    def log_api_call(self, api_name: str, endpoint: str, response_code: int, duration: float):
        """Log API calls for monitoring"""
        
        success = 200 <= response_code < 300
        
        self.log_activity(
            activity_type='api_call',
            details={
                'api_name': api_name,
                'endpoint': endpoint,
                'response_code': response_code,
                'duration': duration
            },
            success=success
        )
        
        # Log performance
        self.log_performance(f"{api_name}_api_call", duration, {
            'endpoint': endpoint,
            'response_code': response_code
        })
    
    def get_recent_activities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent activities"""
        return self.activity_log[-limit:] if self.activity_log else []
    
    def get_recent_errors(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent errors"""
        return self.error_log[-limit:] if self.error_log else []
    
    def get_unresolved_alerts(self) -> List[Dict[str, Any]]:
        """Get unresolved alerts"""
        return [alert for alert in self.alerts if not alert['resolved']]
    
    def resolve_alert(self, alert_index: int):
        """Mark an alert as resolved"""
        if 0 <= alert_index < len(self.alerts):
            self.alerts[alert_index]['resolved'] = True
            self.alerts[alert_index]['resolved_at'] = datetime.now().isoformat()
            self.logger.info(f"Alert resolved: {self.alerts[alert_index]['alert_type']}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        
        recent_errors = len([e for e in self.error_log if 
                           datetime.fromisoformat(e['timestamp']) > 
                           datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)])
        
        unresolved_alerts = len(self.get_unresolved_alerts())
        
        recent_activities = len([a for a in self.activity_log if 
                               datetime.fromisoformat(a['timestamp']) > 
                               datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)])
        
        success_rate = 0
        if recent_activities > 0:
            successful_activities = len([a for a in self.activity_log if 
                                       datetime.fromisoformat(a['timestamp']) > 
                                       datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                                       and a['success']])
            success_rate = (successful_activities / recent_activities) * 100
        
        health_status = "healthy"
        if unresolved_alerts > 0:
            health_status = "critical"
        elif recent_errors > 5:
            health_status = "warning"
        elif success_rate < 80:
            health_status = "warning"
        
        return {
            'status': health_status,
            'recent_errors_today': recent_errors,
            'unresolved_alerts': unresolved_alerts,
            'recent_activities_today': recent_activities,
            'success_rate_today': round(success_rate, 2),
            'last_activity': self.activity_log[-1]['timestamp'] if self.activity_log else None
        }
    
    def export_logs(self, start_date: datetime, end_date: datetime) -> Dict[str, List]:
        """Export logs for a date range"""
        
        filtered_activities = [
            activity for activity in self.activity_log
            if start_date <= datetime.fromisoformat(activity['timestamp']) <= end_date
        ]
        
        filtered_errors = [
            error for error in self.error_log
            if start_date <= datetime.fromisoformat(error['timestamp']) <= end_date
        ]
        
        return {
            'activities': filtered_activities,
            'errors': filtered_errors,
            'export_timestamp': datetime.now().isoformat(),
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }

# Global logger instance
automation_logger = LinkedInAutomationLogger()

# Convenience functions
def log_activity(activity_type: str, details: Dict[str, Any], success: bool = True):
    automation_logger.log_activity(activity_type, details, success)

def log_error(error_type: str, error_message: str, context: Dict[str, Any] = None):
    automation_logger.log_error(error_type, error_message, context)

def log_performance(operation: str, duration: float, details: Dict[str, Any] = None):
    automation_logger.log_performance(operation, duration, details)

def create_alert(alert_type: str, message: str, context: Dict[str, Any] = None):
    automation_logger.create_alert(alert_type, message, context)