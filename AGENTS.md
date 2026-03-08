# iCross Project - Agent Guidelines

This document provides guidelines for AI agents working on the iCross project. It includes build/lint/test commands and code style conventions.

## Project Overview

iCross is a cross-border e-commerce intelligent business operating system built with microservices architecture. The tech stack includes:

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, Celery, Redis, PostgreSQL
- **Frontend**: React 18, TypeScript, Vite, Ant Design, Zustand
- **AI/ML**: LangChain, OpenAI/Claude, Stable Diffusion, Weaviate vector DB
- **Infrastructure**: Docker, Kubernetes, Traefik, Prometheus, GitHub Actions

## Build, Lint, and Test Commands

### Backend (Python)

#### Installation
```bash
pip install -e ".[dev]"          # Install dependencies with dev extras
poetry install --with dev        # Or using poetry
```

#### Development Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Linting and Formatting
```bash
black .                          # Format code
isort .                          # Sort imports
ruff check . --fix               # Lint and auto-fix
mypy .                           # Type checking
```

#### Testing
```bash
pytest                           # Run all tests
pytest tests/test_user_service.py               # Run specific test file
pytest tests/test_user_service.py::test_create_user -xvs  # Run single test
pytest --cov=app --cov-report=html             # Coverage
pytest -m integration                          # Integration tests
```

#### Database Migrations
```bash
alembic revision --autogenerate -m "description"  # Generate migration
alembic upgrade head                              # Apply migrations
alembic downgrade -1                              # Rollback
```

#### Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```

### Frontend (React/TypeScript)

#### Installation
```bash
npm install   # or yarn install / pnpm install
```

#### Development Server
```bash
npm run dev   # or yarn dev
```

#### Linting and Formatting
```bash
npm run lint        # Lint with ESLint
npm run lint:fix    # Fix lint issues
npm run format      # Format with Prettier
npm run type-check  # Type checking
```

#### Testing
```bash
npm test                         # Run all tests
npm run test:watch               # Watch mode
npm test -- tests/component.test.tsx   # Single test file
npm run test:coverage            # Coverage
```

#### Build
```bash
npm run build      # Production build
npm run preview    # Preview build
```

## Code Style Guidelines

### Python

**Imports**: Group imports: stdlib, third‑party, local modules. Use absolute imports. Avoid wildcard imports.

**Formatting**: Black (88‑char line length), double quotes, trailing commas.

**Type Annotations**: Always use type hints. Use `Optional[X]`, `List[X]`, `Dict[K, V]`, etc.

**Naming**: `CamelCase` classes, `snake_case` functions/variables, `UPPER_SNAKE_CASE` constants.

**Error Handling**: Raise `HTTPException` in route handlers, use custom exceptions in business logic, log with context.

**FastAPI**: Use dependency injection, Pydantic models for validation, async/await for I/O, document endpoints with OpenAPI tags.

**SQLAlchemy**: Use declarative base from `app.core.database`, define `__tablename__`, use `mapped_column`, proper relationships.

### TypeScript/React

**Imports**: Group React, third‑party, internal, styles. Use absolute imports (`@/components/`). Prefer named exports.

**TypeScript**: Strict mode, define interfaces for props/state/API responses, avoid `any`.

**Naming**: `PascalCase` components, `camelCase` functions/variables, `UPPER_SNAKE_CASE` exported constants.

**Components**: Functional components with hooks, single responsibility, extract logic to custom hooks, memoize appropriately.

**State Management**: Zustand for global state, TanStack Query for server state.

**Styling**: CSS‑in‑JS or CSS Modules, follow Ant Design design system.

### General Guidelines

- **Error Handling**: Graceful user‑facing messages, log with severity, validate on client/server.
- **Testing**: Unit tests for business logic, integration tests for APIs, mock external dependencies, aim >80% coverage.
- **Documentation**: Document public APIs, complex logic, keep docstrings updated.
- **Security**: Never commit secrets, use environment variables, sanitize inputs, least privilege.
- **Performance**: Optimize DB queries (indexes, avoid N+1), pagination, caching, lazy loading.

## Cursor/Copilot Rules

No project‑specific Cursor or Copilot rules found. Follow the above guidelines.

## Commit Guidelines

- Use conventional commits: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`.
- Keep commits atomic.
- Explain the “why” in commit messages.

## Additional Notes

- Documentation may be in Chinese, but code must be in English (variables, comments, etc.).
- Follow existing patterns when adding new code.
- Consult architecture docs in `docs/` when in doubt.
