"""
Force Post via Main Agent
Uses the main LinkedIn automation agent to post content directly
"""

import asyncio
import sys
from main import LinkedInAutomationAgent
from config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def force_post():
    """Force post using the main agent"""
    
    print("🚀 FORCE POSTING VIA MAIN AGENT")
    print("="*50)
    
    # The exact post content we want to publish
    post_content = """🌍 The clock is ticking on climate change, and the time for half-measures has passed.

Global warming demands urgent, coordinated action across every sector of society. This starts with a fundamental shift towards renewable energy sources like solar and wind, reducing our reliance on fossil fuels. On an individual and corporate level, this means prioritizing energy efficiency, advocating for greener policies, and making conscious choices in our daily consumption. The goal is a circular economy, where waste is minimized, and resources are reused.

A critical part of this shift is the adoption of environmentally friendly products. From biodegradable packaging and plant-based cleaners to energy-efficient appliances, these alternatives significantly lower our carbon footprint. They reduce pollution, conserve natural resources, and often prove more cost-effective in the long run. Embracing them is a direct and powerful action every one of us can take.

I want to extend a special thank you to @Abhinav Nigam for his invaluable insights into the practical benefits and growing market for eco-friendly products. Our conversation reinforced how innovation in this space is not just an environmental imperative but a smart business strategy.

The journey to sustainability is a collective effort. I'm curious to learn from this network: **What is one sustainability practice you've recently adopted in your personal or professional life that has made a significant impact?**

#GlobalWarming #ClimateAction #Sustainability #EcoFriendly #GreenFuture #RenewableEnergy"""
    
    try:
        # Initialize the main agent
        print("🔄 Initializing LinkedIn Automation Agent...")
        agent = LinkedInAutomationAgent()
        
        # Initialize all components
        print("🔄 Setting up agent components...")
        await agent.initialize()
        
        print("✅ Agent initialized successfully")
        
        # Access the LinkedIn client directly
        linkedin_client = agent.linkedin_client
        
        print("🔄 Posting content to LinkedIn...")
        print("\n📝 POST CONTENT:")
        print("-" * 40)
        print(post_content[:200] + "..." if len(post_content) > 200 else post_content)
        print("-" * 40)
        
        # Post the content
        success = await linkedin_client.post_content(post_content)
        
        if success:
            print("\n🎉 SUCCESS! Post published to LinkedIn!")
            print("📱 Check your LinkedIn profile to see the post")
            print("🏷️  @Abhinav Nigam should be tagged in the post")
            return True
        else:
            print("\n❌ Failed to publish post")
            return False
            
    except Exception as e:
        logger.error(f"Force posting error: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        
        # Check for specific error types
        if "CHALLENGE" in str(e).upper():
            print("\n🔐 LinkedIn Security Challenge!")
            print("💡 You need to:")
            print("   1. Open LinkedIn in your browser")
            print("   2. Log in with: ravi.saxena87@gmail.com")
            print("   3. Complete any security verification")
            print("   4. Try posting again in 10-15 minutes")
        
        return False

async def main():
    """Main function"""
    
    print("🌍 POSTING GLOBAL WARMING CONTENT TO LINKEDIN")
    print("Using your credentials: ravi.saxena87@gmail.com")
    print("="*60)
    
    success = await force_post()
    
    if success:
        print("\n✅ MISSION ACCOMPLISHED!")
        print("🌍 Your global warming post is now live!")
        print("🤝 Abhinav Nigam has been tagged!")
    else:
        print("\n❌ POSTING FAILED")
        print("🔧 LinkedIn may require manual verification")
        
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)