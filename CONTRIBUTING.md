# Contributing to ResuMariner

## Development Setup

### Backend Development

The backend uses pre-commit hooks to ensure code quality. All linting and type checking is configured in `/backend/pyproject.toml`.

#### Installing Pre-commit Hooks

From the **backend directory**:

```bash
cd backend
uv run pre-commit install
```

This will install git hooks that run automatically before each commit.

#### Running Pre-commit Manually

To run all checks on all files:

```bash
cd backend
uv run pre-commit run --all-files
```

To run checks on staged files only:

```bash
cd backend
uv run pre-commit run
```

#### Individual Tool Commands

You can also run the tools individually:

**Ruff (linting and auto-fix):**
```bash
cd backend
uv run ruff check --fix .
```

**Ruff (formatting):**
```bash
cd backend
uv run ruff format .
```

**MyPy (type checking):**
```bash
cd backend
uv run mypy . --config-file pyproject.toml
```

## Code Quality Standards

### Python Backend

- **Linting**: Ruff with the configuration in `backend/pyproject.toml`
  - Line length: 120 characters
  - Target: Python 3.12
  - Selected rules: E (pycodestyle errors), W (warnings), F (pyflakes), I (isort), B (bugbear), C4 (comprehensions), UP (pyupgrade)

- **Formatting**: Ruff formatter
  - Double quotes
  - Space indentation
  - Auto-formatting before commit

- **Type Checking**: MyPy with strict settings
  - Check untyped definitions enabled
  - Warn on unused configs
  - Test files excluded from strict checking

### Pre-commit Hook Configuration

The backend uses a `.pre-commit-config.yaml` file with three hooks:

1. **ruff-check**: Runs linting and auto-fixes issues
2. **ruff-format**: Formats code according to style guide
3. **mypy**: Type checks all Python code

All hooks use `uv run` to ensure they run in the correct virtual environment.

### Important Notes

- Pre-commit hooks are configured in `/backend/.pre-commit-config.yaml`
- Always run commands from the `/backend` directory
- The hooks use `pass_filenames: false` to run on all files in the backend directory
- `fail_fast: false` means all hooks will run even if one fails

## Testing

Run tests with pytest:

```bash
cd backend
uv run pytest
```

Run tests for a specific app:

```bash
cd backend
uv run pytest core/
uv run pytest processor/
uv run pytest storage/
uv run pytest search/
```

## Docker Development

Build and run the full stack:

```bash
docker compose up -d
```

Rebuild specific services:

```bash
docker compose build backend backend-worker-processing backend-worker-cleanup
docker compose up -d backend backend-worker-processing backend-worker-cleanup
```

Force rebuild without cache:

```bash
docker compose build --no-cache backend backend-worker-processing backend-worker-cleanup
```

## Common Workflows

### Making Changes to Backend Code

1. Make your changes
2. Run pre-commit hooks: `cd backend && uv run pre-commit run --all-files`
3. Fix any issues reported
4. Commit your changes (hooks will run automatically)
5. If hooks fail, fix issues and commit again

### Adding New Dependencies

1. Edit `backend/pyproject.toml`
2. Run `cd backend && uv lock` to update lockfile
3. Rebuild Docker containers
4. Test the changes

### Before Opening a Pull Request

1. Ensure all pre-commit hooks pass: `cd backend && uv run pre-commit run --all-files`
2. Run the full test suite: `cd backend && uv run pytest`
3. Test the application with Docker: `docker compose up -d`
4. Verify all services are healthy: `docker compose ps`
