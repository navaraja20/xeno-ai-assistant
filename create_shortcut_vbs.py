"""
Create XENO desktop shortcut using VBScript (works on all Windows)
"""
import subprocess
import sys
import tempfile
from pathlib import Path

# Get paths
python_exe = sys.executable.replace("\\", "\\\\")
jarvis_path = str(Path(__file__).parent / "src" / "jarvis.py").replace("\\", "\\\\")
icon_path = str(Path(__file__).parent / "assets" / "XENO.ico").replace("\\", "\\\\")
desktop = str(Path.home() / "Desktop").replace("\\", "\\\\")
working_dir = str(Path(__file__).parent).replace("\\", "\\\\")

# Create VBScript to make shortcut
vbs_script = f"""Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{desktop}\\XENO.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{python_exe}"
oLink.Arguments = "\\"{jarvis_path}\\""
oLink.WorkingDirectory = "{working_dir}"
oLink.Description = "XENO - Personal AI Assistant"
oLink.IconLocation = "{icon_path}"
oLink.Save
"""

# Write VBScript to temp file
with tempfile.NamedTemporaryFile(mode="w", suffix=".vbs", delete=False) as f:
    vbs_path = f.name
    f.write(vbs_script)

try:
    # Execute VBScript
    subprocess.run(["cscript", "//Nologo", vbs_path], check=True)
    print("✓ Desktop shortcut created successfully!")
    print(f"  Location: {Path.home() / 'Desktop' / 'XENO.lnk'}")
    print(f"  Icon: {Path(__file__).parent / 'assets' / 'XENO.ico'}")

    # Clean up temp file
    Path(vbs_path).unlink()

    # Also remove the batch file if it exists
    batch_file = Path.home() / "Desktop" / "XENO.bat"
    if batch_file.exists():
        batch_file.unlink()
        print("  (Removed old batch file)")

except Exception as e:
    print(f"✗ Error: {e}")
    Path(vbs_path).unlink()
