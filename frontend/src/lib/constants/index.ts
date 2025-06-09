// Map constants
export const DEFAULT_MAP_ZOOM = 13;
export const DEFAULT_MAP_CENTER = { lat: 39.8283, lng: -98.5795 }; // US Center
// Use basic OSM style that doesn't require external services
export const MAP_STYLE_URL = {
	version: 8 as const,
	sources: {
		"osm-tiles": {
			type: "raster" as const,
			tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
			tileSize: 256,
			attribution: "© OpenStreetMap contributors",
		},
	},
	layers: [
		{
			id: "osm-tiles",
			type: "raster" as const,
			source: "osm-tiles",
			minzoom: 0,
			maxzoom: 19,
		},
	],
};
export const MAP_ATTRIBUTION = "© OpenStreetMap contributors";

// API endpoints
export const API_ENDPOINTS = {
	WORK_ORDERS: "/api/v1/work-orders",
	LOCATIONS: "/api/v1/locations",
	PROFILES: "/api/v1/profiles",
	AUTH: "/api/v1/auth",
} as const;
