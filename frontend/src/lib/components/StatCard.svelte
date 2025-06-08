<script lang="ts">
import type { ComponentType, SvelteComponent } from "svelte";

interface IconProps {
	class?: string;
	size?: string;
	strokeWidth?: number;
}

interface Props {
	title: string;
	value: number | string;
	iconComponent: ComponentType<SvelteComponent<IconProps>>;
	link: string;
	colorClass: string;
	subtitle?: string;
}

const { title, value, iconComponent, link, colorClass, subtitle }: Props =
	$props();

// Assign to a capitalized variable to use as a dynamic component
const Icon = iconComponent;
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
				<Icon class="w-8 h-8 stroke-current" />
			</div>
		</div>
	</a>
</div>
