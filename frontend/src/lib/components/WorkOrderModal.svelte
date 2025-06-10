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
import { logger } from "$lib/utils/logger";
import { createMutation, useQueryClient } from "@tanstack/svelte-query";

interface LocationCreate {
	address?: string | null;
	city?: string | null;
	state_province?: string | null;
	postal_code?: string | null;
	country?: string;
}

interface Location {
	id: string;
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

let modalElement: HTMLDialogElement;

const queryClient = useQueryClient();

// Reference to the title input for autofocus
// biome-ignore lint/style/useConst: Cannot use const with bind:this
let titleInputElement = $state<HTMLInputElement>();

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

// Default form values (DRY principle)
const DEFAULT_FORM_VALUES = {
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
} as const;

// Initialize form state based on mode and work order data
$effect(() => {
	if (mode === "create" && isOpen) {
		// Reset to default values for create mode when modal opens
		editForm = { ...DEFAULT_FORM_VALUES };
	} else if (workOrder && mode === "edit") {
		// Populate form with existing work order data
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
	onError: (error) => {
		logger.error("Failed to update work order", "WorkOrderModal", {
			error,
			workOrderId: workOrder?.id,
		});
		toastStore.error(
			`Failed to update work order: ${error instanceof Error ? error.message : "Unknown error"}`,
		);
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
	onError: (error) => {
		logger.error("Failed to create work order", "WorkOrderModal", { error });
		toastStore.error(
			`Failed to create work order: ${error instanceof Error ? error.message : "Unknown error"}`,
		);
	},
});

// Helper functions for form validation styling (DRY principle)
function toggleValidationStyling(shouldAdd: boolean) {
	if (!modalElement) return;

	const form = modalElement.querySelector("#work-order-form");
	if (!form) return;

	const inputs = form.querySelectorAll(".validator");
	for (const input of inputs) {
		if (shouldAdd) {
			input.classList.add("was-validated");
		} else {
			input.classList.remove("was-validated");
		}
	}
}

// Specific helper functions for clarity
const addValidationStyling = () => toggleValidationStyling(true);
const clearValidationState = () => toggleValidationStyling(false);

async function handleSubmit() {
	try {
		addValidationStyling();
		let locationId: string | undefined = undefined;

		// All fields are required for new work orders
		// Native browser validation will handle individual field checks via form.checkValidity()
		// Toast messages for individual fields are removed as hints will appear under fields

		// Handle location logic - only create new location if data has changed or if it's a new work order
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

			// Check if location data has changed from existing work order location
			const hasLocationChanged =
				mode === "create" ||
				!workOrder?.location ||
				editForm.location_address.trim() !==
					(workOrder.location.address || "") ||
				editForm.location_city.trim() !== (workOrder.location.city || "") ||
				editForm.location_state.trim() !==
					(workOrder.location.state_province || "") ||
				editForm.location_zip.trim() !== (workOrder.location.postal_code || "");

			if (hasLocationChanged) {
				logger.debug(
					"Location data has changed, creating new location",
					"WorkOrderModal",
					{
						mode,
						existingLocation: workOrder?.location
							? {
									address: workOrder.location.address,
									city: workOrder.location.city,
									state: workOrder.location.state_province,
									zip: workOrder.location.postal_code,
								}
							: null,
						newLocation: {
							address: editForm.location_address,
							city: editForm.location_city,
							state: editForm.location_state,
							zip: editForm.location_zip,
						},
					},
				);

				isCreatingLocation = true;

				// Send clean, separate address fields - let backend construct complete address
				const locationData: LocationCreate = {
					address: editForm.location_address.trim() || null,
					city: editForm.location_city.trim() || null,
					state_province: editForm.location_state.trim() || null,
					postal_code: editForm.location_zip.trim() || null,
					country: "USA",
				};

				logger.debug("Sending location data to backend", "WorkOrderModal", {
					locationData,
				});

				const locationResult = await clientWrapper<Location>({
					method: "POST",
					url: API_ENDPOINTS.LOCATIONS,
					data: locationData,
				});

				logger.info("Location created successfully", "WorkOrderModal", {
					locationId: locationResult.id,
				});

				// Check if location has coordinates and warn user if not
				if (!locationResult.latitude || !locationResult.longitude) {
					toastStore.warning(
						"Location created but could not be mapped. Address may be invalid or geocoding service unavailable.",
					);
					logger.warning(
						"Location created without coordinates",
						"WorkOrderModal",
						{ locationId: locationResult.id, locationData },
					);
				}

				locationId = locationResult.id;
				isCreatingLocation = false;
			} else {
				// Location data hasn't changed, use existing location ID
				logger.debug(
					"Location data unchanged, using existing location ID",
					"WorkOrderModal",
					{ locationId: editForm.location_id },
				);
				locationId = editForm.location_id;
			}
		} else if (editForm.location_id) {
			// Use existing location ID if provided
			logger.debug("Using existing location ID from form", "WorkOrderModal", {
				locationId: editForm.location_id,
			});
			locationId = editForm.location_id;
		}

		if (mode === "create") {
			// Handle create mode
			const createData: WorkOrderCreate = {
				title: editForm.title,
				status: editForm.status as WorkOrderCreate["status"],
				priority: editForm.priority as WorkOrderCreate["priority"],
			};

			// Add optional fields if they have values (handle empty strings properly)
			if (editForm.description.trim()) {
				createData.description = editForm.description.trim();
			}
			if (editForm.assigned_to_user_id.trim()) {
				createData.assigned_to_user_id = editForm.assigned_to_user_id.trim();
			}
			if (locationId) {
				createData.location_id = locationId;
			}

			logger.logFormSubmission("WorkOrderCreate", true, { createData });
			$workOrderCreateMutation.mutate(createData);
		} else if (mode === "edit" && workOrder) {
			// Handle edit mode
			const updateData: WorkOrderUpdate = {};

			// Only include fields that have actually changed and handle empty strings properly
			if (editForm.title.trim() !== workOrder.title) {
				updateData.title = editForm.title.trim();
			}

			const newDescription = editForm.description.trim() || undefined;
			const currentDescription = workOrder.description || undefined;
			if (newDescription !== currentDescription) {
				updateData.description = newDescription;
			}

			if (editForm.status !== workOrder.status) {
				updateData.status = editForm.status as WorkOrder["status"];
			}

			if (editForm.priority !== workOrder.priority) {
				updateData.priority = editForm.priority as WorkOrder["priority"];
			}

			const newAssignedUserId =
				editForm.assigned_to_user_id.trim() || undefined;
			const currentAssignedUserId = workOrder.assigned_to_user_id || undefined;
			if (newAssignedUserId !== currentAssignedUserId) {
				updateData.assigned_to_user_id = newAssignedUserId;
			}

			// Handle location updates
			const currentLocationId = workOrder.location_id;
			if (locationId !== currentLocationId) {
				updateData.location_id = locationId || undefined;
			}

			if (Object.keys(updateData).length > 0) {
				logger.logFormSubmission("WorkOrderUpdate", true, {
					updateData,
					workOrderId: workOrder.id,
				});
				$updateMutation.mutate(updateData);
			} else {
				logger.info(
					"No changes detected in work order form",
					"WorkOrderModal",
					{ workOrderId: workOrder.id },
				);
				toastStore.info("No changes to save");
				onClose();
			}
		}
	} catch (error) {
		logger.error("Error in handleSubmit", "WorkOrderModal", {
			error,
			mode,
			workOrderId: workOrder?.id,
		});
		isCreatingLocation = false;
		// Show error message to the user
		toastStore.error(
			`Failed to save work order: ${error instanceof Error ? error.message : "Unknown error"}`,
		);
	}
}

async function handleDelete() {
	if (!workOrder) return;

	logger.logUserAction("delete_work_order_confirm", "WorkOrderModal", {
		workOrderId: workOrder.id,
		title: workOrder.title,
	});

	if (
		!confirm(
			`Are you sure you want to delete "${workOrder.title}"? This action cannot be undone.`,
		)
	) {
		logger.logUserAction("delete_work_order_cancelled", "WorkOrderModal", {
			workOrderId: workOrder.id,
		});
		return;
	}

	try {
		await clientWrapper({
			method: "DELETE",
			url: `${API_ENDPOINTS.WORK_ORDERS}/${workOrder.id}`,
		});

		// Refresh the work orders list and close modal
		logger.logUserAction("delete_work_order_success", "WorkOrderModal", {
			workOrderId: workOrder.id,
		});
		toastStore.success("Work order deleted successfully");
		queryClient.invalidateQueries({ queryKey: ["workOrders"] });
		onClose();
	} catch (error) {
		logger.error("Failed to delete work order", "WorkOrderModal", {
			error,
			workOrderId: workOrder.id,
		});
		toastStore.error("Failed to delete work order. Please try again.");
	}
}

// Badge styling and date formatting now handled by shared utilities

// Control modal visibility with proper cleanup
$effect(() => {
	if (!modalElement) return;

	if (isOpen) {
		logger.logUserAction("modal_opened", "WorkOrderModal", {
			mode,
			workOrderId: workOrder?.id,
		});
		clearValidationState(); // Clear validation BEFORE showing modal
		modalElement.showModal();

		// Autofocus title input when in create mode
		if (mode === "create" && titleInputElement) {
			// Dialog elements need a small delay to be ready for focus
			setTimeout(() => {
				titleInputElement?.focus();
			}, 10);
		}
	} else {
		logger.logUserAction("modal_closed", "WorkOrderModal", {
			mode,
			workOrderId: workOrder?.id,
		});
		modalElement.close();
	}
});

// Handle modal close event with proper cleanup
$effect(() => {
	if (!modalElement) return;

	const handleClose = () => onClose();
	modalElement.addEventListener("close", handleClose);

	return () => {
		modalElement.removeEventListener("close", handleClose);
	};
});
</script>

<!-- Work Order Modal -->
<dialog id="work-order-modal" class="modal" bind:this={modalElement}>
  <div class="modal-box w-11/12 max-w-5xl rounded-lg">
    <form method="dialog">
      <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2" onclick={() => modalElement.close()}>✕</button>
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
              <div class="text-base">{workOrder?.location?.address || ""}</div>
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
        <button class="btn btn-primary" onclick={() => {
          logger.logUserAction("switch_to_edit_mode", "WorkOrderModal", { workOrderId: workOrder?.id });
          mode = "edit";
        }}>Edit</button>
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
              <input
                id="edit-title"
                name="title"
                type="text"
                class="input validator w-full"
                bind:value={editForm.title}
                bind:this={titleInputElement}
                required
                title="Title is required"
              />
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
          <button type="button" class="btn" onclick={() => modalElement.close()}>Cancel</button>
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
