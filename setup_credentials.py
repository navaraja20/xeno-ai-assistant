"""
Interactive credential setup for XENO
This will help you enter credentials correctly
"""
import os
from pathlib import Path
from dotenv import set_key

def setup_credentials():
    print("=" * 60)
    print("  🎯 XENO Credential Setup")
    print("=" * 60)
    print()
    
    env_path = Path("E:/Personal assistant/.env")
    
    print("📧 GMAIL SETUP")
    print("-" * 60)
    print("Gmail requires an 'App Password' (16 characters)")
    print("Get it from: https://myaccount.google.com/apppasswords")
    print()
    
    gmail_address = input("Enter your Gmail address [navarajamannepalli@gmail.com]: ").strip()
    if not gmail_address:
        gmail_address = "navarajamannepalli@gmail.com"
    
    gmail_password = input("Enter Gmail App Password (16 chars, paste here): ").strip().replace(' ', '')
    
    if gmail_password and len(gmail_password) == 16:
        print(f"✅ Gmail App Password: {len(gmail_password)} characters (correct!)")
    elif gmail_password:
        print(f"⚠️  Warning: Password is {len(gmail_password)} characters (should be 16)")
    else:
        print("⏭️  Skipping Gmail (no password entered)")
    
    print()
    print("🐙 GITHUB SETUP")
    print("-" * 60)
    print("GitHub requires a Personal Access Token")
    print("Create one: https://github.com/settings/tokens/new")
    print("Scopes needed: repo, user, workflow")
    print()
    
    github_username = input("Enter GitHub username [navaraja20]: ").strip()
    if not github_username:
        github_username = "navaraja20"
    
    github_token = input("Enter GitHub token (starts with ghp_ or github_pat_): ").strip()
    
    if github_token:
        if github_token.startswith('ghp_') or github_token.startswith('github_pat_'):
            print(f"✅ GitHub token looks valid")
        else:
            print(f"⚠️  Warning: Token doesn't start with ghp_ or github_pat_")
    else:
        print("⏭️  Skipping GitHub (no token entered)")
    
    print()
    print("💼 LINKEDIN SETUP")
    print("-" * 60)
    
    linkedin_email = input(f"Enter LinkedIn email [{gmail_address}]: ").strip()
    if not linkedin_email:
        linkedin_email = gmail_address
    
    linkedin_password = input("Enter LinkedIn password: ").strip()
    
    if not linkedin_password:
        print("⏭️  Skipping LinkedIn (no password entered)")
    
    # Save to .env
    print()
    print("💾 Saving credentials...")
    print("-" * 60)
    
    try:
        # Keep existing Gemini keys
        gemini_key = "AIzaSyDGt0x8OlDp8_LWE4thwtgAMk7B3QSIvBo"
        
        # Save all credentials
        if gmail_password:
            set_key(str(env_path), "EMAIL_ADDRESS", gmail_address)
            set_key(str(env_path), "EMAIL_PASSWORD", gmail_password)
            print(f"✅ Gmail saved: {gmail_address}")
        
        if github_token:
            set_key(str(env_path), "GITHUB_USERNAME", github_username)
            set_key(str(env_path), "GITHUB_TOKEN", github_token)
            print(f"✅ GitHub saved: {github_username}")
        
        if linkedin_password:
            set_key(str(env_path), "LINKEDIN_EMAIL", linkedin_email)
            set_key(str(env_path), "LINKEDIN_PASSWORD", linkedin_password)
            print(f"✅ LinkedIn saved: {linkedin_email}")
        
        print()
        print("=" * 60)
        print("  🎉 Credentials saved to .env file!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Restart XENO: python src\\jarvis.py")
        print("2. Check for connection errors in the terminal")
        print("3. If you see '✅ Connected', it worked!")
        print()
        
    except Exception as e:
        print(f"❌ Error saving credentials: {e}")

if __name__ == "__main__":
    setup_credentials()
