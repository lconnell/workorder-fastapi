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
let statusFilter = $state<string[]>([]);
// biome-ignore lint/style/useConst: Svelte 5 binding/assignment requires let
let priorityFilter = $state<string[]>([]);
let sortBy = $state<"id" | "title" | "status" | "priority" | "created_at">(
	"created_at",
);
let sortOrder = $state<"asc" | "desc">("desc");
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

// Filter and sort work orders (client-side)
let filteredAndSortedWorkOrders = $state<WorkOrder[]>([]);

$effect(() => {
	if (!$workOrdersQuery.data?.data) {
		filteredAndSortedWorkOrders = [];
		return;
	}

	let filtered = [...$workOrdersQuery.data.data];

	// Apply status filter
	if (statusFilter.length > 0) {
		filtered = filtered.filter((wo) => statusFilter.includes(wo.status));
	}

	// Apply priority filter
	if (priorityFilter.length > 0) {
		filtered = filtered.filter((wo) => priorityFilter.includes(wo.priority));
	}

	// Apply client-side sorting
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

	filteredAndSortedWorkOrders = filtered;
});

// Reset pagination when filters change
$effect(() => {
	statusFilter;
	priorityFilter;
	currentPage = 1;
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

function openCreateModal() {
	selectedWorkOrder = null;
	modalMode = "create";
	isModalOpen = true;
}

function closeModal() {
	isModalOpen = false;
	selectedWorkOrder = null;
}

// Badge styling and date formatting now handled by shared utilities
</script>


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
        <!-- Status Filter -->
        <div class="form-control">
          <span class="label-text font-medium mb-2">Status</span>
          <div class="dropdown">
            <button type="button" class="btn btn-outline bg-base-100 justify-between min-w-48">
              <span>
                {#if statusFilter.length === 0}
                  All Statuses
                {:else if statusFilter.length === 1}
                  {statusFilter[0]}
                {:else}
                  {statusFilter.length} selected
                {/if}
              </span>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div class="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow border">
              {#each uniqueStatuses as status}
                <label class="label cursor-pointer justify-start">
                  <input
                    type="checkbox"
                    class="checkbox checkbox-sm mr-3"
                    bind:group={statusFilter}
                    value={status}
                  />
                  <span class="label-text">{status}</span>
                </label>
              {/each}
            </div>
          </div>
        </div>

        <!-- Priority Filter -->
        <div class="form-control">
          <span class="label-text font-medium mb-2">Priority</span>
          <div class="dropdown">
            <button type="button" class="btn btn-outline bg-base-100 justify-between min-w-48">
              <span>
                {#if priorityFilter.length === 0}
                  All Priorities
                {:else if priorityFilter.length === 1}
                  {priorityFilter[0]}
                {:else}
                  {priorityFilter.length} selected
                {/if}
              </span>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div class="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow border">
              {#each uniquePriorities as priority}
                <label class="label cursor-pointer justify-start">
                  <input
                    type="checkbox"
                    class="checkbox checkbox-sm mr-3"
                    bind:group={priorityFilter}
                    value={priority}
                  />
                  <span class="label-text">{priority}</span>
                </label>
              {/each}
            </div>
          </div>
        </div>
      </div>

      <div class="text-sm text-base-content/60 font-medium">
        {filteredAndSortedWorkOrders.length} of {$workOrdersQuery.data.data.length} orders
      </div>
    </div>

    <div class="card bg-base-100 shadow-xl w-full">
      <div class="card-body p-0">
        {#if filteredAndSortedWorkOrders.length === 0}
          <div class="text-center py-12">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-base-content/30 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p class="text-base-content/60 text-lg">No work orders match your filters</p>
            <button onclick={() => { statusFilter = []; priorityFilter = []; }} class="btn btn-sm btn-ghost mt-4">
              Clear filters
            </button>
          </div>
        {:else}
          <div class="overflow-x-auto">
            <table class="table table-zebra w-full">
              <thead>
                <tr>
                  <th class="cursor-pointer hover:bg-primary/10 transition-colors" onclick={() => toggleSort("title")}>
                    <div class="flex items-center gap-2">
                      Title
                      {#if sortBy === "title"}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={sortOrder === "asc" ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"} />
                        </svg>
                      {/if}
                    </div>
                  </th>
                  <th class="cursor-pointer hover:bg-primary/10 transition-colors" onclick={() => toggleSort("status")}>
                    <div class="flex items-center gap-2">
                      Status
                      {#if sortBy === "status"}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={sortOrder === "asc" ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"} />
                        </svg>
                      {/if}
                    </div>
                  </th>
                  <th class="cursor-pointer hover:bg-primary/10 transition-colors" onclick={() => toggleSort("priority")}>
                    <div class="flex items-center gap-2">
                      Priority
                      {#if sortBy === "priority"}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={sortOrder === "asc" ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"} />
                        </svg>
                      {/if}
                    </div>
                  </th>
                  <th class="cursor-pointer hover:bg-primary/10 transition-colors" onclick={() => toggleSort("created_at")}>
                    <div class="flex items-center gap-2">
                      Date Opened
                      {#if sortBy === "created_at"}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={sortOrder === "asc" ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"} />
                        </svg>
                      {/if}
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                {#each filteredAndSortedWorkOrders as workOrder}
                  <tr class="cursor-pointer hover:bg-primary/10 transition-colors" onclick={() => openViewModal(workOrder)}>
                    <td class="max-w-2xl">
                      <div class="font-medium text-base mb-1">{workOrder.title}</div>
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
                      <div class="badge border {getTableStatusBadgeClasses(workOrder.status)}">
                        {workOrder.status}
                      </div>
                    </td>
                    <td>
                      <div class="badge border {getTablePriorityBadgeClasses(workOrder.priority)}">
                        {workOrder.priority}
                      </div>
                    </td>
                    <td>
                      <div class="text-sm">{formatDate(workOrder.created_at)}</div>
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
