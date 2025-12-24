# AGENTS.md - Jobs for Aspies Project

## Build/Test Commands
- **Backend (Django)**: `cd backend && python manage.py test` (runs all tests)
- **Backend single test**: `cd backend && python manage.py test api.tests.AuthTests.test_register_user`
- **Frontend build**: `cd frontend && npm run build`
- **Frontend dev**: `cd frontend && npm run dev`
- **No linting tools configured** - ensure code follows style guidelines below

## Code Style Guidelines

### Python (Django Backend)
- **Imports**: Standard library first, then Django, then third-party, then local imports
- **Models**: Use `models.CharField(choices=CHOICES)` for enums, `db_index=True` for frequently queried fields
- **Naming**: PascalCase for classes, snake_case for variables/functions, ALL_CAPS for constants
- **Error handling**: Use Django's `ValidationError` for model validation, proper HTTP status codes in views
- **Types**: No explicit type hints, rely on Django's dynamic typing

### JavaScript/TypeScript (Astro + Vue Frontend)
- **Imports**: Group by type (Astro components, Vue, utilities), use relative paths for local imports
- **Naming**: PascalCase for components, camelCase for variables/functions, kebab-case for file names
- **Formatting**: 2-space indentation, single quotes for strings, semicolons required
- **Types**: Strict TypeScript configuration, use type assertions when necessary
- **Error handling**: Standard try/catch, proper error boundaries in Vue components

### General
- **Comments**: Use docstrings for functions/classes, inline comments for complex logic only
- **Security**: Never log secrets, validate all inputs, use HTTPS URLs for external links
- **Testing**: Write comprehensive unit tests, use mocking for external dependencies (Stripe, etc.)
- **File structure**: Follow existing patterns - models in models.py, views in views.py, components in components/