"""
Cover Letter Generator
AI-powered cover letter creation
"""

from datetime import datetime
from typing import Optional

from src.ai.ai_agent import get_ai_agent
from src.core.logger import setup_logger


class CoverLetterGenerator:
    """Generate personalized cover letters"""
    
    def __init__(self):
        self.logger = setup_logger("jobs.cover_letter")
        self.ai_agent = get_ai_agent()
    
    def generate(
        self,
        resume_text: str,
        job_description: str,
        company_name: str,
        position_title: str,
        applicant_name: Optional[str] = None,
        hiring_manager: Optional[str] = None,
        format_type: str = "markdown",
    ) -> str:
        """
        Generate personalized cover letter
        
        Args:
            resume_text: Applicant's resume
            job_description: Full job posting
            company_name: Company name
            position_title: Job title
            applicant_name: Applicant's name (extracted from resume if not provided)
            hiring_manager: Hiring manager's name if known
            format_type: Output format
        """
        self.logger.info(f"Generating cover letter for {position_title} at {company_name}")
        
        # Extract applicant name from resume if not provided
        if not applicant_name:
            applicant_name = self._extract_name(resume_text)
        
        # Build prompt
        salutation = f"Dear {hiring_manager}," if hiring_manager else "Dear Hiring Manager,"
        
        prompt = f"""You are a professional cover letter writer. Write a compelling, personalized cover letter.

**Applicant Information:**
Name: {applicant_name}
Resume Summary:
{resume_text[:1000]}...

**Job Details:**
Company: {company_name}
Position: {position_title}
Description:
{job_description[:1500]}...

**Instructions:**
1. Opening: Express enthusiasm and explain why you're interested in THIS specific company and role
2. Body Paragraphs (2-3):
   - Highlight 2-3 most relevant experiences from resume that match job requirements
   - Use specific examples with quantifiable results
   - Show how your skills directly address their needs
   - Demonstrate knowledge of the company/industry
3. Closing: 
   - Reiterate interest and value you'd bring
   - Call to action (request interview)
   - Professional sign-off

**Style:**
- Professional but conversational tone
- Confident without being arrogant
- Specific and concrete, not generic
- Keep to 3-4 paragraphs, ~300-400 words
- Format in {format_type}

**Cover Letter:**

{salutation}

"""
        
        cover_letter = self.ai_agent.chat(prompt)
        
        # Add date and signature if not present
        if "Sincerely" not in cover_letter and "Best regards" not in cover_letter:
            cover_letter += f"\n\nSincerely,\n{applicant_name}"
        
        self.logger.info("Cover letter generated successfully")
        return cover_letter
    
    def _extract_name(self, resume_text: str) -> str:
        """Extract applicant name from resume"""
        # Usually the first line
        lines = resume_text.strip().split('\n')
        if lines:
            # Clean up name
            name = lines[0].strip()
            # Remove common resume headers
            name = name.replace('Resume', '').replace('CV', '').replace('|', '').strip()
            if len(name.split()) <= 4 and name:  # Reasonable name length
                return name
        
        return "Your Name"
    
    def generate_from_template(
        self,
        template: str,
        variables: dict,
    ) -> str:
        """
        Generate cover letter from template
        
        Args:
            template: Cover letter template with {placeholders}
            variables: Dict of placeholder values
        """
        try:
            return template.format(**variables)
        except KeyError as e:
            self.logger.error(f"Missing variable in template: {e}")
            return template
    
    def get_default_template(self) -> str:
        """Get default cover letter template"""
        return """Dear {hiring_manager},

I am writing to express my strong interest in the {position_title} position at {company_name}. {opening_paragraph}

{body_paragraph_1}

{body_paragraph_2}

{closing_paragraph}

Thank you for considering my application. I look forward to the opportunity to discuss how my skills and experiences align with your team's needs.

Sincerely,
{applicant_name}
"""


def get_cover_letter_generator() -> CoverLetterGenerator:
    """Get CoverLetterGenerator singleton"""
    return CoverLetterGenerator()
