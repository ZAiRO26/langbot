import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import List

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Configuration settings for LinkedIn Automation Agent"""
    
    # LinkedIn API Settings (Option A - Developer API)
    linkedin_client_id: str = os.getenv("LINKEDIN_CLIENT_ID", "")
    linkedin_client_secret: str = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    linkedin_access_token: str = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    linkedin_user_id: str = os.getenv("LINKEDIN_USER_ID", "")
    
    # LinkedIn Direct Settings (Option B - Direct credentials)
    linkedin_username: str = os.getenv("LINKEDIN_USERNAME", "")
    linkedin_password: str = os.getenv("LINKEDIN_PASSWORD", "")
    
    # Ollama Settings (Local LLM)
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "mistral:7b-instruct-v0.3-q4_0")
    
    # Scheduling Settings
    post_days: List[str] = ["wednesday", "saturday"]
    post_time: str = "09:30"
    engagement_start_time: str = "09:00"
    engagement_end_time: str = "10:00"
    timezone: str = os.getenv("TIMEZONE", "UTC")
    
    # Engagement Settings
    top_connections_count: int = 50
    posts_lookback_days: int = 7
    max_comments_per_session: int = 25
    min_delay_between_actions: int = 30  # seconds
    max_delay_between_actions: int = 120  # seconds
    
    # Content settings - will be loaded from topics_config.py
    weekly_topics: List[str] = []
    
    # Logging Settings
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = "linkedin_automation.log"
    
    # Rate Limiting
    linkedin_api_rate_limit: int = 100  # requests per hour
    ollama_rate_limit: int = 600  # requests per hour (local, more generous)
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

def update_weekly_topics(topics: List[str]) -> None:
    """Update weekly topics in settings"""
    global settings
    settings.weekly_topics = topics

def load_weekly_topics() -> List[str]:
    """Load weekly topics from topics_config module"""
    try:
        from topics_config import get_current_topics
        topics = get_current_topics()
        settings.weekly_topics = topics
        return topics
    except ImportError:
        logger.warning("topics_config module not found, using default topics")
        return []
    except Exception as e:
        logger.error(f"Error loading weekly topics: {e}")
        return []
    
def validate_config():
    """Validate the configuration settings"""
    
    # Load weekly topics
    load_weekly_topics()
    
    # Validate LinkedIn credentials (either API or direct)
    has_api_creds = all([
        os.getenv('LINKEDIN_CLIENT_ID'),
        os.getenv('LINKEDIN_CLIENT_SECRET'),
        os.getenv('LINKEDIN_ACCESS_TOKEN'),
        os.getenv('LINKEDIN_USER_ID')
    ])
    
    has_direct_creds = all([
        os.getenv('LINKEDIN_USERNAME'),
        os.getenv('LINKEDIN_PASSWORD')
    ])
    
    if not (has_api_creds or has_direct_creds):
        raise ValueError("Missing LinkedIn credentials. Provide either API credentials (CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, USER_ID) or direct credentials (USERNAME, PASSWORD)")
    
    # Validate Ollama settings (optional, will use defaults if not provided)
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1')
    ollama_model = os.getenv('OLLAMA_MODEL', 'mistral:7b-instruct-v0.3-q4_0')
    
    # Validate time settings
    try:
        from datetime import datetime
        datetime.strptime(settings.post_time, "%H:%M")
    except ValueError as e:
        raise ValueError(f"Invalid time format in settings: {e}")
    
    # Validate topics
    if not settings.weekly_topics:
        print("Warning: No weekly topics configured. Please set topics using topics_config.py")
    
    print("Configuration validation completed successfully")
    
    return True