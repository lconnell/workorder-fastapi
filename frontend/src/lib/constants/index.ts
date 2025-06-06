// Geocoding constants
export const GEOCODING_DELAY = 100; // ms between geocoding requests (Nominatim rate limit)
export const MAX_GEOCODING_ATTEMPTS = 3;
export const GEOCODING_CACHE_TTL = 1000 * 60 * 60 * 24; // 24 hours

// Map constants
export const DEFAULT_MAP_ZOOM = 13;
export const DEFAULT_MAP_CENTER = { lat: 40.7128, lon: -74.006 }; // New York
export const MAP_TILE_URL =
	"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
export const MAP_ATTRIBUTION = "© OpenStreetMap contributors";

// Work order status colors
export const STATUS_COLORS = {
	open: "info",
	"in progress": "warning",
	completed: "success",
	cancelled: "error",
	"on hold": "warning",
} as const;

// Priority colors
export const PRIORITY_COLORS = {
	Low: "info",
	Medium: "warning",
	High: "error",
} as const;

// API endpoints
export const API_ENDPOINTS = {
	WORK_ORDERS: "/api/v1/work-orders",
	LOCATIONS: "/api/v1/locations",
	PROFILES: "/api/v1/profiles",
	AUTH: "/api/v1/auth",
} as const;
