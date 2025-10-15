#!/usr/bin/env python3
"""
Weekly Topics Configuration

This module provides an easy way to manage and update the weekly topics
used for LinkedIn content generation. Users can modify this file to set
their topics for each week.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Default topics for demonstration
DEFAULT_TOPICS = [
    "Artificial Intelligence and Machine Learning trends",
    "Digital transformation in business",
    "Remote work productivity tips",
    "Leadership and team management",
    "Industry insights and market analysis"
]

class TopicsManager:
    """Manages weekly topics for LinkedIn content generation"""
    
    def __init__(self, config_file: str = "weekly_topics.json"):
        self.config_file = config_file
        self.topics_data = self._load_topics()
    
    def _load_topics(self) -> Dict:
        """Load topics from configuration file"""
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading topics file: {e}")
                return self._create_default_config()
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default topics configuration"""
        
        current_week = self._get_current_week()
        
        config = {
            "current_week": current_week,
            "topics_history": {},
            "current_topics": DEFAULT_TOPICS.copy(),
            "last_updated": datetime.now().isoformat(),
            "auto_rotate": False,  # Set to True to automatically rotate topics
            "topic_pool": [
                # Business & Leadership
                "Leadership strategies for remote teams",
                "Building company culture in digital age",
                "Entrepreneurship lessons learned",
                "Business innovation and disruption",
                "Strategic planning and execution",
                
                # Technology & AI
                "Artificial Intelligence in business applications",
                "Cybersecurity best practices",
                "Cloud computing transformation",
                "Data analytics and insights",
                "Automation and workflow optimization",
                
                # Professional Development
                "Career growth and skill development",
                "Networking strategies for professionals",
                "Personal branding on LinkedIn",
                "Work-life balance techniques",
                "Continuous learning and adaptation",
                
                # Industry Trends
                "Digital marketing evolution",
                "Sustainable business practices",
                "Future of work predictions",
                "Customer experience innovation",
                "Market trends and analysis",
                
                # Productivity & Efficiency
                "Time management strategies",
                "Project management best practices",
                "Team collaboration tools",
                "Meeting efficiency tips",
                "Goal setting and achievement"
            ]
        }
        
        self._save_topics(config)
        return config
    
    def _save_topics(self, data: Dict) -> None:
        """Save topics to configuration file"""
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving topics file: {e}")
    
    def _get_current_week(self) -> str:
        """Get current week identifier (YYYY-WW format)"""
        
        now = datetime.now()
        year, week, _ = now.isocalendar()
        return f"{year}-W{week:02d}"
    
    def get_current_topics(self) -> List[str]:
        """Get current week's topics"""
        
        current_week = self._get_current_week()
        
        # Check if we need to update for new week
        if current_week != self.topics_data.get("current_week"):
            self._handle_new_week(current_week)
        
        return self.topics_data.get("current_topics", DEFAULT_TOPICS.copy())
    
    def set_topics(self, topics: List[str]) -> bool:
        """Set topics for current week"""
        
        if not topics or len(topics) < 3:
            print("Error: At least 3 topics are required")
            return False
        
        if len(topics) > 10:
            print("Warning: More than 10 topics provided, using first 10")
            topics = topics[:10]
        
        current_week = self._get_current_week()
        
        # Save current topics to history
        if self.topics_data.get("current_topics"):
            self.topics_data["topics_history"][self.topics_data.get("current_week", current_week)] = \
                self.topics_data["current_topics"]
        
        # Update current topics
        self.topics_data["current_week"] = current_week
        self.topics_data["current_topics"] = topics
        self.topics_data["last_updated"] = datetime.now().isoformat()
        
        self._save_topics(self.topics_data)
        
        print(f"Topics updated for week {current_week}:")
        for i, topic in enumerate(topics, 1):
            print(f"  {i}. {topic}")
        
        return True
    
    def add_topic(self, topic: str) -> bool:
        """Add a single topic to current week"""
        
        current_topics = self.get_current_topics()
        
        if topic in current_topics:
            print(f"Topic '{topic}' already exists")
            return False
        
        if len(current_topics) >= 10:
            print("Maximum of 10 topics allowed")
            return False
        
        current_topics.append(topic)
        return self.set_topics(current_topics)
    
    def remove_topic(self, topic: str) -> bool:
        """Remove a topic from current week"""
        
        current_topics = self.get_current_topics()
        
        if topic not in current_topics:
            print(f"Topic '{topic}' not found")
            return False
        
        if len(current_topics) <= 3:
            print("Cannot remove topic: minimum of 3 topics required")
            return False
        
        current_topics.remove(topic)
        return self.set_topics(current_topics)
    
    def get_random_topics(self, count: int = 5) -> List[str]:
        """Get random topics from the topic pool"""
        
        import random
        
        topic_pool = self.topics_data.get("topic_pool", [])
        
        if len(topic_pool) < count:
            print(f"Warning: Topic pool has only {len(topic_pool)} topics, requested {count}")
            return topic_pool.copy()
        
        return random.sample(topic_pool, count)
    
    def _handle_new_week(self, new_week: str) -> None:
        """Handle transition to new week"""
        
        old_week = self.topics_data.get("current_week")
        
        # Save previous week's topics to history
        if old_week and self.topics_data.get("current_topics"):
            self.topics_data["topics_history"][old_week] = self.topics_data["current_topics"]
        
        # Auto-rotate topics if enabled
        if self.topics_data.get("auto_rotate", False):
            new_topics = self.get_random_topics(5)
            self.topics_data["current_topics"] = new_topics
            print(f"Auto-rotated to new topics for week {new_week}")
        
        self.topics_data["current_week"] = new_week
        self.topics_data["last_updated"] = datetime.now().isoformat()
        
        self._save_topics(self.topics_data)
    
    def get_topics_history(self) -> Dict[str, List[str]]:
        """Get history of topics by week"""
        
        return self.topics_data.get("topics_history", {})
    
    def enable_auto_rotation(self, enabled: bool = True) -> None:
        """Enable or disable automatic topic rotation"""
        
        self.topics_data["auto_rotate"] = enabled
        self.topics_data["last_updated"] = datetime.now().isoformat()
        self._save_topics(self.topics_data)
        
        status = "enabled" if enabled else "disabled"
        print(f"Auto-rotation {status}")
    
    def get_status(self) -> Dict:
        """Get current status of topics configuration"""
        
        current_week = self._get_current_week()
        current_topics = self.get_current_topics()
        
        return {
            "current_week": current_week,
            "topics_count": len(current_topics),
            "current_topics": current_topics,
            "last_updated": self.topics_data.get("last_updated"),
            "auto_rotate": self.topics_data.get("auto_rotate", False),
            "topic_pool_size": len(self.topics_data.get("topic_pool", [])),
            "weeks_in_history": len(self.topics_data.get("topics_history", {}))
        }

# Global instance for easy access
topics_manager = TopicsManager()

def get_current_topics() -> List[str]:
    """Convenience function to get current topics"""
    return topics_manager.get_current_topics()

def update_topics(topics: List[str]) -> bool:
    """Convenience function to update topics"""
    return topics_manager.set_topics(topics)

def add_topic(topic: str) -> bool:
    """Convenience function to add a topic"""
    return topics_manager.add_topic(topic)

def remove_topic(topic: str) -> bool:
    """Convenience function to remove a topic"""
    return topics_manager.remove_topic(topic)

def get_topics_status() -> Dict:
    """Convenience function to get topics status"""
    return topics_manager.get_status()

# CLI interface for easy topic management
if __name__ == "__main__":
    import sys
    
    def print_help():
        print("""
LinkedIn Topics Manager

Usage:
    python topics_config.py [command] [arguments]

Commands:
    list                    - Show current topics
    set <topic1> <topic2>   - Set new topics (space-separated)
    add <topic>             - Add a single topic
    remove <topic>          - Remove a topic
    random [count]          - Get random topics from pool
    status                  - Show configuration status
    history                 - Show topics history
    auto-rotate [on|off]    - Enable/disable auto-rotation
    help                    - Show this help message

Examples:
    python topics_config.py list
    python topics_config.py set "AI trends" "Remote work" "Leadership"
    python topics_config.py add "Digital marketing"
    python topics_config.py random 5
    python topics_config.py auto-rotate on
        """)
    
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "list":
        topics = get_current_topics()
        print(f"Current topics for week {topics_manager._get_current_week()}:")
        for i, topic in enumerate(topics, 1):
            print(f"  {i}. {topic}")
    
    elif command == "set":
        if len(sys.argv) < 3:
            print("Error: Please provide topics to set")
            sys.exit(1)
        
        topics = sys.argv[2:]
        if update_topics(topics):
            print("Topics updated successfully!")
        else:
            print("Failed to update topics")
    
    elif command == "add":
        if len(sys.argv) < 3:
            print("Error: Please provide a topic to add")
            sys.exit(1)
        
        topic = " ".join(sys.argv[2:])
        if add_topic(topic):
            print(f"Topic '{topic}' added successfully!")
        else:
            print("Failed to add topic")
    
    elif command == "remove":
        if len(sys.argv) < 3:
            print("Error: Please provide a topic to remove")
            sys.exit(1)
        
        topic = " ".join(sys.argv[2:])
        if remove_topic(topic):
            print(f"Topic '{topic}' removed successfully!")
        else:
            print("Failed to remove topic")
    
    elif command == "random":
        count = 5
        if len(sys.argv) > 2:
            try:
                count = int(sys.argv[2])
            except ValueError:
                print("Error: Count must be a number")
                sys.exit(1)
        
        random_topics = topics_manager.get_random_topics(count)
        print(f"Random topics from pool ({count}):")
        for i, topic in enumerate(random_topics, 1):
            print(f"  {i}. {topic}")
    
    elif command == "status":
        status = get_topics_status()
        print("Topics Configuration Status:")
        print(f"  Current Week: {status['current_week']}")
        print(f"  Topics Count: {status['topics_count']}")
        print(f"  Last Updated: {status['last_updated']}")
        print(f"  Auto-Rotate: {status['auto_rotate']}")
        print(f"  Topic Pool Size: {status['topic_pool_size']}")
        print(f"  History Weeks: {status['weeks_in_history']}")
    
    elif command == "history":
        history = topics_manager.get_topics_history()
        if not history:
            print("No topics history available")
        else:
            print("Topics History:")
            for week, topics in sorted(history.items()):
                print(f"\n  Week {week}:")
                for i, topic in enumerate(topics, 1):
                    print(f"    {i}. {topic}")
    
    elif command == "auto-rotate":
        if len(sys.argv) < 3:
            status = topics_manager.topics_data.get("auto_rotate", False)
            print(f"Auto-rotation is currently {'enabled' if status else 'disabled'}")
        else:
            enable = sys.argv[2].lower() in ['on', 'true', 'yes', '1']
            topics_manager.enable_auto_rotation(enable)
    
    elif command == "help":
        print_help()
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'python topics_config.py help' for usage information")
        sys.exit(1)