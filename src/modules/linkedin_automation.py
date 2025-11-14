"""
LinkedIn automation module for XENO AI Assistant.
Handles LinkedIn profile updates, connections, and posts using browser automation.
"""

from playwright.sync_api import sync_playwright, Page, Browser
from typing import List, Dict, Optional
import logging
import time

logger = logging.getLogger("XENO.LinkedInAutomation")


class LinkedInAutomation:
    """Handles LinkedIn automation tasks using browser automation."""
    
    def __init__(self, email: str, password: str):
        """
        Initialize LinkedIn automation.
        
        Args:
            email: LinkedIn email
            password: LinkedIn password
        """
        self.email = email
        self.password = password
        self.playwright = None
        self.browser = None
        self.page = None
        self.is_logged_in = False
        logger.info("LinkedInAutomation initialized")
    
    def start_browser(self, headless: bool = False) -> bool:
        """
        Start browser and navigate to LinkedIn.
        
        Args:
            headless: Run browser in headless mode
            
        Returns:
            True if browser started successfully
        """
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=headless)
            self.page = self.browser.new_page()
            
            logger.info("Browser started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False
    
    def stop_browser(self):
        """Stop browser and cleanup."""
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            
            logger.info("Browser stopped")
            
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")
    
    def login(self) -> bool:
        """
        Login to LinkedIn.
        
        Returns:
            True if login successful
        """
        try:
            if not self.page:
                self.start_browser()
            
            # Navigate to LinkedIn login
            self.page.goto('https://www.linkedin.com/login')
            time.sleep(2)
            
            # Fill login form
            self.page.fill('input[name="session_key"]', self.email)
            self.page.fill('input[name="session_password"]', self.password)
            
            # Click sign in
            self.page.click('button[type="submit"]')
            time.sleep(3)
            
            # Check if login successful
            if 'feed' in self.page.url or 'mynetwork' in self.page.url:
                self.is_logged_in = True
                logger.info("Successfully logged in to LinkedIn")
                return True
            else:
                logger.error("Login may have failed - unexpected URL")
                return False
                
        except Exception as e:
            logger.error(f"Failed to login to LinkedIn: {e}")
            return False
    
    def get_profile_info(self) -> Dict:
        """
        Get user's profile information.
        
        Returns:
            Dictionary with profile info
        """
        try:
            if not self.is_logged_in:
                self.login()
            
            # Navigate to profile
            self.page.goto('https://www.linkedin.com/in/me/')
            time.sleep(3)
            
            profile_info = {}
            
            # Get name
            try:
                name_elem = self.page.query_selector('h1.text-heading-xlarge')
                if name_elem:
                    profile_info['name'] = name_elem.inner_text()
            except:
                pass
            
            # Get headline
            try:
                headline_elem = self.page.query_selector('div.text-body-medium')
                if headline_elem:
                    profile_info['headline'] = headline_elem.inner_text()
            except:
                pass
            
            # Get connections count
            try:
                connections_elem = self.page.query_selector('span.t-bold')
                if connections_elem:
                    profile_info['connections'] = connections_elem.inner_text()
            except:
                pass
            
            logger.info("Retrieved profile information")
            return profile_info
            
        except Exception as e:
            logger.error(f"Error getting profile info: {e}")
            return {}
    
    def post_update(self, text: str) -> bool:
        """
        Post an update to LinkedIn feed.
        
        Args:
            text: Text content to post
            
        Returns:
            True if posted successfully
        """
        try:
            if not self.is_logged_in:
                self.login()
            
            # Navigate to feed
            self.page.goto('https://www.linkedin.com/feed/')
            time.sleep(2)
            
            # Click "Start a post" button
            start_post_button = self.page.query_selector('button[aria-label*="Start a post"]')
            if not start_post_button:
                start_post_button = self.page.query_selector('.share-box-feed-entry__trigger')
            
            if start_post_button:
                start_post_button.click()
                time.sleep(2)
            else:
                logger.error("Could not find 'Start a post' button")
                return False
            
            # Type the post content
            editor = self.page.query_selector('div[role="textbox"]')
            if editor:
                editor.click()
                time.sleep(1)
                editor.type(text)
                time.sleep(2)
            else:
                logger.error("Could not find post editor")
                return False
            
            # Click Post button
            post_button = self.page.query_selector('button[aria-label*="Post"]')
            if post_button:
                post_button.click()
                time.sleep(3)
                logger.info("Posted update to LinkedIn")
                return True
            else:
                logger.error("Could not find Post button")
                return False
                
        except Exception as e:
            logger.error(f"Failed to post update: {e}")
            return False
    
    def send_connection_request(self, profile_url: str, message: str = '') -> bool:
        """
        Send a connection request.
        
        Args:
            profile_url: URL of the profile to connect with
            message: Optional connection message
            
        Returns:
            True if request sent successfully
        """
        try:
            if not self.is_logged_in:
                self.login()
            
            # Navigate to profile
            self.page.goto(profile_url)
            time.sleep(3)
            
            # Click Connect button
            connect_button = self.page.query_selector('button[aria-label*="Connect"]')
            if not connect_button:
                connect_button = self.page.query_selector('button:has-text("Connect")')
            
            if connect_button:
                connect_button.click()
                time.sleep(2)
                
                # If there's a message option
                if message:
                    add_note_button = self.page.query_selector('button[aria-label*="Add a note"]')
                    if add_note_button:
                        add_note_button.click()
                        time.sleep(1)
                        
                        message_field = self.page.query_selector('textarea[name="message"]')
                        if message_field:
                            message_field.type(message)
                            time.sleep(1)
                
                # Send invitation
                send_button = self.page.query_selector('button[aria-label*="Send"]')
                if send_button:
                    send_button.click()
                    time.sleep(2)
                    logger.info(f"Sent connection request to {profile_url}")
                    return True
                    
            logger.error("Could not find Connect button")
            return False
            
        except Exception as e:
            logger.error(f"Failed to send connection request: {e}")
            return False
    
    def get_notifications(self) -> List[Dict]:
        """
        Get recent notifications.
        
        Returns:
            List of notifications
        """
        try:
            if not self.is_logged_in:
                self.login()
            
            # Navigate to notifications
            self.page.goto('https://www.linkedin.com/notifications/')
            time.sleep(3)
            
            notifications = []
            
            # Get notification items
            notification_items = self.page.query_selector_all('.notification-card')
            
            for item in notification_items[:10]:  # Get latest 10
                try:
                    text = item.inner_text()
                    notifications.append({
                        'text': text,
                        'timestamp': datetime.now().isoformat()
                    })
                except:
                    continue
            
            logger.info(f"Retrieved {len(notifications)} notifications")
            return notifications
            
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return []
    
    def search_people(self, keywords: str, max_results: int = 10) -> List[Dict]:
        """
        Search for people on LinkedIn.
        
        Args:
            keywords: Search keywords
            max_results: Maximum number of results
            
        Returns:
            List of people profiles
        """
        try:
            if not self.is_logged_in:
                self.login()
            
            # Navigate to search
            search_url = f'https://www.linkedin.com/search/results/people/?keywords={keywords}'
            self.page.goto(search_url)
            time.sleep(3)
            
            people = []
            
            # Get search results
            result_items = self.page.query_selector_all('.entity-result')
            
            for item in result_items[:max_results]:
                try:
                    # Get profile link
                    link_elem = item.query_selector('a.app-aware-link')
                    profile_url = link_elem.get_attribute('href') if link_elem else ''
                    
                    # Get name
                    name_elem = item.query_selector('.entity-result__title-text a span')
                    name = name_elem.inner_text() if name_elem else 'Unknown'
                    
                    # Get headline
                    headline_elem = item.query_selector('.entity-result__primary-subtitle')
                    headline = headline_elem.inner_text() if headline_elem else ''
                    
                    people.append({
                        'name': name,
                        'headline': headline,
                        'profile_url': profile_url
                    })
                    
                except:
                    continue
            
            logger.info(f"Found {len(people)} people for '{keywords}'")
            return people
            
        except Exception as e:
            logger.error(f"Error searching people: {e}")
            return []
    
    def get_job_recommendations(self, max_results: int = 10) -> List[Dict]:
        """
        Get job recommendations from LinkedIn.
        
        Args:
            max_results: Maximum number of results
            
        Returns:
            List of job recommendations
        """
        try:
            if not self.is_logged_in:
                self.login()
            
            # Navigate to jobs
            self.page.goto('https://www.linkedin.com/jobs/')
            time.sleep(3)
            
            jobs = []
            
            # Get job cards
            job_cards = self.page.query_selector_all('.job-card-container')
            
            for card in job_cards[:max_results]:
                try:
                    # Get job title
                    title_elem = card.query_selector('.job-card-list__title')
                    title = title_elem.inner_text() if title_elem else 'Unknown'
                    
                    # Get company
                    company_elem = card.query_selector('.job-card-container__company-name')
                    company = company_elem.inner_text() if company_elem else 'Unknown'
                    
                    # Get location
                    location_elem = card.query_selector('.job-card-container__metadata-item')
                    location = location_elem.inner_text() if location_elem else ''
                    
                    # Get job URL
                    link_elem = card.query_selector('a')
                    job_url = link_elem.get_attribute('href') if link_elem else ''
                    
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'url': job_url
                    })
                    
                except:
                    continue
            
            logger.info(f"Retrieved {len(jobs)} job recommendations")
            return jobs
            
        except Exception as e:
            logger.error(f"Error getting job recommendations: {e}")
            return []


from datetime import datetime
