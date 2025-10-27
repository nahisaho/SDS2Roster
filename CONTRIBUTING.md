# Contributing to SDS2Roster

Thank you for your interest in contributing to SDS2Roster! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- pip

### Setting Up Development Environment

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/SDS2Roster.git
cd SDS2Roster
```

2. **Create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

3. **Install dependencies**

```bash
pip install -e ".[dev]"
```

4. **Verify installation**

```bash
pytest tests/ -v
```

## Development Workflow

### Creating a Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Making Changes

1. Write your code
2. Add or update tests
3. Update documentation if needed
4. Run quality checks (see below)

### Quality Checks

Before committing, run these checks:

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check linting
ruff check src/ tests/ --fix

# Run type checker
mypy src/

# Run tests
pytest tests/ -v --cov=src/sds2roster

# Check coverage threshold
pytest tests/ --cov=src/sds2roster --cov-report=term --cov-fail-under=90
```

### Committing Changes

Follow these commit message conventions:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Example:**

```bash
git commit -m "feat(converter): add support for custom metadata fields"
```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for formatting (line length: 100)
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use [Ruff](https://github.com/astral-sh/ruff) for linting

### Type Hints

Always use type hints:

```python
def convert_data(sds_data: SDSDataModel) -> OneRosterDataModel:
    """Convert SDS data to OneRoster format.
    
    Args:
        sds_data: Input SDS data model
        
    Returns:
        Converted OneRoster data model
    """
    ...
```

### Documentation

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of the function.
    
    Longer description if needed, explaining the function's behavior,
    edge cases, and any important implementation details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: If param2 is negative
        
    Example:
        >>> example_function("test", 42)
        True
    """
    ...
```

### Code Organization

- Keep functions small and focused
- Use meaningful variable names
- Avoid magic numbers (use constants)
- Separate concerns (single responsibility)
- Keep module imports organized:
  1. Standard library
  2. Third-party packages
  3. Local imports

## Testing

### Writing Tests

- Write tests for all new features
- Update tests when changing existing code
- Aim for 90%+ code coverage
- Use descriptive test names

**Test structure:**

```python
def test_feature_description() -> None:
    """Test that feature behaves correctly under specific conditions."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result.expected_property == expected_value
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/unit/test_converter.py -v

# Specific test
pytest tests/unit/test_converter.py::test_convert_empty_data -v

# With coverage
pytest tests/ --cov=src/sds2roster --cov-report=html

# Integration tests only
pytest tests/integration/ -v
```

### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test complete workflows
- **Fixtures**: Use pytest fixtures for reusable test data

## Pull Request Process

### Before Submitting

1. ✅ All tests pass locally
2. ✅ Code coverage is 90% or higher
3. ✅ Linters and formatters pass
4. ✅ Type checking passes
5. ✅ Documentation is updated
6. ✅ CHANGELOG is updated (if applicable)

### Submitting a Pull Request

1. Push your branch to your fork
2. Open a pull request against `main`
3. Fill out the PR template completely
4. Link related issues
5. Wait for CI checks to pass
6. Respond to review comments

### PR Title Format

```
<type>(<scope>): <description>
```

Example:
```
feat(cli): add verbose output option
```

### PR Description

Use the provided template and include:

- What changes were made
- Why the changes were necessary
- How to test the changes
- Screenshots (if UI changes)
- Related issues

### Review Process

1. Automated checks must pass (CI/CD)
2. At least one maintainer review required
3. Address all review comments
4. Maintainer will merge when approved

## Reporting Bugs

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:

- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Sample data (if applicable)
- Error messages and stack traces

## Suggesting Enhancements

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:

- Clear description of the feature
- Problem it solves
- Proposed solution
- Use cases
- Alternative solutions considered

## Code Review Guidelines

### For Reviewers

- Be respectful and constructive
- Focus on code quality, not personal preferences
- Provide specific, actionable feedback
- Approve when standards are met

### For Authors

- Respond to all comments
- Ask questions if unclear
- Make requested changes promptly
- Thank reviewers for their time

## Project Structure

```
SDS2Roster/
├── .github/              # GitHub configuration
│   ├── workflows/        # CI/CD workflows
│   └── ISSUE_TEMPLATE/   # Issue templates
├── docs/                 # Documentation
│   └── requirements/     # Requirements documents
├── src/                  # Source code
│   └── sds2roster/      # Main package
│       ├── models/       # Data models
│       ├── parsers/      # CSV parsers
│       ├── utils/        # Utilities
│       ├── cli.py        # CLI interface
│       └── converter.py  # Conversion logic
├── tests/                # Tests
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── fixtures/        # Test data
├── pyproject.toml       # Project configuration
└── README.md            # Project readme
```

## Release Process

Releases are managed by maintainers:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create and push version tag
4. GitHub Actions handles the rest

## Questions?

If you have questions:

1. Check existing documentation
2. Search [Issues](https://github.com/nahisaho/SDS2Roster/issues)
3. Open a new issue with the question label

## Thank You!

Your contributions make this project better for everyone. Thank you for taking the time to contribute! 🎉
