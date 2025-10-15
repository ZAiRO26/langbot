import requests
import json
import asyncio
from typing import Optional, List
from config import settings
import logging

logger = logging.getLogger(__name__)

class LinkedInOfficialClient:
    """
    Official LinkedIn API v2 client for posting content
    """
    
    def __init__(self, access_token: str):
        """
        Initialize the LinkedIn Official API client
        
        Args:
            access_token: OAuth 2.0 access token for LinkedIn API
        """
        self.access_token = access_token
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
    
    async def get_user_info(self) -> dict:
        """
        Get current user's profile information
        
        Returns:
            dict: User profile information
        """
        try:
            # Try OIDC userinfo first (works with openid/profile/email)
            userinfo_url = f"{self.base_url}/userinfo"
            response = requests.get(userinfo_url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                # Normalize to match /me style fields
                normalized = {
                    "id": data.get("sub"),
                    "localizedFirstName": data.get("given_name"),
                    "localizedLastName": data.get("family_name"),
                    "profilePicture": data.get("picture"),
                    "email": data.get("email")
                }
                return normalized
            else:
                # Fallback to legacy /me which needs r_liteprofile
                me_url = f"{self.base_url}/me"
                response2 = requests.get(me_url, headers=self.headers)

                if response2.status_code == 200:
                    return response2.json()
                else:
                    logger.error(
                        f"Failed to get user info: {response.status_code} - {response.text}; "
                        f"fallback /me: {response2.status_code} - {response2.text}"
                    )
                    return {}
                
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {}
    
    async def post_content(self, content: str, visibility: str = "PUBLIC") -> bool:
        """
        Post content to LinkedIn using official API v2
        
        Args:
            content: The text content to post
            visibility: Post visibility (PUBLIC, CONNECTIONS, LOGGED_IN_MEMBERS)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # First get user info to get the person URN
            user_info = await self.get_user_info()
            if not user_info or 'id' not in user_info:
                logger.error("Could not get user ID for posting")
                return False

            person_urn = f"urn:li:person:{user_info['id']}"

            # Prepare the post data
            post_data = {
                "author": person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": content},
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": visibility}
            }

            # Make the API call
            url = f"{self.base_url}/ugcPosts"
            response = requests.post(url, headers=self.headers, json=post_data)

            if response.status_code == 201:
                logger.info("Successfully posted to LinkedIn")
                post_response = response.json()
                logger.info(f"Post ID: {post_response.get('id', 'Unknown')}")
                return True
            else:
                logger.error(f"Failed to post to LinkedIn: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {e}")
            return False

    def _register_image_upload(self, owner_urn: str) -> Optional[dict]:
        """Register an image upload and return asset + uploadUrl."""
        try:
            url = f"{self.base_url}/assets?action=registerUpload"
            payload = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": owner_urn,
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }
            resp = requests.post(url, headers=self.headers, json=payload)
            if resp.status_code == 200:
                return resp.json().get("value")
            else:
                logger.error(f"Register upload failed: {resp.status_code} - {resp.text}")
                return None
        except Exception as e:
            logger.error(f"Register upload error: {e}")
            return None

    def _upload_image_bytes(self, upload_url: str, image_bytes: bytes, content_type: str = "image/jpeg") -> bool:
        """Upload raw image bytes to LinkedIn's upload URL."""
        try:
            headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": content_type}
            resp = requests.put(upload_url, data=image_bytes, headers=headers)
            return 200 <= resp.status_code < 300
        except Exception as e:
            logger.error(f"Upload image error: {e}")
            return False

    async def post_content_with_images(self, content: str, image_urls: List[str], visibility: str = "PUBLIC") -> bool:
        """
        Post content with one or more images.
        """
        try:
            # Get author
            user_info = await self.get_user_info()
            if not user_info or 'id' not in user_info:
                logger.error("Could not get user ID for posting")
                return False
            owner_urn = f"urn:li:person:{user_info['id']}"

            # Upload each image and collect asset URNs
            media_assets = []
            for idx, url in enumerate(image_urls):
                reg = self._register_image_upload(owner_urn)
                if not reg:
                    return False
                asset_urn = reg.get("asset")
                upload_mech = reg.get("uploadMechanism", {})
                http_req = upload_mech.get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {})
                upload_url = http_req.get("uploadUrl")

                # Download image
                img_resp = requests.get(url, timeout=30)
                if img_resp.status_code != 200:
                    logger.error(f"Failed to download image: {url} - {img_resp.status_code}")
                    return False

                # Heuristic content type
                ctype = img_resp.headers.get("Content-Type", "image/jpeg")
                ok = self._upload_image_bytes(upload_url, img_resp.content, content_type=ctype)
                if not ok:
                    logger.error("Image upload failed")
                    return False

                media_assets.append({
                    "status": "READY",
                    "description": {"text": ""},
                    "media": asset_urn,
                    "title": {"text": f"Image {idx+1}"}
                })

            # Build post payload with images
            post_payload = {
                "author": owner_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": content},
                        "shareMediaCategory": "IMAGE",
                        "media": media_assets
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": visibility}
            }

            post_url = f"{self.base_url}/ugcPosts"
            response = requests.post(post_url, headers=self.headers, json=post_payload)
            if response.status_code == 201:
                logger.info("Successfully posted to LinkedIn with images")
                return True
            else:
                logger.error(f"Failed to post with images: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error posting with images: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """
        Test the LinkedIn API connection
        
        Returns:
            bool: True if connection is successful
        """
        try:
            user_info = await self.get_user_info()
            if user_info and 'id' in user_info:
                logger.info(f"LinkedIn API connection successful. User ID: {user_info['id']}")
                return True
            else:
                logger.error("LinkedIn API connection failed")
                return False
        except Exception as e:
            logger.error(f"Error testing LinkedIn connection: {e}")
            return False


# For testing purposes - you'll need to get an access token
async def test_official_linkedin():
    """
    Test function for the official LinkedIn API
    Note: You need a valid access token to use this
    """
    # Load access token saved by the OAuth flow
    try:
        with open("linkedin_token.json", "r") as f:
            token_json = json.load(f)
            access_token = token_json.get("access_token")
    except Exception:
        access_token = None
    
    if not access_token:
        print("❌ No access token provided. You need to implement OAuth flow first.")
        print("📖 Please follow the LinkedIn API documentation to get an access token:")
        print("   https://docs.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow")
        return False
    
    client = LinkedInOfficialClient(access_token)

    # Test connection
    if await client.test_connection():
        print("✅ LinkedIn API connection successful!")

        # Short sanity post
        test_content = "Hello from the LinkedIn Automation Agent!"
        success = await client.post_content(test_content)
        if success:
            print("✅ Test post successful!")
            return True
        else:
            print("❌ Test post failed!")
            return False
    else:
        print("❌ LinkedIn API connection failed!")
        return False

if __name__ == "__main__":
    asyncio.run(test_official_linkedin())