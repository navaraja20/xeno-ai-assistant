"""
Resume Tailor
AI-powered resume customization for job applications
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass

from src.ai.ai_agent import get_ai_agent
from src.core.logger import setup_logger


@dataclass
class ResumeSection:
    """A section of a resume"""
    title: str
    content: str
    priority: int = 0  # Higher = more important for this job


class ResumeTailor:
    """Tailor resumes to match job descriptions"""
    
    def __init__(self):
        self.logger = setup_logger("jobs.resume_tailor")
        self.ai_agent = get_ai_agent()
    
    def parse_resume(self, resume_text: str) -> Dict[str, str]:
        """Parse resume into sections"""
        sections = {}
        
        # Common section headers
        section_patterns = [
            r'(?i)(summary|profile|objective)',
            r'(?i)(experience|employment|work history)',
            r'(?i)(education)',
            r'(?i)(skills|technical skills|competencies)',
            r'(?i)(projects)',
            r'(?i)(certifications?|licenses?)',
            r'(?i)(publications?)',
            r'(?i)(awards?|honors?)',
        ]
        
        current_section = "header"
        current_content = []
        
        for line in resume_text.split('\n'):
            # Check if this is a section header
            is_section = False
            for pattern in section_patterns:
                if re.match(pattern, line.strip()):
                    # Save previous section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    current_section = line.strip()
                    current_content = []
                    is_section = True
                    break
            
            if not is_section:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def analyze_job_requirements(self, job_description: str) -> Dict[str, List[str]]:
        """Extract key requirements from job description"""
        prompt = f"""Analyze this job description and extract:
1. Required technical skills
2. Preferred qualifications
3. Key responsibilities
4. Industry keywords

Job Description:
{job_description}

Return a JSON object with these keys: required_skills, preferred_skills, responsibilities, keywords
"""
        
        try:
            response = self.ai_agent.chat(prompt)
            
            # Parse AI response
            import json
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                # Fallback: manual extraction
                analysis = {
                    "required_skills": self._extract_skills(job_description),
                    "preferred_skills": [],
                    "responsibilities": [],
                    "keywords": []
                }
            
            return analysis
        
        except Exception as e:
            self.logger.error(f"Failed to analyze job: {e}")
            return {
                "required_skills": [],
                "preferred_skills": [],
                "responsibilities": [],
                "keywords": []
            }
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from text"""
        # Common Data Science skills
        skill_keywords = [
            "python", "r", "sql", "java", "c++", "scala",
            "machine learning", "deep learning", "nlp", "computer vision",
            "tensorflow", "pytorch", "keras", "scikit-learn",
            "pandas", "numpy", "matplotlib", "seaborn",
            "spark", "hadoop", "aws", "azure", "gcp",
            "docker", "kubernetes", "git",
            "statistics", "mathematics", "linear algebra",
            "regression", "classification", "clustering",
            "neural networks", "cnn", "rnn", "transformer",
            "data analysis", "data visualization", "etl",
        ]
        
        text_lower = text.lower()
        found_skills = [skill for skill in skill_keywords if skill in text_lower]
        
        return found_skills
    
    def tailor_resume(
        self,
        resume_text: str,
        job_description: str,
        format_type: str = "markdown",
    ) -> str:
        """
        Tailor resume to match job description
        
        Args:
            resume_text: Original resume content
            job_description: Job posting text
            format_type: Output format (markdown, latex, html)
        """
        self.logger.info("Tailoring resume...")
        
        # Parse resume
        sections = self.parse_resume(resume_text)
        
        # Analyze job
        job_analysis = self.analyze_job_requirements(job_description)
        
        # Build tailored resume with AI
        prompt = f"""You are a professional resume writer. Tailor this resume to match the job description.

**Original Resume:**
{resume_text}

**Job Requirements:**
- Required Skills: {', '.join(job_analysis.get('required_skills', []))}
- Preferred Skills: {', '.join(job_analysis.get('preferred_skills', []))}
- Key Responsibilities: {', '.join(job_analysis.get('responsibilities', []))}

**Instructions:**
1. Emphasize relevant skills and experiences that match the job
2. Reorder bullet points to highlight most relevant first
3. Add keywords from the job description naturally
4. Keep it concise and ATS-friendly
5. Maintain truthfulness - don't add fake experience
6. Format in {format_type}

**Tailored Resume:**
"""
        
        tailored = self.ai_agent.chat(prompt)
        
        self.logger.info("Resume tailored successfully")
        return tailored
    
    def calculate_match_score(
        self,
        resume_text: str,
        job_description: str,
    ) -> float:
        """
        Calculate how well resume matches job (0-100)
        """
        # Extract skills from both
        job_skills = set(self._extract_skills(job_description))
        resume_skills = set(self._extract_skills(resume_text))
        
        if not job_skills:
            return 0.0
        
        # Calculate overlap
        matching_skills = job_skills & resume_skills
        score = (len(matching_skills) / len(job_skills)) * 100
        
        return round(score, 1)
    
    def suggest_improvements(
        self,
        resume_text: str,
        job_description: str,
    ) -> List[str]:
        """Suggest resume improvements for this job"""
        job_analysis = self.analyze_job_requirements(job_description)
        resume_skills = set(self._extract_skills(resume_text))
        required_skills = set(job_analysis.get('required_skills', []))
        
        suggestions = []
        
        # Missing required skills
        missing = required_skills - resume_skills
        if missing:
            suggestions.append(f"Add these skills if you have them: {', '.join(missing)}")
        
        # Check resume length
        word_count = len(resume_text.split())
        if word_count > 800:
            suggestions.append("Resume is too long. Keep it under 2 pages (500-800 words)")
        elif word_count < 300:
            suggestions.append("Resume is too short. Add more details about your experience")
        
        # Check for keywords
        keywords = job_analysis.get('keywords', [])
        missing_keywords = [kw for kw in keywords if kw.lower() not in resume_text.lower()]
        if missing_keywords:
            suggestions.append(f"Consider adding these keywords: {', '.join(missing_keywords[:5])}")
        
        # Check for quantifiable achievements
        if not re.search(r'\d+%|\d+x|\d+ [a-z]+', resume_text):
            suggestions.append("Add quantifiable achievements (e.g., 'Improved accuracy by 15%')")
        
        return suggestions


def get_resume_tailor() -> ResumeTailor:
    """Get ResumeTailor singleton"""
    return ResumeTailor()
