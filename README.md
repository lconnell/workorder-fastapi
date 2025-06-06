# Work Order Management System

A full-stack work order management system with FastAPI backend and modern frontend.

## Features

- **Authentication**: User registration, login, and JWT-based authentication via Supabase
- **Work Order Management**: Create, read, update, and delete work orders
- **User Profiles**: Linked to Supabase auth system
- **Location Management**: Track work order locations
- **Parts Inventory**: Manage parts used in work orders
- **Notes System**: Add notes to work orders

## Architecture

This repository contains both backend and frontend code:

- **`backend/`**: FastAPI REST API with Supabase integration
- **`frontend/`**: SvelteKit frontend application with TypeScript

## Tech Stack

### Backend
- **API**: FastAPI (Python 3.12+)
- **Database**: PostgreSQL via Supabase
- **Authentication**: Supabase Auth
- **Package Management**: uv
- **Testing**: pytest
- **Code Quality**: black, ruff, mypy, pre-commit

### Frontend
- **Framework**: SvelteKit with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with DaisyUI components
- **HTTP Client**: Axios with automatic token management
- **State Management**: Svelte stores and TanStack Query
- **Code Quality**: Biome (formatting & linting)
- **API Integration**: Orval for TypeScript client generation

## Database Schema

The Supabase project includes the following tables:
- `profiles`: User profile information
- `work_orders`: Main work order records
- `locations`: Work order locations
- `parts`: Inventory parts
- `work_order_parts`: Parts used in work orders
- `work_order_notes`: Notes on work orders

## Setup

### Quick Setup with Taskfile (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd workorder-fastapi
   ```

2. **Install Taskfile**
   ```bash
   # macOS
   brew install go-task/tap/go-task

   # Linux
   sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d

   # Windows (PowerShell)
   irm https://taskfile.dev/install.ps1 | iex
   ```

3. **Set up both backend and frontend**
   ```bash
   task setup-all
   ```

   This will automatically:
   - Install uv package manager
   - Create virtual environment in `backend/`
   - Install all Python dependencies
   - Install frontend dependencies (SvelteKit)
   - Set up pre-commit hooks
   - Create .env files from templates

### Manual Setup

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Install uv package manager**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # or
   brew install uv
   ```

3. **Create virtual environment and install dependencies**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

5. **Install pre-commit hooks**
   ```bash
   cd .. # Back to root
   uv run pre-commit install --config .pre-commit-config.yaml
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials and API URL
   ```

## Running the Application

### With Taskfile
```bash
# Backend only
task backend-dev  # Run backend development server
task dev          # Alias for backend-dev

# Frontend only
task frontend-dev # Run SvelteKit development server

# Full stack
task start-all    # Run both backend and frontend

# Generate TypeScript API client
task frontend-openapi-generate  # Generate types from running backend
task openapi-generate           # Alias for frontend-openapi-generate
```

### Without Taskfile
```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

The backend API will be available at `http://localhost:8000`
The frontend will be available at `http://localhost:5173`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication Endpoints

- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/signin` - Sign in user
- `POST /api/v1/auth/signout` - Sign out user
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/refresh` - Refresh access token

## Testing

### Backend Testing
```bash
# With Taskfile
task backend-test         # Run all backend tests
task test                 # Alias for backend-test
task backend-test-verbose # Verbose output
task backend-test-cov     # With coverage report
task backend-test-watch   # Watch mode (auto-rerun on changes)

# Without Taskfile
cd backend
uv run pytest
uv run pytest -v  # Verbose output
uv run pytest --cov  # With coverage
```

### Frontend Testing
```bash
# With Taskfile
task frontend-check # Run SvelteKit type checking
task frontend-lint  # Run Biome linting

# Without Taskfile
cd frontend
npm run check       # Type checking
npm run lint        # Linting
```

## Development

### Code Quality with Taskfile

```bash
task backend-lint       # Run all backend linters and formatters
task lint               # Alias for backend-lint
task backend-pre-commit # Run pre-commit on all files
task backend-check      # Run backend tests and linting
```

Individual tools:
```bash
task backend-format     # Format code with black
task backend-ruff       # Lint code
task backend-ruff-fix   # Lint and auto-fix
task backend-mypy       # Type checking
```

### Manual Commands

```bash
uv run pre-commit run --all-files
uv run black .         # Format code
uv run ruff check .    # Lint code
uv run mypy .          # Type checking
```

### Utility Tasks

```bash
task backend-clean       # Clean backend caches and generated files
task frontend-clean      # Clean frontend caches and build files
task backend-update-deps # Update all backend dependencies
task backend-shell       # Open Python REPL with app context
task backend-docs        # Open API docs in browser
```

### Full-Stack Tasks

```bash
task setup-all           # Set up both backend and frontend
task start-all           # Run both backend and frontend
task start-test          # Start servers and test integration
task check-all           # Run all checks for both backend and frontend
task ci-all              # Run full CI pipeline for both backend and frontend
task commit              # Create commit with full pre-commit checks
task commit-quick        # Create commit with minimal checks (faster)
task stop-servers        # Stop all development servers
```

### API Testing Tasks

```bash
task backend-ping        # Quick check if backend is running
task frontend-ping       # Quick check if frontend is running
task ping-all            # Check both servers
task backend-test-api    # Test backend API endpoints
task backend-test-auth   # Test authentication endpoints
task test-integration   # Test backend-frontend integration
```

### Project Structure

```
workorder-fastapi/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints (auth.py, work_orders.py)
│   │   ├── core/         # Core configuration (config.py)
│   │   ├── models/       # Pydantic models (auth.py, work_orders.py)
│   │   ├── services/     # Business logic (auth.py, supabase.py)
│   │   └── main.py       # FastAPI application entry point
│   ├── tests/            # Test files
│   ├── pyproject.toml    # Python dependencies and project configuration
│   └── Dockerfile        # Backend container configuration
├── frontend/             # SvelteKit frontend
│   ├── src/
│   │   ├── lib/          # Shared utilities and components
│   │   │   ├── api/      # Generated API client and types
│   │   │   ├── components/ # Reusable Svelte components
│   │   │   ├── stores/   # Svelte stores for state management
│   │   │   └── services/ # Frontend services (geocoding, etc.)
│   │   └── routes/       # SvelteKit pages and layouts
│   ├── package.json      # Frontend dependencies
│   └── svelte.config.js  # SvelteKit configuration
├── database/             # Database schema and sample data
│   ├── create_tables.sql # Database table definitions
│   └── sample_data.sql   # Sample data for development
├── Taskfile.yml          # Task automation configuration
└── .pre-commit-config.yaml  # Pre-commit hooks
```

## Security

- Never commit `.env` or `.mcp.json` files
- Use environment variables for all sensitive data
- Pre-commit hooks prevent accidental commits of sensitive files
- JWT tokens expire after 30 minutes by default

## CI/CD

- **Dependabot**: Automated dependency updates
- **Pre-commit**: Code quality checks on every commit

## License

[Add your license here]
