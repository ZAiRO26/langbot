"""
Debug LinkedIn Authentication
Tests the LinkedIn connection and identifies authentication issues
"""

import sys
import logging
from linkedin_api import Linkedin
from config import settings

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_linkedin_auth():
    """Test LinkedIn authentication with detailed debugging"""
    
    print("🔍 LinkedIn Authentication Debug")
    print("="*50)
    
    # Check credentials
    print(f"📧 Username: {settings.linkedin_username}")
    print(f"🔑 Password: {'*' * len(settings.linkedin_password) if settings.linkedin_password else 'NOT SET'}")
    
    if not settings.linkedin_username or not settings.linkedin_password:
        print("❌ LinkedIn credentials not found in .env file")
        return False
    
    try:
        print("\n🔄 Attempting LinkedIn connection...")
        
        # Initialize LinkedIn API
        api = Linkedin(
            username=settings.linkedin_username,
            password=settings.linkedin_password,
            debug=True  # Enable debug mode
        )
        
        print("✅ LinkedIn API initialized")
        
        # Test profile access
        print("🔄 Testing profile access...")
        profile = api.get_profile()
        
        print("✅ Profile retrieved successfully!")
        print(f"👤 Name: {profile.get('firstName', 'Unknown')} {profile.get('lastName', '')}")
        print(f"🏢 Headline: {profile.get('headline', 'No headline')}")
        
        # Test posting capability
        print("\n🔄 Testing posting capability...")
        
        # Try to get user URN (required for posting)
        user_urn = api.get_user_profile()
        print(f"🆔 User URN: {user_urn.get('entityUrn', 'Not found')}")
        
        print("\n🎉 All tests passed! LinkedIn is ready for posting.")
        return True
        
    except Exception as e:
        print(f"\n❌ LinkedIn authentication failed: {str(e)}")
        
        # Detailed error analysis
        error_str = str(e).lower()
        
        if "challenge" in error_str:
            print("\n🔐 CHALLENGE ERROR DETECTED")
            print("💡 Solutions:")
            print("   1. Open LinkedIn in your browser")
            print("   2. Log in manually with your credentials")
            print("   3. Complete any security challenges")
            print("   4. Wait 10-15 minutes and try again")
            
        elif "credentials" in error_str or "login" in error_str:
            print("\n🔑 CREDENTIAL ERROR")
            print("💡 Check:")
            print("   - Username/email is correct")
            print("   - Password is correct")
            print("   - No typos in .env file")
            
        elif "rate" in error_str or "limit" in error_str:
            print("\n⏰ RATE LIMIT ERROR")
            print("💡 Wait 1 hour and try again")
            
        else:
            print(f"\n🔍 UNKNOWN ERROR: {str(e)}")
            print("💡 Try:")
            print("   - Check internet connection")
            print("   - Verify LinkedIn is accessible")
            print("   - Try again in a few minutes")
        
        return False

if __name__ == "__main__":
    success = test_linkedin_auth()
    sys.exit(0 if success else 1)