# Git Branching Strategy

> **Professional, organized, and LLM-friendly workflow for TG-ADMC**

---

## 🌳 Branch Structure

```
main (production-ready)
│
├── develop (integration branch)
│   │
│   ├── feature/* (new features)
│   │   ├── feature/dispute-resolution
│   │   ├── feature/analytics-dashboard
│   │   └── feature/multi-language
│   │
│   ├── enhancement/* (improvements)
│   │   ├── enhancement/performance-optimization
│   │   ├── enhancement/ui-polish
│   │   └── enhancement/error-handling
│   │
│   ├── bugfix/* (bug fixes)
│   │   ├── bugfix/payment-confirmation
│   │   └── bugfix/wallet-connection
│   │
│   └── docs/* (documentation)
│       ├── docs/api-reference
│       └── docs/deployment-guide
│
├── release/* (release preparation)
│   ├── release/v1.0.0
│   └── release/v1.1.0
│
└── hotfix/* (urgent production fixes)
    └── hotfix/critical-security-patch
```

---

## 📋 Branch Types

### 1. `main` - Production Branch

- **Purpose**: Production-ready code only
- **Protected**: Yes (requires PR approval)
- **Deployed to**: Production environment
- **Merge from**: `release/*` or `hotfix/*` only
- **Never commit directly**: Always via PR

### 2. `develop` - Integration Branch

- **Purpose**: Latest development changes
- **Protected**: Yes (requires PR approval)
- **Deployed to**: Staging environment
- **Merge from**: `feature/*`, `enhancement/*`, `bugfix/*`, `docs/*`
- **Merge to**: `release/*`

### 3. `feature/*` - New Features

- **Naming**: `feature/short-description`
- **Examples**:
  - `feature/dispute-resolution`
  - `feature/analytics-dashboard`
  - `feature/smart-contract-migration`
- **Branch from**: `develop`
- **Merge to**: `develop`
- **Lifespan**: Until feature complete

### 4. `enhancement/*` - Improvements

- **Naming**: `enhancement/short-description`
- **Examples**:
  - `enhancement/performance-optimization`
  - `enhancement/ui-polish`
  - `enhancement/caching-layer`
- **Branch from**: `develop`
- **Merge to**: `develop`
- **Lifespan**: Until enhancement complete

### 5. `bugfix/*` - Bug Fixes

- **Naming**: `bugfix/issue-description`
- **Examples**:
  - `bugfix/payment-confirmation-error`
  - `bugfix/wallet-disconnect-issue`
  - `bugfix/database-connection-timeout`
- **Branch from**: `develop`
- **Merge to**: `develop`
- **Lifespan**: Until bug fixed

### 6. `docs/*` - Documentation

- **Naming**: `docs/document-name`
- **Examples**:
  - `docs/api-reference`
  - `docs/deployment-guide`
  - `docs/architecture-update`
- **Branch from**: `develop`
- **Merge to**: `develop`
- **Lifespan**: Until documentation complete

### 7. `release/*` - Release Preparation

- **Naming**: `release/vX.Y.Z` (semantic versioning)
- **Examples**:
  - `release/v1.0.0`
  - `release/v1.1.0`
  - `release/v2.0.0`
- **Branch from**: `develop`
- **Merge to**: `main` AND `develop`
- **Lifespan**: Until release deployed

### 8. `hotfix/*` - Urgent Fixes

- **Naming**: `hotfix/critical-issue`
- **Examples**:
  - `hotfix/security-vulnerability`
  - `hotfix/payment-failure`
  - `hotfix/data-corruption`
- **Branch from**: `main`
- **Merge to**: `main` AND `develop`
- **Lifespan**: Until hotfix deployed

---

## 🔄 Workflow Examples

### Adding a New Feature

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/analytics-dashboard

# 3. Work on feature (commit frequently)
git add .
git commit -m "feat: add analytics data models"
git commit -m "feat: implement analytics API endpoints"
git commit -m "feat: create analytics UI components"

# 4. Push to remote
git push origin feature/analytics-dashboard

# 5. Create Pull Request to develop
# (via GitHub UI)

# 6. After approval and merge, delete branch
git checkout develop
git pull origin develop
git branch -d feature/analytics-dashboard
```

### Fixing a Bug

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create bugfix branch
git checkout -b bugfix/payment-confirmation-error

# 3. Fix the bug
git add .
git commit -m "fix: resolve payment confirmation race condition"

# 4. Push and create PR
git push origin bugfix/payment-confirmation-error

# 5. After merge, delete branch
git checkout develop
git pull origin develop
git branch -d bugfix/payment-confirmation-error
```

### Creating a Release

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create release branch
git checkout -b release/v1.0.0

# 3. Update version numbers, changelog
git add .
git commit -m "chore: bump version to 1.0.0"

# 4. Push release branch
git push origin release/v1.0.0

# 5. Create PR to main
# After approval, merge to main

# 6. Tag the release
git checkout main
git pull origin main
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 7. Merge back to develop
git checkout develop
git merge release/v1.0.0
git push origin develop

# 8. Delete release branch
git branch -d release/v1.0.0
```

### Emergency Hotfix

```bash
# 1. Start from main
git checkout main
git pull origin main

# 2. Create hotfix branch
git checkout -b hotfix/security-vulnerability

# 3. Fix the issue
git add .
git commit -m "fix: patch critical security vulnerability"

# 4. Push and create PR to main
git push origin hotfix/security-vulnerability

# 5. After merge to main, also merge to develop
git checkout develop
git merge hotfix/security-vulnerability
git push origin develop

# 6. Tag the hotfix
git checkout main
git tag -a v1.0.1 -m "Hotfix version 1.0.1"
git push origin v1.0.1

# 7. Delete hotfix branch
git branch -d hotfix/security-vulnerability
```

---

## 📝 Commit Message Convention

We use **Conventional Commits** for clear, structured commit history:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring (no feature/fix)
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, tooling
- `ci`: CI/CD configuration changes

### Examples

```bash
# Feature
git commit -m "feat(api): add analytics endpoint for channel stats"

# Bug fix
git commit -m "fix(payment): resolve race condition in confirmation flow"

# Documentation
git commit -m "docs(readme): update deployment instructions"

# Refactor
git commit -m "refactor(escrow): simplify state machine logic"

# Performance
git commit -m "perf(database): add index on deal.status column"

# Chore
git commit -m "chore(deps): upgrade fastapi to 0.110.0"
```

---

## 🤖 LLM-Friendly Guidelines

### Branch Naming

- **Use kebab-case**: `feature/analytics-dashboard` ✅
- **Not camelCase**: `feature/analyticsDashboard` ❌
- **Be descriptive**: `feature/add-analytics` ✅
- **Not vague**: `feature/update` ❌

### Commit Messages

- **Start with type**: `feat:`, `fix:`, `docs:` ✅
- **Be specific**: `fix: resolve payment timeout in TON SDK` ✅
- **Not generic**: `fix: bug` ❌

### Pull Request Titles

- **Match commit convention**: `feat: add dispute resolution system` ✅
- **Include context**: `fix(payment): handle network failures gracefully` ✅

### PR Descriptions

```markdown
## What

Brief description of changes

## Why

Reason for the change

## How

Technical approach

## Testing

How it was tested

## Screenshots (if UI)

Before/after images
```

---

## 🔒 Branch Protection Rules

### `main` Branch

- ✅ Require pull request reviews (1 approval)
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Require linear history
- ✅ Do not allow force pushes
- ✅ Do not allow deletions

### `develop` Branch

- ✅ Require pull request reviews (1 approval)
- ✅ Require status checks to pass
- ✅ Do not allow force pushes
- ✅ Do not allow deletions

---

## 📊 Version Numbering (Semantic Versioning)

```
MAJOR.MINOR.PATCH

Example: 1.2.3
```

- **MAJOR**: Breaking changes (v1.0.0 → v2.0.0)
- **MINOR**: New features, backward compatible (v1.0.0 → v1.1.0)
- **PATCH**: Bug fixes, backward compatible (v1.0.0 → v1.0.1)

### Current Version

- **MVP**: `v0.1.0` (pre-release)
- **First Production**: `v1.0.0`

---

## 🎯 Roadmap Branches (Planned)

### Phase 1: Security Hardening

- `feature/hsm-integration`
- `feature/multi-sig-wallet`
- `enhancement/rate-limiting`
- `docs/security-audit`

### Phase 2: Reliability

- `feature/redis-caching`
- `enhancement/retry-logic`
- `feature/circuit-breaker`
- `perf/database-optimization`

### Phase 3: Features

- `feature/dispute-resolution`
- `feature/analytics-dashboard`
- `feature/multi-channel-management`
- `feature/scheduled-posting`

### Phase 4: Mainnet

- `feature/smart-contract-escrow`
- `feature/mainnet-wallet`
- `docs/legal-compliance`
- `feature/kyc-integration`

---

## 🚀 Initial Setup Commands

```bash
# 1. Initialize git (if not done)
cd c:\Users\NOdt\Desktop\TG-ADMC
git init

# 2. Create .gitignore (already done)
# Verify .env is excluded
git status

# 3. Create main branch
git checkout -b main

# 4. Initial commit
git add .
git commit -m "chore: initial commit - MVP complete"

# 5. Create develop branch
git checkout -b develop

# 6. Push both branches to GitHub
git remote add origin https://github.com/ssolis-ti/TG-ADMC.git
git push -u origin main
git push -u origin develop

# 7. Set develop as default branch (via GitHub settings)
```

---

## 📚 Quick Reference

### Common Commands

```bash
# Check current branch
git branch

# Switch branch
git checkout <branch-name>

# Create and switch to new branch
git checkout -b <branch-name>

# Update current branch from remote
git pull origin <branch-name>

# Push current branch to remote
git push origin <branch-name>

# Delete local branch
git branch -d <branch-name>

# Delete remote branch
git push origin --delete <branch-name>

# View commit history
git log --oneline --graph --all

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard all local changes
git reset --hard HEAD
```

---

## ✅ Checklist Before First Push

- [ ] `.gitignore` configured
- [ ] `.env` NOT in staging area
- [ ] No sensitive data in code
- [ ] README.md complete
- [ ] LICENSE file present
- [ ] All tests passing (if any)
- [ ] Documentation updated
- [ ] Commit messages follow convention

---

**Created by [@ssolis-ti](https://github.com/ssolis-ti) | [saiberaysen.cl](https://www.saiberaysen.cl)**
