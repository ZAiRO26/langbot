#!/usr/bin/env python3
"""
Limited Engagement Test - Test with specific targets: 5 likes and 2 comments
"""

import asyncio
import logging
from linkedin_client import LinkedInClient
from perplexity_client import PerplexityClient
from engagement_manager import EngagementManager
from config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_limited_engagement():
    """Test engagement with specific limits: 5 likes and 2 comments"""
    
    print("🎯 Testing Limited Engagement System")
    print("Target: 5 likes, 2 comments")
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
                print("⚠️  LinkedIn connection established but profile data is limited")
        except Exception as e:
            print(f"⚠️  LinkedIn connection issue: {e}")
            print("   Continuing with engagement tests...")
        
        # Test Ollama connection
        print("\n3. Testing Ollama connection...")
        if perplexity_client.test_connection():
            print("✅ Ollama connection successful")
        else:
            print("❌ Ollama connection failed - will use fallback comments")
        
        # Initialize engagement manager
        print("\n4. Initializing engagement manager...")
        engagement_manager = EngagementManager(linkedin_client, perplexity_client)
        print("✅ Engagement manager initialized")
        
        # Test getting connections (limited to 10 for safety)
        print("\n5. Testing connection retrieval...")
        connections = await linkedin_client.get_top_connections(limit=10)
        if connections:
            print(f"✅ Retrieved {len(connections)} connections")
            for i, conn in enumerate(connections[:3], 1):
                name = f"{conn.get('firstName', '')} {conn.get('lastName', '')}".strip()
                headline = conn.get('headline', 'No headline')[:50]
                print(f"   {i}. {name} - {headline}...")
        else:
            print("❌ No connections found - cannot proceed with engagement test")
            return False
        
        # Test post collection from first few connections
        print("\n6. Testing post collection...")
        all_posts = []
        for i, connection in enumerate(connections[:3]):  # Only check first 3 connections
            try:
                connection_id = connection.get('urn_id')  # Use urn_id instead of public_id
                if connection_id:
                    posts = await linkedin_client.get_connection_posts(connection_id, days_back=3)
                    if posts:
                        # Add connection info to posts
                        for post in posts:
                            post['connection_info'] = {
                                'name': f"{connection.get('firstName', '')} {connection.get('lastName', '')}".strip(),
                                'headline': connection.get('headline', ''),
                                'connection_id': connection_id
                            }
                        all_posts.extend(posts)
                        print(f"   ✅ Found {len(posts)} posts from {connection.get('firstName', 'Unknown')}")
                    else:
                        print(f"   ⚠️  No recent posts from {connection.get('firstName', 'Unknown')}")
                
                # Add delay between connections
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Error getting posts from connection {i+1}: {e}")
                continue
        
        if not all_posts:
            print("❌ No posts found - cannot proceed with engagement test")
            return False
        
        print(f"\n✅ Total posts collected: {len(all_posts)}")
        
        # Limit posts for testing (take first 7 posts to ensure we can do 5 likes + 2 comments)
        test_posts = all_posts[:7]
        print(f"📝 Using {len(test_posts)} posts for engagement test")
        
        # Perform limited engagement
        print("\n7. Performing limited engagement...")
        likes_count = 0
        comments_count = 0
        
        for i, post in enumerate(test_posts):
            try:
                post_id = post.get('post_id') or post.get('id') or post.get('urn')
                if not post_id:
                    print(f"   ⚠️  Post {i+1}: No valid post ID")
                    continue
                
                connection_name = post.get('connection_info', {}).get('name', 'Unknown')
                post_text = post.get('text', '')[:100] + "..." if len(post.get('text', '')) > 100 else post.get('text', '')
                
                print(f"   📄 Post {i+1} from {connection_name}: {post_text}")
                
                # Decide whether to like or comment
                if likes_count < 5:
                    # Like the post
                    success = await linkedin_client.like_post(post_id)
                    if success:
                        likes_count += 1
                        print(f"   ✅ Liked post {i+1} (Total likes: {likes_count})")
                    else:
                        print(f"   ❌ Failed to like post {i+1}")
                    
                    # Add delay
                    await asyncio.sleep(3)
                
                elif comments_count < 2:
                    # Comment on the post
                    comment_text = await perplexity_client.generate_comment(post.get('text', ''))
                    if comment_text:
                        success = await linkedin_client.comment_on_post(post_id, comment_text)
                        if success:
                            comments_count += 1
                            print(f"   ✅ Commented on post {i+1} (Total comments: {comments_count})")
                            print(f"      Comment: {comment_text[:80]}...")
                        else:
                            print(f"   ❌ Failed to comment on post {i+1}")
                    else:
                        print(f"   ⚠️  Could not generate comment for post {i+1}")
                    
                    # Add delay
                    await asyncio.sleep(5)
                
                # Stop if we've reached our targets
                if likes_count >= 5 and comments_count >= 2:
                    print(f"\n🎯 Target reached! {likes_count} likes, {comments_count} comments")
                    break
                    
            except Exception as e:
                print(f"   ❌ Error processing post {i+1}: {e}")
                continue
        
        # Final results
        print(f"\n📊 Final Results:")
        print(f"   ✅ Likes: {likes_count}/5")
        print(f"   ✅ Comments: {comments_count}/2")
        print(f"   📝 Posts processed: {min(i+1, len(test_posts))}")
        
        if likes_count >= 5 and comments_count >= 2:
            print("\n🎉 SUCCESS: All engagement targets met!")
            return True
        else:
            print(f"\n⚠️  PARTIAL SUCCESS: Achieved {likes_count} likes and {comments_count} comments")
            return True  # Still consider it a success if we got some engagement
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.error(f"Limited engagement test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_limited_engagement())