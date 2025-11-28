"""
Stripe Integration
Payment processing and subscription management
"""

import os
from typing import Any, Dict, List, Optional

import aiohttp

from src.core.logger import setup_logger
from src.integrations import IntegrationBase, IntegrationCredentials


class StripeIntegration(IntegrationBase):
    """Stripe payment integration"""

    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.logger = setup_logger("integrations.stripe")
        self.api_key = credentials.api_key if credentials else os.getenv("STRIPE_API_KEY")
        self.base_url = "https://api.stripe.com/v1"
        self.auth = aiohttp.BasicAuth(self.api_key, "")

    @property
    def service_name(self) -> str:
        return "stripe"

    @property
    def supported_triggers(self) -> List[str]:
        return ["payment_succeeded", "subscription_created", "invoice_paid"]

    @property
    def supported_actions(self) -> List[str]:
        return [
            "create_customer",
            "create_payment_intent",
            "create_subscription",
            "cancel_subscription",
            "list_customers",
            "list_payments",
        ]

    async def authenticate(self) -> bool:
        """Test Stripe authentication"""
        return await self.test_connection()

    async def test_connection(self) -> bool:
        """Test Stripe API connection"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/customers?limit=1", auth=self.auth
                ) as response:
                    self.connected = response.status == 200
                    return self.connected
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Stripe action"""
        action_map = {
            "create_customer": self.create_customer,
            "create_payment_intent": self.create_payment_intent,
            "create_subscription": self.create_subscription,
            "cancel_subscription": self.cancel_subscription,
            "list_customers": self.list_customers,
            "list_payments": self.list_payments,
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
    ) -> Dict[str, Any]:
        """Make Stripe API call"""
        url = f"{self.base_url}/{endpoint}"

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, auth=self.auth, data=data) as response:
                if response.status >= 400:
                    error = await response.text()
                    raise Exception(f"API error: {error}")
                return await response.json()

    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Create a customer"""
        data = {"email": email}
        if name:
            data["name"] = name
        if metadata:
            data["metadata"] = metadata

        return await self._api_call("POST", "customers", data=data)

    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        customer: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a payment intent"""
        data = {
            "amount": amount,
            "currency": currency,
        }
        if customer:
            data["customer"] = customer

        return await self._api_call("POST", "payment_intents", data=data)

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
    ) -> Dict[str, Any]:
        """Create a subscription"""
        data = {
            "customer": customer_id,
            "items": [{"price": price_id}],
        }

        return await self._api_call("POST", "subscriptions", data=data)

    async def cancel_subscription(
        self,
        subscription_id: str,
    ) -> Dict[str, Any]:
        """Cancel a subscription"""
        return await self._api_call("DELETE", f"subscriptions/{subscription_id}")

    async def list_customers(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """List customers"""
        result = await self._api_call("GET", f"customers?limit={limit}")
        return result.get("data", [])

    async def list_payments(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """List payment intents"""
        result = await self._api_call("GET", f"payment_intents?limit={limit}")
        return result.get("data", [])
