"""
Manually create XENO desktop shortcut
Run this script to create a desktop shortcut with icon
"""
import os
import sys
from pathlib import Path

try:
    # Method 1: Using win32com (pywin32)
    from win32com.client import Dispatch
    import winshell
    
    def create_shortcut_pywin32():
        """Create shortcut using pywin32"""
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, "XENO.lnk")
        
        # Get paths
        python_exe = sys.executable
        jarvis_path = Path(__file__).parent / "src" / "jarvis.py"
        icon_path = Path(__file__).parent / "assets" / "xeno.ico"
        working_dir = Path(__file__).parent
        
        # Create shortcut
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = python_exe
        shortcut.Arguments = f'"{jarvis_path}"'
        shortcut.WorkingDirectory = str(working_dir)
        shortcut.Description = "XENO - Personal AI Assistant"
        
        # Set icon if exists
        if icon_path.exists():
            shortcut.IconLocation = str(icon_path)
        
        shortcut.save()
        print(f"✓ Desktop shortcut created: {shortcut_path}")
        print(f"  Target: {python_exe}")
        print(f"  Arguments: {jarvis_path}")
        print(f"  Icon: {icon_path}")
        return True
    
    # Try to create shortcut
    if create_shortcut_pywin32():
        print("\n✓ Success! XENO shortcut is on your desktop.")
    
except ImportError:
    # Method 2: Fallback - Create batch file
    print("pywin32 not available, creating batch file instead...")
    
    desktop = Path.home() / "Desktop"
    batch_path = desktop / "XENO.bat"
    
    python_exe = sys.executable
    jarvis_path = Path(__file__).parent / "src" / "jarvis.py"
    
    batch_content = f'''@echo off
cd /d "{jarvis_path.parent.parent}"
"{python_exe}" "{jarvis_path}"
pause
'''
    
    with open(batch_path, 'w') as f:
        f.write(batch_content)
    
    print(f"✓ Created batch file: {batch_path}")
    print("  Note: To add an icon, right-click the batch file → Properties → Change Icon")
    
except Exception as e:
    print(f"✗ Error creating shortcut: {e}")
    print("\nManual method:")
    print("1. Right-click Desktop → New → Shortcut")
    print(f"2. Location: {sys.executable} \"{Path(__file__).parent / 'src' / 'jarvis.py'}\"")
    print(f"3. Name: XENO")
    print(f"4. Right-click shortcut → Properties → Change Icon → Browse to: {Path(__file__).parent / 'assets' / 'xeno.ico'}")
