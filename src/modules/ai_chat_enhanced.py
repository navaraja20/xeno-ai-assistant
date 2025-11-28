"""
Enhanced AI Chat with Context Awareness and Memory
Integrates with email, GitHub, LinkedIn data for smart responses
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv(override=True)


class ContextualAIChat:
    """Enhanced AI chat with context awareness and data integration"""

    def __init__(
        self, config=None, email_handler=None, github_manager=None, linkedin_automation=None
    ):
        """
        Initialize contextual AI chat

        Args:
            config: Configuration object
            email_handler: Email handler for email context
            github_manager: GitHub manager for repo context
            linkedin_automation: LinkedIn automation for profile context
        """
        self.config = config
        self.email_handler = email_handler
        self.github_manager = github_manager
        self.linkedin_automation = linkedin_automation

        self.conversation_history = []
        self.context_memory = {}  # Long-term memory
        self.session_start = datetime.now()
        self.provider = None
        self.client = None

        self._init_ai_provider()
        self._load_context_memory()

    def _init_ai_provider(self):
        """Initialize AI provider (Gemini first, then OpenAI)"""
        # Try Google Gemini first (free!)
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=gemini_key)
                self.client = genai.GenerativeModel("gemini-2.5-flash")
                self.provider = "gemini"
                print("✅ Enhanced AI with FREE Google Gemini 2.5 Flash")
                return
            except Exception as e:
                print(f"Could not initialize Gemini: {e}")

        # Fallback to OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                import openai

                self.client = openai.OpenAI(api_key=openai_key)
                self.provider = "openai"
                print("✅ Enhanced AI with OpenAI GPT")
                return
            except Exception as e:
                print(f"Could not initialize OpenAI: {e}")

        print("❌ No AI provider configured")

    def _load_context_memory(self):
        """Load context memory from disk"""
        try:
            # Use user home directory to avoid permission issues
            memory_file = Path.home() / ".XENO" / "context_memory.json"
            if memory_file.exists():
                with open(memory_file, "r") as f:
                    self.context_memory = json.load(f)
            else:
                self.context_memory = {}
        except Exception as e:
            print(f"Could not load context memory: {e}")
            self.context_memory = {}

    def _save_context_memory(self):
        """Save context memory to disk"""
        try:
            # Use user home directory to avoid permission issues
            memory_file = Path.home() / ".XENO" / "context_memory.json"
            memory_file.parent.mkdir(parents=True, exist_ok=True)
            with open(memory_file, "w") as f:
                json.dump(self.context_memory, f, indent=2, default=str)
        except Exception as e:
            # Silently fail if we can't save - don't block chat functionality
            print(f"Could not save context memory: {e}")

    def send_message(self, message: str) -> str:
        """
        Send message with context awareness

        Args:
            message: User message

        Returns:
            AI response
        """
        if not self.client:
            return "❌ AI not configured. Get FREE Gemini: https://makersuite.google.com/app/apikey"

        try:
            # Gather relevant context
            context = self._gather_context(message)

            # Build enhanced message with context
            enhanced_message = self._build_enhanced_message(message, context)

            # Get AI response
            if self.provider == "gemini":
                response = self._send_gemini(enhanced_message)
            elif self.provider == "openai":
                response = self._send_openai(enhanced_message)
            else:
                return "❌ No AI provider available"

            # Update conversation history
            self.conversation_history.append(
                {
                    "role": "user",
                    "content": message,
                    "timestamp": datetime.now(),
                    "context": context,
                }
            )
            self.conversation_history.append(
                {"role": "assistant", "content": response, "timestamp": datetime.now()}
            )

            # Update context memory
            self._update_context_memory(message, response, context)

            return response

        except Exception as e:
            return f"❌ Error: {str(e)}"

    def _gather_context(self, message: str) -> Dict[str, Any]:
        """Gather relevant context based on message content"""
        context = {}
        message_lower = message.lower()

        # Email context
        if any(word in message_lower for word in ["email", "mail", "message", "inbox"]):
            context["emails"] = self._get_email_context()

        # GitHub context
        if any(
            word in message_lower
            for word in ["github", "repo", "repository", "code", "pull request", "pr"]
        ):
            context["github"] = self._get_github_context()

        # LinkedIn context
        if any(word in message_lower for word in ["linkedin", "job", "connection", "profile"]):
            context["linkedin"] = self._get_linkedin_context()

        # Time context
        context["time"] = {
            "current": datetime.now().strftime("%A, %B %d, %Y at %I:%M %p"),
            "session_duration": str(datetime.now() - self.session_start),
        }

        # Previous conversation context
        if self.conversation_history:
            context["recent_topics"] = self._extract_recent_topics()

        return context

    def _get_email_context(self) -> Dict[str, Any]:
        """Get email-related context"""
        if not self.email_handler:
            return {}

        try:
            # Get unread count
            unread_count = self.email_handler.get_unread_count()

            # Get recent emails (last 5)
            recent = self.email_handler.get_recent_emails(count=5)

            return {
                "unread_count": unread_count,
                "recent_count": len(recent),
                "recent_senders": [email.get("from", "") for email in recent[:3]],
                "recent_subjects": [email.get("subject", "") for email in recent[:3]],
            }
        except:
            return {}

    def _get_github_context(self) -> Dict[str, Any]:
        """Get GitHub-related context"""
        if not self.github_manager:
            return {}

        try:
            repos = self.github_manager.get_repositories()
            return {
                "repo_count": len(repos),
                "recent_repos": [repo.get("name", "") for repo in repos[:3]],
            }
        except:
            return {}

    def _get_linkedin_context(self) -> Dict[str, Any]:
        """Get LinkedIn-related context"""
        if not self.linkedin_automation:
            return {}

        return {"status": "connected"}

    def _extract_recent_topics(self) -> List[str]:
        """Extract topics from recent conversation"""
        topics = []
        for msg in self.conversation_history[-5:]:
            if msg["role"] == "user":
                # Simple topic extraction (can be enhanced)
                words = msg["content"].lower().split()
                for word in words:
                    if len(word) > 5 and word not in ["please", "thanks", "could"]:
                        topics.append(word)
        return list(set(topics))[:5]

    def _build_enhanced_message(self, message: str, context: Dict[str, Any]) -> str:
        """Build message with context"""
        system_prompt = """You are XENO, an advanced AI assistant inspired by JARVIS from Iron Man.
You are helpful, proactive, intelligent, and slightly witty.
Address the user as 'Sir' or 'Master'.
You have access to the user's email, GitHub, and LinkedIn data.
Provide concise, actionable responses."""

        # Add context if available
        context_str = ""
        if context:
            if "emails" in context and context["emails"]:
                email_ctx = context["emails"]
                context_str += (
                    f"\n[Email Context: {email_ctx.get('unread_count', 0)} unread emails]"
                )

            if "github" in context and context["github"]:
                github_ctx = context["github"]
                context_str += f"\n[GitHub Context: {github_ctx.get('repo_count', 0)} repositories]"

            if "time" in context:
                context_str += f"\n[Time: {context['time']['current']}]"

        # Build conversation history
        history_str = ""
        if self.conversation_history:
            recent = self.conversation_history[-6:]  # Last 3 exchanges
            for msg in recent:
                role = "User" if msg["role"] == "user" else "XENO"
                history_str += f"\n{role}: {msg['content']}"

        full_message = (
            f"{system_prompt}{context_str}\n\nConversation:{history_str}\n\nUser: {message}\nXENO:"
        )
        return full_message

    def _send_gemini(self, message: str) -> str:
        """Send message using Gemini"""
        response = self.client.generate_content(message)
        return response.text.strip()

    def _send_openai(self, message: str) -> str:
        """Send message using OpenAI"""
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    def _update_context_memory(self, message: str, response: str, context: Dict):
        """Update long-term context memory"""
        # Store important topics
        message_lower = message.lower()

        # Remember preferences
        if "prefer" in message_lower or "like" in message_lower:
            self.context_memory["preferences"] = self.context_memory.get("preferences", [])
            self.context_memory["preferences"].append(
                {"statement": message, "timestamp": datetime.now().isoformat()}
            )

        # Remember important entities mentioned
        if "email" in message_lower:
            self.context_memory["last_email_query"] = datetime.now().isoformat()

        if "github" in message_lower:
            self.context_memory["last_github_query"] = datetime.now().isoformat()

        # Save to disk
        self._save_context_memory()

    def get_daily_briefing(self) -> str:
        """Generate AI-powered daily briefing"""
        briefing_prompt = """Generate a brief daily summary for the user based on this data:

Context:
- Time: {time}
- Emails: {email_count} unread
- Recent subjects: {email_subjects}
- GitHub repos: {github_repos}

Provide a concise, actionable briefing in JARVIS style."""

        context = self._gather_context("daily briefing")

        email_ctx = context.get("emails", {})
        github_ctx = context.get("github", {})

        message = briefing_prompt.format(
            time=context["time"]["current"],
            email_count=email_ctx.get("unread_count", 0),
            email_subjects=", ".join(email_ctx.get("recent_subjects", [])[:3]),
            github_repos=", ".join(github_ctx.get("recent_repos", [])[:3]),
        )

        return self.send_message(message)

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history[-limit:]

    def is_available(self) -> bool:
        """Check if AI is available and configured"""
        return self.client is not None and self.provider is not None


# Helper function for backward compatibility
def get_enhanced_ai_chat(config, email_handler=None, github_manager=None, linkedin_automation=None):
    """Get enhanced AI chat instance"""
    return ContextualAIChat(config, email_handler, github_manager, linkedin_automation)
