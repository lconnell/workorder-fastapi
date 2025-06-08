<script lang="ts">
import { clientWrapper } from "$lib/api/client-wrapper";
import StatCard from "$lib/components/StatCard.svelte";
import {
	IconArchiveBox,
	IconCheckCircle,
	IconClock,
	IconErrorCrossCircle,
	IconLightningBolt,
} from "$lib/components/icons";
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
	<div class="px-2 py-4 sm:px-4 lg:px-6 max-w-none flex flex-col flex-grow min-h-screen">
		<!-- Dashboard Header -->
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
				<IconErrorCrossCircle class="stroke-current shrink-0" />
				<span>Failed to load work orders. Please try again.</span>
			</div>
		{:else}
			<!-- Statistics Cards -->
			<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8 w-full">
				<StatCard
					title="Open"
					value={stats.open}
					iconComponent={IconLightningBolt}
					link="/workorders?status=Open"
					colorClass="text-primary"
				/>
				<StatCard
					title="In Progress"
					value={stats.inProgress}
					iconComponent={IconClock}
					link="/workorders?status=In Progress"
					colorClass="text-warning"
				/>
				<StatCard
					title="Completed"
					value={stats.completed}
					iconComponent={IconCheckCircle}
					link="/workorders?status=Completed"
					colorClass="text-success"
					subtitle="this month"
				/>
				<StatCard
					title="Total Orders"
					value={stats.total}
					iconComponent={IconArchiveBox}
					link="/workorders"
					colorClass="text-info"
					subtitle="all time"
				/>
			</div>

			<!-- Map Section -->
			<div class="card bg-base-100 shadow-sm w-full flex-grow flex flex-col rounded-lg">
				<div class="card-body flex-grow flex flex-col p-0 sm:p-4 md:p-6">
					<WorkOrdersMap />
				</div>
			</div>
		{/if}
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
		<div class="card w-96 bg-base-100 shadow-xl rounded-lg">
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
