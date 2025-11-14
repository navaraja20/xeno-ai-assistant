"""
AI Chat Module - Supports FREE Google Gemini and OpenAI
"""
import os
from pathlib import Path
from typing import Optional, List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AIChat:
    """AI chat interface supporting multiple providers (Gemini is FREE!)"""
    
    def __init__(self, config=None):
        """Initialize AI chat - tries Gemini first (free), then OpenAI"""
        self.config = config
        self.conversation_history = []
        self.provider = None
        self.client = None
        
        # Try Google Gemini first (completely free!)
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                self.client = genai.GenerativeModel('gemini-pro')
                self.provider = 'gemini'
                print("✅ Using FREE Google Gemini AI")
                return
            except Exception as e:
                print(f"Could not initialize Gemini: {e}")
        
        # Fallback to OpenAI if available
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=openai_key)
                self.provider = 'openai'
                print("✅ Using OpenAI GPT")
                return
            except Exception as e:
                print(f"Could not initialize OpenAI: {e}")
        
        print("❌ No AI provider configured")
        print("💡 Get FREE Gemini API key: https://makersuite.google.com/app/apikey")
    
    def send_message(self, message: str) -> str:
        """
        Send a message and get AI response.
        Works with both Gemini (free) and OpenAI.
        """
        if not self.client:
            return "❌ AI not configured. Get a FREE Gemini API key: https://makersuite.google.com/app/apikey"
        
        try:
            if self.provider == 'gemini':
                return self._send_gemini(message)
            elif self.provider == 'openai':
                return self._send_openai(message)
            else:
                return "❌ No AI provider available"
                
        except Exception as e:
            error_msg = str(e)
            
            # Handle quota errors with helpful message
            if 'quota' in error_msg.lower() or '429' in error_msg:
                return (
                    "❌ API quota exceeded.\n\n"
                    "FREE Alternative:\n"
                    "1. Get Google Gemini API key (completely free, no credit card): "
                    "https://makersuite.google.com/app/apikey\n"
                    "2. Add to .env file: GEMINI_API_KEY=your_key_here\n"
                    "3. Restart XENO\n\n"
                    "Gemini is free forever with generous limits!"
                )
            
            return f"❌ Error: {error_msg}"
    
    def _send_gemini(self, message: str) -> str:
        """Send message using FREE Google Gemini"""
        try:
            # Build context from conversation history
            if self.conversation_history:
                context = "\n".join([
                    f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                    for msg in self.conversation_history[-10:]  # Last 10 messages
                ])
                full_message = f"{context}\nUser: {message}\nAssistant:"
            else:
                # Add JARVIS personality
                system_prompt = (
                    "You are XENO, an advanced AI assistant inspired by JARVIS from Iron Man. "
                    "You are helpful, proactive, intelligent, and slightly witty. "
                    "Address the user as 'Sir' or 'Master'. "
                    "Provide concise, actionable responses."
                )
                full_message = f"{system_prompt}\n\nUser: {message}\nAssistant:"
            
            # Generate response
            response = self.client.generate_content(full_message)
            ai_response = response.text
            
            # Save to history
            self.conversation_history.append({
                'role': 'user',
                'content': message
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': ai_response
            })
            
            # Keep only last 20 messages
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return ai_response
            
        except Exception as e:
            return f"❌ Gemini error: {str(e)}"
    
    def _send_openai(self, message: str) -> str:
        """Send message using OpenAI GPT"""
        try:
            # Build messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are XENO, an advanced AI assistant inspired by JARVIS from Iron Man. "
                        "You are helpful, proactive, intelligent, and slightly witty. "
                        "Address the user as 'Sir' or 'Master'. "
                        "Provide concise, actionable responses."
                    )
                }
            ]
            
            # Add conversation history
            messages.extend(self.conversation_history[-10:])  # Last 10 messages
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Save to history
            self.conversation_history.append({
                'role': 'user',
                'content': message
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': ai_response
            })
            
            # Keep only last 20 messages
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return ai_response
            
        except Exception as e:
            error_msg = str(e)
            if 'quota' in error_msg.lower() or '429' in error_msg:
                return (
                    "❌ OpenAI quota exceeded.\n\n"
                    "Switch to FREE Gemini:\n"
                    "1. Get key: https://makersuite.google.com/app/apikey\n"
                    "2. Add to .env: GEMINI_API_KEY=your_key_here\n"
                    "3. Restart XENO"
                )
            return f"❌ OpenAI error: {error_msg}"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []


def get_ai_chat(config=None):
    """Get AI chat instance"""
    return AIChat(config)
