<script lang="ts">
import { clientWrapper } from "$lib/api/client-wrapper";
import { IconErrorCrossCircle, IconFaceFrown } from "$lib/components/icons";
import {
	DEFAULT_MAP_CENTER,
	MAP_ATTRIBUTION,
	MAP_STYLE_URL,
} from "$lib/constants";
import {
	ACTIVE_WORK_ORDER_STATUSES,
	type WorkOrderStatus,
} from "$lib/constants/work-orders";
import type { WorkOrder, WorkOrdersResponse } from "$lib/types/work-orders";
import {
	getTablePriorityBadgeClasses,
	getTableStatusBadgeClasses,
} from "$lib/utils/badge-styles";
import { debugLog, debugLogObject } from "$lib/utils/debug";
import { createQuery } from "@tanstack/svelte-query";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

// Component state
// biome-ignore lint/style/useConst: Svelte bind:this requires let for mutability
let mapContainer = $state<HTMLDivElement | null>(null);
let map: maplibregl.Map | null = $state(null);
let isMapReady = $state(false);
let markers: maplibregl.Marker[] = [];

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

// Filter work orders that have valid coordinates
const mappableWorkOrders = $derived.by(() => {
	if (!$workOrdersQuery.isSuccess || !$workOrdersQuery.data?.data) {
		return [];
	}

	const data = $workOrdersQuery.data.data;

	// Only include work orders with coordinates
	return data.filter((wo: WorkOrder) => {
		const hasCoordinates = wo.location?.latitude && wo.location?.longitude;
		const isActive = (ACTIVE_WORK_ORDER_STATUSES as readonly string[]).includes(
			wo.status,
		);
		return isActive && hasCoordinates;
	});
});

// Simple marker colors - these are independent of DaisyUI and just need to look good on the map
function getSimpleMarkerColor(status: WorkOrderStatus): string {
	switch (status) {
		case "Open":
			return "#3b82f6"; // blue
		case "In Progress":
			return "#f59e0b"; // amber
		case "On Hold":
			return "#6b7280"; // gray
		case "Completed":
			return "#10b981"; // green
		case "Cancelled":
			return "#ef4444"; // red
		default:
			return "#3b82f6";
	}
}

// Build popup content
function buildPopupContent(workOrder: WorkOrder): string {
	const addressParts = [
		workOrder.location?.address,
		workOrder.location?.city,
		workOrder.location?.state_province,
		workOrder.location?.postal_code,
	].filter(Boolean);

	const address = addressParts.join(", ");

	// Use shared badge utility functions for consistent styling
	const statusClasses = getTableStatusBadgeClasses(workOrder.status);
	const priorityClasses = getTablePriorityBadgeClasses(workOrder.priority);

	return `
		<div class="p-2 min-w-[200px]">
			<h4 class="font-semibold text-sm mb-1">${workOrder.title}</h4>
			<p class="text-xs text-gray-600 mb-2">${address}</p>
			<div class="flex gap-2 mb-2">
				<span class="badge badge-sm ${statusClasses}">
					${workOrder.status}
				</span>
				<span class="badge badge-sm ${priorityClasses}">
					${workOrder.priority}
				</span>
			</div>
			<a href="/workorders?viewId=${workOrder.id}"
			   class="text-xs text-blue-600 hover:underline">
				View Details →
			</a>
		</div>
	`;
}

// Initialize map when container is ready
$effect(() => {
	if (!mapContainer || map) return;

	debugLog("Initializing MapLibre GL map");

	map = new maplibregl.Map({
		container: mapContainer,
		style: MAP_STYLE_URL,
		center: [DEFAULT_MAP_CENTER.lng, DEFAULT_MAP_CENTER.lat],
		zoom: 4, // Start zoomed out to see all of US
		attributionControl: false,
	});

	// Add attribution control
	map.addControl(
		new maplibregl.AttributionControl({
			customAttribution: MAP_ATTRIBUTION,
		}),
		"bottom-right",
	);

	// Add navigation controls
	map.addControl(new maplibregl.NavigationControl(), "top-right");

	// Mark map as ready when loaded
	map.on("load", () => {
		isMapReady = true;
		debugLog("Map loaded and ready");
	});

	// Add error handling
	map.on("error", (e) => {
		console.error("Map error:", e);
		debugLog(`Map error: ${e.error?.message || "Unknown error"}`);
	});

	// Log style loading
	map.on("style.load", () => {
		debugLog("Map style loaded successfully");
	});
});

// Add/update markers when data changes
$effect(() => {
	if (!map || !isMapReady || !mappableWorkOrders.length) return;

	debugLogObject("Updating map with work orders", {
		totalOrders: $workOrdersQuery.data?.data?.length || 0,
		filteredCount: mappableWorkOrders.length,
		orders: mappableWorkOrders.map((wo) => ({
			id: wo.id,
			title: wo.title,
			status: wo.status,
			hasLocation: !!wo.location,
			hasCoordinates: !!(wo.location?.latitude && wo.location?.longitude),
			lat: wo.location?.latitude,
			lng: wo.location?.longitude,
			address: wo.location?.address,
			city: wo.location?.city,
		})),
	});

	// Clear existing markers
	for (const marker of markers) {
		marker.remove();
	}
	markers = [];

	// Create bounds to fit all markers
	const bounds = new maplibregl.LngLatBounds();

	// Add markers for each work order
	for (const workOrder of mappableWorkOrders) {
		if (!workOrder.location?.latitude || !workOrder.location?.longitude)
			continue;

		const lng = workOrder.location.longitude;
		const lat = workOrder.location.latitude;

		// Create simple solid circle marker - these don't need to match DaisyUI
		const el = document.createElement("div");
		el.style.width = "30px";
		el.style.height = "30px";
		el.style.backgroundColor = getSimpleMarkerColor(workOrder.status);
		el.style.borderRadius = "50%";
		el.style.border = "3px solid white";
		el.style.boxShadow = "0 2px 4px rgba(0,0,0,0.3)";
		el.style.cursor = "pointer";

		// Create marker
		const marker = new maplibregl.Marker({ element: el })
			.setLngLat([lng, lat])
			.setPopup(
				new maplibregl.Popup({ offset: 25 }).setHTML(
					buildPopupContent(workOrder),
				),
			)
			.addTo(map as maplibregl.Map);

		markers.push(marker);
		bounds.extend([lng, lat]);
	}

	// Fit map to show all markers
	if (mappableWorkOrders.length > 0) {
		map.fitBounds(bounds, {
			padding: { top: 50, bottom: 50, left: 50, right: 50 },
			maxZoom: 15,
		});
	}
});

// Cleanup on destroy
$effect(() => {
	return () => {
		if (map) {
			debugLog("Cleaning up map");
			map.remove();
			map = null;
		}
	};
});
</script>

<div class="card bg-base-100 shadow-lg">
	<div class="card-body p-0">
		<div class="p-4 border-b border-base-200">
			<h3 class="card-title text-lg">Work Orders Map</h3>
			{#if $workOrdersQuery.isSuccess}
				<p class="text-sm text-base-content/70">
					Showing {mappableWorkOrders.length} active work order{mappableWorkOrders.length !== 1 ? 's' : ''} with location data
				</p>
			{/if}
		</div>

		<div class="relative">
			{#if $workOrdersQuery.isLoading}
				<div class="absolute inset-0 z-10 bg-base-100 flex items-center justify-center">
					<div class="text-center">
						<span class="loading loading-spinner loading-lg"></span>
						<p class="mt-2 text-sm text-base-content/70">Loading map...</p>
					</div>
				</div>
			{:else if $workOrdersQuery.isError}
				<div class="p-8 text-center">
					<IconErrorCrossCircle class="w-12 h-12 mx-auto text-error mb-4" />
					<p class="text-error">Failed to load work orders</p>
					<p class="text-sm text-base-content/70 mt-1">Please try refreshing the page</p>
				</div>
			{:else if mappableWorkOrders.length === 0}
				<div class="p-8 text-center">
					<IconFaceFrown class="w-12 h-12 mx-auto text-base-content/30 mb-4" />
					<p class="text-base-content/70">No active work orders with location data</p>
					<p class="text-sm text-base-content/50 mt-1">Work orders need coordinates to appear on the map</p>
				</div>
			{/if}

			<!-- Map container -->
			<div
				bind:this={mapContainer}
				class="w-full h-[500px]"
				class:opacity-0={$workOrdersQuery.isLoading || mappableWorkOrders.length === 0}
			></div>
		</div>
	</div>
</div>

<style>
	:global(.maplibregl-popup-content) {
		padding: 0 !important;
		border-radius: 0.5rem;
		box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
	}

	:global(.maplibregl-popup-close-button) {
		padding: 0.25rem;
		font-size: 1.25rem;
	}

</style>
