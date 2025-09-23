# 🤝 Contributing to Cloud Misconfiguration Auto Scanner

We love your input! We want to make contributing to the Cloud Misconfiguration Auto Scanner as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Development Setup](#️-development-setup)
- [Development Workflow](#-development-workflow)
- [Code Style Guidelines](#-code-style-guidelines)
- [Testing](#-testing)
- [Submitting Changes](#-submitting-changes)
- [Issue Reporting](#-issue-reporting)
- [Feature Requests](#-feature-requests)
- [Security Issues](#-security-issues)
- [Documentation](#-documentation)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Harassment of any form
- Discriminatory language or actions
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## ⚡️ Development Setup

### Prerequisites

- **Python 3.8+** (Python 3.12 recommended)
- **Git** for version control
- **Azure CLI** for authentication testing
- **Azure Subscription** with appropriate permissions
- **Code Editor** (VS Code recommended)

### Initial Setup

1. **Fork and clone the repository**
   ```bash
   # Fork the repo on GitHub first, then clone your fork
   git clone https://github.com/YOUR_USERNAME/Cloud_Misconfiguration_Auto_Scanner.git
   cd Cloud_Misconfiguration_Auto_Scanner
   ```

2. **Set up upstream remote**
   ```bash
   git remote add upstream https://github.com/AnirudhDattu/Cloud_Misconfiguration_Auto_Scanner.git
   git remote -v  # Verify remotes are set correctly
   ```

3. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate it
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   # Install all dependencies including dev dependencies
   pip install -r requirements.txt
   
   # Install additional development tools
   pip install pytest black flake8 mypy pre-commit
   ```

5. **Set up pre-commit hooks** (Optional but recommended)
   ```bash
   pre-commit install
   ```

6. **Configure environment variables**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit with your Azure credentials (for testing)
   # Note: Never commit real credentials!
   ```

### Development Environment Verification

Run the following commands to verify your setup:

```bash
# Test Python imports
python -c "import streamlit, azure.identity; print('Dependencies OK')"

# Test basic app launch (should open browser)
streamlit run app.py --server.headless true --server.port 8502
```

## 🔄 Development Workflow

### Branch Naming Convention

Use descriptive branch names with prefixes:

- `feature/add-aws-support` - New features
- `bugfix/fix-auth-error` - Bug fixes
- `hotfix/security-patch` - Critical security fixes
- `docs/update-readme` - Documentation updates
- `refactor/improve-scanner-performance` - Code refactoring
- `test/add-unit-tests` - Test additions

### Making Changes

1. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Keep your branch updated**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

3. **Make your changes**
   - Write clean, readable code
   - Follow the coding standards
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Run tests
   python -m pytest tests/
   
   # Run linting
   flake8 .
   black --check .
   
   # Test the application
   python run_scan.py  # CLI test
   streamlit run app.py  # UI test
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add AWS EC2 instance scanning"
   ```

## 🎨 Code Style Guidelines

### Python Style Guide

We follow **PEP 8** with some specific conventions:

#### General Guidelines
- Use 4 spaces for indentation (no tabs)
- Line length: 88 characters (Black formatter standard)
- Use descriptive variable and function names
- Add docstrings for all public functions and classes

#### Naming Conventions
```python
# Variables and functions: snake_case
user_name = "john_doe"
def get_storage_accounts():
    pass

# Classes: PascalCase
class SecurityScanner:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
AZURE_API_VERSION = "2023-01-01"

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

#### Import Organization
```python
# Standard library imports
import json
import os
from datetime import datetime

# Third-party imports
import streamlit as st
from azure.identity import ClientSecretCredential

# Local application imports
from scanner.utils import get_credential
from db.models import Finding
```

#### Function Documentation
```python
def check_storage_public_blob_access(storage_accounts):
    """
    Analyze storage accounts for public blob access misconfigurations.
    
    Args:
        storage_accounts (list): List of storage account dictionaries from inventory
        
    Returns:
        list: List of finding dictionaries containing security violations
        
    Raises:
        ValueError: If storage_accounts is not a valid list
        AzureError: If Azure API calls fail
    """
    pass
```

#### Error Handling
```python
# Good: Specific exception handling with logging
try:
    storage_accounts = list_storage_accounts()
except AzureError as e:
    logger.error(f"Failed to retrieve storage accounts: {e}")
    return []
except Exception as e:
    logger.exception("Unexpected error during storage account retrieval")
    raise
```

### Code Formatting

We use **Black** as our code formatter:

```bash
# Format all Python files
black .

# Check formatting without making changes
black --check .

# Format specific files
black app.py scanner/
```

### Linting

We use **Flake8** for linting:

```bash
# Run linting on all files
flake8 .

# Run linting with specific configuration
flake8 --max-line-length=88 --extend-ignore=E203,W503
```

### Type Hints

Use type hints for better code clarity:

```python
from typing import List, Dict, Optional, Any

def scan_resources(
    resource_ids: List[str], 
    scan_type: str = "full"
) -> Dict[str, Any]:
    """Scan specified resources and return findings."""
    findings: List[Dict[str, Any]] = []
    return {"findings": findings, "scan_type": scan_type}
```

## 🧪 Testing

### Test Structure

```
tests/
├── unit/
│   ├── test_scanner_utils.py
│   ├── test_checks_azure.py
│   ├── test_check_vms.py
│   └── test_check_nsg.py
├── integration/
│   ├── test_azure_integration.py
│   └── test_database_operations.py
└── fixtures/
    ├── sample_storage_accounts.json
    └── mock_azure_responses.py
```

### Writing Tests

#### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch
from scanner.checks_azure import check_storage_public_blob_access

class TestStorageChecks:
    """Test cases for Azure storage security checks."""
    
    def test_public_blob_access_detection(self):
        """Test detection of storage accounts with public blob access."""
        # Arrange
        mock_accounts = [
            {
                "name": "test-storage",
                "id": "/subscriptions/.../storageAccounts/test-storage",
                "properties": Mock(allow_blob_public_access=True)
            }
        ]
        
        # Act
        findings = check_storage_public_blob_access(mock_accounts)
        
        # Assert
        assert len(findings) == 1
        assert findings[0]["severity"] == "High"
        assert "public blob access" in findings[0]["title"].lower()
        
    def test_no_findings_for_secure_storage(self):
        """Test that secure storage accounts produce no findings."""
        mock_accounts = [
            {
                "name": "secure-storage",
                "properties": Mock(allow_blob_public_access=False)
            }
        ]
        
        findings = check_storage_public_blob_access(mock_accounts)
        assert len(findings) == 0
```

#### Integration Tests
```python
@pytest.mark.integration
class TestAzureIntegration:
    """Integration tests requiring Azure credentials."""
    
    @pytest.fixture
    def azure_client(self):
        """Fixture providing authenticated Azure client."""
        if not os.getenv("AZURE_CLIENT_ID"):
            pytest.skip("Azure credentials not available")
        return get_authenticated_client()
    
    def test_storage_account_listing(self, azure_client):
        """Test actual Azure storage account listing."""
        accounts = list_storage_accounts()
        assert isinstance(accounts, list)
        # Add more specific assertions
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=scanner --cov-report=html

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest -m "not integration"  # Skip integration tests

# Run tests with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/unit/test_checks_azure.py
```

### Test Data and Fixtures

Create reusable test data in the `tests/fixtures/` directory:

```python
# tests/fixtures/sample_data.py
SAMPLE_STORAGE_ACCOUNTS = [
    {
        "name": "secure-storage",
        "id": "/subscriptions/test/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/secure-storage",
        "resource_group": "test-rg",
        "properties": {
            "allow_blob_public_access": False
        }
    },
    # More test data...
]
```

### Continuous Integration

Our CI pipeline runs the following checks:
- Code formatting (Black)
- Linting (Flake8)
- Type checking (MyPy)
- Unit tests with coverage
- Integration tests (if credentials available)

## 📤 Submitting Changes

### Pull Request Process

1. **Ensure your code passes all checks**
   ```bash
   # Run the full test suite
   black .
   flake8 .
   python -m pytest
   ```

2. **Update documentation**
   - Update README.md if you're adding new features
   - Add docstrings to new functions
   - Update any relevant API documentation

3. **Create a pull request**
   - Use a descriptive title
   - Fill out the PR template completely
   - Link any related issues
   - Add screenshots for UI changes

### Pull Request Template

When creating a PR, please include:

```markdown
## Description
Brief description of the changes and why they were made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass (if applicable)
- [ ] Manual testing performed

## Screenshots (if applicable)
Include screenshots for UI changes.

## Checklist
- [ ] Code follows the project's coding standards
- [ ] Self-review of the code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Corresponding changes to documentation made
- [ ] No new warnings introduced
```

### Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(scanner): add AWS EC2 instance scanning support

fix(ui): resolve dashboard loading issue with empty database

docs(readme): update installation instructions for Python 3.12

test(checks): add comprehensive unit tests for NSG scanning
```

## 🐛 Issue Reporting

### Before Reporting an Issue

1. **Search existing issues** to avoid duplicates
2. **Update to the latest version** and test again
3. **Check the documentation** for known issues
4. **Gather relevant information** (logs, system info, etc.)

### Bug Report Template

```markdown
## Bug Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
A clear description of what you expected to happen.

## Actual Behavior
A clear description of what actually happened.

## Environment
- OS: [e.g., Windows 10, macOS 12.0, Ubuntu 20.04]
- Python version: [e.g., 3.12.0]
- Package versions: [run `pip freeze` and paste relevant packages]
- Browser (for UI issues): [e.g., Chrome 91.0]

## Additional Context
- Error logs or screenshots
- Azure subscription type (if relevant)
- Network configuration (if relevant)
```

### Issue Labels

We use the following labels to categorize issues:

- **bug**: Something isn't working
- **enhancement**: New feature or request
- **documentation**: Improvements or additions to documentation
- **good first issue**: Good for newcomers
- **help wanted**: Extra attention is needed
- **priority/high**: High priority issue
- **priority/low**: Low priority issue

## 💡 Feature Requests

We welcome feature requests! Please:

1. **Check existing feature requests** first
2. **Provide a clear use case** and business value
3. **Consider the scope** - will this benefit most users?
4. **Be willing to contribute** to the implementation

### Feature Request Template

```markdown
## Feature Description
A clear and concise description of the feature you'd like to see.

## Problem Statement
What problem does this feature solve? Who would benefit from it?

## Proposed Solution
A clear description of what you want to happen.

## Alternatives Considered
A clear description of any alternative solutions you've considered.

## Implementation Notes
Any technical considerations or implementation ideas.

## Additional Context
Add any other context, mockups, or examples about the feature request here.
```

## 🔒 Security Issues

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please email security concerns to: [Insert security email]

Include the following information:
- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Any suggested fixes

We'll acknowledge your email within 48 hours and provide a detailed response within 72 hours indicating next steps.

## 📚 Documentation

### Documentation Types

1. **Code Documentation**
   - Docstrings for all public functions
   - Inline comments for complex logic
   - Type hints where appropriate

2. **User Documentation**
   - README.md updates
   - Usage examples
   - Configuration guides

3. **Developer Documentation**
   - Architecture decisions
   - API documentation
   - Development guides

### Documentation Standards

- Use **Markdown** for all documentation files
- Include **code examples** where helpful
- Keep documentation **up-to-date** with code changes
- Use **clear, concise language**
- Include **screenshots** for UI-related documentation

### Building Documentation Locally

```bash
# Install documentation dependencies
pip install -r docs/requirements.txt

# Build documentation (if using Sphinx)
cd docs
make html

# Serve documentation locally
python -m http.server 8000 -d _build/html
```

## 🏆 Recognition

Contributors are recognized in the following ways:

- **README.md acknowledgments** for significant contributions
- **Release notes mentions** for features and fixes
- **Contributor badges** based on contribution level
- **Maintainer status** for consistent, high-quality contributions

### Contribution Levels

- **Contributor**: Made one or more accepted contributions
- **Regular Contributor**: 5+ accepted contributions
- **Core Contributor**: 20+ contributions and consistent engagement
- **Maintainer**: Trusted with repository management

## 📞 Getting Help

If you need help with contributing:

1. **Read this guide thoroughly**
2. **Check existing issues and discussions**
3. **Join our community chat** (if available)
4. **Create a discussion** for general questions
5. **Create an issue** for specific problems

## 🎉 Thank You!

Thank you for considering contributing to the Cloud Misconfiguration Auto Scanner! Your contributions help make cloud security more accessible to everyone.

---

<div align="center">
  <strong>Happy Contributing! 🚀</strong>
</div>