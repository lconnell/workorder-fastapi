<script lang="ts">
  export let size = "1.25em"; // Corresponds to h-5 w-5 or 20px if 1em=16px
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
  <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h8m-8 6h16" />
</svg>
