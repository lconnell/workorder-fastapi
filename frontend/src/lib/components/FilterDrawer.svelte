<script lang="ts">
import type { Snippet } from "svelte";

interface Props {
	drawerId: string;
	isOpen: boolean;
	onClose: () => void;
	title?: string;
	children?: Snippet;
	applyLabel?: string;
	onApply?: () => void;
}

const {
	drawerId,
	isOpen = false,
	onClose,
	title = "Filters",
	children,
	applyLabel = "Apply Filters",
	onApply,
}: Props = $props();

function handleApply() {
	onApply?.();
	onClose();
}

// Control drawer state
$effect(() => {
	const checkbox = document.getElementById(drawerId) as HTMLInputElement;
	if (checkbox) {
		checkbox.checked = isOpen;
	}
});
</script>

<div class="drawer">
	<input id={drawerId} type="checkbox" class="drawer-toggle" checked={isOpen} />
	<div class="drawer-side z-50">
		<label for={drawerId} aria-label="close sidebar" class="drawer-overlay"></label>
		<div class="p-4 w-80 min-h-full bg-base-100">
			<!-- Header -->
			<div class="flex items-center justify-between mb-6">
				<h3 class="text-xl font-semibold">{title}</h3>
				<button
					class="btn btn-ghost btn-sm btn-circle"
					onclick={onClose}
					aria-label="Close"
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>

			<!-- Content -->
			<div class="space-y-6">
				{@render children?.()}
			</div>

			<!-- Footer with Apply button -->
			<div class="mt-8">
				<div class="flex gap-2">
					<button
						class="btn btn-ghost flex-1"
						onclick={onClose}
					>
						Cancel
					</button>
					<button
						class="btn btn-primary flex-1"
						onclick={handleApply}
					>
						{applyLabel}
					</button>
				</div>
			</div>
		</div>
	</div>
</div>
