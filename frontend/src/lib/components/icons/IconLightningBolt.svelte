<script lang="ts">
// biome-ignore lint/style/useConst: Svelte props need to be let for binding
let size = "2em";
export { size, strokeWidth }; // Corresponds to w-8 h-8 or 32px
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
  <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
</svg>
