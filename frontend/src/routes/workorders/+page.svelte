<script lang="ts">
import { clientWrapper } from "$lib/api/client-wrapper";
import WorkOrderModal from "$lib/components/WorkOrderModal.svelte";
import { API_ENDPOINTS } from "$lib/constants";
import type { WorkOrder, WorkOrdersResponse } from "$lib/types/work-orders";
import {
	getTablePriorityBadgeClasses,
	getTableStatusBadgeClasses,
} from "$lib/utils/badge-styles";
import { formatDate } from "$lib/utils/date-formatter";
import { createQuery } from "@tanstack/svelte-query";

// Filter states
// biome-ignore lint/style/useConst: Svelte 5 binding/assignment requires let
let statusFilter = $state<string>("all");
// biome-ignore lint/style/useConst: Svelte 5 binding/assignment requires let
let priorityFilter = $state<string>("all");
let sortBy = $state<"id" | "title" | "status" | "priority" | "created_at">(
	"created_at",
);
let sortOrder = $state<"asc" | "desc">("desc");
// biome-ignore lint/style/useConst: Svelte 5 assignment requires let
let currentPage = $state(1);
const itemsPerPage = 10;

// Modal state
let selectedWorkOrder = $state<WorkOrder | null>(null);
let modalMode = $state<"view" | "edit" | "create">("view");
let isModalOpen = $state(false);

// Define reactive query options using $derived
const queryOptions = $derived({
	queryKey: ["workOrders", currentPage],
	queryFn: async () => {
		const response = await clientWrapper<WorkOrdersResponse>({
			method: "GET",
			url: `${API_ENDPOINTS.WORK_ORDERS}?page=${currentPage}&limit=${itemsPerPage}`,
		});
		return response;
	},
});

// Pass the derived options to createQuery, and make workOrdersQuery itself derived
const workOrdersQuery = $derived(createQuery(queryOptions));

// Filter and sort work orders
let filteredWorkOrders = $state<WorkOrder[]>([]);

$effect(() => {
	if (!$workOrdersQuery.data?.data) {
		filteredWorkOrders = [];
		return;
	}

	let filtered = [...$workOrdersQuery.data.data];

	// Apply status filter
	if (statusFilter !== "all") {
		filtered = filtered.filter((wo) => wo.status === statusFilter);
	}

	// Apply priority filter
	if (priorityFilter !== "all") {
		filtered = filtered.filter((wo) => wo.priority === priorityFilter);
	}

	// Apply sorting
	filtered.sort((a, b) => {
		let aVal: string | number | Date = a[sortBy];
		let bVal: string | number | Date = b[sortBy];

		// For UUID sorting, use string comparison
		if (sortBy === "id") {
			aVal = String(aVal);
			bVal = String(bVal);
		}
		// For date sorting, convert to Date objects
		else if (sortBy === "created_at") {
			aVal = new Date(aVal as string);
			bVal = new Date(bVal as string);
		}

		if (aVal < bVal) return sortOrder === "asc" ? -1 : 1;
		if (aVal > bVal) return sortOrder === "asc" ? 1 : -1;
		return 0;
	});

	filteredWorkOrders = filtered;
});

// Get unique statuses and priorities
let uniqueStatuses = $state<string[]>([]);
let uniquePriorities = $state<string[]>([]);

$effect(() => {
	if (!$workOrdersQuery.data?.data) {
		uniqueStatuses = [];
		uniquePriorities = [];
		return;
	}
	uniqueStatuses = [
		...new Set($workOrdersQuery.data.data.map((wo) => wo.status)),
	];
	uniquePriorities = [
		...new Set($workOrdersQuery.data.data.map((wo) => wo.priority)),
	];
});

// Badge styling functions moved to shared utilities

function toggleSort(field: typeof sortBy) {
	if (sortBy === field) {
		sortOrder = sortOrder === "asc" ? "desc" : "asc";
	} else {
		sortBy = field;
		sortOrder = "asc";
	}
}

function openViewModal(workOrder: WorkOrder) {
	selectedWorkOrder = workOrder;
	modalMode = "view";
	isModalOpen = true;
}

function openEditModal(workOrder: WorkOrder) {
	selectedWorkOrder = workOrder;
	modalMode = "edit";
	isModalOpen = true;
}

function openCreateModal() {
	selectedWorkOrder = null;
	modalMode = "create";
	isModalOpen = true;
}

function closeModal() {
	isModalOpen = false;
	selectedWorkOrder = null;
}

async function deleteWorkOrder(workOrder: WorkOrder) {
	if (
		!confirm(
			`Are you sure you want to delete "${workOrder.title}"? This action cannot be undone.`,
		)
	) {
		return;
	}

	try {
		await clientWrapper({
			method: "DELETE",
			url: `${API_ENDPOINTS.WORK_ORDERS}/${workOrder.id}`,
		});

		// Refresh the work orders list
		$workOrdersQuery.refetch();
	} catch (error) {
		console.error("Error deleting work order:", error);
		alert("Failed to delete work order. Please try again.");
	}
}

// Badge styling and date formatting now handled by shared utilities
</script>

<style>
  select:focus {
    outline: none;
    border-color: inherit;
    box-shadow: none;
  }
</style>

<div class="px-2 py-4 sm:px-4 lg:px-6 max-w-none">
  <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
    <div>
      <h1 class="text-3xl font-bold text-base-content">Work Orders</h1>
      <p class="mt-2 text-base-content/70">Manage and track all work orders</p>
    </div>
    <button class="btn btn-primary" onclick={openCreateModal}>
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
      New Work Order
    </button>
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
  {:else if $workOrdersQuery.data}
    <!-- Filters -->
    <div class="flex flex-wrap items-end justify-between gap-4 mb-6">
      <div class="flex gap-4">
        <div class="form-control">
          <label class="label" for="status-filter">
            <span class="label-text font-medium">Status</span>
          </label>
          <select
            id="status-filter"
            name="status-filter"
            class="select select-bordered bg-base-100"
            bind:value={statusFilter}
          >
            <option value="all">All Statuses</option>
            {#each uniqueStatuses as status}
              <option value={status}>{status}</option>
            {/each}
          </select>
        </div>

        <div class="form-control">
          <label class="label" for="priority-filter">
            <span class="label-text font-medium">Priority</span>
          </label>
          <select
            id="priority-filter"
            name="priority-filter"
            class="select select-bordered bg-base-100"
            bind:value={priorityFilter}
          >
            <option value="all">All Priorities</option>
            {#each uniquePriorities as priority}
              <option value={priority}>{priority}</option>
            {/each}
          </select>
        </div>
      </div>

      <div class="text-sm text-base-content/60 font-medium">
        {filteredWorkOrders.length} of {$workOrdersQuery.data.data.length} orders
      </div>
    </div>

    <div class="card bg-base-100 shadow-xl w-full">
      <div class="card-body p-0">
        {#if filteredWorkOrders.length === 0}
          <div class="text-center py-12">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-base-content/30 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p class="text-base-content/60 text-lg">No work orders match your filters</p>
            <button onclick={() => { statusFilter = "all"; priorityFilter = "all"; }} class="btn btn-sm btn-ghost mt-4">
              Clear filters
            </button>
          </div>
        {:else}
          <div class="overflow-x-auto">
            <table class="table table-zebra w-full">
              <thead>
                <tr>
                  <th class="cursor-pointer hover:bg-base-200" onclick={() => toggleSort("title")}>
                    <div class="flex items-center gap-2">
                      Title & Description
                      {#if sortBy === "title"}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={sortOrder === "asc" ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"} />
                        </svg>
                      {/if}
                    </div>
                  </th>
                  <th class="cursor-pointer hover:bg-base-200" onclick={() => toggleSort("created_at")}>
                    <div class="flex items-center gap-2">
                      Date Opened
                      {#if sortBy === "created_at"}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={sortOrder === "asc" ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"} />
                        </svg>
                      {/if}
                    </div>
                  </th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {#each filteredWorkOrders as workOrder}
                  <tr class="hover">
                    <td class="max-w-2xl">
                      <div class="flex items-start justify-between mb-1">
                        <div class="font-medium text-base">{workOrder.title}</div>
                        <div class="flex flex-col gap-1 items-end">
                          <div class="badge badge-xs border {getTableStatusBadgeClasses(workOrder.status)}">
                            {workOrder.status}
                          </div>
                          <div class="badge badge-xs border {getTablePriorityBadgeClasses(workOrder.priority)}">
                            {workOrder.priority}
                          </div>
                        </div>
                      </div>
                      {#if workOrder.description}
                        <div class="text-sm opacity-70 mt-1">{workOrder.description}</div>
                      {/if}
                      {#if workOrder.location}
                        <div class="text-xs opacity-60 mt-1">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                          </svg>
                          {workOrder.location.address || workOrder.location.name}
                        </div>
                      {/if}
                    </td>
                    <td>
                      <div class="text-sm">{formatDate(workOrder.created_at)}</div>
                    </td>
                    <td>
                      <div class="flex gap-1">
                        <button class="btn btn-ghost btn-sm" onclick={() => openViewModal(workOrder)} title="View work order" aria-label="View work order">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                        </button>
                        <button class="btn btn-ghost btn-sm" onclick={() => openEditModal(workOrder)} title="Edit work order" aria-label="Edit work order">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button class="btn btn-ghost btn-sm text-orange-700 hover:bg-orange-50 hover:text-orange-800" onclick={() => deleteWorkOrder(workOrder)} title="Delete work order" aria-label="Delete work order">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>

          {#if $workOrdersQuery.data?.pagination && $workOrdersQuery.data.pagination.totalPages > 1}
            <div class="flex justify-center p-4 border-t">
              <div class="join">
                <button
                  class="join-item btn btn-sm"
                  disabled={currentPage === 1}
                  onclick={() => currentPage = currentPage - 1}
                >
                  «
                </button>
                <button class="join-item btn btn-sm">
                  Page {currentPage} of {$workOrdersQuery.data.pagination.totalPages}
                </button>
                <button
                  class="join-item btn btn-sm"
                  disabled={currentPage === $workOrdersQuery.data.pagination.totalPages}
                  onclick={() => currentPage = currentPage + 1}
                >
                  »
                </button>
              </div>
            </div>
          {/if}
        {/if}
      </div>
    </div>
  {/if}
</div>

<!-- Work Order Modal -->
<WorkOrderModal
  workOrder={selectedWorkOrder}
  bind:mode={modalMode}
  isOpen={isModalOpen}
  onClose={closeModal}
/>
