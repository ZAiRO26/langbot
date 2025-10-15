import requests
import urllib.parse
import webbrowser
import http.server
import socketserver
import threading
import json
from urllib.parse import urlparse, parse_qs
from config import settings
import logging

logger = logging.getLogger(__name__)

class LinkedInOAuth:
    """
    LinkedIn OAuth 2.0 flow implementation
    """
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = "http://localhost:8083/auth/linkedin/callback"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.authorization_code = None
        self.access_token = None
        self.server = None
        
    def get_authorization_url(self, scopes: list = None) -> str:
        """
        Generate the LinkedIn authorization URL
        
        Args:
            scopes: List of LinkedIn API scopes
            
        Returns:
            str: Authorization URL
        """
        if scopes is None:
            # Use OpenID Connect scopes, plus w_member_social for posting
            # Requires the "Share on LinkedIn" product to be added
            scopes = ["openid", "profile", "email", "w_member_social"]
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": "linkedin_oauth_state",
            "scope": " ".join(scopes)
        }
        
        base_url = "https://www.linkedin.com/oauth/v2/authorization"
        return f"{base_url}?{urllib.parse.urlencode(params)}"
    
    def start_callback_server(self):
        """
        Start a local server to handle the OAuth callback
        """
        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def __init__(self, oauth_instance, *args, **kwargs):
                self.oauth_instance = oauth_instance
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                # Parse request
                parsed_url = urlparse(self.path)
                query_params = parse_qs(parsed_url.query)

                # Accept common callback paths or any request carrying OAuth params
                valid_paths = (
                    '/auth/linkedin/callback',
                    '/linkedin/callback',
                    '/linkedin-openid/callback',
                    '/',
                    ''
                )

                if parsed_url.path in valid_paths or 'code' in query_params or 'error' in query_params:
                    # Validate state if provided
                    state = query_params.get('state', [None])[0]
                    if state is not None and state != 'linkedin_oauth_state':
                        self.send_response(400)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        error_html = """
                        <html>
                        <head><title>LinkedIn OAuth Error</title></head>
                        <body>
                            <h1>❌ Invalid state</h1>
                            <p>The state parameter does not match.</p>
                        </body>
                        </html>
                        """
                        self.wfile.write(error_html.encode())
                        return

                    if 'code' in query_params:
                        self.oauth_instance.authorization_code = query_params['code'][0]

                        # Send success response
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()

                        success_html = """
                        <html>
                        <head><title>LinkedIn OAuth Success</title></head>
                        <body>
                            <h1>✅ Authorization Successful!</h1>
                            <p>You can close this window and return to your application.</p>
                            <script>setTimeout(function(){window.close();}, 3000);</script>
                        </body>
                        </html>
                        """
                        self.wfile.write(success_html.encode())
                    else:
                        # Handle error
                        error = query_params.get('error', ['Unknown error'])[0]
                        self.send_response(400)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()

                        error_html = f"""
                        <html>
                        <head><title>LinkedIn OAuth Error</title></head>
                        <body>
                            <h1>❌ Authorization Failed</h1>
                            <p>Error: {error}</p>
                        </body>
                        </html>
                        """
                        self.wfile.write(error_html.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                # Suppress server logs
                pass
        
        # Create handler with oauth instance
        handler = lambda *args, **kwargs: CallbackHandler(self, *args, **kwargs)
        
        # Start server on port 8083
        self.server = socketserver.TCPServer(("127.0.0.1", 8083), handler)
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        logger.info("OAuth callback server started on http://127.0.0.1:8083")
    
    def exchange_code_for_token(self) -> str:
        """
        Exchange authorization code for access token using LinkedIn's token endpoint
        """
        if not self.authorization_code:
            raise ValueError("No authorization code available")
        
        # LinkedIn OAuth 2.0 token endpoint
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        
        data = {
            'grant_type': 'authorization_code',
            'code': self.authorization_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        logger.info("Exchanging authorization code for access token...")
        response = requests.post(token_url, data=data, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            # OpenID Connect also returns id_token and scope string
            id_token = token_data.get('id_token')
            scope_str = token_data.get('scope')
            expires_in = token_data.get('expires_in')
            token_type = token_data.get('token_type')

            # Persist full token payload for downstream clients
            try:
                with open("linkedin_token.json", "w") as f:
                    json.dump({
                        "access_token": access_token,
                        "id_token": id_token,
                        "scope": scope_str,
                        "expires_in": expires_in,
                        "token_type": token_type,
                        "client_id": self.client_id
                    }, f, indent=2)
                logger.info("💾 Saved token payload to linkedin_token.json")
            except Exception as e:
                logger.warning(f"Could not save token file: {e}")

            logger.info("✅ Successfully obtained access token")
            return access_token
        else:
            error_msg = f"Token exchange failed: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_access_token(self) -> str:
        """
        Complete OAuth flow and get access token
        
        Returns:
            str: Access token
        """
        try:
            # Start callback server
            self.start_callback_server()
            
            # Get authorization URL
            auth_url = self.get_authorization_url()
            
            print("🔐 LinkedIn OAuth Flow Started")
            print("=" * 50)
            print(f"1. Opening browser to: {auth_url}")
            print("2. Please authorize the application in your browser")
            print("3. You'll be redirected back automatically")
            print("4. Waiting for authorization...")
            
            # Open browser
            webbrowser.open(auth_url)
            
            # Wait for authorization code
            import time
            timeout = 300  # 5 minutes
            elapsed = 0
            
            while not self.authorization_code and elapsed < timeout:
                time.sleep(1)
                elapsed += 1
            
            # Stop server
            if self.server:
                self.server.shutdown()
            
            if not self.authorization_code:
                raise Exception("Authorization timeout - no code received")
            
            print("✅ Authorization code received!")
            print("🔄 Exchanging code for access token...")
            
            # Exchange code for token
            access_token = self.exchange_code_for_token()
            
            print("✅ Access token obtained successfully!")
            print(f"Token: {access_token[:20]}...")
            
            return access_token
            
        except Exception as e:
            logger.error(f"OAuth flow failed: {e}")
            if self.server:
                self.server.shutdown()
            raise


def get_linkedin_credentials():
    """
    Get LinkedIn OAuth credentials from environment or prompt user
    """
    # Try to get from environment first
    client_id = getattr(settings, 'linkedin_client_id', None)
    client_secret = getattr(settings, 'linkedin_client_secret', None)
    redirect_uri = getattr(settings, 'linkedin_redirect_uri', None)

    if not client_id:
        client_id = input("Enter your LinkedIn Client ID: ").strip()

    if not client_secret:
        client_secret = input("Enter your LinkedIn Client Secret: ").strip()

    if not redirect_uri:
        # Default to the value authorized in LinkedIn app settings
        redirect_uri = "http://localhost:8083/auth/linkedin/callback"

    return client_id, client_secret, redirect_uri


async def main():
    """
    Test the OAuth flow
    """
    try:
        print("🚀 LinkedIn OAuth 2.0 Flow Test")
        print("=" * 40)
        
        # Get credentials
        client_id, client_secret, redirect_uri = get_linkedin_credentials()
        
        if not client_id or not client_secret:
            print("❌ Missing LinkedIn credentials")
            return
        
        # Create OAuth instance
        oauth = LinkedInOAuth(client_id, client_secret, redirect_uri)
        
        # Get access token (the full payload is already saved during exchange)
        access_token = oauth.get_access_token()
        
        # Read back the saved payload for confirmation without overwriting
        try:
            with open("linkedin_token.json", "r") as f:
                saved = json.load(f)
            print("💾 Token payload saved:")
            # Print minimal confirmation to avoid leaking full token
            scopes = saved.get("scope")
            token_type = saved.get("token_type")
            expires_in = saved.get("expires_in")
            print(f"  scope={scopes}")
            print(f"  token_type={token_type}, expires_in={expires_in}")
        except Exception as e:
            print(f"⚠️ Could not read saved token payload: {e}")
        print("🎉 OAuth flow completed successfully!")
        
        return access_token
        
    except Exception as e:
        print(f"❌ OAuth flow failed: {e}")
        return None


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())