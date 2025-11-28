"""
Job Hunter Module
Intelligent job search and application automation
"""

from src.jobs.cover_letter_generator import CoverLetterGenerator, get_cover_letter_generator
from src.jobs.job_hunter import JobHunter, JobOpportunity, JobScraper, get_job_hunter
from src.jobs.job_hunter_ui import JobHunterWidget
from src.jobs.resume_tailor import ResumeTailor, get_resume_tailor

__all__ = [
    # Core
    "JobOpportunity",
    "JobScraper",
    "JobHunter",
    "get_job_hunter",
    # Resume
    "ResumeTailor",
    "get_resume_tailor",
    # Cover Letter
    "CoverLetterGenerator",
    "get_cover_letter_generator",
    # UI
    "JobHunterWidget",
]
