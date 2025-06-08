<script lang="ts">
import { clientWrapper } from "$lib/api/client-wrapper";
import FilterDrawer from "$lib/components/FilterDrawer.svelte";
import {
	IconAppLogo,
	IconErrorCrossCircle,
	IconFilter,
	IconLocationPin,
	IconPlus,
	IconSortArrow,
} from "$lib/components/icons";
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
let statusFilter = $state<string[]>([]);
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

// Filter sheet state
let isFilterSheetOpen = $state(false);
// Temporary filter states for the sheet
let tempStatusFilter = $state<string[]>([]);
let tempPriorityFilter = $state<string[]>([]);

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

function openFilterSheet() {
	// Copy current filters to temp states
	tempStatusFilter = [...statusFilter];
	tempPriorityFilter = [...priorityFilter];
	isFilterSheetOpen = true;
}

function applyFilters() {
	// Apply temp filters to actual filters
	statusFilter = [...tempStatusFilter];
	priorityFilter = [...tempPriorityFilter];
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
      <IconPlus class="mr-2" />
      New Work Order
    </button>
  </div>

  {#if $workOrdersQuery.isLoading}
    <div class="flex justify-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else if $workOrdersQuery.error}
    <div class="alert alert-error">
      <IconErrorCrossCircle class="stroke-current shrink-0 h-6 w-6" />
      <span>Failed to load work orders. Please try again.</span>
    </div>
  {:else if $workOrdersQuery.data}
    <!-- Filters -->
    <div class="card bg-base-100 shadow-sm mb-6 rounded-lg">
      <div class="card-body p-4">
        <div class="flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <button class="btn btn-outline" onclick={openFilterSheet}>
          <IconFilter class="mr-2" />
          Filters
          {#if statusFilter.length > 0 || priorityFilter.length > 0}
            <div class="badge badge-primary badge-sm">{statusFilter.length + priorityFilter.length}</div>
          {/if}
        </button>

        {#if statusFilter.length > 0 || priorityFilter.length > 0}
          <button
            class="btn btn-ghost btn-sm"
            onclick={() => { statusFilter = []; priorityFilter = []; }}
          >
            Clear filters
          </button>
        {/if}
      </div>

          <div class="text-sm text-base-content/60 font-medium">
            {filteredAndSortedWorkOrders.length} of {$workOrdersQuery.data.data.length} orders
          </div>
        </div>
      </div>
    </div>

    {#if filteredAndSortedWorkOrders.length === 0}
      <div class="card bg-base-100 shadow-sm rounded-lg">
        <div class="card-body">
          <div class="text-center py-12">
            <IconAppLogo size="3em" class="mx-auto text-base-content/30 mb-4" /> {/* h-12 w-12 */}
            <p class="text-base-content/60 text-lg">No work orders match your filters</p>
            <button onclick={() => { statusFilter = []; priorityFilter = []; }} class="btn btn-sm btn-ghost mt-4">
              Clear filters
            </button>
          </div>
        </div>
      </div>
    {:else}
      <div class="card bg-base-100 shadow-sm rounded-lg">
        <div class="card-body p-0">
          <div class="overflow-x-auto">
            <table class="table table-pin-rows">
          <thead>
            <tr>
              <th class="cursor-pointer" onclick={() => toggleSort("title")}>
                <div class="flex items-center gap-2">
                  Title
                  {#if sortBy === "title"}
                    <IconSortArrow direction={sortOrder} />
                  {/if}
                </div>
              </th>
              <th class="cursor-pointer" onclick={() => toggleSort("status")}>
                <div class="flex items-center gap-2">
                  Status
                  {#if sortBy === "status"}
                    <IconSortArrow direction={sortOrder} />
                  {/if}
                </div>
              </th>
              <th class="cursor-pointer" onclick={() => toggleSort("priority")}>
                <div class="flex items-center gap-2">
                  Priority
                  {#if sortBy === "priority"}
                    <IconSortArrow direction={sortOrder} />
                  {/if}
                </div>
              </th>
              <th class="cursor-pointer" onclick={() => toggleSort("created_at")}>
                <div class="flex items-center gap-2">
                  Date Opened
                  {#if sortBy === "created_at"}
                    <IconSortArrow direction={sortOrder} />
                  {/if}
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            {#each filteredAndSortedWorkOrders as workOrder}
              <tr class="hover cursor-pointer" onclick={() => openViewModal(workOrder)}>
                <td>
                  <div class="font-bold">{workOrder.title}</div>
                  {#if workOrder.location}
                    <div class="text-sm opacity-50">
                      <IconLocationPin class="inline mr-1" />
                      {workOrder.location.address || workOrder.location.name}
                    </div>
                  {/if}
                </td>
                <td>
                  <div class="badge {getTableStatusBadgeClasses(workOrder.status)}">
                    {workOrder.status}
                  </div>
                </td>
                <td>
                  <div class="badge {getTablePriorityBadgeClasses(workOrder.priority)}">
                    {workOrder.priority}
                  </div>
                </td>
                <td>{formatDate(workOrder.created_at)}</td>
              </tr>
            {/each}
          </tbody>
            </table>
          </div>
        </div>
      </div>

      {#if $workOrdersQuery.data?.pagination && $workOrdersQuery.data.pagination.totalPages > 1}
        <div class="flex justify-center p-4">
          <div class="join">
            <button
              class="join-item btn"
              disabled={currentPage === 1}
              onclick={() => currentPage = currentPage - 1}
            >
              «
            </button>
            <button class="join-item btn">
              Page {currentPage} of {$workOrdersQuery.data.pagination.totalPages}
            </button>
            <button
              class="join-item btn"
              disabled={currentPage === $workOrdersQuery.data.pagination.totalPages}
              onclick={() => currentPage = currentPage + 1}
            >
              »
            </button>
          </div>
        </div>
      {/if}
    {/if}
  {/if}
</div>

<!-- Work Order Modal -->
<WorkOrderModal
  workOrder={selectedWorkOrder}
  bind:mode={modalMode}
  isOpen={isModalOpen}
  onClose={closeModal}
/>

<!-- Filter Drawer -->
<FilterDrawer
  drawerId="filter-drawer"
  isOpen={isFilterSheetOpen}
  onClose={() => isFilterSheetOpen = false}
  title="Filter Work Orders"
  onApply={applyFilters}
>
  <!-- Status Filter Section -->
  <div class="form-control">
    <h4 class="label-text font-semibold mb-3">Status</h4>
    <div class="space-y-3">
      {#each uniqueStatuses as status, index}
        <div class="form-control">
          <label class="label cursor-pointer justify-start" for="status-{index}">
            <input
              type="checkbox"
              class="checkbox checkbox-primary"
              bind:group={tempStatusFilter}
              value={status}
              id="status-{index}"
              name="status-filter"
            />
            <span class="label-text ml-3">{status}</span>
          </label>
        </div>
      {/each}
    </div>
  </div>

  <!-- Priority Filter Section -->
  <div class="form-control">
    <h4 class="label-text font-semibold mb-3">Priority</h4>
    <div class="space-y-3">
      {#each uniquePriorities as priority, index}
        <div class="form-control">
          <label class="label cursor-pointer justify-start" for="priority-{index}">
            <input
              type="checkbox"
              class="checkbox checkbox-primary"
              bind:group={tempPriorityFilter}
              value={priority}
              id="priority-{index}"
              name="priority-filter"
            />
            <span class="label-text ml-3">{priority}</span>
          </label>
        </div>
      {/each}
    </div>
  </div>

  <!-- Filter Summary -->
  <div class="divider"></div>
  <div class="text-sm text-base-content/60">
    {tempStatusFilter.length + tempPriorityFilter.length} filter{tempStatusFilter.length + tempPriorityFilter.length !== 1 ? 's' : ''} selected
  </div>
</FilterDrawer>
