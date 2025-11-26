# XENO Deployment Guide 🚀

Complete guide for deploying XENO AI Assistant in various environments.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Local Deployment](#local-deployment)
- [Production Deployment](#production-deployment)
- [Security Hardening](#security-hardening)
- [Performance Optimization](#performance-optimization)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum:**
- Windows 10/11 or Linux (Ubuntu 20.04+)
- Python 3.9+
- 2GB RAM
- 500MB disk space

**Recommended:**
- Windows 11 or Ubuntu 22.04+
- Python 3.11+
- 4GB RAM
- 2GB disk space
- SSD storage

### Required Software

```powershell
# Check Python version
python --version  # Should be 3.9 or higher

# Check pip
python -m pip --version

# Install Git (if not present)
winget install Git.Git
```

---

## Local Deployment

### 1. Clone Repository

```powershell
git clone https://github.com/YOUR_USERNAME/XENO-ai-assistant.git
cd XENO-ai-assistant
```

### 2. Create Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.venv\Scripts\activate.bat

# Activate (Linux/Mac)
source .venv/bin/activate
```

### 3. Install Dependencies

```powershell
# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list | Select-String "PyQt6|cryptography|pytest"
```

### 4. Configure Environment

```powershell
# Create configuration directory
mkdir $env:USERPROFILE\.XENO

# Create .env file
@"
# AI Provider (choose one - Gemini is FREE!)
GEMINI_API_KEY=your_gemini_key_here
# OPENAI_API_KEY=your_openai_key_here

# Email (optional)
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_app_password

# GitHub (optional)
GITHUB_USERNAME=your_username
GITHUB_TOKEN=your_github_token

# LinkedIn (optional)
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password

# Security (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
SECRET_KEY=your_secret_key_here
ENCRYPTION_KEY=your_fernet_key_here
"@ | Out-File -FilePath $env:USERPROFILE\.XENO\.env -Encoding UTF8
```

### 5. Run Tests

```powershell
# Run all tests
python -m pytest tests/ -v

# Run specific test suites
python -m pytest tests/unit/ -v           # Unit tests
python -m pytest tests/integration/ -v    # Integration tests
python -m pytest tests/e2e/ -v           # E2E tests
python -m pytest tests/benchmarks/ -v    # Performance tests

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### 6. Launch XENO

```powershell
# Run XENO
python src\jarvis.py

# Run in background (Windows)
Start-Process python -ArgumentList "src\jarvis.py" -WindowStyle Hidden

# Run with logging
python src\jarvis.py 2>&1 | Tee-Object -FilePath logs\XENO.log
```

---

## Production Deployment

### 1. Security Hardening

#### Generate Secure Keys

```powershell
# Generate SECRET_KEY (for JWT)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY (for Fernet)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

#### Set Secure Permissions

```powershell
# Restrict .env file access (Windows)
$acl = Get-Acl "$env:USERPROFILE\.XENO\.env"
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule($env:USERNAME, "FullControl", "Allow")
$acl.SetAccessRule($rule)
Set-Acl "$env:USERPROFILE\.XENO\.env" $acl

# Restrict .env file access (Linux)
chmod 600 ~/.XENO/.env
```

#### Enable MFA

```python
# In Python shell or during first run
from src.security.enterprise_security import AuthenticationManager

auth = AuthenticationManager()
# Enable MFA for your account
mfa_uri = auth.enable_mfa("your_username")
print(f"Scan this QR code: {mfa_uri}")
```

### 2. Performance Optimization

#### Configure Performance Settings

```python
# In src/core/config.py or .env

# Database connection pooling
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Cache settings
CACHE_TTL=3600  # 1 hour
CACHE_MAX_SIZE=1000

# Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60  # 1 minute

# Session timeout
SESSION_TIMEOUT=86400  # 24 hours
```

#### Enable Caching

```python
# Install caching backend
pip install redis

# Configure Redis (if using)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 3. Database Setup

```powershell
# Initialize database
python -c "from src.models.database import init_db; init_db()"

# Run migrations (if applicable)
python manage.py migrate

# Create backup script
@"
# Database backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item "data/*.db" "backups/db_backup_$timestamp.db"
"@ | Out-File -FilePath scripts\backup_db.ps1
```

### 4. Service Installation (Windows)

#### Create Windows Service

```powershell
# Install NSSM (Non-Sucking Service Manager)
winget install NSSM.NSSM

# Create service
$pythonPath = (Get-Command python).Source
$scriptPath = "$PWD\src\jarvis.py"

nssm install XENO $pythonPath $scriptPath
nssm set XENO AppDirectory $PWD
nssm set XENO DisplayName "XENO AI Assistant"
nssm set XENO Description "Proactive AI assistant service"
nssm set XENO Start SERVICE_AUTO_START

# Start service
nssm start XENO

# Check status
nssm status XENO
```

### 5. Logging Configuration

```python
# In src/core/logger.py or .env

# Log level
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Log file
LOG_FILE=logs/XENO.log
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5

# Audit logging
AUDIT_LOG_ENABLED=true
AUDIT_LOG_FILE=logs/audit.log
```

---

## Security Hardening

### Checklist

- [ ] **Change default credentials** (if any)
- [ ] **Generate secure SECRET_KEY and ENCRYPTION_KEY**
- [ ] **Enable MFA** for all user accounts
- [ ] **Set strict file permissions** on .env and data files
- [ ] **Enable audit logging**
- [ ] **Configure rate limiting**
- [ ] **Set up firewall rules** (if exposing ports)
- [ ] **Enable HTTPS** (if web interface)
- [ ] **Regular security updates** (`pip install --upgrade -r requirements.txt`)
- [ ] **Backup encryption keys** securely

### Rate Limiting Configuration

```python
# In .env or security config
RATE_LIMIT_LOGIN_ATTEMPTS=5
RATE_LIMIT_LOGIN_WINDOW=300  # 5 minutes
RATE_LIMIT_API_REQUESTS=100
RATE_LIMIT_API_WINDOW=60  # 1 minute
```

### Audit Logging

```python
# Enable comprehensive audit logging
from src.security.security_config import AuditLogger

logger = AuditLogger()
logger.log_auth_attempt(username, success=True)
logger.log_data_access(username, "emails", "read")
logger.log_event("user_action", username, "create_team", "info")
```

---

## Performance Optimization

### 1. Database Optimization

```python
# Enable query caching
SQLALCHEMY_TRACK_MODIFICATIONS=False
SQLALCHEMY_ECHO=False  # Disable query logging in production

# Use connection pooling
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_POOL_RECYCLE=3600
```

### 2. Caching Strategy

```python
# Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user_preferences(user_id):
    # ... fetch from database
    pass
```

### 3. Async Operations

```python
# Use async for I/O-bound operations
import asyncio

async def fetch_emails():
    # ... async email fetching
    pass

asyncio.run(fetch_emails())
```

### 4. Performance Monitoring

```powershell
# Run performance benchmarks
python -m pytest tests/benchmarks/ --benchmark-only

# Profile specific operations
python performance_profiler.py
```

---

## Monitoring & Maintenance

### 1. Health Checks

```python
# Create health check endpoint
def health_check():
    """Check system health"""
    return {
        "status": "healthy",
        "database": check_database(),
        "api": check_api_connectivity(),
        "disk_space": check_disk_space(),
        "memory": check_memory_usage()
    }
```

### 2. Log Monitoring

```powershell
# Monitor logs in real-time
Get-Content logs\XENO.log -Wait -Tail 50

# Search for errors
Select-String -Path logs\XENO.log -Pattern "ERROR|CRITICAL"

# Rotate logs
@"
$logs = Get-ChildItem logs\*.log | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)}
$logs | Remove-Item
"@ | Out-File -FilePath scripts\rotate_logs.ps1
```

### 3. Database Backups

```powershell
# Automated backup script
@"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = "backups\backup_$timestamp"

# Backup database
Copy-Item data\*.db $backupPath\

# Backup configuration
Copy-Item $env:USERPROFILE\.XENO\.env $backupPath\

# Compress
Compress-Archive -Path $backupPath -DestinationPath "$backupPath.zip"
Remove-Item $backupPath -Recurse

# Keep only last 7 backups
Get-ChildItem backups\*.zip | Sort-Object LastWriteTime -Descending | Select-Object -Skip 7 | Remove-Item
"@ | Out-File -FilePath scripts\automated_backup.ps1

# Schedule backup (Windows Task Scheduler)
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File scripts\automated_backup.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
Register-ScheduledTask -TaskName "XENO Backup" -Action $action -Trigger $trigger
```

### 4. Update Checks

```powershell
# Check for updates
git fetch origin
git status

# Update dependencies
pip list --outdated

# Update specific package
pip install --upgrade package_name

# Update all packages
pip install --upgrade -r requirements.txt
```

---

## Troubleshooting

### Common Issues

#### 1. Module Import Errors

```powershell
# Verify Python path
python -c "import sys; print('\n'.join(sys.path))"

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

#### 2. Database Locked

```powershell
# Check for stale lock files
Get-ChildItem data\*.db-journal | Remove-Item

# Restart XENO
nssm restart XENO
```

#### 3. High CPU Usage

```python
# Profile CPU usage
python -m cProfile -o profile.stats src\jarvis.py

# Analyze results
python -m pstats profile.stats
```

#### 4. Memory Leaks

```python
# Install memory profiler
pip install memory_profiler

# Profile memory
python -m memory_profiler src\jarvis.py
```

#### 5. Permission Errors

```powershell
# Reset file permissions
icacls data /reset /T
icacls logs /reset /T

# Run as administrator (if necessary)
Start-Process python -ArgumentList "src\jarvis.py" -Verb RunAs
```

### Debug Mode

```powershell
# Run with debug logging
$env:LOG_LEVEL="DEBUG"
python src\jarvis.py

# Enable verbose output
python src\jarvis.py --verbose

# Run tests in debug mode
python -m pytest tests/ -v --log-cli-level=DEBUG
```

### Getting Help

- **Documentation:** See [README.md](README.md) and [COMPLETE_FEATURES_GUIDE.md](COMPLETE_FEATURES_GUIDE.md)
- **Issues:** Report bugs at [GitHub Issues](https://github.com/YOUR_USERNAME/XENO-ai-assistant/issues)
- **Discussions:** Ask questions at [GitHub Discussions](https://github.com/YOUR_USERNAME/XENO-ai-assistant/discussions)
- **Logs:** Check `logs/XENO.log` and `logs/audit.log`

---

## Performance Benchmarks

Expected performance metrics (validated via `tests/benchmarks/`):

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Device Operations | <1μs | 173-195ns | ✅ Excellent |
| Input Sanitization | <10μs | 1.3-6μs | ✅ Excellent |
| Encryption | <100μs | 68.6μs | ✅ Good |
| Authentication | <100ms | 42ms | ✅ Acceptable |
| Password Hashing | N/A | 46ms | ✅ By design |

**Overall:** 99% operations <100ms, 95% <20ms

---

## Security Checklist

Before going to production:

- [ ] All default credentials changed
- [ ] Secure keys generated and stored
- [ ] MFA enabled for admin accounts
- [ ] File permissions set correctly
- [ ] Audit logging enabled
- [ ] Rate limiting configured
- [ ] Firewall rules configured
- [ ] HTTPS enabled (if applicable)
- [ ] Regular backups scheduled
- [ ] Monitoring set up
- [ ] Security updates scheduled
- [ ] Incident response plan created

---

**⚠️ Important Security Notes:**

1. **Never** commit `.env` files to version control
2. **Always** use HTTPS in production
3. **Regularly** update dependencies for security patches
4. **Monitor** audit logs for suspicious activity
5. **Backup** encryption keys securely (offline if possible)
6. **Test** disaster recovery procedures regularly

---

**Made with ❤️ for production-ready deployments**

*Last updated: November 2025*
