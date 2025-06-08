<script lang="ts">
// biome-ignore lint/style/useConst: Svelte props need to be let for binding
let size = "4em";
export { size, strokeWidth }; // h-16 w-16
// biome-ignore lint/style/useConst: Svelte props need to be let for binding
let strokeWidth = 2;
// biome-ignore lint/style/useConst: Let for Svelte prop
let klass = "";
export { klass as class };
</script>

<svg
  xmlns="http://www.w3.org/2000/svg"
  width={size}
  height={size}
  fill="none"
  viewBox="0 0 24 24"
  stroke="currentColor"
  stroke-width={strokeWidth}
  class={klass}
  aria-hidden="true"
>
  <path stroke-linecap="round" stroke-linejoin="round" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
</svg>
