/**
 * Debug utilities for conditional logging based on environment variable
 */

// Check if DEBUG is enabled in environment
const isDebugEnabled = (): boolean => {
	if (typeof window !== "undefined") {
		// Client-side: check if DEBUG is true in any common ways
		return (
			window.location.search.includes("debug=true") ||
			localStorage.getItem("DEBUG") === "true" ||
			// @ts-ignore - Vite environment variables
			import.meta.env.VITE_DEBUG === "true"
		);
	}
	// Server-side: check Vite environment variable
	// @ts-ignore - Vite environment variables
	return import.meta.env.VITE_DEBUG === "true";
};

/**
 * Log a debug message only if DEBUG is enabled
 */
export const debugLog = (message: string): void => {
	if (isDebugEnabled()) {
		console.log(`DEBUG: ${message}`);
	}
};

/**
 * Log an object as debug message only if DEBUG is enabled
 */
export const debugLogObject = (label: string, obj: unknown): void => {
	if (isDebugEnabled()) {
		console.log(`DEBUG: ${label}:`, obj);
	}
};

/**
 * Log an error as debug message only if DEBUG is enabled
 */
export const debugLogError = (label: string, error: unknown): void => {
	if (isDebugEnabled()) {
		console.error(`DEBUG: ${label}:`, error);
	}
};

/**
 * Check if debug is currently enabled
 */
export const isDebug = (): boolean => {
	return isDebugEnabled();
};
