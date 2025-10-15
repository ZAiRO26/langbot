import asyncio
from linkedin_api import Linkedin
from config import settings

async def check_linkedin_api_methods():
    """Check what methods are available in the LinkedIn API object"""
    try:
        print("Initializing LinkedIn API...")
        api = Linkedin(settings.linkedin_username, settings.linkedin_password)
        
        print("\nAvailable methods in LinkedIn API object:")
        methods = [method for method in dir(api) if not method.startswith('_')]
        for method in sorted(methods):
            print(f"  - {method}")
        
        # Check specifically for posting methods
        posting_methods = [method for method in methods if 'post' in method.lower() or 'share' in method.lower() or 'submit' in method.lower()]
        print(f"\nPosting-related methods found: {posting_methods}")
        
        # Try to find the correct method for posting
        if hasattr(api, 'submit_share'):
            print("\n✓ Found submit_share method")
        if hasattr(api, 'post'):
            print("✓ Found post method")
        if hasattr(api, 'share_update'):
            print("✓ Found share_update method")
        
        return True
        
    except Exception as e:
        print(f"Error checking API methods: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(check_linkedin_api_methods())