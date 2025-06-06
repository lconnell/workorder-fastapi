# Frontend - SvelteKit Application

This is the SvelteKit frontend for the Work Order Management System.

## Tech Stack

- **Framework**: SvelteKit with TypeScript
- **Styling**: Tailwind CSS with DaisyUI components
- **HTTP Client**: Axios with automatic token management
- **State Management**: Svelte stores and TanStack Query
- **API Integration**: Orval for TypeScript client generation
- **Code Quality**: Biome (formatting & linting)

## Development

### Quick Start
```bash
# From project root - start both backend and frontend
task start-all

# Or frontend only
task frontend-dev
```

### Manual Setup
```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run development server
npm run dev
```

## API Integration

The frontend automatically generates TypeScript clients from the backend's OpenAPI schema:

```bash
# Generate API client from running backend
task frontend-openapi-generate
```

## Environment Variables

Required environment variables (see `.env.example`):
- `PUBLIC_SUPABASE_URL` - Your Supabase project URL
- `PUBLIC_SUPABASE_ANON_KEY` - Your Supabase anon key
- `PUBLIC_API_BASE_URL` - Backend API URL (default: http://localhost:8000)

## Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run check        # Type checking
npm run lint         # Code linting
npm run format       # Code formatting
```

## Backend Integration

The backend API is available at `http://localhost:8000` when running locally.

Key API endpoints:
- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/auth/signin` - User login
- `GET /api/v1/auth/me` - Get current user
- Documentation: `http://localhost:8000/docs`

## Features

- ✅ Authentication flow with Supabase Auth (PKCE)
- ✅ Automatic token management and refresh
- ✅ TypeScript types generated from backend API
- ✅ Responsive design with Tailwind CSS
- ✅ Error handling and loading states
- ✅ Work order management interface (in development)

## Testing

```bash
task frontend-check  # Type checking
task frontend-lint   # Linting
```
