<script lang="ts">
  export let size = "1.5em"; // h-6 w-6 (default for Toast)
  export let strokeWidth = 2;
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
  <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
</svg>
