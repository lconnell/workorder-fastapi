# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack work order management system with:
- **Backend**: FastAPI REST API using Supabase for database and authentication
- **Frontend**: SvelteKit application with TypeScript, Tailwind CSS, and TanStack Query

The system manages work orders with secure user authentication and role-based access control.

## Code Quality & Architecture

### ⭐ Core Design Philosophy
**PARAMOUNT PRINCIPLES - MUST BE FOLLOWED AT ALL TIMES:**

- **Best Practices & Standards**: Always use web standards, semantic HTML, proper accessibility (ARIA, WCAG)
- **Clean Design**: Professional, consistent visual hierarchy with cohesive color schemes and proper spacing
- **DRY Principles**: Shared utilities, reusable components, centralized logic - never duplicate code
- **Progressive Web App**: Mobile-first responsive design optimized for web and mobile usage
- **Accessibility First**: Screen readers, keyboard navigation, proper form labels and validation
- **Consistent Architecture**: Well-structured, maintainable codebase that simplifies management

**Design Quality Standards:**
- Use DaisyUI semantic color variables (`hsl(var(--p))` for primary, etc.)
- Eliminate visual inconsistencies (double outlines, mismatched colors, etc.)
- Maintain unified component patterns across the application
- Follow established badge systems, error handling, and state management patterns
- Ensure all interactions provide clear, immediate feedback

**Development Excellence:**
- TypeScript safety with proper interfaces and type checking
- Proper error handling with user-friendly toast notifications
- Form validation using web standards with DaisyUI validator classes
- Performance optimization through TanStack Query caching
- Clean, readable code with consistent formatting and naming

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
- **Toast Notifications**: Use `/frontend/src/lib/stores/toastStore.svelte.ts` for user feedback
  - `toastStore.success()` for successful operations
  - `toastStore.error()` for error messages
  - `toastStore.warning()` and `toastStore.info()` for other notifications
  - Never use browser `alert()` - always use toast system

### Development Principles
- **DRY Principle**: Always check for existing utilities before creating new ones
- **Type Safety**: Use shared TypeScript interfaces from `/frontend/src/lib/types/`
- **DaisyUI First**: When writing frontend code (HTML/Svelte) that uses Tailwind CSS, always prefer using DaisyUI components for UI elements (e.g., buttons, modals, forms, alerts) instead of custom Tailwind classes—unless a DaisyUI component does not meet the functional or stylistic requirements. Custom Tailwind utility classes should only be used for layout, spacing, or when extending DaisyUI components with minimal overrides. The goal is to maintain consistent design and reduce custom styling overhead.
- **Consistent Styling**: Use established badge colors and spacing patterns via DaisyUI semantic classes
- **Error Handling**: Follow standardized error response patterns in backend
- **Performance**: Use TanStack Query for caching and invalidation
- **UI Consistency**: Maintain professional color schemes through DaisyUI theming
- **Form Validation**: Always use DaisyUI validator classes with web standards
  - Add `validator` class to inputs that require validation
  - Include `validator-hint` paragraphs for user guidance
  - Use HTML5 attributes: `required`, `pattern`, `minlength`, `maxlength`, `title`
  - Provide clear, helpful error messages
  - **ALL fields are required for new work orders** (title, status, priority, location)
- **Focus States**: Custom focus styling in `app.css` using DaisyUI color variables
  - Single blue outline using `hsl(var(--p))` (primary color)
  - No double outlines or default browser styling

### Workflow Principles
- **ALWAYS use Taskfile.yml commands** - Never run ad-hoc npm, uv, or python commands directly
  - Use `task --list` to see available commands
  - All commands are configured to run in the correct directories with proper settings
  - This prevents issues like cache directories being created in wrong locations
- Use Taskfile.yml for executing commands, especially for validating code
- Update CLAUDE.md and README.md when changes are relevant
- Use provided API testing tasks to validate backend-frontend communication
- Use tanstack svelte-query for all backend queries from frontend
- Do not use timers in the frontend, use events
- Use daisyui for rendering components in the frontend:
  - Tables use DaisyUI's `table` class with `table-pin-rows` for sticky headers
  - Modals use native HTML `<dialog>` element with DaisyUI modal styling
  - Filters use DaisyUI drawer component (right-side drawer)
  - Navigation uses DaisyUI navbar with responsive dropdowns
  - User avatar in navbar uses DaisyUI avatar component
  - All buttons use DaisyUI button classes (`btn`, `btn-primary`, etc.)
  - Forms use DaisyUI form controls and inputs
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

### Important: Command Execution Policy
**ALWAYS use Task commands from Taskfile.yml instead of running commands directly:**
- ❌ NEVER: `npm run lint`, `uv run mypy`, `cd frontend && npm install`
- ✅ ALWAYS: `task frontend-lint`, `task backend-mypy`, `task frontend-install`

This ensures:
- Commands run in the correct directories
- Cache files are created in the right locations
- Consistent environment across all operations
- Proper dependency management

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

## Recent Frontend Refactoring Summary
This section summarizes recent frontend refactoring work completed (as of current interaction, assuming June 2024).

**Objective:**
To enhance the SvelteKit frontend by improving code quality, increasing modularity, standardizing component patterns, and ensuring optimal use of DaisyUI, while adhering to existing global style configurations.

**Key Changes Implemented:**

*   **Centralized Icon System:**
    *   All inline SVG icons were removed from components and pages.
    *   A comprehensive set of reusable SVG icon components was created in `frontend/src/lib/components/icons/`.
    *   An `index.ts` file was added for easy importing of these icons.

*   **Component & Page Enhancements:**
    *   `WorkOrderModal.svelte`: Modal control logic was refactored using Svelte's `bind:this`. Form validation display was standardized to use the existing `was-validated` CSS class pattern.
    *   `Auth.svelte` & `auth/reset-password/+page.svelte`: Form validation display was made consistent with `WorkOrderModal.svelte`, utilizing the `was-validated` CSS pattern. Reactive clearing of validation states on mode change was implemented in `Auth.svelte`. Console logs were removed from `reset-password`.
    *   `StatCard.svelte`: A new reusable component was created for displaying statistics on the dashboard (`frontend/src/routes/+page.svelte`), promoting DRY principles.
    *   `Toast.svelte`: Refactored to use dynamic Svelte components (`<svelte:component>`) for displaying different icons based on toast type.
    *   `WorkOrdersMap.svelte`: Enhanced with a loading indicator during map initialization and geocoding phases. Debug console logs were cleaned up.
    *   General Cleanup: Various components (`FilterDrawer.svelte`, `profile/+page.svelte`, `workorders/+page.svelte`) were updated to use the new icon system.

*   **Configuration Integrity:**
    *   Per user directive, no modifications were made to `tailwind.config.ts`, `app.css`, or the global DaisyUI/Tailwind setup. All refactoring focused on Svelte component code and local styling within components where necessary.

**Outcome:**
The frontend codebase is now more modular, with a clear separation of concerns for UI elements like icons. Code duplication has been reduced, and maintainability is improved. The user experience was enhanced in some areas (e.g., map loading).
