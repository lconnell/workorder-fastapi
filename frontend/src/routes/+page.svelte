<script lang="ts">
import { clientWrapper } from "$lib/api/client-wrapper";
import WorkOrdersMap from "$lib/components/maps/WorkOrdersMap.svelte";
import { authStore } from "$lib/stores/authStore.svelte";
import type { WorkOrdersResponse } from "$lib/types/work-orders";
import { createQuery } from "@tanstack/svelte-query";

// Fetch work orders statistics
const workOrdersQuery = createQuery({
	queryKey: ["workOrders"],
	queryFn: async () => {
		return await clientWrapper<WorkOrdersResponse>({
			method: "GET",
			url: "/api/v1/work-orders",
		});
	},
	enabled: authStore.isAuthenticated,
});

// Calculate statistics
let stats = $state({
	open: 0,
	inProgress: 0,
	completed: 0,
	onHold: 0,
	total: 0,
});

$effect(() => {
	if (!$workOrdersQuery.data?.data) {
		stats = { open: 0, inProgress: 0, completed: 0, onHold: 0, total: 0 };
		return;
	}

	const data = $workOrdersQuery.data.data;
	stats = {
		open: data.filter((wo) => wo.status === "Open").length,
		inProgress: data.filter((wo) => wo.status === "In Progress").length,
		completed: data.filter((wo) => wo.status === "Completed").length,
		onHold: data.filter((wo) => wo.status === "On Hold").length,
		total: data.length,
	};
});
</script>

{#if authStore.isAuthenticated && authStore.user}
	<div class="min-h-screen bg-base-100">
		<!-- Dashboard Header -->
		<div class="px-2 py-4 sm:px-4 lg:px-6 max-w-none">
			<div class="mb-8">
				<h1 class="text-3xl font-bold text-base-content">Dashboard</h1>
				<p class="mt-2 text-base-content/70">Monitor and manage work orders across all locations</p>
			</div>

			{#if $workOrdersQuery.isLoading}
				<div class="flex justify-center py-12">
					<span class="loading loading-spinner loading-lg"></span>
				</div>
			{:else if $workOrdersQuery.error}
				<div class="alert alert-error">
					<svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<span>Failed to load work orders. Please try again.</span>
				</div>
			{:else}
				<!-- Statistics Cards -->
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8 w-full">
					<a href="/workorders" class="stat bg-base-200 rounded-xl shadow hover:shadow-lg transition-shadow cursor-pointer">
						<div class="stat-figure text-primary">
							<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-8 h-8 stroke-current">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
							</svg>
						</div>
						<div class="stat-title">Open</div>
						<div class="stat-value text-primary">{stats.open}</div>
						<div class="stat-desc">Awaiting action</div>
					</a>

					<a href="/workorders" class="stat bg-base-200 rounded-xl shadow hover:shadow-lg transition-shadow cursor-pointer">
						<div class="stat-figure text-warning">
							<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-8 h-8 stroke-current">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
							</svg>
						</div>
						<div class="stat-title">In Progress</div>
						<div class="stat-value text-warning">{stats.inProgress}</div>
						<div class="stat-desc">Currently working</div>
					</a>

					<a href="/workorders" class="stat bg-base-200 rounded-xl shadow hover:shadow-lg transition-shadow cursor-pointer">
						<div class="stat-figure text-success">
							<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-8 h-8 stroke-current">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
							</svg>
						</div>
						<div class="stat-title">Completed</div>
						<div class="stat-value text-success">{stats.completed}</div>
						<div class="stat-desc">This month</div>
					</a>

					<a href="/workorders" class="stat bg-base-200 rounded-xl shadow hover:shadow-lg transition-shadow cursor-pointer">
						<div class="stat-figure text-info">
							<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-8 h-8 stroke-current">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path>
							</svg>
						</div>
						<div class="stat-title">Total Orders</div>
						<div class="stat-value text-info">{stats.total}</div>
						<div class="stat-desc">All time</div>
					</a>
				</div>

				<!-- Map Section -->
				<div class="card bg-base-100 shadow-xl w-full">
					<div class="card-body">
						<WorkOrdersMap />
					</div>
				</div>
			{/if}
		</div>
	</div>
{:else if authStore.loading}
	<div class="min-h-screen flex items-center justify-center">
		<div class="text-center">
			<span class="loading loading-spinner loading-lg"></span>
			<p class="mt-4 text-lg">Loading dashboard...</p>
		</div>
	</div>
{:else}
	<div class="min-h-screen flex items-center justify-center bg-base-200">
		<div class="card w-96 bg-base-100 shadow-xl">
			<div class="card-body text-center">
				<h2 class="card-title justify-center text-2xl mb-4">Welcome to Work Order Management</h2>
				<p class="mb-6">Please sign in to access your dashboard</p>
				<a href="/login" class="btn btn-primary btn-lg">
					Sign In
				</a>
			</div>
		</div>
	</div>
{/if}
