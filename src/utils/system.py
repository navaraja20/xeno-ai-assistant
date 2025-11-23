"""
System utilities for XENO
"""
import os
import platform
from pathlib import Path
from typing import Optional


def get_platform() -> str:
    """Get current platform (windows, macos, linux)"""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system


def is_first_run() -> bool:
    """Check if this is the first run of XENO"""
    config_dir = Path.home() / ".xeno"
    config_file = config_dir / "config.yaml"
    first_run_marker = config_dir / ".first_run_complete"
    
    return not first_run_marker.exists()


def mark_first_run_complete():
    """Mark first run as complete"""
    config_dir = Path.home() / ".xeno"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    first_run_marker = config_dir / ".first_run_complete"
    first_run_marker.touch()


def create_directories():
    """Create necessary application directories"""
    base_dir = Path.home() / ".xeno"
    
    directories = [
        base_dir,
        base_dir / "data",
        base_dir / "logs",
        base_dir / "plugins",
        base_dir / "templates",
        base_dir / "resumes",
        base_dir / "cover_letters",
        base_dir / "cache",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def get_app_data_dir() -> Path:
    """Get platform-specific application data directory"""
    system = get_platform()
    
    if system == "windows":
        # Windows: %APPDATA%\XENO
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "XENO"
    elif system == "macos":
        # macOS: ~/Library/Application Support/XENO
        return Path.home() / "Library" / "Application Support" / "XENO"
    
    # Linux and fallback: ~/.xeno
    return Path.home() / ".xeno"


def get_startup_command() -> str:
    """Get command to start XENO"""
    import sys
    
    # Get Python executable and jarvis.py path
    python_exe = sys.executable
    jarvis_path = Path(__file__).parent.parent / "jarvis.py"
    
    return f'"{python_exe}" "{jarvis_path}"'


def enable_autostart() -> bool:
    """
    Enable XENO to start on system boot
    
    Returns:
        True if successful, False otherwise
    """
    system = get_platform()
    
    try:
        if system == "windows":
            return _enable_autostart_windows()
        elif system == "macos":
            return _enable_autostart_macos()
        elif system == "linux":
            return _enable_autostart_linux()
        return False
    except Exception as e:
        print(f"Failed to enable autostart: {e}")
        return False


def disable_autostart() -> bool:
    """
    Disable XENO autostart
    
    Returns:
        True if successful, False otherwise
    """
    system = get_platform()
    
    try:
        if system == "windows":
            return _disable_autostart_windows()
        elif system == "macos":
            return _disable_autostart_macos()
        elif system == "linux":
            return _disable_autostart_linux()
        return False
    except Exception as e:
        print(f"Failed to disable autostart: {e}")
        return False


def _enable_autostart_windows() -> bool:
    """Enable autostart on Windows using Registry"""
    import winreg
    
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "XENO"
    command = get_startup_command()
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Windows autostart error: {e}")
        return False


def _disable_autostart_windows() -> bool:
    """Disable autostart on Windows"""
    import winreg
    
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "XENO"
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, app_name)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        # Already removed
        return True
    except Exception as e:
        print(f"Windows autostart disable error: {e}")
        return False


def _enable_autostart_macos() -> bool:
    """Enable autostart on macOS using LaunchAgent"""
    import plistlib
    
    plist_path = Path.home() / "Library" / "LaunchAgents" / "com.xeno.assistant.plist"
    plist_path.parent.mkdir(parents=True, exist_ok=True)
    
    command = get_startup_command()
    python_exe, jarvis_script = command.strip('"').split('" "')
    
    plist_content = {
        "Label": "com.xeno.assistant",
        "ProgramArguments": [python_exe, jarvis_script],
        "RunAtLoad": True,
        "KeepAlive": False,
    }
    
    with open(plist_path, 'wb') as f:
        plistlib.dump(plist_content, f)
    
    # Load the launch agent (using subprocess for security)
    import subprocess
    try:
        subprocess.run(['launchctl', 'load', str(plist_path)], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pass  # Silently ignore if launchctl fails
    return True


def _disable_autostart_macos() -> bool:
    """Disable autostart on macOS"""
    import subprocess
    plist_path = Path.home() / "Library" / "LaunchAgents" / "com.xeno.assistant.plist"
    
    if plist_path.exists():
        try:
            subprocess.run(['launchctl', 'unload', str(plist_path)], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            pass  # Silently ignore if launchctl fails
        plist_path.unlink()
    
    return True


def _enable_autostart_linux() -> bool:
    """Enable autostart on Linux using .desktop file"""
    autostart_dir = Path.home() / ".config" / "autostart"
    autostart_dir.mkdir(parents=True, exist_ok=True)
    
    desktop_file = autostart_dir / "xeno.desktop"
    command = get_startup_command()
    
    desktop_content = f"""[Desktop Entry]
Type=Application
Name=XENO Assistant
Comment=Personal AI Assistant
Exec={command}
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
"""
    
    with open(desktop_file, 'w') as f:
        f.write(desktop_content)
    
    # Make executable
    os.chmod(desktop_file, 0o755)
    return True


def _disable_autostart_linux() -> bool:
    """Disable autostart on Linux"""
    desktop_file = Path.home() / ".config" / "autostart" / "xeno.desktop"
    
    if desktop_file.exists():
        desktop_file.unlink()
    
    return True


def create_desktop_shortcut() -> bool:
    """
    Create a desktop shortcut/icon for XENO
    
    Returns:
        True if successful, False otherwise
    """
    system = get_platform()
    
    try:
        if system == "windows":
            return _create_desktop_shortcut_windows()
        elif system == "macos":
            return _create_desktop_shortcut_macos()
        elif system == "linux":
            return _create_desktop_shortcut_linux()
        return False
    except Exception as e:
        print(f"Failed to create desktop shortcut: {e}")
        return False


def _create_desktop_shortcut_windows() -> bool:
    """Create Windows desktop shortcut (.lnk file)"""
    try:
        import subprocess
        import tempfile
        
        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / "XENO.lnk"
        
        # Get paths
        import sys
        python_exe = sys.executable
        jarvis_path = Path(__file__).parent.parent / "jarvis.py"
        icon_path = Path(__file__).parent.parent.parent / "assets" / "xeno.ico"
        working_dir = Path(__file__).parent.parent.parent
        
        # Create PowerShell script
        ps_script = f'''$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{python_exe}"
$Shortcut.Arguments = "`"{jarvis_path}`""
$Shortcut.WorkingDirectory = "{working_dir}"
$Shortcut.Description = "XENO - Personal AI Assistant"
$Shortcut.IconLocation = "{icon_path}"
$Shortcut.Save()
'''
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
            ps_path = f.name
            f.write(ps_script)
        
        # Execute PowerShell script
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_path],
            capture_output=True,
            text=True
        )
        
        # Clean up
        Path(ps_path).unlink()
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Windows shortcut error: {e}")
        return False


def _create_desktop_shortcut_macos() -> bool:
    """Create macOS desktop alias"""
    try:
        import sys
        desktop = Path.home() / "Desktop"
        app_script = desktop / "XENO.command"
        
        python_exe = sys.executable
        jarvis_path = Path(__file__).parent.parent / "jarvis.py"
        
        script_content = f'''#!/bin/bash
cd "{jarvis_path.parent.parent}"
"{python_exe}" "{jarvis_path}"
'''
        
        with open(app_script, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(app_script, 0o755)
        return True
        
    except Exception as e:
        print(f"macOS shortcut error: {e}")
        return False


def _create_desktop_shortcut_linux() -> bool:
    """Create Linux desktop file"""
    try:
        import sys
        desktop = Path.home() / "Desktop"
        desktop_file = desktop / "XENO.desktop"
        
        python_exe = sys.executable
        jarvis_path = Path(__file__).parent.parent / "jarvis.py"
        icon_path = Path(__file__).parent.parent.parent / "assets" / "xeno.png"
        
        desktop_content = f"""[Desktop Entry]
Type=Application
Name=XENO
Comment=Personal AI Assistant
Exec="{python_exe}" "{jarvis_path}"
Icon={icon_path if icon_path.exists() else ''}
Terminal=false
Categories=Utility;Application;
"""
        
        with open(desktop_file, 'w') as f:
            f.write(desktop_content)
        
        # Make executable
        os.chmod(desktop_file, 0o755)
        return True
        
    except Exception as e:
        print(f"Linux shortcut error: {e}")
        return False
