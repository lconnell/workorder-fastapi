<script lang="ts">
import {
	IconCheckCircle,
	IconErrorCrossCircle,
	IconInfo,
	IconWarning,
} from "$lib/components/icons";
import { toastStore } from "$lib/stores/toastStore.svelte";
import type { ComponentType, SvelteComponent } from "svelte";

function getAlertClasses(type: string) {
	switch (type) {
		case "success":
			return "alert-success";
		case "error":
			return "alert-error";
		case "warning":
			return "alert-warning";
		case "info":
			return "alert-info";
		default:
			return "alert-info";
	}
}

interface IconProps {
	class?: string;
	size?: string;
	strokeWidth?: number;
}

function getIconComponent(
	type: string,
): ComponentType<SvelteComponent<IconProps>> {
	switch (type) {
		case "success":
			return IconCheckCircle;
		case "error":
			return IconErrorCrossCircle;
		case "warning":
			return IconWarning;
		default:
			return IconInfo;
	}
}
</script>

<!-- Toast Container -->
<div class="toast toast-end z-50">
  {#each toastStore.toasts as toast (toast.id)}
    <div class="alert {getAlertClasses(toast.type)} shadow-lg">
      <svelte:component
        this={getIconComponent(toast.type)}
        class="stroke-current shrink-0 h-6 w-6"
      />
      <span>{toast.message}</span>
      <button
        class="btn btn-ghost btn-sm"
        onclick={() => toastStore.remove(toast.id)}
      >
        ✕
      </button>
    </div>
  {/each}
</div>
