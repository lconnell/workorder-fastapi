<script lang="ts">
import type { ComponentType, SvelteComponent } from "svelte";

interface Props {
	title: string;
	value: number | string;
	iconComponent: ComponentType<SvelteComponent<{ class?: string; size?: string }>>;
	link: string;
	colorClass: string;
	subtitle?: string;
}

const {
	title,
	value,
	iconComponent,
	link,
	colorClass,
	subtitle,
}: Props = $props();
</script>

<div class="card bg-base-100 shadow-sm hover:shadow-md transition-shadow rounded-lg">
	<a href={link} class="card-body p-4">
		<div class="flex items-center justify-between">
			<div>
				<p class="text-sm font-medium text-base-content/70">{title}</p>
				<p class="text-2xl font-bold {colorClass}">{value}</p>
				{#if subtitle}
					<p class="text-xs text-base-content/50">{subtitle}</p>
				{/if}
			</div>
			<div class={colorClass}>
				<svelte:component this={iconComponent} class="w-8 h-8 stroke-current" />
			</div>
		</div>
	</a>
</div>
