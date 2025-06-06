import {
	GEOCODING_CACHE_TTL,
	GEOCODING_DELAY,
	MAX_GEOCODING_ATTEMPTS,
} from "$lib/constants";
import type { GeocodingResult } from "$lib/types/work-orders";

interface CachedResult {
	result: GeocodingResult | null;
	timestamp: number;
}

export class GeocodingService {
	private static instance: GeocodingService;
	private cache = new Map<string, CachedResult>();

	static getInstance(): GeocodingService {
		if (!GeocodingService.instance) {
			GeocodingService.instance = new GeocodingService();
		}
		return GeocodingService.instance;
	}

	private constructor() {}

	async geocodeAddress(
		address: string,
		attempt = 1,
	): Promise<GeocodingResult | null> {
		// Check cache first
		const cached = this.cache.get(address);
		if (cached && Date.now() - cached.timestamp < GEOCODING_CACHE_TTL) {
			return cached.result;
		}

		try {
			const response = await fetch(
				`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`,
				{
					headers: {
						"User-Agent": "WorkOrderManagementApp/1.0",
					},
				},
			);

			if (!response.ok) {
				throw new Error(`Geocoding failed: ${response.statusText}`);
			}

			const results = await response.json();

			let result: GeocodingResult | null = null;
			if (results.length > 0) {
				result = {
					lat: Number.parseFloat(results[0].lat),
					lon: Number.parseFloat(results[0].lon),
				};
			}

			// Cache the result
			this.cache.set(address, {
				result,
				timestamp: Date.now(),
			});

			return result;
		} catch (error) {
			console.error(`Geocoding error for "${address}":`, error);

			// Retry with exponential backoff
			if (attempt < MAX_GEOCODING_ATTEMPTS) {
				const delay = GEOCODING_DELAY * 2 ** (attempt - 1);
				await new Promise((resolve) => setTimeout(resolve, delay));
				return this.geocodeAddress(address, attempt + 1);
			}

			// Cache the failure to avoid repeated attempts
			this.cache.set(address, {
				result: null,
				timestamp: Date.now(),
			});

			return null;
		}
	}

	async geocodeMultiple(
		addresses: string[],
	): Promise<Map<string, GeocodingResult | null>> {
		const results = new Map<string, GeocodingResult | null>();
		const uniqueAddresses = [...new Set(addresses)];

		for (const address of uniqueAddresses) {
			const result = await this.geocodeAddress(address);
			results.set(address, result);

			// Respect rate limits (except for cached results)
			const cacheEntry = this.cache.get(address);
			if (
				!this.cache.has(address) ||
				(cacheEntry && Date.now() - cacheEntry.timestamp >= GEOCODING_CACHE_TTL)
			) {
				await new Promise((resolve) => setTimeout(resolve, GEOCODING_DELAY));
			}
		}

		return results;
	}

	clearCache(): void {
		this.cache.clear();
	}

	removeFromCache(address: string): void {
		this.cache.delete(address);
	}
}
