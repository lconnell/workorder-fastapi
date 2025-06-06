<script lang="ts">
import { clientWrapper } from "$lib/api/client-wrapper";
import { API_ENDPOINTS, PRIORITY_COLORS, STATUS_COLORS } from "$lib/constants";
import type { WorkOrder, WorkOrderUpdate } from "$lib/types/work-orders";
import { createMutation, useQueryClient } from "@tanstack/svelte-query";

interface Props {
	workOrder: WorkOrder | null;
	mode: "view" | "edit";
	isOpen: boolean;
	onClose: () => void;
}

// biome-ignore lint/style/useConst: Svelte 5 $bindable prop assignment requires let
let { workOrder, mode = $bindable(), isOpen, onClose }: Props = $props();

const queryClient = useQueryClient();

$effect(() => {
	console.log(
		"[WorkOrderModal] Props received - isOpen:",
		isOpen,
		"workOrder ID:",
		workOrder?.id,
	);
	if (isOpen && workOrder) {
		console.log(
			"[WorkOrderModal] Condition met: Rendering modal for workOrder ID:",
			workOrder.id,
		);
	} else if (isOpen && !workOrder) {
		console.log(
			"[WorkOrderModal] Condition NOT met: isOpen is true, but workOrder is null. Modal will not render.",
		);
	} else if (!isOpen) {
		console.log(
			"[WorkOrderModal] Condition NOT met: isOpen is false. Modal will not render.",
		);
	}
});

// Form state for editing
let editForm = $state({
	title: "",
	description: "",
	status: "",
	priority: "",
	assigned_to_user_id: "",
});

// Initialize form when work order changes
$effect(() => {
	if (workOrder && mode === "edit") {
		editForm = {
			title: workOrder.title || "",
			description: workOrder.description || "",
			status: workOrder.status || "",
			priority: workOrder.priority || "",
			assigned_to_user_id: workOrder.assigned_to_user_id || "",
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

function handleSubmit() {
	if (!workOrder) return;

	const updateData: WorkOrderUpdate = {};

	if (editForm.title !== workOrder.title) updateData.title = editForm.title;
	if (editForm.description !== workOrder.description)
		updateData.description = editForm.description;
	if (editForm.status !== workOrder.status)
		updateData.status = editForm.status as WorkOrder["status"];
	if (editForm.priority !== workOrder.priority)
		updateData.priority = editForm.priority as WorkOrder["priority"];
	if (editForm.assigned_to_user_id !== workOrder.assigned_to_user_id)
		updateData.assigned_to_user_id = editForm.assigned_to_user_id;

	if (Object.keys(updateData).length > 0) {
		$updateMutation.mutate(updateData);
	}
}

function getStatusColor(status: string): string {
	return (
		STATUS_COLORS[status.toLowerCase() as keyof typeof STATUS_COLORS] ||
		"neutral"
	);
}

function getPriorityColor(priority: string): string {
	return PRIORITY_COLORS[priority as keyof typeof PRIORITY_COLORS] || "neutral";
}

function formatDate(dateString: string): string {
	return new Date(dateString).toLocaleDateString("en-US", {
		year: "numeric",
		month: "long",
		day: "numeric",
		hour: "2-digit",
		minute: "2-digit",
	});
}
</script>

{#if isOpen && workOrder}
<div class="modal modal-open z-50">
  <div class="modal-box w-11/12 max-w-6xl bg-base-100 shadow-2xl border border-base-300 rounded-xl p-8 z-50">
    <div class="flex items-center justify-between mb-8">
      <h3 class="font-bold text-xl text-base-content">
        {mode === "view" ? "Work Order Details" : "Edit Work Order"}
        <span class="text-base-content/60 font-mono text-base">#{workOrder.id}</span>
      </h3>
      <button class="btn btn-sm btn-circle btn-ghost" onclick={onClose}>✕</button>
    </div>

    {#if mode === "view"}
      <!-- View Mode -->
      <div class="space-y-8">
        <div class="bg-base-200/50 p-6 rounded-lg">
          <h4 class="text-xl font-semibold text-base-content mb-3">{workOrder.title}</h4>
          <p class="text-base-content/70 text-base leading-relaxed">{workOrder.description || "No description provided"}</p>
        </div>

        <div class="flex gap-6">
          <div class="badge badge-{getStatusColor(workOrder.status)} badge-lg">{workOrder.status}</div>
          <div class="badge badge-{getPriorityColor(workOrder.priority)} badge-outline badge-lg">{workOrder.priority}</div>
        </div>

        {#if workOrder.location}
          <div class="bg-base-200 p-6 rounded-lg border border-base-300">
            <div class="flex items-center gap-3 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-base-content/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <p class="font-semibold text-base-content">Location</p>
            </div>
            <p class="font-semibold text-base">{workOrder.location.name}</p>
            <p class="text-base-content/70 mt-1">{workOrder.location.address}</p>
            <p class="text-base-content/70">{workOrder.location.city}, {workOrder.location.state_province} {workOrder.location.postal_code}</p>
          </div>
        {/if}

        <div class="bg-base-200/30 p-6 rounded-lg">
          <div class="flex items-center gap-3 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-base-content/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="font-semibold text-base-content">Timeline</p>
          </div>
          <div class="space-y-2">
            <p class="text-base"><span class="text-base-content/60">Created:</span> {formatDate(workOrder.created_at)}</p>
            {#if workOrder.updated_at !== workOrder.created_at}
              <p class="text-base"><span class="text-base-content/60">Updated:</span> {formatDate(workOrder.updated_at)}</p>
            {/if}
          </div>
        </div>
      </div>

      <div class="modal-action pt-8 mt-8 border-t border-base-300">
        <button class="btn btn-ghost" onclick={onClose}>Close</button>
        <button class="btn btn-primary" onclick={() => mode = "edit"}>Edit</button>
      </div>

    {:else}
      <!-- Edit Mode -->
      <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
        <div class="space-y-8">
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
            <textarea id="edit-description" name="description" class="textarea textarea-bordered w-full min-h-24" bind:value={editForm.description}></textarea>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="form-control">
              <label class="label" for="edit-status">
                <span class="label-text">Status</span>
              </label>
              <select id="edit-status" name="status" class="select select-bordered w-full" bind:value={editForm.status}>
                <option value="Open">Open</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="On Hold">On Hold</option>
                <option value="Cancelled">Cancelled</option>
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

          {#if workOrder.location}
            <div class="bg-base-200 p-6 rounded-lg border border-base-300">
              <div class="flex items-center gap-3 mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-base-content/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <p class="font-semibold text-base-content">Location</p>
              </div>
              <p class="font-semibold text-base">{workOrder.location.name}</p>
              <p class="text-base-content/70 mt-1">{workOrder.location.address}</p>
              <p class="text-base-content/70">{workOrder.location.city}, {workOrder.location.state_province} {workOrder.location.postal_code}</p>
            </div>
          {/if}
        </div>

        <div class="modal-action pt-8 mt-8 border-t border-base-300">
          <button type="button" class="btn btn-ghost" onclick={onClose}>Cancel</button>
          <button type="submit" class="btn btn-primary" disabled={$updateMutation.isPending}>
            {#if $updateMutation.isPending}
              <span class="loading loading-spinner loading-sm"></span>
              Saving...
            {:else}
              Save Changes
            {/if}
          </button>
        </div>
      </form>
    {/if}

    {#if $updateMutation.error}
      <div class="alert alert-error mt-4">
        <span>Failed to update work order. Please try again.</span>
      </div>
    {/if}
  </div>
</div>
{/if}
