# ⚡ XENO Quick Reference Card

## Essential Commands (PowerShell/Windows)

### Testing
```powershell
# Run all tests
pytest tests/ -v

# Run specific test category
pytest tests/unit/ -v              # Unit tests only
pytest tests/e2e/ -v               # E2E tests only
pytest tests/benchmarks/ -v        # Performance benchmarks

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run and stop on first failure
pytest tests/ -x

# Run specific test file
pytest tests/unit/test_security/test_security_config.py -v
```

### Code Quality
```powershell
# Format code (auto-fix)
black src tests --line-length 100

# Sort imports (auto-fix)
isort src tests

# Lint code (check only)
flake8 src tests

# Type checking
mypy src

# Security scan
bandit -r src
```

### Pre-commit Hooks
```powershell
# Install hooks (one-time setup)
pip install pre-commit
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Skip hooks for a commit (not recommended)
git commit -m "message" --no-verify
```

### Development Workflow
```powershell
# 1. Make changes to code

# 2. Pre-commit runs automatically on git commit
#    (formats, lints, type checks)

# 3. Run tests
pytest tests/ -v

# 4. Check coverage
pytest tests/ --cov=src --cov-report=html

# 5. Commit and push
git add .
git commit -m "feat: your feature description"
git push origin main
```

### Git Commit Message Format
```
<type>: <description>

Types:
  feat     - New feature
  fix      - Bug fix
  docs     - Documentation changes
  style    - Code style (formatting, missing semicolons, etc.)
  refactor - Code restructuring
  test     - Adding/updating tests
  chore    - Build process, dependencies
  perf     - Performance improvements
  ci       - CI/CD changes

Examples:
  feat: add voice emotion detection
  fix: resolve authentication timeout issue
  docs: update API reference for IoT module
  test: add E2E tests for collaboration workflows
```

---

## CI/CD Pipelines

### GitHub Actions (Automatic)
Triggers on every push and pull request:

1. **Main CI Pipeline** (`.github/workflows/ci.yml`)
   - Runs on: Python 3.9, 3.10, 3.11
   - Executes: All 211 tests
   - Generates: Coverage report → Codecov
   - Builds: Distribution package
   - Deploys: Documentation to GitHub Pages (on main branch)

2. **Security Pipeline** (`.github/workflows/security.yml`)
   - Runs: Weekly (Mondays) + on push/PR
   - Scans: safety, bandit, pip-audit, CodeQL
   - Reports: Security vulnerabilities

### Local CI Simulation
```powershell
# Simulate full CI pipeline locally
pytest tests/ -v                    # Run all tests
black src tests --check             # Check formatting
isort src tests --check-only        # Check imports
flake8 src tests                    # Lint
mypy src                            # Type check
bandit -r src                       # Security scan
```

---

## Key File Locations

### Configuration Files
```
.github/
  workflows/
    ci.yml                 # Main CI/CD pipeline
    security.yml           # Security scanning
  BADGES.md                # Badge reference

.pre-commit-config.yaml    # Pre-commit hooks
.editorconfig              # Editor settings
pyproject.toml             # Project config
setup.py                   # Package setup
```

### Documentation
```
docs/
  GETTING_STARTED.md       # Installation & setup
  USER_GUIDE.md            # Feature guide
  DEVELOPER_GUIDE.md       # Development guide
  API_REFERENCE.md         # API docs
  SECURITY_GUIDE.md        # Security features
  DEPLOYMENT_GUIDE.md      # Deployment

CONTRIBUTING.md            # Contribution guidelines
CICD_SETUP.md             # CI/CD infrastructure guide
PRODUCTION_READY.md       # Production status report
README.md                 # Project overview
```

### Source Code
```
src/
  ai/                      # ML & personalization
  collaboration/           # Team features
  iot/                     # Smart home
  ml/                      # Analytics
  security/                # Auth & encryption
  voice/                   # Voice engine
  ui/                      # User interface
  integrations/            # External APIs
  jarvis.py               # Main entry point
```

### Tests
```
tests/
  unit/                    # 132 unit tests
  integration/             # 5 integration tests
  e2e/                     # 39 E2E tests
  benchmarks/              # 15 performance tests
```

---

## Common Tasks

### First-Time Setup
```powershell
# 1. Clone repository
git clone https://github.com/yourusername/XENO-ai-assistant.git
cd XENO-ai-assistant

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Install pre-commit hooks
pre-commit install

# 5. Run tests to verify
pytest tests/ -v
```

### Daily Development
```powershell
# 1. Activate environment
.\venv\Scripts\activate

# 2. Pull latest changes
git pull origin main

# 3. Make your changes

# 4. Run tests
pytest tests/ -v

# 5. Commit (pre-commit auto-runs)
git add .
git commit -m "feat: your feature"
git push origin main
```

### Adding a New Feature
```powershell
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Write code + tests
#    - Add feature code in src/
#    - Add tests in tests/unit/ or tests/e2e/

# 3. Run tests
pytest tests/ -v

# 4. Ensure coverage
pytest tests/ --cov=src --cov-report=term-missing

# 5. Commit and push
git add .
git commit -m "feat: add your feature"
git push origin feature/your-feature-name

# 6. Create Pull Request on GitHub
#    CI/CD will run automatically
```

### Fixing a Bug
```powershell
# 1. Create bug fix branch
git checkout -b fix/bug-description

# 2. Write failing test (reproduces bug)
#    Add to appropriate test file

# 3. Fix the bug
#    Modify source code

# 4. Verify test passes
pytest tests/path/to/test_file.py -v

# 5. Run all tests
pytest tests/ -v

# 6. Commit and push
git add .
git commit -m "fix: resolve bug description"
git push origin fix/bug-description
```

---

## Troubleshooting

### Pre-commit Hook Failures
```powershell
# If black fails (formatting)
black src tests --line-length 100
git add .
git commit -m "your message"

# If isort fails (imports)
isort src tests
git add .
git commit -m "your message"

# If flake8 fails (linting)
flake8 src tests                      # See errors
# Fix errors manually, then commit

# If mypy fails (type checking)
mypy src                              # See errors
# Fix type hints, then commit
```

### Test Failures
```powershell
# Run specific test to see details
pytest tests/path/to/test_file.py::test_name -v

# Run with full traceback
pytest tests/ -v --tb=long

# Run with print statements visible
pytest tests/ -v -s

# Stop on first failure
pytest tests/ -x
```

### GitHub Actions Failures
```bash
# 1. Check workflow status on GitHub
#    https://github.com/yourusername/repo/actions

# 2. Download workflow logs

# 3. Reproduce locally
pytest tests/ -v                      # Run same tests
python -m pip list                    # Check dependencies

# 4. Fix and push
git add .
git commit -m "fix: resolve CI failure"
git push origin main
```

---

## Performance Tips

### Running Tests Faster
```powershell
# Run only changed tests (pytest-watch)
pip install pytest-watch
ptw tests/

# Run in parallel (pytest-xdist)
pip install pytest-xdist
pytest tests/ -n auto                 # Auto-detect CPU cores

# Skip slow tests
pytest tests/ -m "not slow"
```

### Development Optimization
```powershell
# Use pytest cache
pytest tests/ -v                      # First run (builds cache)
pytest tests/ --lf                    # Only last failed
pytest tests/ --ff                    # Failed first, then rest

# Use coverage cache
pytest tests/ --cov=src --cov-append
```

---

## Metrics at a Glance

### Test Suite
- **Total Tests**: 211
- **Pass Rate**: 100%
- **Coverage**: ~85% (focus on user-facing code)
- **Average Runtime**: ~51 seconds

### Performance Targets
- **99%** operations < 100ms ✅
- **95%** operations < 20ms ✅
- **Device ops**: < 200ns ✅

### Code Quality Targets
- **Pylint**: > 9.0/10 ✅
- **Type Coverage**: > 80% ✅
- **Security Scan**: 0 vulnerabilities ✅

---

## Getting Help

### Documentation
1. Read `GETTING_STARTED.md` - First steps
2. Check `USER_GUIDE.md` - Feature usage
3. Review `API_REFERENCE.md` - API details
4. See `DEVELOPER_GUIDE.md` - Architecture

### Community
- GitHub Issues - Bug reports, feature requests
- GitHub Discussions - Questions, ideas
- CONTRIBUTING.md - How to contribute

### Emergency
- Security issues → GitHub Security Advisories
- Critical bugs → GitHub Issues (priority label)

---

**Pro Tip**: Run `pre-commit run --all-files` before pushing to catch issues early!

*Last updated: 2025*
