<script lang="ts">
import { clientWrapper } from "$lib/api/client-wrapper";
import { IconErrorCrossCircle, IconFaceFrown } from "$lib/components/icons";
import { MAP_ATTRIBUTION, MAP_TILE_URL } from "$lib/constants";
import { GeocodingService } from "$lib/services/geocoding";
import type {
	GeocodedLocation,
	WorkOrder,
	WorkOrdersResponse,
} from "$lib/types/work-orders";
import { createQuery } from "@tanstack/svelte-query";
import type * as L from "leaflet";
import { onDestroy, tick } from "svelte";

// biome-ignore lint/style/useConst: Svelte 5 bind:this requires let
let mapContainer = $state<HTMLDivElement | null>(null);
let leafletMap: L.Map | null = $state(null);
let leafletLib: typeof L | null = null;
let isMapReady = $state(false);

const DEFAULT_LAT = 39.8283; // Approx US center
const DEFAULT_LON = -98.5795;
const DEFAULT_ZOOM_NO_ORDERS = 4;
const DEFAULT_ZOOM_SINGLE_ORDER = 13;

const geocodingService = GeocodingService.getInstance();

// Fetch work orders (using same key as main page to share cache)
const workOrdersQuery = createQuery({
	queryKey: ["workOrders"],
	queryFn: async () => {
		return await clientWrapper<WorkOrdersResponse>({
			method: "GET",
			url: "/api/v1/work-orders",
		});
	},
});

// Process work orders for mapping - using explicit reactive variables
let mappableWorkOrders = $state<WorkOrder[]>([]);

// Watch for query changes and update mappable work orders
$effect(() => {
	if (!$workOrdersQuery.isSuccess || !$workOrdersQuery.data?.data) {
		mappableWorkOrders = [];
		return;
	}

	const data = $workOrdersQuery.data.data;

	const filtered = data.filter((wo: WorkOrder) => {
		const hasLocation =
			wo.location && (wo.location.address || wo.location.name);
		const isActive = wo.status === "Open" || wo.status === "In Progress";
		return isActive && hasLocation;
	});

	mappableWorkOrders = filtered;
});

// Load Leaflet library
async function loadLeaflet() {
	if (leafletLib) return leafletLib;

	// Check if already loaded
	if ((window as Window & { L?: typeof import("leaflet") }).L) {
		leafletLib =
			(window as Window & { L?: typeof import("leaflet") }).L || null;
		return leafletLib;
	}

	// Load CSS if not already loaded
	if (!document.querySelector('link[href*="leaflet"]')) {
		const link = document.createElement("link");
		link.rel = "stylesheet";
		link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
		document.head.appendChild(link);
	}

	// Load JS
	await new Promise((resolve, reject) => {
		const script = document.createElement("script");
		script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
		script.onload = resolve;
		script.onerror = reject;
		document.head.appendChild(script);
	});

	leafletLib = (window as Window & { L?: typeof import("leaflet") }).L || null;
	return leafletLib;
}

// Geocode and display work orders
async function displayWorkOrders(
	currentMapContainer: HTMLDivElement,
	currentMappableOrders: WorkOrder[],
) {
	if (!currentMappableOrders.length || !currentMapContainer) {
		// Kept: This warn might indicate a logic flaw or race condition.
		console.warn(
			"displayWorkOrders called with invalid container or empty orders.",
		);
		return;
	}

	try {
		// Load Leaflet if needed
		const L = await loadLeaflet();
		if (!L) {
			console.error("Leaflet library could not be loaded."); // Kept: Critical failure.
			return;
		}

		// Check if container or data became unavailable during await
		if (!currentMapContainer || !currentMappableOrders.length) {
			// Kept: Important for debugging potential race conditions.
			console.warn(
				"Map container or work orders became unavailable (during Leaflet load). Aborting displayWorkOrders.",
			);
			return;
		}

		// Geocode unique addresses
		const uniqueAddresses = new Map<string, WorkOrder[]>();
		for (const wo of currentMappableOrders) {
			// Build address from available fields
			const addressParts = [
				wo.location?.address,
				wo.location?.city,
				wo.location?.state_province,
				wo.location?.postal_code,
			].filter(Boolean);

			const address =
				addressParts.length > 0
					? addressParts.join(", ")
					: wo.location?.name || "Unknown Location";

			if (!uniqueAddresses.has(address)) {
				uniqueAddresses.set(address, []);
			}
			uniqueAddresses.get(address)?.push(wo);
		}

		// Geocode all addresses
		const geocodedResults = await geocodingService.geocodeMultiple([
			...uniqueAddresses.keys(),
		]);

		// Check if container or data became unavailable during await
		if (!currentMapContainer || !currentMappableOrders.length) {
			// Kept: Important for debugging potential race conditions.
			console.warn(
				"Map container or work orders became unavailable (during geocoding). Aborting displayWorkOrders.",
			);
			if (leafletMap && !currentMapContainer) {
				// This console.log is more of a debug trace, could be removed, but harmless for now.
				// console.log(
				// 	"Removing stale map instance as container is gone after geocoding.",
				// );
				leafletMap.remove();
				leafletMap = null;
			}
			return;
		}

		// Build geocoded locations array
		const geocodedLocations: GeocodedLocation[] = [];
		for (const [address, workOrders] of uniqueAddresses) {
			const result = geocodedResults.get(address);
			if (result) {
				geocodedLocations.push({
					...result,
					address,
					workOrderCount: workOrders.length,
					workOrders,
				});
			}
		}

		if (geocodedLocations.length === 0) {
			console.warn("No locations could be geocoded"); // Kept: Useful info if addresses are bad.
			return;
		}

		// Clean up existing map
		if (leafletMap) {
			leafletMap.remove();
			leafletMap = null;
		}

		// Final check for map container AND work order data before initializing map
		// This is critical as reactive updates might nullify mapContainer or empty mappableWorkOrders synchronously.
		if (!currentMapContainer || !currentMappableOrders.length) {
			// Kept: Critical failure scenario.
			console.error(
				"CRITICAL: Map container or work orders became invalid just before L.map() call (parameters). Aborting map initialization.",
			);
			return;
		}
		// Initialize the map instance FIRST
		leafletMap = L.map(currentMapContainer);

		// Add tile layer
		L.tileLayer(MAP_TILE_URL, {
			attribution: MAP_ATTRIBUTION,
		}).addTo(leafletMap);

		// Filter for valid geocoded points
		const validGeocodedLocations = geocodedLocations.filter(
			(loc) => Number.isFinite(loc.lat) && Number.isFinite(loc.lon),
		);

		if (validGeocodedLocations.length === 0) {
			// Kept: Informs why map might look empty or default.
			console.warn(
				"No valid geocoded locations to display. Setting default view.",
			);
			leafletMap.setView([DEFAULT_LAT, DEFAULT_LON], DEFAULT_ZOOM_NO_ORDERS);
		} else if (validGeocodedLocations.length === 1) {
			const singleLoc = validGeocodedLocations[0];
			leafletMap.setView(
				[singleLoc.lat, singleLoc.lon],
				DEFAULT_ZOOM_SINGLE_ORDER,
			);
			// Add marker for the single valid location
			const popupContent = `
				<div class="p-2">
					<strong>${singleLoc.workOrderCount} work order${singleLoc.workOrderCount > 1 ? "s" : ""}</strong><br>
					<small>${singleLoc.address}</small>
					<ul class="mt-2 text-xs">
						${singleLoc.workOrders
							.slice(0, 3)
							.map((wo) => `<li>• ${wo.title}</li>`)
							.join("")}
						${singleLoc.workOrders.length > 3 ? `<li class="opacity-60">+${singleLoc.workOrders.length - 3} more</li>` : ""}
					</ul>
				</div>
			`;
			L.marker([singleLoc.lat, singleLoc.lon])
				.addTo(leafletMap)
				.bindPopup(popupContent);
		} else {
			// More than one valid location, fit bounds
			const bounds = L.latLngBounds(
				validGeocodedLocations.map((loc) => [loc.lat, loc.lon]),
			);
			leafletMap.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });

			// Add markers for all valid locations
			for (const loc of validGeocodedLocations) {
				const popupContent = `
					<div class="p-2">
						<strong>${loc.workOrderCount} work order${loc.workOrderCount > 1 ? "s" : ""}</strong><br>
						<small>${loc.address}</small>
						<ul class="mt-2 text-xs">
							${loc.workOrders
								.slice(0, 3)
								.map((wo) => `<li>• ${wo.title}</li>`)
								.join("")}
							${loc.workOrders.length > 3 ? `<li class="opacity-60">+${loc.workOrders.length - 3} more</li>` : ""}
						</ul>
					</div>
				`;

				L.marker([loc.lat, loc.lon]).addTo(leafletMap).bindPopup(popupContent);
			}
		} // Closes the if/else if/else for validGeocodedLocations

		// Ensure map size is correct after view operations, common to all paths
		if (leafletMap) {
			// leafletMap should be initialized if any path was successful
			await tick(); // Wait for DOM updates
			if (leafletMap) {
				// Check again, map might have been destroyed during the tick
				leafletMap.invalidateSize();
			}
		}
		isMapReady = true;
	} catch (error) {
		console.error("Failed to display work orders on map:", error);
	}
}

// Initialize map when container and data are both ready
$effect(() => {
	// Capture current reactive values for this effect run
	const currentOrders = mappableWorkOrders;
	const currentContainer = mapContainer;

	if (currentOrders.length > 0 && currentContainer) {
		// Conditions met to display or update the map
		displayWorkOrders(currentContainer, currentOrders);
	} else {
		// Conditions to display map are NOT met. If map exists, remove it.
		if (leafletMap) {
			// This console.log is more of a debug trace.
			// console.log("Conditions to display map no longer met. Removing map.");
			leafletMap.remove();
			leafletMap = null;
			isMapReady = false; // Reset map ready state
		}
	}
});

onDestroy(() => {
	if (leafletMap) {
		leafletMap.remove();
		leafletMap = null;
	}
});
</script>

<div class="w-full h-full flex flex-col flex-grow">
	{#if $workOrdersQuery.isLoading}
		<div class="flex-grow flex flex-col items-center justify-center">
			<span class="loading loading-spinner loading-lg"></span>
			<p class="text-base-content/70 mt-4">Loading map data...</p>
		</div>
	{:else if $workOrdersQuery.error}
		<div class="flex-grow flex flex-col items-center justify-center">
			<div class="alert alert-error max-w-md">
				<IconErrorCrossCircle class="stroke-current shrink-0 h-6 w-6" />
				<span>Failed to load work orders for the map.</span>
			</div>
		</div>
	{:else if mappableWorkOrders.length === 0}
		<div class="flex-grow flex flex-col items-center justify-center text-center p-4">
			<IconFaceFrown class="text-base-content/30 mb-4" />
			<p class="text-lg font-medium text-base-content/70">No Active Work Orders to Display</p>
			<p class="text-sm text-base-content/50">There are currently no open or in-progress work orders with valid locations.</p>
		</div>
	{:else}
    <!-- Map Info Bar -->
    <div class="bg-base-200/80 backdrop-blur-sm p-2 rounded-t-lg shadow text-center text-sm text-base-content/90 mb-[-1px] z-10 relative">
      Displaying <span class="font-semibold text-primary">{mappableWorkOrders.length}</span> active work order{mappableWorkOrders.length !== 1 ? 's' : ''}
      {#if isMapReady}
        {@const uniqueAddresses = new Set(mappableWorkOrders.map(wo => wo.location?.address).filter(Boolean))}
        at <span class="font-semibold text-secondary">{uniqueAddresses.size}</span> unique location{uniqueAddresses.size !== 1 ? 's' : ''}
      {/if}
    </div>
		<div class="flex-grow w-full rounded-b-xl bg-base-200 border border-base-300 relative overflow-hidden">
			<div bind:this={mapContainer} class="absolute inset-0 w-full h-full" id="work-orders-map"></div>
		</div>
	{/if}
</div>
