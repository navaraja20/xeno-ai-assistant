"""
Quick setup script for FREE Google Gemini AI
Run this to test Gemini without editing files manually
"""

import os
import webbrowser

print("="*60)
print("  🆓 FREE AI Setup - Google Gemini (No Credit Card!)")
print("="*60)
print()

# Check if Gemini is already configured
env_file = os.path.expanduser("~/.xeno/.env")
has_gemini = False

if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        content = f.read()
        if 'GEMINI_API_KEY' in content and not content.split('GEMINI_API_KEY=')[1].split('\n')[0].strip() == '':
            has_gemini = True

if has_gemini:
    print("✅ Gemini API key already configured!")
    print()
    print("Testing...")
    
    import sys
    sys.path.insert(0, 'src')
    from modules.ai_chat import AIChat
    
    chat = AIChat()
    
    if chat.provider == 'gemini':
        print("✅ Gemini is working!")
        print()
        print("Try chatting:")
        response = chat.send_message("Hi! Say hello in JARVIS style.")
        print(f"\nXENO: {response}")
    else:
        print(f"ℹ️  Currently using: {chat.provider}")
        print("To switch to FREE Gemini, follow steps below.")
else:
    print("⚠️  Gemini not configured yet")
    print()
    print("📝 Follow these steps:")
    print()
    print("1. I'll open the Gemini API page in your browser")
    print("   → Sign in with Google (free account)")
    print("   → Click 'Create API key'")
    print("   → Copy the key (starts with AIzaSy...)")
    print()
    print("2. Then come back here and paste your key")
    print()
    
    input("Press Enter to open Gemini API page...")
    
    # Open Gemini API page
    webbrowser.open("https://makersuite.google.com/app/apikey")
    
    print()
    print("Browser opened! Get your free API key.")
    print()
    
    # Get API key from user
    api_key = input("Paste your Gemini API key here: ").strip()
    
    if api_key and api_key.startswith("AIza"):
        # Create .xeno directory if needed
        xeno_dir = os.path.expanduser("~/.xeno")
        os.makedirs(xeno_dir, exist_ok=True)
        
        # Read existing .env or create new
        env_content = ""
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                env_content = f.read()
        
        # Add or update Gemini key
        if 'GEMINI_API_KEY' in env_content:
            # Replace existing
            lines = env_content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith('GEMINI_API_KEY'):
                    new_lines.append(f'GEMINI_API_KEY={api_key}')
                else:
                    new_lines.append(line)
            env_content = '\n'.join(new_lines)
        else:
            # Add new
            if env_content and not env_content.endswith('\n'):
                env_content += '\n'
            env_content += f'GEMINI_API_KEY={api_key}\n'
        
        # Save
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print()
        print("✅ Gemini API key saved!")
        print()
        print("Testing...")
        
        # Test it
        import sys
        sys.path.insert(0, 'src')
        
        # Force reload environment
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_file, override=True)
        
        from modules.ai_chat import AIChat
        chat = AIChat()
        
        if chat.provider == 'gemini':
            print("✅ SUCCESS! Gemini is working!")
            print()
            print("Test message:")
            response = chat.send_message("Say hello in JARVIS style!")
            print(f"\nXENO: {response}")
            print()
            print("="*60)
            print("🎉 You're all set! Free AI forever!")
            print("="*60)
        else:
            print("⚠️  Gemini not detected. Restart XENO to use it.")
    else:
        print("❌ Invalid API key format")
        print("Key should start with 'AIza'")

print()
print("Next steps:")
print("1. Restart XENO: python src\\jarvis.py")
print("2. Go to Chat page")
print("3. You'll see: '✅ Using FREE Google Gemini AI'")
print("4. Start chatting for free!")
print()
