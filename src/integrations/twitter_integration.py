"""
Twitter/X Integration for XENO
Support for posting tweets, managing threads, interacting with content
"""

import aiohttp
from typing import Dict, Any, List, Optional
from . import IntegrationBase


class TwitterIntegration(IntegrationBase):
    """Twitter/X API integration (v2)"""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__(credentials)
        self.bearer_token = credentials.get('bearer_token')
        self.api_key = credentials.get('api_key')
        self.api_secret = credentials.get('api_secret')
        self.access_token = credentials.get('access_token')
        self.access_secret = credentials.get('access_secret')
        self.base_url = 'https://api.twitter.com/2'
        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }
    
    @property
    def service_name(self) -> str:
        return 'twitter'
    
    @property
    def supported_triggers(self) -> List[str]:
        return ['new_mention', 'new_follower', 'tweet_liked', 'tweet_retweeted']
    
    @property
    def supported_actions(self) -> List[str]:
        return [
            'post_tweet',
            'post_thread',
            'reply_to_tweet',
            'retweet',
            'like_tweet',
            'delete_tweet',
            'follow_user',
            'unfollow_user'
        ]
    
    async def authenticate(self) -> bool:
        """Test Twitter authentication"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.base_url}/users/me',
                    headers=self.headers
                ) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def test_connection(self) -> bool:
        """Test Twitter API connection"""
        return await self.authenticate()
    
    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Twitter action"""
        actions = {
            'post_tweet': self.post_tweet,
            'post_thread': self.post_thread,
            'reply_to_tweet': self.reply_to_tweet,
            'retweet': self.retweet,
            'like_tweet': self.like_tweet,
            'delete_tweet': self.delete_tweet,
            'follow_user': self.follow_user,
            'unfollow_user': self.unfollow_user
        }
        
        if action not in actions:
            raise ValueError(f"Unknown action: {action}")
        
        return await actions[action](**parameters)
    
    async def post_tweet(
        self,
        text: str,
        media_ids: Optional[List[str]] = None,
        poll_options: Optional[List[str]] = None,
        poll_duration_minutes: Optional[int] = None
    ) -> Dict[str, Any]:
        """Post a new tweet"""
        data = {'text': text}
        
        if media_ids:
            data['media'] = {'media_ids': media_ids}
        
        if poll_options and poll_duration_minutes:
            data['poll'] = {
                'options': poll_options,
                'duration_minutes': poll_duration_minutes
            }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.base_url}/tweets',
                headers=self.headers,
                json=data
            ) as response:
                result = await response.json()
                return {
                    'success': response.status == 201,
                    'tweet_id': result.get('data', {}).get('id'),
                    'text': result.get('data', {}).get('text')
                }
    
    async def post_thread(self, tweets: List[str]) -> Dict[str, Any]:
        """Post a thread of tweets"""
        tweet_ids = []
        previous_id = None
        
        for tweet_text in tweets:
            data = {'text': tweet_text}
            
            if previous_id:
                data['reply'] = {'in_reply_to_tweet_id': previous_id}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{self.base_url}/tweets',
                    headers=self.headers,
                    json=data
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        tweet_id = result.get('data', {}).get('id')
                        tweet_ids.append(tweet_id)
                        previous_id = tweet_id
                    else:
                        break
        
        return {
            'success': len(tweet_ids) == len(tweets),
            'tweet_ids': tweet_ids,
            'thread_length': len(tweet_ids)
        }
    
    async def reply_to_tweet(
        self,
        tweet_id: str,
        text: str
    ) -> Dict[str, Any]:
        """Reply to a tweet"""
        data = {
            'text': text,
            'reply': {
                'in_reply_to_tweet_id': tweet_id
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.base_url}/tweets',
                headers=self.headers,
                json=data
            ) as response:
                result = await response.json()
                return {
                    'success': response.status == 201,
                    'tweet_id': result.get('data', {}).get('id')
                }
    
    async def retweet(self, tweet_id: str, user_id: str) -> Dict[str, Any]:
        """Retweet a tweet"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.base_url}/users/{user_id}/retweets',
                headers=self.headers,
                json={'tweet_id': tweet_id}
            ) as response:
                return {
                    'success': response.status == 200
                }
    
    async def like_tweet(self, tweet_id: str, user_id: str) -> Dict[str, Any]:
        """Like a tweet"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.base_url}/users/{user_id}/likes',
                headers=self.headers,
                json={'tweet_id': tweet_id}
            ) as response:
                return {
                    'success': response.status == 200
                }
    
    async def delete_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Delete a tweet"""
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f'{self.base_url}/tweets/{tweet_id}',
                headers=self.headers
            ) as response:
                return {
                    'success': response.status == 200
                }
    
    async def follow_user(self, user_id: str, target_user_id: str) -> Dict[str, Any]:
        """Follow a user"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.base_url}/users/{user_id}/following',
                headers=self.headers,
                json={'target_user_id': target_user_id}
            ) as response:
                return {
                    'success': response.status == 200
                }
    
    async def unfollow_user(self, user_id: str, target_user_id: str) -> Dict[str, Any]:
        """Unfollow a user"""
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f'{self.base_url}/users/{user_id}/following/{target_user_id}',
                headers=self.headers
            ) as response:
                return {
                    'success': response.status == 200
                }
    
    async def get_mentions(
        self,
        user_id: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Get mentions timeline"""
        params = {'max_results': max_results}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'{self.base_url}/users/{user_id}/mentions',
                headers=self.headers,
                params=params
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('data', [])
                return []
    
    async def search_tweets(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search tweets"""
        params = {
            'query': query,
            'max_results': max_results
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'{self.base_url}/tweets/search/recent',
                headers=self.headers,
                params=params
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('data', [])
                return []
    
    async def upload_media(self, file_path: str) -> Optional[str]:
        """Upload media and return media ID"""
        # Note: Media upload uses v1.1 API
        upload_url = 'https://upload.twitter.com/1.1/media/upload.json'
        
        import os
        import base64
        
        with open(file_path, 'rb') as f:
            media_data = base64.b64encode(f.read()).decode()
        
        data = {
            'media_data': media_data
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                upload_url,
                headers=self.headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('media_id_string')
                return None
    
    def get_available_actions(self) -> List[Dict[str, Any]]:
        """Get list of available actions with metadata"""
        return [
            {
                'name': 'post_tweet',
                'description': 'Post a new tweet',
                'parameters': ['text', 'media_ids', 'poll_options']
            },
            {
                'name': 'post_thread',
                'description': 'Post a thread of tweets',
                'parameters': ['tweets']
            },
            {
                'name': 'reply_to_tweet',
                'description': 'Reply to a tweet',
                'parameters': ['tweet_id', 'text']
            },
            {
                'name': 'retweet',
                'description': 'Retweet a tweet',
                'parameters': ['tweet_id', 'user_id']
            },
            {
                'name': 'like_tweet',
                'description': 'Like a tweet',
                'parameters': ['tweet_id', 'user_id']
            }
        ]
