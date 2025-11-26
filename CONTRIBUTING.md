# Contributing to XENO AI Assistant

Thank you for your interest in contributing to XENO! This document provides guidelines and instructions for contributing.

## 🎯 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the community
- Show empathy towards others

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/XENO-ai-assistant.git
cd XENO-ai-assistant
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"  # Install in editable mode with dev dependencies

# Install pre-commit hooks
pre-commit install
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## 📝 Development Workflow

### Code Style

We use the following tools to maintain code quality:

- **Black** for code formatting (line length: 100)
- **isort** for import sorting
- **flake8** for linting
- **pylint** for static analysis
- **mypy** for type checking

Run before committing:

```bash
# Format code
black src tests --line-length 100

# Sort imports
isort src tests

# Check linting
flake8 src --max-line-length=100

# Run pylint
pylint src --max-line-length=100

# Or use pre-commit to run all checks
pre-commit run --all-files
```

### Testing

All contributions must include tests:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit -v
pytest tests/integration -v
pytest tests/e2e -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run benchmarks
pytest tests/benchmarks --benchmark-only
```

**Test Requirements:**
- Unit tests for new functions/classes
- Integration tests for multi-component features
- E2E tests for complete user workflows
- Maintain 100% pass rate
- Add benchmarks for performance-critical code

### Documentation

- Add docstrings to all public functions/classes
- Update README.md if adding user-facing features
- Update API_REFERENCE.md for new APIs
- Add comments for complex logic

**Docstring Format:**

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When something goes wrong
    """
    pass
```

## 🔍 Pull Request Process

### 1. Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass (100% pass rate required)
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Pre-commit hooks pass
- [ ] No new security vulnerabilities

### 2. Commit Messages

Use conventional commit format:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `perf`: Performance improvements
- `chore`: Maintenance tasks

**Example:**

```
feat(voice): add emotion detection to voice engine

Implemented EmotionAnalyzer class that detects emotions from
text and audio features. Supports 8 emotion types.

Closes #123
```

### 3. Pull Request Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] E2E tests added/updated
- [ ] All tests passing

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests provide good coverage
```

### 4. Review Process

1. Automated CI/CD checks must pass
2. Code review by maintainers
3. Address feedback and update PR
4. Approval from at least one maintainer
5. Merge by maintainer

## 🐛 Reporting Bugs

### Before Submitting

- Check existing issues
- Verify it's reproducible
- Gather relevant information

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**To Reproduce**
1. Step 1
2. Step 2
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: Windows 11
- Python: 3.9.7
- XENO Version: 1.0.0

**Logs/Screenshots**
Attach relevant logs or screenshots
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Problem Statement**
What problem does this solve?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other approaches you've thought about

**Additional Context**
Any other relevant information
```

## 📂 Project Structure

```
XENO-ai-assistant/
├── src/                    # Source code
│   ├── collaboration/      # Team features
│   ├── iot/               # Smart home integration
│   ├── ml/                # AI/ML modules
│   ├── security/          # Security features
│   ├── voice/             # Voice engine
│   └── ...
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── e2e/              # End-to-end tests
│   └── benchmarks/       # Performance tests
├── docs/                 # Documentation
└── .github/              # GitHub workflows
```

## 🎨 Areas for Contribution

### High Priority
- Bug fixes
- Security improvements
- Performance optimizations
- Test coverage improvements
- Documentation enhancements

### Medium Priority
- New integrations (Slack, Discord, etc.)
- UI/UX improvements
- Voice command additions
- Smart home device support

### Low Priority
- Code refactoring
- Additional examples
- Translations
- Theme customization

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- GitHub contributors page

## 📞 Getting Help

- **Questions**: Open a GitHub Discussion
- **Chat**: Join our Discord (coming soon)
- **Email**: dev@XENO-ai.com

---

Thank you for contributing to XENO! 🚀
