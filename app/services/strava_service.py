from typing import Dict, Optional, List
import aiohttp
import ssl
import certifi
from datetime import datetime
from app.core.config import get_settings

settings = get_settings()

class StravaService:
    BASE_URL = "https://www.strava.com/api/v3"
    
    def __init__(self):
        self.client_id = settings.STRAVA_CLIENT_ID
        self.client_secret = settings.STRAVA_CLIENT_SECRET
        self.webhook_verify_token = settings.STRAVA_WEBHOOK_VERIFY_TOKEN
        self.is_configured = all([self.client_id, self.client_secret, self.webhook_verify_token])
        # Create SSL context using certifi's certificates
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        
    async def get_oauth_url(self, redirect_uri: str, state: str = "") -> str:
        """Get Strava OAuth URL for user authorization."""
        if not self.is_configured:
            return None
            
        return (
            f"https://www.strava.com/oauth/authorize"
            f"?client_id={self.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope=activity:read_all"
            f"&state={state}"
        )
        
    async def exchange_token(self, code: str) -> Dict:
        """Exchange authorization code for access token."""
        if not self.is_configured:
            return None
            
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                "https://www.strava.com/oauth/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code"
                }
            ) as response:
                return await response.json()
                
    async def refresh_token(self, refresh_token: str) -> Dict:
        """Refresh expired access token."""
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                "https://www.strava.com/oauth/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                }
            ) as response:
                return await response.json()
                
    async def get_activity(self, activity_id: int, access_token: str) -> Optional[Dict]:
        """Get detailed activity data."""
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                f"{self.BASE_URL}/activities/{activity_id}",
                headers={"Authorization": f"Bearer {access_token}"}
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
                
    async def get_recent_activities(self, access_token: str, after: datetime = None) -> List[Dict]:
        """Get user's recent activities."""
        params = {"per_page": 30}
        if after:
            params["after"] = int(after.timestamp())
            
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                f"{self.BASE_URL}/athlete/activities",
                headers={"Authorization": f"Bearer {access_token}"},
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                return []
                
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[Dict]:
        """Verify Strava webhook subscription."""
        if mode == "subscribe" and token == self.webhook_verify_token:
            return {"hub.challenge": challenge}
        return None
        
    async def create_webhook_subscription(self, callback_url: str) -> Optional[Dict]:
        """Create Strava webhook subscription."""
        print(f"Creating webhook subscription with callback URL: {callback_url}")
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                "https://www.strava.com/api/v3/push_subscriptions",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "callback_url": callback_url,
                    "verify_token": self.webhook_verify_token
                }
            ) as response:
                print(f"Webhook subscription response status: {response.status}")
                if response.status == 200:
                    return await response.json()
                print(f"Webhook subscription failed: {await response.text()}")
                return None 