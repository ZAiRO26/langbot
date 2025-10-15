"""
Direct LinkedIn Posting Script
Posts the generated global warming content with connection tagging
"""

import asyncio
import sys
import os
from ollama_client import OllamaOpenAIClient
from linkedin_client import LinkedInClient
from config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def post_to_linkedin():
    """Generate and post the global warming content to LinkedIn"""
    
    print("🌍 LinkedIn Global Warming Post - DIRECT POSTING")
    print("="*60)
    
    # Initialize Ollama client
    print("🔄 Initializing Ollama AI...")
    ollama_client = OllamaOpenAIClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model
    )
    
    # Test Ollama connection
    if not ollama_client.test_connection():
        print("❌ Ollama connection failed. Make sure Ollama is running.")
        return False
    
    print("✅ Ollama connected successfully")
    
    # Generate the post content
    print("🔄 Generating LinkedIn post about global warming...")
    
    system_prompt = """You are a LinkedIn content expert. Create an engaging, professional LinkedIn post about global warming that:
    - Is 200-350 words long
    - Has a compelling hook in the first line
    - Discusses the global warming issue and actionable solutions
    - Mentions environmental-friendly products and their benefits
    - Includes a section thanking a connection for insights on eco-friendly products
    - Uses professional but passionate tone
    - Includes relevant hashtags (4-6)
    - Ends with a call-to-action question to encourage engagement
    - Uses @Abhinav Nigam for tagging the connection"""
    
    user_prompt = """Create a LinkedIn post about global warming and environmental solutions. 
    
    The post should:
    1. Start with an attention-grabbing statement about climate change
    2. Discuss what we should do to rectify global warming
    3. Highlight the importance of using environmentally friendly products
    4. Include a thank you section to @Abhinav Nigam who helped understand the benefits of eco-friendly products
    5. End with an engaging question about sustainability practices
    
    Make it professional, engaging, and actionable."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        post_content = ollama_client.chat_complete(messages, temperature=0.8)
        
        print("\n" + "="*60)
        print("📝 GENERATED POST CONTENT:")
        print("="*60)
        print(post_content)
        print("="*60)
        
    except Exception as e:
        logger.error(f"Failed to generate post: {str(e)}")
        print(f"❌ Post generation failed: {str(e)}")
        return False
    
    # Initialize LinkedIn client and post
    print("\n🔄 Connecting to LinkedIn...")
    
    try:
        linkedin_client = LinkedInClient()
        
        # Test connection by getting profile
        print("🔄 Verifying LinkedIn authentication...")
        profile = linkedin_client.get_profile_info()
        
        if not profile:
            print("❌ LinkedIn authentication failed!")
            print("💡 This might be due to:")
            print("   - Incorrect credentials in .env file")
            print("   - LinkedIn security challenge")
            print("   - Network connectivity issues")
            return False
        
        print(f"✅ LinkedIn authenticated as: {profile.get('firstName', 'Unknown')} {profile.get('lastName', '')}")
        
        # Post the content
        print("\n🚀 Posting to LinkedIn...")
        success = await linkedin_client.post_content(post_content)
        
        if success:
            print("🎉 SUCCESS! Post published to LinkedIn!")
            print("📱 Check your LinkedIn profile to see the post")
            print("🏷️  Connection @Abhinav Nigam should be tagged")
            return True
        else:
            print("❌ Failed to publish post to LinkedIn")
            print("💡 This might be due to:")
            print("   - LinkedIn API rate limits")
            print("   - Content policy restrictions")
            print("   - Network connectivity issues")
            return False
            
    except Exception as e:
        logger.error(f"LinkedIn posting error: {str(e)}")
        print(f"❌ LinkedIn error: {str(e)}")
        
        # Check if it's a CHALLENGE error
        if "CHALLENGE" in str(e).upper():
            print("\n🔐 LinkedIn Security Challenge Detected!")
            print("💡 Solutions:")
            print("   1. Log into LinkedIn manually in your browser")
            print("   2. Complete any security challenges")
            print("   3. Try running the script again")
            print("   4. Consider using LinkedIn Developer API instead")
        
        return False

async def main():
    """Main function"""
    
    success = await post_to_linkedin()
    
    if success:
        print("\n✅ MISSION ACCOMPLISHED!")
        print("🌍 Your global warming post is now live on LinkedIn")
        print("🤝 Abhinav Nigam has been tagged for his eco-friendly insights")
    else:
        print("\n❌ POSTING FAILED")
        print("🔧 Please check the error messages above for troubleshooting")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)