# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack work order management system with:
- **Backend**: FastAPI REST API using Supabase for database and authentication
- **Frontend**: SvelteKit application with TypeScript, Tailwind CSS, and TanStack Query

The system manages work orders with secure user authentication and role-based access control.

## Code Quality & Architecture

### Shared Utilities (Follow DRY Principles)
- **Badge Styling**: Use `/frontend/src/lib/utils/badge-styles.ts` for consistent badge colors
  - `getModalStatusBadgeClasses()` and `getModalPriorityBadgeClasses()` for modal views
  - `getTableStatusBadgeClasses()` and `getTablePriorityBadgeClasses()` for table displays
- **Date Formatting**: Use `/frontend/src/lib/utils/date-formatter.ts` for all date displays
  - `formatDate()` for short dates (e.g., "Dec 6, 2024")
  - `formatDateTime()` for full timestamps
- **Error Handling**: Use `/backend/app/utils/error_handlers.py` for standardized API errors
  - `handle_supabase_error()` for database operation errors
  - `validate_supabase_response()` for response validation
  - `create_not_found_error()` and `create_validation_error()` for common errors

### Development Principles
- **DRY Principle**: Always check for existing utilities before creating new ones
- **Type Safety**: Use shared TypeScript interfaces from `/frontend/src/lib/types/`
- **Consistent Styling**: Use established badge colors and spacing patterns
- **Error Handling**: Follow standardized error response patterns in backend
- **Performance**: Use TanStack Query for caching and invalidation
- **UI Consistency**: Maintain professional color schemes (subtle backgrounds, darker text)

### Workflow Principles
- Use Taskfile.yml for executing commands, especially for validating code
- Update CLAUDE.md and README.md when changes are relevant
- Use provided API testing tasks to validate backend-frontend communication
- Use tanstack svelte-query for all backend queries from frontend
- Do not use timers in the frontend, use events
- Use daisyui for rendering components in the frontend
- Use context7 MCP server for Svelte5, Supabase and FastAPI documentation
- Use supabase MCP server for Supabase related actions
- When writing frontend/typescript code, take into consideration that we are building a progressive web app that can be used on web and mobile

### Database Management
- All database schema changes must be done through Supabase migrations in `supabase/migrations/`
- Use `task db-migration-new -- "migration_name"` to create new migrations
- Deploy migrations with `task db-migration-push`
- Generate updated TypeScript types with `task db-types` after schema changes
- GitHub Actions automatically deploy migrations when pushed to main branch
- Use UUIDs for all primary keys (already implemented)
- Locations table includes geocoding cache (lat/lng) for performance

## Development Setup

This project uses `uv` as the package manager and Taskfile for task automation.

### Quick Setup
```bash
# Install Taskfile (if not already installed)
brew install go-task/tap/go-task  # macOS
# or see https://taskfile.dev/installation/ for other systems

# Complete project setup (backend + frontend)
task setup-all

# Run both backend and frontend
task start-all

# Test API integration
task test-integration
```

### API Testing Tasks
```bash
# Server Status
task backend-ping        # Quick check if backend is running
task frontend-ping       # Quick check if frontend is running
task ping-all            # Check both servers

# API Validation
task backend-test-api    # Test backend API endpoints
task backend-test-auth   # Test authentication endpoints
task test-integration   # Test backend-frontend integration

# Development Utilities
task start-test          # Start servers and test integration
task stop-servers        # Stop all development servers
```

### Database Migration Tasks
```bash
# Migration Management
task db-migration-new -- "migration_name"  # Create new migration
task db-migration-status                   # Check migration status
task db-migration-push                     # Deploy to production
task db-migration-reset                    # Reset local DB (dev only)

# Type Generation
task db-types            # Generate TypeScript types from database
task db-link             # Link to remote Supabase project
```

## Project Structure

The project follows this structure:
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
├── supabase/             # Supabase configuration and migrations
│   ├── migrations/       # Database migration files (UUID migration included)
│   └── config.toml       # Supabase project configuration
├── .github/              # GitHub Actions workflows
│   └── workflows/        # CI/CD pipelines including migration deployment
└── Taskfile.yml          # Task automation configuration
```
