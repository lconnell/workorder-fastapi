<script lang="ts">
  export let size = "2em"; // Corresponds to w-8 h-8
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
  <path stroke-linecap="round" stroke-linejoin="round" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path>
</svg>
