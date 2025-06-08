<script lang="ts">
import { toastStore } from "$lib/stores/toastStore.svelte";

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

function getIcon(type: string) {
	switch (type) {
		case "success":
			return "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z";
		case "error":
			return "M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z";
		case "warning":
			return "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z";
		default:
			return "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z";
	}
}
</script>

<!-- Toast Container -->
<div class="toast toast-end z-50">
  {#each toastStore.toasts as toast (toast.id)}
    <div class="alert {getAlertClasses(toast.type)} shadow-lg">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="stroke-current shrink-0 h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d={getIcon(toast.type)}
        />
      </svg>
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
