# Contributing to Feishu Bot SDK

Thank you for your interest in contributing to the Feishu Bot SDK! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git

### Setting Up Your Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/feishu-bot-sdk.git
   cd feishu-bot-sdk
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install the package in development mode with dev dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Running Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=feishu_sdk --cov-report=html
```

### Code Style

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **mypy** for type checking

Run formatters:
```bash
black feishu_sdk tests
isort feishu_sdk tests
```

Run type checker:
```bash
mypy feishu_sdk
```

### Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and write tests for new functionality

3. Ensure all tests pass:
   ```bash
   pytest
   ```

4. Format your code:
   ```bash
   black feishu_sdk tests
   isort feishu_sdk tests
   ```

5. Commit your changes with a descriptive message:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

6. Push to your fork and submit a pull request

## Pull Request Guidelines

- Include tests for any new functionality
- Update documentation as needed
- Follow the existing code style
- Keep pull requests focused on a single topic
- Write clear commit messages

## Reporting Issues

When reporting issues, please include:
- A clear description of the problem
- Steps to reproduce the issue
- Expected vs actual behavior
- Python version and OS
- Relevant error messages or logs

## Code of Conduct

Please be respectful and constructive in all interactions. We welcome contributors of all experience levels.

## Questions?

Feel free to open an issue for any questions about contributing.
