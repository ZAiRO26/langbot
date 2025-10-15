"""
Test script to generate a custom LinkedIn post about global warming
with connection tagging for testing purposes
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

async def generate_custom_post():
    """Generate a custom post about global warming with connection tagging"""
    
    # Initialize Ollama client
    ollama_client = OllamaOpenAIClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model
    )
    
    # Test connection first
    if not ollama_client.test_connection():
        print("❌ Ollama connection failed. Make sure Ollama is running.")
        return None
    
    print("✅ Ollama connection successful")
    
    # Custom prompt for global warming post with connection tagging
    system_prompt = """You are a LinkedIn content expert. Create an engaging, professional LinkedIn post about global warming that:
    - Is 200-350 words long
    - Has a compelling hook in the first line
    - Discusses the global warming issue and actionable solutions
    - Mentions environmental-friendly products and their benefits
    - Includes a section thanking a connection for insights on eco-friendly products
    - Uses professional but passionate tone
    - Includes relevant hashtags (4-6)
    - Ends with a call-to-action question to encourage engagement
    - Leaves space for @mention tagging (use placeholder @[Connection Name])"""
    
    user_prompt = """Create a LinkedIn post about global warming and environmental solutions. 
    
    The post should:
    1. Start with an attention-grabbing statement about climate change
    2. Discuss what we should do to rectify global warming
    3. Highlight the importance of using environmentally friendly products
    4. Include a thank you section to a connection who helped understand the benefits of eco-friendly products
    5. End with an engaging question about sustainability practices
    
    Use @[Connection Name] as a placeholder for tagging a connection who provided insights on environmental products."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        print("🔄 Generating custom LinkedIn post about global warming...")
        post_content = ollama_client.chat_complete(messages, temperature=0.8)
        
        # Replace placeholder with actual connection
        connection_name = "Abhinav Nigam"  # From the LinkedIn URL provided
        post_content = post_content.replace("@[Connection Name]", f"@{connection_name}")
        
        print("\n" + "="*60)
        print("📝 GENERATED LINKEDIN POST:")
        print("="*60)
        print(post_content)
        print("="*60)
        
        return post_content
        
    except Exception as e:
        logger.error(f"Failed to generate post: {str(e)}")
        return None

async def test_linkedin_posting(post_content):
    """Test posting to LinkedIn (optional)"""
    
    try:
        # Initialize LinkedIn client
        linkedin_client = LinkedInClient()
        
        print("\n🔄 Testing LinkedIn connection...")
        
        # Get profile info to test connection
        profile = linkedin_client.get_profile_info()
        if profile:
            print(f"✅ LinkedIn connected as: {profile.get('name', 'Unknown')}")
            
            # Ask user if they want to actually post
            response = input("\n❓ Do you want to post this to LinkedIn? (y/N): ").strip().lower()
            
            if response == 'y':
                print("🔄 Posting to LinkedIn...")
                success = await linkedin_client.post_content(post_content)
                
                if success:
                    print("✅ Post published successfully to LinkedIn!")
                else:
                    print("❌ Failed to publish post to LinkedIn")
            else:
                print("ℹ️  Post generation completed. Not posted to LinkedIn.")
        else:
            print("❌ LinkedIn connection failed. Check your credentials.")
            
    except Exception as e:
        logger.error(f"LinkedIn testing error: {str(e)}")
        print(f"❌ LinkedIn error: {str(e)}")

async def main():
    """Main function to run the custom post test"""
    
    print("🌍 LinkedIn Global Warming Post Generator")
    print("="*50)
    
    # Generate the post
    post_content = await generate_custom_post()
    
    if post_content:
        print("\n✅ Post generated successfully!")
        
        # Ask if user wants to test LinkedIn posting
        test_linkedin = input("\n❓ Do you want to test LinkedIn posting? (y/N): ").strip().lower()
        
        if test_linkedin == 'y':
            await test_linkedin_posting(post_content)
        else:
            print("\nℹ️  Post generation completed. Ready for manual posting or integration.")
            print("\n📋 Connection to tag:")
            print("   Name: Abhinav Nigam")
            print("   URL: https://www.linkedin.com/in/abhinavnigam2207/")
    else:
        print("❌ Failed to generate post")

if __name__ == "__main__":
    asyncio.run(main())