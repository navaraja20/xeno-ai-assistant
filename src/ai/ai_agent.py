"""
AI Agent Core
Local LLM integration with Ollama + Gemini fallback
"""

import json
import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import google.generativeai as genai
import requests

from src.core.logger import setup_logger


class ModelProvider(Enum):
    """AI model providers"""

    LOCAL = "local"  # Ollama
    GEMINI = "gemini"  # Google Gemini
    AUTO = "auto"  # Choose best available


@dataclass
class Message:
    """Chat message"""

    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class Tool:
    """AI tool definition"""

    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]


class AIAgent:
    """XENO AI Agent with local and cloud LLM support"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        self.logger = setup_logger("ai.agent")

        # Ollama setup (local) - Using D drive to save C drive space
        self.ollama_available = False
        self.ollama_base_url = "http://localhost:11434"
        self.current_local_model = "llama3.1:8b"

        # Set Ollama to use D drive
        os.environ["OLLAMA_MODELS"] = r"D:\Ollama\models"
        os.environ["OLLAMA_HOME"] = r"D:\Ollama"

        # Gemini setup (cloud)
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_available = False

        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel("gemini-pro")
                self.gemini_available = True
                self.logger.info("Gemini API configured")
            except Exception as e:
                self.logger.error(f"Gemini setup failed: {e}")

        # Check Ollama availability
        self._check_ollama()

        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 10

        # Default provider
        self.default_provider = ModelProvider.AUTO

        self._initialized = True
        self.logger.info("AI Agent initialized")

    def _check_ollama(self):
        """Check if Ollama is running"""
        try:
            import requests

            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                self.ollama_available = True
                models = response.json().get("models", [])
                if models:
                    self.logger.info(f"Ollama available with {len(models)} models")
                else:
                    self.logger.warning("Ollama running but no models installed")
            else:
                self.ollama_available = False
        except Exception as e:
            self.ollama_available = False
            self.logger.warning("Ollama not available (install with: ollama pull llama3.1)")

    def chat(
        self,
        message: str,
        provider: ModelProvider = ModelProvider.AUTO,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Chat with AI agent

        Args:
            message: User message
            provider: Which AI provider to use
            system_prompt: Optional system instruction
            temperature: Response creativity (0-1)
            max_tokens: Maximum response length
        """
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})

        # Keep history manageable
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history * 2 :]

        # Choose provider
        if provider == ModelProvider.AUTO:
            # Prefer local for privacy, fallback to Gemini
            if self.ollama_available:
                provider = ModelProvider.LOCAL
            elif self.gemini_available:
                provider = ModelProvider.GEMINI
            else:
                return "❌ No AI provider available. Please install Ollama or configure Gemini API."

        # Generate response
        try:
            if provider == ModelProvider.LOCAL:
                response = self._chat_ollama(message, system_prompt, temperature, max_tokens)
            elif provider == ModelProvider.GEMINI:
                response = self._chat_gemini(message, system_prompt, temperature, max_tokens)
            else:
                response = "❌ Invalid provider"

            # Add to history
            self.conversation_history.append({"role": "assistant", "content": response})

            return response

        except Exception as e:
            self.logger.error(f"Chat failed: {e}")
            return f"❌ Error: {str(e)}"

    def _chat_ollama(
        self,
        message: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Chat with local Ollama model"""
        import requests

        # Build prompt with history
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add recent history
        messages.extend(self.conversation_history[-6:])  # Last 3 exchanges

        data = {
            "model": self.current_local_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        response = requests.post(f"{self.ollama_base_url}/api/chat", json=data, timeout=60)

        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.text}")

        result = response.json()
        return result["message"]["content"]

    def _chat_gemini(
        self,
        message: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Chat with Gemini API"""
        # Build prompt
        full_prompt = ""

        if system_prompt:
            full_prompt += f"System: {system_prompt}\n\n"

        # Add recent history
        for msg in self.conversation_history[-6:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            full_prompt += f"{role}: {msg['content']}\n\n"

        full_prompt += f"User: {message}\n\nAssistant:"

        # Generate
        response = self.gemini_model.generate_content(
            full_prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
        )

        return response.text

    def generate_code(
        self,
        task: str,
        language: str = "python",
        context: Optional[str] = None,
    ) -> str:
        """Generate code for a task"""
        system_prompt = f"""You are an expert {language} programmer.
Generate clean, efficient, well-commented code.
Return ONLY the code, no explanations unless requested."""

        prompt = f"Task: {task}"
        if context:
            prompt += f"\n\nContext: {context}"

        return self.chat(prompt, system_prompt=system_prompt, temperature=0.3)

    def analyze_text(
        self,
        text: str,
        task: str = "analyze",
    ) -> str:
        """Analyze text (sentiment, entities, summary, etc.)"""
        system_prompt = "You are an expert text analyst. Provide clear, structured analysis."

        prompt = f"Task: {task}\n\nText:\n{text}"

        return self.chat(prompt, system_prompt=system_prompt, temperature=0.5)

    def tailor_resume(
        self,
        original_resume: str,
        job_description: str,
        format_type: str = "markdown",
    ) -> str:
        """Tailor resume to match job description"""
        system_prompt = """You are an expert resume writer and career coach.
Tailor the resume to match the job description while keeping it truthful.
Highlight relevant skills and experience. Use ATS-friendly formatting."""

        prompt = f"""Tailor this resume for the following job:

JOB DESCRIPTION:
{job_description}

ORIGINAL RESUME:
{original_resume}

Generate a tailored resume in {format_type} format that:
1. Emphasizes relevant skills and experience
2. Uses keywords from the job description
3. Maintains truthfulness
4. Is ATS-friendly
5. Highlights quantifiable achievements"""

        return self.chat(prompt, system_prompt=system_prompt, temperature=0.4)

    def write_cover_letter(
        self,
        resume: str,
        job_description: str,
        company_name: str,
        position: str,
    ) -> str:
        """Generate cover letter"""
        system_prompt = """You are an expert cover letter writer.
Write compelling, professional cover letters that get interviews."""

        prompt = f"""Write a cover letter for this job application:

COMPANY: {company_name}
POSITION: {position}

JOB DESCRIPTION:
{job_description}

MY RESUME:
{resume}

Write a professional cover letter that:
1. Shows genuine interest in the company
2. Highlights relevant experience and skills
3. Explains why I'm a great fit
4. Is concise (3-4 paragraphs)
5. Has a strong call to action"""

        return self.chat(prompt, system_prompt=system_prompt, temperature=0.6)

    def extract_job_requirements(self, job_description: str) -> Dict[str, List[str]]:
        """Extract structured requirements from job description"""
        prompt = f"""Extract requirements from this job description and return as JSON:

{job_description}

Return JSON with these keys:
- required_skills: []
- preferred_skills: []
- education: []
- experience: []
- responsibilities: []
- keywords: []

Return ONLY valid JSON, no other text."""

        response = self.chat(prompt, temperature=0.2)

        try:
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_str = response[json_start:json_end]
            return json.loads(json_str)
        except:
            return {
                "required_skills": [],
                "preferred_skills": [],
                "education": [],
                "experience": [],
                "responsibilities": [],
                "keywords": [],
            }

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        self.logger.info("Conversation history cleared")

    def set_local_model(self, model: str):
        """Set Ollama model to use"""
        self.current_local_model = model
        self.logger.info(f"Local model set to: {model}")

    def list_local_models(self) -> List[str]:
        """List available Ollama models"""
        if not self.ollama_available:
            return []

        try:
            import requests

            response = requests.get(f"{self.ollama_base_url}/api/tags")
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        except:
            return []

    def get_status(self) -> Dict[str, Any]:
        """Get AI agent status"""
        return {
            "ollama_available": self.ollama_available,
            "ollama_models": self.list_local_models() if self.ollama_available else [],
            "current_local_model": self.current_local_model,
            "gemini_available": self.gemini_available,
            "conversation_length": len(self.conversation_history) // 2,
            "default_provider": self.default_provider.value,
        }


def get_ai_agent() -> AIAgent:
    """Get AI agent singleton"""
    return AIAgent()
