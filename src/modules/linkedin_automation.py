"""
LinkedIn automation module for XENO AI Assistant.
Handles LinkedIn profile updates, connections, and posts using browser automation.
"""

import logging
import time
from typing import Dict, List, Optional

from playwright.sync_api import Browser, Page, sync_playwright

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
            self.page.goto("https://www.linkedin.com/login")
            time.sleep(2)

            # Fill login form
            self.page.fill('input[name="session_key"]', self.email)
            self.page.fill('input[name="session_password"]', self.password)

            # Click sign in
            self.page.click('button[type="submit"]')
            time.sleep(3)

            # Check if login successful
            if "feed" in self.page.url or "mynetwork" in self.page.url:
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
            self.page.goto("https://www.linkedin.com/in/me/")
            time.sleep(3)

            profile_info = {}

            # Get name
            try:
                name_elem = self.page.query_selector("h1.text-heading-xlarge")
                if name_elem:
                    profile_info["name"] = name_elem.inner_text()
            except:
                pass

            # Get headline
            try:
                headline_elem = self.page.query_selector("div.text-body-medium")
                if headline_elem:
                    profile_info["headline"] = headline_elem.inner_text()
            except:
                pass

            # Get connections count
            try:
                connections_elem = self.page.query_selector("span.t-bold")
                if connections_elem:
                    profile_info["connections"] = connections_elem.inner_text()
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
            self.page.goto("https://www.linkedin.com/feed/")
            time.sleep(2)

            # Click "Start a post" button
            start_post_button = self.page.query_selector('button[aria-label*="Start a post"]')
            if not start_post_button:
                start_post_button = self.page.query_selector(".share-box-feed-entry__trigger")

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

    def send_connection_request(self, profile_url: str, message: str = "") -> bool:
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
            self.page.goto("https://www.linkedin.com/notifications/")
            time.sleep(3)

            notifications = []

            # Get notification items
            notification_items = self.page.query_selector_all(".notification-card")

            for item in notification_items[:10]:  # Get latest 10
                try:
                    text = item.inner_text()
                    notifications.append({"text": text, "timestamp": datetime.now().isoformat()})
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
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={keywords}"
            self.page.goto(search_url)
            time.sleep(3)

            people = []

            # Get search results
            result_items = self.page.query_selector_all(".entity-result")

            for item in result_items[:max_results]:
                try:
                    # Get profile link
                    link_elem = item.query_selector("a.app-aware-link")
                    profile_url = link_elem.get_attribute("href") if link_elem else ""

                    # Get name
                    name_elem = item.query_selector(".entity-result__title-text a span")
                    name = name_elem.inner_text() if name_elem else "Unknown"

                    # Get headline
                    headline_elem = item.query_selector(".entity-result__primary-subtitle")
                    headline = headline_elem.inner_text() if headline_elem else ""

                    people.append({"name": name, "headline": headline, "profile_url": profile_url})

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
            self.page.goto("https://www.linkedin.com/jobs/")
            time.sleep(3)

            jobs = []

            # Get job cards
            job_cards = self.page.query_selector_all(".job-card-container")

            for card in job_cards[:max_results]:
                try:
                    # Get job title
                    title_elem = card.query_selector(".job-card-list__title")
                    title = title_elem.inner_text() if title_elem else "Unknown"

                    # Get company
                    company_elem = card.query_selector(".job-card-container__company-name")
                    company = company_elem.inner_text() if company_elem else "Unknown"

                    # Get location
                    location_elem = card.query_selector(".job-card-container__metadata-item")
                    location = location_elem.inner_text() if location_elem else ""

                    # Get job URL
                    link_elem = card.query_selector("a")
                    job_url = link_elem.get_attribute("href") if link_elem else ""

                    jobs.append(
                        {"title": title, "company": company, "location": location, "url": job_url}
                    )

                except:
                    continue

            logger.info(f"Retrieved {len(jobs)} job recommendations")
            return jobs

        except Exception as e:
            logger.error(f"Error getting job recommendations: {e}")
            return []

    def search_jobs(
        self,
        keywords: str,
        location: str = "",
        job_type: str = "",
        experience_level: str = "",
        remote: bool = False,
        max_results: int = 25,
    ) -> List[Dict]:
        """
        Search for jobs with advanced filters.

        Args:
            keywords: Job search keywords (e.g., "Python Developer")
            location: Job location (e.g., "New York, NY")
            job_type: Job type filter ("Full-time", "Part-time", "Contract", "Internship")
            experience_level: Experience level ("Entry level", "Associate", "Mid-Senior level", "Director", "Executive")
            remote: Filter for remote jobs only
            max_results: Maximum number of results to return

        Returns:
            List of job dictionaries with details
        """
        try:
            if not self.is_logged_in:
                self.login()

            # Build search URL
            base_url = "https://www.linkedin.com/jobs/search/?"
            params = []

            if keywords:
                params.append(f'keywords={keywords.replace(" ", "%20")}')
            if location:
                params.append(f'location={location.replace(" ", "%20")}')
            if job_type:
                type_map = {"Full-time": "F", "Part-time": "P", "Contract": "C", "Internship": "I"}
                if job_type in type_map:
                    params.append(f"f_JT={type_map[job_type]}")
            if experience_level:
                level_map = {
                    "Entry level": "2",
                    "Associate": "3",
                    "Mid-Senior level": "4",
                    "Director": "5",
                    "Executive": "6",
                }
                if experience_level in level_map:
                    params.append(f"f_E={level_map[experience_level]}")
            if remote:
                params.append("f_WT=2")  # Remote work type

            search_url = base_url + "&".join(params)

            # Navigate to search results
            self.page.goto(search_url)
            time.sleep(3)

            jobs = []

            # Scroll to load more jobs
            for _ in range(3):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)

            # Get job cards
            job_cards = self.page.query_selector_all(
                ".job-card-container, .jobs-search-results__list-item"
            )

            for card in job_cards[:max_results]:
                try:
                    # Click on job card to load details
                    card.click()
                    time.sleep(1)

                    # Get job title
                    title_elem = self.page.query_selector(
                        ".job-details-jobs-unified-top-card__job-title"
                    )
                    if not title_elem:
                        title_elem = card.query_selector(
                            ".job-card-list__title, .job-card-container__link"
                        )
                    title = title_elem.inner_text().strip() if title_elem else "Unknown"

                    # Get company
                    company_elem = self.page.query_selector(
                        ".job-details-jobs-unified-top-card__company-name"
                    )
                    if not company_elem:
                        company_elem = card.query_selector(".job-card-container__company-name")
                    company = company_elem.inner_text().strip() if company_elem else "Unknown"

                    # Get location
                    location_elem = self.page.query_selector(
                        ".job-details-jobs-unified-top-card__bullet"
                    )
                    if not location_elem:
                        location_elem = card.query_selector(".job-card-container__metadata-item")
                    location_text = location_elem.inner_text().strip() if location_elem else ""

                    # Get job description
                    desc_elem = self.page.query_selector(".jobs-description__content")
                    description = desc_elem.inner_text().strip() if desc_elem else ""

                    # Get job URL
                    job_url = self.page.url

                    # Check if Easy Apply available
                    easy_apply_btn = self.page.query_selector('button[aria-label*="Easy Apply"]')
                    is_easy_apply = easy_apply_btn is not None

                    # Get salary info if available
                    salary_elem = self.page.query_selector(
                        ".job-details-jobs-unified-top-card__job-insight"
                    )
                    salary = salary_elem.inner_text().strip() if salary_elem else None

                    jobs.append(
                        {
                            "title": title,
                            "company": company,
                            "location": location_text,
                            "url": job_url,
                            "description": description[:500],  # First 500 chars
                            "is_easy_apply": is_easy_apply,
                            "salary": salary,
                            "posted_date": datetime.now().strftime("%Y-%m-%d"),
                            "applied": False,
                        }
                    )

                except Exception as e:
                    logger.debug(f"Error parsing job card: {e}")
                    continue

            logger.info(f"Found {len(jobs)} jobs for '{keywords}'")
            return jobs

        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return []

    def apply_to_job(
        self, job_url: str, cover_letter: str = None, phone: str = None, resume_path: str = None
    ) -> bool:
        """
        Apply to a job using Easy Apply.

        Args:
            job_url: URL of the job posting
            cover_letter: Optional cover letter text
            phone: Phone number if required
            resume_path: Path to resume file if upload required

        Returns:
            True if application submitted successfully
        """
        try:
            if not self.is_logged_in:
                self.login()

            # Navigate to job posting
            self.page.goto(job_url)
            time.sleep(2)

            # Click Easy Apply button
            easy_apply_btn = self.page.query_selector('button[aria-label*="Easy Apply"]')
            if not easy_apply_btn:
                logger.warning("Easy Apply not available for this job")
                return False

            easy_apply_btn.click()
            time.sleep(2)

            # Multi-step application process
            max_steps = 5
            for step in range(max_steps):
                try:
                    # Check if phone number is required
                    if phone:
                        phone_input = self.page.query_selector('input[id*="phoneNumber"]')
                        if phone_input and not phone_input.input_value():
                            phone_input.fill(phone)
                            time.sleep(0.5)

                    # Check for resume upload
                    if resume_path:
                        file_input = self.page.query_selector('input[type="file"]')
                        if file_input:
                            file_input.set_input_files(resume_path)
                            time.sleep(1)

                    # Check for cover letter
                    if cover_letter:
                        cover_letter_input = self.page.query_selector('textarea[id*="coverLetter"]')
                        if not cover_letter_input:
                            cover_letter_input = self.page.query_selector("textarea")
                        if cover_letter_input and not cover_letter_input.input_value():
                            cover_letter_input.fill(cover_letter)
                            time.sleep(0.5)

                    # Fill any required text inputs with placeholder
                    text_inputs = self.page.query_selector_all(
                        'input[required]:not([type="file"]):not([type="checkbox"]):not([type="radio"])'
                    )
                    for inp in text_inputs:
                        if not inp.input_value():
                            # Try to infer what to fill based on label
                            label = (
                                inp.get_attribute("aria-label")
                                or inp.get_attribute("placeholder")
                                or ""
                            )
                            if "experience" in label.lower():
                                inp.fill("3")
                            elif "why" in label.lower() or "interest" in label.lower():
                                inp.fill(
                                    "I am very interested in this position and believe my skills align well with the requirements."
                                )

                    # Click Next button or Submit
                    next_btn = self.page.query_selector('button[aria-label*="Continue"]')
                    if not next_btn:
                        next_btn = self.page.query_selector('button[aria-label*="Review"]')
                    if not next_btn:
                        next_btn = self.page.query_selector(
                            'button[aria-label*="Submit application"]'
                        )
                    if not next_btn:
                        next_btn = self.page.query_selector('button:has-text("Next")')
                    if not next_btn:
                        next_btn = self.page.query_selector('button:has-text("Submit")')

                    if next_btn:
                        next_btn.click()
                        time.sleep(2)

                        # Check if application was submitted
                        success_message = self.page.query_selector(
                            'h3:has-text("Application sent")'
                        )
                        if not success_message:
                            success_message = self.page.query_selector(
                                'h2:has-text("Your application was sent")'
                            )

                        if success_message:
                            logger.info(f"Successfully applied to job: {job_url}")

                            # Close the modal
                            close_btn = self.page.query_selector('button[aria-label*="Dismiss"]')
                            if close_btn:
                                close_btn.click()

                            return True
                    else:
                        # No next button, might be done or error
                        break

                except Exception as e:
                    logger.debug(f"Error in application step {step + 1}: {e}")
                    break

            logger.warning("Application process incomplete - may require manual completion")
            return False

        except Exception as e:
            logger.error(f"Failed to apply to job: {e}")
            return False

    def generate_cover_letter_ai(self, job_details: Dict, user_info: Dict = None) -> str:
        """
        Generate a cover letter using AI based on job details.

        Args:
            job_details: Dictionary with job title, company, description
            user_info: Optional user info (name, experience, skills)

        Returns:
            Generated cover letter text
        """
        try:
            # This will integrate with the AI chat module
            import os

            from .ai_chat import AIChat

            ai = AIChat(api_key=os.getenv("GEMINI_API_KEY"))

            user_name = user_info.get("name", "Applicant") if user_info else "Applicant"
            user_experience = user_info.get("experience", "") if user_info else ""
            user_skills = user_info.get("skills", "") if user_info else ""

            prompt = f"""
Generate a professional cover letter for the following job application:

Job Title: {job_details.get('title', 'Unknown')}
Company: {job_details.get('company', 'Unknown')}
Job Description: {job_details.get('description', '')[:1000]}

Applicant Name: {user_name}
{"Experience: " + user_experience if user_experience else ""}
{"Skills: " + user_skills if user_skills else ""}

Please write a concise, professional cover letter (200-300 words) that:
1. Expresses genuine interest in the position
2. Highlights relevant skills and experience
3. Explains why the candidate is a good fit
4. Maintains a professional yet personable tone
5. Does NOT include any placeholder text or brackets

Start directly with the letter content, no need for "Dear Hiring Manager" greeting.
"""

            response = ai.send_message(prompt)
            logger.info("Generated AI cover letter")
            return response

        except Exception as e:
            logger.error(f"Failed to generate cover letter: {e}")
            # Fallback template
            return f"I am writing to express my strong interest in the {job_details.get('title', 'position')} role at {job_details.get('company', 'your company')}. I believe my skills and experience make me an excellent candidate for this opportunity."


from datetime import datetime
