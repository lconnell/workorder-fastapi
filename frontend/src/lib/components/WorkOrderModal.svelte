<script lang="ts">
import { clientWrapper } from "$lib/api/client-wrapper";
import { API_ENDPOINTS } from "$lib/constants";
import type {
	WorkOrder,
	WorkOrderCreate,
	WorkOrderUpdate,
} from "$lib/types/work-orders";
import {
	getModalPriorityBadgeClasses,
	getModalStatusBadgeClasses,
} from "$lib/utils/badge-styles";
import { formatDateTime } from "$lib/utils/date-formatter";
import { createMutation, useQueryClient } from "@tanstack/svelte-query";

interface LocationCreate {
	name: string;
	address?: string | null;
	city?: string | null;
	state_province?: string | null;
	postal_code?: string | null;
	country?: string;
}

interface Location {
	id: string;
	name: string;
	address?: string | null;
	city?: string | null;
	state_province?: string | null;
	postal_code?: string | null;
	country?: string | null;
	latitude?: number | null;
	longitude?: number | null;
}

interface Props {
	workOrder: WorkOrder | null;
	mode: "view" | "edit" | "create";
	isOpen: boolean;
	onClose: () => void;
}

// biome-ignore lint/style/useConst: Svelte 5 $bindable prop assignment requires let
let { workOrder, mode = $bindable(), isOpen, onClose }: Props = $props();

const queryClient = useQueryClient();

// Form state initialization handled in separate effect below

// Form state for editing/creating
let editForm = $state({
	title: "",
	description: "",
	status: "",
	priority: "",
	assigned_to_user_id: "",
	location_id: "",
	// Separate address fields for clarity
	location_address: "",
	location_city: "",
	location_state: "",
	location_zip: "",
});

// Form submission state
let isCreatingLocation = $state(false);

// Initialize form when work order changes or when creating new
$effect(() => {
	if (mode === "create") {
		// Initialize with default values for create mode
		editForm = {
			title: "",
			description: "",
			status: "Open",
			priority: "Medium",
			assigned_to_user_id: "",
			location_id: "",
			location_address: "",
			location_city: "",
			location_state: "",
			location_zip: "",
		};
	} else if (workOrder && mode === "edit") {
		editForm = {
			title: workOrder.title || "",
			description: workOrder.description || "",
			status: workOrder.status || "",
			priority: workOrder.priority || "",
			assigned_to_user_id: workOrder.assigned_to_user_id || "",
			location_id: workOrder.location_id || "",
			location_address: workOrder.location?.address || "",
			location_city: workOrder.location?.city || "",
			location_state: workOrder.location?.state_province || "",
			location_zip: workOrder.location?.postal_code || "",
		};
	}
});

// Update mutation
const updateMutation = createMutation({
	mutationFn: async (data: WorkOrderUpdate) => {
		return await clientWrapper<WorkOrder>({
			method: "PUT",
			url: `${API_ENDPOINTS.WORK_ORDERS}/${workOrder?.id}`,
			data,
		});
	},
	onSuccess: () => {
		queryClient.invalidateQueries({ queryKey: ["workOrders"] });
		onClose();
	},
});

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
		queryClient.invalidateQueries({ queryKey: ["workOrders"] });
		onClose();
	},
});

async function handleSubmit() {
	try {
		let locationId: string | undefined = undefined;

		// Create location if any address fields are provided
		if (
			editForm.location_address.trim() ||
			editForm.location_city.trim() ||
			editForm.location_state.trim() ||
			editForm.location_zip.trim()
		) {
			isCreatingLocation = true;

			// Use the separate fields directly (no parsing needed!)
			const locationData: LocationCreate = {
				name: editForm.location_address.trim() || "Work Location",
				address: editForm.location_address.trim() || null,
				city: editForm.location_city.trim() || null,
				state_province: editForm.location_state.trim() || null,
				postal_code: editForm.location_zip.trim() || null,
				country: "USA",
			};

			const locationResult = await clientWrapper<Location>({
				method: "POST",
				url: API_ENDPOINTS.LOCATIONS,
				data: locationData,
			});

			locationId = locationResult.id;
			isCreatingLocation = false;
		} else if (editForm.location_id) {
			// Use existing location ID if provided
			locationId = editForm.location_id;
		}

		if (mode === "create") {
			// Handle create mode
			const createData: WorkOrderCreate = {
				title: editForm.title,
				status: editForm.status as WorkOrderCreate["status"],
				priority: editForm.priority as WorkOrderCreate["priority"],
			};

			// Add optional fields if they have values
			if (editForm.description) createData.description = editForm.description;
			if (editForm.assigned_to_user_id)
				createData.assigned_to_user_id = editForm.assigned_to_user_id;
			if (locationId) createData.location_id = locationId;

			$workOrderCreateMutation.mutate(createData);
		} else if (mode === "edit" && workOrder) {
			// Handle edit mode
			const updateData: WorkOrderUpdate = {};

			if (editForm.title !== workOrder.title) updateData.title = editForm.title;
			if (editForm.description !== workOrder.description)
				updateData.description = editForm.description;
			if (editForm.status !== workOrder.status)
				updateData.status = editForm.status as WorkOrder["status"];
			if (editForm.priority !== workOrder.priority)
				updateData.priority = editForm.priority as WorkOrder["priority"];
			if (editForm.assigned_to_user_id !== workOrder.assigned_to_user_id)
				updateData.assigned_to_user_id =
					editForm.assigned_to_user_id || undefined;

			// Handle location updates
			const currentLocationId = workOrder.location_id;
			if (locationId !== currentLocationId) {
				updateData.location_id = locationId;
			}

			if (Object.keys(updateData).length > 0) {
				$updateMutation.mutate(updateData);
			}
		}
	} catch (error) {
		console.error("Error in handleSubmit:", error);
		isCreatingLocation = false;
		// You might want to show an error message to the user here
		alert(
			`Failed to save work order: ${error instanceof Error ? error.message : "Unknown error"}`,
		);
	}
}

async function handleDelete() {
	if (!workOrder) return;

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

		// Refresh the work orders list and close modal
		queryClient.invalidateQueries({ queryKey: ["workOrders"] });
		onClose();
	} catch (error) {
		console.error("Error deleting work order:", error);
		alert("Failed to delete work order. Please try again.");
	}
}

// Badge styling and date formatting now handled by shared utilities
</script>

{#if isOpen && (workOrder || mode === "create")}
<div class="modal modal-open z-50">
  <div class="modal-box w-full max-w-5xl h-[92vh] mx-auto bg-base-100 shadow-2xl border border-base-300 rounded-xl p-8 z-50 flex flex-col">
    <div class="flex items-center justify-between mb-8">
      <h3 class="font-bold text-xl text-base-content">
        {mode === "view" ? workOrder?.title || "Work Order Details" : mode === "edit" ? workOrder?.title || "Edit Work Order" : "Create Work Order"}
        {#if workOrder}
          <span class="text-base-content/60 font-mono text-sm">(#{workOrder.id.slice(0, 8)})</span>
        {/if}
      </h3>
      <button class="btn btn-sm btn-circle btn-ghost" onclick={onClose}>✕</button>
    </div>

    {#if mode === "view"}
      <!-- View Mode -->
      <div class="space-y-8 flex-1 overflow-auto">
        <div class="bg-base-200/50 p-6 rounded-lg">
          <div class="flex items-center gap-3 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-base-content/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="font-semibold text-base-content">Description</p>
          </div>
          <textarea readonly class="w-full min-h-32 max-h-48 resize-none whitespace-pre-wrap text-base-content/70 bg-transparent border-none outline-none p-0">{workOrder?.description || "No description provided"}</textarea>
        </div>

        <!-- Location and Timeline side by side -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          {#if workOrder?.location}
            <div class="bg-base-200/50 p-6 rounded-lg">
              <div class="flex items-center gap-3 mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-base-content/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <p class="font-semibold text-base-content">Location</p>
              </div>
              <p class="font-semibold text-base">{workOrder?.location?.address || workOrder?.location?.name}</p>
              {#if workOrder?.location?.city || workOrder?.location?.state_province || workOrder?.location?.postal_code}
                <p class="text-base-content/70 mt-1">
                  {[workOrder?.location?.city, [workOrder?.location?.state_province, workOrder?.location?.postal_code].filter(Boolean).join(' ')].filter(Boolean).join(', ')}
                </p>
              {/if}
            </div>
          {/if}

          <div class="bg-base-200/50 p-6 rounded-lg">
            <div class="flex items-center gap-3 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-base-content/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="font-semibold text-base-content">Timeline</p>
            </div>
            <div class="space-y-2">
              <p class="text-base"><span class="text-base-content/60">Created:</span> {formatDateTime(workOrder?.created_at || '')}</p>
              {#if workOrder?.updated_at !== workOrder?.created_at}
                <p class="text-base"><span class="text-base-content/60">Updated:</span> {formatDateTime(workOrder?.updated_at || '')}</p>
              {/if}
            </div>
          </div>
        </div>

        <!-- Badges below -->
        <div class="flex gap-2">
          <div class="badge {getModalStatusBadgeClasses(workOrder?.status || '').bg} {getModalStatusBadgeClasses(workOrder?.status || '').text}">{workOrder?.status}</div>
          <div class="badge border {getModalPriorityBadgeClasses(workOrder?.priority || '').bg} {getModalPriorityBadgeClasses(workOrder?.priority || '').text} {getModalPriorityBadgeClasses(workOrder?.priority || '').border}">{workOrder?.priority}</div>
        </div>
      </div>

      <div class="modal-action pt-6 border-t border-base-300 mt-auto">
        {#if workOrder}
          <button class="btn btn-ghost text-orange-700 hover:bg-orange-50 hover:text-orange-800" onclick={handleDelete} title="Delete work order" aria-label="Delete work order">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Delete
          </button>
        {/if}
        <div class="flex-1"></div>
        <button class="btn btn-ghost" onclick={onClose}>Close</button>
        <button class="btn btn-primary" onclick={() => mode = "edit"}>Edit</button>
      </div>

    {:else if mode === "edit" || mode === "create"}
      <!-- Edit/Create Mode -->
      <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="flex flex-col flex-1">
        <div class="space-y-8 flex-1 overflow-auto">
          <div class="form-control">
            <label class="label" for="edit-title">
              <span class="label-text">Title</span>
            </label>
            <input id="edit-title" name="title" type="text" class="input input-bordered w-full" bind:value={editForm.title} required />
          </div>

          <div class="form-control">
            <label class="label" for="edit-description">
              <span class="label-text">Description</span>
            </label>
            <textarea id="edit-description" name="description" class="textarea textarea-bordered w-full min-h-24 max-h-40 resize-y" bind:value={editForm.description}></textarea>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="form-control">
              <label class="label" for="edit-status">
                <span class="label-text">Status</span>
              </label>
              <select id="edit-status" name="status" class="select select-bordered w-full" bind:value={editForm.status}>
                <option value="Open">Open</option>
                <option value="In Progress">In Progress</option>
                {#if mode === "edit"}
                  <option value="Completed">Completed</option>
                {/if}
                <option value="On Hold">On Hold</option>
                {#if mode === "edit"}
                  <option value="Cancelled">Cancelled</option>
                {/if}
              </select>
            </div>

            <div class="form-control">
              <label class="label" for="edit-priority">
                <span class="label-text">Priority</span>
              </label>
              <select id="edit-priority" name="priority" class="select select-bordered w-full" bind:value={editForm.priority}>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
            </div>
          </div>

          <div class="space-y-4">
            <div class="form-control">
              <label class="label" for="edit-location-address">
                <span class="label-text">Street Address</span>
              </label>
              <input
                id="edit-location-address"
                name="location_address"
                type="text"
                class="input input-bordered w-full"
                bind:value={editForm.location_address}
                placeholder="123 Main Street"
              />
            </div>

            <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div class="form-control md:col-span-3">
                <label class="label" for="edit-location-city">
                  <span class="label-text">City</span>
                </label>
                <input
                  id="edit-location-city"
                  name="location_city"
                  type="text"
                  class="input input-bordered w-full"
                  bind:value={editForm.location_city}
                  placeholder="Springfield"
                />
              </div>

              <div class="form-control">
                <label class="label" for="edit-location-state">
                  <span class="label-text">State</span>
                </label>
                <input
                  id="edit-location-state"
                  name="location_state"
                  type="text"
                  class="input input-bordered w-full"
                  bind:value={editForm.location_state}
                  placeholder="IL"
                  maxlength="2"
                />
              </div>

              <div class="form-control">
                <label class="label" for="edit-location-zip">
                  <span class="label-text">ZIP Code</span>
                </label>
                <input
                  id="edit-location-zip"
                  name="location_zip"
                  type="text"
                  class="input input-bordered w-full"
                  bind:value={editForm.location_zip}
                  placeholder="62701"
                  maxlength="10"
                />
              </div>
            </div>
          </div>

        </div>

        <div class="modal-action pt-6 border-t border-base-300 mt-auto">
          {#if workOrder && mode === "edit"}
            <button type="button" class="btn btn-ghost text-orange-700 hover:bg-orange-50 hover:text-orange-800" onclick={handleDelete} title="Delete work order" aria-label="Delete work order">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Delete
            </button>
          {/if}
          <div class="flex-1"></div>
          <button type="button" class="btn btn-ghost" onclick={onClose}>Cancel</button>
          <button type="submit" class="btn btn-primary" disabled={isCreatingLocation || (mode === "create" ? $workOrderCreateMutation.isPending : $updateMutation.isPending)}>
            {#if mode === "create"}
              {#if isCreatingLocation}
                <span class="loading loading-spinner loading-sm"></span>
                Creating Location...
              {:else if $workOrderCreateMutation.isPending}
                <span class="loading loading-spinner loading-sm"></span>
                Creating Work Order...
              {:else}
                Create Work Order
              {/if}
            {:else}
              {#if isCreatingLocation}
                <span class="loading loading-spinner loading-sm"></span>
                Updating Location...
              {:else if $updateMutation.isPending}
                <span class="loading loading-spinner loading-sm"></span>
                Saving Changes...
              {:else}
                Save Changes
              {/if}
            {/if}
          </button>
        </div>
      </form>
    {/if}

    {#if $updateMutation.error || $workOrderCreateMutation.error}
      <div class="alert alert-error mt-4">
        <span>Failed to {mode === "create" ? "create" : "update"} work order. Please try again.</span>
      </div>
    {/if}
  </div>
</div>
{/if}
