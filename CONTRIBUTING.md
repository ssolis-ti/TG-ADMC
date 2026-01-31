# Contributing to TG-ADMC

Thank you for your interest in contributing to TG-ADMC! This document provides guidelines for contributing to the project.

---

## 🌳 Branching Strategy

Please read our [Branching Strategy](BRANCHING_STRATEGY.md) for detailed information on:

- Branch types and naming conventions
- Workflow examples
- Commit message format
- Pull request guidelines

---

## 🚀 Quick Start for Contributors

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR-USERNAME/TG-ADMC.git
cd TG-ADMC
```

### 2. Set Up Development Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
# (See README.md for details)

# Build and run
docker-compose up -d
```

### 3. Create a Feature Branch

```bash
# Always branch from develop
git checkout develop
git pull origin develop

# Create your feature branch
git checkout -b feature/your-feature-name
```

### 4. Make Your Changes

- Write clean, documented code
- Follow existing code style
- Add tests if applicable
- Update documentation

### 5. Commit Your Changes

Use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add .
git commit -m "feat: add your feature description"
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub targeting the `develop` branch.

---

## 📝 Commit Message Format

```
<type>(<scope>): <subject>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `perf`: Performance improvement
- `test`: Tests
- `chore`: Maintenance

### Examples

```bash
feat(api): add analytics endpoint
fix(payment): resolve timeout issue
docs(readme): update installation steps
```

---

## 🔍 Code Review Process

1. **Automated Checks**: CI/CD runs tests and linting
2. **Peer Review**: At least 1 approval required
3. **Maintainer Review**: Final check by project maintainer
4. **Merge**: Squash and merge to keep history clean

---

## 🧪 Testing Guidelines

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Writing Tests

- Test files: `tests/test_*.py`
- Use descriptive test names
- Cover happy path and edge cases
- Mock external dependencies

---

## 📋 Pull Request Template

```markdown
## What

Brief description of changes

## Why

Reason for the change

## How

Technical approach

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if UI changes)

Before/after images

## Checklist

- [ ] Code follows project style
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or documented)
```

---

## 🎨 Code Style

### Python

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use `black` for formatting
- Use `mypy` for type checking
- Max line length: 100 characters

```bash
# Format code
black src/

# Check types
mypy src/
```

### JavaScript

- Use ES6+ syntax
- Use `prettier` for formatting
- Use descriptive variable names
- Add JSDoc comments for functions

```bash
# Format code
prettier --write src/static/js/
```

---

## 🐛 Reporting Bugs

### Before Reporting

1. Check existing issues
2. Verify it's reproducible
3. Test on latest version

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**

1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**

- OS: [e.g., Ubuntu 22.04]
- Docker version: [e.g., 20.10.0]
- Python version: [e.g., 3.11.14]

**Logs**
Relevant error messages or logs
```

---

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Problem**
What problem does this solve?

**Proposed Solution**
How would you solve it?

**Alternatives**
Other approaches considered

**Additional Context**
Any other relevant information
```

---

## 🔒 Security

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead, email: [Contact via GitHub]

Include:

- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 🙏 Recognition

Contributors will be recognized in:

- README.md acknowledgments
- Release notes
- Project documentation

---

## 📞 Questions?

- **Documentation**: See [docs/](docs/)
- **GitHub Issues**: For bugs and features
- **Discussions**: For questions and ideas

---

**Thank you for contributing to TG-ADMC!**

[@ssolis-ti](https://github.com/ssolis-ti) | [saiberaysen.cl](https://www.saiberaysen.cl)
