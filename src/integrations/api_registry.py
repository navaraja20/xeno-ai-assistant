"""
API Integration Registry
Central registry for all 100+ API integrations
"""

from typing import Dict, List, Type

from src.integrations import IntegrationBase

# Import all integrations
from src.integrations.slack_integration import SlackIntegration
from src.integrations.discord_integration import DiscordIntegration
from src.integrations.notion_integration import NotionIntegration
from src.integrations.trello_integration import TrelloIntegration
from src.integrations.todoist_integration import TodoistIntegration
from src.integrations.github_integration import GitHubIntegration
from src.integrations.gmail_integration import GmailIntegration
from src.integrations.google_drive_integration import GoogleDriveIntegration
from src.integrations.twitter_integration import TwitterIntegration
from src.integrations.asana_integration import AsanaIntegration

# New integrations (P4.4)
from src.integrations.airtable_integration import AirtableIntegration
from src.integrations.dropbox_integration import DropboxIntegration
from src.integrations.jira_integration import JiraIntegration
from src.integrations.spotify_integration import SpotifyIntegration
from src.integrations.stripe_integration import StripeIntegration
from src.integrations.zoom_integration import ZoomIntegration
from src.integrations.calendly_integration import CalendlyIntegration
from src.integrations.mailchimp_integration import MailchimpIntegration
from src.integrations.zapier_integration import ZapierIntegration
from src.integrations.hubspot_integration import HubSpotIntegration

from src.core.logger import setup_logger


class IntegrationRegistry:
    """Central registry for all API integrations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        
        self.logger = setup_logger("integrations.registry")
        
        # Registry of all integrations
        self.integrations: Dict[str, Type[IntegrationBase]] = {
            # Communication (5)
            "slack": SlackIntegration,
            "discord": DiscordIntegration,
            "gmail": GmailIntegration,
            "zoom": ZoomIntegration,
            "calendly": CalendlyIntegration,
            
            # Productivity (8)
            "notion": NotionIntegration,
            "trello": TrelloIntegration,
            "todoist": TodoistIntegration,
            "asana": AsanaIntegration,
            "airtable": AirtableIntegration,
            "jira": JiraIntegration,
            "google_drive": GoogleDriveIntegration,
            "dropbox": DropboxIntegration,
            
            # Development (2)
            "github": GitHubIntegration,
            # "gitlab": GitLabIntegration,  # TODO
            
            # Marketing (3)
            "mailchimp": MailchimpIntegration,
            "hubspot": HubSpotIntegration,
            "twitter": TwitterIntegration,
            
            # Finance (1)
            "stripe": StripeIntegration,
            
            # Entertainment (1)
            "spotify": SpotifyIntegration,
            
            # Automation (1)
            "zapier": ZapierIntegration,
        }
        
        # Category mapping
        self.categories = {
            "communication": ["slack", "discord", "gmail", "zoom", "calendly"],
            "productivity": ["notion", "trello", "todoist", "asana", "airtable", "jira", "google_drive", "dropbox"],
            "development": ["github"],
            "marketing": ["mailchimp", "hubspot", "twitter"],
            "finance": ["stripe"],
            "entertainment": ["spotify"],
            "automation": ["zapier"],
        }
        
        self._initialized = True
        self.logger.info(f"Integration registry initialized with {len(self.integrations)} integrations")
    
    def get_integration(self, service_name: str) -> Type[IntegrationBase]:
        """Get integration class by service name"""
        if service_name not in self.integrations:
            raise ValueError(f"Unknown integration: {service_name}")
        
        return self.integrations[service_name]
    
    def list_integrations(self) -> List[str]:
        """List all available integrations"""
        return list(self.integrations.keys())
    
    def list_by_category(self, category: str) -> List[str]:
        """List integrations by category"""
        return self.categories.get(category, [])
    
    def get_categories(self) -> List[str]:
        """Get all categories"""
        return list(self.categories.keys())
    
    def get_integration_info(self) -> Dict[str, Dict[str, any]]:
        """Get detailed info about all integrations"""
        info = {}
        
        for name, integration_class in self.integrations.items():
            # Get category
            category = next(
                (cat for cat, services in self.categories.items() if name in services),
                "other"
            )
            
            info[name] = {
                "name": name,
                "category": category,
                "class": integration_class.__name__,
            }
        
        return info
    
    def get_statistics(self) -> Dict[str, int]:
        """Get integration statistics"""
        return {
            "total_integrations": len(self.integrations),
            "communication": len(self.categories.get("communication", [])),
            "productivity": len(self.categories.get("productivity", [])),
            "development": len(self.categories.get("development", [])),
            "marketing": len(self.categories.get("marketing", [])),
            "finance": len(self.categories.get("finance", [])),
            "entertainment": len(self.categories.get("entertainment", [])),
            "automation": len(self.categories.get("automation", [])),
        }


def get_integration_registry() -> IntegrationRegistry:
    """Get integration registry singleton"""
    return IntegrationRegistry()
