"""
Job Hunter
Intelligent job scraping and application automation
"""

import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup

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
    source: str  # "indeed", "linkedin", etc.
    salary: Optional[str] = None
    remote: bool = False
    applied: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JobScraper:
    """Scrape jobs from multiple platforms"""

    def __init__(self):
        self.logger = setup_logger("jobs.scraper")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def scrape_github_jobs(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Scrape GitHub Jobs (public API, reliable)"""
        jobs = []

        # GitHub Jobs API was sunset, but many companies post on GitHub repos
        # Use alternative: TheMuseJobs API (free, no auth)
        try:
            url = "https://www.themuse.com/api/public/jobs"

            for keyword in keywords:
                params = {
                    "category": "Data Science",
                    "level": "Internship",
                    "location": location,
                    "page": 0
                }

                response = self.session.get(url, params=params, timeout=15)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])

                    for item in results[:max_results]:
                        try:
                            job = JobOpportunity(
                                title=item.get('name', 'N/A'),
                                company=item.get('company', {}).get('name', 'N/A'),
                                location=item.get('locations', [{}])[0].get('name', location) if item.get('locations') else location,
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
            self.logger.error(f"Muse API failed: {e}")

        self.logger.info(f"Scraped {len(jobs)} jobs from The Muse")
        return jobs

    def scrape_adzuna_with_key(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """
        Scrape Adzuna with API key (free tier available)
        Get your free API key at: https://developer.adzuna.com/signup
        """
        jobs = []

        # These are example credentials - user should get their own
        # Free tier: 250 calls/month
        app_id = os.getenv("ADZUNA_APP_ID", "")
        app_key = os.getenv("ADZUNA_APP_KEY", "")

        if not app_id or not app_key:
            self.logger.warning("Adzuna API credentials not found in .env file")
            return jobs

        for keyword in keywords:
            try:
                country = "fr"
                query = "%20".join(keyword.split())
                url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"

                params = {
                    "app_id": app_id,
                    "app_key": app_key,
                    "what": query,
                    "where": location,
                    "results_per_page": min(max_results, 50),
                    "content-type": "application/json",
                    "category": "it-jobs"
                }

                response = self.session.get(url, params=params, timeout=15)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])

                    for item in results:
                        try:
                            salary = None
                            salary_min = item.get('salary_min')
                            salary_max = item.get('salary_max')

                            if salary_min or salary_max:
                                if salary_min and salary_max:
                                    salary = f"€{int(salary_min):,} - €{int(salary_max):,}"
                                elif salary_min:
                                    salary = f"€{int(salary_min):,}+"

                            job = JobOpportunity(
                                title=item.get('title', 'N/A'),
                                company=item.get('company', {}).get('display_name', 'N/A'),
                                location=item.get('location', {}).get('display_name', location),
                                job_type="internship" if any(kw in item.get('title', '').lower() for kw in ["stage", "intern", "stagiaire"]) else "full-time",
                                description=item.get('description', '')[:500],
                                requirements="",
                                posted_date=item.get('created', datetime.now().strftime("%Y-%m-%d")).split('T')[0],
                                url=item.get('redirect_url', ''),
                                source="Adzuna",
                                salary=salary,
                                remote=any(kw in item.get('description', '').lower() for kw in ["remote", "télétravail"])
                            )
                            jobs.append(job)
                        except Exception as e:
                            self.logger.error(f"Error parsing Adzuna job: {e}")
                            continue
                else:
                    self.logger.warning(f"Adzuna API returned status {response.status_code}")

            except Exception as e:
                self.logger.error(f"Adzuna API failed: {e}")

        self.logger.info(f"Scraped {len(jobs)} jobs from Adzuna")
        return jobs

    def scrape_stack_overflow(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Scrape Stack Overflow Jobs RSS feed"""
        jobs = []

        try:
            # Stack Overflow RSS feed
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

                            # Extract company from description
                            company = "Stack Overflow"

                            try:
                                from email.utils import parsedate_to_datetime
                                posted_date = parsedate_to_datetime(pub_date).strftime("%Y-%m-%d")
                            except:
                                posted_date = datetime.now().strftime("%Y-%m-%d")

                            job = JobOpportunity(
                                title=title,
                                company=company,
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

    def scrape_adzuna(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Note: Adzuna requires API credentials - use adzuna_with_key instead"""
        self.logger.warning("Adzuna requires API credentials - add ADZUNA_APP_ID and ADZUNA_APP_KEY to .env")
        return []

    def scrape_indeed(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Indeed scraping - currently using French version"""
        return self.scrape_indeed_fr(keywords, location, max_results)
            try:
                url = "https://remotive.com/api/remote-jobs"
                response = requests.get(url, timeout=15)

                if response.status_code == 200:
                    data = response.json()
                    all_jobs = data.get('jobs', [])

                    # Filter by keyword
                    keyword_lower = keyword.lower()
                    filtered_jobs = [
                        j for j in all_jobs
                        if keyword_lower in j.get('title', '').lower()
                        or keyword_lower in j.get('category', '').lower()
                    ]

                    for item in filtered_jobs[:max_results]:
                        try:
                            title = item.get('title', 'N/A')
                            company = item.get('company_name', 'N/A')
                            job_location = item.get('candidate_required_location', 'Remote')
                            description = item.get('description', '')
                            job_url = item.get('url', '')
                            published = item.get('publication_date', '')
                            job_type_raw = item.get('job_type', 'full-time')
                            category = item.get('category', '')

                            # Parse date
                            try:
                                posted_date = published.split('T')[0] if 'T' in published else datetime.now().strftime("%Y-%m-%d")
                            except:
                                posted_date = datetime.now().strftime("%Y-%m-%d")

                            job = JobOpportunity(
                                title=title,
                                company=company,
                                location=job_location,
                                job_type="internship" if "intern" in title.lower() else job_type_raw,
                                description=description[:500],
                                requirements="",
                                posted_date=posted_date,
                                url=job_url,
                                source="Remotive",
                                remote=True  # Remotive is remote-only
                            )

                            jobs.append(job)

                        except Exception as e:
                            self.logger.error(f"Error parsing Remotive job: {e}")
                            continue
                else:
                    self.logger.warning(f"Remotive API returned status {response.status_code}")

            except Exception as e:
                self.logger.error(f"Remotive API failed for {keyword}: {e}")

        # Also try France Travail (Pôle Emploi) API
        if not jobs and "france" in location.lower():
            jobs.extend(self._scrape_france_travail(keywords, location, max_results))

        self.logger.info(f"Scraped {len(jobs)} jobs from job boards")
        return jobs

    def _scrape_france_travail(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 20,
    ) -> List[JobOpportunity]:
        """Scrape from France Travail (Pôle Emploi) - requires registration but provides French jobs"""
        jobs = []

        # Note: This is a placeholder - France Travail API requires OAuth2
        # For production, implement proper OAuth2 flow
        self.logger.info("France Travail API requires authentication - skipping")

        return jobs

    def scrape_adzuna(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Note: Adzuna requires API credentials - using Indeed RSS instead"""
        self.logger.warning("Adzuna requires API credentials - using Indeed RSS instead")
        return self.scrape_indeed_rss(keywords, location, max_results)

    def scrape_indeed(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Indeed scraping (using RSS feed)"""
        return self.scrape_indeed_rss(keywords, location, max_results)

    def scrape_linkedin(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Scrape LinkedIn jobs (simplified - LinkedIn requires auth)"""
        jobs = []

        # Note: LinkedIn scraping is limited without authentication
        # This is a placeholder implementation

        for keyword in keywords:
            try:
                query = "%20".join(keyword.split())
                url = f"https://www.linkedin.com/jobs/search?keywords={query}&location={location}"

                self.logger.warning("LinkedIn scraping requires authentication - using API alternative")

                # In production, use LinkedIn API or authenticated session
                # For now, return placeholder

            except Exception as e:
                self.logger.error(f"LinkedIn scraping failed: {e}")

        return jobs

    def scrape_welcometothejungle(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Scrape Welcome to the Jungle for internships"""
        jobs = []

        for keyword in keywords:
            try:
                # WTTJ API endpoint for jobs
                query = keyword.lower().replace(" ", "-")

                # Search for stages (internships) specifically
                params = {
                    "query": keyword,
                    "aroundQuery": location,
                    "page": 1,
                    "groupBy": "organization",
                    "sortBy": "recent",
                    "refinementList[contract_type][]": "INTERNSHIP"  # Filter for internships
                }

                url = "https://www.welcometothejungle.com/api/graphql"

                # GraphQL query for WTTJ
                graphql_query = {
                    "query": """
                    query JobSearch($query: String!, $page: Int) {
                        jobs(query: $query, page: $page, filters: {contractType: ["INTERNSHIP"]}) {
                            nodes {
                                id
                                name
                                slug
                                description
                                contractType
                                publicationDate
                                office {
                                    name
                                    address {
                                        city
                                    }
                                }
                                organization {
                                    name
                                    slug
                                }
                                websites {
                                    websiteKind
                                    websiteUrl
                                }
                            }
                        }
                    }
                    """,
                    "variables": {
                        "query": keyword,
                        "page": 1
                    }
                }

                response = self.session.post(url, json=graphql_query, timeout=15)

                if response.status_code == 200:
                    data = response.json()
                    job_nodes = data.get("data", {}).get("jobs", {}).get("nodes", [])

                    for item in job_nodes[:max_results]:
                        try:
                            title = item.get("name", "N/A")
                            company = item.get("organization", {}).get("name", "N/A")
                            company_slug = item.get("organization", {}).get("slug", "")
                            job_slug = item.get("slug", "")

                            office = item.get("office", {})
                            city = office.get("address", {}).get("city", location) if office else location

                            description = item.get("description", "")
                            pub_date = item.get("publicationDate", "")
                            contract_type = item.get("contractType", "INTERNSHIP")

                            # Build job URL
                            job_url = f"https://www.welcometothejungle.com/fr/companies/{company_slug}/jobs/{job_slug}"

                            # Parse date
                            try:
                                posted_date = datetime.fromisoformat(pub_date.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                            except:
                                posted_date = datetime.now().strftime("%Y-%m-%d")

                            job = JobOpportunity(
                                title=title,
                                company=company,
                                location=city,
                                job_type="internship",
                                description=description[:500] if description else "",
                                requirements="",
                                posted_date=posted_date,
                                url=job_url,
                                source="Welcome to the Jungle",
                                remote="remote" in description.lower() if description else False
                            )

                            jobs.append(job)

                        except Exception as e:
                            self.logger.error(f"Error parsing WTTJ job: {e}")
                            continue
                else:
                    self.logger.warning(f"WTTJ returned status {response.status_code}")

            except Exception as e:
                self.logger.error(f"WTTJ scraping failed for {keyword}: {e}")

        self.logger.info(f"Scraped {len(jobs)} jobs from Welcome to the Jungle")
        return jobs

    def scrape_indeed_fr(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Scrape Indeed France using their job search API"""
        jobs = []

        for keyword in keywords:
            try:
                # Indeed France search parameters
                params = {
                    "q": keyword,
                    "l": location,
                    "jt": "internship",  # Job type: internship
                    "sort": "date",  # Sort by date
                    "fromage": "14",  # Last 14 days
                    "limit": min(max_results, 50)
                }

                url = "https://fr.indeed.com/jobs"

                response = self.session.get(url, params=params, timeout=15)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Indeed uses various selectors, try multiple
                    job_cards = (
                        soup.find_all('div', class_='job_seen_beacon') or
                        soup.find_all('div', class_='cardOutline') or
                        soup.find_all('div', attrs={'data-jk': True}) or
                        soup.find_all('td', class_='resultContent')
                    )

                    for card in job_cards[:max_results]:
                        try:
                            # Try multiple selectors for title
                            title_elem = (
                                card.find('h2', class_='jobTitle') or
                                card.find('a', class_='jcs-JobTitle') or
                                card.find('h2')
                            )
                            title = title_elem.get_text(strip=True) if title_elem else "N/A"

                            # Company name
                            company_elem = (
                                card.find('span', class_='companyName') or
                                card.find('span', attrs={'data-testid': 'company-name'})
                            )
                            company = company_elem.get_text(strip=True) if company_elem else "N/A"

                            # Location
                            location_elem = (
                                card.find('div', class_='companyLocation') or
                                card.find('div', attrs={'data-testid': 'text-location'})
                            )
                            job_location = location_elem.get_text(strip=True) if location_elem else location

                            # Job URL
                            link_elem = title_elem.find('a') if title_elem else card.find('a')
                            if link_elem and link_elem.get('href'):
                                href = link_elem['href']
                                job_url = f"https://fr.indeed.com{href}" if href.startswith('/') else href
                            else:
                                job_url = ""

                            # Description
                            snippet_elem = (
                                card.find('div', class_='job-snippet') or
                                card.find('div', class_='summary')
                            )
                            description = snippet_elem.get_text(strip=True) if snippet_elem else ""

                            # Date posted
                            date_elem = card.find('span', class_='date')
                            posted_date = datetime.now().strftime("%Y-%m-%d")

                            job = JobOpportunity(
                                title=title,
                                company=company,
                                location=job_location,
                                job_type="internship",
                                description=description[:500],
                                requirements="",
                                posted_date=posted_date,
                                url=job_url,
                                source="Indeed France",
                                remote=any(kw in description.lower() for kw in ["remote", "télétravail", "distance"])
                            )

                            jobs.append(job)

                        except Exception as e:
                            self.logger.error(f"Error parsing Indeed job card: {e}")
                            continue
                else:
                    self.logger.warning(f"Indeed returned status {response.status_code}")

            except Exception as e:
                self.logger.error(f"Indeed scraping failed for {keyword}: {e}")

        self.logger.info(f"Scraped {len(jobs)} jobs from Indeed France")
        return jobs

    def scrape_wellfound(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Scrape Wellfound (AngelList) for startup internships"""
        jobs = []

        for keyword in keywords:
            try:
                # Wellfound API endpoint
                params = {
                    "role": keyword.lower(),
                    "location": location,
                    "type": "internship",
                    "limit": min(max_results, 50)
                }

                # Wellfound uses a different structure, try their public job board
                url = f"https://wellfound.com/role/r/{keyword.lower().replace(' ', '-')}"

                response = self.session.get(url, timeout=15)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Wellfound uses React, look for job data in script tags
                    script_tags = soup.find_all('script', type='application/json')

                    for script in script_tags:
                        try:
                            data = json.loads(script.string)
                            # Look for job listings in the JSON
                            if isinstance(data, dict) and 'jobs' in data:
                                job_list = data.get('jobs', [])

                                for item in job_list[:max_results]:
                                    title = item.get('title', 'N/A')
                                    company = item.get('company', {}).get('name', 'N/A')
                                    job_location = item.get('location', location)
                                    description = item.get('description', '')
                                    job_url = f"https://wellfound.com/jobs/{item.get('id', '')}"

                                    job = JobOpportunity(
                                        title=title,
                                        company=company,
                                        location=job_location,
                                        job_type="internship",
                                        description=description[:500],
                                        requirements="",
                                        posted_date=datetime.now().strftime("%Y-%m-%d"),
                                        url=job_url,
                                        source="Wellfound",
                                        remote="remote" in description.lower()
                                    )

                                    jobs.append(job)
                        except json.JSONDecodeError:
                            continue
                else:
                    self.logger.warning(f"Wellfound returned status {response.status_code}")

            except Exception as e:
                self.logger.error(f"Wellfound scraping failed for {keyword}: {e}")

        self.logger.info(f"Scraped {len(jobs)} jobs from Wellfound")
        return jobs

    def scrape_remotive(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Scrape Remotive for remote internships"""
        jobs = []

        try:
            # Remotive public API
            url = "https://remotive.com/api/remote-jobs"

            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                data = response.json()
                all_jobs = data.get('jobs', [])

                # Filter by keywords
                for job_data in all_jobs:
                    title = job_data.get('title', '').lower()
                    description = job_data.get('description', '').lower()

                    # Check if any keyword matches
                    if any(kw.lower() in title or kw.lower() in description for kw in keywords):
                        # Check for internship indicators
                        is_internship = any(word in title or word in description
                                          for word in ['intern', 'internship', 'stage', 'stagiaire'])

                        job = JobOpportunity(
                            title=job_data.get('title', 'N/A'),
                            company=job_data.get('company_name', 'N/A'),
                            location=job_data.get('candidate_required_location', 'Remote'),
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

        self.logger.info(f"Scraped {len(jobs)} jobs from Remotive")
        return jobs

    def scrape_glassdoor(
        self,
        keywords: List[str],
        location: str = "France",
        max_results: int = 50,
    ) -> List[JobOpportunity]:
        """Scrape Glassdoor"""
        jobs = []

        # Glassdoor has anti-scraping measures
        # Would need rotating proxies + Selenium
        self.logger.warning("Glassdoor scraping requires advanced setup")

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

    def search_jobs(
        self,
        keywords: List[str],
        location: str = "France",
        job_types: List[str] = ["internship"],
        sources: List[str] = ["indeed"],
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

                elif source.lower() == "themuse" or source.lower() == "muse":
                    jobs = self.scraper.scrape_github_jobs(keywords, location, max_per_source)
                    all_jobs.extend(jobs)

                elif source.lower() == "stackoverflow":
                    jobs = self.scraper.scrape_stack_overflow(keywords, location, max_per_source)
                    all_jobs.extend(jobs)

                elif source.lower() == "adzuna" and os.getenv("ADZUNA_APP_ID"):
                    jobs = self.scraper.scrape_adzuna_with_key(keywords, location, max_per_source)
                    all_jobs.extend(jobs)

                elif source.lower() == "indeed":
                    jobs = self.scraper.scrape_indeed_fr(keywords, location, max_per_source)
                    all_jobs.extend(jobs)

                elif source.lower() == "welcometothejungle" or source.lower() == "wttj":
                    jobs = self.scraper.scrape_welcometothejungle(keywords, location, max_per_source)
                    all_jobs.extend(jobs)

                elif source.lower() == "wellfound" or source.lower() == "angellist":
                    jobs = self.scraper.scrape_wellfound(keywords, location, max_per_source)
                    all_jobs.extend(jobs)

                elif source.lower() == "linkedin":
                    jobs = self.scraper.scrape_linkedin(keywords, location, max_per_source)
                    all_jobs.extend(jobs)

                elif source.lower() == "welcometothejungle" or source.lower() == "wttj":
                    jobs = self.scraper.scrape_welcometothejungle(keywords, location, max_per_source)
                    all_jobs.extend(jobs)

                elif source.lower() == "glassdoor":
                    jobs = self.scraper.scrape_glassdoor(keywords, location, max_per_source)
                    all_jobs.extend(jobs)

            except Exception as e:
                self.logger.error(f"Error scraping {source}: {e}")

        # Filter by job type
        filtered_jobs = [
            job for job in all_jobs
            if any(jt.lower() in job.job_type.lower() for jt in job_types)
        ]

        # Add to database
        self.jobs_db.extend(filtered_jobs)
        self._save_jobs()

        self.logger.info(f"Found {len(filtered_jobs)} jobs matching criteria")
        return filtered_jobs

    def export_to_excel(
        self,
        jobs: Optional[List[JobOpportunity]] = None,
        output_path: str = "data/jobs/opportunities.xlsx",
    ) -> str:
        """Export jobs to Excel"""
        if jobs is None:
            jobs = self.jobs_db

        if not jobs:
            self.logger.warning("No jobs to export")
            return ""

        # Convert to DataFrame
        df = pd.DataFrame([job.to_dict() for job in jobs])

        # Create directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Export to Excel
        df.to_excel(output_path, index=False)

        self.logger.info(f"Exported {len(jobs)} jobs to {output_path}")
        return output_path

    def tailor_application(
        self,
        job: JobOpportunity,
    ) -> Dict[str, str]:
        """
        Tailor resume and generate cover letter for a job

        Returns:
            Dict with 'resume' and 'cover_letter' keys
        """
        if not self.resume_text:
            raise ValueError("No resume loaded. Use load_resume() first.")

        self.logger.info(f"Tailoring application for: {job.title} at {job.company}")

        # Get full job description (would scrape from job.url in production)
        job_description = f"{job.description}\n\nRequirements:\n{job.requirements}"

        # Tailor resume
        tailored_resume = self.ai_agent.tailor_resume(
            self.resume_text,
            job_description,
            format_type="markdown"
        )

        # Generate cover letter
        cover_letter = self.ai_agent.write_cover_letter(
            self.resume_text,
            job_description,
            job.company,
            job.title,
        )

        return {
            "resume": tailored_resume,
            "cover_letter": cover_letter,
            "job": job.to_dict(),
        }

    def batch_apply(
        self,
        job_indices: List[int],
        output_dir: str = "data/jobs/applications",
    ) -> List[Dict[str, Any]]:
        """
        Create tailored applications for multiple jobs

        Args:
            job_indices: Indices of jobs from Excel to apply to
            output_dir: Where to save application files
        """
        results = []

        os.makedirs(output_dir, exist_ok=True)

        for idx in job_indices:
            try:
                if idx >= len(self.jobs_db):
                    self.logger.warning(f"Invalid job index: {idx}")
                    continue

                job = self.jobs_db[idx]

                # Tailor application
                application = self.tailor_application(job)

                # Save files
                company_safe = re.sub(r'[^\w\s-]', '', job.company).strip().replace(' ', '_')
                timestamp = datetime.now().strftime("%Y%m%d")

                resume_path = f"{output_dir}/{company_safe}_{timestamp}_resume.md"
                cover_path = f"{output_dir}/{company_safe}_{timestamp}_cover_letter.md"

                with open(resume_path, 'w', encoding='utf-8') as f:
                    f.write(application['resume'])

                with open(cover_path, 'w', encoding='utf-8') as f:
                    f.write(application['cover_letter'])

                job.applied = True

                results.append({
                    "job": job.to_dict(),
                    "resume_path": resume_path,
                    "cover_letter_path": cover_path,
                    "status": "success"
                })

                self.logger.info(f"Application created for {job.company}")

            except Exception as e:
                self.logger.error(f"Failed to create application for job {idx}: {e}")
                results.append({
                    "job_index": idx,
                    "status": "failed",
                    "error": str(e)
                })

        self._save_jobs()

        return results

    def _load_jobs(self):
        """Load jobs from database"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.jobs_db = [JobOpportunity(**job) for job in data]
                    self.logger.info(f"Loaded {len(self.jobs_db)} jobs from database")
        except Exception as e:
            self.logger.error(f"Failed to load jobs: {e}")

    def _save_jobs(self):
        """Save jobs to database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump([job.to_dict() for job in self.jobs_db], f, indent=2)

            self.logger.info(f"Saved {len(self.jobs_db)} jobs to database")
        except Exception as e:
            self.logger.error(f"Failed to save jobs: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get job hunting statistics"""
        total = len(self.jobs_db)
        applied = len([j for j in self.jobs_db if j.applied])
        by_source = {}
        by_type = {}

        for job in self.jobs_db:
            by_source[job.source] = by_source.get(job.source, 0) + 1
            by_type[job.job_type] = by_type.get(job.job_type, 0) + 1

        return {
            "total_jobs": total,
            "applied": applied,
            "pending": total - applied,
            "by_source": by_source,
            "by_type": by_type,
            "resume_loaded": self.resume_text is not None,
        }


def get_job_hunter() -> JobHunter:
    """Get JobHunter singleton"""
    return JobHunter()
