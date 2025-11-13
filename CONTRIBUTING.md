# Contributing to Vibe Scraper SaaS

Thank you for your interest in contributing to Vibe Scraper SaaS! This document provides guidelines and information for contributors.

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to uphold this code.

## Getting Started

### Development Environment Setup

1. **Prerequisites**
   - Python 3.11+
   - Poetry for dependency management
   - Docker and Docker Compose
   - Git

2. **Clone and Setup**
   ```bash
   git clone https://github.com/evanokeefe39/vibe-code-ig-scraper-saas.git
   cd vibe-code-ig-scraper-saas
   poetry install
   ```

3. **Database Setup**
   ```bash
   docker-compose up -d postgres
   poetry run python manage.py migrate
   ```

4. **Run Development Server**
   ```bash
   poetry run python manage.py runserver
   ```

### Branching Strategy

- **Main Branch**: `master` - Production-ready code
- **Feature Branches**: `feature/feature-name` - New features
- **Bugfix Branches**: `bugfix/issue-number-description` - Bug fixes
- **Documentation**: `docs/description` - Documentation updates

Branch naming: Use lowercase, hyphen-separated names.

### Commit Message Guidelines

We follow [Conventional Commits](https://conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

Examples:
- `feat: add user authentication`
- `fix: resolve database connection issue`
- `docs: update API documentation`

## Issue Management

### Creating Issues

Use appropriate issue templates for:
- **Bug Reports**: Report bugs with reproduction steps
- **Feature Requests**: Propose new features with use cases
- **Tasks**: General development tasks

### Issue Lifecycle

1. **Draft**: Initial idea or incomplete information
2. **Backlog**: Triaged and prioritized
3. **Ready**: Fully specified and ready for development
4. **In Progress**: Actively being worked on
5. **Review**: Code review in progress
6. **Closed**: Completed or resolved

### Labels and Priority

**Priority Levels:**
- `priority: critical` - Blocks development
- `priority: high` - Important for next release
- `priority: medium` - Should be addressed
- `priority: low` - Nice to have

**Status Labels:**
- `status: backlog` - Not yet prioritized
- `status: ready` - Ready for development
- `status: in progress` - Currently being worked on
- `status: review` - Under review
- `status: blocked` - Waiting on dependencies

**Component Labels:**
- `component: frontend` - Django templates, UI
- `component: backend` - Django views, APIs
- `component: database` - Models, migrations
- `component: n8n` - Workflow orchestration
- `component: docs` - Documentation

## Pull Request Process

### Creating Pull Requests

1. **Branch**: Create from `master`, use descriptive branch name
2. **Commits**: Squash related commits, follow commit guidelines
3. **Tests**: Ensure all tests pass
4. **Documentation**: Update docs for any API/user-facing changes

### PR Template Requirements

PRs must include:
- Clear title following commit conventions
- Description of changes and rationale
- Screenshots for UI changes
- Testing instructions
- Related issues (Closes #123)

### Review Process

1. **Automated Checks**: CI must pass
2. **Code Review**: At least one approval required
3. **Testing**: Reviewer should test changes
4. **Merge**: Squash merge with conventional commit message

### Merge Guidelines

- **Squash Merges**: Combine related commits
- **Linear History**: Maintain clean git history
- **No Force Pushes**: After reviews begin

## Development Workflow

### Code Quality

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Maintain >80% test coverage

### Testing

- Write unit tests for new functionality
- Integration tests for API endpoints
- Manual testing for UI features
- All tests must pass before merging

### Documentation

- Update README.md for setup changes
- Document new API endpoints
- Update architecture docs for significant changes
- Keep changelog current

### Security

- Never commit secrets or credentials
- Use environment variables for configuration
- Validate all user inputs
- Follow OWASP guidelines

## Release Process

1. **Versioning**: Follow semantic versioning (MAJOR.MINOR.PATCH)
2. **Changelog**: Update CHANGELOG.md with changes
3. **Testing**: Full regression testing
4. **Release**: Create GitHub release with notes
5. **Deployment**: Automated deployment to production

## Getting Help

- **Issues**: Use GitHub issues for bugs and features
- **Discussions**: General questions and ideas
- **Documentation**: Check existing docs first

Thank you for contributing to Vibe Scraper SaaS! 🎉