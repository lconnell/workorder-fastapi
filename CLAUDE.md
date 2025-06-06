# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack work order management system with:
- **Backend**: FastAPI REST API using Supabase for database and authentication
- **Frontend**: SvelteKit application with TypeScript, Tailwind CSS, and TanStack Query

The system manages work orders with secure user authentication and role-based access control.

## Development Guidance

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
├── database/             # Database schema and sample data
│   ├── create_tables.sql # Database table definitions
│   └── sample_data.sql   # Sample data for development
└── Taskfile.yml          # Task automation configuration
```
