"""
Job Hunter - Clean Version
Intelligent job scraping using reliable APIs (no auth required)
"""

import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import json

import pandas as pd
from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

from src.ai.ai_agent import get_ai_agent
from src.core.logger import setup_logger


@dataclass
class JobOpportunity:
    """Job/Internship opportunity"""
    title: str
    company: str
    location: str
    job_type: str  # "internship", "full-time", "contract"
    description: str
    requirements: str
    posted_date: str
    url: str
    source: str  # "remotive", "themuse", etc.
    salary: Optional[str] = None
    remote: bool = False
    applied: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JobScraper:
    """Scrape jobs from multiple platforms using reliable APIs"""
    
    def __init__(self):
        self.logger = setup_logger("jobs.scraper")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self._driver = None
        self._undetected_driver = None
    
    def _get_undetected_driver(self):
        """Get undetected Chrome driver for sites with bot detection (like Wellfound)"""
        if self._undetected_driver is None:
            try:
                options = uc.ChromeOptions()
                options.add_argument('--start-minimized')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                
                # Use Brave browser if available
                brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
                if os.path.exists(brave_path):
                    options.binary_location = brave_path
                    self.logger.info("Using Brave with undetected_chromedriver")
                
                self._undetected_driver = uc.Chrome(options=options, version_main=142)
                self.logger.info("Undetected ChromeDriver initialized successfully")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize undetected driver: {e}")
                return None
        
        return self._undetected_driver
    
    def _get_undetected_driver(self):
        """Get undetected Chrome driver for sites with bot detection (like Wellfound)"""
        try:
            # Use undetected_chromedriver which bypasses bot detection
            options = uc.ChromeOptions()
            options.add_argument('--start-minimized')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # Use Brave browser if available
            brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
            if os.path.exists(brave_path):
                options.binary_location = brave_path
                self.logger.info("Using Brave with undetected_chromedriver")
            
            driver = uc.Chrome(options=options, version_main=142)
            self.logger.info("Undetected ChromeDriver initialized successfully")
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to initialize undetected driver: {e}")
            return None
    
    def _get_driver(self):
        """Get or create Selenium WebDriver using Brave browser"""
        if self._driver is None:
            try:
                chrome_options = Options()
                # DON'T use headless mode for sites with bot detection like Wellfound
                # chrome_options.add_argument('--headless=new')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-infobars')
                chrome_options.add_argument('--start-minimized')  # Start minimized instead of headless
                chrome_options.add_argument('--remote-debugging-port=0')  # Let system assign port
                chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # Brave browser (Chromium-based, fully compatible)
                brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
                
                if os.path.exists(brave_path):
                    chrome_options.binary_location = brave_path
                    self.logger.info("Using Brave browser for WebDriver")
                
                # Use specific ChromeDriver v142 compatible with Brave v142
                chromedriver_path = os.path.expandvars(r"%USERPROFILE%\.wdm\drivers\chromedriver\win64\142.0.7444.175\chromedriver-win64\chromedriver.exe")
                
                if os.path.exists(chromedriver_path):
                    service = Service(chromedriver_path)
                    self.logger.info(f"Using ChromeDriver v142")
                else:
                    # Fallback to webdriver-manager
                    service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
                
                self._driver = webdriver.Chrome(service=service, options=chrome_options)
                self._driver.set_page_load_timeout(30)
                self.logger.info("WebDriver initialized successfully")
            except Exception as e:
                self.logger.warning(f"WebDriver not available: {e}")
                self.logger.info("Falling back to requests-based scraping where possible")
                self._driver = None
        return self._driver
    
    def _close_driver(self):
        """Close WebDriver"""
        if self._driver:
            try:
                self._driver.quit()
                self._driver = None
            except:
                pass
    
    def scrape_remotive(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Scrape Remotive for remote jobs (free API, no auth) - France filter applied"""
        jobs = []
        
        try:
            url = "https://remotive.com/api/remote-jobs"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                all_jobs = data.get('jobs', [])
                
                for job_data in all_jobs:
                    title = job_data.get('title', '').lower()
                    description = job_data.get('description', '').lower()
                    category = job_data.get('category', '').lower()
                    job_location = job_data.get('candidate_required_location', 'Remote')
                    
                    # Filter by keywords
                    if any(kw.lower() in title or kw.lower() in description or kw.lower() in category for kw in keywords):
                        # Check for internship
                        is_internship = any(word in title or word in description 
                                          for word in ['intern', 'internship', 'stage', 'stagiaire'])
                        
                        # France-only filter
                        france_keywords = ['france', 'paris', 'lyon', 'toulouse', 'marseille', 'lille', 'nice', 'nantes', 
                                         'bordeaux', 'french', 'fr', 'europe', 'eu', 'anywhere', 'worldwide']
                        location_lower = job_location.lower()
                        
                        # Only include if location mentions France or is global/Europe
                        if not any(kw in location_lower for kw in france_keywords):
                            continue
                        
                        # If location is specific but not France-related, skip
                        if any(country in location_lower for country in ['usa', 'united states', 'canada', 'uk', 'australia', 'india', 'singapore']):
                            if not any(kw in location_lower for kw in ['france', 'paris', 'french', 'fr ']):
                                continue
                        
                        job = JobOpportunity(
                            title=job_data.get('title', 'N/A'),
                            company=job_data.get('company_name', 'N/A'),
                            location=job_location,
                            job_type="internship" if is_internship else job_data.get('job_type', 'full_time'),
                            description=job_data.get('description', '')[:500],
                            requirements="",
                            posted_date=job_data.get('publication_date', datetime.now().strftime("%Y-%m-%d")),
                            url=job_data.get('url', ''),
                            source="Remotive",
                            remote=True,
                            salary=job_data.get('salary', None)
                        )
                        
                        jobs.append(job)
                        
                        if len(jobs) >= max_results:
                            break
            else:
                self.logger.warning(f"Remotive API returned status {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Remotive scraping failed: {e}")
        
        self.logger.info(f"Scraped {len(jobs)} jobs from Remotive (France-filtered)")
        return jobs
    
    def scrape_themuse(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Scrape The Muse (free API, no auth)"""
        jobs = []
        
        try:
            url = "https://www.themuse.com/api/public/jobs"
            
            for keyword in keywords:
                params = {
                    "category": keyword,
                    "level": "Internship",
                    "page": 0
                }
                
                response = self.session.get(url, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    for item in results[:max_results]:
                        try:
                            locations = item.get('locations', [])
                            job_location = locations[0].get('name', location) if locations else location
                            
                            job = JobOpportunity(
                                title=item.get('name', 'N/A'),
                                company=item.get('company', {}).get('name', 'N/A'),
                                location=job_location,
                                job_type="internship",
                                description=item.get('contents', '')[:500],
                                requirements="",
                                posted_date=item.get('publication_date', datetime.now().strftime("%Y-%m-%d")),
                                url=item.get('refs', {}).get('landing_page', ''),
                                source="The Muse",
                                remote=False
                            )
                            jobs.append(job)
                        except Exception as e:
                            self.logger.error(f"Error parsing Muse job: {e}")
                            continue
        except Exception as e:
            self.logger.error(f"The Muse scraping failed: {e}")
        
        self.logger.info(f"Scraped {len(jobs)} jobs from The Muse")
        return jobs
    
    def scrape_stackoverflow(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Scrape Stack Overflow Jobs RSS feed"""
        jobs = []
        
        try:
            for keyword in keywords:
                url = f"https://stackoverflow.com/jobs/feed?q={keyword.replace(' ', '+')}&l={location}"
                
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'xml')
                    items = soup.find_all('item')[:max_results]
                    
                    for item in items:
                        try:
                            title = item.find('title').text if item.find('title') else "N/A"
                            link = item.find('link').text if item.find('link') else ""
                            description = item.find('description').text if item.find('description') else ""
                            pub_date = item.find('pubDate').text if item.find('pubDate') else ""
                            
                            try:
                                from email.utils import parsedate_to_datetime
                                posted_date = parsedate_to_datetime(pub_date).strftime("%Y-%m-%d")
                            except:
                                posted_date = datetime.now().strftime("%Y-%m-%d")
                            
                            job = JobOpportunity(
                                title=title,
                                company="Stack Overflow",
                                location=location,
                                job_type="internship" if any(kw in title.lower() for kw in ["intern", "stage"]) else "full-time",
                                description=description[:500],
                                requirements="",
                                posted_date=posted_date,
                                url=link,
                                source="Stack Overflow",
                                remote="remote" in description.lower()
                            )
                            jobs.append(job)
                        except Exception as e:
                            self.logger.error(f"Error parsing Stack Overflow job: {e}")
                            continue
        except Exception as e:
            self.logger.error(f"Stack Overflow scraping failed: {e}")
        
        self.logger.info(f"Scraped {len(jobs)} jobs from Stack Overflow")
        return jobs
    
    def scrape_welcometothejungle(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Scrape Welcome to the Jungle for French internships using Selenium"""
        jobs = []
        driver = self._get_driver()
        
        if not driver:
            self.logger.error("WebDriver not available for WTTJ scraping")
            return jobs
        
        try:
            for keyword in keywords:
                # Build WTTJ URL with internship filter
                base_url = "https://www.welcometothejungle.com/fr/jobs"
                params = f"?query={keyword.replace(' ', '+')}&aroundQuery=France&refinementList[contract_type][]=INTERNSHIP"
                url = base_url + params
                
                self.logger.info(f"Scraping WTTJ for: {keyword}")
                driver.get(url)
                
                # Wait for jobs to load (WTTJ is React-based)
                time.sleep(3)  # Give React time to render
                
                # Scroll to load more jobs
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # WTTJ job card selectors (updated for current structure)
                job_cards = (
                    soup.find_all('li', attrs={'data-testid': 'job-list-item'}) or
                    soup.find_all('div', class_=lambda x: x and 'job' in x.lower() and 'card' in x.lower()) or
                    soup.find_all('a', href=lambda x: x and '/jobs/' in x and '/fr/companies/' in x)
                )
                
                self.logger.info(f"Found {len(job_cards)} job cards on WTTJ")
                
                for card in job_cards[:max_results]:
                    try:
                        # Extract data from card
                        if card.name == 'a':
                            # Link element
                            title = card.get_text(strip=True)
                            job_url = f"https://www.welcometothejungle.com{card['href']}" if card['href'].startswith('/') else card['href']
                            
                            # Extract company and location from URL or surrounding elements
                            parent = card.find_parent(['li', 'div'])
                            company_elem = parent.find('span', string=lambda x: x and len(x) > 2) if parent else None
                            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                            
                            # Check if location is in France
                            location_elem = parent.find('span', string=lambda x: x and ('Paris' in str(x) or 'France' in str(x) or 'Lyon' in str(x) or 'Marseille' in str(x))) if parent else None
                            job_location = location_elem.get_text(strip=True) if location_elem else "France"
                        else:
                            # Card element
                            title_elem = card.find(['h3', 'h2', 'a'])
                            title = title_elem.get_text(strip=True) if title_elem else "N/A"
                            
                            company_elem = card.find('span', attrs={'data-testid': 'job-company-name'}) or card.find(string=lambda x: len(str(x)) > 3 and str(x).isupper() == False)
                            company = company_elem.get_text(strip=True) if hasattr(company_elem, 'get_text') else str(company_elem).strip() if company_elem else "Unknown"
                            
                            location_elem = card.find('span', attrs={'data-testid': 'job-location'}) or card.find(string=lambda x: 'Paris' in str(x) or 'France' in str(x))
                            job_location = location_elem.get_text(strip=True) if hasattr(location_elem, 'get_text') else str(location_elem).strip() if location_elem else "France"
                            
                            link_elem = card.find('a', href=True)
                            job_url = ""
                            if link_elem and link_elem.get('href'):
                                href = link_elem['href']
                                job_url = f"https://www.welcometothejungle.com{href}" if href.startswith('/') else href
                        
                        # Only include jobs in France
                        if any(loc in job_location for loc in ['France', 'Paris', 'Lyon', 'Marseille', 'Lille', 'Toulouse', 'Nice', 'Nantes', 'Bordeaux']):
                            job = JobOpportunity(
                                title=title,
                                company=company,
                                location=job_location,
                                job_type="internship",
                                description="",
                                requirements="",
                                posted_date=datetime.now().strftime("%Y-%m-%d"),
                                url=job_url,
                                source="Welcome to the Jungle",
                                remote=False
                            )
                            jobs.append(job)
                    
                    except Exception as e:
                        self.logger.error(f"Error parsing WTTJ job card: {e}")
                        continue
                
                if len(jobs) >= max_results:
                    break
                    
        except Exception as e:
            self.logger.error(f"WTTJ scraping failed: {e}")
        
        self.logger.info(f"Scraped {len(jobs)} jobs from Welcome to the Jungle")
        return jobs
    
    def scrape_wellfound(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Scrape Wellfound (formerly AngelList) for French startup internships using undetected Selenium"""
        jobs = []
        driver = self._get_undetected_driver()  # Use undetected driver
        
        if not driver:
            self.logger.error("WebDriver not available for Wellfound scraping")
            return jobs
        
        try:
            for keyword in keywords:
                # Try multiple URL patterns for Wellfound
                urls = [
                    f"https://wellfound.com/jobs?location=France&role={keyword.replace(' ', '%20')}",
                    f"https://wellfound.com/role/l/{keyword.replace(' ', '%20')}/france",
                    f"https://wellfound.com/jobs/internship-{keyword.replace(' ', '-').lower()}/l/france"
                ]
                
                for url in urls:
                    try:
                        self.logger.info(f"Scraping Wellfound: {url}")
                        driver.get(url)
                        
                        # Wait longer for React app to load
                        time.sleep(8)  # Wellfound uses heavy JavaScript/React
                        
                        # Scroll to trigger lazy loading
                        for _ in range(5):
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(2)
                        # Scroll to trigger lazy loading
                        for _ in range(3):
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(2)
                        
                        # Parse with BeautifulSoup
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        
                        # Save HTML for debugging (first iteration only)
                        if keyword == keywords[0] and url == urls[0]:
                            try:
                                with open('wellfound_debug.html', 'w', encoding='utf-8') as f:
                                    f.write(driver.page_source)
                                self.logger.info("Saved page HTML to wellfound_debug.html for analysis")
                            except Exception as e:
                                self.logger.warning(f"Could not save debug HTML: {e}")
                        
                        # Try multiple Wellfound selectors
                        job_cards = (
                            soup.find_all('div', attrs={'data-test': 'JobSearchResult'}) or
                            soup.find_all('div', class_=lambda x: x and 'styles_component' in str(x)) or
                            soup.find_all('div', class_=lambda x: x and 'job-listing' in str(x).lower()) or
                            soup.find_all('div', class_=lambda x: x and 'result' in str(x).lower()) or
                            soup.find_all('a', href=lambda x: x and '/company/' in str(x) and '/jobs/' in str(x))
                        )
                        
                        self.logger.info(f"Found {len(job_cards)} job cards on Wellfound from {url}")
                        
                        if job_cards:
                            break  # Found jobs, don't try other URLs
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to load Wellfound URL {url}: {e}")
                        continue
                        if job_cards:
                            break  # Found jobs, don't try other URLs
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to load Wellfound URL {url}: {e}")
                        continue
                
                # If no job cards found, log and continue
                if not job_cards:
                    self.logger.warning(f"No job cards found for '{keyword}' on Wellfound")
                    continue
                
                for card in job_cards[:max_results]:
                    try:
                        # Extract data from different card structures
                        title = "N/A"
                        company = "Startup"
                        job_location = "France"
                        job_url = ""
                        
                        if card.name == 'a':
                            # Link-based card
                            title = card.get_text(strip=True)
                            href = card.get('href', '')
                            job_url = f"https://wellfound.com{href}" if href.startswith('/') else href
                            
                            # Try to find company in parent
                            parent = card.find_parent(['div', 'li', 'article'])
                            if parent:
                                company_elem = parent.find(['h2', 'h3', 'span'], class_=lambda x: x and 'company' in str(x).lower())
                                if company_elem:
                                    company = company_elem.get_text(strip=True)
                        else:
                            # Div-based card
                            title_elem = (
                                card.find('h2', class_=lambda x: x and 'title' in str(x).lower()) or
                                card.find('h3') or
                                card.find('a', class_=lambda x: x and 'title' in str(x).lower())
                            )
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                            
                            company_elem = (
                                card.find('h2', class_=lambda x: x and 'company' in str(x).lower()) or
                                card.find('span', attrs={'data-test': 'StartupResult-name'}) or
                                card.find('div', class_=lambda x: x and 'company' in str(x).lower())
                            )
                            if company_elem:
                                company = company_elem.get_text(strip=True)
                            
                            location_elem = card.find(['span', 'div'], string=lambda x: x and any(loc in str(x) for loc in ['France', 'Paris', 'Lyon', 'Remote']))
                            if location_elem:
                                job_location = location_elem.get_text(strip=True)
                            
                            link_elem = card.find('a', href=True)
                            if link_elem:
                                href = link_elem.get('href', '')
                                job_url = f"https://wellfound.com{href}" if href.startswith('/') else href
                        
                        # Check if internship-related
                        is_internship = any(term in title.lower() for term in ['intern', 'stage', 'apprentice', 'graduate'])
                        
                        # Only include France jobs
                        if 'france' in job_location.lower() or 'paris' in job_location.lower() or 'french' in job_location.lower():
                            job = JobOpportunity(
                                title=title,
                                company=company,
                                location=job_location,
                                job_type="internship" if is_internship else "entry-level",
                                description="",
                                requirements="",
                                posted_date=datetime.now().strftime("%Y-%m-%d"),
                                url=job_url,
                                source="Wellfound",
                                remote="Remote" in job_location
                            )
                            jobs.append(job)
                    
                    except Exception as e:
                        self.logger.error(f"Error parsing Wellfound job card: {e}")
                        continue
                
                if len(jobs) >= max_results:
                    break
                    
        except Exception as e:
            self.logger.error(f"Wellfound scraping failed: {e}")
        
        self.logger.info(f"Scraped {len(jobs)} jobs from Wellfound")
        return jobs


class JobHunter:
    """Intelligent job hunting automation"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        
        self.logger = setup_logger("jobs.hunter")
        self.ai_agent = get_ai_agent()
        self.scraper = JobScraper()
        
        # User's resume
        self.resume_text: Optional[str] = None
        self.resume_path: Optional[str] = None
        
        # Job database
        self.jobs_db: List[JobOpportunity] = []
        self.db_path = "data/jobs/opportunities.json"
        
        self._initialized = True
    
    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'scraper') and self.scraper:
            self.scraper._close_driver()
        
        # Load existing jobs
        self._load_jobs()
        
        self._initialized = True
    
    def load_resume(self, resume_path: str):
        """Load user's resume"""
        self.resume_path = resume_path
        
        try:
            with open(resume_path, 'r', encoding='utf-8') as f:
                self.resume_text = f.read()
            
            self.logger.info(f"Resume loaded from {resume_path}")
        except Exception as e:
            self.logger.error(f"Failed to load resume: {e}")
            raise
    
    def search_jobs(
        self,
        keywords: List[str],
        location: str = "France",
        job_types: List[str] = ["internship"],
        sources: List[str] = ["remotive", "themuse", "stackoverflow"],
        max_per_source: int = 50,
    ) -> List[JobOpportunity]:
        """
        Search for jobs across multiple platforms
        
        Args:
            keywords: Search keywords (e.g., ["Data Science", "Machine Learning"])
            location: Job location
            job_types: Types to search for
            sources: Which job boards to scrape
            max_per_source: Maximum results per source
        """
        all_jobs = []
        
        for source in sources:
            try:
                if source.lower() == "remotive":
                    jobs = self.scraper.scrape_remotive(keywords, location, max_per_source)
                    all_jobs.extend(jobs)
                
                elif source.lower() in ["themuse", "muse"]:
                    jobs = self.scraper.scrape_themuse(keywords, location, max_per_source)
                    all_jobs.extend(jobs)
                
                elif source.lower() == "stackoverflow":
                    jobs = self.scraper.scrape_stackoverflow(keywords, location, max_per_source)
                    all_jobs.extend(jobs)
                
                elif source.lower() in ["welcometothejungle", "wttj"]:
                    jobs = self.scraper.scrape_welcometothejungle(keywords, location, max_per_source)
                    all_jobs.extend(jobs)
                
                elif source.lower() in ["wellfound", "angellist"]:
                    jobs = self.scraper.scrape_wellfound(keywords, location, max_per_source)
                    all_jobs.extend(jobs)
                
            except Exception as e:
                self.logger.error(f"Error scraping {source}: {e}")
                continue
        
        # Filter by job type
        if job_types:
            all_jobs = [j for j in all_jobs if j.job_type in job_types]
        
        # Remove duplicates (same title + company)
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            key = (job.title.lower(), job.company.lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        # Save to database
        self.jobs_db.extend(unique_jobs)
        self._save_jobs()
        
        self.logger.info(f"Found {len(unique_jobs)} unique jobs from {len(sources)} sources")
        
        # Convert to dictionaries for UI compatibility
        return [job.to_dict() for job in unique_jobs]
    
    def _load_jobs(self):
        """Load jobs from database"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.jobs_db = [JobOpportunity(**job) for job in data]
                self.logger.info(f"Loaded {len(self.jobs_db)} jobs from database")
        except Exception as e:
            self.logger.error(f"Failed to load jobs database: {e}")
            self.jobs_db = []
    
    def _save_jobs(self):
        """Save jobs to database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump([job.to_dict() for job in self.jobs_db], f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved {len(self.jobs_db)} jobs to database")
        except Exception as e:
            self.logger.error(f"Failed to save jobs database: {e}")
    
    def export_to_excel(self, filename: str = "job_opportunities.xlsx"):
        """Export jobs to Excel"""
        try:
            df = pd.DataFrame([job.to_dict() for job in self.jobs_db])
            df.to_excel(filename, index=False)
            self.logger.info(f"Exported {len(self.jobs_db)} jobs to {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Failed to export to Excel: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get job hunting statistics"""
        return {
            "total_jobs": len(self.jobs_db),
            "sources": list(set(job.source for job in self.jobs_db)),
            "job_types": dict(pd.Series([job.job_type for job in self.jobs_db]).value_counts()) if self.jobs_db else {},
            "locations": dict(pd.Series([job.location for job in self.jobs_db]).value_counts().head(10)) if self.jobs_db else {},
            "recent_jobs": len([j for j in self.jobs_db if (datetime.now() - datetime.fromisoformat(j.posted_date)).days <= 7]) if self.jobs_db else 0
        }


# Singleton instance
_job_hunter_instance: Optional[JobHunter] = None


def get_job_hunter() -> JobHunter:
    """Get singleton JobHunter instance"""
    global _job_hunter_instance
    if _job_hunter_instance is None:
        _job_hunter_instance = JobHunter()
    return _job_hunter_instance
