"""
AI Agent Demo
Test XENO's AI capabilities
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import QApplication

from src.ai.ai_agent import ModelProvider, get_ai_agent
from src.ai.ai_chat_ui import AIChatWidget, QMainWindow


def test_basic_chat():
    """Test basic chat functionality"""
    print("=" * 60)
    print("XENO AI Agent - Basic Chat Test")
    print("=" * 60)

    agent = get_ai_agent()

    # Check status
    print("\n1. Checking AI status...")
    status = agent.get_status()

    print(f"\n✅ Ollama (Local): {'Available' if status['ollama_available'] else 'Not Available'}")
    if status["ollama_available"]:
        print(f"   Models: {', '.join(status['ollama_models'])}")
        print(f"   Current: {status['current_local_model']}")

    print(f"\n✅ Gemini (Cloud): {'Available' if status['gemini_available'] else 'Not Configured'}")

    # Test chat
    print("\n2. Testing chat...")

    if not status["ollama_available"] and not status["gemini_available"]:
        print("\n⚠️  No AI provider available!")
        print("\nTo use local AI:")
        print("   1. Install Ollama: https://ollama.ai/download")
        print("   2. Pull a model: ollama pull llama3.1:8b")
        print("\nTo use Gemini:")
        print("   1. Get API key: https://makersuite.google.com/app/apikey")
        print("   2. Add to .env: GEMINI_API_KEY=your_key")
        return

    # Test questions
    questions = [
        "What is machine learning?",
        "Explain Python in one sentence",
        "What's the difference between AI and ML?",
    ]

    for q in questions:
        print(f"\n❓ {q}")
        response = agent.chat(q)
        print(f"🤖 {response[:200]}...")

    print("\n✅ Chat test complete")


def test_code_generation():
    """Test code generation"""
    print("\n" + "=" * 60)
    print("Code Generation Test")
    print("=" * 60)

    agent = get_ai_agent()

    print("\n1. Generating Python code...")
    code = agent.generate_code(
        "Create a function to calculate fibonacci numbers", language="python"
    )

    print("\n📝 Generated code:")
    print(code)


def test_resume_features():
    """Test resume and job hunting AI features"""
    print("\n" + "=" * 60)
    print("Resume & Job Hunting Features Test")
    print("=" * 60)

    agent = get_ai_agent()

    sample_resume = """John Doe
Data Science Student

SKILLS
Python, Machine Learning, TensorFlow, PyTorch

EXPERIENCE
ML Intern - Tech Company
- Built classification models
- Improved accuracy by 20%
"""

    job_description = """Data Science Intern
Looking for student with:
- Python, ML, Deep Learning
- Experience with NLP
- PyTorch knowledge

Build NLP models for text classification.
"""

    print("\n1. Extracting job requirements...")
    requirements = agent.extract_job_requirements(job_description)

    print("\n📋 Extracted requirements:")
    for key, values in requirements.items():
        if values:
            print(f"   {key}: {', '.join(values)}")

    print("\n2. Tailoring resume...")
    print("   (This will take a moment...)")

    # Note: Only test if AI is available
    status = agent.get_status()
    if not status["ollama_available"] and not status["gemini_available"]:
        print("   ⚠️  Skipped - No AI provider available")
        return

    tailored = agent.tailor_resume(sample_resume, job_description)
    print("\n📄 Tailored resume:")
    print(tailored[:300] + "...")


def main():
    """Main demo"""
    print(
        """
╔══════════════════════════════════════════════════════════╗
║            XENO AI Agent - Interactive Demo             ║
╚══════════════════════════════════════════════════════════╝

Transform XENO into an AI agent with:

1. 🧠 Local LLM (Ollama) - Privacy-focused, runs on your GPU
2. ☁️  Cloud AI (Gemini) - Powerful, cloud-based fallback
3. 💬 Natural conversation - Chat like with Claude
4. 💻 Code generation - Write code from natural language
5. 📝 Text analysis - Analyze and summarize text
6. 🎯 Job hunting - Resume tailoring, cover letters

Choose a demo:
[1] Test Basic Chat
[2] Test Code Generation
[3] Test Resume Features
[4] Launch Chat UI
[0] Exit
"""
    )

    # Check AI availability
    agent = get_ai_agent()
    status = agent.get_status()

    if not status["ollama_available"] and not status["gemini_available"]:
        print("\n⚠️  WARNING: No AI provider available!")
        print("\nSetup Instructions:")
        print("\n📥 Option 1: Local AI (Ollama) - Recommended for RTX 4050")
        print("   1. Download: https://ollama.ai/download")
        print("   2. Install Ollama")
        print("   3. Open terminal and run: ollama pull llama3.1:8b")
        print("   4. Restart this demo")
        print("\n☁️  Option 2: Cloud AI (Gemini)")
        print("   1. Get API key: https://makersuite.google.com/app/apikey")
        print("   2. Open .env file")
        print("   3. Add: GEMINI_API_KEY=your_key_here")
        print("   4. Restart this demo")
        print("\n" + "=" * 60)

    while True:
        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            test_basic_chat()

        elif choice == "2":
            test_code_generation()

        elif choice == "3":
            test_resume_features()

        elif choice == "4":
            print("\n🚀 Launching Chat UI...")
            app = QApplication(sys.argv)

            window = QMainWindow()
            window.setWindowTitle("XENO AI Chat")
            window.setGeometry(100, 100, 800, 900)

            widget = AIChatWidget()
            window.setCentralWidget(widget)

            window.show()
            sys.exit(app.exec())

        elif choice == "0":
            print("\nGoodbye! 🤖")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
