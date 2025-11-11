# Contributing to Demand Letter Generator

Thank you for your interest in contributing to the Demand Letter Generator project! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a positive and collaborative environment

## Getting Started

1. **Fork the repository** and clone your fork locally
2. **Set up your development environment** following the instructions in [README.md](README.md)
3. **Create a branch** for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix-name
   ```

## Development Guidelines

### Code Style

**Python (Backend):**
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Format code with `black` (if configured)
- Maximum line length: 100 characters
- Use meaningful variable and function names

**JavaScript/React (Frontend):**
- Follow ESLint configuration
- Use functional components with hooks
- Follow React best practices
- Use meaningful component and variable names
- Format code with Prettier (if configured)

### Commit Messages

Write clear, descriptive commit messages:

```
feat: Add document upload functionality
fix: Resolve PDF parsing error for encrypted files
docs: Update API documentation
refactor: Simplify template service logic
test: Add unit tests for letter generation
```

Use conventional commit format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `refactor:` for code refactoring
- `test:` for adding or updating tests
- `chore:` for maintenance tasks

### Testing

- Write tests for new features and bug fixes
- Ensure all existing tests pass before submitting
- Aim for meaningful test coverage
- Test both success and error cases

**Backend Testing:**
```bash
cd backend
pytest
```

**Frontend Testing:**
```bash
cd frontend
npm test
```

### Pull Request Process

1. **Update documentation** if you've changed functionality
2. **Ensure your code follows the project's style guidelines**
3. **Run tests** and ensure they pass
4. **Update the CHANGELOG.md** (if applicable) with your changes
5. **Create a pull request** with a clear description:
   - What changes were made
   - Why the changes were necessary
   - How to test the changes
   - Any breaking changes

### Pull Request Checklist

Before submitting a pull request, ensure:

- [ ] Code follows the project's style guidelines
- [ ] All tests pass locally
- [ ] New tests are added for new functionality
- [ ] Documentation is updated (if needed)
- [ ] Commit messages follow the conventional format
- [ ] No console errors or warnings
- [ ] Code is reviewed for security issues
- [ ] Environment variables are documented (if new ones are added)

## Project Structure

### Backend Structure

```
backend/
├── services/           # Service modules
│   ├── document_service/
│   ├── template_service/
│   ├── parser_service/
│   ├── ai_service/
│   └── letter_service/
├── shared/            # Shared utilities
│   ├── database.py
│   ├── s3_client.py
│   └── config.py
└── main.py           # Local development entry point
```

### Frontend Structure

```
frontend/src/
├── components/       # Reusable React components
├── pages/            # Page components
├── hooks/            # Custom React hooks
├── utils/            # Utility functions
└── lib/              # Third-party library configurations
```

## Adding New Features

1. **Discuss major changes** by opening an issue first
2. **Follow the existing architecture patterns**
3. **Update relevant documentation**
4. **Add appropriate tests**
5. **Consider backward compatibility**

## Reporting Bugs

When reporting bugs, please include:

- **Description:** Clear description of the bug
- **Steps to Reproduce:** Detailed steps to reproduce the issue
- **Expected Behavior:** What you expected to happen
- **Actual Behavior:** What actually happened
- **Environment:** OS, browser, Node.js/Python versions
- **Screenshots:** If applicable
- **Error Messages:** Full error messages or stack traces

## Feature Requests

For feature requests:

- **Open an issue** with the `enhancement` label
- **Describe the feature** clearly
- **Explain the use case** and why it would be valuable
- **Consider alternatives** and trade-offs

## Code Review

All pull requests require review before merging. Reviewers will check:

- Code quality and style
- Test coverage
- Documentation updates
- Security considerations
- Performance implications

## Questions?

If you have questions about contributing:

- Open an issue with the `question` label
- Check existing documentation
- Review closed issues and pull requests

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to the Demand Letter Generator!

