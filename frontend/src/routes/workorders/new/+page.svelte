<script lang="ts">
import { goto } from "$app/navigation";
import { clientWrapper } from "$lib/api/client-wrapper";
import { API_ENDPOINTS } from "$lib/constants";
import type { WorkOrder, WorkOrderCreate } from "$lib/types/work-orders";
import { createMutation } from "@tanstack/svelte-query";

// Define Location interface for mock data
interface Location {
	id: number;
	name: string;
	address: string;
}

// Form state
let form = $state({
	title: "",
	description: "",
	status: "Open" as const,
	priority: "Medium" as const,
	location_id: "",
});

let locations = $state<Location[]>([]);
let isLoadingLocations = $state(false);

// Create mutation
const workOrderCreateMutation = createMutation({
	mutationFn: async (data: WorkOrderCreate) => {
		return await clientWrapper<WorkOrder>({
			method: "POST",
			url: API_ENDPOINTS.WORK_ORDERS,
			data,
		});
	},
	onSuccess: () => {
		goto("/workorders");
	},
});

// Load locations on mount
$effect(() => {
	loadLocations();
});

async function loadLocations() {
	isLoadingLocations = true;
	try {
		// For now, we'll use mock locations until we have a locations API
		locations = [
			{
				id: 1,
				name: "Main Office Building",
				address: "316 E. Washington St, Hagerstown, MD",
			},
			{
				id: 2,
				name: "Warehouse Facility",
				address: "17850 Garland Groh Blvd, Hagerstown, MD",
			},
			{
				id: 3,
				name: "Customer Site A",
				address: "11374 Cross Fields Dr, Waynesboro, PA",
			},
		];
	} catch (error) {
		console.error("Failed to load locations:", error);
	} finally {
		isLoadingLocations = false;
	}
}

function handleSubmit() {
	if (!form.title.trim()) return;

	const createData: WorkOrderCreate = {
		title: form.title.trim(),
		description: form.description.trim() || undefined,
		status: form.status,
		priority: form.priority,
		location_id: form.location_id
			? Number.parseInt(form.location_id)
			: undefined,
	};

	$workOrderCreateMutation.mutate(createData);
}

function resetForm() {
	form = {
		title: "",
		description: "",
		status: "Open",
		priority: "Medium",
		location_id: "",
	};
}
</script>

<div class="px-4 py-6 sm:px-6 lg:px-8">
  <div class="max-w-2xl mx-auto">
    <div class="flex items-center gap-4 mb-8">
      <a href="/workorders" class="btn btn-ghost btn-sm">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Back to Work Orders
      </a>
      <div>
        <h1 class="text-3xl font-bold text-base-content">New Work Order</h1>
        <p class="mt-2 text-base-content/70">Create a new work order</p>
      </div>
    </div>

    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
          <div class="space-y-6">
            <!-- Title -->
            <div class="form-control">
              <label class="label" for="new-title">
                <span class="label-text font-medium">Title <span class="text-error">*</span></span>
              </label>
              <input
                id="new-title"
                name="title"
                type="text"
                class="input input-bordered"
                bind:value={form.title}
                placeholder="Enter work order title..."
                required
              />
            </div>

            <!-- Description -->
            <div class="form-control">
              <label class="label" for="new-description">
                <span class="label-text font-medium">Description</span>
              </label>
              <textarea
                id="new-description"
                name="description"
                class="textarea textarea-bordered h-32"
                bind:value={form.description}
                placeholder="Describe the work to be done..."
              ></textarea>
            </div>

            <!-- Status and Priority Row -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="form-control">
                <label class="label" for="new-status">
                  <span class="label-text font-medium">Status</span>
                </label>
                <select
                  id="new-status"
                  name="status"
                  class="select select-bordered"
                  bind:value={form.status}
                >
                  <option value="Open">Open</option>
                  <option value="In Progress">In Progress</option>
                  <option value="On Hold">On Hold</option>
                </select>
              </div>

              <div class="form-control">
                <label class="label" for="new-priority">
                  <span class="label-text font-medium">Priority</span>
                </label>
                <select
                  id="new-priority"
                  name="priority"
                  class="select select-bordered"
                  bind:value={form.priority}
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </div>
            </div>

            <!-- Location -->
            <div class="form-control">
              <label class="label" for="new-location">
                <span class="label-text font-medium">Location</span>
              </label>
              {#if isLoadingLocations}
                <div class="flex items-center gap-2">
                  <span class="loading loading-spinner loading-sm"></span>
                  <span class="text-sm">Loading locations...</span>
                </div>
              {:else}
                <select
                  id="new-location"
                  name="location"
                  class="select select-bordered"
                  bind:value={form.location_id}
                >
                  <option value="">Select a location (optional)</option>
                  {#each locations as location}
                    <option value={location.id}>{location.name} - {location.address}</option>
                  {/each}
                </select>
              {/if}
            </div>

            <!-- Form Actions -->
            <div class="flex flex-col sm:flex-row gap-4 pt-6">
              <button
                type="submit"
                class="btn btn-primary flex-1"
                disabled={!form.title.trim() || $workOrderCreateMutation.isPending}
              >
                {#if $workOrderCreateMutation.isPending}
                  <span class="loading loading-spinner loading-sm"></span>
                  Creating...
                {:else}
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  Create Work Order
                {/if}
              </button>

              <button
                type="button"
                class="btn btn-outline flex-1"
                onclick={resetForm}
                disabled={$workOrderCreateMutation.isPending}
              >
                Reset Form
              </button>
            </div>
          </div>
        </form>

        {#if $workOrderCreateMutation.error}
          <div class="alert alert-error mt-6">
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Failed to create work order. Please try again.</span>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>
