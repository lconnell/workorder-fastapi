<script lang="ts">
// biome-ignore lint/style/useConst: Svelte props need to be let for binding
let size = "1em";
export { size, strokeWidth }; // Corresponds to h-4 w-4
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
  <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
</svg>
