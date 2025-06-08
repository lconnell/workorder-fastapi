<script lang="ts">
import { clientWrapper } from "$lib/api/client-wrapper";
import { API_ENDPOINTS } from "$lib/constants";
import { toastStore } from "$lib/stores/toastStore.svelte";
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
		toastStore.success("Work order updated successfully");
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
		toastStore.success("Work order created successfully");
		queryClient.invalidateQueries({ queryKey: ["workOrders"] });
		onClose();
	},
});

async function handleSubmit() {
	try {
		// Add validation state to form fields
		const form = document.querySelector("#work-order-form");
		if (form) {
			const inputs = form.querySelectorAll(".validator");
			for (const input of inputs) {
				input.classList.add("was-validated");
			}
		}

		let locationId: string | undefined = undefined;

		// All fields are required for new work orders
		if (mode === "create") {
			if (!editForm.title.trim()) {
				toastStore.error("Title is required.");
				return;
			}
			if (!editForm.description.trim()) {
				toastStore.error("Description is required.");
				return;
			}
			if (!editForm.status.trim()) {
				toastStore.error("Status is required.");
				return;
			}
			if (!editForm.priority.trim()) {
				toastStore.error("Priority is required.");
				return;
			}
			if (!editForm.location_address.trim()) {
				toastStore.error("Street address is required.");
				return;
			}
			if (!editForm.location_city.trim()) {
				toastStore.error("City is required.");
				return;
			}
			if (!editForm.location_state.trim()) {
				toastStore.error("State is required.");
				return;
			}
			if (!editForm.location_zip.trim()) {
				toastStore.error("ZIP code is required.");
				return;
			}
		}

		// Create location if any address fields are provided
		if (
			editForm.location_address.trim() ||
			editForm.location_city.trim() ||
			editForm.location_state.trim() ||
			editForm.location_zip.trim()
		) {
			// Validate that if location is provided, we have at least city
			if (!editForm.location_city.trim()) {
				toastStore.error("Please provide at least a city for the location.");
				return;
			}

			isCreatingLocation = true;

			// Send clean, separate address fields - let backend construct complete address
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
		// Show error message to the user
		toastStore.error(
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
		toastStore.success("Work order deleted successfully");
		queryClient.invalidateQueries({ queryKey: ["workOrders"] });
		onClose();
	} catch (error) {
		console.error("Error deleting work order:", error);
		toastStore.error("Failed to delete work order. Please try again.");
	}
}

// Badge styling and date formatting now handled by shared utilities

// Show/hide modal based on isOpen prop
$effect(() => {
	const modal = document.getElementById(
		"work-order-modal",
	) as HTMLDialogElement;
	if (modal) {
		if (isOpen) {
			modal.showModal();
			// Clear validation state when modal opens
			const form = document.querySelector("#work-order-form");
			if (form) {
				const inputs = form.querySelectorAll(".validator");
				for (const input of inputs) {
					input.classList.remove("was-validated");
				}
			}
		} else {
			modal.close();
		}
	}
});

// Handle modal close event
$effect(() => {
	const modal = document.getElementById(
		"work-order-modal",
	) as HTMLDialogElement;
	if (modal) {
		const handleClose = () => {
			onClose();
		};
		modal.addEventListener("close", handleClose);
		return () => {
			modal.removeEventListener("close", handleClose);
		};
	}
});
</script>

<!-- Work Order Modal -->
<dialog id="work-order-modal" class="modal">
  <div class="modal-box w-11/12 max-w-5xl rounded-lg">
    <form method="dialog">
      <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
    </form>
    <h3 class="font-bold text-lg">
      {mode === "view" ? workOrder?.title || "Work Order Details" : mode === "edit" ? workOrder?.title || "Edit Work Order" : "Create Work Order"}
      {#if workOrder}
        <span class="text-base-content/60 font-mono text-sm">(#{workOrder.id.slice(0, 8)})</span>
      {/if}
    </h3>

    {#if mode === "view"}
      <!-- View Mode -->
      <div class="space-y-8 flex-1 overflow-auto">
        <!-- Work Order Details Section -->
        <fieldset class="border border-base-300 rounded-lg p-4 space-y-4">
          <legend class="text-sm font-medium px-2">Work Order Details</legend>

          <div>
            <h4 class="text-sm font-medium text-base-content/70 mb-2">Title</h4>
            <div class="text-base font-semibold">{workOrder?.title}</div>
          </div>

          <div>
            <h4 class="text-sm font-medium text-base-content/70 mb-2">Description</h4>
            <textarea
              readonly
              id="view-description"
              name="description"
              class="w-full min-h-32 max-h-48 resize-none whitespace-pre-wrap text-base-content/90 bg-transparent border-none outline-none p-0"
              aria-label="Work order description"
            >{workOrder?.description || "No description provided"}</textarea>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h4 class="text-sm font-medium text-base-content/70 mb-2">Status</h4>
              <div class="badge {getModalStatusBadgeClasses(workOrder?.status || '')}">{workOrder?.status}</div>
            </div>

            <div>
              <h4 class="text-sm font-medium text-base-content/70 mb-2">Priority</h4>
              <div class="badge {getModalPriorityBadgeClasses(workOrder?.priority || '')}">{workOrder?.priority}</div>
            </div>
          </div>
        </fieldset>

        <!-- Location Section -->
        {#if workOrder?.location}
          <fieldset class="border border-base-300 rounded-lg p-4 space-y-4">
            <legend class="text-sm font-medium px-2">Location</legend>

            <div>
              <h4 class="text-sm font-medium text-base-content/70 mb-2">Address</h4>
              <div class="text-base">{workOrder?.location?.address || workOrder?.location?.name}</div>
              {#if workOrder?.location?.city || workOrder?.location?.state_province || workOrder?.location?.postal_code}
                <div class="text-base-content/70 mt-1">
                  {[workOrder?.location?.city, [workOrder?.location?.state_province, workOrder?.location?.postal_code].filter(Boolean).join(' ')].filter(Boolean).join(', ')}
                </div>
              {/if}
            </div>
          </fieldset>
        {/if}

        <!-- Timeline Section -->
        <fieldset class="border border-base-300 rounded-lg p-4 space-y-4">
          <legend class="text-sm font-medium px-2">Timeline</legend>

          <div class="space-y-3">
            <div>
              <h4 class="text-sm font-medium text-base-content/70 mb-2">Created</h4>
              <div class="text-base">{formatDateTime(workOrder?.created_at || '')}</div>
            </div>

            {#if workOrder?.updated_at !== workOrder?.created_at}
              <div>
                <h4 class="text-sm font-medium text-base-content/70 mb-2">Last Updated</h4>
                <div class="text-base">{formatDateTime(workOrder?.updated_at || '')}</div>
              </div>
            {/if}
          </div>
        </fieldset>
      </div>

      <div class="modal-action">
        {#if workOrder}
          <button class="btn btn-error btn-outline" onclick={handleDelete}>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Delete
          </button>
        {/if}
        <div class="flex-1"></div>
        <form method="dialog" class="inline-flex gap-2">
          <button class="btn">Close</button>
        </form>
        <button class="btn btn-primary" onclick={() => mode = "edit"}>Edit</button>
      </div>

    {:else if mode === "edit" || mode === "create"}
      <!-- Edit/Create Mode -->
      <form id="work-order-form" onsubmit={(e) => {
        e.preventDefault();
        const form = e.target as HTMLFormElement;
        if (form.checkValidity()) {
          handleSubmit();
        } else {
          form.reportValidity();
        }
      }} class="flex flex-col flex-1">
        <div class="space-y-8 flex-1 overflow-auto">
          <fieldset class="border border-base-300 rounded-lg p-4 space-y-4">
            <legend class="text-sm font-medium px-2">Work Order Details</legend>

            <div class="form-control">
              <label class="label" for="edit-title">
                <span class="label-text">Title <span class="text-error">*</span></span>
              </label>
              <input id="edit-title" name="title" type="text" class="input validator w-full" bind:value={editForm.title} required title="Title is required" />
              <p class="validator-hint">Title is required</p>
            </div>

            <div class="form-control">
              <label class="label" for="edit-description">
                <span class="label-text">Description <span class="text-error">*</span></span>
              </label>
              <textarea id="edit-description" name="description" class="textarea validator w-full min-h-24 max-h-40 resize-y" bind:value={editForm.description} required title="Description is required"></textarea>
              <p class="validator-hint">Description is required</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="form-control">
                <label class="label" for="edit-status">
                  <span class="label-text">Status <span class="text-error">*</span></span>
                </label>
                <select id="edit-status" name="status" class="select validator w-full" bind:value={editForm.status} required title="Status is required">
                  <option disabled value="">Choose status</option>
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
                <p class="validator-hint">Status is required</p>
              </div>

              <div class="form-control">
                <label class="label" for="edit-priority">
                  <span class="label-text">Priority <span class="text-error">*</span></span>
                </label>
                <select id="edit-priority" name="priority" class="select validator w-full" bind:value={editForm.priority} required title="Priority is required">
                  <option disabled value="">Choose priority</option>
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
                <p class="validator-hint">Priority is required</p>
              </div>
            </div>
          </fieldset>

          <fieldset class="border border-base-300 rounded-lg p-4 space-y-4">
            <legend class="text-sm font-medium px-2">Location (Required)</legend>
            <div class="form-control">
              <label class="label" for="edit-location-address">
                <span class="label-text">Street Address <span class="text-error">*</span></span>
              </label>
              <input
                id="edit-location-address"
                name="location_address"
                type="text"
                class="input validator w-full"
                bind:value={editForm.location_address}
                placeholder="123 Main Street"
                autocomplete="address-line1"
                required
                title="Street address is required"
              />
              <p class="validator-hint">Street address is required</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div class="form-control md:col-span-3">
                <label class="label" for="edit-location-city">
                  <span class="label-text">City <span class="text-error">*</span></span>
                  <span class="label-text-alt text-base-content/60">Required</span>
                </label>
                <input
                  id="edit-location-city"
                  name="location_city"
                  type="text"
                  class="input validator w-full"
                  bind:value={editForm.location_city}
                  placeholder="Springfield"
                  autocomplete="address-level2"
                  pattern=".+"
                  required
                  title="City is required"
                />
                <p class="validator-hint">Required</p>
              </div>

              <div class="form-control">
                <label class="label" for="edit-location-state">
                  <span class="label-text">State <span class="text-error">*</span></span>
                </label>
                <input
                  id="edit-location-state"
                  name="location_state"
                  type="text"
                  class="input validator w-full"
                  bind:value={editForm.location_state}
                  placeholder="IL"
                  maxlength="2"
                  autocomplete="address-level1"
                  required
                  title="State is required"
                />
                <p class="validator-hint">State is required</p>
              </div>

              <div class="form-control">
                <label class="label" for="edit-location-zip">
                  <span class="label-text">ZIP Code <span class="text-error">*</span></span>
                </label>
                <input
                  id="edit-location-zip"
                  name="location_zip"
                  type="text"
                  class="input validator w-full"
                  bind:value={editForm.location_zip}
                  placeholder="62701"
                  maxlength="10"
                  autocomplete="postal-code"
                  required
                  title="ZIP code is required"
                />
                <p class="validator-hint">ZIP code is required</p>
              </div>
            </div>
          </fieldset>

        </div>

        <div class="modal-action">
          {#if workOrder && mode === "edit"}
            <button type="button" class="btn btn-error btn-outline" onclick={handleDelete}>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Delete
            </button>
          {/if}
          <div class="flex-1"></div>
          <button type="button" class="btn" onclick={() => (document.getElementById('work-order-modal') as HTMLDialogElement)?.close()}>Cancel</button>
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
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        <span>Failed to {mode === "create" ? "create" : "update"} work order. Please try again.</span>
      </div>
    {/if}
  </div>
</dialog>
