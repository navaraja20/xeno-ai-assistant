"""
Spotify Integration
Music playback and playlist management
"""

import os
from typing import Any, Dict, List, Optional

import aiohttp

from src.integrations import IntegrationBase, IntegrationCredentials
from src.core.logger import setup_logger


class SpotifyIntegration(IntegrationBase):
    """Spotify music integration"""
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.logger = setup_logger("integrations.spotify")
        self.access_token = credentials.api_key if credentials else os.getenv("SPOTIFY_ACCESS_TOKEN")
        self.base_url = "https://api.spotify.com/v1"
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
    
    @property
    def service_name(self) -> str:
        return "spotify"
    
    @property
    def supported_triggers(self) -> List[str]:
        return ["track_played", "playlist_updated"]
    
    @property
    def supported_actions(self) -> List[str]:
        return [
            "play_track",
            "pause_playback",
            "next_track",
            "previous_track",
            "create_playlist",
            "add_to_playlist",
            "search_tracks",
            "get_current_playback",
        ]
    
    async def authenticate(self) -> bool:
        """Test Spotify authentication"""
        return await self.test_connection()
    
    async def test_connection(self) -> bool:
        """Test Spotify API connection"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/me",
                    headers=self.headers
                ) as response:
                    self.connected = response.status == 200
                    return self.connected
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Spotify action"""
        action_map = {
            "play_track": self.play_track,
            "pause_playback": self.pause_playback,
            "next_track": self.next_track,
            "previous_track": self.previous_track,
            "create_playlist": self.create_playlist,
            "add_to_playlist": self.add_to_playlist,
            "search_tracks": self.search_tracks,
            "get_current_playback": self.get_current_playback,
        }
        
        handler = action_map.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(**parameters)
    
    async def _api_call(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Optional[Dict[str, Any]]:
        """Make Spotify API call"""
        url = f"{self.base_url}/{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=self.headers, json=data, params=params
            ) as response:
                if response.status >= 400:
                    error = await response.text()
                    raise Exception(f"API error: {error}")
                
                if response.status == 204:
                    return {"success": True}
                
                return await response.json()
    
    async def play_track(
        self,
        track_uri: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Play a track"""
        data = {}
        if track_uri:
            data["uris"] = [track_uri]
        
        params = {}
        if device_id:
            params["device_id"] = device_id
        
        return await self._api_call("PUT", "me/player/play", data=data, params=params)
    
    async def pause_playback(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """Pause playback"""
        params = {"device_id": device_id} if device_id else None
        return await self._api_call("PUT", "me/player/pause", params=params)
    
    async def next_track(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """Skip to next track"""
        params = {"device_id": device_id} if device_id else None
        return await self._api_call("POST", "me/player/next", params=params)
    
    async def previous_track(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """Go to previous track"""
        params = {"device_id": device_id} if device_id else None
        return await self._api_call("POST", "me/player/previous", params=params)
    
    async def create_playlist(
        self,
        user_id: str,
        name: str,
        description: str = "",
        public: bool = True,
    ) -> Dict[str, Any]:
        """Create a playlist"""
        data = {
            "name": name,
            "description": description,
            "public": public,
        }
        
        return await self._api_call("POST", f"users/{user_id}/playlists", data=data)
    
    async def add_to_playlist(
        self,
        playlist_id: str,
        track_uris: List[str],
    ) -> Dict[str, Any]:
        """Add tracks to playlist"""
        data = {"uris": track_uris}
        return await self._api_call("POST", f"playlists/{playlist_id}/tracks", data=data)
    
    async def search_tracks(
        self,
        query: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search for tracks"""
        params = {
            "q": query,
            "type": "track",
            "limit": limit,
        }
        
        result = await self._api_call("GET", "search", params=params)
        return result.get("tracks", {}).get("items", [])
    
    async def get_current_playback(self) -> Dict[str, Any]:
        """Get current playback state"""
        return await self._api_call("GET", "me/player")
