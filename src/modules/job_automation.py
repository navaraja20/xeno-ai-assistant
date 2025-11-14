"""
Job application automation module for XENO AI Assistant.
Handles job searching on LinkedIn and Indeed, tracking applications.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from datetime import datetime
import time
import re

logger = logging.getLogger("XENO.JobAutomation")


class JobAutomation:
    """Handles job search and application tracking."""
    
    def __init__(self):
        """Initialize job automation."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        logger.info("JobAutomation initialized")
    
    def search_indeed(self, job_title: str, location: str = '', 
                     max_results: int = 20) -> List[Dict]:
        """
        Search for jobs on Indeed.
        
        Args:
            job_title: Job title or keywords
            location: Job location
            max_results: Maximum number of results
            
        Returns:
            List of job dictionaries
        """
        try:
            jobs = []
            
            # Build search URL
            params = {
                'q': job_title,
                'l': location,
                'sort': 'date'
            }
            
            url = "https://www.indeed.com/jobs"
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Indeed returned status code {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards (Indeed's structure changes frequently)
            job_cards = soup.find_all('div', class_=re.compile(r'job_seen_beacon'))
            
            for card in job_cards[:max_results]:
                try:
                    # Extract job details
                    title_elem = card.find('h2', class_=re.compile(r'jobTitle'))
                    company_elem = card.find('span', class_=re.compile(r'companyName'))
                    location_elem = card.find('div', class_=re.compile(r'companyLocation'))
                    
                    if not title_elem:
                        continue
                    
                    # Get job URL
                    link_elem = title_elem.find('a')
                    job_url = ''
                    if link_elem and 'href' in link_elem.attrs:
                        job_url = 'https://www.indeed.com' + link_elem['href']
                    
                    jobs.append({
                        'title': title_elem.get_text(strip=True),
                        'company': company_elem.get_text(strip=True) if company_elem else 'Unknown',
                        'location': location_elem.get_text(strip=True) if location_elem else '',
                        'url': job_url,
                        'source': 'Indeed',
                        'found_date': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.error(f"Error parsing job card: {e}")
                    continue
            
            logger.info(f"Found {len(jobs)} jobs on Indeed for '{job_title}'")
            return jobs
            
        except Exception as e:
            logger.error(f"Error searching Indeed: {e}")
            return []
    
    def search_linkedin(self, job_title: str, location: str = '',
                       max_results: int = 20) -> List[Dict]:
        """
        Search for jobs on LinkedIn (basic scraping, no login required).
        
        Args:
            job_title: Job title or keywords
            location: Job location
            max_results: Maximum number of results
            
        Returns:
            List of job dictionaries
        """
        try:
            jobs = []
            
            # LinkedIn jobs URL
            params = {
                'keywords': job_title,
                'location': location,
                'sortBy': 'DD'  # Sort by date
            }
            
            url = "https://www.linkedin.com/jobs/search"
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"LinkedIn returned status code {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards
            job_cards = soup.find_all('div', class_=re.compile(r'job-search-card'))
            
            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find('h3', class_=re.compile(r'job-search-card__title'))
                    company_elem = card.find('h4', class_=re.compile(r'job-search-card__company-name'))
                    location_elem = card.find('span', class_=re.compile(r'job-search-card__location'))
                    link_elem = card.find('a', class_=re.compile(r'job-search-card'))
                    
                    if not title_elem:
                        continue
                    
                    job_url = ''
                    if link_elem and 'href' in link_elem.attrs:
                        job_url = link_elem['href']
                    
                    jobs.append({
                        'title': title_elem.get_text(strip=True),
                        'company': company_elem.get_text(strip=True) if company_elem else 'Unknown',
                        'location': location_elem.get_text(strip=True) if location_elem else '',
                        'url': job_url,
                        'source': 'LinkedIn',
                        'found_date': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.error(f"Error parsing job card: {e}")
                    continue
            
            logger.info(f"Found {len(jobs)} jobs on LinkedIn for '{job_title}'")
            return jobs
            
        except Exception as e:
            logger.error(f"Error searching LinkedIn: {e}")
            return []
    
    def search_all_platforms(self, job_title: str, location: str = '',
                           max_per_platform: int = 10) -> List[Dict]:
        """
        Search for jobs across all platforms.
        
        Args:
            job_title: Job title or keywords
            location: Job location
            max_per_platform: Max results per platform
            
        Returns:
            Combined list of jobs from all platforms
        """
        all_jobs = []
        
        # Search Indeed
        indeed_jobs = self.search_indeed(job_title, location, max_per_platform)
        all_jobs.extend(indeed_jobs)
        
        # Wait a bit to avoid rate limiting
        time.sleep(2)
        
        # Search LinkedIn
        linkedin_jobs = self.search_linkedin(job_title, location, max_per_platform)
        all_jobs.extend(linkedin_jobs)
        
        logger.info(f"Found {len(all_jobs)} total jobs across all platforms")
        return all_jobs
    
    def filter_jobs(self, jobs: List[Dict], keywords: List[str] = None,
                   exclude_keywords: List[str] = None) -> List[Dict]:
        """
        Filter jobs by keywords.
        
        Args:
            jobs: List of job dictionaries
            keywords: Required keywords (must contain at least one)
            exclude_keywords: Keywords to exclude (must not contain any)
            
        Returns:
            Filtered list of jobs
        """
        filtered = []
        
        for job in jobs:
            # Combine title and company for searching
            text = f"{job['title']} {job['company']}".lower()
            
            # Check exclude keywords
            if exclude_keywords:
                if any(kw.lower() in text for kw in exclude_keywords):
                    continue
            
            # Check required keywords
            if keywords:
                if not any(kw.lower() in text for kw in keywords):
                    continue
            
            filtered.append(job)
        
        logger.info(f"Filtered to {len(filtered)} jobs from {len(jobs)}")
        return filtered
    
    def get_job_details(self, job_url: str) -> Optional[Dict]:
        """
        Get detailed information about a job posting.
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Dictionary with job details
        """
        try:
            response = self.session.get(job_url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract description (structure varies by site)
            description_elem = soup.find('div', class_=re.compile(r'jobsearch-jobDescriptionText|description'))
            
            if description_elem:
                description = description_elem.get_text(strip=True)
            else:
                description = "Description not available"
            
            return {
                'url': job_url,
                'description': description[:1000],  # First 1000 chars
                'full_description': description
            }
            
        except Exception as e:
            logger.error(f"Error getting job details: {e}")
            return None
    
    def save_job(self, job: Dict, database_session) -> bool:
        """
        Save a job to the database.
        
        Args:
            job: Job dictionary
            database_session: SQLAlchemy session
            
        Returns:
            True if saved successfully
        """
        try:
            from ..models.database import JobApplication
            
            # Check if job already exists
            existing = database_session.query(JobApplication).filter_by(
                url=job.get('url', '')
            ).first()
            
            if existing:
                logger.info(f"Job already saved: {job['title']}")
                return False
            
            # Create new job application
            application = JobApplication(
                title=job.get('title', ''),
                company=job.get('company', ''),
                location=job.get('location', ''),
                description=job.get('description', ''),
                url=job.get('url', ''),
                status='saved',
                source=job.get('source', 'Unknown'),
                extra_data={}
            )
            
            database_session.add(application)
            database_session.commit()
            
            logger.info(f"Saved job: {job['title']} at {job['company']}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving job: {e}")
            database_session.rollback()
            return False
    
    def get_saved_jobs(self, database_session, status: str = None) -> List[Dict]:
        """
        Get saved jobs from database.
        
        Args:
            database_session: SQLAlchemy session
            status: Filter by status (saved, applied, interviewing, rejected)
            
        Returns:
            List of saved jobs
        """
        try:
            from ..models.database import JobApplication
            
            query = database_session.query(JobApplication)
            
            if status:
                query = query.filter_by(status=status)
            
            jobs = query.order_by(JobApplication.created_at.desc()).all()
            
            return [
                {
                    'id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'description': job.description,
                    'url': job.url,
                    'status': job.status,
                    'source': job.source,
                    'created': job.created_at.isoformat()
                }
                for job in jobs
            ]
            
        except Exception as e:
            logger.error(f"Error getting saved jobs: {e}")
            return []
    
    def update_job_status(self, database_session, job_id: int, 
                         status: str, notes: str = '') -> bool:
        """
        Update job application status.
        
        Args:
            database_session: SQLAlchemy session
            job_id: Job ID
            status: New status (saved, applied, interviewing, rejected, accepted)
            notes: Optional notes
            
        Returns:
            True if updated successfully
        """
        try:
            from ..models.database import JobApplication
            
            job = database_session.query(JobApplication).get(job_id)
            
            if not job:
                logger.error(f"Job {job_id} not found")
                return False
            
            job.status = status
            job.updated_at = datetime.now()
            
            if notes:
                if not job.extra_data:
                    job.extra_data = {}
                if 'notes' not in job.extra_data:
                    job.extra_data['notes'] = []
                job.extra_data['notes'].append({
                    'date': datetime.now().isoformat(),
                    'text': notes
                })
            
            database_session.commit()
            
            logger.info(f"Updated job {job_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating job status: {e}")
            database_session.rollback()
            return False
