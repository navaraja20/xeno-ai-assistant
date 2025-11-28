"""
Zapier Integration
Connect to 5000+ apps via Zapier webhooks
"""

import os
from typing import Any, Dict, List, Optional

import aiohttp

from src.integrations import IntegrationBase, IntegrationCredentials
from src.core.logger import setup_logger


class ZapierIntegration(IntegrationBase):
    """Zapier webhook integration"""
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.logger = setup_logger("integrations.zapier")
        
        # Zapier uses webhook URLs, not traditional API
        self.webhook_url = credentials.additional_data.get("webhook_url") if credentials else None
    
    @property
    def service_name(self) -> str:
        return "zapier"
    
    @property
    def supported_triggers(self) -> List[str]:
        return ["webhook_received"]
    
    @property
    def supported_actions(self) -> List[str]:
        return ["send_webhook", "trigger_zap"]
    
    async def authenticate(self) -> bool:
        """Test Zapier webhook"""
        return self.webhook_url is not None
    
    async def test_connection(self) -> bool:
        """Test webhook by sending test data"""
        if not self.webhook_url:
            return False
        
        try:
            test_data = {"test": True, "message": "XENO connection test"}
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=test_data) as response:
                    self.connected = response.status in [200, 201]
                    return self.connected
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Zapier action"""
        if action in ["send_webhook", "trigger_zap"]:
            return await self.send_webhook(**parameters)
        
        raise ValueError(f"Unknown action: {action}")
    
    async def send_webhook(
        self,
        data: Dict[str, Any],
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send data to Zapier webhook"""
        url = webhook_url or self.webhook_url
        
        if not url:
            raise ValueError("No webhook URL configured")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status >= 400:
                    error = await response.text()
                    raise Exception(f"Webhook error: {error}")
                
                return {
                    "success": True,
                    "status": response.status,
                    "message": "Webhook triggered successfully"
                }
