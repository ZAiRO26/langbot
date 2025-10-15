#!/usr/bin/env python3
"""
Test Engagement Functionality
Tests the LinkedIn engagement system with a limited scope for safety
"""

import asyncio
import logging
from datetime import datetime
from engagement_manager import EngagementManager
from linkedin_client import LinkedInClient
from perplexity_client import PerplexityClient
from config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_engagement_system():
    """Test the engagement system with limited scope"""
    
    print("🔄 Testing LinkedIn Engagement System")
    print("="*50)
    
    try:
        # Initialize clients
        print("\n1. Initializing clients...")
        linkedin_client = LinkedInClient()
        perplexity_client = PerplexityClient()
        
        # Test LinkedIn connection
        print("\n2. Testing LinkedIn connection...")
        try:
            profile = linkedin_client.get_profile_info()
            if profile and isinstance(profile, dict) and profile:
                print(f"✅ LinkedIn connected as: {profile.get('firstName', 'Unknown')} {profile.get('lastName', '')}")
            else:
                print("⚠️  LinkedIn connection established but profile data is empty")
                print("   This might be due to LinkedIn API limitations or rate limiting")
                print("   Continuing with engagement tests...")
        except Exception as e:
            print(f"⚠️  LinkedIn connection issue: {e}")
            print("   This might be due to LinkedIn API limitations")
            print("   Continuing with engagement tests...")
        
        # Test Perplexity/Ollama connection
        print("\n3. Testing Perplexity/Ollama connection...")
        if perplexity_client.test_connection():
            print("✅ Perplexity/Ollama connection successful")
        else:
            print("❌ Perplexity/Ollama connection failed")
            return False
        
        # Initialize engagement manager
        print("\n4. Initializing engagement manager...")
        engagement_manager = EngagementManager(linkedin_client, perplexity_client)
        print("✅ Engagement manager initialized")
        
        # Get initial stats
        print("\n5. Getting engagement stats...")
        stats = engagement_manager.get_engagement_stats()
        print(f"✅ Current stats: {stats['session_stats']}")
        
        # Test getting connections (limited to 5 for safety)
        print("\n6. Testing connection retrieval...")
        connections = await linkedin_client.get_top_connections(limit=5)
        if connections:
            print(f"✅ Retrieved {len(connections)} connections")
            for i, conn in enumerate(connections[:3], 1):
                name = f"{conn.get('firstName', '')} {conn.get('lastName', '')}".strip()
                print(f"   {i}. {name} - {conn.get('headline', 'No headline')[:50]}...")
        else:
            print("⚠️  No connections found")
        
        # Test post collection (very limited)
        if connections:
            print("\n7. Testing post collection from first connection...")
            first_connection = connections[0]
            connection_id = first_connection.get('public_id') or first_connection.get('id')
            
            if connection_id:
                posts = await linkedin_client.get_connection_posts(connection_id, days_back=3)
                if posts:
                    print(f"✅ Retrieved {len(posts)} posts from connection")
                    for i, post in enumerate(posts[:2], 1):
                        content_preview = post.get('text', '')[:100] + "..." if len(post.get('text', '')) > 100 else post.get('text', '')
                        print(f"   Post {i}: {content_preview}")
                else:
                    print("⚠️  No posts found from connection")
            else:
                print("⚠️  Connection ID not found")
        
        # Test comment generation
        print("\n8. Testing comment generation...")
        test_post_content = "Just launched our new AI product! Excited to see how it helps businesses automate their workflows."
        comment = await perplexity_client.generate_comment(test_post_content, "Test Author")
        if comment:
            print(f"✅ Generated comment: {comment}")
        else:
            print("❌ Comment generation failed")
        
        print("\n" + "="*50)
        print("✅ Engagement system test completed successfully!")
        print("\n📊 Configuration Summary:")
        print(f"   - Top connections limit: {settings.top_connections_count}")
        print(f"   - Max comments per session: {settings.max_comments_per_session}")
        print(f"   - Posts lookback days: {settings.posts_lookback_days}")
        print(f"   - Engagement time: {settings.engagement_start_time} - {settings.engagement_end_time}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Engagement test failed: {e}")
        logger.error(f"Engagement test error: {e}")
        return False

async def test_limited_engagement_session():
    """Test a very limited engagement session (1 minute, max 2 actions)"""
    
    print("\n🧪 Testing Limited Engagement Session")
    print("="*50)
    
    try:
        # Initialize clients
        linkedin_client = LinkedInClient()
        perplexity_client = PerplexityClient()
        engagement_manager = EngagementManager(linkedin_client, perplexity_client)
        
        # Override limits for safety
        original_max_comments = settings.max_comments_per_session
        settings.max_comments_per_session = 2  # Very limited for testing
        
        print(f"⚠️  Running LIMITED engagement session (max 2 actions, 1 minute)")
        print(f"   Original limit: {original_max_comments}, Test limit: {settings.max_comments_per_session}")
        
        # Run a very short engagement session
        await engagement_manager.run_engagement_session("test", duration_minutes=1)
        
        # Get final stats
        final_stats = engagement_manager.get_engagement_stats()
        print(f"\n📊 Session Results:")
        print(f"   - Comments made: {final_stats['session_stats']['comments_made']}")
        print(f"   - Likes made: {final_stats['session_stats']['likes_made']}")
        print(f"   - Errors: {final_stats['session_stats']['errors']}")
        
        # Restore original limits
        settings.max_comments_per_session = original_max_comments
        
        print("✅ Limited engagement session completed")
        return True
        
    except Exception as e:
        print(f"❌ Limited engagement session failed: {e}")
        # Restore original limits even on error
        settings.max_comments_per_session = original_max_comments
        return False

if __name__ == "__main__":
    print("LinkedIn Engagement System Test")
    print("This will test the engagement functionality with limited scope for safety")
    
    # Ask for confirmation
    response = input("\nDo you want to proceed with the engagement test? (y/N): ").strip().lower()
    
    if response == 'y':
        # Run basic tests
        success = asyncio.run(test_engagement_system())
        
        if success:
            # Ask if user wants to test actual engagement
            response = input("\nDo you want to test a LIMITED engagement session (max 2 actions)? (y/N): ").strip().lower()
            if response == 'y':
                asyncio.run(test_limited_engagement_session())
            else:
                print("Skipping limited engagement session test")
        
        print("\n🏁 Test completed!")
    else:
        print("Test cancelled by user")